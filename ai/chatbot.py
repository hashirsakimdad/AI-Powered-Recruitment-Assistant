"""AI-powered feedback generation using Google Gemini."""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List

from .feedback_validator import validate_feedback_against_resume
from .llm_parser import parse_llm_json
from .scorer import score_candidate

logger = logging.getLogger(__name__)

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

GEMINI_FEEDBACK_PROMPT = """You are an expert HR consultant and career coach.
Analyze this resume against the job requirements and give detailed, actionable feedback.

JOB REQUIRED SKILLS: {required_skills}
MISSING SKILLS: {missing_skills}
OVERALL SCORE: {score:.1f}/100
KEYWORD MATCH: {keyword_score:.1f}/40
SEMANTIC SCORE: {semantic_score:.1f}/35
EXPERIENCE SCORE: {experience_score:.1f}/15
RESUME EXCERPT: {resume_excerpt}

Respond ONLY in this exact JSON format, no other text:
{{
    "overall_assessment": "2-3 sentence honest assessment",
    "strengths": ["strength 1", "strength 2", "strength 3"],
    "missing_skills": [
        {{
            "skill": "skill name",
            "importance": "high/medium/low",
            "how_to_learn": "specific resource or course"
        }}
    ],
    "next_steps": ["action 1", "action 2", "action 3"],
    "interview_tips": "2 sentence tip specific to this role",
    "improvement_potential": "what score they could reach if gaps fixed"
}}
"""


def _configure_gemini() -> bool:
    api_key = os.getenv("GOOGLE_API_KEY", "").strip()
    if not api_key:
        return False
    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        return True
    except Exception as exc:
        logger.warning("Gemini configure failed: %s", exc)
        return False


def generate_fallback_feedback(
    score: float,
    missing_skills: List[str],
) -> Dict[str, Any]:
    """Fallback if Gemini is unavailable."""
    if score >= 70:
        assessment = f"Score: {score:.1f}/100. Strong match!"
    elif score >= 50:
        assessment = f"Score: {score:.1f}/100. Moderate match."
    else:
        assessment = f"Score: {score:.1f}/100. Needs improvement."

    return {
        "overall_assessment": assessment,
        "strengths": ["Resume submitted successfully"],
        "missing_skills": [
            {
                "skill": skill,
                "importance": "high",
                "how_to_learn": "Online courses recommended",
            }
            for skill in missing_skills[:3]
        ],
        "next_steps": [
            "Add missing skills to resume",
            "Take relevant online courses",
            "Update resume with projects",
        ],
        "interview_tips": "Prepare examples of your experience.",
        "improvement_potential": "Score could improve significantly with targeted skill development.",
        "source": "fallback",
    }


def _normalize_gemini_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure Gemini response has expected types."""
    missing = data.get("missing_skills") or []
    normalized_missing = []
    for item in missing:
        if isinstance(item, dict):
            normalized_missing.append(
                {
                    "skill": str(item.get("skill", "")).strip(),
                    "importance": str(item.get("importance", "medium")).strip().lower(),
                    "how_to_learn": str(item.get("how_to_learn", "")).strip(),
                }
            )
        elif item:
            normalized_missing.append(
                {
                    "skill": str(item).strip(),
                    "importance": "medium",
                    "how_to_learn": "Explore online tutorials and hands-on projects.",
                }
            )

    return {
        "overall_assessment": str(data.get("overall_assessment", "")).strip(),
        "strengths": [str(s).strip() for s in (data.get("strengths") or []) if str(s).strip()],
        "missing_skills": normalized_missing,
        "next_steps": [str(s).strip() for s in (data.get("next_steps") or []) if str(s).strip()],
        "interview_tips": str(data.get("interview_tips", "")).strip(),
        "improvement_potential": str(data.get("improvement_potential", "")).strip(),
        "source": "gemini",
    }


def generate_gemini_feedback(
    score: float,
    keyword_score: float,
    semantic_score: float,
    experience_score: float,
    required_skills: List[str],
    resume_text: str,
    missing_skills: List[str],
) -> Dict[str, Any]:
    """Call Google Gemini 1.5 Flash for structured feedback JSON."""
    if not os.getenv("GOOGLE_API_KEY", "").strip():
        return generate_fallback_feedback(score, missing_skills)

    if not _configure_gemini():
        return generate_fallback_feedback(score, missing_skills)

    try:
        import google.generativeai as genai

        model = genai.GenerativeModel(GEMINI_MODEL)
        prompt = GEMINI_FEEDBACK_PROMPT.format(
            required_skills=", ".join(required_skills) or "Not specified",
            missing_skills=", ".join(missing_skills) or "None identified",
            score=score,
            keyword_score=keyword_score,
            semantic_score=semantic_score,
            experience_score=experience_score,
            resume_excerpt=(resume_text or "")[:800],
        )
        response = model.generate_content(prompt)
        raw_text = (response.text or "").strip()
        logger.info("Gemini raw feedback response: %s", raw_text[:2000])

        parsed = parse_llm_json(raw_text)
        return _normalize_gemini_payload(parsed)
    except Exception as exc:
        logger.warning("Gemini feedback failed: %s", exc, exc_info=True)
        fallback = generate_fallback_feedback(score, missing_skills)
        fallback["gemini_error"] = str(exc)
        return fallback


def _missing_skill_names(missing_skills: List[Any]) -> List[str]:
    names = []
    for item in missing_skills:
        if isinstance(item, dict):
            name = item.get("skill", "")
        else:
            name = str(item)
        if name:
            names.append(name)
    return names


def generate_feedback(profile: Dict, job: Dict[str, str]) -> Dict[str, Any]:
    """
    Generate personalized feedback via Gemini (with rule-based fallback).

    Returns a dict compatible with existing templates and validators, including
    Gemini fields: overall_assessment, strengths, missing_skills, next_steps,
    interview_tips, improvement_potential.
    """
    scoring = score_candidate(profile, job)
    overall_score = float(scoring.get("score", 0))
    keyword_score = float(scoring.get("keyword_score", 0))
    semantic_score = float(scoring.get("semantic_score", 0))
    experience_score = float(scoring.get("experience_score", 0))

    required_skills = [
        s.strip() for s in job.get("required_skills", "").split(",") if s.strip()
    ]
    required_lower = {s.lower() for s in required_skills}
    resume_skills = set()
    for line in profile.get("skills", []):
        for token in line.split(","):
            token = token.strip().lower()
            if token:
                resume_skills.add(token)
    missing = sorted(required_lower - resume_skills)

    gemini_data = generate_gemini_feedback(
        score=overall_score,
        keyword_score=keyword_score,
        semantic_score=semantic_score,
        experience_score=experience_score,
        required_skills=required_skills,
        resume_text=profile.get("raw_text", ""),
        missing_skills=missing,
    )

    suggestions = gemini_data.get("next_steps", [])
    summary = gemini_data.get("overall_assessment", "")

    feedback: Dict[str, Any] = {
        **gemini_data,
        "summary": summary,
        "suggestions": suggestions,
        "missing_skills": gemini_data.get("missing_skills", []),
        "score_breakdown": {
            "overall_score": overall_score,
            "keyword_score": keyword_score,
            "semantic_score": semantic_score,
            "experience_score": experience_score,
            "skill_alignment": scoring.get("skill_alignment", 0),
            "experience_bonus": scoring.get("experience_bonus", 0),
        },
    }

    validator_payload = {
        **feedback,
        "missing_skills": _missing_skill_names(feedback.get("missing_skills", [])),
    }
    is_valid, validation_result = validate_feedback_against_resume(
        validator_payload, profile, job
    )
    if not is_valid:
        feedback["validation_warnings"] = validation_result.get("all_errors", [])

    return feedback
