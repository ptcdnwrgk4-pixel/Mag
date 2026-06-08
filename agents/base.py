"""Basis-Klasse für alle Friday Specialist Agents."""

import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

WORKSPACE_DIR = str(Path(__file__).resolve().parent.parent)


@dataclass
class AgentResult:
    text: str
    cost_usd: float = 0.0
    duration_ms: int = 0
    num_turns: int = 0
    is_error: bool = False
    output_files: list[str] = field(default_factory=list)


class SpecialistAgent:
    """Basis für alle Friday Specialist Agents.

    Jeder Agent:
    - Läuft als vollständige Claude Code Session (via claude-agent-sdk)
    - Hat Zugriff auf alle Workspace-Dateien und Tools
    - Speichert Ergebnisse in outputs/
    - Protokolliert in memory/friday.db
    """

    name: str = "base"
    description: str = "Basis-Agent"
    model: str = "sonnet"
    max_turns: int = 20
    max_budget_usd: float = 2.00

    system_append: str = """
Du bist Friday — die persönliche KI-Assistentin von Max.
Max ist Inhaber eines Café-Bars am Marktplatz (Padella Vino).
Sei direkt, präzise, analytisch. Keine Weichspüler-Antworten.
Lies immer zuerst die relevanten context/-Dateien, bevor du antwortest.
Speichere Ergebnisse in outputs/ und nenne den Pfad am Ende deiner Antwort.
"""

    def _build_options(self):
        from claude_agent_sdk import ClaudeAgentOptions

        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

        return ClaudeAgentOptions(
            system_prompt={
                "type": "preset",
                "preset": "claude_code",
                "append": self.system_append,
            },
            setting_sources=["project"],
            cwd=WORKSPACE_DIR,
            allowed_tools=[
                "Read", "Write", "Edit", "Bash", "Glob", "Grep",
                "WebSearch", "WebFetch",
            ],
            permission_mode="bypassPermissions",
            max_turns=self.max_turns,
            max_budget_usd=self.max_budget_usd,
            model=self.model,
            env=env,
        )

    async def run(self, task: str) -> AgentResult:
        from claude_agent_sdk import (
            AssistantMessage,
            ResultMessage,
            TextBlock,
            query,
        )

        options = self._build_options()
        latest_text: list[str] = []
        final: ResultMessage | None = None

        logger.info("[%s] Starte: %s", self.name, task[:80])

        try:
            async for msg in query(prompt=task, options=options):
                if isinstance(msg, AssistantMessage):
                    parts = [b.text for b in msg.content if isinstance(b, TextBlock)]
                    if parts:
                        latest_text = parts
                elif isinstance(msg, ResultMessage):
                    final = msg

        except RuntimeError as exc:
            if "cancel scope" in str(exc):
                logger.warning("[%s] anyio cancel scope suppressed", self.name)
            else:
                raise
        except Exception as exc:
            logger.exception("[%s] Fehler", self.name)
            return AgentResult(
                text=f"Fehler im {self.name}-Agenten: {exc}",
                is_error=True,
            )

        text = "\n".join(latest_text)

        if final:
            return AgentResult(
                text=text,
                cost_usd=final.total_cost_usd or 0.0,
                duration_ms=final.duration_ms or 0,
                num_turns=final.num_turns or 0,
                is_error=final.is_error or False,
                output_files=self._find_outputs(text),
            )

        return AgentResult(text=text or "Kein Output.", is_error=not text)

    def _find_outputs(self, text: str) -> list[str]:
        """Findet Output-Datei-Pfade im Ergebnistext."""
        raw = re.findall(r'outputs/[\w\-/]+\.\w{1,10}', text)
        return [p for p in raw if (Path(WORKSPACE_DIR) / p).exists()]

    async def run_scheduled_task(self) -> AgentResult:
        raise NotImplementedError(f"{self.name} hat keine Scheduled-Aufgabe")
