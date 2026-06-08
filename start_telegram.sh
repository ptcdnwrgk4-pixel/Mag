#!/bin/bash
# Friday Telegram Bot starten

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "Setup noch nicht ausgeführt. Bitte zuerst: bash setup.sh"
    exit 1
fi

source .venv/bin/activate

echo ""
echo "════════════════════════════════════════"
echo "  Friday Telegram Bot wird gestartet..."
echo "  (Beenden mit Ctrl+C)"
echo "════════════════════════════════════════"
echo ""

python telegram_bot.py
