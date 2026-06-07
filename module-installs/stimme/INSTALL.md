# Stimme: Installation

<!-- MODUL-METADATEN
modul: stimme
version: v1
status: RELEASED
released: 2026-02-27
requires: [kontext]
phase: 2
category: Kern-Module
complexity: complex
api_keys: 2-3
setup_time: 30-45 Minuten
-->

---

## FÜR CLAUDE (Anleitung für dich, das Programm)

Du hilfst dem Member, seinem Mitarbeiter eine **Stimme** zu geben. Bis jetzt sitzt der Mitarbeiter am Rechner und ist weg, sobald der Member den Laptop zuklappt. Mit diesem Modul lebt der Mitarbeiter im Handy, der Member chattet mit ihm über Telegram, schickt Sprachnachrichten, Fotos und Screenshots.

Das ist ein komplexes Modul mit mehreren beweglichen Teilen (Telegram-Verbindung, Claude Agent SDK, gespeicherte Sitzungen). Halt dich an diese Regeln:

**Kernregel, der Member fasst kein Terminal an:**
- DU führst jeden Befehl aus. Der Member tippt nicht ins Terminal, niemals.
- Die Aufgabe des Members ist: Fragen beantworten, in Telegram und Browser klicken (Bot anlegen, API-Keys holen), Keys an dich weitergeben.
- DU machst alles andere still im Hintergrund: Dateien anlegen, Pakete installieren, Umgebung einrichten, konfigurieren, testen, ausrollen.
- Wenn du einen Befehl ausführst, sag dem Member in Klartext, was passiert ("Ich richte gerade die Umgebung deiner Stimme ein", "Ich installiere die Pakete, die dein Mitarbeiter braucht"). Zeig dem Member nie den Befehl und bitte ihn nie, einen einzugeben.

**Verhalten:**
- Geh davon aus, dass der Member nicht technisch ist, vielleicht hat er noch nie ein Terminal gesehen
- Erklär in Klartext, was du gleich tust, bevor du es tust
- Feier Meilensteine, die erste Antwort vom Handy ist ein großer Moment
- Wenn was schiefgeht, kein Error-Log dumpen, sondern Problem in Klartext erklären und selbst fixen
- Keine Prüfschritte überspringen, wenn ein Check fehlschlägt, stehenbleiben und fixen
- Aufmunternd reden, der Member baut hier was Echtes

**Pacing:**
- Nicht durchrasen. Das ist eines der komplexeren Module. Pause an den Meilensteinen.
- Nach Voraussetzungen: "Werkzeuge stehen. Bauen wir deinen Telegram-Zugang?"
- Nach Telegram-Setup: "Der Zugang steht, jetzt kriegt dein Mitarbeiter eine Stimme."
- Nach erster Test-Antwort: "Er lebt. Du hast eine Nachricht vom Handy geschickt und dein Mitarbeiter hat sie verarbeitet. Genau so wird er ab jetzt für dich erreichbar."
- Nach Deployment: "Dein Mitarbeiter läuft jetzt rund um die Uhr. Von überall auf der Welt machst du Telegram auf und redest mit ihm."

**Fehlerbehandlung:**
- Python-Version zu alt: präzise Upgrade-Anleitung für sein Betriebssystem
- `claude` CLI nicht da: `npm install -g @anthropic-ai/claude-code`
- `claude_agent_sdk` Import-Fehler: `pip install claude-agent-sdk`
- Telegram-Bot antwortet nicht: check ob (1) der Bot Admin in der Gruppe ist, (2) die Group-ID stimmt (negative Zahl, fängt mit -100 an), (3) Topics aktiviert sind
- "Prime failed": der prime-Befehl verweist auf Dateien, die noch nicht existieren
- WeasyPrint Installation fehlt: auf macOS `brew install weasyprint` oder erst System-Pakete: `brew install pango cairo gdk-pixbuf libffi`. Auf Linux: `apt install python3-weasyprint`
- Niemals sagen "schau in die Logs", sondern selbst reingucken, Problem finden, fixen

**CEO-GPT-Kontext:**
Der Member hat schon eine CLAUDE.md (aus dem `kontext`) oder fängt komplett frisch an. Wenn Kontext schon installiert ist, sind CLAUDE.md und Prime-Befehle vorhanden, dann anpassen statt überschreiben. Wenn alles frisch ist, alles neu anlegen.

**Datei-Platzierung:**
Die Bot-Dateien gehören als Python-Paket nach `apps/command/`. Das Paket importiert sich selbst, also bleibt die Struktur intakt:

```
CEO-GPT/
├── CLAUDE.md
├── .env
├── .claude/commands/
│   ├── prime.md
│   └── prime-telegram.md
├── apps/
│   └── command/
│       ├── __init__.py
│       ├── main.py
│       ├── agent_sdk.py
│       ├── bot.py
│       ├── config.py
│       ├── orchestrator.py
│       ├── worker.py
│       ├── session_manager.py
│       ├── cost_tracker.py
│       ├── formatting.py
│       ├── telegram_utils.py
│       ├── logger.py
│       ├── chart_style.py
│       ├── pdf_generator.py
│       └── templates/
│           └── report.css
├── requirements.txt
└── data/command/  (wird automatisch angelegt)
```

---

## ÜBERSICHT (lies das dem Member vor dem Start vor)

Jetzt bauen wir die Stimme deines Mitarbeiters. Bis jetzt lebt er auf deinem Rechner, du kannst nur mit ihm arbeiten, wenn du am Schreibtisch sitzt. Sobald du den Laptop zuklappst, ist er weg.

Mit der Stimme zieht dein Mitarbeiter in deine Tasche. Du chattest mit ihm über Telegram wie mit einem Kollegen. Tippen oder Sprachnachricht, Foto oder Screenshot, alles geht rein. Er antwortet mit Text, Tabelle oder PDF.

Das hast du am Ende:

- **Mitarbeiter im Chat, rund um die Uhr.** Aus jeder Ecke der Welt Telegram auf, Nachricht raus, Antwort rein. Er hat vollen Zugriff auf dein CEO-GPT.
- **Allgemeiner Chat, der sich erinnert.** Der Haupt-Thread behält den Faden, auch nach Tagen, auch nach Bot-Neustarts.
- **Frische Mitarbeiter für einzelne Themen.** Mit `/new` startest du einen sauberen Mitarbeiter in einem eigenen Thread, wie ein neuer Tab. Jedes Projekt in seinem eigenen Faden.
- **Sprachnachrichten.** Rein quatschen, dein Mitarbeiter hört zu, versteht und arbeitet weiter (optional, braucht OpenRouter Key).
- **Fotos und Screenshots.** Bild rein, dein Mitarbeiter sieht es und reagiert.
- **Saubere Ausgabe.** Tabellen werden sauber gerendert, Diagramme kommen als Bild, längere Reports als PDF direkt in Telegram.
- **Threads benennen.** Mit `/name` kriegt jeder Thread einen Titel, der zum Gespräch passt.

**Setup-Zeit:** 30 bis 45 Minuten
**Voraussetzung:** Das `kontext` muss schon installiert sein, du brauchst eine CLAUDE.md. Den Rest richten wir zusammen ein.

---

## SCOPING

Bevor wir installieren, klären wir das Setup. Stell dem Member diese Fragen, eine nach der anderen.

### Frage 1: Sprachnachrichten

"Willst du deinem Mitarbeiter Sprachnachrichten schicken können? Du redest ins Handy, er transkribiert (über OpenRouter / Whisper) und arbeitet damit weiter. Dafür brauchst du einen OpenRouter API Key."

**Optionen:**
- **A) Ja, Sprachnachrichten einrichten**: Wir brauchen deinen OpenRouter API Key. Wenn du noch keinen hast, führe ich dich durch.
- **B) Erstmal überspringen**: Kein Problem, Text und Fotos gehen trotzdem. Sprachnachrichten kannst du jederzeit später dazuschalten, sobald du einen OpenRouter Key hast.

Notier: `VOICE_ENABLED = true | false`

### Frage 2: PDF-Reports

"Sollen längere Reports als saubere PDFs in Telegram landen? Statt einer Textwüste kriegst du dann eine gestaltete PDF direkt in den Chat."

**Optionen:**
- **A) Ja, PDFs einrichten** (empfohlen): Braucht WeasyPrint, eine Render-Bibliothek. Installation übernehme ich.
- **B) Erstmal überspringen**: Reports kommen dann als Text oder Markdown-Datei.

Notier: `PDF_ENABLED = true | false`

### Frage 3: Diagramme

"Soll dein Mitarbeiter Diagramme erzeugen können? Wenn du nach Zahlen oder Daten fragst, kommt das visuell als Bild in den Chat."

**Optionen:**
- **A) Ja, Diagramme einrichten** (empfohlen): Braucht matplotlib, einfache Installation.
- **B) Erstmal überspringen**: Zahlen kommen dann als Text oder Tabelle.

Notier: `CHARTS_ENABLED = true | false`

### Frage 4: Plattform

"Auf welcher Maschine soll dein Mitarbeiter rund um die Uhr laufen? Sie muss durchgehend an sein, damit er deine Nachrichten empfangen kann."

**Optionen:**
- **A) Mac** (Mac Mini, MacBook, iMac): Wir nutzen launchd, damit er automatisch läuft.
- **B) Linux** (VPS, Cloud-Server, Raspberry Pi): Wir nutzen systemd.
- **C) Erstmal nur mein Laptop**: Für den Anfang okay. Dann läuft er nur, wenn dein Laptop an ist und der Bot manuell gestartet wurde. Später kannst du auf eine Always-on-Maschine umziehen.

Notier: `PLATFORM = mac | linux | laptop`

**Wichtiger Hinweis für MacBook-Nutzer:** Du brauchst keinen Mac Mini und keinen externen Server, um den Mitarbeiter rund um die Uhr laufen zu lassen. Dein MacBook reicht, solange es am Strom hängt. Geh in **Systemeinstellungen → Batterie → Optionen** und aktivier **"Verhindern, dass der Mac automatisch in den Ruhezustand wechselt, wenn das Display ausgeschaltet ist"**. Damit bleibt dein Mac wach, auch wenn das Display dunkel ist, und der Bot läuft durch. Wenn du im Clamshell-Modus arbeiten willst (Deckel zu), brauchst du entweder einen externen Monitor oder eine kleine App wie Amphetamine oder KeepingYouAwake.

Nach dem Scoping fass zusammen: "So sieht dein Setup aus: Stimme mit {Voice-Status}, {PDF-Status}, {Diagramm-Status}, auf {Plattform}. Passt?"

---

## VORAUSSETZUNGEN

Jede Voraussetzung prüfen und sicherstellen, dass sie sauber läuft, bevor du weitergehst.

### Python 3.11+
```bash
python3 --version
```
Wenn nicht da oder zu alt, OS-spezifische Anleitung:
- macOS: `brew install python@3.12` oder von python.org runterladen
- Linux: `sudo apt install python3.12` oder Äquivalent

### Node.js (für Claude Code CLI)
```bash
node --version
```
Wenn nicht da:
- macOS: `brew install node`
- Linux: `curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt install -y nodejs`

### Claude Code CLI
```bash
claude --version
```
Wenn nicht da:
```bash
npm install -g @anthropic-ai/claude-code
```

### pip
```bash
python3 -m pip --version
```
Wenn nicht da:
```bash
python3 -m ensurepip --upgrade
```

### Bestehender CEO-GPT (aus dem `kontext`)
```bash
ls CLAUDE.md
```
Wenn CLAUDE.md fehlt: "Du hast noch keinen CEO-GPT. Das richten wir minimal ein. Aber für das beste Erlebnis vorher das `kontext` installieren, das legt die Grundlage, auf der die Stimme aufsetzt."

Wenn keine CLAUDE.md existiert, eine minimale anlegen:
```markdown
# Mein CEO-GPT

## Was das hier ist
[Frag den Member, sein Business in zwei bis drei Sätzen zu beschreiben, dann hier einsetzen]

## Schlüsseldateien
- `CLAUDE.md`: Diese Datei (CEO-GPT-Überblick)
```

[VERIFY] Alle Voraussetzungen geben Versionsnummern aus, keine Fehler.
Frag: "Alles steht. Sollen wir deinen Telegram-Zugang anlegen?"

---

## API-KEYS

API-Keys einsammeln, basierend auf den Scoping-Antworten.

### Telegram Bot Token (Pflicht)

Dauert ungefähr zwei Minuten.

1. Öffne Telegram auf Handy oder Rechner
2. Such nach **@BotFather** (blaues Häkchen, das ist der echte)
3. Tipp **Start**, wenn das dein erstes Mal ist
4. Schick: `/newbot`
5. BotFather fragt nach dem **Anzeigenamen**, gib was wie "Mein CEO-GPT Bot" oder "[Firmenname] Bot"
6. BotFather fragt nach dem **Benutzernamen**, muss auf `bot` enden. Beispiele: `mein_ceogpt_bot`, `acme_ki_bot`. Such was Einzigartiges.
7. BotFather antwortet mit einem Token, sieht so aus: `7123456789:AAHx_dein_langer_token_hier`
8. **Kopier den ganzen Token** und gib ihn mir, ich speicher ihn

**Wichtig:** Niemals weitergeben. Wer den Token hat, kann deinen Bot übernehmen.

[VERIFY] Format muss sein: Zahl:Buchstaben_und_Zahlen (z.B. 7123456789:AAH...)

### Telegram Group ID (Pflicht)

Jetzt legen wir die Gruppe an, in der du mit deinem Mitarbeiter chattest.

1. Telegram auf, **neue Gruppe** erstellen
2. Nenn sie was Eingängiges, z.B. "CEO-GPT Zentrale" oder "[Firma] HQ"
3. Füg deinen Bot zur Gruppe hinzu (such den Benutzernamen, den du gerade angelegt hast)
4. Geh in **Gruppeneinstellungen** → **Administratoren** → **Administrator hinzufügen** → wähl deinen Bot → gib **alle Rechte** → speichern
5. Geh in **Gruppeneinstellungen** → scroll runter → **Topics** finden → **anschalten**

Jetzt brauchen wir die Group ID:

6. Schreib irgendeine Nachricht in die Gruppe (auch nur "test" reicht)
7. Dann lass ich diesen Befehl laufen, um die Group-ID zu finden:

```bash
# DEIN_BOT_TOKEN durch den Token von oben ersetzen
curl -s "https://api.telegram.org/botDEIN_BOT_TOKEN/getUpdates" | python3 -c "
import json, sys
data = json.load(sys.stdin)
if data.get('result'):
    for update in data['result']:
        msg = update.get('message', {})
        chat = msg.get('chat', {})
        if chat.get('id'):
            print(f'Group ID: {chat[\"id\"]}')
            print(f'Group Name: {chat.get(\"title\", \"unknown\")}')
            break
else:
    print('Keine Updates gefunden. Vorher in der Gruppe eine Nachricht schicken, dann nochmal.')
"
```

Die Group-ID ist eine negative Zahl, die mit `-100` anfängt, z.B. `-1001234567890`.

[VERIFY]
```bash
# Schnellcheck, ob der Bot die Gruppe sieht
curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getChat?chat_id=$TELEGRAM_GROUP_ID" | python3 -c "
import json, sys
data = json.load(sys.stdin)
if data.get('ok'):
    print(f'Verbunden mit Gruppe: {data[\"result\"][\"title\"]}')
    print(f'Topics aktiviert: {data[\"result\"].get(\"is_forum\", False)}')
else:
    print(f'Fehler: {data.get(\"description\", \"unbekannt\")}')
    print('Check ob (1) der Bot-Token stimmt, (2) die Group-ID stimmt, (3) der Bot in der Gruppe ist')
"
```
Erwartet: "Verbunden mit Gruppe: [Name]" und "Topics aktiviert: True"

Wenn Topics aus sind: "Geh in deine Telegram-Gruppe → Einstellungen → Topics → anmachen. Damit kriegt jeder Mitarbeiter seinen eigenen Thread."

### API-Keys & Auth prüfen

Die Stimme braucht **eine** Sache: einen OpenRouter-Key (für Sprachnachrichten). Der Mitarbeiter-Brain selbst läuft über den Claude Agent SDK mit deiner Claude-CLI-Auth — kein extra Anthropic-Key nötig.

**Voraussetzung Claude-CLI-Login.** Prüf, dass deine Claude-CLI eingeloggt ist:
```bash
claude --version && echo "Claude CLI gefunden"
```
Wenn du Claude Code regulär nutzt, ist die Auth schon da. Falls nicht: einmal `claude` ohne Argumente laufen lassen, dem Browser-Login folgen.

**OpenRouter-Key prüfen.** Wurde bei der Absicherung als `OPENROUTER_API_KEY` eingerichtet. Falls nicht, hol ihn jetzt nach unter [openrouter.ai/keys](https://openrouter.ai/keys).

[VERIFY]
```bash
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
or_key = os.getenv('OPENROUTER_API_KEY', '')
if or_key.startswith('sk-or-'):
    print(f'OpenRouter Key sitzt ({or_key[:10]}...)')
else:
    print('OpenRouter Key FEHLT (nur nötig für Sprachnachrichten). Hol ihn unter openrouter.ai/keys')
"
```

Wenn der Key da ist: "Key geprüft. Jetzt bauen wir die Stimme."

---

## INSTALLATION

Schritt für Schritt durchgehen. Nach jedem Schritt prüfen, bevor du zum nächsten gehst.

### Virtuelle Umgebung und Pakete

```bash
# Virtuelle Umgebung anlegen (falls noch nicht da)
python3 -m venv .venv
source .venv/bin/activate

# Kern-Pakete installieren
pip install -r requirements.txt
```

Die `requirements.txt` aus diesem Modul enthält:
- `aiogram>=3.0`: Telegram-Framework
- `claude-agent-sdk`: Claude Code Agent SDK
- `python-dotenv`: Umgebungsvariablen laden
- `markdown`: Markdown-Verarbeitung (für PDFs)
- `httpx`: HTTP-Client für den OpenRouter-Whisper-Aufruf

**Wenn PDF_ENABLED:**
```bash
pip install weasyprint
```
Wenn WeasyPrint streikt (häufig auf macOS):
```bash
# macOS, erst System-Pakete
brew install pango cairo gdk-pixbuf libffi
pip install weasyprint
```
```bash
# Linux
sudo apt install python3-weasyprint
# oder: sudo apt install libpango-1.0-0 libcairo2 libgdk-pixbuf2.0-0 && pip install weasyprint
```

**Wenn CHARTS_ENABLED:**
```bash
pip install matplotlib
```

**Sprachnachrichten:** Kein extra Paket nötig — läuft über OpenRouter via httpx (ist schon in der `requirements.txt`).

[VERIFY]
```bash
python3 -c "
from aiogram import Bot; print('aiogram OK')
from claude_agent_sdk import query; print('claude-agent-sdk OK')
from dotenv import load_dotenv; print('dotenv OK')
import httpx; print('httpx OK')
"
```
Optionale Checks:
```bash
python3 -c "from weasyprint import HTML; print('weasyprint OK')" 2>/dev/null || echo "weasyprint nicht installiert (PDFs aus)"
python3 -c "import matplotlib; print('matplotlib OK')" 2>/dev/null || echo "matplotlib nicht installiert (Diagramme aus)"
```

### .env-Datei anlegen

Schreib die .env mit den eingesammelten API-Keys. Liegt im CEO-GPT-Root (gleicher Ordner wie CLAUDE.md).

```
# === Stimme ===
TELEGRAM_BOT_TOKEN=dein_token_hier
TELEGRAM_GROUP_ID=-100deine_group_id

# === KI-Dienste ===
# Mitarbeiter-Brain laeuft ueber Claude-CLI-Auth - kein Anthropic-Key noetig.
# Nur OpenRouter fuer Sprachnachrichten (Whisper).
OPENROUTER_API_KEY=sk-or-dein_openrouter_key_hier

# === Feintuning (Default-Werte reichen am Anfang) ===
# COMMAND_GENERAL_MODEL=sonnet
# COMMAND_GENERAL_MAX_TURNS=30
# COMMAND_GENERAL_MAX_BUDGET=5.00
# COMMAND_CONTEXT_WARNING_TOKENS=180000
```

**Wenn eine .env schon existiert:** Keys anhängen, keine bestehenden Keys überschreiben.

[VERIFY]
```bash
python3 -c "
from dotenv import load_dotenv; import os; load_dotenv()
token = os.getenv('TELEGRAM_BOT_TOKEN', '')
group = os.getenv('TELEGRAM_GROUP_ID', '')
or_key = os.getenv('OPENROUTER_API_KEY', '')
print(f'Bot-Token: {\"OK\" if token else \"FEHLT\"} ({token[:10]}...)' if token else 'Bot-Token: FEHLT')
print(f'Group-ID: {\"OK\" if group else \"FEHLT\"} ({group})' if group else 'Group-ID: FEHLT')
if or_key: print(f'OpenRouter: OK ({or_key[:10]}...)')
else: print('OpenRouter: nicht gesetzt (Sprachnachrichten aus)')
"
```

### 🎯 PFLICHT-VERIFIKATION: Whisper-Transkription testen

Bevor der Bot startet, lass das Verify-Skript laufen. Es schickt eine kleine Test-Audio-Datei an OpenRouter und prüft, dass die Antwort sauber zurückkommt. Wenn dieser Test fehlschlägt, gehen später deine Sprachnachrichten nicht durch — also lieber jetzt fixen.

```bash
python3 scripts/verify_openrouter_whisper.py
```

Erwartet: HTTP 200, eine vollständige JSON-Response mit einem `text`-Feld, und am Ende "Verifikation erfolgreich."

**Wenn der Test fehlschlägt:**
- HTTP 401 → Key ist falsch oder leer. Prüf `OPENROUTER_API_KEY` in der `.env`.
- HTTP 402 → keine Credits. Lade auf bei [openrouter.ai/credits](https://openrouter.ai/credits) (5–10 $ reichen lange).
- `text`-Feld nicht gefunden → die volle Response ausgeben lassen, das Feld mit der Transkription identifizieren und in `apps/command/bot.py` die Zeile mit `data.get("text")` entsprechend anpassen. Das ist die einzige Stelle, die das Response-Format kennt.

### Bot-Code in das CEO-GPT kopieren

Kopier alle Dateien aus dem `scripts/`-Ordner dieses Moduls in das CEO-GPT des Members. Die Struktur muss so aussehen:

```
CEO-GPT/
├── apps/
│   ├── __init__.py          (leere Datei)
│   └── command/
│       ├── __init__.py      (leere Datei)
│       ├── agent_sdk.py     ← Claude Agent SDK Wrapper
│       ├── bot.py           ← Telegram-Nachrichten-Handler
│       ├── config.py        ← Umgebungs-Konfiguration
│       ├── orchestrator.py  ← Kern-Engine (Routing, Sitzungen, Befehle)
│       ├── worker.py        ← System-Prompts & Mitarbeiter-Wrapper
│       ├── session_manager.py ← Gespeicherte Sitzungen
│       ├── cost_tracker.py  ← Verbrauchs-Logging
│       ├── formatting.py    ← Markdown zu Telegram-HTML
│       ├── telegram_utils.py ← Nachrichten-Versand
│       ├── logger.py        ← Farbiges Logging und Boot-Banner
│       ├── main.py          ← Einstiegspunkt (startet die Stimme)
│       ├── chart_style.py   ← Diagramm-Branding (wenn Diagramme an)
│       ├── pdf_generator.py ← PDF-Erzeugung (wenn PDFs an)
│       └── templates/
│           └── report.css   ← PDF-Stylesheet
└── requirements.txt
```

Jede Datei aus `scripts/apps/` in den `apps/`-Ordner des CEO-GPT. Beide `__init__.py` müssen da sein (können leer sein).

**Wenn das CEO-GPT schon einen `apps/`-Ordner hat:** Den `command/`-Unterordner danebenlegen, nichts überschreiben.

[VERIFY]
```bash
python3 -c "
from apps.command.config import load_config
c = load_config()
print(f'Config geladen, Gruppe: {c.group_id}, Modell: {c.general_agent_model}')
"
```
Erwartet: Group-ID und Modell werden ausgegeben, keine Import-Fehler.

### Prime-Befehle einrichten

Prime-Befehle sagen deinem Mitarbeiter, welche Dateien er beim Start lesen soll. Kopier die Vorlagen aus `scripts/.claude/commands/` in den `.claude/commands/`-Ordner des CEO-GPT.

```bash
mkdir -p .claude/commands
```

**Wenn Prime-Befehle schon existieren** (aus dem `kontext`), so lassen. Die Stimme nutzt, was schon konfiguriert ist.

**Wenn keine Prime-Befehle existieren:** Die Vorlagen aus diesem Modul kopieren:
- `.claude/commands/prime.md`: Voller Prime für gestartete Mitarbeiter (/new)
- `.claude/commands/prime-telegram.md`: Schnellerer Prime für den allgemeinen Mitarbeiter

Dann beide Dateien auf die Kontext-Dateien des Members anpassen. Mindestens muss jede sagen:
1. `CLAUDE.md` lesen: CEO-GPT-Überblick
2. Wichtige Geschäftsdokumente oder Strategie-Dateien lesen

Je mehr relevante Dateien im Prime stehen, desto kluger arbeitet der Mitarbeiter. Aber `prime-telegram.md` schlank halten, der läuft bei jeder ersten Nachricht und der Member wartet auf seinem Handy.

[VERIFY]
```bash
ls .claude/commands/prime.md .claude/commands/prime-telegram.md
```
Beide Dateien müssen existieren.

### Stimme-Persönlichkeit anpassen

Mach `apps/command/worker.py` auf und schau auf den `_GENERAL_AGENT_PROMPT`-String oben. Das ist die Persönlichkeit und Anleitung für den allgemeinen Mitarbeiter.

Die Vorlage ist generisch. Hilf dem Member, das auf sein Business zuzuschneiden:

Frag: "Was soll dein Mitarbeiter über dich und dein Business wissen, wenn er antwortet? Was ist deine Rolle? Womit soll er dir am häufigsten helfen? Gibt es Regeln, an die er sich halten soll?"

Aus der Antwort den `_GENERAL_AGENT_PROMPT` aktualisieren. Knapp halten, der Prompt läuft vor jeder Antwort mit.

[VERIFY] Lies dem Member den angepassten Prompt vor: "So stellt sich dein Mitarbeiter im Chat auf, passt das?"

### Daten-Ordner anlegen

```bash
mkdir -p data/command
```

Da landen Sitzungs-Daten und Logs.

[VERIFY]
```bash
ls -la data/command/
```

---

## TEST

### Schnelltest, die Stimme bootet

```bash
source .venv/bin/activate
python -m apps.command.main
```

Du solltest sehen:
1. Ein Boot-Banner
2. Konfigurations-Übersicht (Modell, CEO-GPT-Pfad)
3. System-Checks (alles grün)
4. "Online: polling for messages"

Wenn Fehler kommen, hier stehenbleiben und fixen.

### Test 1: Basis-Nachricht

1. Mach deine Telegram-Gruppe auf
2. Geh in das **General**-Topic
3. Schick: "Hallo, in welchem CEO-GPT bist du gerade?"
4. Warte 10 bis 30 Sekunden, der Mitarbeiter primed sich beim ersten Mal (Erstantwort dauert länger)
5. Er antwortet mit Infos aus deiner CLAUDE.md

"Dein Mitarbeiter hat geantwortet. Diese Antwort kam von einem Claude-Code-Mitarbeiter mit vollem Zugriff auf dein CEO-GPT. Alles was in deinen Dateien steht, sieht und nutzt er."

### Test 2: Frischen Mitarbeiter starten

1. Im General-Topic schick: `/new`
2. Ein neues Topic taucht auf, mit einem Namen wie "Agent: Feb 27 2:30PM UTC"
3. Warte auf die "Primed and ready"-Bestätigung
4. Schick eine Nachricht in das neue Topic, der frische Mitarbeiter antwortet

"Du hast gerade einen frischen Mitarbeiter gestartet. Wie ein neuer Tab in deinem Browser, eigener Faden, voller Kontext."

### Test 3: Thread umbenennen

1. Führ im Thread aus Test 2 ein kurzes Gespräch zu einem konkreten Thema
2. Schick: `/name`
3. Der Mitarbeiter schlägt einen passenden Namen vor und benennt das Topic um

"`/name` ist dein Aufräum-Befehl. Nach jeder Arbeitssession den Befehl, und der Thread kriegt einen Titel, der zum Inhalt passt. Viel besser als 'Agent: Feb 27 2:30PM'."

### Test 4: Foto-Analyse

1. In einem beliebigen Topic einen Screenshot oder ein Foto schicken, mit Bildunterschrift wie "Was siehst du hier?"
2. Der Mitarbeiter beschreibt und analysiert das Bild

### Test 5: Sprachnachricht [wenn VOICE_ENABLED]

1. Sprachnachricht in Telegram aufnehmen und schicken
2. Antwort kommt erstmal "Transkribiere Sprachnachricht..."
3. Dann verarbeitet er die Transkription und antwortet

### Test 6: Befehle

1. Schick `/help`, um alle Befehle zu sehen
2. Schick `/compact`, um den Kontext-Kompressor zu testen (nützlich nach langen Gesprächen)

Wenn alle Tests durch sind, sag mit Pause und Wärme:
> *"Dein Mitarbeiter ist jetzt auf Handy und Rechner erreichbar. Schreib ihm oder sprich mit ihm."*

Jetzt richten wir ihn so ein, dass er rund um die Uhr läuft.

---

## DEPLOYMENT

Jetzt sorgen wir dafür, dass dein Mitarbeiter durchgehend läuft, damit er immer da ist, wenn du ihn brauchst.

### Wenn PLATFORM = laptop

"Für den Anfang startest du den Mitarbeiter manuell mit `python -m apps.command.main`, wenn du ihn brauchst. Sobald du den Laptop zuklappst, ist er aus. Wenn du echte Rund-um-die-Uhr-Verfügbarkeit willst, sind Mac Mini, VPS oder Cloud-Server eine Option, die wir hier nicht aufsetzen."

Spring zu WAS ALS NÄCHSTES.

### Wenn PLATFORM = mac

Wir nutzen macOS launchd, das hält die Stimme am Leben und startet sie automatisch neu, falls sie crasht.

1. Plist-Vorlage aus dem `config/`-Ordner kopieren:
```bash
cp config/com.ceogpt.stimme.plist ~/Library/LaunchAgents/com.ceogpt.stimme.plist
```

2. Plist bearbeiten und Platzhalter ersetzen:
   - `__VENV_PYTHON__` → voller Pfad zu deinem venv-Python (mit aktivem venv `which python` ausführen)
   - `__WORKSPACE_ROOT__` → voller Pfad zu deinem CEO-GPT (`pwd` im CEO-GPT ausführen)
   - `__USERNAME__` → dein macOS-Username (`whoami` ausführen)

3. Log-Ordner anlegen:
```bash
mkdir -p data
```

4. Service laden:
```bash
launchctl load ~/Library/LaunchAgents/com.ceogpt.stimme.plist
```

5. Prüfen:
```bash
launchctl list | grep ceogpt.stimme
```
Sollte eine PID und Exit-Code 0 zeigen.

6. Wenn der Bot-Prozess noch manuell läuft, mit Ctrl+C beenden, launchd übernimmt jetzt.

**Verwaltung:**
- **Stop:** `launchctl unload ~/Library/LaunchAgents/com.ceogpt.stimme.plist`
- **Neustart:** Unload, dann Load, oder `/reboot` in Telegram schicken
- **Logs ansehen:** `tail -f data/command.stdout.log`

### Wenn PLATFORM = linux

Wir nutzen systemd, der Standard-Service-Manager unter Linux.

1. Service-Vorlage aus dem `config/`-Ordner nach systemd kopieren:
```bash
sudo cp config/command-bot.service /etc/systemd/system/command-bot.service
```

2. Service-Datei bearbeiten, Platzhalter ersetzen:
   - `__VENV_PYTHON__` → voller Pfad zum venv-Python
   - `__WORKSPACE_ROOT__` → voller Pfad zum CEO-GPT
   - `__USERNAME__` → dein Linux-Username

3. Aktivieren und starten:
```bash
sudo systemctl daemon-reload
sudo systemctl enable command-bot
sudo systemctl start command-bot
```

4. Prüfen:
```bash
sudo systemctl status command-bot
```
Sollte "active (running)" zeigen.

**Verwaltung:**
- **Stop:** `sudo systemctl stop command-bot`
- **Neustart:** `sudo systemctl restart command-bot` oder `/reboot` in Telegram
- **Logs:** `journalctl -u command-bot -f`

---

## SO NUTZT DU SIE

Jetzt läuft die Stimme. Hier deine Befehls-Übersicht:

| Befehl | Wo | Was er tut |
|---|---|---|
| `/new` | General | Frischen Sonnet-Mitarbeiter in neuem Thread starten |
| `/new opus` | General | Frischen Opus-Mitarbeiter starten (stärkeres Modell) |
| `/name` | Mitarbeiter-Thread | Thread basierend auf dem Gespräch umbenennen |
| `/compact` | Mitarbeiter-Thread | Kontext komprimieren, wenn der Mitarbeiter zu vergessen anfängt |
| `/reset` | Mitarbeiter-Thread | Sitzung zurücksetzen und neu anfangen |
| `/help` | General | Befehlsliste anzeigen |
| `/reboot` | Beliebig | Bot-Prozess neu starten |

**Tipps für den Alltag:**

1. **General-Topic ist dein Wohnzimmer.** Schnelle Fragen, Status-Checks, kleine Aufgaben. Hier behält dein Mitarbeiter den Faden über alle Gespräche.
2. **Für fokussierte Arbeit `/new`.** Jedes größere Thema kriegt seinen eigenen Thread. `/new opus` für Aufgaben, die mehr Denkkraft brauchen.
3. **Threads benennen mit `/name`.** Nach jedem produktiven Gespräch den Befehl absetzen, damit du den Thread später wiederfindest.
4. **Sprachnachrichten sind stark.** Beim Spazierengehen reinquatschen, dein Mitarbeiter verarbeitet alles.
5. **Screenshots reinschicken.** Spannendes Diagramm, Fehler-Meldung, Dokument, alles fotografieren und rein.
6. **`/compact` wenn er anfängt zu vergessen.** Komprimiert das Gespräch und schafft Platz im Kopf.

**Profi-Tipp:** Schreib in deine CLAUDE.md, dass die Stimme erreichbar ist, dann wissen alle Mitarbeiter davon:
```markdown
## Stimme: Telegram-Verbindung
- Bot: läuft rund um die Uhr
- Befehle: /new (Mitarbeiter starten), /name (Thread umbenennen), /compact (Kontext komprimieren)
- Voller CEO-GPT-Zugriff, Dateien, Datenbank, Websuche, Code-Ausführung
- Gespeicherte Sitzungen überleben Neustarts
```

---

## WAS ALS NÄCHSTES

*"Deine Stimme steht. Du erreichst mich jetzt überall, mit Telegram, Voice, Fotos und Screenshots.*

*Als Nächstes käme die Hand. Wir gehen deine wiederkehrenden Aufgaben durch und bauen das System, mit dem ich sie ab jetzt für dich im Blick halte und Stück für Stück übernehme. Setup-Zeit etwa 30 bis 45 Minuten.*

*Willst du gleich weitermachen, oder lieber Pause?"*

Wenn der Member "ja" oder "weiter" sagt, direkt `/install module-installs/ordnung` starten.
Wenn er Pause will, warm verabschieden und sagen dass er einfach `/install module-installs/ordnung` läuft wenn er soweit ist.

## Nützliche Gewohnheiten

Voice-first arbeiten. Beim Spaziergang, beim Autofahren, zwischen Terminen reinquatschen. Du bist nicht mehr an den Schreibtisch gefesselt, dein Mitarbeiter hört zu wo du gerade bist. Wenn er im Chat nicht ganz nach dir klingt, kannst du in `apps/command/worker.py` den Prompt nochmal schärfen. Und in `.claude/commands/` kannst du neue Markdown-Dateien anlegen, jede wird zu einem ausführbaren Befehl wie `/report`, `/analyse` oder `/notiz`.
