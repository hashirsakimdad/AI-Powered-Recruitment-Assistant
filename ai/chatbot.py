"""AI-powered feedback generation using Groq."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List

from .feedback_validator import validate_feedback_against_resume
from .scorer import score_candidate

logger = logging.getLogger(__name__)

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


def generate_fallback_feedback(
    score: float,
    missing_skills: List[str],
) -> Dict[str, Any]:
    """Fallback if Groq is unavailable."""
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


def generate_groq_feedback(profile, job, scoring):
    try:
        from groq import Groq

        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            return None

        gaps = scoring.get("skill_gap", [])
        score = scoring.get("score", 0)

        client = Groq(api_key=api_key)
        prompt = f"""You are a career coach giving resume feedback.

Job Title: {job.get('title', 'Role')}
Required Skills: {job.get('required_skills', '')}
Candidate Score: {score}/100
Missing Skills: {', '.join(gaps[:5]) if gaps else 'None'}

Write 3-4 sentences of specific, actionable feedback.
Tell them exactly what to improve and how."""

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.warning("Groq feedback failed: %s", e)
        return None


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
    Generate personalized feedback via Groq (with rule-based fallback).
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

    groq_text = generate_groq_feedback(profile, job, scoring)
    if groq_text:
        feedback_data = {
            "overall_assessment": groq_text.strip(),
            "strengths": [],
            "missing_skills": [
                {
                    "skill": skill,
                    "importance": "high",
                    "how_to_learn": "Explore tutorials and hands-on projects.",
                }
                for skill in missing[:3]
            ],
            "next_steps": [],
            "interview_tips": "",
            "improvement_potential": "",
            "source": "groq",
        }
    else:
        feedback_data = generate_fallback_feedback(overall_score, missing)

    suggestions = feedback_data.get("next_steps", [])
    summary = feedback_data.get("overall_assessment", "")

    feedback: Dict[str, Any] = {
        **feedback_data,
        "summary": summary,
        "suggestions": suggestions,
        "missing_skills": feedback_data.get("missing_skills", []),
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
