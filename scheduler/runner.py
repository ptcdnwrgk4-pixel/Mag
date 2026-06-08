"""Friday Scheduler — autonome Aufgaben auf Zeitplan."""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Callable

logger = logging.getLogger("friday.scheduler")

WORKSPACE = Path(__file__).resolve().parent.parent


class FridayScheduler:
    """Führt Agenten-Aufgaben automatisch nach Zeitplan aus.

    Jobs:
    - Tages-Briefing:     Mo–Sa 08:30
    - Social-Wochen-Plan: Mo    09:00
    - Dienstplan:         Fr    16:00 (für nächste Woche)
    """

    def __init__(self, send_fn: Callable | None = None):
        """
        Args:
            send_fn: Optionale async-Funktion zum Versenden der Ergebnisse
                     (z.B. Telegram-Nachricht). Signatur: async def send(text: str)
        """
        from apscheduler.schedulers.asyncio import AsyncIOScheduler

        self.scheduler = AsyncIOScheduler(timezone="Europe/Berlin")
        self.send_fn = send_fn
        self._setup_jobs()

    def _setup_jobs(self) -> None:
        from apscheduler.triggers.cron import CronTrigger

        # Tages-Briefing Mo–Sa um 10:00
        self.scheduler.add_job(
            self._job_briefing,
            CronTrigger(day_of_week="mon-sat", hour=10, minute=0),
            id="daily_briefing",
            name="Tages-Briefing",
            replace_existing=True,
        )

        # Social-Media-Plan: jeden Montag 11:00
        self.scheduler.add_job(
            self._job_social,
            CronTrigger(day_of_week="mon", hour=11, minute=0),
            id="weekly_social",
            name="Social-Wochen-Plan",
            replace_existing=True,
        )

        # Dienstplan: jeden 18. im Monat um 10:00
        self.scheduler.add_job(
            self._job_personal,
            CronTrigger(day=18, hour=10, minute=0),
            id="monthly_personal",
            name="Dienstplan",
            replace_existing=True,
        )

    # ── Jobs ──────────────────────────────────────────────────────────────

    async def _job_briefing(self) -> None:
        from agents.briefing import BriefingAgent
        await self._run("briefing", BriefingAgent(), "Tages-Briefing")

    async def _job_social(self) -> None:
        from agents.social import SocialAgent
        await self._run("social", SocialAgent(), "Social-Wochen-Plan")

    async def _job_personal(self) -> None:
        from agents.personal import PersonalAgent
        await self._run("personal", PersonalAgent(), "Dienstplan")

    async def _run(self, agent_name: str, agent, job_name: str) -> None:
        from memory.store import MemoryStore

        mem = MemoryStore()
        logger.info("Starte Job: %s", job_name)

        try:
            result = await agent.run_scheduled_task()

            mem.record_run(
                agent=agent_name,
                task=f"scheduled:{job_name}",
                result=result.text,
                cost_usd=result.cost_usd,
                num_turns=result.num_turns,
                is_error=result.is_error,
            )
            self._update_status_json()

            if self.send_fn and result.text and not result.is_error:
                summary = result.text[:2000]
                await self.send_fn(f"**{job_name}**\n\n{summary}")

            logger.info(
                "Job abgeschlossen: %s | $%.4f | %d turns",
                job_name, result.cost_usd, result.num_turns,
            )

        except Exception:
            logger.exception("Job fehlgeschlagen: %s", job_name)

    # ── Status ────────────────────────────────────────────────────────────

    def _update_status_json(self) -> None:
        try:
            from memory.store import MemoryStore
            mem = MemoryStore()
            out = WORKSPACE / "memory" / "status.json"
            mem.export_status_json(out)
        except Exception as exc:
            logger.warning("Status-Export fehlgeschlagen: %s", exc)

    def next_runs(self) -> list[dict]:
        jobs = []
        for job in self.scheduler.get_jobs():
            next_fire = job.next_run_time
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": next_fire.isoformat() if next_fire else None,
            })
        return jobs

    # ── Lifecycle ─────────────────────────────────────────────────────────

    def start(self) -> None:
        self.scheduler.start()
        logger.info("Scheduler gestartet. Jobs: %s", [j.name for j in self.scheduler.get_jobs()])

    def stop(self) -> None:
        self.scheduler.shutdown(wait=False)
        logger.info("Scheduler gestoppt.")
