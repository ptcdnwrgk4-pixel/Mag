"""Basis-Klasse für alle Friday Specialist Agents.

Verwendet die Anthropic Python SDK direkt — kein Node.js oder Claude CLI nötig.
Kontext-Dateien werden vor jedem Run geladen und in den System-Prompt eingebettet.
"""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

from anthropic import Anthropic

logger = logging.getLogger(__name__)

WORKSPACE = Path(__file__).resolve().parent.parent
CONTEXT_FILES = [
    "strategy.md",
    "business-info.md",
    "current-data.md",
    "aufgaben.md",
    "personal-info.md",
]


@dataclass
class AgentResult:
    text: str
    cost_usd: float = 0.0
    num_turns: int = 1
    is_error: bool = False
    output_files: list[str] = field(default_factory=list)
    duration_ms: int = 0


def _load_context() -> str:
    """Lädt alle verfügbaren context/-Dateien."""
    parts = []
    for name in CONTEXT_FILES:
        path = WORKSPACE / "context" / name
        if path.exists():
            content = path.read_text(encoding="utf-8").strip()
            if content:
                parts.append(f"## {name}\n{content}")
    return "\n\n---\n\n".join(parts) if parts else ""


def _save_output(filename: str, content: str) -> Path:
    """Speichert Ergebnis in outputs/."""
    out_dir = WORKSPACE / "outputs"
    out_dir.mkdir(exist_ok=True)
    path = out_dir / filename
    path.write_text(content, encoding="utf-8")
    return path


class SpecialistAgent:
    """Basis für alle Friday Specialist Agents.

    Jeder Agent:
    - Lädt beim Start die context/-Dateien
    - Schickt Task + Kontext an Claude (Anthropic API)
    - Speichert Ergebnis in outputs/
    - Gibt AgentResult zurück
    """

    name: str = "base"
    description: str = "Basis-Agent"
    model: str = "claude-sonnet-4-6"
    max_tokens: int = 4096

    system_append: str = ""

    def _get_client(self) -> Anthropic:
        api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY fehlt in .env — "
                "Key holen unter: console.anthropic.com"
            )
        return Anthropic(api_key=api_key)

    def _build_system(self) -> str:
        base = (
            "Du bist Friday — die persönliche KI-Assistentin von Max.\n"
            "Max ist Inhaber eines Café-Bars am Marktplatz (Padella Vino).\n"
            "Sei direkt, analytisch, präzise. Keine Weichspüler-Antworten.\n\n"
        )
        context = _load_context()
        if context:
            base += f"## Business-Kontext\n\n{context}\n\n"
        if self.system_append:
            base += self.system_append
        return base

    def run(self, task: str) -> AgentResult:
        import time
        start = time.time()

        logger.info("[%s] Starte: %s", self.name, task[:80])

        try:
            client = self._get_client()
            response = client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=self._build_system(),
                messages=[{"role": "user", "content": task}],
            )
        except Exception as exc:
            logger.exception("[%s] API-Fehler", self.name)
            return AgentResult(text=f"Fehler: {exc}", is_error=True)

        text = response.content[0].text if response.content else ""
        duration_ms = int((time.time() - start) * 1000)

        # Kosten schätzen (Sonnet: $3/$15 per MTok input/output)
        input_tokens = response.usage.input_tokens if response.usage else 0
        output_tokens = response.usage.output_tokens if response.usage else 0
        cost = (input_tokens * 3 + output_tokens * 15) / 1_000_000

        logger.info(
            "[%s] Fertig: %d Tokens, $%.4f, %dms",
            self.name, input_tokens + output_tokens, cost, duration_ms,
        )

        return AgentResult(
            text=text,
            cost_usd=cost,
            duration_ms=duration_ms,
            is_error=False,
        )

    def run_scheduled_task(self) -> AgentResult:
        raise NotImplementedError(f"{self.name} hat keine Scheduled-Aufgabe")
