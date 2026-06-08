"""
TradingBot – Haupt-Orchestrator

Kombinierte Strategie: RSI Reversal + Bollinger Band Reversal
Broker: Trade Republic (via pytr, inoffizielle API)

Starten:
  python bot.py              → Echtgeld-Betrieb, stündliche Prüfung
  python bot.py --setup      → Einmaliger Trade-Republic-Login einrichten
  python bot.py --status     → Aktuelle Positionen und heutigen P&L anzeigen
  python bot.py --dry-run    → Signale berechnen und loggen, keine Orders
"""

import argparse
import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

import yfinance as yf
import pandas as pd

# Eigene Module aus demselben Ordner laden
sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
import db
import strategy
import risk_manager as risk
from trade_republic import TRClient


# --- Logging einrichten ---

def setup_logging():
    fmt = "%(asctime)s [%(levelname)s] %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=fmt,
        handlers=[
            logging.FileHandler(config.LOG_PATH),
            logging.StreamHandler(sys.stdout),
        ],
    )

logger = logging.getLogger(__name__)


# --- Hilfsfunktionen ---

def load_history(yahoo_ticker: str, days: int) -> pd.DataFrame | None:
    """Lädt tägliche OHLCV-Daten von Yahoo Finance."""
    try:
        df = yf.download(yahoo_ticker, period=f"{days}d", interval="1d", progress=False, auto_adjust=True)
        if df.empty:
            return None
        df.columns = [c.lower() for c in df.columns]
        df = df.rename(columns={"adj close": "close"}) if "adj close" in df.columns else df
        df = df[["open", "high", "low", "close", "volume"]].dropna()
        return df
    except Exception as e:
        logger.error(f"Yahoo Finance Fehler [{yahoo_ticker}]: {e}")
        return None


def print_status(conn):
    """Zeigt offene Positionen und heutigen P&L."""
    positions = db.get_open_positions(conn)
    pnl       = db.get_todays_pnl(conn)

    print("\n" + "=" * 60)
    print(f"  TradingBot Status  –  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    if not positions:
        print("  Offene Positionen: keine")
    else:
        print(f"  Offene Positionen ({len(positions)}):")
        for p in positions:
            print(
                f"    {p['asset_name']:15s}  {p['quantity']:>10.6f}  "
                f"Ø-Einstieg: {p['avg_entry_price']:>10.2f} EUR"
            )

    sign = "+" if pnl >= 0 else ""
    print(f"\n  Heutiger P&L: {sign}{pnl:.2f} EUR")
    print("=" * 60 + "\n")


# --- Kern-Zyklus ---

async def run_cycle(tr_client: TRClient, conn, dry_run: bool) -> None:
    """Ein vollständiger Prüfzyklus: Risiko → offene Pos. → Signale → Orders."""

    # 1. Portfoliowert
    portfolio_value = await tr_client.get_portfolio_value()
    if portfolio_value <= 0:
        logger.warning("Portfoliowert = 0 oder nicht abrufbar – Zyklus übersprungen")
        return

    logger.info(f"Portfoliowert: {portfolio_value:.2f} EUR")

    # 2. Tagesverlust-Check
    if not risk.can_trade_today(conn, portfolio_value, config):
        daily_pnl = db.get_todays_pnl(conn)
        logger.warning(
            f"Tagesverlust-Limit erreicht: {daily_pnl:.2f} EUR "
            f"(>{config.MAX_DAILY_LOSS_PCT*100:.0f}% von {portfolio_value:.2f} EUR). "
            f"Bot pausiert für heute."
        )
        return

    # 3. Offene Positionen auf Stop-Loss / Take-Profit prüfen
    open_positions = db.get_open_positions(conn)
    for pos in open_positions:
        current_price = await tr_client.get_price(pos["isin"])
        if current_price is None:
            logger.warning(f"Kein Preis für offene Position {pos['asset_name']}, übersprungen")
            continue

        entry = pos["avg_entry_price"]

        if risk.should_stop_loss(entry, current_price, config):
            pct = (entry - current_price) / entry * 100
            logger.warning(
                f"STOP-LOSS: {pos['asset_name']} | "
                f"Einstieg={entry:.4f} | Jetzt={current_price:.4f} | Verlust={pct:.1f}%"
            )
            if not dry_run:
                result = await tr_client.sell(pos["isin"], pos["quantity"])
                if result:
                    db.log_trade(
                        conn, pos["asset_name"], pos["isin"],
                        "SELL", current_price, pos["quantity"],
                        current_price * pos["quantity"],
                        "STOP_LOSS", portfolio_value,
                    )

        elif risk.should_take_profit(entry, current_price, config):
            pct = (current_price - entry) / entry * 100
            logger.info(
                f"TAKE-PROFIT: {pos['asset_name']} | "
                f"Einstieg={entry:.4f} | Jetzt={current_price:.4f} | Gewinn={pct:.1f}%"
            )
            if not dry_run:
                result = await tr_client.sell(pos["isin"], pos["quantity"])
                if result:
                    db.log_trade(
                        conn, pos["asset_name"], pos["isin"],
                        "SELL", current_price, pos["quantity"],
                        current_price * pos["quantity"],
                        "TAKE_PROFIT", portfolio_value,
                    )

    # 4. Signale für alle Watchlist-Assets berechnen
    for asset in config.WATCHLIST:
        try:
            # Historische Daten (yfinance)
            hist_df = load_history(asset["yahoo_ticker"], config.HISTORY_DAYS)
            if hist_df is None or len(hist_df) < config.MA_TREND_PERIOD:
                logger.warning(
                    f"{asset['name']}: Nicht genug historische Daten "
                    f"({0 if hist_df is None else len(hist_df)} Tage)"
                )
                continue

            # Signal berechnen
            sig = strategy.calculate_signals(hist_df, config)

            # Signal loggen
            db.log_signal(
                conn, asset["name"], asset["isin"],
                sig["rsi"], sig["price"],
                sig["bb_lower"], sig["bb_upper"], sig["ma200"],
                sig["signal"],
            )

            logger.info(
                f"{asset['name']:15s} | Signal={sig['signal']:4s} | {sig['reason']}"
            )

            # --- BUY ---
            if sig["signal"] == "BUY":
                if risk.has_open_position(conn, asset["isin"]):
                    logger.debug(f"{asset['name']}: Position bereits offen, BUY übersprungen")
                    continue

                if not risk.can_open_position(conn, config):
                    logger.warning(f"{asset['name']}: Max. Positionen ({config.MAX_OPEN_POSITIONS}) erreicht")
                    continue

                price    = sig["price"]
                quantity = risk.calculate_position_size(portfolio_value, price, config)
                if quantity <= 0:
                    logger.warning(f"{asset['name']}: Berechnete Menge = 0, übersprungen")
                    continue

                value_eur = price * quantity
                logger.info(
                    f"{'[DRY-RUN] ' if dry_run else ''}KAUFE {quantity} x {asset['name']} "
                    f"@ {price:.4f} EUR = {value_eur:.2f} EUR"
                )

                if not dry_run:
                    result = await tr_client.buy(asset["isin"], quantity)
                    if result:
                        db.log_trade(
                            conn, asset["name"], asset["isin"],
                            "BUY", price, quantity, value_eur,
                            "SIGNAL", portfolio_value,
                        )
                        db.log_signal(
                            conn, asset["name"], asset["isin"],
                            sig["rsi"], sig["price"],
                            sig["bb_lower"], sig["bb_upper"], sig["ma200"],
                            sig["signal"], executed=True,
                        )

            # --- SELL ---
            elif sig["signal"] == "SELL":
                if not risk.has_open_position(conn, asset["isin"]):
                    logger.debug(f"{asset['name']}: Keine offene Position, SELL übersprungen")
                    continue

                open_pos = db.get_open_positions(conn)
                pos = next((p for p in open_pos if p["isin"] == asset["isin"]), None)
                if not pos:
                    continue

                price     = sig["price"]
                value_eur = price * pos["quantity"]
                logger.info(
                    f"{'[DRY-RUN] ' if dry_run else ''}VERKAUFE {pos['quantity']} x {asset['name']} "
                    f"@ {price:.4f} EUR = {value_eur:.2f} EUR"
                )

                if not dry_run:
                    result = await tr_client.sell(asset["isin"], pos["quantity"])
                    if result:
                        db.log_trade(
                            conn, asset["name"], asset["isin"],
                            "SELL", price, pos["quantity"], value_eur,
                            "SIGNAL", portfolio_value,
                        )

        except Exception as e:
            logger.error(f"Fehler bei {asset['name']}: {e}", exc_info=True)


# --- Modi ---

async def mode_setup():
    """Interaktiver Trade-Republic-Login – einmalig ausführen."""
    print("\n=== Trade Republic Login einrichten ===")
    print("pytr speichert den Geräteschlüssel in ~/.pytr/ – danach kein SMS mehr nötig.\n")

    phone = input("Telefonnummer (mit Ländervorwahl, z.B. +491234567890): ").strip()
    pin   = input("PIN (4 Stellen): ").strip()

    # Credentials in .env schreiben
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    env_content = env_path.read_text() if env_path.exists() else ""

    for key, val in [("TR_PHONE", phone), ("TR_PIN", pin)]:
        if f"{key}=" in env_content:
            lines = [
                f"{key}={val}" if line.startswith(f"{key}=") else line
                for line in env_content.splitlines()
            ]
            env_content = "\n".join(lines)
        else:
            env_content += f"\n{key}={val}\n"

    env_path.write_text(env_content)
    print(f"\nCredentials in {env_path} gespeichert.")

    # Probeverbindung
    print("\nVerbinde mit Trade Republic …")
    client = TRClient(phone, pin)
    await client.connect()
    print("Verbindung erfolgreich. Bot ist bereit.\n")
    await client.disconnect()


async def mode_status(conn):
    print_status(conn)


async def mode_run(conn, dry_run: bool):
    """Haupt-Loop: stündliche Prüfung."""
    if not config.TR_PHONE or not config.TR_PIN:
        logger.error(
            "TR_PHONE oder TR_PIN nicht gesetzt. "
            "Zuerst 'python bot.py --setup' ausführen."
        )
        sys.exit(1)

    label = "[DRY-RUN] " if dry_run else ""
    logger.info(f"{label}TradingBot gestartet. Intervall: {config.CHECK_INTERVAL_SECONDS}s")

    tr = TRClient(config.TR_PHONE, config.TR_PIN)
    await tr.connect()

    try:
        while True:
            logger.info(f"{label}=== Prüfzyklus startet ===")
            await run_cycle(tr, conn, dry_run=dry_run)
            logger.info(
                f"{label}=== Zyklus fertig. Nächster Check in "
                f"{config.CHECK_INTERVAL_SECONDS // 60} Minuten ==="
            )
            await asyncio.sleep(config.CHECK_INTERVAL_SECONDS)

    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        logger.info("Bot durch Benutzer gestoppt (Ctrl+C)")
    finally:
        await tr.disconnect()
        logger.info("Trade Republic Verbindung getrennt. Bot beendet.")


# --- Entry Point ---

def main():
    setup_logging()

    parser = argparse.ArgumentParser(description="TradingBot für Trade Republic")
    parser.add_argument("--setup",   action="store_true", help="Trade Republic Login einrichten")
    parser.add_argument("--status",  action="store_true", help="Positionen und P&L anzeigen")
    parser.add_argument("--dry-run", action="store_true", help="Signale berechnen, keine Orders")
    args = parser.parse_args()

    if args.setup:
        asyncio.run(mode_setup())
        return

    # Datenbank initialisieren
    conn = db.init_db(config.DB_PATH)

    if args.status:
        asyncio.run(mode_status(conn))
        return

    asyncio.run(mode_run(conn, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
