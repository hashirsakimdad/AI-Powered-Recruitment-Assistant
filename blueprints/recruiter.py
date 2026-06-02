import json
from collections import Counter
from datetime import datetime
from io import BytesIO, StringIO
import csv

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from sqlalchemy import desc, nullslast

from app_helpers import clean_text
from blueprints.auth_utils import role_required
from extensions import limiter
from models import JobPosting, ResumeSubmission, db
from services.email_service import notify_candidate
from services.resume_service import rescore_submission

recruiter_bp = Blueprint("recruiter", __name__, url_prefix="/recruiter")


@recruiter_bp.route("/dashboard")
@role_required("recruiter")
def dashboard():
    user_id = session["user_id"]
    jobs = JobPosting.query.filter_by(recruiter_id=user_id).all()
    page = request.args.get("page", 1, type=int)
    submissions = (
        ResumeSubmission.query.join(JobPosting)
        .filter(JobPosting.recruiter_id == user_id)
        .order_by(nullslast(desc(ResumeSubmission.score)))
        .paginate(page=page, per_page=20, error_out=False)
    )
    return render_template(
        "recruiter_dashboard.html",
        jobs=jobs,
        submissions=submissions.items,
        pagination=submissions,
    )


@recruiter_bp.route("/analytics")
@role_required("recruiter")
def analytics():
    user_id = session["user_id"]
    jobs = JobPosting.query.filter_by(recruiter_id=user_id).all()
    submissions = (
        ResumeSubmission.query.join(JobPosting)
        .filter(JobPosting.recruiter_id == user_id)
        .all()
    )
    buckets = [0, 0, 0, 0, 0]
    for sub in submissions:
        s = sub.score or 0
        idx = min(int(s // 20), 4)
        buckets[idx] += 1
    apps_per_job = {j.title: len(j.submissions) for j in jobs}
    skill_gaps = Counter()
    for sub in submissions:
        gaps = json.loads(sub.skill_gap or "[]")
        skill_gaps.update(gaps)
    top_gaps = skill_gaps.most_common(8)
    return render_template(
        "recruiter_analytics.html",
        jobs=jobs,
        submissions=submissions,
        score_buckets=buckets,
        apps_per_job=apps_per_job,
        top_gaps=top_gaps,
    )


@recruiter_bp.route("/jobs/new", methods=["GET", "POST"])
@role_required("recruiter")
def create_job():
    if request.method == "POST":
        expires_raw = request.form.get("expires_at")
        expires_at = None
        if expires_raw:
            try:
                expires_at = datetime.strptime(expires_raw, "%Y-%m-%d")
            except ValueError:
                flash("Invalid expiry date format", "danger")
                return render_template("job_form.html", editing=False)

        job = JobPosting(
            title=clean_text(request.form.get("title")),
            description=clean_text(request.form.get("description")),
            required_skills=clean_text(request.form.get("required_skills")),
            recruiter_id=session["user_id"],
            job_type=clean_text(request.form.get("job_type", "Full-time")),
            work_mode=clean_text(request.form.get("work_mode", "Onsite")),
            company_name=clean_text(request.form.get("company_name", "")),
            location=clean_text(request.form.get("location", "")),
            experience_level=clean_text(request.form.get("experience_level", "")),
            expires_at=expires_at,
            is_active=True,
        )
        db.session.add(job)
        db.session.commit()
        flash("Job created", "success")
        return redirect(url_for("recruiter.dashboard"))
    return render_template("job_form.html", editing=False)


@recruiter_bp.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
@role_required("recruiter")
def edit_job(job_id):
    job = JobPosting.query.filter_by(
        id=job_id, recruiter_id=session["user_id"]
    ).first()
    if job is None:
        abort(404)
    if request.method == "POST":
        job.title = clean_text(request.form.get("title"))
        job.description = clean_text(request.form.get("description"))
        job.required_skills = clean_text(request.form.get("required_skills"))
        job.job_type = clean_text(request.form.get("job_type", job.job_type))
        job.work_mode = clean_text(request.form.get("work_mode", job.work_mode))
        job.company_name = clean_text(request.form.get("company_name", job.company_name))
        job.location = clean_text(request.form.get("location", job.location))
        job.experience_level = clean_text(
            request.form.get("experience_level", job.experience_level)
        )
        expires_raw = request.form.get("expires_at")
        if expires_raw:
            try:
                job.expires_at = datetime.strptime(expires_raw, "%Y-%m-%d")
            except ValueError:
                flash("Invalid expiry date", "danger")
                return render_template("job_form.html", job=job, editing=True)
        db.session.commit()
        for sub in job.submissions:
            try:
                rescore_submission(sub, job)
            except Exception as exc:
                print(f"Re-score failed for submission {sub.id}: {exc}")
        db.session.commit()
        flash("Job updated and all candidates re-scored.", "success")
        return redirect(url_for("recruiter.dashboard"))
    return render_template("job_form.html", job=job, editing=True)


@recruiter_bp.route("/jobs/<int:job_id>/close", methods=["POST"])
@role_required("recruiter")
def close_job(job_id):
    job = JobPosting.query.filter_by(
        id=job_id, recruiter_id=session["user_id"]
    ).first()
    if job is None:
        abort(404)
    job.is_active = False
    db.session.commit()
    flash("Job closed", "info")
    return redirect(url_for("recruiter.dashboard"))


@recruiter_bp.route("/reports/<int:job_id>")
@role_required("recruiter")
def download_report(job_id):
    # Ensure user isolation
    job = JobPosting.query.filter_by(
        id=job_id, recruiter_id=session["user_id"]
    ).first()
    if job is None:
        abort(404)
    rows = [["Candidate", "Email", "Score", "Submitted"]]
    for sub in job.submissions:
        rows.append(
            [
                sub.candidate_name,
                sub.email,
                sub.score,
                sub.created_at.isoformat() if sub.created_at else "",
            ]
        )
    output = StringIO()
    writer = csv.writer(output)
    writer.writerows(rows)
    output.seek(0)
    bytes_output = BytesIO(output.getvalue().encode("utf-8"))
    bytes_output.seek(0)
    return send_file(
        bytes_output,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"job_{job_id}_report.csv",
    )


@recruiter_bp.route("/reports/<int:job_id>/pdf")
@role_required("recruiter")
def download_report_pdf(job_id):
    job = JobPosting.query.filter_by(
        id=job_id, recruiter_id=session["user_id"]
    ).first()
    if job is None:
        abort(404)
    from services.pdf_report import generate_job_report

    buffer = generate_job_report(job, job.submissions)
    safe_title = job.title.replace(" ", "_")[:40]
    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"report_{safe_title}_{job_id}.pdf",
    )


@recruiter_bp.route("/candidate/<int:submission_id>/status", methods=["POST"])
@role_required("recruiter")
def update_candidate_status(submission_id):
    submission = db.session.get(ResumeSubmission, submission_id)
    if submission is None:
        abort(404)
    # Ensure user isolation
    job = JobPosting.query.filter_by(
        id=submission.job_id, recruiter_id=session["user_id"]
    ).first()
    if job is None:
        abort(404)

    new_status = request.json.get("status") if request.is_json else None
    valid_statuses = [
        "pending",
        "shortlisted",
        "rejected",
        "under_review",
        "selected",
    ]

    if new_status not in valid_statuses:
        return jsonify({"error": "Invalid status"}), 400

    submission.status = new_status
    db.session.commit()
    notify_candidate(current_app._get_current_object(), submission, new_status)

    return jsonify({"success": True, "status": new_status})
