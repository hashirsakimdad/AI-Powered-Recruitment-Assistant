import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

from werkzeug.utils import secure_filename

from ai import extract_text, parse_resume, score_candidate, generate_feedback
from ai.resume_detector import validate_resume_document
from models import JobPosting, ResumeSubmission, db


def allowed_file(filename: str, allowed_extensions: set[str]) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def validate_mime_type(filepath: Path) -> None:
    """Validate uploaded file MIME type. Removes file and raises on failure."""
    allowed_mimes = {
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    mime = None
    try:
        import magic

        mime = magic.from_file(str(filepath), mime=True)
    except Exception:
        import mimetypes

        mime, _ = mimetypes.guess_type(str(filepath))

    if mime not in allowed_mimes:
        if filepath.exists():
            os.remove(filepath)
        raise ValueError(
            f"Invalid file type: {mime}. Only PDF and Word documents are accepted."
        )


def handle_upload(file_storage, upload_dir: str, allowed_extensions: set[str]) -> Path:
    filename = secure_filename(file_storage.filename)
    if not allowed_file(filename, allowed_extensions):
        raise ValueError("Invalid file type. Only PDF and Word documents are allowed.")
    destination = Path(upload_dir) / filename
    file_storage.save(destination)
    validate_mime_type(destination)
    return destination


def _apply_scoring_to_submission(submission: ResumeSubmission, scoring: dict) -> None:
    submission.score = scoring.get("score")
    submission.keyword_score = scoring.get("keyword_score", 0.0)
    submission.semantic_score = scoring.get("semantic_score", 0.0)
    submission.experience_score = scoring.get("experience_score", 0.0)
    submission.format_score = scoring.get("format_score", 0.0)
    submission.skill_gap = json.dumps(scoring.get("skill_gap", []))


def process_resume(
    resume_path: Path, job: JobPosting
) -> Tuple[dict, dict, ResumeSubmission]:
    """
    Process resume with resume detection layer.
    Raises ValueError if document is not a valid resume.
    """
    text = extract_text(str(resume_path))

    is_valid, error_message = validate_resume_document(text)
    if not is_valid:
        raise ValueError(error_message)

    parsed_profile = parse_resume(text)

    from ai.skill_inference import combine_explicit_and_inferred_skills

    skill_data = combine_explicit_and_inferred_skills(
        parsed_profile.get("skills", []),
        text,
    )
    parsed_profile["all_skills"] = skill_data["all_skills"]
    parsed_profile["explicit_skills"] = skill_data["explicit_skills"]
    parsed_profile["inferred_skills"] = skill_data["inferred_skills"]

    from ai.resume_detector import detect_resume

    _, detection_details = detect_resume(text)

    job_payload = {
        "title": job.title,
        "description": job.description,
        "required_skills": job.required_skills,
    }
    scoring = score_candidate(parsed_profile, job_payload)
    feedback = generate_feedback(parsed_profile, job_payload)

    feedback_history = [
        {
            "timestamp": datetime.utcnow().isoformat(),
            "feedback": feedback,
            "score": scoring["score"],
        }
    ]

    submission = ResumeSubmission(
        candidate_name="N/A",
        email="unknown@example.com",
        file_path=str(resume_path),
        parsed_summary=parsed_profile,
        score=scoring["score"],
        explanation={
            "scores": scoring,
            "feedback": feedback,
        },
        job_id=job.id,
        is_resume_valid=True,
        detection_details=detection_details,
        feedback_history=feedback_history,
        explicit_skills=skill_data["explicit_skills"],
        inferred_skills=skill_data["inferred_skills"],
        status="pending",
    )
    _apply_scoring_to_submission(submission, scoring)
    db.session.add(submission)
    db.session.commit()
    return parsed_profile, scoring, submission


def rescore_submission(submission: ResumeSubmission, job: JobPosting) -> dict:
    """Re-parse and re-score an existing submission from its stored file."""
    resume_path = Path(submission.file_path)
    if not resume_path.exists():
        raise FileNotFoundError(f"Resume file missing: {resume_path}")

    text = extract_text(str(resume_path))
    parsed_profile = parse_resume(text)
    job_payload = {
        "title": job.title,
        "description": job.description,
        "required_skills": job.required_skills,
    }
    scoring = score_candidate(parsed_profile, job_payload)
    feedback = generate_feedback(parsed_profile, job_payload)
    submission.parsed_summary = parsed_profile
    submission.explanation = {"scores": scoring, "feedback": feedback}
    _apply_scoring_to_submission(submission, scoring)
    return scoring
