"""PersonalAgent — Dienstpläne."""

from datetime import date, timedelta
from pathlib import Path

from .base import AgentResult, SpecialistAgent, _save_output

_SYSTEM = """
Du bist Friday's Personalplaner für das Padella Vino.

Regeln:
- Minijob-Grenze: 556 €/Monat (ca. 40-45h bei Mindestlohn)
- Team: Max (Inhaber) + 1 Teilzeitkraft + 4 Minijobber
- Schichten: Früh (09-14 Uhr), Mittag (12-17 Uhr), Abend (17-22 Uhr)
- Sa/So: höhere Auslastung → mehr Personal

Format: Tabelle (Tag × Schicht × Person) + Stundenübersicht pro Mitarbeiter.
"""

_TASK = """
Erstelle den Dienstplan für KW {kw} ({von} bis {bis}).

Berücksichtige:
- Saisonale Auslastung (aktueller Monat: {monat})
- Minijob-Grenzen für alle Minijobber
- Ausgewogene Verteilung

Liefere:
1. Wochenplan als Tabelle
2. Stundenübersicht (Soll vs. geplant)
3. Hinweise falls Grenzen knapp werden
"""


class PersonalAgent(SpecialistAgent):
    name = "personal"
    description = "Erstellt Dienstpläne"
    system_append = _SYSTEM

    def run_scheduled_task(self) -> AgentResult:
        today = date.today()
        kw = today.isocalendar()[1] + 1
        mon = today + timedelta(days=(7 - today.weekday()))
        sun = mon + timedelta(days=6)

        result = self.run(_TASK.format(
            kw=kw,
            von=mon.strftime("%d.%m."),
            bis=sun.strftime("%d.%m.%Y"),
            monat=mon.strftime("%B"),
        ))

        if not result.is_error and result.text:
            path = _save_output(f"dienstplan-KW{kw}.md", result.text)
            result.output_files = [str(path.relative_to(Path(__file__).parent.parent))]

        return result
