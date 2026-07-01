"""
TradingBot – Haupt-Orchestrator

Strategie: RSI Reversal + Bollinger Band Reversal
Richtungen: Long (Underlying oder Call-KO), Short (Short-KO)
Broker: Trade Republic (via pytr, inoffizielle API)

Starten:
  python bot.py              → Echtgeld-Betrieb, stündliche Prüfung
  python bot.py --setup      → Einmaliger Trade-Republic-Login einrichten
  python bot.py --status     → Positionen und P&L anzeigen
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

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
import db
import strategy
import risk_manager as risk
from trade_republic import TRClient


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
    longs  = db.get_open_longs(conn)
    shorts = db.get_open_shorts(conn)
    pnl    = db.get_todays_pnl(conn)

    print("\n" + "=" * 65)
    print(f"  TradingBot Status  –  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 65)

    print(f"\n  Long-Positionen ({len(longs)}):")
    if longs:
        for p in longs:
            label = "(Call-KO)" if p["isin"] != p["underlying_isin"] else ""
            print(
                f"    {p['asset_name']:20s}  {p['quantity']:>12.6f}  "
                f"Ø {p['avg_entry_price']:>10.4f} EUR  {label}"
            )
    else:
        print("    keine")

    print(f"\n  Short-Positionen ({len(shorts)}):")
    if shorts:
        for p in shorts:
            print(
                f"    {p['asset_name']:20s}  {p['quantity']:>12.6f}  "
                f"Underlying-Einstieg: {p['avg_underlying_entry']:>10.4f} EUR"
            )
    else:
        print("    keine")

    sign = "+" if pnl >= 0 else ""
    print(f"\n  Heutiger P&L: {sign}{pnl:.2f} EUR")
    print("=" * 65 + "\n")


# --- Stop-Loss / Take-Profit für Shorts ---
# Für Short-Positionen prüfen wir die Underlying-Preisentwicklung (nicht den KO-Preis):
# → Underlying steigt +5 % → Stop-Loss (wir verlieren mit dem Short)
# → Underlying fällt -10 % → Take-Profit (wir gewinnen mit dem Short)

def short_stop_loss(underlying_entry: float, current_underlying: float, cfg) -> bool:
    if underlying_entry <= 0:
        return False
    return (current_underlying - underlying_entry) / underlying_entry >= cfg.STOP_LOSS_PCT

def short_take_profit(underlying_entry: float, current_underlying: float, cfg) -> bool:
    if underlying_entry <= 0:
        return False
    return (underlying_entry - current_underlying) / underlying_entry >= cfg.TAKE_PROFIT_PCT


# --- Kern-Zyklus ---

async def run_cycle(tr: TRClient, conn, dry_run: bool) -> None:
    label = "[DRY-RUN] " if dry_run else ""

    # 1. Portfoliowert
    portfolio_value = await tr.get_portfolio_value()
    if portfolio_value <= 0:
        logger.warning("Portfoliowert = 0 oder nicht abrufbar – Zyklus übersprungen")
        return
    logger.info(f"Portfoliowert: {portfolio_value:.2f} EUR")

    # 2. Tagesverlust-Check
    if not risk.can_trade_today(conn, portfolio_value, config):
        pnl = db.get_todays_pnl(conn)
        logger.warning(
            f"Tagesverlust-Limit erreicht ({pnl:.2f} EUR). Bot pausiert für heute."
        )
        return

    # 3. Stop-Loss / Take-Profit für offene Long-Positionen
    for pos in db.get_open_longs(conn):
        underlying_price = await tr.get_price(pos["underlying_isin"])
        if underlying_price is None:
            continue
        entry = pos["avg_entry_price"]

        if risk.should_stop_loss(entry, underlying_price, config):
            pct = (entry - underlying_price) / entry * 100
            logger.warning(f"LONG STOP-LOSS: {pos['asset_name']} | -{pct:.1f}%")
            if not dry_run:
                result = await tr.sell(pos["isin"], pos["quantity"])
                if result:
                    db.log_trade(
                        conn, pos["asset_name"], pos["isin"], "SELL",
                        underlying_price, pos["quantity"],
                        underlying_price * pos["quantity"], "STOP_LOSS",
                        portfolio_value, pos["underlying_isin"], "LONG", underlying_price,
                    )

        elif risk.should_take_profit(entry, underlying_price, config):
            pct = (underlying_price - entry) / entry * 100
            logger.info(f"LONG TAKE-PROFIT: {pos['asset_name']} | +{pct:.1f}%")
            if not dry_run:
                result = await tr.sell(pos["isin"], pos["quantity"])
                if result:
                    db.log_trade(
                        conn, pos["asset_name"], pos["isin"], "SELL",
                        underlying_price, pos["quantity"],
                        underlying_price * pos["quantity"], "TAKE_PROFIT",
                        portfolio_value, pos["underlying_isin"], "LONG", underlying_price,
                    )

    # 4. Stop-Loss / Take-Profit für offene Short-Positionen
    for pos in db.get_open_shorts(conn):
        underlying_price = await tr.get_price(pos["underlying_isin"])
        if underlying_price is None:
            continue
        entry = pos["avg_underlying_entry"] or pos["avg_entry_price"]

        if short_stop_loss(entry, underlying_price, config):
            pct = (underlying_price - entry) / entry * 100
            logger.warning(f"SHORT STOP-LOSS: {pos['asset_name']} | Underlying +{pct:.1f}%")
            if not dry_run:
                result = await tr.sell(pos["isin"], pos["quantity"])
                if result:
                    current_price = await tr.get_price(pos["isin"]) or underlying_price
                    db.log_trade(
                        conn, pos["asset_name"], pos["isin"], "SELL",
                        current_price, pos["quantity"],
                        current_price * pos["quantity"], "STOP_LOSS",
                        portfolio_value, pos["underlying_isin"], "SHORT", underlying_price,
                    )

        elif short_take_profit(entry, underlying_price, config):
            pct = (entry - underlying_price) / entry * 100
            logger.info(f"SHORT TAKE-PROFIT: {pos['asset_name']} | Underlying -{pct:.1f}%")
            if not dry_run:
                result = await tr.sell(pos["isin"], pos["quantity"])
                if result:
                    current_price = await tr.get_price(pos["isin"]) or underlying_price
                    db.log_trade(
                        conn, pos["asset_name"], pos["isin"], "SELL",
                        current_price, pos["quantity"],
                        current_price * pos["quantity"], "TAKE_PROFIT",
                        portfolio_value, pos["underlying_isin"], "SHORT", underlying_price,
                    )

    # 5. Universum scannen
    buy_candidates   = []   # (score, asset, sig)  → Long-Einstieg
    short_candidates = []   # (score, asset, sig)  → Short-Einstieg
    sell_longs       = []   # (asset, sig, pos)     → Long schließen
    close_shorts     = []   # (asset, pos)          → Short schließen (weil BUY-Signal)

    logger.info(f"Scanne {len(config.UNIVERSE)} Assets …")

    for asset in config.UNIVERSE:
        try:
            hist_df = load_history(asset["yahoo_ticker"], config.HISTORY_DAYS)
            if hist_df is None or len(hist_df) < config.MA_TREND_PERIOD:
                logger.debug(f"{asset['name']}: zu wenig Daten")
                continue

            sig = strategy.calculate_signals(hist_df, config)
            db.log_signal(
                conn, asset["name"], asset["isin"],
                sig["rsi"], sig["price"],
                sig["bb_lower"], sig["bb_upper"], sig["ma200"],
                sig["signal"],
            )

            underlying = asset["isin"]

            if sig["signal"] == "BUY":
                # Offene Short-Position schließen
                if db.has_open_short(conn, underlying):
                    shorts = db.get_open_shorts(conn)
                    pos = next((p for p in shorts if p["underlying_isin"] == underlying), None)
                    if pos:
                        close_shorts.append((asset, pos))

                # Long-Kandidat wenn noch keine Long-Position
                if not db.has_open_long(conn, underlying):
                    score = strategy.score_signal(sig, config)
                    buy_candidates.append((score, asset, sig))
                    logger.info(f"  BUY   {asset['name']:20s} | Score={score:5.1f} | {sig['reason']}")

            elif sig["signal"] == "SELL":
                # Offene Long-Position schließen
                if db.has_open_long(conn, underlying):
                    longs = db.get_open_longs(conn)
                    pos = next((p for p in longs if p["underlying_isin"] == underlying), None)
                    if pos:
                        sell_longs.append((asset, sig, pos))
                        logger.info(f"  SELL  {asset['name']:20s} | {sig['reason']}")

                # Short-Kandidat wenn SHORT aktiviert und ISIN hinterlegt
                if (
                    config.SHORT_ENABLED
                    and asset.get("short_isin")
                    and not db.has_open_short(conn, underlying)
                ):
                    score = strategy.score_sell_signal(sig, config)
                    if score >= config.SHORT_MIN_SCORE:
                        short_candidates.append((score, asset, sig))
                        logger.info(f"  SHORT {asset['name']:20s} | Score={score:5.1f} | {sig['reason']}")

            else:
                logger.debug(f"  HOLD  {asset['name']:20s} | {sig['reason']}")

        except Exception as e:
            logger.error(f"Scan-Fehler {asset['name']}: {e}", exc_info=True)

    # 6. Shorts schließen (BUY-Signal auf Underlying)
    for asset, pos in close_shorts:
        try:
            current_price = sig["price"]  # Preis des Short-KOs
            value_eur = current_price * pos["quantity"]
            logger.info(f"{label}CLOSE SHORT: {pos['quantity']} x {asset['name']}")
            if not dry_run:
                result = await tr.sell(pos["isin"], pos["quantity"])
                if result:
                    db.log_trade(
                        conn, asset["name"], pos["isin"], "SELL",
                        current_price, pos["quantity"], value_eur, "SIGNAL_REVERSE",
                        portfolio_value, asset["isin"], "SHORT",
                    )
        except Exception as e:
            logger.error(f"Close-Short-Fehler {asset['name']}: {e}", exc_info=True)

    # 7. Longs schließen
    for asset, sig, pos in sell_longs:
        try:
            price     = sig["price"]
            value_eur = price * pos["quantity"]
            logger.info(f"{label}CLOSE LONG: {pos['quantity']} x {asset['name']} @ {price:.4f} EUR")
            if not dry_run:
                result = await tr.sell(pos["isin"], pos["quantity"])
                if result:
                    db.log_trade(
                        conn, asset["name"], pos["isin"], "SELL",
                        price, pos["quantity"], value_eur, "SIGNAL",
                        portfolio_value, asset["isin"], "LONG", price,
                    )
        except Exception as e:
            logger.error(f"Close-Long-Fehler {asset['name']}: {e}", exc_info=True)

    # 8. Freie Slots berechnen
    total_open = len(db.get_open_positions(conn))
    free_slots = max(0, config.MAX_OPEN_POSITIONS - total_open)
    new_trades = 0

    # 9. Top-N Longs öffnen
    buy_candidates.sort(key=lambda x: x[0], reverse=True)
    if buy_candidates:
        logger.info(f"{len(buy_candidates)} Long-Kandidaten | freie Slots: {free_slots}")

    for score, asset, sig in buy_candidates:
        if new_trades >= config.TOP_N_TRADES or free_slots <= 0:
            break
        try:
            trade_isin = (
                asset["call_isin"] if config.USE_LEVERAGE and asset.get("call_isin")
                else asset["isin"]
            )
            price    = sig["price"]
            quantity = risk.calculate_position_size(portfolio_value, price, config)
            if quantity <= 0:
                continue
            value_eur = price * quantity
            kind = "CALL-KO" if trade_isin != asset["isin"] else "LONG"
            logger.info(
                f"{label}KAUFE {kind}: {quantity} x {asset['name']} "
                f"@ {price:.4f} EUR = {value_eur:.2f} EUR  [Score={score:.1f}]"
            )
            if not dry_run:
                result = await tr.buy(trade_isin, quantity)
                if result:
                    db.log_trade(
                        conn, asset["name"], trade_isin, "BUY",
                        price, quantity, value_eur, "SIGNAL",
                        portfolio_value, asset["isin"], "LONG", price,
                    )
                    new_trades += 1
                    free_slots -= 1
            else:
                new_trades += 1
                free_slots -= 1
        except Exception as e:
            logger.error(f"Buy-Fehler {asset['name']}: {e}", exc_info=True)

    # 10. Top-N Shorts öffnen
    short_candidates.sort(key=lambda x: x[0], reverse=True)
    if short_candidates:
        logger.info(f"{len(short_candidates)} Short-Kandidaten | freie Slots: {free_slots}")

    for score, asset, sig in short_candidates:
        if new_trades >= config.TOP_N_TRADES or free_slots <= 0:
            break
        try:
            short_isin       = asset["short_isin"]
            underlying_price = sig["price"]
            short_price      = await tr.get_price(short_isin) if not dry_run else sig["price"]
            if short_price is None:
                logger.warning(f"{asset['name']}: Short-KO-Preis nicht abrufbar")
                continue
            quantity  = risk.calculate_position_size(portfolio_value, short_price, config)
            if quantity <= 0:
                continue
            value_eur = short_price * quantity
            logger.info(
                f"{label}KAUFE SHORT-KO: {quantity} x {asset['name']} "
                f"@ {short_price:.4f} EUR = {value_eur:.2f} EUR  [Score={score:.1f}]"
            )
            if not dry_run:
                result = await tr.buy(short_isin, quantity)
                if result:
                    db.log_trade(
                        conn, asset["name"], short_isin, "BUY",
                        short_price, quantity, value_eur, "SIGNAL",
                        portfolio_value, asset["isin"], "SHORT", underlying_price,
                    )
                    new_trades += 1
                    free_slots -= 1
            else:
                new_trades += 1
                free_slots -= 1
        except Exception as e:
            logger.error(f"Short-Fehler {asset['name']}: {e}", exc_info=True)


# --- Modi ---

async def mode_setup():
    print("\n=== Trade Republic Login einrichten ===")
    print("pytr speichert den Geräteschlüssel in ~/.pytr/ – danach kein SMS mehr nötig.\n")
    phone = input("Telefonnummer (mit Ländervorwahl, z.B. +491234567890): ").strip()
    pin   = input("PIN (4 Stellen): ").strip()

    env_path    = Path(__file__).resolve().parent.parent.parent / ".env"
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

    print("\nVerbinde mit Trade Republic …")
    client = TRClient(phone, pin)
    await client.connect()
    print("Verbindung erfolgreich. Bot ist bereit.\n")
    await client.disconnect()


async def mode_status(conn):
    print_status(conn)


async def mode_run(conn, dry_run: bool):
    if not config.TR_PHONE or not config.TR_PIN:
        logger.error("TR_PHONE oder TR_PIN nicht gesetzt. Zuerst --setup ausführen.")
        sys.exit(1)

    label = "[DRY-RUN] " if dry_run else ""
    logger.info(
        f"{label}TradingBot gestartet | "
        f"Long={'Call-KO' if config.USE_LEVERAGE else 'Underlying'} | "
        f"Short={'aktiv' if config.SHORT_ENABLED else 'deaktiviert'} | "
        f"Universum={len(config.UNIVERSE)} Assets | "
        f"Top-N={config.TOP_N_TRADES}"
    )

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
    except (asyncio.CancelledError, KeyboardInterrupt):
        logger.info("Bot gestoppt.")
    finally:
        await tr.disconnect()
        logger.info("Verbindung getrennt.")


# --- Entry Point ---

def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="TradingBot für Trade Republic")
    parser.add_argument("--setup",   action="store_true")
    parser.add_argument("--status",  action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.setup:
        asyncio.run(mode_setup())
        return

    conn = db.init_db(config.DB_PATH)

    if args.status:
        asyncio.run(mode_status(conn))
        return

    asyncio.run(mode_run(conn, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
