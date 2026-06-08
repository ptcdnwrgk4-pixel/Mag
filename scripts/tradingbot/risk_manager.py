import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import sqlite3


def can_trade_today(conn: "sqlite3.Connection", portfolio_value: float, config) -> bool:
    """True wenn der Tagesverlust das Limit noch nicht erreicht hat."""
    from db import get_todays_pnl
    if portfolio_value <= 0:
        return False
    pnl = get_todays_pnl(conn)
    loss_pct = abs(min(pnl, 0.0)) / portfolio_value
    return loss_pct < config.MAX_DAILY_LOSS_PCT


def can_open_position(conn: "sqlite3.Connection", config) -> bool:
    """True wenn noch Platz für eine weitere Position ist."""
    from db import get_open_positions
    return len(get_open_positions(conn)) < config.MAX_OPEN_POSITIONS


def has_open_position(conn: "sqlite3.Connection", isin: str) -> bool:
    """True wenn für dieses Asset bereits eine offene Position existiert."""
    from db import get_open_positions
    return any(p["isin"] == isin for p in get_open_positions(conn))


def calculate_position_size(portfolio_value: float, price: float, config) -> float:
    """
    Berechnet die Kaufmenge basierend auf MAX_POSITION_PCT.
    Wenn ganze Stücke >= 1 möglich: ganze Stücke (Aktien).
    Sonst: Bruchteile (Krypto / teure Assets wie BTC).
    """
    if price <= 0 or portfolio_value <= 0:
        return 0.0
    max_value = portfolio_value * config.MAX_POSITION_PCT
    quantity  = max_value / price
    floored   = math.floor(quantity)
    return float(floored) if floored >= 1 else round(quantity, 6)


def should_stop_loss(entry_price: float, current_price: float, config) -> bool:
    """True wenn der Verlust >= STOP_LOSS_PCT."""
    if entry_price <= 0:
        return False
    loss_pct = (entry_price - current_price) / entry_price
    return loss_pct >= config.STOP_LOSS_PCT


def should_take_profit(entry_price: float, current_price: float, config) -> bool:
    """True wenn der Gewinn >= TAKE_PROFIT_PCT."""
    if entry_price <= 0:
        return False
    gain_pct = (current_price - entry_price) / entry_price
    return gain_pct >= config.TAKE_PROFIT_PCT
