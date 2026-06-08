"""SocialAgent — Social-Media-Posts und Wochenpläne."""

from datetime import date, datetime
from pathlib import Path

from .base import AgentResult, SpecialistAgent, _save_output

_SYSTEM = """
Du bist Friday's Social-Media-Spezialist für das Padella Vino.

Stil:
- Authentisch, nicht werblich
- Kurz und visuell vorstellbar
- Abwechslungsreich in der Struktur
- Auf Deutsch, gelegentlich ital. Einsprengsel okay
- Hashtags: 8-10, themenrelevant, nicht als Spam

Gib immer den fertigen Post-Text zurück, direkt verwendbar.
"""

_POST_TASK = """
Erstelle einen Social-Media-Post für das Padella Vino.

Thema: {thema}
Datum: {datum}
Plattform: Instagram / Facebook

Liefere:
1. Post-Text (max. 150 Wörter)
2. Hashtags (8-10)
3. Optional: Story-Idee
"""

_WEEKLY_TASK = """
Erstelle den Social-Media-Wochen-Plan für KW {kw}.

Plane 3-4 Posts für die Woche:
- Berücksichtige Wochentag-Logik (Mo=Start der Woche, Fr=Wochenende einläuten, So=gemütlich)
- Aktuelle Jahreszeit
- Abwechslung in Themen und Formaten

Format pro Post:
**Tag, Uhrzeit**
Thema: [Thema]
Text: [Fertiger Post-Text]
Hashtags: [Liste]
"""


class SocialAgent(SpecialistAgent):
    name = "social"
    description = "Erstellt Social-Media-Posts und Wochenpläne"
    system_append = _SYSTEM

    def run(self, task: str | None = None) -> AgentResult:
        if task is None:
            today = datetime.now().strftime("%Y-%m-%d")
            task = _POST_TASK.format(thema="Tagesaktuell", datum=today)
        return super().run(task)

    def run_scheduled_task(self) -> AgentResult:
        kw = date.today().isocalendar()[1]
        result = super().run(_WEEKLY_TASK.format(kw=kw))

        if not result.is_error and result.text:
            path = _save_output(f"social-plan-KW{kw}.md", result.text)
            result.output_files = [str(path.relative_to(Path(__file__).parent.parent))]

        return result

    def create_post(self, thema: str) -> AgentResult:
        today = datetime.now().strftime("%Y-%m-%d")
        return super().run(_POST_TASK.format(thema=thema, datum=today))
