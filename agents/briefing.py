"""BriefingAgent — erstellt das tägliche Business-Briefing."""

from datetime import datetime

from .base import AgentResult, SpecialistAgent

_SYSTEM = """
Du bist Friday's Briefing-Spezialist.
Jeden Morgen analysierst du den aktuellen Stand des Business und erstellst ein prägnantes Briefing.

Dein Stil:
- Direkt und analytisch — keine Floskeln
- Zahlen immer mit Kontext
- Proaktive Einschätzungen: wenn du etwas Wichtiges siehst, sag es
- Max ist auf dem Handy: kurz halten, aber vollständig

Format des Briefings:
1. Datum und Status (eine Zeile)
2. Heutiger Fokus (1-2 Punkte)
3. Stand Strategie (kurz: neue Karte / Social Media)
4. Top 3 offene Aufgaben
5. Friday's Einschätzung (eine direkte Meinung)
"""

_TASK = """
Erstelle das Tages-Briefing für Max. Datum: {datum}

Schritte:
1. Lies context/strategy.md
2. Lies context/current-data.md
3. Lies context/aufgaben.md (falls vorhanden)
4. Analysiere: Was ist heute wichtig? Wo steht das Business?
5. Schreibe das Briefing im definierten Format
6. Speichere als outputs/briefing-{datum}.md
7. Gib eine Kurzzusammenfassung (3-5 Zeilen) als Antwort zurück
"""


class BriefingAgent(SpecialistAgent):
    name = "briefing"
    description = "Erstellt das tägliche Business-Briefing"
    model = "sonnet"
    max_turns = 15
    max_budget_usd = 1.50
    system_append = _SYSTEM

    async def run_scheduled_task(self) -> AgentResult:
        today = datetime.now().strftime("%Y-%m-%d")
        return await self.run(_TASK.format(datum=today))
