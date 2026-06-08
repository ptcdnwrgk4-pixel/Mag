# Plan: TradingBot – RSI Reversal + Bollinger Band Kombination

**Erstellt:** 2026-06-08
**Status:** Entwurf
**Anfrage:** Vollautomatischer TradingBot für Trade Republic (Aktien, Krypto, Derivate) mit kombinierter RSI + Bollinger-Band-Strategie und hartem Risikomanagement

---

## Überblick

### Was dieser Plan erreicht

Ein vollautomatischer TradingBot wird in `scripts/tradingbot/` aufgebaut. Er überwacht eine konfigurierbare Liste von Assets (Aktien, Krypto, Derivate), berechnet kontinuierlich RSI- und Bollinger-Band-Signale, und platziert bei Übereinstimmung beider Signale automatisch Kauf- bzw. Verkaufsorders über die inoffizielle Trade Republic API (`pytr`). Hartes Risikomanagement (Stop-Loss, Max-Position, Max-Tagesverlust) schützt das Kapital.

### Warum das zählt

Max trägt alle Aufgaben allein. Ein Bot, der Marktchancen rund um die Uhr überwacht und ausführt, ersetzt Stunden manuelles Chart-Monitoring. Das ist Bandbreite zurück – für das Café, für Flaconella, für alles andere.

---

## Aktueller Stand

### Bestehende relevante Struktur

- `scripts/` existiert noch nicht (wird mit diesem Plan angelegt)
- `module-installs/daten/scripts/` zeigt bewährte Muster: modulare Python-Scripts, SQLite-DB für Logging, `collect_*.py`-Konvention
- `module-installs/stimme/scripts/apps/command/` zeigt: `config.py`, `logger.py`, `db.py` als eigenständige Module
- `.env` existiert (API-Keys werden dort abgelegt, nie committed)
- `.gitignore` ist vorhanden (prüfen ob `.env` und DB-Dateien ausgeschlossen)

### Lücken oder Probleme, die der Plan löst

- Kein `scripts/`-Ordner auf Root-Ebene vorhanden → wird angelegt
- Kein `requirements.txt` → wird angelegt
- Keine Trade-Republic-Anbindung im System → wird via `pytr` gebaut
- Kein Risikomanagement → wird als eigenständiges Modul implementiert

---

## Geplante Änderungen

### Zusammenfassung der Änderungen

- `scripts/tradingbot/` mit 7 Python-Modulen anlegen
- `requirements.txt` auf Root-Ebene anlegen (pytr, pandas, ta, schedule, python-dotenv)
- `.env` um Trade-Republic-Credentials erweitern (Vorlage, nicht Werte)
- `.gitignore` prüfen und `tradingbot.db` ausschließen
- `CLAUDE.md` um Bot-Befehle ergänzen

### Neue Dateien

| Pfad | Zweck |
|---|---|
| `scripts/tradingbot/__init__.py` | Package-Marker |
| `scripts/tradingbot/config.py` | Alle Einstellungen: Assets, Strategie-Parameter, Risikolimits |
| `scripts/tradingbot/strategy.py` | RSI + Bollinger-Band-Berechnung, Signal-Logik |
| `scripts/tradingbot/trade_republic.py` | pytr-Anbindung: Preise abrufen, Orders platzieren |
| `scripts/tradingbot/risk_manager.py` | Positionsgröße, Stop-Loss, Tagesverlust-Limit |
| `scripts/tradingbot/db.py` | SQLite-Logging aller Trades und Signale |
| `scripts/tradingbot/bot.py` | Haupt-Orchestrator: Schleife, alle Module zusammenführen |
| `requirements.txt` | Python-Abhängigkeiten |

### Geänderte Dateien

| Pfad | Änderungen |
|---|---|
| `.gitignore` | `tradingbot.db` und `scripts/tradingbot/*.db` ausschließen |
| `CLAUDE.md` | Abschnitt „Bot starten / stoppen" in Befehle aufnehmen |

---

## Design-Entscheidungen

### Wichtige Entscheidungen

1. **pytr als Trade-Republic-Connector**: Einzige verfügbare Python-Bibliothek mit Order-Platzierung. Inoffiziell, aber aktiv gewartet. Risiko ist bekannt und akzeptiert.
2. **yfinance für historische Daten**: Die 200-Tage-MA braucht mindestens 200 Tage History. Trade Republic liefert keine langen Historien über pytr. yfinance holt die Daten kostenlos von Yahoo Finance.
3. **SQLite für Trade-Logging**: Kein Setup, kein Server, alles lokal. Passt zur Philosophie „Daten lokal".
4. **Beide Indikatoren müssen bestätigen (AND-Logik)**: RSI allein und Bollinger allein geben zu viele Fehlsignale. Erst wenn beide gleichzeitig feuern, wird gehandelt – das reduziert Trade-Frequenz, erhöht aber Trefferquote.
5. **Modulare Struktur statt Ein-Datei-Bot**: Jedes Modul ist einzeln testbar. `config.py` trennt Parameter von Logik. Bot lässt sich später erweitern ohne alles umzuschreiben.
6. **Max-Tagesverlust als hartes Limit**: Bot stoppt sich selbst bei -3% Tagesverlust. Schutz vor Margin-Calls und Panik-Kaskaden.

### Verworfene Alternativen

- **Eigener Websocket ohne pytr**: Zu viel Aufwand, unnötige Wartungslast. pytr ist die Community-Lösung.
- **Paper-Trading-Modus einbauen**: Max hat Echtgeld gewählt. Paper-Modus ist Komplexität ohne Nutzen für ihn jetzt.
- **Telegram-Benachrichtigungen**: Kann später via `stimme`-Modul ergänzt werden. Jetzt fokussiert bleiben.

### Offene Fragen

1. **Welche Assets konkret?** config.py kommt mit Beispiel-Liste (Bitcoin, Apple, Nvidia). Max muss die echten ISINs/Ticker nach Setup eintragen.
2. **Kapital pro Trade?** Standard wird 10% des Portfolios pro Position. Max kann in config.py anpassen.
3. **Trade-Republic-Login:** pytr braucht Telefonnummer + PIN beim ersten Start. Das passiert interaktiv beim ersten `python scripts/tradingbot/bot.py --setup`.

---

## Schritt-für-Schritt-Aufgaben

### Schritt 1: Ordnerstruktur anlegen

`scripts/tradingbot/` anlegen.

**Aktionen:**
- `scripts/tradingbot/` Ordner erstellen
- `scripts/tradingbot/__init__.py` anlegen (leer)

**Betroffene Dateien:**
- `scripts/tradingbot/__init__.py`

---

### Schritt 2: requirements.txt anlegen

Python-Abhängigkeiten definieren, die für den Bot nötig sind.

**Aktionen:**
- `requirements.txt` auf Root-Ebene anlegen mit:
  ```
  pytr>=0.1.0
  pandas>=2.0.0
  numpy>=1.24.0
  ta>=0.11.0
  yfinance>=0.2.0
  python-dotenv>=1.0.0
  schedule>=1.2.0
  ```

**Betroffene Dateien:**
- `requirements.txt`

---

### Schritt 3: config.py – Alle Einstellungen an einem Ort

Alle Parameter des Bots in einer Datei. Max ändert nur hier, nirgendwo sonst.

**Aktionen:**
- `scripts/tradingbot/config.py` anlegen mit folgenden Sektionen:

```python
# Trade Republic Login (aus .env)
TR_PHONE = os.getenv("TR_PHONE")       # Telefonnummer mit Ländervorwahl
TR_PIN   = os.getenv("TR_PIN")         # 4-stellige PIN

# Assets zum Beobachten
# Format: {"name": "...", "isin": "...", "yahoo_ticker": "...", "type": "stock|crypto|derivative"}
WATCHLIST = [
    {"name": "Bitcoin",  "isin": "XF000BTC0002", "yahoo_ticker": "BTC-EUR",  "type": "crypto"},
    {"name": "Apple",    "isin": "US0378331005",  "yahoo_ticker": "AAPL",     "type": "stock"},
    {"name": "Nvidia",   "isin": "US67066G1040",  "yahoo_ticker": "NVDA",     "type": "stock"},
]

# Strategie-Parameter
RSI_PERIOD      = 14     # RSI-Berechnung über 14 Perioden
RSI_BUY         = 30     # Kaufsignal wenn RSI unter diesem Wert
RSI_SELL        = 70     # Verkaufssignal wenn RSI über diesem Wert
BB_PERIOD       = 20     # Bollinger-Band-Berechnung über 20 Perioden
BB_STD          = 2      # Bollinger-Breite: 2 Standardabweichungen
MA_TREND_PERIOD = 200    # Langfristiger Trend: 200-Tage-MA
HISTORY_DAYS    = 250    # Tage historische Daten laden (muss > MA_TREND_PERIOD)

# Risikomanagement
MAX_POSITION_PCT   = 0.10   # Max 10% des Portfolios pro Position
MAX_OPEN_POSITIONS = 5      # Max 5 gleichzeitige Positionen
STOP_LOSS_PCT      = 0.05   # Stop-Loss bei -5% vom Kaufpreis
TAKE_PROFIT_PCT    = 0.10   # Take-Profit bei +10% vom Kaufpreis
MAX_DAILY_LOSS_PCT = 0.03   # Bot stoppt bei -3% Tagesverlust

# Bot-Verhalten
CHECK_INTERVAL_SECONDS = 3600  # Stündliche Prüfung (3600 = 1 Stunde)
DB_PATH = "scripts/tradingbot/tradingbot.db"
LOG_PATH = "scripts/tradingbot/bot.log"
```

**Betroffene Dateien:**
- `scripts/tradingbot/config.py`

---

### Schritt 4: db.py – Trade-Logging

SQLite-Datenbank für alle Trades und Signale. Vollständige Nachvollziehbarkeit.

**Aktionen:**
- `scripts/tradingbot/db.py` anlegen mit:
  - Funktion `init_db()`: Erstellt zwei Tabellen
    - `trades`: id, timestamp, asset_name, isin, action (BUY/SELL), price, quantity, value_eur, reason, portfolio_value_after
    - `signals`: id, timestamp, asset_name, isin, rsi, price, bb_lower, bb_upper, ma200, signal_type (BUY/SELL/HOLD), executed
  - Funktion `log_trade(conn, ...)`: Trade eintragen
  - Funktion `log_signal(conn, ...)`: Signal eintragen
  - Funktion `get_open_positions(conn)`: Alle offenen Positionen (Käufe ohne Verkauf)
  - Funktion `get_todays_pnl(conn)`: Heutiger Gewinn/Verlust in EUR
  - Funktion `get_entry_price(conn, isin)`: Kaufpreis für eine offene Position

**Betroffene Dateien:**
- `scripts/tradingbot/db.py`

---

### Schritt 5: strategy.py – Signal-Berechnung

Kernlogik. Berechnet RSI und Bollinger Bänder, gibt BUY/SELL/HOLD zurück.

**Aktionen:**
- `scripts/tradingbot/strategy.py` anlegen mit:
  - Funktion `calculate_signals(df, config)`:
    - Input: pandas DataFrame mit OHLCV-Daten (Open, High, Low, Close, Volume)
    - Berechnet RSI (ta-Bibliothek: `ta.momentum.RSIIndicator`)
    - Berechnet Bollinger Bänder (ta-Bibliothek: `ta.volatility.BollingerBands`)
    - Berechnet 200-Tage-MA (`df['close'].rolling(200).mean()`)
    - Nimmt letzten Wert (aktueller Zustand)
    - Returns: dict mit `{"signal": "BUY"|"SELL"|"HOLD", "rsi": float, "bb_lower": float, "bb_upper": float, "ma200": float, "price": float}`

  - **BUY-Logik (ALLE müssen wahr sein):**
    1. RSI < RSI_BUY (30)
    2. Aktueller Preis ≤ unteres Bollinger Band
    3. Aktueller Preis > 200-Tage-MA (kein Kauf im Langzeit-Abwärtstrend)

  - **SELL-Logik (EINES reicht):**
    1. RSI > RSI_SELL (70)
    2. Aktueller Preis ≥ oberes Bollinger Band

  - **HOLD:** Sonst

**Betroffene Dateien:**
- `scripts/tradingbot/strategy.py`

---

### Schritt 6: risk_manager.py – Kapitalschutz

Entscheidet, wie viel gekauft wird, und ob der Bot heute noch handeln darf.

**Aktionen:**
- `scripts/tradingbot/risk_manager.py` anlegen mit:
  - Funktion `can_trade_today(conn, portfolio_value, config)`: Prüft ob Tagesverlust unter Limit
  - Funktion `can_open_position(conn, config)`: Prüft ob max. offene Positionen erreicht
  - Funktion `calculate_position_size(portfolio_value, price, config)`: Berechnet Stückzahl (10% des Portfolios / Preis, auf ganze Einheiten abgerundet)
  - Funktion `should_stop_loss(entry_price, current_price, config)`: True wenn Verlust ≥ 5%
  - Funktion `should_take_profit(entry_price, current_price, config)`: True wenn Gewinn ≥ 10%

**Betroffene Dateien:**
- `scripts/tradingbot/risk_manager.py`

---

### Schritt 7: trade_republic.py – Broker-Anbindung

Verbindet sich mit Trade Republic via pytr. Holt Preise, platziert Orders.

**Aktionen:**
- `scripts/tradingbot/trade_republic.py` anlegen mit:
  - Klasse `TRClient`:
    - `__init__(phone, pin)`: pytr-Verbindung aufbauen
    - `get_portfolio()`: Gibt Portfoliowert in EUR zurück
    - `get_price(isin)`: Aktuellen Kurs eines Assets abrufen
    - `buy(isin, quantity)`: Marktorder kaufen, gibt Ausführungspreis zurück
    - `sell(isin, quantity)`: Marktorder verkaufen, gibt Ausführungspreis zurück
    - `get_position(isin)`: Aktuell gehaltene Stückzahl
  - Fehlerbehandlung: Verbindungsabbrüche werden geloggt, Bot läuft weiter

**Betroffene Dateien:**
- `scripts/tradingbot/trade_republic.py`

---

### Schritt 8: bot.py – Haupt-Orchestrator

Führt alles zusammen. Läuft in einer Schleife, prüft stündlich alle Assets.

**Aktionen:**
- `scripts/tradingbot/bot.py` anlegen mit:

```
Haupt-Schleife (alle CHECK_INTERVAL_SECONDS):
  1. Portfoliowert abrufen (TRClient)
  2. Prüfen ob Tagesverlust-Limit erreicht (RiskManager) → wenn ja, stoppen + loggen
  3. Für jedes Asset in WATCHLIST:
     a. Historische Daten laden (yfinance, HISTORY_DAYS Tage)
     b. Signale berechnen (strategy.calculate_signals)
     c. Signal loggen (db.log_signal)
     d. Wenn BUY-Signal:
        - Hat Bot diese Position bereits? Wenn ja, überspringen
        - Kann neue Position eröffnet werden? (RiskManager.can_open_position)
        - Positionsgröße berechnen (RiskManager.calculate_position_size)
        - Order platzieren (TRClient.buy)
        - Trade loggen (db.log_trade)
     e. Wenn SELL-Signal oder Stop-Loss oder Take-Profit:
        - Ist Position offen? Wenn ja, verkaufen
        - Order platzieren (TRClient.sell)
        - Trade loggen mit Reason (SIGNAL|STOP_LOSS|TAKE_PROFIT)
  4. Offene Positionen prüfen (Stop-Loss / Take-Profit unabhängig vom Signal)
  5. Warten bis nächster Check

CLI-Argumente:
  --setup    Interaktiver Login bei Trade Republic (einmalig)
  --status   Zeigt aktuelle Positionen + heutigen P&L
  --dry-run  Signale berechnen und loggen, keine echten Orders
```

**Betroffene Dateien:**
- `scripts/tradingbot/bot.py`

---

### Schritt 9: .env Vorlage ergänzen

Trade-Republic-Credentials als Kommentar-Vorlage in `.env` dokumentieren.

**Aktionen:**
- `.env` prüfen, ob TR_PHONE und TR_PIN schon drin sind
- Falls nicht: Kommentarzeilen als Vorlage einfügen:
  ```
  # Trade Republic Bot
  # TR_PHONE=+49...
  # TR_PIN=1234
  ```

**Betroffene Dateien:**
- `.env`

---

### Schritt 10: .gitignore prüfen

Sicherstellen dass Datenbankdatei und Logdatei nicht committed werden.

**Aktionen:**
- `.gitignore` lesen
- `tradingbot.db` und `*.log` hinzufügen falls nicht vorhanden

**Betroffene Dateien:**
- `.gitignore`

---

### Schritt 11: CLAUDE.md aktualisieren

Neuen Bot-Bereich in CLAUDE.md dokumentieren damit zukünftige Sitzungen wissen, was gebaut wurde.

**Aktionen:**
- Im Abschnitt „Befehle" folgenden Block ergänzen:

```markdown
### TradingBot starten
python scripts/tradingbot/bot.py          # Bot starten (Echtgeld, stündliche Prüfung)
python scripts/tradingbot/bot.py --setup  # Einmalig: Trade Republic Login einrichten
python scripts/tradingbot/bot.py --status # Aktuelle Positionen und P&L anzeigen
python scripts/tradingbot/bot.py --dry-run # Signale testen ohne echte Orders
```

- Im Abschnitt Ordner-Struktur: `scripts/tradingbot/` eintragen

**Betroffene Dateien:**
- `CLAUDE.md`

---

## Verbindungen und Abhängigkeiten

### Dateien, die auf diesen Bereich verweisen

- `CLAUDE.md` wird aktualisiert
- `.env` bekommt neue Felder
- `.gitignore` bekommt neue Ausschlüsse

### Updates für Konsistenz

- `context/current-data.md` kann später um Trading-Zahlen (P&L, Win-Rate) ergänzt werden
- Der Bot selbst erzeugt `tradingbot.db` – das ist die Wahrheitsquelle für Trades

### Auswirkung auf bestehende Abläufe

- Keine bestehenden Befehle werden verändert
- `/prime` kann später `--status` aufrufen um Trading-Stand zu zeigen
- Stimme-Modul (Telegram) kann später Benachrichtigungen bei Trade-Ausführung senden

---

## Prüf-Checkliste

- [ ] `pip install -r requirements.txt` läuft ohne Fehler
- [ ] `python scripts/tradingbot/bot.py --dry-run` startet ohne Exception
- [ ] `python scripts/tradingbot/bot.py --setup` führt Trade-Republic-Login durch
- [ ] `python scripts/tradingbot/bot.py --status` zeigt Portfolio-Stand
- [ ] Signale werden in `tradingbot.db` Tabelle `signals` geschrieben
- [ ] Stop-Loss wird bei -5% korrekt ausgelöst (Test mit Mock-Preis)
- [ ] Tagesverlust-Limit stoppt Bot bei -3%
- [ ] `tradingbot.db` ist in `.gitignore`
- [ ] CLAUDE.md spiegelt neue Bot-Befehle

---

## Erfolgskriterien

Die Umsetzung ist fertig, wenn:

1. `python scripts/tradingbot/bot.py --dry-run` stündlich alle WATCHLIST-Assets prüft, Signale berechnet und in der DB loggt – ohne Fehler
2. `python scripts/tradingbot/bot.py --setup` den Trade-Republic-Login einmalig abschließt und Credentials in `.env` persistiert
3. `python scripts/tradingbot/bot.py` (Echtgeld) automatisch kauft wenn RSI < 30 + Preis unter unterem Bollinger Band + über 200MA, und verkauft bei RSI > 70 oder Preis über oberem Bollinger Band oder Stop-Loss oder Take-Profit

---

## Notizen

- **pytr Single-Device-Limit:** Trade Republic erlaubt nur ein aktives Gerät. Wenn der Bot läuft, kann man die App gleichzeitig nutzen, aber zu viele gleichzeitige Requests können die Session unterbrechen. Bot fängt solche Fehler ab und versucht Reconnect.
- **Krypto 24/7:** Bot läuft durch, auch nachts. Aktien werden nur während Handelszeiten signifikante Bewegungen haben, aber Crypto braucht den Nacht-Check.
- **Derivate (ISINs):** Derivate haben oft kurze Laufzeiten. Yahoo Finance hat für viele Trade-Republic-Derivate keine Daten. Für Derivate wird der Bot reine TR-Preisdaten nutzen, ohne 200MA-Filter.
- **Weiterentwicklung:** Telegram-Benachrichtigungen via `stimme`-Modul sind der logische nächste Schritt nach erfolgreichem Betrieb.
