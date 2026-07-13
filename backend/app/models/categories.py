"""Support ticket category definitions."""

from enum import Enum


class TicketCategory(str, Enum):
    """Allowed support ticket categories."""

    LOGIN_ISSUE = "Login Issue"
    PAYMENT = "Payment"
    ACCOUNT = "Account"
    DELIVERY = "Delivery"
    TECHNICAL_ISSUE = "Technical Issue"
    OTHERS = "Others"

    @classmethod
    def values(cls) -> list[str]:
        """Return all category values as strings."""
        return [member.value for member in cls]

    @classmethod
    def is_valid(cls, category: str) -> bool:
        """Check whether a category string is valid."""
        return category in cls.values()
