from .briefing import BriefingAgent
from .social import SocialAgent
from .orders import OrdersAgent
from .personal import PersonalAgent

REGISTRY: dict = {
    "briefing": BriefingAgent,
    "social": SocialAgent,
    "orders": OrdersAgent,
    "personal": PersonalAgent,
}

__all__ = ["BriefingAgent", "SocialAgent", "OrdersAgent", "PersonalAgent", "REGISTRY"]
