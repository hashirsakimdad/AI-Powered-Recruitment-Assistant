from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import joblib

try:
    from sentence_transformers import SentenceTransformer, util

    _MODEL: Optional[SentenceTransformer] = None
except Exception:  # pragma: no cover - optional dependency
    SentenceTransformer = None  # type: ignore
    util = None  # type: ignore
    _MODEL = None

# Global variable to cache loaded scoring model
_SCORING_MODEL: Optional[dict] = None


def _load_model() -> Optional[SentenceTransformer]:
    """Load embedding model, preferring fine-tuned version if available."""
    global _MODEL
    if _MODEL is not None:
        return _MODEL
    
    if SentenceTransformer is None:
        return None
    
    # Try to load fine-tuned model first
    from pathlib import Path
    fine_tuned_path = Path(__file__).parent.parent / "training" / "models" / "finetuned_embedding"
    if fine_tuned_path.exists():
        try:
            _MODEL = SentenceTransformer(str(fine_tuned_path))
            return _MODEL
        except Exception as e:
            print(f"Warning: Could not load fine-tuned embedding model: {e}")
    
    # Fall back to base model
    try:
        _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        return _MODEL
    except Exception:
        return None


def embed_text(text: str) -> np.ndarray:
    model = _load_model()
    if model is None:
        # Lightweight fallback: fixed-size hash-based bag-of-words frequency vector
        # Use a fixed dimension (384) to match common embedding sizes
        FIXED_DIM = 384
        tokens = text.lower().split()
        vector = np.zeros(FIXED_DIM, dtype=float)
        for token in tokens:
            # Use hash to map token to a fixed dimension index
            idx = hash(token) % FIXED_DIM
            vector[idx] += 1.0
        # Normalize to prevent overflow
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        return vector
    try:
        return model.encode(text, convert_to_numpy=True)
    except Exception:
        # Fallback if encoding fails
        FIXED_DIM = 384
        tokens = text.lower().split()
        vector = np.zeros(FIXED_DIM, dtype=float)
        for token in tokens:
            idx = hash(token) % FIXED_DIM
            vector[idx] += 1.0
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        return vector


def _load_scoring_model() -> Optional[dict]:
    """Load the trained scoring model."""
    global _SCORING_MODEL
    if _SCORING_MODEL is not None:
        return _SCORING_MODEL
    
    model_path = Path(__file__).parent.parent / "training" / "models" / "scoring_model.pkl"
    if model_path.exists():
        try:
            _SCORING_MODEL = joblib.load(model_path)
            return _SCORING_MODEL
        except Exception as e:
            print(f"Warning: Could not load trained scoring model: {e}")
            return None
    return None


def _parse_resume_for_scoring(text: str) -> dict:
    """Parse resume text to extract features for scoring model."""
    text_lower = text.lower()
    
    # Extract skills
    skills = re.findall(r"skills?[:\s]+(.*?)(?=\n|experience|education|summary|$)", text, re.IGNORECASE | re.DOTALL)
    
    # Extract years of experience
    years_patterns = [
        r"(\d+)\s*\+?\s*(?:years?|yrs?)\s*(?:of\s*)?experience",
        r"experience[:\s]+(?:.*?)(\d+)\s*\+?\s*(?:years?|yrs?)",
        r"(\d+)\s*\+?\s*(?:years?|yrs?)"
    ]
    years_exp = 0.0
    for pattern in years_patterns:
        matches = re.findall(pattern, text_lower)
        if matches:
            try:
                years_exp = max(years_exp, float(max(matches, key=lambda x: float(x))))
            except:
                pass
    
    # Extract education level
    education_keywords = ['phd', 'doctorate', 'masters', 'bachelor', 'degree', 'diploma']
    education_level = max([i+1 for i, kw in enumerate(education_keywords) if kw in text_lower] or [0])
    
    # Extract certifications
    cert_keywords = ['certified', 'certification', 'certificate', 'license', 'licensed']
    has_certifications = 1 if any(kw in text_lower for kw in cert_keywords) else 0
    
    # Count technical terms
    tech_terms = ['python', 'java', 'javascript', 'sql', 'react', 'node', 'aws', 'docker', 
                  'machine learning', 'ai', 'data science', 'algorithm', 'api', 'database']
    tech_term_count = sum(1 for term in tech_terms if term in text_lower)
    
    return {
        'skills': skills,
        'years_experience': years_exp,
        'education_level': education_level,
        'has_certifications': has_certifications,
        'tech_term_count': tech_term_count
    }


def _extract_features_for_scoring(resume_text: str, job_description: str, required_skills: str) -> Optional[np.ndarray]:
    """Extract features using the same method as training."""
    parsed = _parse_resume_for_scoring(resume_text)
    
    # Use embedding model for semantic similarity
    resume_vec = embed_text(resume_text[:2000])
    job_text = f"{job_description} {required_skills}"
    job_vec = embed_text(job_text)
    
    # Cosine similarity
    dot_product = np.dot(resume_vec, job_vec)
    norm_resume = np.linalg.norm(resume_vec)
    norm_job = np.linalg.norm(job_vec)
    semantic_sim = dot_product / (norm_resume * norm_job + 1e-8)
    
    # Skill matching - include both explicit and inferred skills
    resume_skills = set()
    for skill_line in parsed.get('skills', []):
        for token in skill_line.split(','):
            token = token.strip().lower()
            if token and len(token) > 2:
                resume_skills.add(token)
    
    # Add inferred skills if available in parsed data
    if isinstance(parsed, dict) and 'inferred_skills' in parsed:
        for skill in parsed.get('inferred_skills', []):
            skill_lower = skill.strip().lower()
            if skill_lower and len(skill_lower) > 2:
                resume_skills.add(skill_lower)
    
    job_skills = {s.strip().lower() for s in required_skills.split(',') if s.strip()}
    skill_overlap = len(resume_skills.intersection(job_skills)) / max(len(job_skills), 1) if job_skills else 0
    
    # Experience features
    years_exp = parsed.get('years_experience', 0)
    exp_normalized = min(years_exp / 10.0, 1.0)
    exp_squared = exp_normalized ** 2
    
    # Text length features
    resume_length = len(resume_text)
    job_length = len(job_description)
    length_ratio = resume_length / max(job_length, 1)
    length_log_ratio = np.log1p(resume_length) / max(np.log1p(job_length), 1)
    
    # Additional features
    education_level = parsed.get('education_level', 0) / 5.0
    has_certifications = parsed.get('has_certifications', 0)
    tech_term_count = parsed.get('tech_term_count', 0) / 10.0
    
    # Skill count features
    resume_skill_count = len(resume_skills)
    job_skill_count = len(job_skills)
    skill_count_ratio = resume_skill_count / max(job_skill_count, 1)
    
    # Word overlap
    resume_words = set(resume_text.lower().split())
    job_words = set(job_text.lower().split())
    word_overlap = len(resume_words.intersection(job_words)) / max(len(job_words), 1)
    
    return np.array([
        semantic_sim,
        skill_overlap,
        exp_normalized,
        exp_squared,
        length_ratio,
        length_log_ratio,
        education_level,
        has_certifications,
        tech_term_count,
        resume_skill_count / 20.0,
        job_skill_count / 10.0,
        skill_count_ratio,
        word_overlap,
        years_exp / 20.0,
    ])


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    if vec_a.size == 0 or vec_b.size == 0:
        return 0.0
    # Ensure vectors have the same shape
    if vec_a.shape != vec_b.shape:
        # If shapes don't match, pad or truncate to the smaller size
        min_size = min(vec_a.size, vec_b.size)
        vec_a = vec_a.flatten()[:min_size]
        vec_b = vec_b.flatten()[:min_size]
    denom = np.linalg.norm(vec_a) * np.linalg.norm(vec_b)
    if denom == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / denom)


def score_candidate(profile: Dict, job: Dict[str, str]) -> Dict[str, float | str | List[str]]:
    """
    Score candidate using trained ML model if available, otherwise use weighted formula.
    """
    resume_text = profile.get("raw_text", "")
    job_description = job.get('description', '')
    job_title = job.get('title', '')
    required_skills = job.get('required_skills', '')
    job_text = f"{job_title}. {job_description}. {required_skills}"

    # Try to use trained scoring model first
    model_data = _load_scoring_model()
    if model_data is not None:
        try:
            model = model_data.get('model')
            scaler = model_data.get('scaler')
            use_scaler = model_data.get('use_scaler', False)
            
            if model:
                # Extract features using same method as training
                features = _extract_features_for_scoring(resume_text, job_description, required_skills)
                if features is not None:
                    # Scale if needed
                    if use_scaler and scaler:
                        features = scaler.transform(features.reshape(1, -1))
                    else:
                        features = features.reshape(1, -1)
                    
                    # Predict score (0-1 range)
                    predicted_score = float(model.predict(features)[0])
                    predicted_score = max(0.0, min(1.0, predicted_score))  # Clamp to [0, 1]
                    
                    # Extract components for breakdown
                    semantic_score = float(features[0][0]) if features.shape[1] > 0 else 0.0
                    skill_overlap = float(features[0][1]) if features.shape[1] > 1 else 0.0
                    exp_normalized = float(features[0][2]) if features.shape[1] > 2 else 0.0
                    
                    final_score = round(predicted_score * 100, 2)
                    
                    return {
                        "score": final_score,
                        "semantic_score": round(semantic_score * 100, 2),
                        "skill_alignment": round(skill_overlap * 100, 2),
                        "experience_bonus": round(exp_normalized * 100, 2),
                        "rationale": _build_rationale(skill_overlap, exp_normalized, semantic_score),
                        "method": "ml_model"
                    }
        except Exception as e:
            print(f"Warning: Trained scoring model failed, using fallback: {e}")
    
    # Fallback to weighted formula (original method)
    resume_vec = embed_text(resume_text)
    job_vec = embed_text(job_text)
    semantic_score = cosine_similarity(resume_vec, job_vec)

    # Use both explicit and inferred skills for matching
    inferred_skills = profile.get("inferred_skills", [])
    skill_matches = _match_skills(profile.get("skills", []), required_skills, inferred_skills)
    experience_bonus = min(profile.get("years_experience", 0), 10) / 10

    weighted_score = 0.55 * semantic_score + 0.30 * skill_matches + 0.15 * experience_bonus
    final_score = round(weighted_score * 100, 2)

    return {
        "score": final_score,
        "semantic_score": round(semantic_score * 100, 2),
        "skill_alignment": round(skill_matches * 100, 2),
        "experience_bonus": round(experience_bonus * 100, 2),
        "rationale": _build_rationale(skill_matches, experience_bonus, semantic_score),
        "method": "weighted_formula"
    }


def _match_skills(resume_skills: List[str], job_skill_text: str, inferred_skills: List[str] = None) -> float:
    """
    Match skills including both explicit and inferred skills.
    
    Args:
        resume_skills: Explicitly listed skills
        job_skill_text: Required skills from job posting
        inferred_skills: Skills inferred from experience/projects
    """
    job_skills = {skill.strip().lower() for skill in job_skill_text.split(",") if skill.strip()}
    if not job_skills:
        return 0.5  # neutral when job skills unspecified
    
    # Build resume skill set from explicit skills
    resume_set = set()
    for line in resume_skills:
        for token in line.split(","):
            token = token.strip().lower()
            if token:
                resume_set.add(token)
    
    # Add inferred skills
    if inferred_skills:
        for skill in inferred_skills:
            skill_lower = skill.strip().lower()
            if skill_lower:
                resume_set.add(skill_lower)
    
    if not resume_set:
        return 0.0
    
    overlap = job_skills.intersection(resume_set)
    return len(overlap) / len(job_skills)


def _build_rationale(skill_matches: float, exp_bonus: float, semantic: float) -> List[str]:
    reasons = []
    if semantic >= 0.65:
        reasons.append("Resume content semantically aligns with the job description.")
    elif semantic >= 0.45:
        reasons.append("Resume shows partial alignment; consider adding role-specific keywords.")
    else:
        reasons.append("Low semantic similarity; highlight relevant projects and responsibilities.")

    if skill_matches >= 0.7:
        reasons.append("Skills closely match requirements.")
    elif skill_matches >= 0.4:
        reasons.append("Some required skills present; add missing competencies explicitly.")
    else:
        reasons.append("Few required skills detected; update skills section to mirror job needs.")

    if exp_bonus >= 0.5:
        reasons.append("Experience level meets or exceeds expectations.")
    else:
        reasons.append("Experience appears limited; emphasize impact and measurable outcomes.")
    return reasons

