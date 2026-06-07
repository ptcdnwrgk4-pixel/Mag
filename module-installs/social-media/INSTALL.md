# Modul: Social Media – INSTALL.md

> **Für den Mitarbeiter (Claude Code).** Drehbuch für alle Social-Media-Aufgaben.

---

## Kontext

**Account:** @padellavino
**Plattform:** Instagram (Stories + Highlights)
**Stil:** Locker, persönlich, auf Deutsch. Nah am Gast. Nicht übertrieben. 1–2 Emojis.
**Foto-Ordner:** `context/social-media/`

**Standard-Hashtags:**
`#padellavino #dieburg #marktplatzdieburg #cafedieburg #aperitivo #sprizz #weinliebhaber #gastro #genuss #kaffeeliebe`

**Highlight-Kategorien:**
- ☕ Kaffee → Highlight "Kaffee"
- 🍹 Sprizz & Aperitif → Highlight "Sprizz"
- 🍷 Wein → Highlight "Wein"
- 🍽️ Speisen & Antipasti → Highlight "Speisen"
- 🎉 Aktionen & Events → Highlight "Aktionen"
- 🌟 Angebot der Woche → Highlight "Angebot"

---

## Befehl: "Erstell den heutigen Story-Post"

1. Schaue in `context/social-media/` – nimm das neueste Foto
2. Erkenne was auf dem Foto zu sehen ist
3. Schreibe eine lockere, persönliche Caption auf Deutsch (2–4 Sätze, 1–2 Emojis)
4. Füge die Standard-Hashtags an
5. Weise das passende Highlight zu
6. Ausgabe-Format:

---
**📸 Foto:** [Dateiname]
**📝 Caption:**
[Caption-Text]

[Hashtags]

**🗂️ Highlight:** [Kategorie]
---

---

## Befehl: "Erstell den Angebot-der-Woche-Post"

Max nennt das Angebot. Dann:

1. Schreibe einen Post der das Angebot klar und appetitlich beschreibt
2. Preis nennen falls angegeben
3. Call-to-action am Ende ("Komm vorbei!", "Diese Woche bei uns!", etc.)
4. Standard-Hashtags + `#angebotderwoche`
5. Highlight: "Angebot"

---

## Befehl: "Erstell einen Post für [Produkt/Anlass]"

Flexibler Post für spezifische Anlässe – neues Signature-Getränk, neues Sandwich, saisonales Angebot, Event.

Gleiche Struktur wie oben, angepasst an den Anlass.

---

## Caption-Stil – Beispiele

**Gut:**
"Frisch aus dem Ofen und direkt auf den Tisch ☕ Unser Cappuccino wartet schon auf dich – komm vorbei und gönn dir eine Pause am Marktplatz."

**Gut:**
"Sommerlaune auf Knopfdruck 🍹 Der Aperol Sprizz läuft heute besonders gut. Schau einfach vorbei – wir haben noch Plätze."

**Vermeiden:**
- Übertriebene Ausrufezeichen (!!!)
- Englische Phrasen
- Mehr als 2 Emojis
- Generisches ("Wir lieben was wir tun!")

---

## Wöchentlicher Ablauf

| Tag | Aufgabe |
|---|---|
| Täglich 9 Uhr | Story-Post aus neuestem Foto in `context/social-media/` |
| Montags 9 Uhr | Angebot der Woche – Max nennt das Angebot, Post wird erstellt |

---

## Nach Einrichtung in CLAUDE.md ergänzen

Hinweis im Abschnitt "Befehle":
- `erstell den heutigen Story-Post`
- `erstell den Angebot-der-Woche-Post`
