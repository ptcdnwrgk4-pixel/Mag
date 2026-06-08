"""PersonalAgent — Dienstpläne und Team-Management."""

from datetime import date

from .base import AgentResult, SpecialistAgent

_SYSTEM = """
Du bist Friday's Personalplaner für das Padella Vino.

Das Team:
- Max (Inhaber, immer dabei)
- 1 Teilzeitkraft
- 4 Minijobber

Wichtige Regeln:
- Minijob-Grenze: 556 €/Monat (ca. 40-45h bei Mindestlohn)
- Öffnungszeiten: typ. Di-So, Frühschicht ab 09:00, Abend bis ~22:00
- Samstag/Sonntag: höhere Auslastung — mehr Personal einplanen
- Saisonalität berücksichtigen (Sommer = Terrasse = mehr Bedarf)

Format: Wochenplan als Tabelle (Tag × Schicht × Person), darunter Stundenübersicht.
"""

_TASK = """
Erstelle den Dienstplan für KW {kw} ({von} bis {bis}).

1. Lies context/personal-info.md (Team-Details, falls vorhanden)
2. Lies context/current-data.md nach Auslastungshinweisen
3. Lies context/aufgaben.md nach Personal-Notizen

Erstelle:
- Wochenplan als Tabelle
- Stunden-Übersicht pro Mitarbeiter
- Hinweis wenn Minijob-Grenze in Gefahr
- Besondere Hinweise (Feiertage, Events)

Speichere als outputs/dienstplan-KW{kw}.md
"""


class PersonalAgent(SpecialistAgent):
    name = "personal"
    description = "Erstellt Dienstpläne und verwaltet das Team"
    model = "sonnet"
    max_turns = 15
    max_budget_usd = 1.00
    system_append = _SYSTEM

    async def run_scheduled_task(self) -> AgentResult:
        today = date.today()
        iso = today.isocalendar()
        kw = iso[1] + 1  # Nächste Woche planen

        from datetime import timedelta
        mon = today + timedelta(days=(7 - today.weekday()))
        sun = mon + timedelta(days=6)

        return await self.run(
            _TASK.format(
                kw=kw,
                von=mon.strftime("%d.%m."),
                bis=sun.strftime("%d.%m.%Y"),
            )
        )
