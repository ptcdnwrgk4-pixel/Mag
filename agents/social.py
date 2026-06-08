"""SocialAgent — Social-Media-Posts und Wochenpläne."""

from datetime import date, datetime

from .base import AgentResult, SpecialistAgent

_SYSTEM = """
Du bist Friday's Social-Media-Spezialist für das Padella Vino Café-Bar am Marktplatz.

Das Business:
- Hochwertige Kaffeespezialitäten, ~17 Sprizz-Varianten, kuratierte ital. Weinkarte
- Kleine Speisen zum Verweilen
- Stimmung: laid-back, authentisch, Süditalien trifft Marktplatz-Flair

Dein Stil:
- Authentisch, nicht werblich
- Kurz und visuell vorstellbar
- Abwechslungsreich — nicht immer dieselbe Struktur
- Hashtags strategisch, nicht als Spam
- Auf Deutsch, gelegentlich ital. Einsprengsel okay

Posts immer in Outputs speichern, Pfad angeben.
"""

_POST_TASK = """
Erstelle einen Social-Media-Post für das Padella Vino.

1. Lies context/business-info.md (Marke, Tonalität, Angebot)
2. Lies context/strategy.md (aktuelle Prioritäten)

Post-Details:
- Thema: {thema}
- Datum: {datum}
- Plattform: Instagram / Facebook

Format:
- Haupttext (max. 150 Wörter)
- Hashtags (8-12, themenrelevant)
- Optional: Story-Idee oder Call-to-Action

Speichere als outputs/social-post-{datum}.md
"""

_WEEKLY_TASK = """
Erstelle den Social-Media-Wochen-Plan für das Padella Vino.

1. Lies context/business-info.md und context/strategy.md
2. Berücksichtige: aktuelle Jahreszeit, Wochentag-Logik (Mo=motivierend, Fr=TGIF, So=gemütlich)
3. Plane 3-4 Posts für KW {kw}

Format pro Post:
- Tag + Uhrzeit
- Thema und Headline
- Post-Text (ready to copy)
- Hashtags
- Story-Idee (optional)

Speichere als outputs/social-plan-KW{kw}.md
"""


class SocialAgent(SpecialistAgent):
    name = "social"
    description = "Erstellt Social-Media-Posts und Wochenpläne"
    model = "sonnet"
    max_turns = 15
    max_budget_usd = 1.50
    system_append = _SYSTEM

    async def run(self, task: str | None = None) -> AgentResult:
        if task is None:
            today = datetime.now().strftime("%Y-%m-%d")
            task = _POST_TASK.format(thema="Tagesaktuell", datum=today)
        return await super().run(task)

    async def run_scheduled_task(self) -> AgentResult:
        kw = date.today().isocalendar()[1]
        return await super().run(_WEEKLY_TASK.format(kw=kw))

    async def create_post(self, thema: str) -> AgentResult:
        today = datetime.now().strftime("%Y-%m-%d")
        return await super().run(_POST_TASK.format(thema=thema, datum=today))
