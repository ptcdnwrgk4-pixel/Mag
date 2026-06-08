"""Persistentes Gedächtnis für Friday — SQLite-basiert."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

_DEFAULT_DB = Path(__file__).resolve().parent / "friday.db"


class MemoryStore:
    def __init__(self, db_path: Path | str | None = None):
        self.db_path = Path(db_path) if db_path else _DEFAULT_DB
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self) -> None:
        with self._connect() as c:
            c.executescript("""
                CREATE TABLE IF NOT EXISTS runs (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent       TEXT    NOT NULL,
                    task        TEXT,
                    result      TEXT,
                    cost_usd    REAL    DEFAULT 0,
                    num_turns   INTEGER DEFAULT 0,
                    is_error    INTEGER DEFAULT 0,
                    created_at  TEXT    NOT NULL
                );
                CREATE TABLE IF NOT EXISTS facts (
                    key         TEXT PRIMARY KEY,
                    value       TEXT,
                    agent       TEXT    DEFAULT 'system',
                    updated_at  TEXT    NOT NULL
                );
                CREATE TABLE IF NOT EXISTS status (
                    agent       TEXT PRIMARY KEY,
                    last_run    TEXT,
                    last_result TEXT,
                    next_run    TEXT,
                    cost_total  REAL    DEFAULT 0,
                    runs_total  INTEGER DEFAULT 0,
                    updated_at  TEXT    NOT NULL
                );
            """)

    # ── Runs ──────────────────────────────────────────────────────────────

    def record_run(
        self,
        agent: str,
        task: str,
        result: str,
        cost_usd: float = 0.0,
        num_turns: int = 0,
        is_error: bool = False,
    ) -> None:
        now = datetime.now().isoformat()
        with self._connect() as c:
            c.execute(
                "INSERT INTO runs (agent,task,result,cost_usd,num_turns,is_error,created_at)"
                " VALUES (?,?,?,?,?,?,?)",
                (agent, task, result, cost_usd, num_turns, int(is_error), now),
            )
            # Update rolling status
            c.execute(
                """
                INSERT INTO status (agent,last_run,last_result,cost_total,runs_total,updated_at)
                     VALUES (?,?,?,?,1,?)
                ON CONFLICT(agent) DO UPDATE SET
                    last_run    = excluded.last_run,
                    last_result = excluded.last_result,
                    cost_total  = cost_total + excluded.cost_total,
                    runs_total  = runs_total + 1,
                    updated_at  = excluded.updated_at
                """,
                (agent, now, (result or "")[:500], cost_usd, now),
            )

    def get_recent_runs(self, agent: str | None = None, limit: int = 20) -> list[dict]:
        with self._connect() as c:
            if agent:
                cur = c.execute(
                    "SELECT * FROM runs WHERE agent=? ORDER BY created_at DESC LIMIT ?",
                    (agent, limit),
                )
            else:
                cur = c.execute(
                    "SELECT * FROM runs ORDER BY created_at DESC LIMIT ?", (limit,)
                )
            return [dict(row) for row in cur.fetchall()]

    def last_run(self, agent: str) -> dict | None:
        rows = self.get_recent_runs(agent, limit=1)
        return rows[0] if rows else None

    # ── Facts ─────────────────────────────────────────────────────────────

    def save_fact(self, key: str, value: str, agent: str = "system") -> None:
        with self._connect() as c:
            c.execute(
                "INSERT OR REPLACE INTO facts (key,value,agent,updated_at) VALUES (?,?,?,?)",
                (key, value, agent, datetime.now().isoformat()),
            )

    def get_fact(self, key: str) -> str | None:
        with self._connect() as c:
            row = c.execute("SELECT value FROM facts WHERE key=?", (key,)).fetchone()
            return row["value"] if row else None

    def all_facts(self) -> dict[str, str]:
        with self._connect() as c:
            rows = c.execute("SELECT key, value FROM facts").fetchall()
            return {r["key"]: r["value"] for r in rows}

    # ── Status ────────────────────────────────────────────────────────────

    def set_next_run(self, agent: str, next_run: str) -> None:
        with self._connect() as c:
            c.execute(
                """
                INSERT INTO status (agent,next_run,updated_at)
                     VALUES (?,?,?)
                ON CONFLICT(agent) DO UPDATE SET
                    next_run   = excluded.next_run,
                    updated_at = excluded.updated_at
                """,
                (agent, next_run, datetime.now().isoformat()),
            )

    def get_all_status(self) -> list[dict]:
        with self._connect() as c:
            rows = c.execute("SELECT * FROM status ORDER BY agent").fetchall()
            return [dict(r) for r in rows]

    # ── Export für Web-Interface ──────────────────────────────────────────

    def export_status_json(self, path: Path | str) -> None:
        """Schreibt Status als JSON für das Web-Interface."""
        data = {
            "updated": datetime.now().isoformat(),
            "agents": self.get_all_status(),
            "recent_runs": self.get_recent_runs(limit=10),
            "facts": self.all_facts(),
        }
        Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
