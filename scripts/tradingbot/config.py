import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT / ".env")

# --- Trade Republic Login ---
TR_PHONE = os.getenv("TR_PHONE", "")
TR_PIN   = os.getenv("TR_PIN", "")

# --- Universum ---
# call_isin:  ISIN eines Call-Knock-Outs auf dieses Asset (optional).
#             Wenn gesetzt und USE_LEVERAGE=True, kauft der Bot bei BUY-Signal
#             dieses Zertifikat statt das Underlying.
# short_isin: ISIN eines Short-Knock-Outs auf dieses Asset (optional).
#             Wenn gesetzt und SHORT_ENABLED=True, kauft der Bot bei starkem
#             SELL-Signal dieses Zertifikat (Wette auf fallenden Kurs).
#
# ISINs findest du in der Trade Republic App:
#   Asset suchen → Derivate → Knock-Outs → gewünschten Hebel wählen → ISIN kopieren
#
# WICHTIG: Knock-Outs können ausgeknockt werden (Totalverlust) und haben
# ein Ablaufdatum. Regelmäßig in der App prüfen und ISINs aktualisieren.

UNIVERSE = [
    # ── DAX / MDAX ──────────────────────────────────────────────────────────
    {"name": "SAP",               "isin": "DE0007164600", "yahoo_ticker": "SAP.DE",   "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Siemens",           "isin": "DE0007236101", "yahoo_ticker": "SIE.DE",   "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Allianz",           "isin": "DE0008404005", "yahoo_ticker": "ALV.DE",   "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Deutsche Telekom",  "isin": "DE0005557508", "yahoo_ticker": "DTE.DE",   "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "BASF",              "isin": "DE000BASF111", "yahoo_ticker": "BAS.DE",   "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "BMW",               "isin": "DE0005190003", "yahoo_ticker": "BMW.DE",   "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Volkswagen",        "isin": "DE0007664039", "yahoo_ticker": "VOW3.DE",  "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Bayer",             "isin": "DE000BAY0017", "yahoo_ticker": "BAYN.DE",  "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Mercedes-Benz",     "isin": "DE0007100000", "yahoo_ticker": "MBG.DE",   "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Deutsche Bank",     "isin": "DE0005140008", "yahoo_ticker": "DBK.DE",   "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Infineon",          "isin": "DE0006231004", "yahoo_ticker": "IFX.DE",   "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Adidas",            "isin": "DE000A1EWWW0", "yahoo_ticker": "ADS.DE",   "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "RWE",               "isin": "DE0007037129", "yahoo_ticker": "RWE.DE",   "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Münchener Rück",    "isin": "DE0008430026", "yahoo_ticker": "MUV2.DE",  "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Vonovia",           "isin": "DE000A1ML7J1", "yahoo_ticker": "VNA.DE",   "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Continental",       "isin": "DE0005439004", "yahoo_ticker": "CON.DE",   "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Rheinmetall",       "isin": "DE0007030009", "yahoo_ticker": "RHM.DE",   "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Porsche AG",        "isin": "DE000PAG9113", "yahoo_ticker": "P911.DE",  "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Beiersdorf",        "isin": "DE0005200000", "yahoo_ticker": "BEI.DE",   "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "E.ON",              "isin": "DE000ENAG999", "yahoo_ticker": "EOAN.DE",  "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Fresenius",         "isin": "DE0005785604", "yahoo_ticker": "FRE.DE",   "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Hannover Rück",     "isin": "DE0008402215", "yahoo_ticker": "HNR1.DE",  "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Commerzbank",       "isin": "DE000CBK1001", "yahoo_ticker": "CBK.DE",   "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Heidelberg Mat.",   "isin": "DE0006047004", "yahoo_ticker": "HDMG.DE",  "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Airbus",            "isin": "NL0000235190", "yahoo_ticker": "AIR.PA",   "type": "stock",  "call_isin": None, "short_isin": None},

    # ── US-Tech & Large Cap ──────────────────────────────────────────────────
    {"name": "Apple",             "isin": "US0378331005", "yahoo_ticker": "AAPL",     "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Microsoft",         "isin": "US5949181045", "yahoo_ticker": "MSFT",     "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Nvidia",            "isin": "US67066G1040", "yahoo_ticker": "NVDA",     "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Amazon",            "isin": "US0231351067", "yahoo_ticker": "AMZN",     "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Tesla",             "isin": "US88160R1014", "yahoo_ticker": "TSLA",     "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Meta",              "isin": "US30303M1027", "yahoo_ticker": "META",     "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Alphabet",          "isin": "US02079K3059", "yahoo_ticker": "GOOGL",    "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Netflix",           "isin": "US64110L1061", "yahoo_ticker": "NFLX",     "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "AMD",               "isin": "US0079031078", "yahoo_ticker": "AMD",      "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Intel",             "isin": "US4581401001", "yahoo_ticker": "INTC",     "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Broadcom",          "isin": "US11135F1012", "yahoo_ticker": "AVGO",     "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Qualcomm",          "isin": "US7475251036", "yahoo_ticker": "QCOM",     "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "JPMorgan",          "isin": "US46625H1005", "yahoo_ticker": "JPM",      "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Goldman Sachs",     "isin": "US38141G1040", "yahoo_ticker": "GS",       "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Visa",              "isin": "US92826C8394", "yahoo_ticker": "V",        "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Mastercard",        "isin": "US57636Q1040", "yahoo_ticker": "MA",       "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "PayPal",            "isin": "US70450Y1038", "yahoo_ticker": "PYPL",     "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Pfizer",            "isin": "US7170811035", "yahoo_ticker": "PFE",      "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "ExxonMobil",        "isin": "US30231G1022", "yahoo_ticker": "XOM",      "type": "stock",  "call_isin": None, "short_isin": None},
    {"name": "Johnson & Johnson", "isin": "US4781601046", "yahoo_ticker": "JNJ",      "type": "stock",  "call_isin": None, "short_isin": None},

    # ── Krypto ──────────────────────────────────────────────────────────────
    {"name": "Bitcoin",           "isin": "XF000BTC0002", "yahoo_ticker": "BTC-EUR",  "type": "crypto", "call_isin": None, "short_isin": None},
    {"name": "Ethereum",          "isin": "XF000ETH0002", "yahoo_ticker": "ETH-EUR",  "type": "crypto", "call_isin": None, "short_isin": None},
    {"name": "Solana",            "isin": "XF000SOL0002", "yahoo_ticker": "SOL-EUR",  "type": "crypto", "call_isin": None, "short_isin": None},
    {"name": "XRP",               "isin": "XF000XRP0002", "yahoo_ticker": "XRP-EUR",  "type": "crypto", "call_isin": None, "short_isin": None},
    {"name": "Cardano",           "isin": "XF000ADA0002", "yahoo_ticker": "ADA-EUR",  "type": "crypto", "call_isin": None, "short_isin": None},
    {"name": "Polkadot",          "isin": "XF000DOT0002", "yahoo_ticker": "DOT-EUR",  "type": "crypto", "call_isin": None, "short_isin": None},
    {"name": "Chainlink",         "isin": "XF000LNK0002", "yahoo_ticker": "LINK-EUR", "type": "crypto", "call_isin": None, "short_isin": None},
    {"name": "Litecoin",          "isin": "XF000LTC0002", "yahoo_ticker": "LTC-EUR",  "type": "crypto", "call_isin": None, "short_isin": None},
    {"name": "Avalanche",         "isin": "XF000AVA0002", "yahoo_ticker": "AVAX-EUR", "type": "crypto", "call_isin": None, "short_isin": None},
    {"name": "Dogecoin",          "isin": "XF000XDG0002", "yahoo_ticker": "DOGE-EUR", "type": "crypto", "call_isin": None, "short_isin": None},
]

# --- Strategie-Parameter ---
RSI_PERIOD      = 14    # RSI über 14 Perioden
RSI_BUY         = 30    # Long-Einstieg wenn RSI < dieser Wert
RSI_SELL        = 70    # Ausstieg / Short-Einstieg wenn RSI > dieser Wert
BB_PERIOD       = 20    # Bollinger Bänder über 20 Perioden
BB_STD          = 2     # Bollinger-Breite: 2 Standardabweichungen
MA_TREND_PERIOD = 200   # Langfristiger Trend-Filter: 200-Tage-MA
HISTORY_DAYS    = 250   # Historische Tage laden (muss > MA_TREND_PERIOD sein)

# --- Risikomanagement ---
MAX_POSITION_PCT   = 0.10  # Max. 10 % des Portfolios pro Position
MAX_OPEN_POSITIONS = 5     # Max. 5 gleichzeitige Positionen (Long + Short)
STOP_LOSS_PCT      = 0.05  # Stop-Loss bei -5 % (bezogen auf Underlying-Bewegung)
TAKE_PROFIT_PCT    = 0.10  # Take-Profit bei +10 % (bezogen auf Underlying-Bewegung)
MAX_DAILY_LOSS_PCT = 0.03  # Bot stoppt sich bei -3 % Tagesverlust

# --- Calls & Shorts ---
USE_LEVERAGE    = False  # True: call_isin statt Underlying bei BUY kaufen
SHORT_ENABLED   = True   # True: short_isin kaufen bei starkem SELL-Signal
SHORT_MIN_SCORE = 20.0   # Mindest-Score für SHORT-Einstieg (0–100)

# --- Bot-Verhalten ---
TOP_N_TRADES           = 3     # Pro Zyklus max. neue Käufe (Long + Short zusammen)
CHECK_INTERVAL_SECONDS = 3600  # Stündliche Prüfung

DB_PATH  = str(ROOT / "scripts" / "tradingbot" / "tradingbot.db")
LOG_PATH = str(ROOT / "scripts" / "tradingbot" / "bot.log")
