#!/usr/bin/env python3
"""Friday CLI — Agentic OS für das Padella Vino.

Usage:
    python friday.py briefing               # Tages-Briefing
    python friday.py social                 # Social-Post (heute)
    python friday.py social "Post über..."  # Custom-Post
    python friday.py orders                 # Bestellliste
    python friday.py personal               # Dienstplan
    python friday.py scheduler              # Scheduler starten (Daemon)
    python friday.py memory [agent]         # Letzten Runs anzeigen
    python friday.py status                 # System-Status
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-20s | %(message)s",
    datefmt="%H:%M:%S",
)


# ── CLI Helpers ──────────────────────────────────────────────────────────────

def _header(text: str) -> None:
    print(f"\n{'─'*60}")
    print(f"  {text}")
    print(f"{'─'*60}")


def _footer(result) -> None:
    print(f"\n{'─'*60}")
    elapsed = result.duration_ms / 1000 if result.duration_ms else 0
    print(f"  ${result.cost_usd:.4f} | {result.num_turns} turns | {elapsed:.1f}s")
    if result.output_files:
        print(f"  Output: {', '.join(result.output_files)}")
    print(f"{'─'*60}\n")


# ── Commands ─────────────────────────────────────────────────────────────────

async def cmd_agent(name: str, task: str | None = None) -> None:
    from agents import REGISTRY
    from memory.store import MemoryStore

    if name not in REGISTRY:
        print(f"Unbekannter Agent: {name}")
        print(f"Verfügbar: {', '.join(REGISTRY.keys())}")
        sys.exit(1)

    agent = REGISTRY[name]()
    _header(f"Friday › {name.upper()}" + (f" — {task[:50]}" if task else " (geplante Aufgabe)"))

    result = await agent.run(task) if task else await agent.run_scheduled_task()

    print(result.text)
    _footer(result)

    MemoryStore().record_run(
        agent=name,
        task=task or "scheduled",
        result=result.text,
        cost_usd=result.cost_usd,
        num_turns=result.num_turns,
        is_error=result.is_error,
    )


def cmd_memory(agent_filter: str | None = None) -> None:
    from memory.store import MemoryStore

    mem = MemoryStore()
    runs = mem.get_recent_runs(agent_filter, limit=20)

    if not runs:
        print("Keine Einträge gefunden.")
        return

    _header(f"Memory — {'alle Agenten' if not agent_filter else agent_filter}")
    for r in runs:
        ts = r["created_at"][:16]
        ok = "✓" if not r.get("is_error") else "✗"
        snippet = (r["result"] or "")[:120].replace("\n", " ")
        print(f"  {ts}  [{r['agent']:10}] {ok} ${r['cost_usd']:.4f} — {snippet}")


def cmd_status() -> None:
    from memory.store import MemoryStore

    mem = MemoryStore()
    statuses = mem.get_all_status()
    facts = mem.all_facts()

    _header("Friday Agentic OS — System-Status")

    if statuses:
        print("\n  AGENTEN:\n")
        for s in statuses:
            last = s["last_run"][:16] if s.get("last_run") else "—"
            nxt  = s["next_run"][:16] if s.get("next_run") else "—"
            print(f"    {s['agent']:12} | letzter Run: {last} | nächster: {nxt} | Runs: {s['runs_total']} | ${s['cost_total']:.4f}")
    else:
        print("\n  Noch keine Agent-Runs aufgezeichnet.")

    if facts:
        print("\n  FACTS:\n")
        for k, v in list(facts.items())[:10]:
            print(f"    {k}: {v[:80]}")

    print()


def cmd_scheduler() -> None:
    from scheduler.runner import FridayScheduler

    _header("Friday Scheduler — startet autonome Jobs")

    sched = FridayScheduler()
    sched.start()

    for job in sched.next_runs():
        print(f"  {job['name']:20} — nächster Run: {job['next_run'] or '—'}")
    print()

    try:
        while True:
            import time
            time.sleep(60)
    except KeyboardInterrupt:
        sched.stop()
        print("\nScheduler gestoppt.")


# ── Entrypoint ────────────────────────────────────────────────────────────────

def main() -> None:
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        return

    cmd = args[0]
    rest = args[1:]

    if cmd == "scheduler":
        cmd_scheduler()

    elif cmd == "memory":
        cmd_memory(rest[0] if rest else None)

    elif cmd == "status":
        cmd_status()

    elif cmd in ("briefing", "social", "orders", "personal"):
        task = " ".join(rest) if rest else None
        asyncio.run(cmd_agent(cmd, task))

    else:
        print(f"Unbekannter Befehl: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
