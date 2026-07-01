import numpy as np
import pandas as pd
import talib


def calculate_signals(df: pd.DataFrame, config) -> dict:
    """
    Berechnet RSI + Bollinger Bänder auf täglichen Schlusskursen.

    Kombinierte Kauflogik (ALLE Bedingungen müssen zutreffen):
      - RSI < RSI_BUY (überverkauft)
      - Preis <= unteres Bollinger Band
      - Preis > 200-Tage-MA (kein Kauf im Langzeit-Abwärtstrend)

    Verkauflogik (EINE Bedingung reicht):
      - RSI > RSI_SELL (überkauft)
      - Preis >= oberes Bollinger Band

    Erwartet df mit Spalte 'close'. Gibt Signal-Dict zurück.
    """
    min_rows = max(config.RSI_PERIOD, config.BB_PERIOD, config.MA_TREND_PERIOD)
    if len(df) < min_rows:
        return {
            "signal":   "HOLD",
            "rsi":      None,
            "bb_lower": None,
            "bb_upper": None,
            "ma200":    None,
            "price":    None,
            "reason":   f"Nicht genug Daten ({len(df)} < {min_rows})",
        }

    close = df["close"].astype(float).values

    # RSI
    rsi_arr = talib.RSI(close, timeperiod=config.RSI_PERIOD)
    rsi = float(rsi_arr[-1])

    # Bollinger Bänder
    upper_arr, _, lower_arr = talib.BBANDS(
        close,
        timeperiod=config.BB_PERIOD,
        nbdevup=config.BB_STD,
        nbdevdn=config.BB_STD,
        matype=0,  # SMA
    )
    bb_upper = float(upper_arr[-1])
    bb_lower = float(lower_arr[-1])

    # 200-Tage MA
    ma200_arr = talib.MA(close, timeperiod=config.MA_TREND_PERIOD)
    ma200 = float(ma200_arr[-1])

    price = float(close[-1])

    if np.isnan(rsi) or np.isnan(bb_upper) or np.isnan(bb_lower) or np.isnan(ma200):
        return {
            "signal":   "HOLD",
            "rsi":      None,
            "bb_lower": None,
            "bb_upper": None,
            "ma200":    None,
            "price":    price,
            "reason":   "Indikator-Berechnung liefert NaN (zu wenig Daten)",
        }

    base = {
        "rsi":      rsi,
        "bb_lower": bb_lower,
        "bb_upper": bb_upper,
        "ma200":    ma200,
        "price":    price,
    }

    # BUY: alle drei Bedingungen
    if rsi < config.RSI_BUY and price <= bb_lower and price > ma200:
        return {
            **base,
            "signal": "BUY",
            "reason": (
                f"RSI={rsi:.1f}<{config.RSI_BUY} | "
                f"Preis={price:.4f}<=BB_low={bb_lower:.4f} | "
                f"über MA200={ma200:.4f}"
            ),
        }

    # SELL: eine reicht
    if rsi > config.RSI_SELL:
        return {
            **base,
            "signal": "SELL",
            "reason": f"RSI={rsi:.1f}>{config.RSI_SELL}",
        }

    if price >= bb_upper:
        return {
            **base,
            "signal": "SELL",
            "reason": f"Preis={price:.4f}>=BB_up={bb_upper:.4f}",
        }

    return {
        **base,
        "signal": "HOLD",
        "reason": (
            f"RSI={rsi:.1f} | Preis={price:.4f} | "
            f"BB=[{bb_lower:.4f}–{bb_upper:.4f}] | MA200={ma200:.4f}"
        ),
    }


def score_sell_signal(sig: dict, config) -> float:
    """
    Bewertet die Stärke eines SELL-Signals für SHORT-Einstiege (0–100).
    Höher = stärker überkauft = besser für Short.

    RSI-Komponente  (0–50): Wie weit über RSI_SELL?
    BB-Komponente   (0–50): Wie weit über dem oberen Bollinger Band?
    """
    if sig.get("signal") != "SELL" or sig.get("rsi") is None:
        return 0.0

    rsi      = sig["rsi"]
    price    = sig["price"]
    bb_upper = sig["bb_upper"]

    rsi_score = max(0.0, (rsi - config.RSI_SELL) / (100 - config.RSI_SELL) * 50)

    if bb_upper and bb_upper > 0 and price > bb_upper:
        bb_depth = (price - bb_upper) / bb_upper
        bb_score = min(50.0, bb_depth * 500)
    else:
        bb_score = 0.0

    return round(rsi_score + bb_score, 2)


def score_signal(sig: dict, config) -> float:
    """
    Bewertet die Stärke eines BUY-Signals von 0–100.
    Wird genutzt um die besten Chancen aus dem Universum herauszupicken.

    RSI-Komponente  (0–50): Wie weit ist RSI unter RSI_BUY?
    BB-Komponente   (0–50): Wie weit ist der Preis unter dem unteren Bollinger Band?

    Nur BUY-Signale bekommen einen Score > 0.
    """
    if sig.get("signal") != "BUY" or sig.get("rsi") is None:
        return 0.0

    rsi      = sig["rsi"]
    price    = sig["price"]
    bb_lower = sig["bb_lower"]

    # RSI-Score: bei RSI=0 → 50 Punkte, bei RSI=RSI_BUY → 0 Punkte
    rsi_score = max(0.0, (config.RSI_BUY - rsi) / config.RSI_BUY * 50)

    # BB-Score: wie weit (%) ist der Preis unter dem unteren Band?
    # 1 % unter BB → 5 Punkte, 10 % unter BB → 50 Punkte (gedeckelt)
    if bb_lower and bb_lower > 0 and price < bb_lower:
        bb_depth  = (bb_lower - price) / bb_lower
        bb_score  = min(50.0, bb_depth * 500)
    else:
        bb_score = 0.0

    return round(rsi_score + bb_score, 2)
