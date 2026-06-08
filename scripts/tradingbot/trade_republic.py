"""
Trade Republic Connector – inoffizielle pytr-Bibliothek.

pytr nutzt WebSockets und ist vollständig async. Diese Klasse kapselt die
Verbindung und stellt synchron wirkende Methoden zur Verfügung.

Hinweis: pytr ist eine inoffizielle Drittanbieter-Bibliothek. Trade Republic
kann die Schnittstelle jederzeit ändern. Bei Verbindungsfehlern nach
TR-Updates: github.com/nborrmann/pytr auf neue Releases prüfen.
"""

import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TRClient:
    def __init__(self, phone: str, pin: str):
        self.phone = phone
        self.pin   = pin
        self._api  = None

    async def connect(self) -> None:
        """Verbindet mit Trade Republic. Beim ersten Start: interaktiver SMS-Login."""
        from pytr.api import TradeRepublicApi
        self._api = TradeRepublicApi(
            phone_no=self.phone,
            pin=self.pin,
            locale="de",
        )
        await self._api.login()
        logger.info("Trade Republic: Verbunden")

    async def disconnect(self) -> None:
        if self._api:
            try:
                await self._api.close()
            except Exception:
                pass
            self._api = None

    async def get_portfolio_value(self) -> float:
        """Gesamtwert des Portfolios in EUR."""
        try:
            data = await self._api.portfolio()
            # pytr gibt portfolioValue oder totalValue zurück – beide abfangen
            val = (
                data.get("portfolioValue")
                or data.get("totalValue", {}).get("value")
                or 0
            )
            return float(val)
        except Exception as e:
            logger.error(f"Portfolio-Abruf fehlgeschlagen: {e}")
            return 0.0

    async def get_price(self, isin: str) -> Optional[float]:
        """Aktuellen Marktpreis eines Assets abrufen."""
        try:
            # Ticker-Subscription: erstes Paket enthält den aktuellen Kurs
            async for tick in self._api.ticker(isin, exchange="LSX"):
                price = (
                    tick.get("last", {}).get("price")
                    or tick.get("bid", {}).get("price")
                    or tick.get("ask", {}).get("price")
                )
                if price is not None:
                    return float(price)
                break
        except Exception as e:
            logger.error(f"Preis für {isin} nicht abrufbar: {e}")
        return None

    async def get_position(self, isin: str) -> float:
        """Gehaltene Stückzahl eines Assets im Portfolio."""
        try:
            data = await self._api.portfolio()
            positions = data.get("positions", [])
            for pos in positions:
                if pos.get("instrumentId") == isin or pos.get("isin") == isin:
                    return float(pos.get("netSize", pos.get("quantity", 0)))
        except Exception as e:
            logger.error(f"Position für {isin} nicht abrufbar: {e}")
        return 0.0

    async def buy(self, isin: str, quantity: float) -> Optional[dict]:
        """
        Platziert eine Markt-Kauforder.
        Gibt das Order-Ergebnis-Dict zurück oder None bei Fehler.
        """
        try:
            result = await self._api.place_order(
                isin=isin,
                order_type="market",
                size=quantity,
                direction="buy",
                expiry={"type": "gfd"},  # Good-For-Day
            )
            order_id = result.get("id", "n/a") if result else "n/a"
            logger.info(f"KAUF ausgeführt: {quantity}x {isin} | Order-ID: {order_id}")
            return result
        except Exception as e:
            logger.error(f"Kauf fehlgeschlagen [{isin}]: {e}")
            return None

    async def sell(self, isin: str, quantity: float) -> Optional[dict]:
        """
        Platziert eine Markt-Verkaufsorder.
        Gibt das Order-Ergebnis-Dict zurück oder None bei Fehler.
        """
        try:
            result = await self._api.place_order(
                isin=isin,
                order_type="market",
                size=quantity,
                direction="sell",
                expiry={"type": "gfd"},
            )
            order_id = result.get("id", "n/a") if result else "n/a"
            logger.info(f"VERKAUF ausgeführt: {quantity}x {isin} | Order-ID: {order_id}")
            return result
        except Exception as e:
            logger.error(f"Verkauf fehlgeschlagen [{isin}]: {e}")
            return None
