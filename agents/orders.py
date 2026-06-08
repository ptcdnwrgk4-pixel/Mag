"""OrdersAgent — Bestelllisten und Lagerstand-Management."""

from datetime import datetime

from .base import AgentResult, SpecialistAgent

_SYSTEM = """
Du bist Friday's Bestell-Assistent für das Padella Vino.

Deine Aufgabe:
- Bestelllisten strukturiert erstellen
- Prioritäten klar kennzeichnen (DRINGEND / DIESE WOCHE / SPÄTER)
- Lieferanten wenn bekannt angeben
- Mengen realistisch einschätzen (Café-Bar, ~60-80k € Umsatz p.a.)

Kategorien:
- ☕ Kaffee & Heißgetränke
- 🍷 Wein & Spirituosen
- 🍹 Bar (Sirups, Mixers, Sprizz-Komponenten)
- 🥗 Küche (Lebensmittel, Frische)
- 📦 Verbrauchsmaterial (Gläser, Servietten, To-Go)
- 🔧 Sonstiges

Format: übersichtliche Tabelle, direkt in Markdown.
"""

_TASK = """
Erstelle die aktuelle Bestellliste für das Padella Vino. Datum: {datum}

1. Lies context/aufgaben.md nach Bestell-Notizen und Engpässen
2. Lies context/current-data.md nach Lagerstand-Hinweisen
3. Lies context/business-info.md für Produktkategorien und Sortiment

Erstelle eine strukturierte Bestellliste:
- Nach Kategorien sortiert
- Priorität pro Position
- Mengenschätzung wenn möglich
- Lieferant wenn bekannt

Speichere als outputs/bestellen-{datum}.md
Gib eine kurze Zusammenfassung zurück: wie viele Positionen, was ist DRINGEND?
"""


class OrdersAgent(SpecialistAgent):
    name = "orders"
    description = "Erstellt und verwaltet Bestelllisten"
    model = "sonnet"
    max_turns = 12
    max_budget_usd = 1.00
    system_append = _SYSTEM

    async def run_scheduled_task(self) -> AgentResult:
        today = datetime.now().strftime("%Y-%m-%d")
        return await self.run(_TASK.format(datum=today))
