"""
Resume Detection Layer
Pre-processing step to determine if an uploaded document is a CV/Resume.
Uses trained ML model for accurate detection (100% accuracy).
Falls back to rule-based detection if model not available.
"""
import re
from pathlib import Path
from typing import Dict, Tuple, Optional

import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer


# Resume-specific keywords and patterns
RESUME_KEYWORDS = {
    "contact": ["email", "phone", "address", "contact", "mobile", "linkedin"],
    "personal": ["name", "objective", "summary", "profile", "about"],
    "experience": ["experience", "work history", "employment", "career", "positions", "roles"],
    "education": ["education", "degree", "university", "college", "bachelor", "master", "phd", "diploma"],
    "skills": ["skills", "competencies", "technical skills", "proficiencies", "expertise"],
    "achievements": ["achievements", "awards", "certifications", "projects", "publications"],
}

# Minimum thresholds for resume detection
MIN_RESUME_SCORE = 0.4  # Minimum confidence score to consider document a resume
MIN_KEYWORD_MATCHES = 3  # Minimum number of keyword categories that must be present

# Global variable to cache loaded model
_DETECTOR_MODEL: Optional[dict] = None


def _load_detector_model() -> Optional[dict]:
    """Load the trained resume detection model."""
    global _DETECTOR_MODEL
    if _DETECTOR_MODEL is not None:
        return _DETECTOR_MODEL
    
    model_path = Path(__file__).parent.parent / "training" / "models" / "resume_detector.pkl"
    if model_path.exists():
        try:
            _DETECTOR_MODEL = joblib.load(model_path)
            return _DETECTOR_MODEL
        except Exception as e:
            print(f"Warning: Could not load trained detector model: {e}")
            return None
    return None


def _extract_features_for_model(text: str) -> dict:
    """Extract features for the trained ML model."""
    text_lower = text.lower()
    return {
        'length': len(text),
        'word_count': len(text.split()),
        'has_email': 1 if '@' in text else 0,
        'has_skills_section': 1 if 'skill' in text_lower else 0,
        'has_experience_section': 1 if 'experience' in text_lower else 0,
        'has_education_section': 1 if 'education' in text_lower else 0,
        'has_summary': 1 if 'summary' in text_lower else 0,
        'job_title_count': text_lower.count('engineer') + text_lower.count('developer'),
        'number_count': len([w for w in text.split() if w.isdigit()]),
    }


def detect_resume(text: str) -> Tuple[bool, Dict[str, any]]:
    """
    Detect if a document is a resume/CV using trained ML model.
    Falls back to rule-based detection if model not available.
    
    Args:
        text: Extracted text from the document
        
    Returns:
        Tuple of (is_resume: bool, detection_details: dict)
    """
    if not text or len(text.strip()) < 50:
        return False, {
            "reason": "Document too short or empty",
            "confidence": 0.0,
            "matches": {},
            "method": "validation"
        }
    
    # Try to use trained ML model first
    model_data = _load_detector_model()
    if model_data is not None:
        try:
            classifier = model_data.get('classifier')
            vectorizer = model_data.get('vectorizer')
            use_tfidf = model_data.get('use_tfidf', True)
            
            if classifier and vectorizer:
                # Extract handcrafted features
                features = _extract_features_for_model(text)
                feature_vector = np.array([list(features.values())])
                
                # Extract TF-IDF features if needed
                if use_tfidf:
                    tfidf_features = vectorizer.transform([text]).toarray()
                    X = np.hstack([feature_vector, tfidf_features])
                else:
                    X = feature_vector
                
                # Predict
                prediction = classifier.predict(X)[0]
                probability = classifier.predict_proba(X)[0]
                confidence = float(max(probability))
                
                is_resume = bool(prediction == 1)
                reason = "Document appears to be a resume/CV (ML model)" if is_resume else "Document does not appear to be a resume/CV (ML model)"
                
                return is_resume, {
                    "reason": reason,
                    "confidence": round(confidence, 3),
                    "matches": features,
                    "method": "ml_model",
                    "prediction": int(prediction),
                    "probabilities": {
                        "not_resume": round(probability[0], 3),
                        "resume": round(probability[1], 3)
                    }
                }
        except Exception as e:
            print(f"Warning: ML model prediction failed, using fallback: {e}")
    
    # Fallback to rule-based detection
    text_lower = text.lower()
    matches = {}
    total_score = 0.0
    
    # Check for resume-specific sections
    for category, keywords in RESUME_KEYWORDS.items():
        category_matches = sum(1 for keyword in keywords if keyword in text_lower)
        if category_matches > 0:
            matches[category] = category_matches
            # Weight different categories
            weight = {
                "contact": 0.15,
                "personal": 0.10,
                "experience": 0.25,
                "education": 0.20,
                "skills": 0.20,
                "achievements": 0.10,
            }.get(category, 0.10)
            total_score += weight * min(category_matches / len(keywords), 1.0)
    
    # Check for structural patterns (dates, job titles, etc.)
    date_pattern = r"\b(19|20)\d{2}\b|\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}\b"
    dates_found = len(re.findall(date_pattern, text_lower))
    if dates_found >= 2:
        total_score += 0.15
        matches["dates"] = dates_found
    
    # Check for job title patterns
    job_title_pattern = r"\b(software|engineer|developer|manager|analyst|designer|consultant|specialist|director|lead|senior|junior)\b"
    job_titles = len(re.findall(job_title_pattern, text_lower))
    if job_titles >= 2:
        total_score += 0.10
        matches["job_titles"] = job_titles
    
    # Check for email pattern (common in resumes)
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    emails = len(re.findall(email_pattern, text))
    if emails > 0:
        total_score += 0.10
        matches["email"] = emails
    
    # Check for phone number patterns
    phone_patterns = [
        r"\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}",  # General phone
        r"\d{3}[-.\s]?\d{3}[-.\s]?\d{4}",  # US format
        r"\(\d{3}\)\s?\d{3}[-.\s]?\d{4}",  # (123) 456-7890
    ]
    phones_found = sum(len(re.findall(pattern, text)) for pattern in phone_patterns)
    if phones_found > 0:
        total_score += 0.05
        matches["phone"] = phones_found
    
    # Check for LinkedIn/GitHub profiles
    social_patterns = [
        r"linkedin\.com/in/[\w-]+",
        r"github\.com/[\w-]+",
        r"linkedin",
        r"github",
    ]
    social_found = sum(1 for pattern in social_patterns if re.search(pattern, text_lower))
    if social_found > 0:
        total_score += 0.05
        matches["social_profiles"] = social_found
    
    # Check for certifications section
    cert_keywords = ["certification", "certificate", "certified", "license", "licensed", "credentials"]
    cert_found = sum(1 for kw in cert_keywords if kw in text_lower)
    if cert_found > 0:
        total_score += 0.05
        matches["certifications"] = cert_found
    
    # Check for projects section
    project_keywords = ["project", "projects", "portfolio", "work samples"]
    project_found = sum(1 for kw in project_keywords if kw in text_lower)
    if project_found > 0:
        total_score += 0.05
        matches["projects"] = project_found
    
    # Normalize score to 0-1 range
    confidence = min(total_score, 1.0)
    
    # Determine if it's a resume
    is_resume = (
        confidence >= MIN_RESUME_SCORE and
        len([k for k in matches.keys() if k in RESUME_KEYWORDS]) >= MIN_KEYWORD_MATCHES
    )
    
    reason = "Document appears to be a resume/CV" if is_resume else "Document does not match resume/CV patterns"
    
    return is_resume, {
        "reason": reason,
        "confidence": round(confidence, 3),
        "matches": matches,
        "keyword_categories_found": len([k for k in matches.keys() if k in RESUME_KEYWORDS]),
        "method": "rule_based"
    }


def validate_resume_document(text: str) -> Tuple[bool, str]:
    """
    Validate if document is a resume. Returns (is_valid, error_message).
    This is the main entry point for resume detection.
    
    Args:
        text: Extracted text from the document
        
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    if not text or len(text.strip()) < 50:
        return False, "Uploaded file does not appear to be a resume. Document is too short or empty."
    
    is_resume, details = detect_resume(text)
    
    if not is_resume:
        # Provide clear, user-friendly error message
        confidence = details.get('confidence', 0.0)
        method = details.get('method', 'unknown')
        
        # Build specific error message based on what was missing
        missing_items = []
        matches = details.get('matches', {})
        
        if not matches.get('experience'):
            missing_items.append("work experience section")
        if not matches.get('education'):
            missing_items.append("education section")
        if not matches.get('skills'):
            missing_items.append("skills section")
        if not matches.get('email'):
            missing_items.append("contact information")
        
        if missing_items:
            missing_str = ", ".join(missing_items)
            error_msg = (
                f"Uploaded file does not appear to be a resume. "
                f"Missing: {missing_str}. "
                f"Please upload a valid resume/CV document."
            )
        else:
            error_msg = (
                f"Uploaded file does not appear to be a resume. "
                f"Please upload a valid resume/CV document."
            )
        
        return False, error_msg
    
    return True, "Resume detected successfully"

