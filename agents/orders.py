"""OrdersAgent — Bestelllisten."""

from datetime import datetime
from pathlib import Path

from .base import AgentResult, SpecialistAgent, _save_output

_SYSTEM = """
Du bist Friday's Bestell-Assistent für das Padella Vino.

Erstelle strukturierte Bestelllisten mit:
- Kategorisierung: ☕ Kaffee | 🍷 Wein/Spirits | 🍹 Bar | 🥗 Küche | 📦 Verbrauchsmaterial
- Priorität pro Position: DRINGEND / DIESE WOCHE / SPÄTER
- Menge wenn einschätzbar
- Lieferant wenn bekannt

Format: Tabelle in Markdown.
"""

_TASK = """
Erstelle die aktuelle Bestellliste für das Padella Vino. Datum: {datum}

Analysiere den Kontext auf Hinweise zu:
- Niedrigem Lagerbestand
- Ausstehenden Bestellungen aus aufgaben.md
- Saisonalen Besonderheiten

Erstelle dann die vollständige, priorisierte Bestellliste.
"""


class OrdersAgent(SpecialistAgent):
    name = "orders"
    description = "Erstellt Bestelllisten"
    system_append = _SYSTEM

    def run_scheduled_task(self) -> AgentResult:
        today = datetime.now().strftime("%Y-%m-%d")
        result = self.run(_TASK.format(datum=today))

        if not result.is_error and result.text:
            path = _save_output(f"bestellen-{today}.md", result.text)
            result.output_files = [str(path.relative_to(Path(__file__).parent.parent))]

        return result
