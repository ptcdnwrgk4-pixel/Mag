#!/bin/bash
# Friday starten

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "Setup noch nicht ausgeführt. Bitte zuerst: ./setup.sh"
    exit 1
fi

source .venv/bin/activate

echo ""
echo "════════════════════════════════════════"
echo "  Friday wird gestartet..."
echo "  (Beenden mit Ctrl+C)"
echo "════════════════════════════════════════"
echo ""

python -m apps.command.main
