import json

from flask import Blueprint, abort, jsonify, session

from blueprints.auth_utils import login_required, role_required
from extensions import limiter
from models import JobPosting, ResumeSubmission, db

api_bp = Blueprint("api", __name__, url_prefix="/api")


def _parse_skill_gap(raw: str | None) -> list:
    try:
        return json.loads(raw or "[]")
    except json.JSONDecodeError:
        return []


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
@limiter.limit("60 per minute", override_defaults=True)
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

    explanation = sub.explanation or {}
    scores = explanation.get("scores", {}) if isinstance(explanation, dict) else {}

    return jsonify(
        {
            "scoring_status": sub.scoring_status,
            "status": sub.status,
            "score": sub.score,
            "summary": explanation.get("llm_summary", scores.get("llm_summary", "")),
            "strengths": explanation.get("strengths", []),
            "weaknesses": explanation.get("weaknesses", []),
            "recommendation": explanation.get("recommendation", ""),
            "error": scores.get("llm_error"),
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
            "skill_gap": _parse_skill_gap(sub.skill_gap),
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
