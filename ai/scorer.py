from __future__ import annotations

import pickle
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

_job_classifier = None
_job_vectorizer = None
_job_categories: Optional[List[str]] = None

SKILL_WEIGHTS = {
    "programming": 1.2,
    "frameworks": 1.1,
    "soft_skills": 0.8,
    "domain": 1.0,
    "tools": 1.0,
    "education": 0.9,
}

SKILL_CATEGORIES = {
    "python": "programming",
    "javascript": "programming",
    "java": "programming",
    "c++": "programming",
    "react": "frameworks",
    "django": "frameworks",
    "flask": "frameworks",
    "node": "frameworks",
    "communication": "soft_skills",
    "leadership": "soft_skills",
    "teamwork": "soft_skills",
    "problem solving": "soft_skills",
    "git": "tools",
    "docker": "tools",
    "aws": "tools",
    "sql": "tools",
    "linux": "tools",
    "finance": "domain",
    "healthcare": "domain",
    "machine learning": "domain",
    "data science": "domain",
}

_model = None


def get_model():
    global _model
    if _model is None:
        print("Loading semantic model... (first time only)")
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer("all-mpnet-base-v2")
        print("Model loaded successfully")
    return _model


def normalize_score(raw: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Clamp and normalize a raw score to 0-100 range."""
    clamped = max(min_val, min(max_val, raw))
    if max_val == min_val:
        return 0.0
    return round((clamped - min_val) / (max_val - min_val) * 100, 1)


def compute_keyword_score(resume_text: str, required_skills_str: str) -> float:
    """
    Case-insensitive partial match.
    Max contribution capped at 40 points.
    """
    resume_lower = resume_text.lower()
    skills = [s.strip().lower() for s in required_skills_str.split(",") if s.strip()]
    if not skills:
        return 0.0

    total_weight = 0.0
    matched_weight = 0.0

    for skill in skills:
        category = SKILL_CATEGORIES.get(skill, "domain")
        weight = SKILL_WEIGHTS.get(category, 1.0)
        total_weight += weight
        if skill in resume_lower:
            matched_weight += weight

    if total_weight == 0:
        return 0.0

    raw_ratio = matched_weight / total_weight
    return min(40.0, raw_ratio * 40.0)


def compute_semantic_score(resume_text: str, job_description: str) -> float:
    """Temperature-scaled cosine similarity. Max 35 points."""
    try:
        from sentence_transformers import util
        import torch

        model = get_model()
        emb_resume = model.encode(resume_text, convert_to_tensor=True)
        emb_job = model.encode(job_description, convert_to_tensor=True)
        raw_sim = float(util.cos_sim(emb_resume, emb_job)[0][0])
        temperature = 1.5
        scaled = 1 / (1 + pow(2.718, -(raw_sim / temperature) * 10))
        return round(scaled * 35, 1)
    except Exception:
        resume_words = set(resume_text.lower().split())
        job_words = set(job_description.lower().split())
        if not job_words:
            return 0.0
        overlap = len(resume_words & job_words) / len(job_words)
        return round(min(35.0, overlap * 35.0), 1)


def compute_experience_score(resume_text: str) -> float:
    """Award points for years of experience mentions. Max 15 points."""
    patterns = [
        r"(\d+)\+?\s*years?\s*of\s*experience",
        r"(\d+)\+?\s*yrs?\s*experience",
        r"experience\s*of\s*(\d+)\+?\s*years?",
    ]
    years = 0
    for pattern in patterns:
        matches = re.findall(pattern, resume_text.lower())
        if matches:
            years = max(years, max(int(m) for m in matches))
    if years >= 8:
        return 15.0
    if years >= 5:
        return 10.0
    if years >= 3:
        return 7.0
    if years >= 1:
        return 4.0
    return 0.0


def get_job_classifier() -> Tuple[Any, Any, Optional[List[str]]]:
    global _job_classifier, _job_vectorizer, _job_categories
    if _job_classifier is None:
        model_path = Path(__file__).parent.parent / "training" / "models" / "job_classifier.pkl"
        if model_path.exists():
            with open(model_path, "rb") as f:
                data = pickle.load(f)
            _job_classifier = data["classifier"]
            _job_vectorizer = data["vectorizer"]
            _job_categories = data["categories"]
    return _job_classifier, _job_vectorizer, _job_categories


def predict_job_category(resume_text: str) -> Dict[str, Any]:
    clf, vec, categories = get_job_classifier()
    if clf is None or vec is None or not categories:
        return {"category": "Unknown", "confidence": 0.0, "top_3": []}

    try:
        X = vec.transform([resume_text.lower()])
        proba = clf.predict_proba(X)[0]
        top_idx = int(proba.argmax())
        return {
            "category": categories[top_idx],
            "confidence": round(float(proba[top_idx]) * 100, 1),
            "top_3": [
                {
                    "category": categories[i],
                    "confidence": round(float(proba[i]) * 100, 1),
                }
                for i in proba.argsort()[-3:][::-1]
            ],
        }
    except Exception:
        return {"category": "Unknown", "confidence": 0.0, "top_3": []}


def apply_length_regularization(score: float, resume_text: str) -> float:
    """Penalize very short resumes (under 100 words)."""
    word_count = len(resume_text.split())
    if word_count < 100:
        return round(score * 0.85, 1)
    return score


def score(resume_text: str, job) -> Dict[str, Union[float, str, List[str]]]:
    """
    Returns total score + breakdown out of 100.
    job must have .description and .required_skills attributes.
    """
    required_skills = getattr(job, "required_skills", "") or ""
    description = getattr(job, "description", "") or ""

    keyword_score = compute_keyword_score(resume_text, required_skills)
    semantic_score = compute_semantic_score(resume_text, description)
    experience_score = compute_experience_score(resume_text)

    format_score = 0.0
    text_lower = resume_text.lower()
    if any(w in text_lower for w in ["education", "degree", "university"]):
        format_score += 3
    if any(w in text_lower for w in ["experience", "worked", "employment"]):
        format_score += 3
    if any(w in text_lower for w in ["skill", "proficient", "expertise"]):
        format_score += 2
    if "@" in resume_text and any(w in text_lower for w in ["phone", "mobile", "contact"]):
        format_score += 2

    raw_total = keyword_score + semantic_score + experience_score + format_score
    total = apply_length_regularization(min(100.0, raw_total), resume_text)

    required = [s.strip().lower() for s in required_skills.split(",") if s.strip()]
    missing = [s for s in required if s not in resume_text.lower()]

    job_title = getattr(job, "title", "") or ""
    job_description = f"{job_title} {description} {required_skills}".strip()
    from ai.neural_classifier import get_neural_score

    neural_match = get_neural_score(resume_text, job_description)
    predicted_category = predict_job_category(resume_text)

    # Percentages for UI display (0-100).
    skill_match = round((keyword_score / 40.0) * 100.0, 1) if keyword_score else 0.0
    experience_match = (
        round((experience_score / 15.0) * 100.0, 1) if experience_score else 0.0
    )
    keyword_match = round((semantic_score / 35.0) * 100.0, 1) if semantic_score else 0.0

    return {
        "score": total,
        "keyword_score": keyword_score,
        "semantic_score": semantic_score,
        "experience_score": experience_score,
        "format_score": format_score,
        "skill_gap": missing,
        "word_count": len(resume_text.split()),
        "neural_match": neural_match,
        "predicted_category": predicted_category,
        "skill_match": skill_match,
        "experience_match": experience_match,
        "keyword_match": keyword_match,
        "breakdown_note": (
            f"keyword:{keyword_score} semantic:{semantic_score} "
            f"exp:{experience_score} fmt:{format_score}"
        ),
    }


def score_candidate(profile: Dict, job: Dict[str, str]) -> Dict[str, float | str | List[str]]:
    """Backward-compatible wrapper for existing callers."""
    resume_text = profile.get("raw_text", "")

    class _Job:
        def __init__(self, data: Dict[str, str]):
            self.title = data.get("title", "")
            self.description = data.get("description", "")
            self.required_skills = data.get("required_skills", "")

    result = score(resume_text, _Job(job))
    keyword = float(result["keyword_score"])
    semantic = float(result["semantic_score"])
    experience = float(result["experience_score"])

    # UI percentages (keep in sync with `score()` return keys)
    skill_match = float(result.get("skill_match") or 0.0)
    experience_match = float(result.get("experience_match") or 0.0)
    keyword_match = float(result.get("keyword_match") or 0.0)

    return {
        "score": result["score"],
        "keyword_score": keyword,
        "semantic_score": semantic,
        "experience_score": experience,
        "format_score": result["format_score"],
        "skill_gap": result.get("skill_gap", []),
        "skill_alignment": skill_match,
        "experience_bonus": experience_match,
        "skill_match": skill_match,
        "experience_match": experience_match,
        "keyword_match": keyword_match,
        "rationale": _build_rationale(keyword, experience, semantic),
        "neural_match": result.get("neural_match"),
        "predicted_category": result.get("predicted_category"),
        "method": "weighted_v2",
        "breakdown_note": result.get("breakdown_note", ""),
    }


def embed_text(text: str):
    """Lightweight embedding helper kept for compatibility."""
    import numpy as np

    fixed_dim = 384
    tokens = text.lower().split()
    vector = np.zeros(fixed_dim, dtype=float)
    for token in tokens:
        vector[hash(token) % fixed_dim] += 1.0
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = vector / norm
    return vector


def _build_rationale(keyword_score: float, experience_score: float, semantic_score: float) -> List[str]:
    reasons = []
    sem_pct = semantic_score / 35 * 100 if semantic_score else 0
    if sem_pct >= 65:
        reasons.append("Resume content semantically aligns with the job description.")
    elif sem_pct >= 45:
        reasons.append("Resume shows partial alignment; consider adding role-specific keywords.")
    else:
        reasons.append("Low semantic similarity; highlight relevant projects and responsibilities.")

    kw_pct = keyword_score / 40 * 100 if keyword_score else 0
    if kw_pct >= 70:
        reasons.append("Skills closely match requirements.")
    elif kw_pct >= 40:
        reasons.append("Some required skills present; add missing competencies explicitly.")
    else:
        reasons.append("Few required skills detected; update skills section to mirror job needs.")

    exp_pct = experience_score / 15 * 100 if experience_score else 0
    if exp_pct >= 50:
        reasons.append("Experience level meets or exceeds expectations.")
    else:
        reasons.append("Experience appears limited; emphasize impact and measurable outcomes.")
    return reasons
