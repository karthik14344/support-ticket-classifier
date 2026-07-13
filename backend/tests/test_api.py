"""Tests for API endpoints."""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_classifier_service
from app.main import app
from app.utils.exceptions import ConfigurationError
from app.schemas.request_response import ClassifyResponse


class TestHealthEndpoint:
    """Tests for GET /health."""

    def test_health_returns_healthy(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestRootEndpoint:
    """Tests for GET /."""

    def test_root_returns_api_info(self, client: TestClient) -> None:
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data
        assert data["endpoints"]["classify"] == "POST /classify"


class TestClassifyEndpoint:
    """Tests for POST /classify."""

    def test_classify_success(self, client: TestClient) -> None:
        mock_response = ClassifyResponse(
            ticket="Payment deducted twice.",
            category="Payment",
            confidence=0.95,
        )
        mock_service = AsyncMock()
        mock_service.classify.return_value = mock_response
        app.dependency_overrides[get_classifier_service] = lambda: mock_service

        try:
            response = client.post(
                "/classify",
                json={"ticket": "Payment deducted twice."},
            )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "Payment"
        assert data["confidence"] == 0.95
        assert data["ticket"] == "Payment deducted twice."

    def test_classify_empty_ticket_returns_422(self, client: TestClient) -> None:
        response = client.post("/classify", json={"ticket": "   "})
        assert response.status_code == 422

    def test_classify_missing_ticket_returns_422(self, client: TestClient) -> None:
        response = client.post("/classify", json={})
        assert response.status_code == 422

    def test_classify_invalid_llm_response_returns_502(self, client: TestClient) -> None:
        from app.utils.exceptions import LLMResponseError

        mock_service = AsyncMock()
        mock_service.classify.side_effect = LLMResponseError("Invalid response.")
        app.dependency_overrides[get_classifier_service] = lambda: mock_service

        try:
            response = client.post(
                "/classify",
                json={"ticket": "Some ticket text."},
            )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 502
        assert "Invalid response" in response.json()["detail"]

    def test_classify_llm_service_error_returns_503(self, client: TestClient) -> None:
        from app.utils.exceptions import LLMServiceError

        mock_service = AsyncMock()
        mock_service.classify.side_effect = LLMServiceError("Service unavailable.")
        app.dependency_overrides[get_classifier_service] = lambda: mock_service

        try:
            response = client.post(
                "/classify",
                json={"ticket": "Some ticket text."},
            )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 503

    def test_classify_missing_api_key_returns_500(self, client: TestClient) -> None:
        mock_service = AsyncMock()
        mock_service.classify.side_effect = ConfigurationError(
            "GEMINI_API_KEY is not configured.",
            "Set it in your .env file.",
        )
        app.dependency_overrides[get_classifier_service] = lambda: mock_service

        try:
            response = client.post(
                "/classify",
                json={"ticket": "Valid ticket text."},
            )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 500
        assert "GEMINI_API_KEY" in response.json()["detail"]
