# Architektur Deep Dive — Telegram KI Command Bot

Die internen Muster, das Kostenmodell und die Erweiterungspunkte. Lies das hier, wenn der Bot läuft und du verstehen oder erweitern willst, was unter der Haube passiert.

---

## 1. Prime --> Task Pattern (persistente Sessions)

Das Kern-Ausführungsmodell besteht aus zwei Schritten:

```
Schritt 1: PRIME
  - Startet einen Claude Code Mitarbeiter
  - Mitarbeiter liest die Workspace Kontext-Dateien (via prime command)
  - Gibt eine session_id zurück

Schritt 2: TASK
  - Setzt die geprimete Session via session_id fort
  - Schickt die eigentliche Anfrage des Users
  - Mitarbeiter arbeitet mit komplettem Kontext im Hintergrund
  - Gibt Ergebnis-Text, Kosten und neue session_id zurück
```

**Warum zwei Schritte?**

Der Prime Schritt ist teuer (der Mitarbeiter liest 5 bis 15 Dateien, $0.02 bis $0.10). Sobald aber geprimet, sind Folge-Tasks auf derselben Session günstig, weil der Kontext schon geladen ist. Der General Mitarbeiter primet einmal und übernimmt danach dutzende Folgenachrichten auf derselben Session.

**Implementierung in `agent_sdk.py` (Worker Layer):**

```python
# Schritt 1: Prime — erstellt eine neue Session
result = await run_prime(workspace_dir=..., model="sonnet")
session_id = result.session_id

# Schritt 2: Task — setzt die Session fort
result = await run_task_on_session(
    prompt="What were last month's revenue numbers?",
    session_id=session_id,
    workspace_dir=...,
)
```

Das `ClaudeAgentOptions` Objekt nutzt `resume = session_id`, um eine bestehende Session fortzuführen statt eine neue zu starten.

---

## 2. Session Resume (persistente Mitarbeiter)

Der General Mitarbeiter und gespawnte Mitarbeiter-Topics laufen auf persistenten Sessions, die über Nachrichten UND Bot-Restarts hinweg überleben.

**So funktioniert es:**

1. `SessionManager` speichert Session Metadaten in `data/command/agent_sessions.json`
2. Jede Session wird über einen Topic Identifier indiziert (z.B. `"general"` oder `"12345"` für eine Topic-ID)
3. Wenn der Bot neu startet, liest er die JSON Datei und verbindet sich wieder mit bestehenden Sessions
4. Der `resume` Parameter des Claude Agent SDK übernimmt die eigentliche Reconnection

**Session Lifecycle:**

```
User schickt erste Nachricht in General
  --> Keine Session gefunden
  --> Prime (erstellt Session)
  --> session_id auf Disk speichern
  --> Task auf Session ausführen
  --> Antwort zurückgeben

User schickt zweite Nachricht
  --> Session im Manager gefunden
  --> Task auf bestehender Session ausführen (kein Prime nötig)
  --> Mitarbeiter hat vollen Kontext aus vorherigen Interaktionen
  --> Antwort zurückgeben

Bot startet neu
  --> Sessions von Disk laden
  --> User schickt Nachricht
  --> Session gefunden (von Disk geladen)
  --> Session via SDK fortsetzen
  --> Mitarbeiter hat den kompletten vorherigen Kontext
```

**Datenformat (`agent_sessions.json`):**

```json
{
  "general": {
    "session_id": "sess_abc123...",
    "model": "sonnet",
    "created": "2026-02-25T10:30:00Z",
    "name": "General",
    "total_cost": 1.45,
    "total_turns": 87,
    "last_input_tokens": 145000
  },
  "98765": {
    "session_id": "sess_def456...",
    "model": "opus",
    "created": "2026-02-25T14:00:00Z",
    "name": "Agent - Feb 25 2:00PM",
    "total_cost": 0.32,
    "total_turns": 12,
    "last_input_tokens": 52000
  }
}
```

**Thread Safety:** Der SessionManager nutzt `fcntl.flock()` für Read Locking und atomare Writes (`tempfile` + `os.replace`) für Write Safety. Mehrere Prozesse können sicher lesen, Writes werden serialisiert.

---

## 3. Message Debounce (1.5s Batching)

Telegram splittet lange einkopierte Texte in mehrere Nachrichten. User feuern auch schnelle aufeinanderfolgende Nachrichten ab. Ohne Debouncing würde jede Nachricht einen eigenen Mitarbeiter-Call triggern.

**Der Debounce Mechanismus:**

```
Nachricht 1 kommt an --> starte 1.5s Timer
Nachricht 2 kommt an (0.5s später) --> Timer abbrechen, neuen 1.5s Timer starten
Nachricht 3 kommt an (0.3s später) --> Timer abbrechen, neuen 1.5s Timer starten
Timer läuft ab (1.5s nach Nachricht 3) --> alle 3 als eine kombinierte Nachricht raushauen
```

**Implementierung in `bot.py`:**

```python
_DEBOUNCE_SECONDS = 1.5

def _enqueue_and_debounce(item: _BufferedItem) -> None:
    global _message_buffer, _debounce_task
    _message_buffer.append(item)
    if _debounce_task and not _debounce_task.done():
        _debounce_task.cancel()
    async def _debounce_fire():
        await asyncio.sleep(_DEBOUNCE_SECONDS)
        await _flush_message_buffer()
    _debounce_task = asyncio.create_task(_debounce_fire())
```

Der Buffer sammelt `_BufferedItem` Objekte, die Text, transkribierte Voice oder Fotos sein können. Wenn der Timer feuert, werden alle Items zusammengefügt und als ein einziger Request verarbeitet.

**Der 1.5s Wert** ist eine Balance zwischen Reaktionsfähigkeit (niedriger = schneller) und Batching-Effektivität (höher = fängt mehr gesplittete Nachrichten). Passe `_DEBOUNCE_SECONDS` an, wenn nötig.

---

## 4. Owner Lock

Der Bot sperrt sich auf den ersten menschlichen User, der eine Nachricht schickt. Alle weiteren Nachrichten von anderen Usern werden still ignoriert.

**Implementierung in `bot.py`:**

```python
_owner_id: int | None = None

def _is_authorized(message: Message) -> bool:
    global _owner_id
    if not message.from_user or message.from_user.is_bot:
        return False
    if _owner_id is None:
        _owner_id = message.from_user.id
        return True
    return message.from_user.id == _owner_id
```

**Warum Auto-Capture statt Config-Wert?** Es spart einen Setup Schritt. Beim ersten Schreiben an den Bot sperrt er sich auf dich. Wenn du den Owner wechseln willst, startest du den Bot neu und der neue Owner schickt die erste Nachricht.

**Für Multi-User Support:** Ersetz das durch einen Whitelist Check gegen konfigurierte User-IDs:
```python
AUTHORIZED_USERS = {123456789, 987654321}  # Aus der Config

def _is_authorized(message: Message) -> bool:
    if not message.from_user or message.from_user.is_bot:
        return False
    return message.from_user.id in AUTHORIZED_USERS
```

---

## 5. Context Warning (180K Token Schwelle)

Das Context Window von Claude liegt bei 200K Tokens. Wenn Gespräche länger werden, füllt sich der Kontext. Bei 180K Tokens (90%) schickt der Bot eine Warnung.

**Wie das getrackt wird:**

Nach jeder Mitarbeiter-Interaktion enthält das Result ein `usage` Feld mit `input_tokens`. Der SessionManager speichert `last_input_tokens` pro Session.

```python
if input_tokens > self.config.context_warning_threshold:
    pct = int((input_tokens / 200000) * 100)
    await bot.send_message(
        text=f"Context at {pct}% ({input_tokens:,} tokens). Use /compact or /new.",
    )
```

**Optionen für den User bei vollem Kontext:**
- `/compact` bittet den Mitarbeiter, seinen Kontext zusammenzufassen und zu komprimieren (Teilentlastung)
- `/reset` löscht die Session komplett, die nächste Nachricht startet frisch
- `/new` spawnt einen frischen Mitarbeiter in einem neuen Topic (alte Session bleibt erhalten)

Die Schwelle ist konfigurierbar via `COMMAND_CONTEXT_WARNING_TOKENS` in der `.env`. Default: 180,000.

---

## 6. File Path Detection (Auto-Delivery)

Wenn Mitarbeiter Dateien erstellen (Charts, PDFs, Dokumente), erkennt der Bot die Datei-Pfade im Response-Text automatisch und liefert sie aus.

**Detection Patterns:**

```python
# Chart Bilder: ![title](outputs/charts/filename.png)
extract_image_paths(text)  # gibt [(title, path), ...] zurück

# Andere erstellte Dateien: erkennt Pfade wie outputs/reports/file.pdf
_extract_created_files(text)  # gibt [path, ...] zurück
```

**Delivery Logic:**
- Bilddateien (`.png`, `.jpg`) gehen als Telegram Fotos mit Captions raus
- PDFs und andere Dateien gehen als Telegram Dokumente raus
- Der Mitarbeiter muss von Telegram nichts wissen, er schreibt einfach normal Dateien und das Delivery System kümmert sich

---

## 7. Table Rendering

Wenn die Antwort eines Mitarbeiters Markdown-Tabellen enthält, werden sie als Monospace `<pre>` Blöcke gerendert für eine saubere Darstellung in Telegram.

**So funktioniert es:**

1. `formatting.py` erkennt Markdown-Tabellen im Mitarbeiter-Output (Zeilen mit `|` als Spalten-Separator)
2. Tabellen werden in Header und Zeilen geparst
3. Jede Tabelle wird als `<pre>` Monospace Block mit ausgerichteten Spalten gerendert
4. Das Ergebnis sieht sauber aus auf Mobile und Desktop Telegram

**Die Split Logic** (`extract_and_split_on_tables` in `formatting.py`) erhält die Lesereihenfolge. Eine Antwort wie "Hier sind die Zahlen: [TABLE] Und hier die Analyse:" wird zu Segmenten in dieser Reihenfolge gesendet — Text, gerenderte Tabelle, Text.

---

## 8. PDF Generation Pipeline

Lange Reports werden für besseres Lesen am Handy automatisch zu PDF konvertiert.

**Die Pipeline:**

```
Mitarbeiter Markdown Output
  |
  v
Aufsplitten in Summary + Full Report
  |
  v
Markdown rendern --> HTML (mit Tabellen, Code Blocks, TOC)
  |
  v
report.css Stylesheet anwenden
  |
  v
Wenn Charts referenziert: als base64 Data URIs einbetten
  |
  v
WeasyPrint: HTML --> PDF Bytes
  |
  v
An Telegram schicken als BufferedInputFile
```

**Dual Delivery:** Bei Reports schickt der Bot eine kurze Summary inline (im Chat) UND das volle PDF als Dokument. Der User kriegt schnellen Überblick ohne die Datei zu öffnen, plus die vollen Details wenn er sie will.

**Chart Embedding:** Wenn ein Report Chart Bilder referenziert (`outputs/charts/*.png`), liest der PDF Generator die Bilddateien, encodet sie als base64 und bettet sie direkt im HTML ein, bevor das PDF konvertiert wird. So bleibt das PDF in sich geschlossen.

**Das CSS** (`templates/report.css`) nutzt die `@page` Direktive von WeasyPrint für A4 Ränder, Header und Seitenzahlen.

---

## 9. Progress Tracking (Live Status Edits)

Bei langlaufenden Tasks zeigt der Bot Live-Fortschritt, indem er eine Status-Nachricht in place editiert.

**Das Pattern:**

```
User schickt Nachricht
  --> Bot schickt "Arbeite daran..."
  --> Mitarbeiter startet
  --> Mitarbeiter nutzt Read Tool --> Bot editiert Nachricht zu "Lese Dateien..."
  --> Mitarbeiter nutzt Bash Tool --> Bot editiert Nachricht zu "Führe Analyse aus..."
  --> Mitarbeiter nutzt WebSearch --> Bot editiert Nachricht zu "Recherchiere online..."
  --> Mitarbeiter fertig --> Bot löscht Status Message, schickt Ergebnis
```

**Tool zu Status Mapping** (in `orchestrator.py`):
```python
TOOL_STATUS_MAP = {
    "Read": "Reading files...",
    "Glob": "Reading files...",
    "Grep": "Searching codebase...",
    "Bash": "Running analysis...",
    "WebSearch": "Researching online...",
    "WebFetch": "Researching online...",
    "Write": "Writing output...",
    "Edit": "Writing output...",
    "Task": "Running sub-task...",
}
```

**Throttling:** Status Edits sind auf eines alle 6 Sekunden gedrosselt (`PROGRESS_THROTTLE_SECONDS`), damit die Rate Limits von Telegram nicht reißen.

**Implementierung:** Der `on_tool_use` Callback, der an `_run_agent()` übergeben wird, bekommt die Tool-Namen während der Mitarbeiter läuft. Der Orchestrator mappt sie auf menschenlesbare Statuse und editiert die Progress Message.

---

## 10. Kostenmodell

Jede Mitarbeiter-Interaktion kostet Geld. Hier die Preisstruktur (Stand Anfang 2026):

| Operation | Modell | Typische Kosten | Tokens |
|-----------|-------|-------------|--------|
| Prime (erste Nachricht) | Sonnet | $0.02 bis $0.10 | 5K bis 20K Input |
| General Mitarbeiter Antwort | Sonnet | $0.01 bis $0.05 | 10K bis 50K Input |
| Gespawnter Mitarbeiter Prime+Task | Sonnet | $0.05 bis $0.15 | 15K bis 40K Input |
| Gespawnter Opus Mitarbeiter | Opus | $0.10 bis $0.50 | 15K bis 40K Input |
| Folge-Nachricht auf bestehender Session | Sonnet | $0.005 bis $0.02 | Inkrementell |

**Cost Tracking:**

Jede Interaktion wird in `data/command/costs.jsonl` geloggt mit:
- Task ID, Topic, Modell
- Kosten in USD
- Dauer in Millisekunden
- Anzahl Turns (Mitarbeiter-Schritte)
- Timestamps

Das `/cost` Command liest diese Datei und summiert die heutigen Einträge.

**Budget Controls:**

| Config Variable | Default | Was sie kontrolliert |
|----------------|---------|-----------------|
| `COMMAND_GENERAL_MAX_BUDGET` | $5.00 | Hartes Limit pro Mitarbeiter-Nachricht |
| `COMMAND_GENERAL_MAX_TURNS` | 30 | Max Mitarbeiter-Schritte pro Nachricht |
| `COMMAND_CONTEXT_WARNING_TOKENS` | 180,000 | Token-Schwelle für Context Warning |

Das Agent SDK setzt diese Limits durch. Wenn ein Mitarbeiter das Budget oder Turn-Cap erreicht, stoppt er und gibt zurück was er hat.

**Typische tägliche Kosten:**
- Leichte Nutzung (5 bis 10 Nachrichten): $2 bis $5 pro Tag
- Mittlere Nutzung (20 bis 30 Nachrichten): $5 bis $15 pro Tag
- Heavy Nutzung (50+ Nachrichten, Opus Mitarbeiter): $15 bis $30 pro Tag

---

## 11. Das System erweitern

### Special Topics hinzufügen

Siehe [customization.md](customization.md) Abschnitt 9. Das Muster ist: Config-Eintrag --> in config.py laden --> in bot.py routen --> Handler in orchestrator.py.

### Cron Jobs hinzufügen

Mitarbeiter können auf einem Schedule getriggert werden, um tägliche Reports zu produzieren, Metriken zu checken oder Wartungs-Tasks zu fahren.

**Pattern:**

1. Schreib ein Python Script, das den Mitarbeiter-Worker direkt aufruft:
```python
# scripts/daily_report.py
import asyncio
from apps.command.worker import run_worker

async def main():
    result = await run_worker(
        prompt="Generate today's business summary. Query the database for metrics...",
        workspace_dir="/path/to/workspace",
        model="sonnet",
        max_turns=30,
        max_budget_usd=3.00,
        output_format="report",
    )
    # Result an Telegram schicken via Bot API
    # Oder in eine Datei schreiben zum späteren Review

asyncio.run(main())
```

2. Mit cron (Linux) oder launchd (macOS) schedulen:
```bash
# crontab -e
0 7 * * * cd /path/to/workspace && .venv/bin/python scripts/daily_report.py
```

### Datenbank-Integration hinzufügen

Siehe [customization.md](customization.md) Abschnitt 10. Mitarbeiter können jede SQLite Datenbank via Bash Tool abfragen. Dokumentier das Schema in deiner CLAUDE.md und im System Prompt des Mitarbeiters.

### Slack/Discord Delivery hinzufügen

Der Delivery Layer (`telegram_utils.py`) ist Telegram-spezifisch, aber der Mitarbeiter-Layer ist plattform-agnostisch. Um einen weiteren Delivery Channel hinzuzufügen:

1. Neues Delivery Modul erstellen (z.B. `slack_utils.py`) mit äquivalenten Send-Funktionen
2. Routing-Option im Orchestrator hinzufügen, die Ergebnisse an den neuen Channel schickt
3. Mitarbeiter-Worker, Formatting und PDF-Generation funktionieren unverändert weiter

### Bildgenerierung hinzufügen

Mitarbeiter können Bilder generieren, indem sie Python Scripts schreiben, die Image-Generation APIs aufrufen. Das File Path Detection System liefert die erstellten Bilder dann automatisch aus.

Beispiel: in den General Mitarbeiter Prompt einfügen:
```
## Bildgenerierung
Wenn du Bilder erstellen sollst, schreib ein Python Script, das eine
Image-Generation-API über OpenRouter aufruft (z.B. `openai/dall-e-3` via OpenRouter
chat completions). Speicher die Ergebnisse in outputs/images/. Das Delivery System
schickt sie automatisch an Telegram.
```

### Web Scraping hinzufügen

Mitarbeiter haben `WebSearch` und `WebFetch` schon eingebaut via Claude Code. Für schwerere Scraping-Bedürfnisse:

1. Installier `playwright` in deinem Virtual Environment: `pip install playwright && playwright install`
2. Scraping-Instruktionen in den Mitarbeiter-Prompt hinzufügen
3. Mitarbeiter können Playwright Scripts via Bash Tool schreiben und ausführen

---

## Message Flow Diagram

```
Telegram Nachricht
  |
  v
bot.py: handle_message()
  |-- Authorization Check (Owner Lock)
  |-- Voice? --> mit Whisper transkribieren
  |-- Foto? --> runterladen, base64 encoden
  |-- Text? --> direkt nutzen
  |
  v
bot.py: _enqueue_and_debounce()
  |-- in Buffer schieben
  |-- 1.5s Timer resetten
  |
  v (Timer feuert)
bot.py: _flush_message_buffer()
  |-- Alle gebufferten Items zusammenfügen
  |-- Route nach Topic:
      |
      |-- Mitarbeiter-Topic (gespawnt) --> orchestrator.handle_agent_topic_message()
      |-- General Topic --> orchestrator.handle_general_message()
          |
          |-- /new --> _spawn_new_agent()
          |-- /reset --> Session löschen
          |-- /compact --> Kontext komprimieren
          |-- /cost, /tasks, /help --> direkte Antworten
          |-- Text --> _handle_cc_agent_message()
              |
              |-- Session existiert? Resume. Nein? Erst primen.
              |-- Task auf Session ausführen via Agent SDK
              |-- Output cleanen, an Tabellen splitten
              |-- Tabellen als <pre> Blöcke rendern
              |-- In Telegram HTML konvertieren
              |-- Segmente in Reihenfolge schicken
              |-- Erstellte Dateien erkennen und schicken
              |-- Cost Footer schicken
              |-- Context Warning Schwelle checken
```

---

## File Responsibility Map

| File | Verantwortlich für | Hängt ab von |
|------|---------------|------------|
| `main.py` | Boot, Komponenten verkabeln, Polling starten | config, logger, orchestrator, bot |
| `bot.py` | Nachrichten empfangen, debouncen, routen | orchestrator, config |
| `orchestrator.py` | Mitarbeiter-Lifecycle, Delivery, Commands | worker, sessions, formatting, telegram_utils |
| `worker.py` | System Prompts, Agent SDK Wrapper | agent_sdk |
| `agent_sdk.py` | Claude Agent SDK Interface | claude_agent_sdk Package |
| `config.py` | Environment Variablen laden | python-dotenv |
| `session_manager.py` | Persistente Session-Speicherung (JSON + File Locks) | - |
| `formatting.py` | Markdown zu Telegram HTML, Table Extraction | - |
| `telegram_utils.py` | Message Splitting, Sending, File Delivery | aiogram |
| `cost_tracker.py` | JSONL Cost Logging, tägliche Summen | - |
| `logger.py` | Farbiges Console Logging, Boot Banner | - |
| `chart_style.py` | Matplotlib Brand Styling | matplotlib |
| `pdf_generator.py` | Markdown zu PDF via WeasyPrint | weasyprint, markdown |
| `templates/report.css` | PDF Report Stylesheet | - |
