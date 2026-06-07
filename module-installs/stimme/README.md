# Stimme

> Die Stimme deines Mitarbeiters. Du sprichst mit ihm vom Handy aus, er antwortet, egal wo du bist.

| Feld | Wert |
|---|---|
| Modul | `stimme` |
| Version | v1 |
| Status | RELEASED |
| Released | 2026-02-27 |
| Voraussetzung | Kontext (du brauchst eine CLAUDE.md) |
| Setup-Zeit | 30 bis 45 Minuten |
| Laufende Kosten | Claude-Code-Subscription (Auth über CLI) + optional OpenRouter für Voice |

## Was hier passiert

Bis jetzt sitzt dein Mitarbeiter auf deinem Rechner. Sobald du den Laptop zuklappst, ist er weg.

Mit der Stimme lebt er in deiner Tasche. Du chattest mit ihm über Telegram wie mit einem Kollegen. Tippen oder Sprachnachricht, Foto oder Screenshot, alles geht rein. Er antwortet mit Text, Tabelle oder PDF.

- **Mitarbeiter im Chat erreichbar.** Eine Telegram-Gruppe ist sein Büro, du schreibst rein, er antwortet. Solange dein Mac eingeschaltet ist, läuft dein Mitarbeiter. Wenn du echte Rund-um-die-Uhr-Verfügbarkeit willst, sind dafür Mini-Server oder Cloud-Setups eine Option, die wir hier nicht aufsetzen.
- **Allgemeiner Mitarbeiter, der sich erinnert.** Der Haupt-Chat behält den Faden, auch über Tage hinweg.
- **Frische Mitarbeiter für einzelne Themen.** Mit `/new` startest du einen sauberen Mitarbeiter in einem eigenen Thread, wie ein neuer Tab.
- **Sprachnachrichten verarbeiten.** Rein quatschen, er versteht und arbeitet weiter (optional, braucht OpenRouter Key — günstiges Whisper-Turbo).
- **Fotos und Screenshots verarbeiten.** Bild rein, er sieht es und kommentiert.
- **Saubere Ausgabe.** Tabellen sauber, Diagramme als Bild, längere Reports als PDF.

## Was du brauchst

- Einen Computer (Mac oder Linux), der durchlaufen kann, oder erstmal nur Laptop für Tests
- Telegram-Account auf Handy und Rechner
- Claude Code installiert und **eingeloggt** (`claude` CLI muss authentifiziert sein — Mitarbeiter-Brain läuft über deine Subscription)
- Eine bestehende CLAUDE.md (kommt aus `kontext`)
- Optional einen OpenRouter API Key (für Sprachnachrichten via Whisper-Turbo)

## Installation

1. Der `stimme` Ordner liegt schon in `module-installs/`
2. Führe `/install module-installs/stimme` aus
3. Folge der Anleitung, dein Mitarbeiter führt dich Schritt für Schritt durch

**Geschätzte Setup-Zeit:** 30 bis 45 Minuten

## Kosten

- **Claude-Code-Subscription:** Mitarbeiter-Brain läuft über deine bestehende Claude-Auth, kein separater API-Verbrauch.
- **OpenRouter (optional, nur für Voice):** Whisper-large-v3-turbo kostet ~0,04 $/h Audio (~9× günstiger als OpenAI direkt). Mindestaufladung 5–10 $ reicht lange.
- **Telegram:** kostenlos
- **Hosting:** dein eigener Rechner, kein externer Server nötig

## Was hier drin liegt

| Datei | Zweck |
|---|---|
| `INSTALL.md` | Geführte Installation (liest dein Mitarbeiter und führt dich durch) |
| `README.md` | Diese Datei, der Überblick für dich |
| `scripts/apps/command/` | Der Code, der dein Mitarbeiter zur Stimme macht |
| `scripts/.claude/commands/` | Prime-Vorlagen, damit dein Mitarbeiter beim Start weiß, wo er ist |
| `config/` | Vorlagen, damit die Stimme rund um die Uhr läuft (Mac und Linux) |
| `templates/` | CLAUDE.md-Vorlage für den Fall, dass du Kontext noch nicht eingerichtet hast |

## Befehle, die du nach der Installation hast

| Befehl | Wo | Was er tut |
|---|---|---|
| `/new` | Allgemeiner Chat | Frischen Mitarbeiter in neuem Thread starten (Sonnet) |
| `/new opus` | Allgemeiner Chat | Frischen Mitarbeiter mit dem stärkeren Modell (Opus) |
| `/name` | Mitarbeiter-Thread | Thread sinnvoll umbenennen, basierend auf dem Gespräch |
| `/compact` | Mitarbeiter-Thread | Kontext komprimieren, wenn das Gespräch lang wird |
| `/reset` | Mitarbeiter-Thread | Mitarbeiter zurücksetzen und neu anfangen |
| `/help` | Allgemeiner Chat | Befehlsliste anzeigen |
| `/reboot` | Beliebig | Bot-Prozess neu starten |

## Pro-Tipp

Die Sprachnachricht-Option lohnt sich. Beim Spaziergang ins Handy reden, dein Mitarbeiter hört zu, transkribiert und arbeitet weiter, während du läufst. Drei Minuten reden ersetzt zwanzig Minuten am Rechner tippen.

## Nach diesem Modul

Dein Mitarbeiter ist auf Handy und Rechner erreichbar. Schreib ihm oder sprich mit ihm. Im nächsten Schritt nimmt er dir wiederkehrende Aufgaben ab mit `/install module-installs/ordnung`.
