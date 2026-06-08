# /personal [woche] — Personalplanung

Hilf Max beim Erstellen des Dienstplans für das Café-Bar-Team.

## Team-Kontext (aus context/)

Team: 1 Teilzeitkraft, 4 Minijobber, Max als Backup.
Lies `context/business-info.md` für aktuellen Team-Stand.

## Ablauf

1. Frage nach der Woche: "Für welche Woche planst du? (KW oder Datum)" — außer Max hat es schon angegeben
2. Frage nach besonderen Umständen: "Gibt es Urlaube, Ausfälle, besondere Events diese Woche?"
3. Erstelle den Dienstplan

## Format des Dienstplans

```markdown
# Dienstplan KW [XX] — [DATUM VON] bis [DATUM BIS]

| Zeit | Mo | Di | Mi | Do | Fr | Sa | So |
|------|----|----|----|----|----|----|-----|
| Früh | | | | | | | |
| Mittag | | | | | | | |
| Abend | | | | | | | |

## Mitarbeiter-Übersicht

| Name | Rolle | Stunden diese Woche | Bemerkung |
|------|-------|---------------------|-----------|
| [Name] | Teilzeit | XX h | |
| [Name] | Minijob | XX h | |
| ...

## Gesamtstunden: XX h

## Hinweise
- [Besonderheiten, Engpässe, offene Fragen]
```

4. Speichere in `outputs/dienstplan-kw[xx]-[jahr].md`
5. Frage: "Passt das so, oder soll ich etwas anpassen?"

## Hinweise für Friday

- Minijobbern max. 556 € pro Monat (Minijob-Grenze) im Blick behalten
- Bei Engpässen direkt darauf hinweisen und Max als Backup einplanen
- Freitag und Samstag sind erfahrungsgemäß die stärksten Tage → mehr Personal einplanen
- Wenn Max einzelne Schichten selbst übernimmt, das im Plan markieren
