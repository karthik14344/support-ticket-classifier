"""Safe JSON parsing utilities for LLM responses."""

import json
import logging
import re
from typing import Any, Optional

from app.utils.exceptions import LLMResponseError

logger = logging.getLogger(__name__)


def _strip_markdown_fences(text: str) -> str:
    """Remove markdown code fences if present."""
    cleaned = text.strip()
    fence_pattern = r"^```(?:json)?\s*|\s*```$"
    cleaned = re.sub(fence_pattern, "", cleaned, flags=re.IGNORECASE | re.MULTILINE)
    return cleaned.strip()


def extract_json_object(text: str) -> Optional[dict[str, Any]]:
    """
    Extract and parse a JSON object from LLM response text.

    Handles responses wrapped in markdown or with surrounding text.
    """
    if not text or not text.strip():
        return None

    cleaned = _strip_markdown_fences(text)

    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[^{}]*\}", cleaned, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group())
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            logger.warning("Failed to parse extracted JSON object.")

    return None


def parse_classification_response(text: str) -> dict[str, Any]:
    """
    Parse LLM classification response into category and confidence.

    Raises LLMResponseError on failure.
    """
    data = extract_json_object(text)
    if data is None:
        logger.error("Malformed JSON in LLM response: %s", text[:200])
        raise LLMResponseError("Malformed JSON in LLM response.")

    if "category" not in data or "confidence" not in data:
        logger.error("Missing required fields in LLM response: %s", data)
        raise LLMResponseError("LLM response missing required fields.")

    return data
