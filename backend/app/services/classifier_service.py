"""Business logic for support ticket classification."""

import logging

from app.config import Settings
from app.models.categories import TicketCategory
from app.schemas.request_response import ClassifyResponse
from app.services.llm_service import LLMService
from app.utils.exceptions import LLMResponseError
from app.utils.json_parser import parse_classification_response

logger = logging.getLogger(__name__)


class ClassifierService:
    """Orchestrates ticket classification with business rules."""

    def __init__(self, llm_service: LLMService, settings: Settings) -> None:
        self._llm_service = llm_service
        self._settings = settings

    async def classify(self, ticket: str) -> ClassifyResponse:
        """
        Classify a support ticket into one of six categories.

        Applies confidence threshold business rule:
        if confidence < threshold, category is forced to Others.
        """
        result = await self._llm_service.classify_ticket_raw(ticket)

        try:
            parsed = parse_classification_response(result.content)
        except LLMResponseError:
            raise
        except Exception as exc:
            logger.error("Unexpected error parsing LLM response: %s", exc)
            raise LLMResponseError("Failed to parse LLM response.") from exc

        category = str(parsed["category"]).strip()
        confidence = self._normalize_confidence(parsed["confidence"])

        if not TicketCategory.is_valid(category):
            logger.warning(
                "Invalid category '%s' from LLM, defaulting to Others.",
                category,
            )
            category = TicketCategory.OTHERS.value
            confidence = min(confidence, self._settings.confidence_threshold)

        if confidence < self._settings.confidence_threshold:
            logger.info(
                "Confidence %.2f below threshold %.2f; reclassifying as Others.",
                confidence,
                self._settings.confidence_threshold,
            )
            category = TicketCategory.OTHERS.value

        return ClassifyResponse(
            ticket=ticket,
            category=category,
            confidence=round(confidence, 4),
        )

    @staticmethod
    def _normalize_confidence(value: object) -> float:
        """Normalize confidence to a float between 0.0 and 1.0."""
        try:
            confidence = float(value)  # type: ignore[arg-type]
        except (TypeError, ValueError) as exc:
            raise LLMResponseError("Invalid confidence value in LLM response.") from exc

        if confidence > 1.0 and confidence <= 100.0:
            confidence = confidence / 100.0

        return max(0.0, min(1.0, confidence))
