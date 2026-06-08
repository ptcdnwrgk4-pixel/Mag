# /aufgaben — Aufgaben-Management

Zeige und verwalte die offenen Aufgaben aus `context/aufgaben.md`.

## Ablauf

1. Lies `context/aufgaben.md`
2. Wenn die Datei nicht existiert, lege sie an mit einer leeren Struktur
3. Zeige die aktuellen Aufgaben übersichtlich an:

---

**AUFGABEN — [DATUM]**

🔴 **DRINGEND**
[Aufgaben mit Status DRINGEND]

🟡 **DIESE WOCHE**
[Aufgaben mit Status DIESE_WOCHE]

🟢 **IRGENDWANN**
[Aufgaben mit Status IRGENDWANN]

✅ **ZULETZT ERLEDIGT**
[Die letzten 3 erledigten Aufgaben, damit Max sieht was gelaufen ist]

---

4. Dann fragen: "Was möchtest du tun?"

## Mögliche Aktionen

- **Neue Aufgabe:** "Füge hinzu: [Aufgabe] — [Priorität]"
- **Erledigt:** "Hak ab: [Aufgabe]" → verschieben in den ✅-Bereich mit Datum
- **Priorität ändern:** "Ändere Priorität von [Aufgabe] auf [DRINGEND/DIESE_WOCHE/IRGENDWANN]"
- **Aufgabe löschen:** "Lösche: [Aufgabe]"
- **Alle abgehakten löschen:** "Archiviere Erledigtes"

## Format in context/aufgaben.md

```markdown
# Aufgaben

## DRINGEND
- [ ] Aufgabe hier (hinzugefügt: DATUM)

## DIESE WOCHE  
- [ ] Aufgabe hier

## IRGENDWANN
- [ ] Aufgabe hier

## ERLEDIGT
- [x] Erledigte Aufgabe (erledigt: DATUM)
```

Aktualisiere die Datei nach jeder Änderung sofort.
Friday merkt sich den Kontext und schlägt proaktiv Prioritäten vor, wenn eine Aufgabe zu lange offen ist.
