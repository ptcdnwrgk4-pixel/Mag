#!/usr/bin/env python3
"""Friday Telegram Bot — aiogram + Anthropic SDK, kein Node.js nötig.

Start:  python telegram_bot.py
        bash start_telegram.sh
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

WORKSPACE = Path(__file__).resolve().parent
load_dotenv(WORKSPACE / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-20s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("friday.telegram")

for _lib in ("aiogram", "httpx", "httpcore", "anthropic"):
    logging.getLogger(_lib).setLevel(logging.WARNING)


# ── Kontext laden ─────────────────────────────────────────────────────────────

_CONTEXT_FILES = [
    "strategy.md",
    "business-info.md",
    "current-data.md",
    "aufgaben.md",
    "personal-info.md",
]


def _load_context() -> str:
    parts = []
    for name in _CONTEXT_FILES:
        path = WORKSPACE / "context" / name
        if path.exists():
            content = path.read_text(encoding="utf-8").strip()
            if content:
                parts.append(f"## {name}\n{content}")
    return "\n\n---\n\n".join(parts) if parts else ""


def _build_system() -> str:
    context = _load_context()
    system = (
        "Du bist Friday — die persönliche KI-Assistentin von Max.\n"
        "Iron Man's Friday: analytisch scharf, direkt, trocken witzig, einen Schritt voraus.\n"
        "Du redest Max mit Namen an. Liefere Ergebnisse, keine Optionen.\n\n"
    )
    if context:
        system += f"## Business-Kontext\n\n{context}\n\n"
    system += (
        "## Telegram-Regeln\n"
        "- Anworte auf Deutsch, kurz und präzise — der User ist am Handy\n"
        "- Nutze Markdown für Formatierung (fett, Aufzählungen)\n"
        "- Keine langen Einleitungen, direkt zum Punkt\n"
    )
    return system


# ── Conversation History ──────────────────────────────────────────────────────

_history: list[dict] = []
_MAX_TURNS = 20


def _add(role: str, content: str) -> None:
    _history.append({"role": role, "content": content})
    # Älteste Nachrichten verwerfen wenn zu lang
    while len(_history) > _MAX_TURNS * 2:
        _history.pop(0)


def _reset() -> None:
    _history.clear()


# ── Anthropic Chat ────────────────────────────────────────────────────────────

async def _chat(user_text: str) -> str:
    import anthropic

    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        return "ANTHROPIC_API_KEY fehlt in .env — check mal die Konfiguration, Max."

    _add("user", user_text)

    client = anthropic.Anthropic(api_key=api_key)
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=_build_system(),
            messages=list(_history),
        )
        reply = response.content[0].text if response.content else "(keine Antwort)"
        _add("assistant", reply)
        return reply
    except Exception as exc:
        logger.exception("Anthropic API Fehler")
        # Fehlgeschlagene User-Nachricht wieder raus
        if _history and _history[-1]["role"] == "user":
            _history.pop()
        return f"API-Fehler: {exc}"


# ── Agenten-Befehle ───────────────────────────────────────────────────────────

async def _run_agent(agent_name: str, task: str | None = None) -> str:
    if str(WORKSPACE) not in sys.path:
        sys.path.insert(0, str(WORKSPACE))

    from agents import REGISTRY

    if agent_name not in REGISTRY:
        return f"Unbekannter Agent: {agent_name}"

    agent = REGISTRY[agent_name]()
    loop = asyncio.get_event_loop()

    try:
        if task:
            result = await loop.run_in_executor(None, lambda: agent.run(task))
        else:
            result = await loop.run_in_executor(None, agent.run_scheduled_task)
        return result.text
    except Exception as exc:
        logger.exception("Agent %s fehlgeschlagen", agent_name)
        return f"Fehler bei {agent_name}: {exc}"


def _trim(text: str, limit: int = 4000) -> str:
    if len(text) > limit:
        return text[:limit - 20] + "\n\n_(gekürzt)_"
    return text


# ── Bot aufbauen ──────────────────────────────────────────────────────────────

def _build_bot():
    from aiogram import Bot, Dispatcher, Router
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode
    from aiogram.filters import Command
    from aiogram.types import Message

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN fehlt in .env")

    group_id_str = os.getenv("TELEGRAM_GROUP_ID", "").strip()
    if not group_id_str:
        raise ValueError("TELEGRAM_GROUP_ID fehlt in .env")
    group_id = int(group_id_str)

    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )
    dp = Dispatcher()
    router = Router()

    # Owner-Lock: erste echte Person wird Owner
    _owner: list[int | None] = [None]

    def _ok(msg: Message) -> bool:
        if not msg.from_user or msg.from_user.is_bot:
            return False
        if msg.chat.id != group_id:
            return False
        if _owner[0] is None:
            _owner[0] = msg.from_user.id
            logger.info("Owner gesetzt: %s (id=%d)", msg.from_user.full_name, _owner[0])
            return True
        return msg.from_user.id == _owner[0]

    # ── Befehle ───────────────────────────────────────────────────────────────

    @router.message(Command("start", "help"))
    async def cmd_help(msg: Message) -> None:
        if not _ok(msg):
            return
        await msg.reply(
            "*Friday — dein Mitarbeiter*\n\n"
            "Schreib mir direkt — ich antworte als Friday.\n\n"
            "*Schnell-Befehle:*\n"
            "/briefing — Tages-Briefing\n"
            "/social — Social-Wochen-Plan\n"
            "/orders — Bestellliste\n"
            "/personal — Dienstplan\n"
            "/status — System-Status\n"
            "/reset — Gespräch zurücksetzen\n"
            "/help — Diese Übersicht"
        )

    @router.message(Command("reset"))
    async def cmd_reset(msg: Message) -> None:
        if not _ok(msg):
            return
        _reset()
        await msg.reply("Gespräch zurückgesetzt. Frischer Start, Max.")

    @router.message(Command("status"))
    async def cmd_status(msg: Message) -> None:
        if not _ok(msg):
            return
        try:
            from memory.store import MemoryStore
            mem = MemoryStore()
            statuses = mem.get_all_status()
            if statuses:
                lines = ["*System-Status*\n"]
                for s in statuses:
                    last = s["last_run"][:16] if s.get("last_run") else "—"
                    lines.append(
                        f"• {s['agent']:10} letzter Run: {last} | "
                        f"{s['runs_total']} Runs | ${s['cost_total']:.4f}"
                    )
                await msg.reply("\n".join(lines))
            else:
                await msg.reply("Noch keine Agent-Runs aufgezeichnet.")
        except Exception as exc:
            await msg.reply(f"Status-Fehler: {exc}")

    @router.message(Command("briefing"))
    async def cmd_briefing(msg: Message) -> None:
        if not _ok(msg):
            return
        await msg.reply("Starte Tages-Briefing...")
        result = await _run_agent("briefing")
        await msg.reply(_trim(result))

    @router.message(Command("social"))
    async def cmd_social(msg: Message) -> None:
        if not _ok(msg):
            return
        text = msg.text or ""
        parts = text.split(None, 1)
        task = parts[1] if len(parts) > 1 else None
        await msg.reply("Starte Social-Plan...")
        result = await _run_agent("social", task)
        await msg.reply(_trim(result))

    @router.message(Command("orders"))
    async def cmd_orders(msg: Message) -> None:
        if not _ok(msg):
            return
        text = msg.text or ""
        parts = text.split(None, 1)
        task = parts[1] if len(parts) > 1 else None
        await msg.reply("Erstelle Bestellliste...")
        result = await _run_agent("orders", task)
        await msg.reply(_trim(result))

    @router.message(Command("personal"))
    async def cmd_personal(msg: Message) -> None:
        if not _ok(msg):
            return
        await msg.reply("Erstelle Dienstplan...")
        result = await _run_agent("personal")
        await msg.reply(_trim(result))

    @router.message()
    async def handle_text(msg: Message) -> None:
        if not _ok(msg):
            return
        if not msg.text:
            return

        try:
            await bot.send_chat_action(chat_id=msg.chat.id, action="typing")
        except Exception:
            pass

        reply = await _chat(msg.text)
        await msg.reply(_trim(reply))

    dp.include_router(router)

    # ── Startup ───────────────────────────────────────────────────────────────

    @dp.startup()
    async def on_startup() -> None:
        logger.info("Bot online")

        # Scheduler starten (sendet geplante Runs an Telegram)
        try:
            from scheduler.runner import FridayScheduler

            async def _send(text: str) -> None:
                try:
                    await bot.send_message(chat_id=group_id, text=_trim(text))
                except Exception as exc:
                    logger.warning("Scheduler-Nachricht fehlgeschlagen: %s", exc)

            sched = FridayScheduler(send_fn=_send)
            sched.start()
            logger.info("Scheduler gestartet")
            for job in sched.next_runs():
                logger.info("  %-22s nächster Run: %s", job["name"], job["next_run"] or "—")
        except Exception as exc:
            logger.warning("Scheduler konnte nicht gestartet werden: %s", exc)

        # Startup-Meldung
        try:
            await bot.send_message(chat_id=group_id, text="Dein Mitarbeiter ist online.")
        except Exception:
            logger.warning("Startup-Meldung konnte nicht gesendet werden")

    return bot, dp


# ── Main ──────────────────────────────────────────────────────────────────────

async def main() -> None:
    bot, dp = _build_bot()

    # Stale Polling-Lock leeren
    try:
        await bot.delete_webhook(drop_pending_updates=False)
    except Exception:
        pass

    logger.info("Polling läuft...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
