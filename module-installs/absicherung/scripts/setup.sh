#!/bin/bash
# CEO-GPT Absicherung – setup.sh
# Initialisiert Git, legt .gitignore an, macht ersten Commit

set -e

echo ""
echo "CEO-GPT Absicherung wird eingerichtet..."
echo ""

# Git initialisieren
if [ ! -d ".git" ]; then
  git init
  git checkout -b main 2>/dev/null || git branch -M main
  echo "Git initialisiert."
else
  echo "Git bereits vorhanden – überspringe init."
fi

# .gitignore anlegen
if [ ! -f ".gitignore" ]; then
  cat > .gitignore << 'EOF'
# API-Keys und Zugänge – niemals committen
.env
.env.*
*.env

# Betriebssystem
.DS_Store
Thumbs.db
desktop.ini

# Editor
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
*.log
logs/

# Node
node_modules/
npm-debug.log*

# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/
env/

# Temporäre Dateien
tmp/
temp/
*.tmp
*.temp
EOF
  echo ".gitignore angelegt – .env ist geschützt."
else
  # Sicherstellen dass .env drin ist
  if ! grep -q "^\.env$" .gitignore 2>/dev/null; then
    echo "" >> .gitignore
    echo "# API-Keys – niemals committen" >> .gitignore
    echo ".env" >> .gitignore
    echo ".env in bestehende .gitignore ergänzt."
  else
    echo ".gitignore bereits vorhanden und .env geschützt."
  fi
fi

# Warnung falls .env existiert aber nicht ignoriert wird
if [ -f ".env" ]; then
  if git check-ignore -q .env 2>/dev/null; then
    echo ".env ist geschützt – wird nicht hochgeladen."
  else
    echo ""
    echo "ACHTUNG: .env gefunden aber nicht in .gitignore."
    echo "Bitte prüfen bevor du pushst."
    echo ""
  fi
fi

# Ersten Commit oder aktuellen Stand committen
COMMIT_COUNT=$(git rev-list --count HEAD 2>/dev/null || echo "0")

if [ "$COMMIT_COUNT" = "0" ]; then
  git add .
  git commit -m "CEO-GPT: Initialer Stand – Absicherung eingerichtet"
  echo "Erster Commit erstellt."
else
  if [ -n "$(git status --porcelain)" ]; then
    git add .
    git commit -m "CEO-GPT: Absicherungs-Modul hinzugefügt"
    echo "Änderungen committed."
  else
    echo "Alles sauber – kein neuer Commit nötig."
  fi
fi

echo ""
echo "Lokal fertig. Git läuft, .env ist geschützt."
echo ""
