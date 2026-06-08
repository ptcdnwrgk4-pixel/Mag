import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT / ".env")

# --- Trade Republic Login ---
TR_PHONE = os.getenv("TR_PHONE", "")
TR_PIN   = os.getenv("TR_PIN", "")

# --- Watchlist ---
# Passe diese Liste mit deinen eigenen Assets an.
# yahoo_ticker: Ticker für yfinance (historische Daten + Signalberechnung)
# isin: ISIN wie in Trade Republic angezeigt
# type: "stock", "crypto" oder "derivative"
WATCHLIST = [
    {
        "name":         "Bitcoin",
        "isin":         "XF000BTC0002",
        "yahoo_ticker": "BTC-EUR",
        "type":         "crypto",
    },
    {
        "name":         "Apple",
        "isin":         "US0378331005",
        "yahoo_ticker": "AAPL",
        "type":         "stock",
    },
    {
        "name":         "Nvidia",
        "isin":         "US67066G1040",
        "yahoo_ticker": "NVDA",
        "type":         "stock",
    },
]

# --- Strategie-Parameter ---
RSI_PERIOD      = 14    # RSI über 14 Perioden
RSI_BUY         = 30    # Kaufsignal wenn RSI < dieser Wert
RSI_SELL        = 70    # Verkaufssignal wenn RSI > dieser Wert
BB_PERIOD       = 20    # Bollinger Bänder über 20 Perioden
BB_STD          = 2     # Bollinger-Breite: 2 Standardabweichungen
MA_TREND_PERIOD = 200   # Langfristiger Trend: 200-Tage-MA
HISTORY_DAYS    = 250   # Historische Tage laden (muss > MA_TREND_PERIOD sein)

# --- Risikomanagement ---
MAX_POSITION_PCT   = 0.10  # Max. 10 % des Portfolios pro Position
MAX_OPEN_POSITIONS = 5     # Max. 5 gleichzeitige Positionen
STOP_LOSS_PCT      = 0.05  # Stop-Loss bei -5 % vom Kaufpreis
TAKE_PROFIT_PCT    = 0.10  # Take-Profit bei +10 % vom Kaufpreis
MAX_DAILY_LOSS_PCT = 0.03  # Bot stoppt sich bei -3 % Tagesverlust

# --- Bot-Verhalten ---
CHECK_INTERVAL_SECONDS = 3600  # Stündliche Prüfung

DB_PATH  = str(ROOT / "scripts" / "tradingbot" / "tradingbot.db")
LOG_PATH = str(ROOT / "scripts" / "tradingbot" / "bot.log")
