# Convenience imports for AI utilities
from .parser import extract_text, parse_resume
from .scorer import score_candidate, embed_text
from .chatbot import generate_feedback
from .resume_detector import detect_resume, validate_resume_document
from .feedback_validator import validate_feedback_against_resume
from .section_feedback import generate_section_aware_feedback
from .skill_inference import infer_skills_from_text, combine_explicit_and_inferred_skills

__all__ = [
    "extract_text",
    "parse_resume",
    "score_candidate",
    "embed_text",
    "generate_feedback",
    "detect_resume",
    "validate_resume_document",
    "validate_feedback_against_resume",
    "generate_section_aware_feedback",
    "infer_skills_from_text",
    "combine_explicit_and_inferred_skills",
]

