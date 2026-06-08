#!/bin/bash
# Friday starten — Scheduler + optionaler Telegram-Bot

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "Setup noch nicht ausgeführt. Bitte zuerst: bash setup.sh"
    exit 1
fi

source .venv/bin/activate

echo ""
echo "════════════════════════════════════════"
echo "  Friday Agentic OS wird gestartet..."
echo "  (Beenden mit Ctrl+C)"
echo "════════════════════════════════════════"
echo ""

python friday.py scheduler
