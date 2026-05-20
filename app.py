import json
import os
from functools import wraps
from pathlib import Path

import bleach
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import desc, inspect, nullslast, text

from config import Config, ensure_instance_dirs
from models import JobPosting, ResumeSubmission, User, db, seed_demo_users
from services.resume_service import handle_upload, process_resume, rescore_submission

ALLOWED_TAGS = []
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])


def clean_text(value) -> str:
    if value is None:
        return ""
    return bleach.clean(str(value).strip(), tags=ALLOWED_TAGS, strip=True)


def ensure_breakdown_columns():
    """Add score breakdown columns to existing SQLite DBs without full migration."""
    try:
        insp = inspect(db.engine)
        if "resume_submissions" not in insp.get_table_names():
            return
        cols = {c["name"] for c in insp.get_columns("resume_submissions")}
        additions = [
            ("keyword_score", "FLOAT DEFAULT 0.0"),
            ("semantic_score", "FLOAT DEFAULT 0.0"),
            ("experience_score", "FLOAT DEFAULT 0.0"),
            ("format_score", "FLOAT DEFAULT 0.0"),
            ("skill_gap", "TEXT DEFAULT ''"),
        ]
        for name, col_type in additions:
            if name not in cols:
                db.session.execute(
                    text(f"ALTER TABLE resume_submissions ADD COLUMN {name} {col_type}")
                )
        db.session.commit()
    except Exception:
        db.session.rollback()


def get_score_percentile(submission_id: int, job_id: int) -> int:
    """Returns what percentile this candidate is in for that job (0-100)."""
    all_scores = [
        s.score
        for s in ResumeSubmission.query.filter_by(job_id=job_id).all()
        if s.score is not None
    ]
    if not all_scores:
        return 0
    target = ResumeSubmission.query.get(submission_id)
    if not target or target.score is None:
        return 0
    below = sum(1 for s in all_scores if s < target.score)
    return round((below / len(all_scores)) * 100)


def create_app():
    ensure_instance_dirs()
    app = Flask(
        __name__,
        instance_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), "instance"),
    )
    app.config.from_object(Config)
    db.init_app(app)
    Migrate(app, db)
    csrf.init_app(app)
    limiter.init_app(app)

    @app.errorhandler(429)
    def ratelimit_handler(e):
        flash("Too many login attempts. Please wait 1 minute.", "danger")
        return render_template("login.html"), 429

    @app.before_request
    def ensure_upload_dir():
        Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    register_routes(app)
    with app.app_context():
        os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)
        os.makedirs(os.path.join(app.root_path, "instance", "uploads"), exist_ok=True)
        db.create_all()
        ensure_breakdown_columns()
        seed_demo_users(db.session)
    return app


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to access this page", "warning")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)

    return wrapper


def role_required(role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                flash("Please login to access this page", "warning")
                return redirect(url_for("login"))
            if session.get("role") != role:
                flash("Unauthorized access", "danger")
                return redirect(url_for("login"))
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def register_routes(app: Flask):
    @app.route("/")
    def index():
        if "user_id" in session:
            if session.get("role") == "recruiter":
                return redirect(url_for("recruiter_dashboard"))
            return redirect(url_for("candidate_dashboard"))
        return render_template("index.html")

    @app.route("/login", methods=["GET", "POST"])
    @limiter.limit("5 per minute", methods=["POST"])
    def login():
        if request.method == "POST":
            email = clean_text(request.form.get("email"))
            password = request.form.get("password") or ""
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                session.permanent = True
                session["user_id"] = user.id
                session["role"] = user.role
                flash("Welcome back!", "success")
                return redirect(url_for(f"{user.role}_dashboard"))
            flash("Invalid credentials", "danger")
        return render_template("login.html")

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if request.method == "POST":
            email = clean_text(request.form.get("email"))
            password = request.form.get("password") or ""
            confirm_password = request.form.get("confirm_password") or ""
            role = clean_text(request.form.get("role"))

            if not email or not password or not role:
                flash("All fields are required", "danger")
                return render_template("signup.html")

            if password != confirm_password:
                flash("Passwords do not match", "danger")
                return render_template("signup.html")

            if len(password) < 6:
                flash("Password must be at least 6 characters", "danger")
                return render_template("signup.html")

            if role not in ["candidate", "recruiter"]:
                flash("Invalid role selected", "danger")
                return render_template("signup.html")

            if User.query.filter_by(email=email).first():
                flash("Email already registered. Please login instead.", "danger")
                return redirect(url_for("login"))

            user = User(email=email, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            flash("Account created successfully! Please login.", "success")
            return redirect(url_for("login"))

        return render_template("signup.html")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("Logged out", "info")
        return redirect(url_for("login"))

    @app.route("/recruiter/dashboard")
    @role_required("recruiter")
    def recruiter_dashboard():
        user_id = session["user_id"]
        jobs = JobPosting.query.filter_by(recruiter_id=user_id).all()
        submissions = (
            ResumeSubmission.query.join(JobPosting)
            .filter(JobPosting.recruiter_id == user_id)
            .order_by(nullslast(desc(ResumeSubmission.score)))
            .all()
        )
        return render_template(
            "recruiter_dashboard.html", jobs=jobs, submissions=submissions
        )

    @app.route("/recruiter/analytics")
    @role_required("recruiter")
    def recruiter_analytics():
        from collections import Counter

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

    @app.route("/recruiter/jobs/new", methods=["GET", "POST"])
    @role_required("recruiter")
    def create_job():
        if request.method == "POST":
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
            )
            db.session.add(job)
            db.session.commit()
            flash("Job created", "success")
            return redirect(url_for("recruiter_dashboard"))
        return render_template("job_form.html", editing=False)

    @app.route("/recruiter/jobs/<int:job_id>/edit", methods=["GET", "POST"])
    @role_required("recruiter")
    def edit_job(job_id):
        job = JobPosting.query.filter_by(
            id=job_id, recruiter_id=session["user_id"]
        ).first_or_404()
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
            db.session.commit()
            for sub in job.submissions:
                try:
                    rescore_submission(sub, job)
                except Exception as exc:
                    print(f"Re-score failed for submission {sub.id}: {exc}")
            db.session.commit()
            flash("Job updated and all candidates re-scored.", "success")
            return redirect(url_for("recruiter_dashboard"))
        return render_template("job_form.html", job=job, editing=True)

    @app.route("/recruiter/reports/<int:job_id>")
    @role_required("recruiter")
    def download_report(job_id):
        job = JobPosting.query.filter_by(
            id=job_id, recruiter_id=session["user_id"]
        ).first_or_404()
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
        from io import BytesIO, StringIO
        import csv

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

    @app.route("/recruiter/reports/<int:job_id>/pdf")
    @role_required("recruiter")
    def download_report_pdf(job_id):
        job = JobPosting.query.filter_by(
            id=job_id, recruiter_id=session["user_id"]
        ).first_or_404()
        from services.pdf_report import generate_job_report

        buffer = generate_job_report(job, job.submissions)
        safe_title = job.title.replace(" ", "_")[:40]
        return send_file(
            buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"report_{safe_title}_{job_id}.pdf",
        )

    @app.route("/candidate/dashboard")
    @role_required("candidate")
    def candidate_dashboard():
        query = clean_text(request.args.get("q", ""))
        job_type = clean_text(request.args.get("job_type", ""))
        work_mode = clean_text(request.args.get("work_mode", ""))

        jobs_query = JobPosting.query
        if query:
            jobs_query = jobs_query.filter(
                db.or_(
                    JobPosting.title.ilike(f"%{query}%"),
                    JobPosting.description.ilike(f"%{query}%"),
                    JobPosting.company_name.ilike(f"%{query}%"),
                    JobPosting.required_skills.ilike(f"%{query}%"),
                )
            )
        if job_type:
            jobs_query = jobs_query.filter(JobPosting.job_type == job_type)
        if work_mode:
            jobs_query = jobs_query.filter(JobPosting.work_mode == work_mode)

        jobs = jobs_query.order_by(JobPosting.created_at.desc()).all()
        user_id = session["user_id"]
        my_submissions = ResumeSubmission.query.filter_by(candidate_id=user_id).all()
        percentiles = {
            sub.id: get_score_percentile(sub.id, sub.job_id) for sub in my_submissions
        }

        return render_template(
            "candidate_dashboard.html",
            jobs=jobs,
            submissions=my_submissions,
            search_query=query,
            selected_job_type=job_type,
            selected_work_mode=work_mode,
            percentiles=percentiles,
        )

    @app.route("/candidate/upload/<int:job_id>", methods=["POST"])
    @role_required("candidate")
    def upload_resume(job_id):
        job = JobPosting.query.get_or_404(job_id)
        file = request.files.get("resume")
        if not file:
            flash("No file uploaded", "danger")
            return redirect(url_for("candidate_dashboard"))
        try:
            dest = handle_upload(
                file, app.config["UPLOAD_FOLDER"], app.config["ALLOWED_EXTENSIONS"]
            )
            parsed, scoring, submission = process_resume(dest, job)
            user_id = session["user_id"]
            submission.candidate_id = user_id
            submission.candidate_name = clean_text(
                request.form.get("name", "Candidate")
            )
            submission.email = clean_text(request.form.get("email", "unknown@example.com"))
            db.session.commit()
            flash(f"Resume scored: {scoring['score']}", "success")
        except ValueError as exc:
            flash(f"Upload failed: {exc}", "danger")
        except Exception as exc:
            flash(f"Upload failed: {exc}", "danger")
        return redirect(url_for("candidate_dashboard"))

    @app.route("/api/submission/<int:submission_id>/breakdown")
    @login_required
    def submission_breakdown(submission_id):
        sub = ResumeSubmission.query.get_or_404(submission_id)
        job = JobPosting.query.get_or_404(sub.job_id)
        if session.get("role") == "recruiter":
            if job.recruiter_id != session["user_id"]:
                return jsonify({"error": "Unauthorized"}), 403
        elif session.get("role") == "candidate":
            if sub.candidate_id != session["user_id"]:
                return jsonify({"error": "Unauthorized"}), 403
        else:
            return jsonify({"error": "Unauthorized"}), 403

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
            }
        )

    @app.route("/api/job/<int:job_id>/submissions")
    @role_required("recruiter")
    def api_submissions(job_id):
        job = JobPosting.query.filter_by(
            id=job_id, recruiter_id=session["user_id"]
        ).first_or_404()
        payload = [sub.as_dict() for sub in job.submissions]
        return jsonify(payload)

    @app.route("/candidate/jobs/search")
    @role_required("candidate")
    def search_jobs():
        query = clean_text(request.args.get("q", ""))
        job_type = clean_text(request.args.get("job_type", ""))
        work_mode = clean_text(request.args.get("work_mode", ""))

        jobs_query = JobPosting.query
        if query:
            jobs_query = jobs_query.filter(
                db.or_(
                    JobPosting.title.ilike(f"%{query}%"),
                    JobPosting.description.ilike(f"%{query}%"),
                    JobPosting.company_name.ilike(f"%{query}%"),
                    JobPosting.required_skills.ilike(f"%{query}%"),
                )
            )
        if job_type:
            jobs_query = jobs_query.filter(JobPosting.job_type == job_type)
        if work_mode:
            jobs_query = jobs_query.filter(JobPosting.work_mode == work_mode)

        jobs = jobs_query.order_by(JobPosting.created_at.desc()).all()
        my_submissions = ResumeSubmission.query.filter_by(
            candidate_id=session["user_id"]
        ).all()
        percentiles = {
            sub.id: get_score_percentile(sub.id, sub.job_id) for sub in my_submissions
        }

        return render_template(
            "candidate_dashboard.html",
            jobs=jobs,
            submissions=my_submissions,
            search_query=query,
            selected_job_type=job_type,
            selected_work_mode=work_mode,
            percentiles=percentiles,
        )

    @app.route("/candidate/jobs/<int:job_id>")
    @role_required("candidate")
    def job_details(job_id):
        job = JobPosting.query.get_or_404(job_id)
        return render_template("job_details.html", job=job)

    @app.route("/recruiter/candidate/<int:submission_id>/status", methods=["POST"])
    @role_required("recruiter")
    def update_candidate_status(submission_id):
        submission = ResumeSubmission.query.get_or_404(submission_id)
        JobPosting.query.filter_by(
            id=submission.job_id, recruiter_id=session["user_id"]
        ).first_or_404()

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

        return jsonify({"success": True, "status": new_status})


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
