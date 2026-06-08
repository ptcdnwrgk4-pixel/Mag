# Friday Agentic OS — Implementierungsplan

**Datum:** 2026-06-08  
**Status:** Umgesetzt

---

## Ziel

Friday von einem reaktiven Werkzeug (antwortet wenn gefragt) zu einem proaktiven Mitarbeiter upgraden, der selbstständig beobachtet, entscheidet und handelt.

---

## Architektur

```
┌─────────────────────────────────────────────────────────────┐
│                   FRIDAY AGENTIC OS                         │
├───────────────┬──────────────────┬──────────────────────────┤
│  INTERFACES   │   ORCHESTRATION  │     MEMORY LAYER         │
│  friday.py    │   agents/        │  memory/friday.db        │
│  (CLI)        │   - briefing     │  (SQLite: runs/facts/    │
│               │   - social       │   status)                │
│  Telegram Bot │   - orders       │                          │
│  (stimme/)    │   - personal     │  memory/status.json      │
│               │                  │  (für Web-Interface)     │
│  Web-HUD      │   scheduler/     │                          │
│  (index.html) │   - runner       │                          │
└───────────────┴──────────────────┴──────────────────────────┘
```

---

## Umgesetzte Komponenten

### 1. Specialist Agents (`agents/`)

Jeder Agent:
- Läuft als vollständige Claude Code Session (claude-agent-sdk)
- Hat Zugriff auf alle Workspace-Dateien und Tools (Read, Write, Bash, Grep...)
- Spezialisierter System-Prompt für seinen Aufgabenbereich
- `run(task)` für Ad-hoc-Aufgaben
- `run_scheduled_task()` für geplante Jobs

| Agent | Datei | Aufgabe | Budget |
|-------|-------|---------|--------|
| BriefingAgent | agents/briefing.py | Tages-Briefing | $1.50 |
| SocialAgent | agents/social.py | Social-Posts + Wochenpläne | $1.50 |
| OrdersAgent | agents/orders.py | Bestelllisten | $1.00 |
| PersonalAgent | agents/personal.py | Dienstpläne | $1.00 |

### 2. Memory Store (`memory/store.py`)

SQLite-Datenbank mit 3 Tabellen:
- `runs` — Protokoll aller Agent-Runs (wer, wann, was, Kosten)
- `facts` — Wichtige Business-Fakten (persistent über Sessions)
- `status` — Aggregierter Status pro Agent (letzter Run, Gesamtkosten)

Export-Funktion für Web-Interface: `export_status_json(path)`

### 3. Scheduler (`scheduler/runner.py`)

APScheduler mit 3 Jobs:
- **Tages-Briefing**: Mo–Sa um 08:30 → BriefingAgent
- **Social-Wochen-Plan**: Montag 09:00 → SocialAgent  
- **Dienstplan**: Freitag 16:00 → PersonalAgent

Optional: Telegram-Callback für Ausgabe direkt in den Chat.

### 4. CLI (`friday.py`)

```bash
python friday.py briefing              # Tages-Briefing jetzt
python friday.py social                # Social-Post für heute
python friday.py social "Weinthema"    # Post zu spezifischem Thema
python friday.py orders                # Bestellliste
python friday.py personal              # Dienstplan nächste Woche
python friday.py scheduler             # Scheduler als Daemon starten
python friday.py memory                # Alle Runs anzeigen
python friday.py memory briefing       # Runs für spezifischen Agenten
python friday.py status                # System-Gesamtstatus
```

### 5. Web-Interface (erweitert)

Sidebar um "AGENTEN OS" Panel ergänzt:
- Quick-Action-Buttons für jeden Agenten
- Vorausgefüllte, optimierte Prompts
- Status-Anzeige aus `memory/status.json` (automatisch aktualisiert)

---

## Installation

```bash
# 1. Abhängigkeiten installieren
pip install -r requirements.txt

# 2. .env prüfen (ANTHROPIC_API_KEY oder claude login)
# Das Claude Agent SDK nutzt den claude CLI Login — einmalig:
# claude login

# 3. Agent testen
python friday.py briefing

# 4. Scheduler als Daemon
python friday.py scheduler
```

---

## Nächste Schritte (optional)

- [ ] Scheduler in Stimme-Telegram-Bot integrieren (Ergebnisse direkt in Chat)
- [ ] `context/aufgaben.md` befüllen (Basis für Briefing-Qualität)
- [ ] `context/current-data.md` mit echten Zahlen füllen
- [ ] Weitere Agenten: `AnalyticsAgent`, `PromoAgent`
- [ ] Daten-Integration: Kassendaten → `current-data.md` automatisch
