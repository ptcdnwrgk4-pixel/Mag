# Modul: Absicherung – INSTALL.md

> **Diese Datei ist für den Mitarbeiter (Claude Code) geschrieben.** Sie ist dein Drehbuch für die Einrichtung. Lies sie vollständig, bevor du anfängst.

---

## Was diese Fähigkeit tut

Die Absicherung legt das Fundament des CEO-GPT:

1. **Git-Versionskontrolle** – Jede Sitzung wird gesichert. Nichts geht verloren.
2. **Remote-Backup** – Eine Kopie liegt im Internet, privat und sicher.
3. **Saubere `.gitignore`** – API-Keys und sensible Dateien bleiben lokal. Immer.

Nach dieser Einrichtung ist das CEO-GPT versioniert, gesichert und bereit zum Wachsen.

---

## FÜR CLAUDE: Verhaltensregeln für diese Einrichtung

- Erklär jeden Schritt in normalem Deutsch, BEVOR du ihn ausführst
- Der Geschäftsführer ist nicht-technisch. Kein Git-Jargon, keine Fachbegriffe ohne Erklärung
- Pausier nach jedem Schritt mit einer kurzen Bestätigung ("Das läuft. Weiter?")
- Wenn etwas schiefgeht: Problem schlicht erklären, sofort fixen, kein Error-Log-Dump
- Feier Fortschritt ("Gut. Die Basis steht.")

---

## Schritt 1: Git-Status prüfen

Prüf zuerst, ob Git schon eingerichtet ist:

```bash
git -C . rev-parse --is-inside-work-tree 2>/dev/null && echo "GIT_VORHANDEN" || echo "KEIN_GIT"
```

**Wenn `GIT_VORHANDEN`:** Sag dem Geschäftsführer: "Git ist schon drin – überspringe die Einrichtung." Weiter zu Schritt 3.

**Wenn `KEIN_GIT`:** Sag: "Ich richte jetzt die Versionskontrolle ein. Das dauert eine Minute." Weiter zu Schritt 2.

---

## Schritt 2: Git initialisieren

Führe das Setup-Skript aus:

```bash
bash module-installs/absicherung/scripts/setup.sh
```

Das Skript:
- Initialisiert Git
- Legt die `.gitignore` an (schützt `.env` und sensible Dateien)
- Macht den ersten Commit

Wenn das Skript erfolgreich war, sag: "Gut. Versionskontrolle läuft. Dein CEO-GPT ist jetzt gesichert – lokal."

---

## Schritt 3: Remote-Backup einrichten

Frag den Geschäftsführer:

> "Jetzt richten wir das Backup im Internet ein. Ich empfehle GitHub – kostenlos, weit verbreitet, privates Repo reicht. GitLab geht auch. Was bevorzugst du?"

Warte auf Antwort.

### Option A: GitHub

Erkläre:
> "Gut. Ich führe dich jetzt durch drei Klicks. Das Repo bleibt privat – nur du hast Zugriff."

Anleitung für den Geschäftsführer (Schritt für Schritt erklären, nicht nur auflisten):

1. Öffne https://github.com/new in deinem Browser
2. Name: `ceo-gpt` (oder was du möchtest)
3. Sichtbarkeit: **Private** auswählen (wichtig!)
4. Klick auf "Create repository"
5. Kopiere die URL, die erscheint – sie sieht so aus: `https://github.com/DEINNAME/ceo-gpt.git`

Frag: "Hast du die URL? Dann gib sie mir."

### Option B: GitLab

1. Öffne https://gitlab.com/projects/new in deinem Browser
2. Name: `ceo-gpt`
3. Sichtbarkeit: **Private**
4. Klick auf "Create project"
5. Kopiere die URL: `https://gitlab.com/DEINNAME/ceo-gpt.git`

Frag: "Hast du die URL? Dann gib sie mir."

### Remote verbinden

Sobald du die URL hast:

```bash
git remote add origin REPO_URL_HIER
git branch -M main
git push -u origin main
```

Wenn der Push erfolgreich war, sag: "Perfekt. Dein CEO-GPT liegt jetzt sicher im Internet. Nur du hast Zugriff."

---

## Schritt 4: Prüfen

```bash
git status
git log --oneline -3
git remote -v
```

Erwartetes Ergebnis:
- `git status` zeigt "nothing to commit"
- `git log` zeigt mindestens einen Commit
- `git remote` zeigt die Remote-URL

Wenn alles stimmt, weiter zu Schritt 5.

---

## Schritt 5: Commit-Workflow erklären

Erkläre dem Geschäftsführer:

> "Ab jetzt kannst du nach jeder Sitzung deine Arbeit mit einem Befehl sichern:
>
> `git add . && git commit -m 'Sitzung gesichert' && git push`
>
> Oder ich erledige das für dich am Ende jeder Sitzung automatisch. Soll ich das übernehmen?"

Warte auf Antwort.

**Falls Ja:** Notiere in `context/personal-info.md` am Ende unter einem neuen Abschnitt:

```
## Präferenzen

- Am Ende jeder Sitzung automatisch committen und pushen
```

---

## Schritt 6: CLAUDE.md aktualisieren

Prüf CLAUDE.md auf folgende Punkte und ergänze sie, falls noch nicht vorhanden:

1. In der Ordner-Struktur: `.git/` als eingerichtet markieren
2. In "Hinweise": den Satz "API-Keys in `.env`, diese Datei niemals committen" – sollte bereits da sein, sonst ergänzen
3. Optional: Kurzen Hinweis auf den Commit-Befehl im Abschnitt "Sitzungs-Ablauf"

---

## Schritt 7: Abschluss

Sag dem Geschäftsführer:

> "Absicherung steht. Dein CEO-GPT ist versioniert, läuft lokal und hat ein Backup im Internet. Nichts geht mehr verloren.
>
> Das war Schritt 1. Bereit für Schritt 2 – den Kontext? Mit `/install module-installs/kontext` bekommt dein Mitarbeiter sein Gehirn."
