"""BriefingAgent — erstellt das tägliche Business-Briefing."""

from datetime import datetime
from pathlib import Path

from .base import AgentResult, SpecialistAgent, _save_output

_SYSTEM = """
Du bist Friday's Briefing-Spezialist.
Jeden Morgen analysierst du den Stand des Business und erstellst ein prägnantes Briefing.

Format (strikt einhalten):
**BRIEFING — {DATUM}**

**Heutiger Fokus**
• [wichtigste Aufgabe heute]

**Stand Strategie**
• Neue Karte: [Status]
• Social Media: [Status]

**Top 3 Aufgaben**
1. [Aufgabe]
2. [Aufgabe]
3. [Aufgabe]

**Friday's Einschätzung**
[Eine direkte, ehrliche Einschätzung — was läuft gut, was hakt, was fehlt]

---
Sei präzise und direkt. Max ist beschäftigt.
"""

_TASK = """
Erstelle das Tages-Briefing für Max. Datum heute: {datum}

Analysiere den Business-Kontext aus den context/-Dateien und schreibe das Briefing
exakt im vorgegebenen Format. Konzentriere dich auf das Wesentliche.
"""


class BriefingAgent(SpecialistAgent):
    name = "briefing"
    description = "Erstellt das tägliche Business-Briefing"
    system_append = _SYSTEM

    def run_scheduled_task(self) -> AgentResult:
        today = datetime.now().strftime("%Y-%m-%d")
        result = self.run(_TASK.format(datum=today))

        if not result.is_error and result.text:
            path = _save_output(f"briefing-{today}.md", result.text)
            result.output_files = [str(path.relative_to(Path(__file__).parent.parent))]

        return result
