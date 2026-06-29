"""LLM-based CV scoring — Groq primary, rule-based fallback."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Tuple

from .llm_parser import normalize_cv_analysis, parse_llm_json
from .scorer import score_candidate

logger = logging.getLogger(__name__)

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

CV_SCORING_PROMPT = """You are an expert recruitment AI.
Analyze the candidate resume against the job posting.

Respond with ONLY a single valid JSON object.
No markdown, no explanation, no code fences. Pure JSON only.

Schema:
{{
  "score": 78,
  "summary": "2-3 sentence honest assessment of candidate fit.",
  "strengths": ["specific strength one", "specific strength two"],
  "weaknesses": ["specific gap one", "specific gap two"],
  "recommendation": "hire / consider / reject — with brief reason"
}}

Rules:
- score must be integer 0 to 100 reflecting job fit
- Be specific — mention actual skills from resume
- Return pure JSON only — nothing else before or after

Job Title: {title}
Required Skills: {required_skills}
Job Description:
{description}

Resume Text:
{resume_text}
"""


def _truncate(text: str, max_chars: int = 8000) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n...[truncated]"


def safe(text: str) -> str:
    """Escape curly braces to prevent .format() KeyError."""
    if not text:
        return ""
    return str(text).replace("{", "(").replace("}", ")")


def build_scoring_prompt(profile: Dict[str, Any], job: Dict[str, str]) -> str:
    resume_text = profile.get("raw_text") or ""
    return CV_SCORING_PROMPT.format(
        title=safe(job.get("title", "Role")),
        required_skills=safe(job.get("required_skills", "")),
        description=safe(job.get("description", "")),
        resume_text=safe(_truncate(resume_text)),
    )


def call_groq(prompt: str) -> str:
    """Call Groq API."""
    from groq import Groq

    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set")

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a recruitment scoring AI. "
                    "Always reply with valid JSON only. No markdown, no explanation."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=1024,
    )
    content = (response.choices[0].message.content or "").strip()
    if not content:
        raise RuntimeError("Groq returned an empty response")
    return content


def call_llm(prompt: str) -> str:
    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    if not groq_key:
        raise RuntimeError("GROQ_API_KEY not configured")
    result = call_groq(prompt)
    logger.info("Groq scoring successful")
    return result


def rule_based_analysis(profile: Dict[str, Any], job: Dict[str, str]) -> Dict[str, Any]:
    """Local fallback — works without any API key."""
    scoring = score_candidate(profile, job)
    score = float(scoring.get("score", 0))
    rationale = scoring.get("rationale", [])
    gaps = scoring.get("skill_gap", [])

    if score >= 70:
        rec = "hire — strong alignment with job requirements"
    elif score >= 50:
        rec = "consider — moderate fit, some gaps present"
    else:
        rec = "reject — significant skill gaps versus requirements"

    return {
        "score": score,
        "summary": (
            f"Automated match score: {score:.1f}/100. "
            + (rationale[0] if rationale else "Review skill alignment carefully.")
        ),
        "strengths": rationale[:2] or ["Resume successfully parsed"],
        "weaknesses": [f"Missing skill: {g}" for g in gaps[:3]]
        or ["Limited alignment with required skills"],
        "recommendation": rec,
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
    Score CV using LLM.
    Priority: Groq → Rule-based fallback
    """
    prompt = build_scoring_prompt(profile, job)
    raw_response = ""

    if not os.getenv("GROQ_API_KEY", "").strip():
        logger.info("GROQ_API_KEY not set — using rule-based scoring")
        fallback = rule_based_analysis(profile, job)
        return fallback, "no_api_keys"

    try:
        raw_response = call_llm(prompt)

        if log_raw:
            print(f"[CV SCORING] LLM response: {raw_response[:300]}")
        logger.info("LLM response received: %s", raw_response[:500])

        parsed = parse_llm_json(raw_response)
        normalized = normalize_cv_analysis(parsed)
        normalized["source"] = "llm"
        return normalized, raw_response

    except Exception as exc:
        logger.warning("LLM scoring failed (%s) — rule-based fallback", exc)
        if log_raw and raw_response:
            print(f"[CV SCORING] Failed response: {raw_response[:300]}")
        fallback = rule_based_analysis(profile, job)
        fallback["llm_error"] = str(exc)
        return fallback, raw_response or str(exc)
