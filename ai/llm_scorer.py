"""LLM-based CV scoring via Groq (OpenAI-compatible API)."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Tuple

import requests

from .llm_parser import normalize_cv_analysis, parse_llm_json
from .scorer import score_candidate

logger = logging.getLogger(__name__)

CV_SCORING_PROMPT = """You are an expert recruitment AI. Analyze the candidate resume against the job posting.

You MUST respond with ONLY a single JSON object. No markdown, no code fences, no preamble, no explanation outside JSON.

Use exactly this schema:
{{
  "score": 78,
  "summary": "Brief overall assessment in 2-3 sentences.",
  "strengths": ["strength one", "strength two"],
  "weaknesses": ["weakness one", "weakness two"],
  "recommendation": "hire / consider / reject with brief reason"
}}

Rules:
- "score" must be an integer from 0 to 100 reflecting job fit.
- Return pure JSON only.

Job Title: {title}
Required Skills: {required_skills}
Job Description:
{description}

Resume Text:
{resume_text}
"""


def _truncate(text: str, max_chars: int = 12000) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n...[truncated]"


def build_scoring_prompt(profile: Dict[str, Any], job: Dict[str, str]) -> str:
    resume_text = profile.get("raw_text") or ""
    return CV_SCORING_PROMPT.format(
        title=job.get("title", "Role"),
        required_skills=job.get("required_skills", ""),
        description=job.get("description", ""),
        resume_text=_truncate(resume_text),
    )


def call_groq_chat(prompt: str) -> str:
    """Call Groq chat completions API; returns raw assistant message text."""
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured")

    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    url = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
    timeout = int(os.getenv("GROQ_TIMEOUT_SECONDS", "60"))

    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a recruitment scoring engine. "
                        "Always reply with a single valid JSON object only."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 1024,
        },
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    return payload["choices"][0]["message"]["content"]


def rule_based_analysis(profile: Dict[str, Any], job: Dict[str, str]) -> Dict[str, Any]:
    """Fallback analysis using the local weighted scorer."""
    scoring = score_candidate(profile, job)
    score = float(scoring.get("score", 0))
    rationale = scoring.get("rationale", [])
    gaps = scoring.get("skill_gap", [])

    if score >= 70:
        recommendation = "consider — strong alignment with role requirements"
    elif score >= 50:
        recommendation = "consider — moderate fit with room to improve"
    else:
        recommendation = "reject — significant gaps versus job requirements"

    return {
        "score": score,
        "summary": (
            f"Automated scoring: {score:.1f}/100. "
            + (rationale[0] if rationale else "Review skill gaps and experience alignment.")
        ),
        "strengths": [r for r in rationale[:2]] or ["Resume parsed successfully"],
        "weaknesses": [f"Missing skill: {g}" for g in gaps[:3]]
        or ["Limited alignment with required skills"],
        "recommendation": recommendation,
        "source": "rule_based",
        "scoring_breakdown": scoring,
    }


def analyze_cv_with_llm(
    profile: Dict[str, Any],
    job: Dict[str, str],
    *,
    log_raw: bool = True,
) -> Tuple[Dict[str, Any], str]:
    """
    Score a CV using the LLM (Groq). Falls back to rule-based scoring if unavailable.

    Returns:
        Tuple of (normalized analysis dict, raw model response string).
    """
    prompt = build_scoring_prompt(profile, job)

    if not os.getenv("GROQ_API_KEY", "").strip():
        logger.info("GROQ_API_KEY not set — using rule-based CV scoring fallback")
        fallback = rule_based_analysis(profile, job)
        raw = '{"source":"rule_based_fallback","score":%s}' % fallback["score"]
        if log_raw:
            print(f"[CV SCORING] Raw model response (fallback): {raw}")
        return fallback, raw

    raw_response = ""
    try:
        raw_response = call_groq_chat(prompt)
        if log_raw:
            print(f"[CV SCORING] Raw model response: {raw_response}")
        logger.info("LLM raw CV scoring response: %s", raw_response[:2000])

        parsed = parse_llm_json(raw_response)
        normalized = normalize_cv_analysis(parsed)
        normalized["source"] = "llm"
        return normalized, raw_response
    except Exception as exc:
        logger.warning("LLM CV scoring failed (%s); using rule-based fallback", exc)
        if log_raw and raw_response:
            print(f"[CV SCORING] Raw model response (parse failed): {raw_response}")
        fallback = rule_based_analysis(profile, job)
        fallback["llm_error"] = str(exc)
        return fallback, raw_response or str(exc)
