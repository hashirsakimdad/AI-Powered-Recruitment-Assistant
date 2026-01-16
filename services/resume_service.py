from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

from werkzeug.utils import secure_filename

from ai import extract_text, parse_resume, score_candidate, generate_feedback
from ai.resume_detector import validate_resume_document
from models import JobPosting, ResumeSubmission, db


def allowed_file(filename: str, allowed_extensions: set[str]) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def handle_upload(file_storage, upload_dir: str, allowed_extensions: set[str]) -> Path:
    filename = secure_filename(file_storage.filename)
    if not allowed_file(filename, allowed_extensions):
        raise ValueError("Invalid file type. Only PDF and DOCX are allowed.")
    destination = Path(upload_dir) / filename
    file_storage.save(destination)
    return destination


def process_resume(
    resume_path: Path, job: JobPosting
) -> Tuple[dict, dict, ResumeSubmission]:
    """
    Process resume with resume detection layer.
    Raises ValueError if document is not a valid resume.
    """
    # Step 1: Extract text
    text = extract_text(str(resume_path))
    
    # Step 2: Resume Detection Layer - validate if document is a resume
    is_valid, error_message = validate_resume_document(text)
    if not is_valid:
        raise ValueError(error_message)
    
    # Step 3: Parse resume (existing analyzer logic - unchanged)
    parsed_profile = parse_resume(text)
    
    # Step 4: Infer skills from experience/projects
    from ai.skill_inference import combine_explicit_and_inferred_skills
    skill_data = combine_explicit_and_inferred_skills(
        parsed_profile.get("skills", []),
        text
    )
    # Update parsed profile with skill inference data
    parsed_profile["all_skills"] = skill_data["all_skills"]
    parsed_profile["explicit_skills"] = skill_data["explicit_skills"]
    parsed_profile["inferred_skills"] = skill_data["inferred_skills"]
    
    # Step 5: Get detection details for storage
    from ai.resume_detector import detect_resume
    _, detection_details = detect_resume(text)
    
    # Step 6: Score and generate feedback (existing analyzer logic - unchanged)
    job_payload = {
        "title": job.title,
        "description": job.description,
        "required_skills": job.required_skills,
    }
    scoring = score_candidate(parsed_profile, job_payload)
    feedback = generate_feedback(parsed_profile, job_payload)
    
    # Step 7: Store feedback history
    feedback_history = [{
        "timestamp": datetime.utcnow().isoformat(),
        "feedback": feedback,
        "score": scoring["score"],
    }]

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
    db.session.add(submission)
    db.session.commit()
    return parsed_profile, scoring, submission

