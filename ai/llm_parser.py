"""Parse structured JSON from LLM responses (with optional markdown fences)."""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict

logger = logging.getLogger(__name__)

_FENCE_PATTERN = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE | re.MULTILINE)


def strip_code_fences(text: str) -> str:
    """Remove ```json ... ``` wrappers and trim whitespace."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = _FENCE_PATTERN.sub("", cleaned).strip()
    return cleaned


def extract_json_object(text: str) -> str:
    """Return the first JSON object substring from mixed LLM output."""
    cleaned = strip_code_fences(text)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        return cleaned[start : end + 1]
    return cleaned


def parse_llm_json(raw_response: str) -> Dict[str, Any]:
    """
    Safely parse JSON from an LLM response.

    Raises:
        ValueError: If the response cannot be parsed as JSON.
    """
    if not raw_response or not str(raw_response).strip():
        raise ValueError("Empty model response")

    payload = extract_json_object(str(raw_response))
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        logger.warning("LLM JSON parse failed: %s | raw=%r", exc, raw_response[:500])
        raise ValueError(f"Could not parse model response as JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("Model response must be a JSON object")

    return data


def normalize_cv_analysis(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize the CV analysis schema."""
    score_raw = data.get("score")
    if score_raw is None:
        raise ValueError("Model response missing required field: score")

    try:
        score = float(score_raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid score value: {score_raw!r}") from exc

    score = max(0.0, min(100.0, round(score, 1)))

    def _as_str_list(value: Any) -> list[str]:
        if not value:
            return []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        return [str(value).strip()] if str(value).strip() else []

    return {
        "score": score,
        "summary": str(data.get("summary", "")).strip(),
        "strengths": _as_str_list(data.get("strengths")),
        "weaknesses": _as_str_list(data.get("weaknesses")),
        "recommendation": str(data.get("recommendation", "")).strip(),
    }
