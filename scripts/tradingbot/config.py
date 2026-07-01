import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT / ".env")

# --- Trade Republic Login ---
TR_PHONE = os.getenv("TR_PHONE", "")
TR_PIN   = os.getenv("TR_PIN", "")

# --- Universum ---
# Der Bot scannt alle Assets und wählt die besten Signale automatisch aus.
# WICHTIG: Crypto-ISINs (XF000...) bitte einmalig in der TR-App verifizieren –
# Trade Republic kann diese intern ändern.
UNIVERSE = [
    # ── DAX / MDAX ──────────────────────────────────────────────────────────
    {"name": "SAP",               "isin": "DE0007164600", "yahoo_ticker": "SAP.DE",   "type": "stock"},
    {"name": "Siemens",           "isin": "DE0007236101", "yahoo_ticker": "SIE.DE",   "type": "stock"},
    {"name": "Allianz",           "isin": "DE0008404005", "yahoo_ticker": "ALV.DE",   "type": "stock"},
    {"name": "Deutsche Telekom",  "isin": "DE0005557508", "yahoo_ticker": "DTE.DE",   "type": "stock"},
    {"name": "BASF",              "isin": "DE000BASF111", "yahoo_ticker": "BAS.DE",   "type": "stock"},
    {"name": "BMW",               "isin": "DE0005190003", "yahoo_ticker": "BMW.DE",   "type": "stock"},
    {"name": "Volkswagen",        "isin": "DE0007664039", "yahoo_ticker": "VOW3.DE",  "type": "stock"},
    {"name": "Bayer",             "isin": "DE000BAY0017", "yahoo_ticker": "BAYN.DE",  "type": "stock"},
    {"name": "Mercedes-Benz",     "isin": "DE0007100000", "yahoo_ticker": "MBG.DE",   "type": "stock"},
    {"name": "Deutsche Bank",     "isin": "DE0005140008", "yahoo_ticker": "DBK.DE",   "type": "stock"},
    {"name": "Infineon",          "isin": "DE0006231004", "yahoo_ticker": "IFX.DE",   "type": "stock"},
    {"name": "Adidas",            "isin": "DE000A1EWWW0", "yahoo_ticker": "ADS.DE",   "type": "stock"},
    {"name": "RWE",               "isin": "DE0007037129", "yahoo_ticker": "RWE.DE",   "type": "stock"},
    {"name": "Münchener Rück",    "isin": "DE0008430026", "yahoo_ticker": "MUV2.DE",  "type": "stock"},
    {"name": "Vonovia",           "isin": "DE000A1ML7J1", "yahoo_ticker": "VNA.DE",   "type": "stock"},
    {"name": "Continental",       "isin": "DE0005439004", "yahoo_ticker": "CON.DE",   "type": "stock"},
    {"name": "Rheinmetall",       "isin": "DE0007030009", "yahoo_ticker": "RHM.DE",   "type": "stock"},
    {"name": "Porsche AG",        "isin": "DE000PAG9113", "yahoo_ticker": "P911.DE",  "type": "stock"},
    {"name": "Beiersdorf",        "isin": "DE0005200000", "yahoo_ticker": "BEI.DE",   "type": "stock"},
    {"name": "E.ON",              "isin": "DE000ENAG999", "yahoo_ticker": "EOAN.DE",  "type": "stock"},
    {"name": "Fresenius",         "isin": "DE0005785604", "yahoo_ticker": "FRE.DE",   "type": "stock"},
    {"name": "Hannover Rück",     "isin": "DE0008402215", "yahoo_ticker": "HNR1.DE",  "type": "stock"},
    {"name": "Commerzbank",       "isin": "DE000CBK1001", "yahoo_ticker": "CBK.DE",   "type": "stock"},
    {"name": "Heidelberg Mat.",   "isin": "DE0006047004", "yahoo_ticker": "HDMG.DE",  "type": "stock"},
    {"name": "Airbus",            "isin": "NL0000235190", "yahoo_ticker": "AIR.PA",   "type": "stock"},

    # ── US-Tech & Large Cap ──────────────────────────────────────────────────
    {"name": "Apple",             "isin": "US0378331005", "yahoo_ticker": "AAPL",     "type": "stock"},
    {"name": "Microsoft",         "isin": "US5949181045", "yahoo_ticker": "MSFT",     "type": "stock"},
    {"name": "Nvidia",            "isin": "US67066G1040", "yahoo_ticker": "NVDA",     "type": "stock"},
    {"name": "Amazon",            "isin": "US0231351067", "yahoo_ticker": "AMZN",     "type": "stock"},
    {"name": "Tesla",             "isin": "US88160R1014", "yahoo_ticker": "TSLA",     "type": "stock"},
    {"name": "Meta",              "isin": "US30303M1027", "yahoo_ticker": "META",     "type": "stock"},
    {"name": "Alphabet",          "isin": "US02079K3059", "yahoo_ticker": "GOOGL",    "type": "stock"},
    {"name": "Netflix",           "isin": "US64110L1061", "yahoo_ticker": "NFLX",     "type": "stock"},
    {"name": "AMD",               "isin": "US0079031078", "yahoo_ticker": "AMD",      "type": "stock"},
    {"name": "Intel",             "isin": "US4581401001", "yahoo_ticker": "INTC",     "type": "stock"},
    {"name": "Broadcom",          "isin": "US11135F1012", "yahoo_ticker": "AVGO",     "type": "stock"},
    {"name": "Qualcomm",          "isin": "US7475251036", "yahoo_ticker": "QCOM",     "type": "stock"},
    {"name": "JPMorgan",          "isin": "US46625H1005", "yahoo_ticker": "JPM",      "type": "stock"},
    {"name": "Goldman Sachs",     "isin": "US38141G1040", "yahoo_ticker": "GS",       "type": "stock"},
    {"name": "Visa",              "isin": "US92826C8394", "yahoo_ticker": "V",        "type": "stock"},
    {"name": "Mastercard",        "isin": "US57636Q1040", "yahoo_ticker": "MA",       "type": "stock"},
    {"name": "PayPal",            "isin": "US70450Y1038", "yahoo_ticker": "PYPL",     "type": "stock"},
    {"name": "Pfizer",            "isin": "US7170811035", "yahoo_ticker": "PFE",      "type": "stock"},
    {"name": "ExxonMobil",        "isin": "US30231G1022", "yahoo_ticker": "XOM",      "type": "stock"},
    {"name": "Johnson & Johnson", "isin": "US4781601046", "yahoo_ticker": "JNJ",      "type": "stock"},

    # ── Krypto ──────────────────────────────────────────────────────────────
    {"name": "Bitcoin",           "isin": "XF000BTC0002", "yahoo_ticker": "BTC-EUR",  "type": "crypto"},
    {"name": "Ethereum",          "isin": "XF000ETH0002", "yahoo_ticker": "ETH-EUR",  "type": "crypto"},
    {"name": "Solana",            "isin": "XF000SOL0002", "yahoo_ticker": "SOL-EUR",  "type": "crypto"},
    {"name": "XRP",               "isin": "XF000XRP0002", "yahoo_ticker": "XRP-EUR",  "type": "crypto"},
    {"name": "Cardano",           "isin": "XF000ADA0002", "yahoo_ticker": "ADA-EUR",  "type": "crypto"},
    {"name": "Polkadot",          "isin": "XF000DOT0002", "yahoo_ticker": "DOT-EUR",  "type": "crypto"},
    {"name": "Chainlink",         "isin": "XF000LNK0002", "yahoo_ticker": "LINK-EUR", "type": "crypto"},
    {"name": "Litecoin",          "isin": "XF000LTC0002", "yahoo_ticker": "LTC-EUR",  "type": "crypto"},
    {"name": "Avalanche",         "isin": "XF000AVA0002", "yahoo_ticker": "AVAX-EUR", "type": "crypto"},
    {"name": "Dogecoin",          "isin": "XF000XDG0002", "yahoo_ticker": "DOGE-EUR", "type": "crypto"},
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
TOP_N_TRADES           = 3     # Pro Zyklus maximal diese Anzahl neuer Käufe
CHECK_INTERVAL_SECONDS = 3600  # Stündliche Prüfung

DB_PATH  = str(ROOT / "scripts" / "tradingbot" / "tradingbot.db")
LOG_PATH = str(ROOT / "scripts" / "tradingbot" / "bot.log")
