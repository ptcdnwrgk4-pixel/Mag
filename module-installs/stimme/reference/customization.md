# Customization Guide — Telegram KI Command Bot

Wie du den Bot zu deinem machst. Jeder Abschnitt zielt auf eine bestimmte Datei ab, die du editieren kannst.

---

## 1. Bot Persona — `worker.py`

Der `_GENERAL_AGENT_PROMPT` String in `worker.py` definiert, wie sich dein General Mitarbeiter verhält. Das ist der System Prompt, der an jede Interaktion im General Topic angehängt wird.

**Was du ändern solltest:**

Öffne `apps/command/worker.py` und finde die `_GENERAL_AGENT_PROMPT` Variable. Ersetz sie durch deine eigene Persona:

```python
_GENERAL_AGENT_PROMPT = """\
You are [NAME]'s main Telegram assistant — their General agent for [BUSINESS NAME].
You are a persistent Claude Code agent running on Sonnet. [NAME] chats with you throughout the day,
primarily from their phone. You have full workspace power — files, database, web search, everything.

## Your Role
- Strategic thinking partner and chief of staff
- Data analyst (query data/[your-db].db via sqlite3)
- Quick research via WebSearch
- Task coordinator (when [NAME] needs a fresh agent, tell them to use /new or /new opus)

## Telegram Rules
- Keep responses concise — phone screen, on the go
- Use bold and bullets for readability
- For detailed analysis: send inline first, then offer PDF for long reports
- Be direct and conversational. No corporate fluff.

## Voice Notes
When voice notes are received (transcribed by Whisper): read current context first,
cross-reference with existing data, ask clarifying questions when ambiguous.

## Image Analysis
When photos are sent, they are saved to data/command/photos/ and the file path appears in the message.
Use the Read tool to view the image. Analyze screenshots, charts, documents, handwritten notes, etc.
"""
```

Der `_BASE_PROMPT` wird für gespawnte Mitarbeiter verwendet (aus `/new`). Er ist generischer gehalten. Customize ihn auf dieselbe Art, wenn du eine andere Persona für einmalige Mitarbeiter willst.

---

## 2. Workspace Context — `CLAUDE.md`

Das ist die wirkungsvollste Datei. Jeder Mitarbeiter liest sie zu Beginn jeder Session.

Nutz die `CLAUDE.md.template` Datei in diesem Kit als Startpunkt. Die wichtigen Abschnitte:

- **What This Is** zwei bis drei Sätze. Der Mitarbeiter nutzt das, um sich zu orientieren.
- **Key Files** liste jede Datei auf, die der Mitarbeiter brauchen könnte. Sei spezifisch mit Pfaden.
- **Conventions** Währung, Zeitzone, Terminologie, Formatregeln.
- **Commands** wenn du Slash Commands baust, dokumentier sie hier.
- **Workspace Structure** Ordner-Layout, damit der Mitarbeiter navigieren kann.

**Pro Tipps:**
- Je mehr Kontext du in CLAUDE.md packst, desto smarter wird jede Interaktion
- Halte sie aktuell während dein CEO-GPT wächst. Veraltete CLAUDE.md = verwirrte Mitarbeiter
- Bleib unter 15K Tokens (etwa 10,000 Wörter). Längere Dateien bremsen das Priming aus
- Nutze Header und Struktur. Mitarbeiter parsen strukturierten Text viel besser als reine Prose

---

## 3. Prime Commands — `.claude/commands/`

Prime Commands sagen Mitarbeitern, welche Dateien sie beim Start lesen sollen.

**`prime-telegram.md`** wird vom General Mitarbeiter und gespawnten Telegram Mitarbeitern genutzt. Halte das KURZ (max 5 bis 8 Dateien). Mitarbeiter müssen schnell primen, weil User auf ihrem Handy warten.

**`prime.md`** wird für volle Claude Code Sessions genutzt (nicht Telegram). Darf länger und gründlicher sein.

**Worauf du sie zeigen lassen solltest:**

Denk darüber nach, welchen Kontext ein Mitarbeiter braucht, um in 80% der Gespräche nützlich zu sein:
- Deine CLAUDE.md (immer)
- Dein aktuelles Strategy- oder Roadmap-Dokument
- Dein neuestes Metrik- oder KPI-File
- Dein Team Roster (wenn relevant)
- Referenz-Dokumente, die häufig genutzt werden

Beispiel `prime-telegram.md`:
```markdown
# Prime (Telegram)

> Kurzes Prime für Telegram Mitarbeiter. Halte das Acknowledgment kurz.

Lies diese Dateien der Reihe nach:
1. `CLAUDE.md` — Workspace Übersicht und Conventions
2. `context/strategy.md` — Aktuelle strategische Prioritäten
3. `context/metrics.md` — Neueste Business-Metriken
4. `context/team.md` — Team Roster und Verantwortlichkeiten

Nach dem Lesen antworte kurz:
**Primed and ready.** What do you need?
```

---

## 4. Brand-Farben — `chart_style.py`

Charts, die Mitarbeiter generieren, nutzen die Farbpalette aus `apps/command/chart_style.py`.

**So änderst du die Farben:**

```python
# Öffne apps/command/chart_style.py

COLORS = {
    "primary": "#1a73e8",      # Deine primäre Brand-Farbe
    "secondary": "#34a853",     # Sekundärfarbe
    "accent1": "#ea4335",       # Akzentfarben für Chart-Serien
    "accent2": "#fbbc04",
    "accent3": "#9334e6",
    "accent4": "#ff6d01",
    "light_bg": "#f8f9ff",      # Heller Hintergrund für Chart-Area
    "grid": "#e8e8e8",          # Grid-Linien
    "text": "#1a1a1a",          # Achsen-Labels und Titel
    "text_muted": "#666666",    # Sekundärer Text
}
```

Die `PALETTE` Liste steuert die Reihenfolge der Farben für Multi-Series Charts:
```python
PALETTE = [
    COLORS["primary"], COLORS["secondary"], COLORS["accent1"],
    COLORS["accent2"], COLORS["accent3"], COLORS["accent4"],
]
```

---

## 5. PDF Styling — `templates/report.css`

Wenn Mitarbeiter lange Reports generieren, werden sie via diesem Stylesheet automatisch zu PDF konvertiert.

**Was du in `apps/command/templates/report.css` anpassen solltest:**

```css
/* Akzentfarbe ändern (für Headings, Borders, Links) */
/* Suche nach #1a73e8 und ersetz durch deine Brand-Farbe */

.report-header h1 {
    color: #1a73e8;  /* <-- Deine Brand-Farbe */
}

th {
    background-color: #f0f4ff;  /* <-- Helle Version deiner Brand-Farbe */
    color: #1a73e8;             /* <-- Deine Brand-Farbe */
    border-bottom: 2px solid #1a73e8;  /* <-- Deine Brand-Farbe */
}

/* Footer-Text ändern */
@page {
    @bottom-center {
        content: "Your Company Name";  /* <-- Dein Firmenname */
    }
}

/* Font-Stack ändern */
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    /* Deinen Brand-Font vorn in die Liste setzen, falls du einen hast */
}
```

---

## 6. Boot Banner — `logger.py`

Wenn der Bot startet, druckt er ein gebrandetes ASCII Banner. Editier `apps/command/logger.py`, um es zu ändern:

```python
BANNER = f"""\
{_C.BRIGHT_CYAN}{_C.BOLD}
   +----------------------------------------------+
   |                                              |
   |       Y O U R   C O M P A N Y               |
   |       C O M M A N D        v1.0              |
   |                                              |
   +----------------------------------------------+
   |  Your Company AI Command Center              |
   |  Your Name                                   |
   +----------------------------------------------+
{_C.RESET}"""
```

Pass auch die Startup Message in `main.py` an. Such die `on_startup` Funktion:
```python
await bot.send_message(
    chat_id=config.group_id,
    text="Your Bot Name is online.",  # <-- Hier ändern
)
```

---

## 7. Special Topics hinzufügen

Du kannst bestimmte Forum-Topics für bestimmte Personas oder Zwecke registrieren. Das Pattern:

1. **Topic erstellen** in deiner Telegram Gruppe (Rechtsklick oder Long-Press --> "New Topic")
2. **Topic-ID rausfinden**, indem du eine Nachricht im Topic schickst und in den Bot Logs nach `message_thread_id` schaust
3. **Config-Eintrag** in `.env`:
   ```
   MY_SPECIAL_TOPIC_ID=12345
   ```
4. **In config.py laden:**
   ```python
   my_special_topic_id: int | None
   # In load_config():
   my_special_topic_id=int(v) if (v := os.getenv("MY_SPECIAL_TOPIC_ID", "").strip()) else None,
   ```
5. **Routing in bot.py hinzufügen** (in `_flush_message_buffer`, vor dem General Catch-all):
   ```python
   elif topic_id and _config.my_special_topic_id and topic_id == _config.my_special_topic_id:
       await _orchestrator.handle_my_special_topic(last_message, text_override=combined_text, photos=all_photos or None)
   ```
6. **Handler in orchestrator.py hinzufügen** mit einem Custom System Prompt für den Zweck des Topics.

**Beispiele für Special Topics:**
- **Inbox Topic** für GTD Inbox Processing mit spezialisiertem Prompt
- **Content Topic** für Content Ideation mit Zugriff auf deine Content Pipeline
- **Research Topic** für Deep Research mit einem Prompt, der Web Search betont
- **Data Topic** für Analytics mit einem Prompt, der dein Datenbank-Schema kennt

---

## 8. Datenbank-Queries hinzufügen

Mitarbeiter können jede SQLite Datenbank in deinem CEO-GPT abfragen. Der Schlüssel ist, ihnen im System Prompt davon zu erzählen.

**Schritt 1:** Leg deine SQLite Datenbank irgendwo in den Workspace (z.B. `data/my-database.db`)

**Schritt 2:** Datenbank-Info zur `CLAUDE.md` hinzufügen:
```markdown
## Datenbank
SQLite Datenbank unter `data/my-database.db`. Wichtige Tabellen:
- `customers` — id, name, email, plan, created_at
- `revenue` — id, customer_id, amount, date
- `metrics` — id, metric_name, value, date

Beispiel-Queries:
- Monatlicher Umsatz: `SELECT strftime('%Y-%m', date) as month, SUM(amount) FROM revenue GROUP BY month`
- Aktive Kunden: `SELECT COUNT(*) FROM customers WHERE plan != 'cancelled'`
```

**Schritt 3:** Datenbank-Kontext zum General Mitarbeiter Prompt in `worker.py` hinzufügen:
```python
_GENERAL_AGENT_PROMPT = """\
...
## Database
You have a SQLite database at data/my-database.db.
Query it using: sqlite3 data/my-database.db "SELECT ..."
Key tables: customers, revenue, metrics.
...
"""
```

Mitarbeiter nutzen das Bash Tool, um `sqlite3` Queries direkt auszuführen. Sie können auch Python Scripts schreiben, die die Datenbank für komplexere Analysen abfragen.

---

## Übersicht der Dateien zum Anpassen

| Priorität | Datei | Was du änderst |
|----------|------|----------------|
| 1 | `CLAUDE.md` | Dein Business-Kontext (am wirkungsvollsten) |
| 2 | `.claude/commands/prime-telegram.md` | Welche Dateien Mitarbeiter beim Start lesen |
| 3 | `apps/command/worker.py` | Mitarbeiter-Persona und Verhaltens-Prompts |
| 4 | `.env` | API Keys, Modell-Auswahl, Budgets |
| 5 | `apps/command/chart_style.py` | Brand-Farben für Charts |
| 6 | `apps/command/templates/report.css` | PDF Report Styling |
| 7 | `apps/command/logger.py` | Boot Banner und Log Labels |
| 8 | `apps/command/orchestrator.py` | Special Topics, Custom Routing |
| 9 | `apps/command/config.py` | Neue Environment Variablen |
