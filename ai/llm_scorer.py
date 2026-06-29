"""LLM-based CV scoring via Google Gemini."""

import logging
import os
from typing import Any, Dict, Tuple

import google.generativeai as genai

from .llm_parser import normalize_cv_analysis, parse_llm_json
from .scorer import score_candidate

logger = logging.getLogger(__name__)

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

CV_SCORING_PROMPT = """You are an expert recruitment AI. 
Analyze the candidate resume against the job posting.

Respond with ONLY a single JSON object. No markdown, 
no explanation outside JSON.

Use exactly this schema:
{{
  "score": 78,
  "summary": "Brief overall assessment in 2-3 sentences.",
  "strengths": ["strength one", "strength two"],
  "weaknesses": ["weakness one", "weakness two"],
  "recommendation": "hire / consider / reject with brief reason"
}}

Rules:
- score must be integer 0 to 100
- Return pure JSON only

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


def safe(text: str) -> str:
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


def call_gemini(prompt: str) -> str:
    api_key = os.getenv("GOOGLE_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not configured")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(prompt)
    text = (response.text or "").strip()
    if not text:
        raise RuntimeError("Gemini returned an empty response")
    return text


def rule_based_analysis(profile: Dict[str, Any], job: Dict[str, str]) -> Dict[str, Any]:
    scoring = score_candidate(profile, job)
    score = float(scoring.get("score", 0))
    rationale = scoring.get("rationale", [])
    gaps = scoring.get("skill_gap", [])

    if score >= 70:
        recommendation = "hire — strong alignment"
    elif score >= 50:
        recommendation = "consider — moderate fit"
    else:
        recommendation = "reject — significant gaps"

    return {
        "score": score,
        "summary": f"Score: {score:.1f}/100. " + (rationale[0] if rationale else ""),
        "strengths": rationale[:2] or ["Resume parsed successfully"],
        "weaknesses": [f"Missing: {g}" for g in gaps[:3]] or ["Limited skill alignment"],
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
    prompt = build_scoring_prompt(profile, job)

    if not os.getenv("GOOGLE_API_KEY", "").strip():
        logger.info("GOOGLE_API_KEY not set — using rule-based fallback")
        fallback = rule_based_analysis(profile, job)
        return fallback, "rule_based_fallback"

    raw_response = ""
    try:
        raw_response = call_gemini(prompt)
        if log_raw:
            logger.info("Gemini CV scoring response: %s", raw_response[:2000])

        parsed = parse_llm_json(raw_response)
        normalized = normalize_cv_analysis(parsed)
        normalized["source"] = "gemini"
        return normalized, raw_response

    except Exception as exc:
        logger.warning("Gemini scoring failed (%s) — fallback", exc, exc_info=True)
        fallback = rule_based_analysis(profile, job)
        fallback["llm_error"] = str(exc)
        return fallback, raw_response or str(exc)
