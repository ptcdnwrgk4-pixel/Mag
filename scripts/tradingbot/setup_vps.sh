#!/bin/bash
# TradingBot – VPS Setup Script
# Läuft auf einem frischen Ubuntu 22.04 / 24.04 Server.
# Einmalig ausführen: bash setup_vps.sh

set -e

REPO_URL="https://github.com/ptcdnwrgk4-pixel/Mag.git"
APP_DIR="$HOME/Mag"
PYTHON="python3"
SERVICE_NAME="tradingbot"

echo ""
echo "======================================================"
echo "  TradingBot VPS Setup"
echo "======================================================"
echo ""

# 1. System aktualisieren
echo "[1/7] System aktualisieren …"
sudo apt-get update -q
sudo apt-get upgrade -y -q

# 2. Abhängigkeiten installieren
echo "[2/7] Pakete installieren (Python, Git, TA-Lib) …"
sudo apt-get install -y -q \
    python3 python3-pip python3-venv \
    git curl wget \
    build-essential \
    libssl-dev libffi-dev

# TA-Lib C-Bibliothek (wird von ta-lib Python-Paket benötigt)
if ! ldconfig -p | grep -q libta_lib; then
    echo "    → TA-Lib C-Bibliothek bauen …"
    cd /tmp
    wget -q https://github.com/ta-lib/ta-lib/releases/download/v0.6.4/ta-lib-0.6.4-src.tar.gz
    tar -xzf ta-lib-0.6.4-src.tar.gz
    cd ta-lib-0.6.4
    ./configure --prefix=/usr
    make -j"$(nproc)" > /dev/null
    sudo make install > /dev/null
    sudo ldconfig
    cd "$HOME"
else
    echo "    → TA-Lib bereits installiert, übersprungen"
fi

# 3. Repo klonen oder aktualisieren
echo "[3/7] Repository klonen/aktualisieren …"
if [ -d "$APP_DIR/.git" ]; then
    cd "$APP_DIR"
    git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || true
    echo "    → Bereits vorhanden, aktualisiert"
else
    git clone "$REPO_URL" "$APP_DIR"
    echo "    → Geklont nach $APP_DIR"
fi

# 4. Python-Umgebung einrichten
echo "[4/7] Python-Abhängigkeiten installieren …"
cd "$APP_DIR"
$PYTHON -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
deactivate

# 5. .env Vorlage anlegen (falls nicht vorhanden)
echo "[5/7] .env prüfen …"
if [ ! -f "$APP_DIR/.env" ]; then
    cat > "$APP_DIR/.env" << 'EOF'
# Trade Republic Bot
# Mit python scripts/tradingbot/bot.py --setup ausfüllen
# TR_PHONE=+49...
# TR_PIN=1234
EOF
    echo "    → .env angelegt"
else
    echo "    → .env bereits vorhanden"
fi

# 6. systemd Service einrichten (Bot startet automatisch, auch nach Neustart)
echo "[6/7] systemd Service einrichten …"

SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
VENV_PYTHON="$APP_DIR/.venv/bin/python3"
BOT_SCRIPT="$APP_DIR/scripts/tradingbot/bot.py"
LOG_FILE="$APP_DIR/scripts/tradingbot/bot.log"
CURRENT_USER="$(whoami)"

sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=TradingBot Trade Republic (RSI + Bollinger Band)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${CURRENT_USER}
WorkingDirectory=${APP_DIR}
ExecStart=${VENV_PYTHON} ${BOT_SCRIPT}
Restart=always
RestartSec=60
Environment=PYTHONUNBUFFERED=1

# Log direkt in Datei zusätzlich zum Journal
StandardOutput=append:${LOG_FILE}
StandardError=append:${LOG_FILE}

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
echo "    → Service aktiviert (startet nach Reboot automatisch)"

# 7. Fertig
echo ""
echo "[7/7] Setup abgeschlossen."
echo ""
echo "======================================================"
echo "  Nächste Schritte:"
echo "======================================================"
echo ""
echo "  1. Trade Republic Login einrichten (einmalig):"
echo "     cd $APP_DIR"
echo "     source .venv/bin/activate"
echo "     python scripts/tradingbot/bot.py --setup"
echo ""
echo "  2. Bot testen (kein Echtgeld):"
echo "     python scripts/tradingbot/bot.py --dry-run"
echo ""
echo "  3. Bot als Service starten:"
echo "     sudo systemctl start $SERVICE_NAME"
echo ""
echo "  4. Status prüfen:"
echo "     sudo systemctl status $SERVICE_NAME"
echo "     tail -f $APP_DIR/scripts/tradingbot/bot.log"
echo ""
echo "  5. Bot stoppen:"
echo "     sudo systemctl stop $SERVICE_NAME"
echo ""
echo "======================================================"
