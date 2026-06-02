import json

from flask import Blueprint, abort, jsonify, session

from blueprints.auth_utils import login_required, role_required
from models import JobPosting, ResumeSubmission, db

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/job/<int:job_id>/submissions")
@role_required("recruiter")
def api_submissions(job_id):
    job = JobPosting.query.filter_by(
        id=job_id, recruiter_id=session["user_id"]
    ).first()
    if job is None:
        abort(404)
    payload = [sub.as_dict() for sub in job.submissions]
    return jsonify(payload)


@api_bp.route("/submission/<int:submission_id>/status")
@login_required
def submission_status(submission_id):
    sub = db.session.get(ResumeSubmission, submission_id)
    if sub is None:
        abort(404)
    job = db.session.get(JobPosting, sub.job_id)
    if session.get("role") == "recruiter":
        if not job or job.recruiter_id != session["user_id"]:
            return jsonify({"error": "Unauthorized"}), 403
    elif session.get("role") == "candidate":
        if sub.candidate_id != session["user_id"]:
            return jsonify({"error": "Unauthorized"}), 403
    else:
        return jsonify({"error": "Unauthorized"}), 403

    return jsonify(
        {
            "status": sub.scoring_status,
            "score": sub.score,
            "application_status": sub.status,
        }
    )


@api_bp.route("/submission/<int:submission_id>/breakdown")
@login_required
def submission_breakdown(submission_id):
    sub = db.session.get(ResumeSubmission, submission_id)
    if sub is None:
        abort(404)
    job = db.session.get(JobPosting, sub.job_id)
    if session.get("role") == "recruiter":
        if not job or job.recruiter_id != session["user_id"]:
            return jsonify({"error": "Unauthorized"}), 403
    elif session.get("role") == "candidate":
        if sub.candidate_id != session["user_id"]:
            return jsonify({"error": "Unauthorized"}), 403
    else:
        return jsonify({"error": "Unauthorized"}), 403

    explanation = sub.explanation or {}
    scores = explanation.get("scores", {}) if isinstance(explanation, dict) else {}

    return jsonify(
        {
            "id": sub.id,
            "candidate_name": sub.candidate_name,
            "total_score": sub.score,
            "keyword_score": sub.keyword_score,
            "semantic_score": sub.semantic_score,
            "experience_score": sub.experience_score,
            "format_score": sub.format_score,
            "skill_gap": json.loads(sub.skill_gap or "[]"),
            "skill_match": explanation.get("skill_match", scores.get("skill_match")),
            "experience_match": explanation.get(
                "experience_match", scores.get("experience_match")
            ),
            "keyword_match": explanation.get(
                "keyword_match", scores.get("keyword_match")
            ),
            "rationale": explanation.get("rationale", scores.get("rationale", [])),
        }
    )
