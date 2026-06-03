from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from sqlalchemy import desc, func

from blueprints.auth_utils import role_required
from models import JobPosting, ResumeSubmission, User, db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@role_required("admin")
def dashboard():
    total_users = User.query.count()
    total_jobs = JobPosting.query.count()
    total_submissions = ResumeSubmission.query.count()
    avg = db.session.query(func.avg(ResumeSubmission.score)).scalar() or 0
    recent_submissions = (
        ResumeSubmission.query.order_by(desc(ResumeSubmission.created_at)).limit(10).all()
    )
    recent_users = User.query.order_by(desc(User.created_at)).limit(5).all()
    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_jobs=total_jobs,
        total_submissions=total_submissions,
        avg_score=round(float(avg), 1),
        recent_submissions=recent_submissions,
        recent_users=recent_users,
    )


@admin_bp.route("/users")
@role_required("admin")
def users():
    page = request.args.get("page", 1, type=int)
    users_page = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template("admin_users.html", users=users_page)


@admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@role_required("admin")
def toggle_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    if user.role == "admin" and user.is_active:
        flash("Cannot deactivate admin accounts.", "warning")
        return redirect(url_for("admin.users"))
    user.is_active = not user.is_active
    db.session.commit()
    action = "activated" if user.is_active else "deactivated"
    flash(f"User {user.email} has been {action}.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/deactivate", methods=["POST"])
@role_required("admin")
def deactivate_user(user_id):
    return toggle_user(user_id)


@admin_bp.route("/jobs")
@role_required("admin")
def jobs():
    page = request.args.get("page", 1, type=int)
    jobs_page = JobPosting.query.order_by(JobPosting.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template("admin_jobs.html", jobs=jobs_page)


@admin_bp.route("/jobs/<int:job_id>/remove", methods=["POST"])
@role_required("admin")
def remove_job(job_id):
    job = db.session.get(JobPosting, job_id)
    if job is None:
        abort(404)
    db.session.delete(job)
    db.session.commit()
    flash("Job posting removed.", "success")
    return redirect(url_for("admin.jobs"))
