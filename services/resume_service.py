import json
import logging
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

from werkzeug.utils import secure_filename

from ai import extract_text, generate_feedback, parse_resume, score_candidate
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
    """Save and validate an uploaded resume file.

    Args:
        file_storage: Werkzeug FileStorage from the request.
        upload_dir: Directory path for stored uploads.
        allowed_extensions: Permitted file extensions.

    Returns:
        Path to the saved file.

    Raises:
        ValueError: If the file type is not allowed or MIME validation fails.
    """
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


def create_pending_submission(
    resume_path: Path,
    job: JobPosting,
    candidate_id: int,
    candidate_name: str,
    email: str,
) -> ResumeSubmission:
    """Create a submission record in processing state before background scoring."""
    submission = ResumeSubmission(
        candidate_name=candidate_name,
        email=email,
        file_path=str(resume_path),
        job_id=job.id,
        candidate_id=candidate_id,
        scoring_status="processing",
        status="pending",
    )
    db.session.add(submission)
    db.session.commit()
    return submission


def score_in_background(app, submission_id: int, file_path: str, job_id: int) -> None:
    """Run AI scoring in a background thread with app context."""
    with app.app_context():
        submission = db.session.get(ResumeSubmission, submission_id)
        job = db.session.get(JobPosting, job_id)
        if not submission or not job:
            return
        try:
            process_resume(Path(file_path), job, submission=submission)
            submission.scoring_status = "scored"
            db.session.commit()
        except Exception:
            logger.exception(
                "Background scoring failed for submission_id=%s job_id=%s",
                submission_id,
                job_id,
            )
            submission.scoring_status = "failed"
            db.session.commit()


def rescore_in_background(app, submission_id: int, job_id: int) -> None:
    """Re-score a submission in a background thread."""
    with app.app_context():
        submission = db.session.get(ResumeSubmission, submission_id)
        job = db.session.get(JobPosting, job_id)
        if not submission or not job:
            return
        try:
            rescore_submission(submission, job)
            db.session.commit()
        except Exception:
            logger.exception(
                "Background re-score failed for submission_id=%s job_id=%s",
                submission_id,
                job_id,
            )
            submission.scoring_status = "failed"
            db.session.commit()


def start_background_scoring(app, submission: ResumeSubmission, dest: Path, job: JobPosting) -> None:
    """Launch background thread for resume scoring."""
    thread = threading.Thread(
        target=score_in_background,
        args=(app._get_current_object(), submission.id, str(dest), job.id),
        daemon=True,
    )
    thread.start()


def process_resume(
    resume_path: Path,
    job: JobPosting,
    submission: Optional[ResumeSubmission] = None,
) -> Tuple[dict, dict, ResumeSubmission]:
    """Parse and score a resume, updating or creating a submission record.

    Args:
        resume_path: Absolute path to the uploaded resume.
        job: Job posting to score against.
        submission: Optional existing submission to update.

    Returns:
        Tuple of (parsed_profile, scoring dict, submission).

    Raises:
        ValueError: If the document is not a valid resume.
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

    explanation = {
        "scores": scoring,
        "feedback": feedback,
        "skill_match": scoring.get("skill_match", scoring.get("skill_alignment", 0)),
        "experience_match": scoring.get(
            "experience_match", scoring.get("experience_bonus", 0)
        ),
        "keyword_match": scoring.get("keyword_match", 0),
        "rationale": scoring.get("rationale", []),
    }

    if submission is None:
        logger.warning(
            "process_resume called without submission for job_id=%s path=%s",
            job.id,
            resume_path,
        )
        raise ValueError(
            "A submission record is required before scoring; use create_pending_submission first."
        )

    submission.file_path = str(resume_path)
    submission.parsed_summary = parsed_profile
    submission.explanation = explanation
    submission.is_resume_valid = True
    submission.detection_details = detection_details
    submission.feedback_history = feedback_history
    submission.explicit_skills = skill_data["explicit_skills"]
    submission.inferred_skills = skill_data["inferred_skills"]
    _apply_scoring_to_submission(submission, scoring)
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
    submission.explanation = {
        "scores": scoring,
        "feedback": feedback,
        "skill_match": scoring.get("skill_match", scoring.get("skill_alignment", 0)),
        "experience_match": scoring.get(
            "experience_match", scoring.get("experience_bonus", 0)
        ),
        "keyword_match": scoring.get("keyword_match", 0),
        "rationale": scoring.get("rationale", []),
    }
    _apply_scoring_to_submission(submission, scoring)
    submission.scoring_status = "scored"
    return scoring
