import sqlite3
from datetime import datetime, date


def init_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp            TEXT    NOT NULL,
            asset_name           TEXT    NOT NULL,
            isin                 TEXT    NOT NULL,
            action               TEXT    NOT NULL,
            price                REAL    NOT NULL,
            quantity             REAL    NOT NULL,
            value_eur            REAL    NOT NULL,
            reason               TEXT    NOT NULL,
            portfolio_value_after REAL
        )
    """)
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
) -> None:
    conn.execute(
        """INSERT INTO trades
           (timestamp, asset_name, isin, action, price, quantity, value_eur, reason, portfolio_value_after)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (
            datetime.utcnow().isoformat(),
            asset_name, isin, action,
            price, quantity, value_eur,
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


def get_open_positions(conn: sqlite3.Connection) -> list[dict]:
    """Alle Positionen mit positivem Netto-Bestand (mehr Käufe als Verkäufe)."""
    rows = conn.execute("""
        SELECT
            isin,
            asset_name,
            SUM(CASE WHEN action='BUY' THEN quantity ELSE -quantity END) AS net_qty,
            SUM(CASE WHEN action='BUY' THEN price * quantity ELSE 0 END) /
                NULLIF(SUM(CASE WHEN action='BUY' THEN quantity ELSE 0 END), 0) AS avg_entry
        FROM trades
        GROUP BY isin
        HAVING net_qty > 0.000001
    """).fetchall()
    return [
        {
            "isin":            r[0],
            "asset_name":      r[1],
            "quantity":        r[2],
            "avg_entry_price": r[3],
        }
        for r in rows
    ]


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


def get_entry_price(conn: sqlite3.Connection, isin: str) -> float | None:
    """Durchschnittlicher Kaufpreis für eine offene Position."""
    row = conn.execute("""
        SELECT
            SUM(price * quantity) / NULLIF(SUM(quantity), 0)
        FROM trades
        WHERE isin=? AND action='BUY'
    """, (isin,)).fetchone()
    return float(row[0]) if row and row[0] is not None else None
