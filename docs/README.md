# Checklisten-App · Padella Vino

Mobile Web-App (PWA) der Schicht-Checklisten. Zum Abhaken auf dem Handy,
funktioniert offline, Haken werden pro Gerät gespeichert, installierbar auf
dem Startbildschirm.

## Teilbarer Link (GitHub Pages)

Diese App wird aus dem Ordner `docs/` per GitHub Pages ausgeliefert.

**Einmalig aktivieren:**
1. Repo → **Settings → Pages**
2. **Source:** „Deploy from a branch"
3. **Branch:** `claude/mobile-app-conversion-7m5l64` · Ordner: `/docs` → Save

Nach 1–2 Minuten ist der Link live:

    https://ptcdnwrgk4-pixel.github.io/mag/

Diesen Link ans Team schicken. Auf dem Handy: im Browser öffnen →
„Zum Startbildschirm hinzufügen" → läuft dann wie eine App.

## Dateien
- `index.html` – die App
- `manifest.webmanifest` – App-Metadaten (Name, Icons, Farben)
- `sw.js` – Service Worker (Offline-Betrieb)
- `icon-*.png`, `apple-touch-icon.png`, `favicon-64.png` – App-Icons
  (neu erzeugen mit `python3 scripts/make_icons.py`)
