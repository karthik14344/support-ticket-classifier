"""Tests for classifier business logic."""

import pytest

from app.models.categories import TicketCategory
from tests.conftest import build_classifier


@pytest.mark.asyncio
async def test_successful_classification(test_settings) -> None:
    """Classify a ticket successfully with high confidence."""
    classifier = build_classifier(
        test_settings,
        '{"category": "Login Issue", "confidence": 0.92}',
    )
    result = await classifier.classify("I cannot login to my account.")

    assert result.category == TicketCategory.LOGIN_ISSUE.value
    assert result.confidence == 0.92
    assert result.ticket == "I cannot login to my account."


@pytest.mark.asyncio
async def test_confidence_threshold_forces_others(test_settings) -> None:
    """Low confidence should force classification to Others."""
    classifier = build_classifier(
        test_settings,
        '{"category": "Payment", "confidence": 0.45}',
    )
    result = await classifier.classify("Something vague happened.")

    assert result.category == TicketCategory.OTHERS.value
    assert result.confidence == 0.45


@pytest.mark.asyncio
async def test_confidence_at_threshold_keeps_category(test_settings) -> None:
    """Confidence exactly at threshold should keep the predicted category."""
    classifier = build_classifier(
        test_settings,
        '{"category": "Delivery", "confidence": 0.60}',
    )
    result = await classifier.classify("My order is late.")

    assert result.category == TicketCategory.DELIVERY.value
    assert result.confidence == 0.60


@pytest.mark.asyncio
async def test_invalid_category_defaults_to_others(test_settings) -> None:
    """Invalid category from LLM should default to Others."""
    classifier = build_classifier(
        test_settings,
        '{"category": "Unknown Category", "confidence": 0.85}',
    )
    result = await classifier.classify("Random ticket text.")

    assert result.category == TicketCategory.OTHERS.value


@pytest.mark.asyncio
async def test_percentage_confidence_normalized(test_settings) -> None:
    """Confidence values above 1.0 up to 100 should be normalized."""
    classifier = build_classifier(
        test_settings,
        '{"category": "Technical Issue", "confidence": 85}',
    )
    result = await classifier.classify("App crashes after opening.")

    assert result.category == TicketCategory.TECHNICAL_ISSUE.value
    assert result.confidence == 0.85
