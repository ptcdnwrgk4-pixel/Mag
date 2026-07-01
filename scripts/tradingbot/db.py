import sqlite3
from datetime import datetime, date


def init_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp               TEXT    NOT NULL,
            asset_name              TEXT    NOT NULL,
            isin                    TEXT    NOT NULL,
            underlying_isin         TEXT,
            direction               TEXT    DEFAULT 'LONG',
            action                  TEXT    NOT NULL,
            price                   REAL    NOT NULL,
            underlying_price        REAL,
            quantity                REAL    NOT NULL,
            value_eur               REAL    NOT NULL,
            reason                  TEXT    NOT NULL,
            portfolio_value_after   REAL
        )
    """)
    # Migration für bestehende DBs: fehlende Spalten nachrüsten
    existing = {r[1] for r in conn.execute("PRAGMA table_info(trades)").fetchall()}
    for col, defn in [
        ("underlying_isin",    "TEXT"),
        ("direction",          "TEXT DEFAULT 'LONG'"),
        ("underlying_price",   "REAL"),
    ]:
        if col not in existing:
            conn.execute(f"ALTER TABLE trades ADD COLUMN {col} {defn}")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT    NOT NULL,
            asset_name  TEXT    NOT NULL,
            isin        TEXT    NOT NULL,
            rsi         REAL,
            price       REAL,
            bb_lower    REAL,
            bb_upper    REAL,
            ma200       REAL,
            signal_type TEXT    NOT NULL,
            executed    INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    return conn


def log_trade(
    conn: sqlite3.Connection,
    asset_name: str,
    isin: str,
    action: str,
    price: float,
    quantity: float,
    value_eur: float,
    reason: str,
    portfolio_value_after: float = None,
    underlying_isin: str = None,
    direction: str = "LONG",
    underlying_price: float = None,
) -> None:
    conn.execute(
        """INSERT INTO trades
           (timestamp, asset_name, isin, underlying_isin, direction, action,
            price, underlying_price, quantity, value_eur, reason, portfolio_value_after)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            datetime.utcnow().isoformat(),
            asset_name, isin,
            underlying_isin or isin,
            direction,
            action,
            price, underlying_price,
            quantity, value_eur,
            reason, portfolio_value_after,
        ),
    )
    conn.commit()


def log_signal(
    conn: sqlite3.Connection,
    asset_name: str,
    isin: str,
    rsi: float,
    price: float,
    bb_lower: float,
    bb_upper: float,
    ma200: float,
    signal_type: str,
    executed: bool = False,
) -> None:
    conn.execute(
        """INSERT INTO signals
           (timestamp, asset_name, isin, rsi, price, bb_lower, bb_upper, ma200, signal_type, executed)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (
            datetime.utcnow().isoformat(),
            asset_name, isin,
            rsi, price, bb_lower, bb_upper, ma200,
            signal_type, 1 if executed else 0,
        ),
    )
    conn.commit()


def _open_by_direction(conn: sqlite3.Connection, direction_filter: str) -> list[dict]:
    """Interne Funktion: offene Positionen einer bestimmten Richtung."""
    rows = conn.execute("""
        SELECT
            isin,
            underlying_isin,
            asset_name,
            direction,
            SUM(CASE WHEN action='BUY' THEN quantity ELSE -quantity END)           AS net_qty,
            SUM(CASE WHEN action='BUY' THEN price * quantity ELSE 0 END) /
                NULLIF(SUM(CASE WHEN action='BUY' THEN quantity ELSE 0 END), 0)    AS avg_entry,
            AVG(CASE WHEN action='BUY' THEN underlying_price END)                  AS avg_underlying_entry
        FROM trades
        WHERE (direction = ? OR (direction IS NULL AND ? = 'LONG'))
        GROUP BY isin
        HAVING net_qty > 0.000001
    """, (direction_filter, direction_filter)).fetchall()
    return [
        {
            "isin":                    r[0],
            "underlying_isin":         r[1] or r[0],
            "asset_name":              r[2],
            "direction":               r[3] or "LONG",
            "quantity":                r[4],
            "avg_entry_price":         r[5],
            "avg_underlying_entry":    r[6],
        }
        for r in rows
    ]


def get_open_longs(conn: sqlite3.Connection) -> list[dict]:
    return _open_by_direction(conn, "LONG")


def get_open_shorts(conn: sqlite3.Connection) -> list[dict]:
    return _open_by_direction(conn, "SHORT")


def get_open_positions(conn: sqlite3.Connection) -> list[dict]:
    """Alle offenen Positionen (Long + Short)."""
    return get_open_longs(conn) + get_open_shorts(conn)


def has_open_long(conn: sqlite3.Connection, underlying_isin: str) -> bool:
    longs = get_open_longs(conn)
    return any(p["underlying_isin"] == underlying_isin for p in longs)


def has_open_short(conn: sqlite3.Connection, underlying_isin: str) -> bool:
    shorts = get_open_shorts(conn)
    return any(p["underlying_isin"] == underlying_isin for p in shorts)


def get_todays_pnl(conn: sqlite3.Connection) -> float:
    """Heutiger realisierter P&L in EUR (Verkäufe minus Käufe)."""
    today = date.today().isoformat()
    rows = conn.execute(
        "SELECT action, value_eur FROM trades WHERE timestamp LIKE ?",
        (f"{today}%",),
    ).fetchall()
    pnl = 0.0
    for action, value in rows:
        pnl += value if action == "SELL" else -value
    return pnl
