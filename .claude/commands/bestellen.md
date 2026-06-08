# /bestellen — Bestellliste erstellen

Hilf Max beim Erstellen einer Bestellliste für das Café-Bar.

## Ablauf

1. Lies `context/business-info.md` (Produktkategorien kennen)
2. Frage Max: "Was brauchen wir? Nenn mir die Kategorien oder Einzelprodukte — ich strukturiere den Rest."
3. Wenn Max antwortet, erstelle eine strukturierte Bestellliste

## Format der Bestellliste

```markdown
# Bestellliste — [DATUM]

## Getränke (Heiß)
| Produkt | Menge | Einheit | Lieferant | Bemerkung |
|---------|-------|---------|-----------|-----------|
| Espresso Bohnen (Drago Mocambo) | 5 | kg | [Lieferant] | |
| ...

## Getränke (Kalt / Bar)
| Produkt | Menge | Einheit | Lieferant | Bemerkung |
|---------|-------|---------|-----------|-----------|
| Aperol | 6 | Flaschen | [Lieferant] | |
| ...

## Weine
| Produkt | Menge | Einheit | Lieferant | Bemerkung |
|---------|-------|---------|-----------|-----------|
| ...

## Speisen & Zutaten
| Produkt | Menge | Einheit | Lieferant | Bemerkung |
|---------|-------|---------|-----------|-----------|
| ...

## Verbrauchsmaterial
| Produkt | Menge | Einheit | Lieferant | Bemerkung |
|---------|-------|---------|-----------|-----------|
| ...

---
Erstellt: [DATUM] | Bearbeitet von: Friday
```

4. Speichere die Liste in `outputs/bestellen-[datum].md`
5. Frage: "Fehlt noch etwas?"

## Tipps für Friday

- Wenn Max vage ist ("Wein nachbestellen"), frag nach Menge und ob bestimmte Sorten
- Saisonale Hinweise geben (Juni → Aperitif-Hochsaison, Rosé wichtig)
- Wenn Lieferanten nicht bekannt, die Spalte leer lassen
- Mengen realistisch halten (Café-Bar-Maßstab, nicht Großhandel)
