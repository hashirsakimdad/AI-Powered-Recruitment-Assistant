from typing import Dict, List, Tuple

from .feedback_validator import validate_feedback_against_resume
from .scorer import score_candidate
from .section_feedback import generate_section_aware_feedback

SYSTEM_PROMPT = """
You are an expert recruitment advisor analyzing a resume against a job posting.

You MUST respond with ONLY a single JSON object — no markdown, no code fences, no preamble.

Required schema:
{
  "score": 78,
  "summary": "2-3 sentence overall assessment",
  "strengths": ["strength one", "strength two"],
  "weaknesses": ["weakness one", "weakness two"],
  "recommendation": "hire / consider / reject with brief reason"
}

Be specific. Mention actual technologies and experience. Never give generic advice.
"""


def _rank_suggestions_by_importance(
    suggestions: List[str],
    overall_score: float,
    semantic_score: float,
    skill_alignment: float,
    missing_skills: List[str]
) -> List[str]:
    """
    Rank suggestions by importance based on scores and missing skills.
    Higher priority = lower scores or critical missing skills.
    
    Returns:
        List of suggestions ranked by importance (most important first)
    """
    if not suggestions:
        return []
    
    # Score each suggestion based on importance
    scored_suggestions: List[Tuple[float, str]] = []
    
    for suggestion in suggestions:
        priority = 0.0
        suggestion_lower = suggestion.lower()
        
        # Critical issues get higher priority
        if overall_score < 50:
            if "score" in suggestion_lower or "align" in suggestion_lower:
                priority += 10.0
        
        if semantic_score < 40:
            if "semantic" in suggestion_lower or "keyword" in suggestion_lower:
                priority += 8.0
        
        if skill_alignment < 30:
            if "skill" in suggestion_lower or any(skill in suggestion_lower for skill in missing_skills[:3]):
                priority += 9.0
        
        # Missing skills mentioned get priority
        for skill in missing_skills[:3]:
            if skill in suggestion_lower:
                priority += 5.0
        
        # Experience-related suggestions
        if "experience" in suggestion_lower or "years" in suggestion_lower:
            priority += 3.0
        
        # Section-specific feedback gets moderate priority
        if "[" in suggestion and "]" in suggestion:
            priority += 2.0
        
        scored_suggestions.append((priority, suggestion))
    
    # Sort by priority (highest first), then by original order
    scored_suggestions.sort(key=lambda x: (-x[0], suggestions.index(x[1])))
    
    return [suggestion for _, suggestion in scored_suggestions]


def _build_structured_markdown(
    overall_score: float,
    missing: List[str],
    strengths: List[str],
    suggestions: List[str],
    job_title: str,
) -> str:
    """Format feedback as markdown per SYSTEM_PROMPT structure."""
    if overall_score >= 70:
        assessment = (
            f"Your profile aligns well with **{job_title}** (score {overall_score:.1f}/100). "
            "You demonstrate relevant skills and experience for this role."
        )
    elif overall_score >= 50:
        assessment = (
            f"You show moderate fit for **{job_title}** (score {overall_score:.1f}/100). "
            "Strengthening a few gaps below would improve your competitiveness."
        )
    else:
        assessment = (
            f"Your resume needs targeted improvements for **{job_title}** (score {overall_score:.1f}/100). "
            "Focus on the missing skills and experience signals recruiters expect."
        )

    missing_lines = []
    for i, skill in enumerate((missing or ["Role-specific tooling"])[:3], 1):
        missing_lines.append(
            f"{i}. **{skill.title()}** — Required for this role — "
            f"Spend week {i} on a hands-on tutorial and one portfolio mini-project using {skill}."
        )
    while len(missing_lines) < 3:
        n = len(missing_lines) + 1
        missing_lines.append(
            f"{n}. **Industry terminology** — Improves ATS matching — "
            f"Mirror keywords from the job description in your project bullets this week."
        )

    strength_items = strengths[:3] if strengths else [
        "Clear resume structure",
        "Relevant background for the role",
        "Willingness to close skill gaps quickly",
    ]
    step_items = suggestions[:3] if suggestions else [
        "Update your skills section to mirror required technologies (this week)",
        "Add one quantified achievement per recent role (3 days)",
        "Submit a revised resume after practicing one missing skill (7 days)",
    ]

    return f"""## Overall Assessment
{assessment}

## Top 3 Missing Skills
{chr(10).join(missing_lines)}

## What You Did Well
{chr(10).join('- ' + s for s in strength_items)}

## Recommended Next Steps
{chr(10).join(f'{i + 1}. {s}' for i, s in enumerate(step_items))}
"""


def generate_feedback(profile: Dict, job: Dict[str, str]) -> Dict[str, List[str] | str]:
    """
    Generate personalized feedback using scoring results and section-aware approach.
    Feedback is now unique to each resume based on actual scores and content.
    """
    # Get scoring results to personalize feedback
    scoring = score_candidate(profile, job)
    overall_score = scoring.get("score", 0)
    semantic_score = scoring.get("semantic_score", 0)
    skill_alignment = scoring.get("skill_alignment", 0)
    experience_bonus = scoring.get("experience_bonus", 0)
    
    # Generate section-aware feedback
    section_feedback = generate_section_aware_feedback(profile, job)
    
    # Extract missing skills
    required_skills = {s.strip().lower() for s in job.get("required_skills", "").split(",") if s.strip()}
    resume_skills = set()
    for line in profile.get("skills", []):
        for token in line.split(","):
            token = token.strip().lower()
            if token:
                resume_skills.add(token)
    
    missing = sorted(required_skills - resume_skills)
    
    # Generate personalized feedback based on scores
    personalized_suggestions = []
    
    # Score-based personalized feedback
    if overall_score < 50:
        personalized_suggestions.append(
            f"Your resume score is {overall_score:.1f}%. Focus on aligning your content more closely with the job requirements."
        )
    elif overall_score < 70:
        personalized_suggestions.append(
            f"Your resume score is {overall_score:.1f}%. There's room for improvement to better match this role."
        )
    else:
        personalized_suggestions.append(
            f"Your resume score is {overall_score:.1f}%. Good alignment with the job requirements!"
        )
    
    # Semantic similarity feedback
    if semantic_score < 40:
        personalized_suggestions.append(
            f"Low semantic similarity ({semantic_score:.1f}%). Incorporate more keywords and phrases from the job description naturally into your resume."
        )
    elif semantic_score < 60:
        personalized_suggestions.append(
            f"Moderate semantic similarity ({semantic_score:.1f}%). Consider adding more role-specific terminology to improve ATS matching."
        )
    else:
        personalized_suggestions.append(
            f"Strong semantic alignment ({semantic_score:.1f}%) with the job description. Well done!"
        )
    
    # Skill alignment feedback
    if skill_alignment < 30:
        personalized_suggestions.append(
            f"Low skill match ({skill_alignment:.1f}%). You're missing several required skills. Consider highlighting transferable skills or gaining experience with: {', '.join(list(missing)[:3]) if missing else 'the required technologies'}."
        )
    elif skill_alignment < 60:
        personalized_suggestions.append(
            f"Partial skill match ({skill_alignment:.1f}%). You have some required skills. Consider adding: {', '.join(list(missing)[:2]) if missing else 'additional relevant skills'}."
        )
    else:
        matched_skills = required_skills.intersection(resume_skills)
        personalized_suggestions.append(
            f"Good skill alignment ({skill_alignment:.1f}%)! You have {len(matched_skills)} of the required skills: {', '.join(list(matched_skills)[:3])}."
        )
    
    # Experience feedback
    years_exp = profile.get("years_experience", 0)
    if experience_bonus < 30:
        if years_exp == 0:
            personalized_suggestions.append(
                "Your experience level appears limited. Emphasize projects, internships, or relevant coursework to demonstrate capabilities."
            )
        else:
            personalized_suggestions.append(
                f"With {years_exp} years of experience, highlight more specific achievements and measurable impact in your roles."
            )
    elif experience_bonus >= 70:
        personalized_suggestions.append(
            f"Strong experience profile ({experience_bonus:.1f}%). Your {years_exp} years of experience align well with the role requirements."
        )
    
    # Add section-specific feedback
    all_suggestions = personalized_suggestions.copy()
    for section, suggestions in section_feedback.items():
        for suggestion in suggestions:
            # Make sure we don't duplicate similar feedback
            suggestion_lower = suggestion.lower()
            is_duplicate = any(
                suggestion_lower[:40] in existing.lower() or existing.lower()[:40] in suggestion_lower
                for existing in all_suggestions
            )
            if not is_duplicate:
                all_suggestions.append(f"[{section.title()}]: {suggestion}")
    
    # Limit total suggestions but prioritize personalized ones
    final_suggestions = personalized_suggestions + [
        s for s in all_suggestions[len(personalized_suggestions):] 
        if s not in personalized_suggestions
    ][:8]
    
    # Create personalized summary
    if overall_score >= 70:
        summary = f"Your resume shows strong alignment (Score: {overall_score:.1f}%) with this position. "
    elif overall_score >= 50:
        summary = f"Your resume has moderate alignment (Score: {overall_score:.1f}%) with this position. "
    else:
        summary = f"Your resume needs improvement (Score: {overall_score:.1f}%) to better match this position. "
    
    summary += "Focus on the suggestions below to enhance your candidacy."
    
    # Calculate skill gap percentage
    total_required_skills = len(required_skills) if required_skills else 1
    matched_skills_count = len(required_skills.intersection(resume_skills))
    skill_gap_percentage = ((total_required_skills - matched_skills_count) / total_required_skills) * 100
    
    # Calculate confidence score (weighted average of all scores)
    confidence_score = (
        (overall_score / 100) * 0.4 +
        (semantic_score / 100) * 0.3 +
        (skill_alignment / 100) * 0.2 +
        (experience_bonus / 100) * 0.1
    ) * 100
    
    # Rank suggestions by importance (score-based ranking)
    ranked_suggestions = _rank_suggestions_by_importance(
        final_suggestions, 
        overall_score, 
        semantic_score, 
        skill_alignment,
        missing
    )
    
    strengths = []
    matched_skills = required_skills.intersection(resume_skills)
    if matched_skills:
        strengths.append(f"Matched skills: {', '.join(list(matched_skills)[:4])}.")
    if semantic_score >= 50:
        strengths.append("Resume language aligns with the job description.")
    if experience_bonus >= 50:
        strengths.append("Experience level supports the role requirements.")
    if not strengths:
        strengths.append("Resume is parseable with identifiable sections.")

    markdown_response = _build_structured_markdown(
        overall_score,
        missing,
        strengths,
        ranked_suggestions,
        job.get("title", "this role"),
    )

    # Build feedback response
    feedback = {
        "summary": markdown_response,
        "markdown_response": markdown_response,
        "system_prompt": SYSTEM_PROMPT,
        "missing_skills": missing,
        "suggestions": ranked_suggestions,
        "section_feedback": section_feedback,
        "score_breakdown": {
            "overall_score": overall_score,
            "semantic_score": semantic_score,
            "skill_alignment": skill_alignment,
            "experience_bonus": experience_bonus,
        },
        # Bonus features
        "confidence_score": round(confidence_score, 2),
        "skill_gap_percentage": round(skill_gap_percentage, 1),
        "matched_skills_count": matched_skills_count,
        "total_required_skills": total_required_skills,
    }
    
    # Validate feedback
    is_valid, validation_result = validate_feedback_against_resume(feedback, profile, job)
    
    if not is_valid:
        # If validation fails, keep personalized suggestions but filter invalid ones
        valid_suggestions = personalized_suggestions.copy()
        for suggestion in all_suggestions[len(personalized_suggestions):]:
            is_invalid = any(error.lower() in suggestion.lower() for error in validation_result.get("all_errors", []))
            if not is_invalid and suggestion not in valid_suggestions:
                valid_suggestions.append(suggestion)
        
        feedback["suggestions"] = valid_suggestions[:8] if valid_suggestions else personalized_suggestions
        feedback["validation_warnings"] = validation_result.get("all_errors", [])
    
    return feedback

