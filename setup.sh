#!/bin/bash
# Friday Setup — einmalig ausführen

set -e

echo ""
echo "════════════════════════════════════════"
echo "  Friday — Einrichtung"
echo "════════════════════════════════════════"
echo ""

# ── Python prüfen ─────────────────────────────────────────────────────────────

echo "▶ Python wird geprüft..."

# Python 3.12 bevorzugen (3.14 hat macOS-Kompatibilitätsprobleme)
if command -v python3.12 &>/dev/null; then
    PYTHON=python3.12
elif command -v python3.11 &>/dev/null; then
    PYTHON=python3.11
elif command -v python3 &>/dev/null; then
    PYTHON=python3
else
    echo ""
    echo "✗ Python nicht gefunden."
    echo ""
    echo "  Bitte installieren: https://www.python.org/downloads/release/python-3126/"
    echo "  → macOS 64-bit universal2 installer"
    echo ""
    exit 1
fi

# Version prüfen
PYTHON_VERSION=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)

if [ -z "$PYTHON_VERSION" ]; then
    echo ""
    echo "✗ Python gefunden, aber nicht lauffähig (möglicherweise macOS-Kompatibilitätsproblem)."
    echo ""
    echo "  Bitte Python 3.12 installieren:"
    echo "  https://www.python.org/downloads/release/python-3126/"
    echo "  → macOS 64-bit universal2 installer"
    echo ""
    exit 1
fi

if $PYTHON -c "import sys; exit(0 if sys.version_info >= (3,11) else 1)" 2>/dev/null; then
    echo "  ✓ Python $PYTHON_VERSION ($PYTHON)"
else
    echo ""
    echo "  ✗ Python $PYTHON_VERSION — mindestens 3.11 benötigt."
    echo ""
    echo "  Bitte Python 3.12 installieren:"
    echo "  https://www.python.org/downloads/release/python-3126/"
    echo ""
    exit 1
fi

# ── Virtuelle Umgebung ────────────────────────────────────────────────────────

if [ ! -d ".venv" ]; then
    echo "▶ Virtuelle Umgebung wird erstellt..."
    $PYTHON -m venv .venv
    echo "  ✓ .venv erstellt"
else
    echo "  ✓ .venv vorhanden"
fi

source .venv/bin/activate

# ── Pakete installieren ───────────────────────────────────────────────────────

echo "▶ Pakete werden installiert..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "  ✓ Pakete installiert"

# ── .env prüfen ───────────────────────────────────────────────────────────────

echo "▶ Konfiguration wird geprüft..."

if [ ! -f ".env" ]; then
    echo ""
    echo "  ✗ .env fehlt — bitte anlegen."
    echo ""
    echo "  Erstelle die Datei .env im Mag-Ordner mit folgendem Inhalt:"
    echo ""
    echo "    TELEGRAM_BOT_TOKEN=<dein-bot-token>"
    echo "    TELEGRAM_GROUP_ID=<deine-group-id>"
    echo ""
    exit 1
fi

if ! grep -q "ANTHROPIC_API_KEY=sk-ant-" .env 2>/dev/null; then
    echo ""
    echo "  ✗ ANTHROPIC_API_KEY fehlt in .env"
    echo ""
    echo "  Key holen unter: console.anthropic.com → API Keys → Create Key"
    echo "  Dann in .env eintragen: ANTHROPIC_API_KEY=sk-ant-..."
    echo ""
    exit 1
fi

echo "  ✓ .env vollständig"

# ── Fertig ────────────────────────────────────────────────────────────────────

echo ""
echo "════════════════════════════════════════"
echo "  ✓ Setup abgeschlossen"
echo ""
echo "  Friday starten:"
echo "    ./start.sh"
echo ""
echo "  Oder einzelnen Agenten testen:"
echo "    source .venv/bin/activate && python friday.py briefing"
echo "════════════════════════════════════════"
echo ""
