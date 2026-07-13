"""Tests for JSON parsing utilities."""

import pytest

from app.utils.exceptions import LLMResponseError
from app.utils.json_parser import extract_json_object, parse_classification_response


class TestExtractJsonObject:
    """Tests for extract_json_object."""

    def test_parses_plain_json(self) -> None:
        result = extract_json_object('{"category": "Payment", "confidence": 0.95}')
        assert result == {"category": "Payment", "confidence": 0.95}

    def test_parses_json_with_markdown_fences(self) -> None:
        text = '```json\n{"category": "Login Issue", "confidence": 0.88}\n```'
        result = extract_json_object(text)
        assert result == {"category": "Login Issue", "confidence": 0.88}

    def test_parses_json_with_surrounding_text(self) -> None:
        text = 'Here is the result: {"category": "Delivery", "confidence": 0.77} done.'
        result = extract_json_object(text)
        assert result == {"category": "Delivery", "confidence": 0.77}

    def test_returns_none_for_invalid_json(self) -> None:
        assert extract_json_object("not json at all") is None

    def test_returns_none_for_empty_string(self) -> None:
        assert extract_json_object("") is None


class TestParseClassificationResponse:
    """Tests for parse_classification_response."""

    def test_parses_valid_response(self) -> None:
        result = parse_classification_response(
            '{"category": "Account", "confidence": 0.91}'
        )
        assert result["category"] == "Account"
        assert result["confidence"] == 0.91

    def test_raises_on_malformed_json(self) -> None:
        with pytest.raises(LLMResponseError, match="Malformed JSON"):
            parse_classification_response("invalid response")

    def test_raises_on_missing_fields(self) -> None:
        with pytest.raises(LLMResponseError, match="missing required fields"):
            parse_classification_response('{"category": "Payment"}')
