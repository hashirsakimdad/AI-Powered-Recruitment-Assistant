"""
Feedback Validation Guard
Validates feedback against extracted resume data to ensure:
 Relevance against resume content
 Logical consistency
 Zero hallucination tolerance
"""
from typing import Dict, List, Tuple


def validate_feedback_relevance(
    feedback: Dict[str, any],
    resume_data: Dict[str, any],
    job_data: Dict[str, str]
) -> Tuple[bool, List[str]]:
    """
    Validate that feedback is relevant to the resume content.
    
    Args:
        feedback: Generated feedback dictionary
        resume_data: Parsed resume data
        job_data: Job posting data
        
    Returns:
        Tuple of (is_valid: bool, validation_errors: List[str])
    """
    errors = []
    
    # Check if feedback mentions skills that don't exist in resume
    resume_skills_text = " ".join([
        " ".join(resume_data.get("skills", [])),
        resume_data.get("raw_text", "").lower()
    ]).lower()
    
    feedback_text = str(feedback).lower()
    
    # Extract skill mentions from feedback
    skill_keywords = ["python", "java", "javascript", "sql", "react", "node", "aws", "docker"]
    mentioned_skills = [skill for skill in skill_keywords if skill in feedback_text]
    
    for skill in mentioned_skills:
        if skill not in resume_skills_text:
            errors.append(f"Feedback mentions '{skill}' but it's not found in resume")
    
    # Validate missing skills suggestions are actually missing
    missing_skills = feedback.get("missing_skills", [])
    resume_skills_set = set()
    for skill_line in resume_data.get("skills", []):
        for token in skill_line.split(","):
            token = token.strip().lower()
            if token:
                resume_skills_set.add(token)
    
    job_skills = {s.strip().lower() for s in job_data.get("required_skills", "").split(",") if s.strip()}
    
    for missing_skill in missing_skills:
        if missing_skill.lower() in resume_skills_set:
            errors.append(f"Feedback incorrectly lists '{missing_skill}' as missing when it's in the resume")
    
    # Check for generic/fabricated suggestions
    generic_phrases = [
        "add more experience",
        "improve your resume",
        "make it better",
        "enhance your skills",
    ]
    
    for phrase in generic_phrases:
        if phrase in feedback_text and len(feedback_text) < 200:
            errors.append(f"Feedback contains generic phrase without specific context: '{phrase}'")
    
    # Validate experience-related feedback
    resume_exp = resume_data.get("years_experience", 0)
    if resume_exp > 0:
        # If resume has experience, feedback shouldn't suggest adding experience without context
        if "add experience" in feedback_text.lower() and "years" not in feedback_text.lower():
            errors.append("Feedback suggests adding experience without acknowledging existing experience")
    
    return len(errors) == 0, errors


def validate_feedback_consistency(feedback: Dict[str, any]) -> Tuple[bool, List[str]]:
    """
    Check logical consistency of feedback.
    
    Args:
        feedback: Generated feedback dictionary
        
    Returns:
        Tuple of (is_consistent: bool, inconsistencies: List[str])
    """
    inconsistencies = []
    
    # Check if suggestions contradict each other
    suggestions = feedback.get("suggestions", [])
    
    # Look for contradictory advice
    has_quantify = any("quantify" in s.lower() or "metrics" in s.lower() for s in suggestions)
    has_simplify = any("simplify" in s.lower() or "concise" in s.lower() for s in suggestions)
    
    if has_quantify and has_simplify and len(suggestions) < 4:
        inconsistencies.append("Feedback suggests both quantifying (adding metrics) and simplifying simultaneously")
    
    # Check for repetitive suggestions
    if len(suggestions) > 1:
        unique_suggestions = set(s.lower().strip() for s in suggestions)
        if len(unique_suggestions) < len(suggestions):
            inconsistencies.append("Feedback contains repetitive suggestions")
    
    return len(inconsistencies) == 0, inconsistencies


def validate_feedback_against_resume(
    feedback: Dict[str, any],
    resume_data: Dict[str, any],
    job_data: Dict[str, str]
) -> Tuple[bool, Dict[str, any]]:
    """
    Comprehensive feedback validation.
    
    Args:
        feedback: Generated feedback
        resume_data: Parsed resume data
        job_data: Job posting data
        
    Returns:
        Tuple of (is_valid: bool, validation_result: dict)
    """
    is_relevant, relevance_errors = validate_feedback_relevance(feedback, resume_data, job_data)
    is_consistent, consistency_errors = validate_feedback_consistency(feedback)
    
    is_valid = is_relevant and is_consistent
    all_errors = relevance_errors + consistency_errors
    
    return is_valid, {
        "is_valid": is_valid,
        "relevance_check": {
            "passed": is_relevant,
            "errors": relevance_errors
        },
        "consistency_check": {
            "passed": is_consistent,
            "errors": consistency_errors
        },
        "all_errors": all_errors
    }

