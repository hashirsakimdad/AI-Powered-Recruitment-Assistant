from datetime import datetime
from pathlib import Path

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)

from app_helpers import clean_text, get_score_percentile
from blueprints.auth_utils import role_required
from extensions import limiter
from models import JobPosting, ResumeSubmission, User, db
from services.resume_service import (
    create_pending_submission,
    handle_upload,
    start_background_scoring,
)
from utils.job_utils import get_filtered_jobs

candidate_bp = Blueprint("candidate", __name__, url_prefix="/candidate")


@candidate_bp.route("/dashboard")
@role_required("candidate")
def dashboard():
    query = clean_text(request.args.get("q", ""))
    job_type = clean_text(request.args.get("job_type", ""))
    work_mode = clean_text(request.args.get("work_mode", ""))
    page = request.args.get("page", 1, type=int)

    jobs_query = get_filtered_jobs(query, job_type, work_mode)
    jobs = jobs_query.paginate(page=page, per_page=20, error_out=False)
    user_id = session["user_id"]
    my_submissions = ResumeSubmission.query.filter_by(candidate_id=user_id).all()
    percentiles = {
        sub.id: get_score_percentile(sub.id, sub.job_id) for sub in my_submissions
    }

    return render_template(
        "candidate_dashboard.html",
        jobs=jobs.items,
        jobs_pagination=jobs,
        submissions=my_submissions,
        search_query=query,
        selected_job_type=job_type,
        selected_work_mode=work_mode,
        percentiles=percentiles,
    )


@candidate_bp.route("/upload/<int:job_id>", methods=["POST"])
@role_required("candidate")
@limiter.limit("5 per minute", methods=["POST"])
def upload_resume(job_id):
    job = db.session.get(JobPosting, job_id)
    if job is None:
        abort(404)

    if not job.is_active or (job.expires_at and job.expires_at < datetime.utcnow()):
        flash("This job is no longer accepting applications.", "warning")
        return redirect(url_for("candidate.dashboard"))

    user_id = session["user_id"]
    existing = ResumeSubmission.query.filter_by(
        candidate_id=user_id, job_id=job_id
    ).first()
    if existing:
        flash(
            "You have already applied to this job. Check your dashboard for your score.",
            "info",
        )
        return redirect(url_for("candidate.dashboard"))

    file = request.files.get("resume")
    if not file:
        flash("No file uploaded", "danger")
        return redirect(url_for("candidate.dashboard"))
    try:
        dest = handle_upload(
            file,
            current_app.config["UPLOAD_FOLDER"],
            current_app.config["ALLOWED_EXTENSIONS"],
        )
        submission = create_pending_submission(
            dest,
            job,
            user_id,
            clean_text(request.form.get("name", "Candidate")),
            clean_text(request.form.get("email", "unknown@example.com")),
        )
        start_background_scoring(current_app._get_current_object(), submission, dest, job)
        flash("Resume uploaded. Scoring in progress...", "success")
    except ValueError as exc:
        flash(f"Upload failed: {exc}", "danger")
    except Exception as exc:
        flash(f"Upload failed: {exc}", "danger")
    return redirect(url_for("candidate.dashboard"))


@candidate_bp.route("/jobs/<int:job_id>")
@role_required("candidate")
def job_details(job_id):
    job = db.session.get(JobPosting, job_id)
    if job is None:
        abort(404)
    return render_template("job_details.html", job=job)


@candidate_bp.route("/profile")
@role_required("candidate")
def profile():
    user = db.session.get(User, session["user_id"])
    if user is None:
        abort(404)
    submissions = (
        ResumeSubmission.query.filter_by(candidate_id=user.id)
        .order_by(ResumeSubmission.created_at.desc())
        .all()
    )
    scored = [s for s in submissions if s.score is not None]
    avg_score = sum(s.score for s in scored) / len(scored) if scored else 0
    return render_template(
        "candidate_profile.html",
        user=user,
        submissions=submissions,
        total_applications=len(submissions),
        average_score=round(avg_score, 1),
        shortlisted_count=sum(1 for s in submissions if s.status == "shortlisted"),
        selected_count=sum(1 for s in submissions if s.status == "selected"),
    )


@candidate_bp.route("/submission/<int:submission_id>/download")
@role_required("candidate")
def download_resume(submission_id):
    submission = db.session.get(ResumeSubmission, submission_id)
    if submission is None:
        abort(404)
    if submission.candidate_id != session["user_id"]:
        abort(403)

    file_path = Path(submission.file_path)
    if not file_path.exists():
        flash("Resume file no longer exists on server.", "warning")
        return redirect(url_for("candidate.profile"))

    return send_file(
        file_path,
        as_attachment=True,
        download_name=f"resume_{submission.id}{file_path.suffix}",
    )
