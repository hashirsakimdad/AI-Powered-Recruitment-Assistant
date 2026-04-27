import os
from functools import wraps
from pathlib import Path

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
from flask_migrate import Migrate
from sqlalchemy import desc, nullslast

from config import Config, ensure_instance_dirs
from models import JobPosting, ResumeSubmission, User, db, seed_demo_users
from services.resume_service import handle_upload, process_resume


def create_app():
    ensure_instance_dirs()
    app = Flask(
        __name__,
        instance_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), "instance"),
    )
    app.config.from_object(Config)
    db.init_app(app)
    Migrate(app, db)

    @app.before_request
    def ensure_upload_dir():
        Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    register_routes(app)
    with app.app_context():
        os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)
        os.makedirs(os.path.join(app.root_path, "instance", "uploads"), exist_ok=True)
        db.create_all()
        seed_demo_users(db.session)
    return app


def login_required(fn):
    """Decorator to ensure user is logged in."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to access this page", "warning")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper


def role_required(role):
    """Decorator to ensure user has the required role."""
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
    def login():
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                session["user_id"] = user.id
                session["role"] = user.role
                flash("Welcome back!", "success")
                return redirect(url_for(f"{user.role}_dashboard"))
            flash("Invalid credentials", "danger")
        return render_template("login.html")

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")
            role = request.form.get("role")
            
            # Validation
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
            
            # Check if user already exists
            if User.query.filter_by(email=email).first():
                flash("Email already registered. Please login instead.", "danger")
                return redirect(url_for("login"))
            
            # Create new user
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

    # Recruiter routes
    @app.route("/recruiter/dashboard")
    @role_required("recruiter")
    def recruiter_dashboard():
        # Ensure user isolation: only show jobs created by this recruiter
        user_id = session["user_id"]
        jobs = JobPosting.query.filter_by(recruiter_id=user_id).all()
        # Order by score descending, handling NULL values (NULLs last)
        submissions = (
            ResumeSubmission.query.join(JobPosting)
            .filter(JobPosting.recruiter_id == user_id)
            .order_by(nullslast(desc(ResumeSubmission.score)))
            .all()
        )
        return render_template(
            "recruiter_dashboard.html", jobs=jobs, submissions=submissions
        )

    @app.route("/recruiter/jobs/new", methods=["GET", "POST"])
    @role_required("recruiter")
    def create_job():
        if request.method == "POST":
            title = request.form["title"]
            description = request.form["description"]
            required_skills = request.form["required_skills"]
            job_type = request.form.get("job_type", "Full-time")
            work_mode = request.form.get("work_mode", "Onsite")
            company_name = request.form.get("company_name", "")
            location = request.form.get("location", "")
            experience_level = request.form.get("experience_level", "")
            # Ensure user isolation: job is linked to current user
            job = JobPosting(
                title=title,
                description=description,
                required_skills=required_skills,
                recruiter_id=session["user_id"],
                job_type=job_type,
                work_mode=work_mode,
                company_name=company_name,
                location=location,
                experience_level=experience_level,
            )
            db.session.add(job)
            db.session.commit()
            flash("Job created", "success")
            return redirect(url_for("recruiter_dashboard"))
        return render_template("job_form.html")

    @app.route("/recruiter/reports/<int:job_id>")
    @role_required("recruiter")
    def download_report(job_id):
        # Ensure user isolation: only allow access to own jobs
        job = JobPosting.query.filter_by(id=job_id, recruiter_id=session["user_id"]).first_or_404()
        rows = [
            ["Candidate", "Email", "Score", "Submitted"],
        ]
        for sub in job.submissions:
            rows.append(
                [
                    sub.candidate_name,
                    sub.email,
                    sub.score,
                    sub.created_at.isoformat(),
                ]
            )
        from io import BytesIO, StringIO
        import csv

        # Use StringIO for writing, then encode to bytes
        output = StringIO()
        writer = csv.writer(output)
        writer.writerows(rows)
        output.seek(0)
        # Convert to BytesIO for send_file
        bytes_output = BytesIO(output.getvalue().encode('utf-8'))
        bytes_output.seek(0)
        return send_file(
            bytes_output,
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"job_{job_id}_report.csv",
        )

    # Candidate routes
    @app.route("/candidate/dashboard")
    @role_required("candidate")
    def candidate_dashboard():
        # Get search parameters
        query = request.args.get("q", "").strip()
        job_type = request.args.get("job_type", "")
        work_mode = request.args.get("work_mode", "")
        
        # Build query
        jobs_query = JobPosting.query
        
        # Search by title, description, or company
        if query:
            jobs_query = jobs_query.filter(
                db.or_(
                    JobPosting.title.ilike(f"%{query}%"),
                    JobPosting.description.ilike(f"%{query}%"),
                    JobPosting.company_name.ilike(f"%{query}%"),
                    JobPosting.required_skills.ilike(f"%{query}%"),
                )
            )
        
        # Filter by job type
        if job_type:
            jobs_query = jobs_query.filter(JobPosting.job_type == job_type)
        
        # Filter by work mode
        if work_mode:
            jobs_query = jobs_query.filter(JobPosting.work_mode == work_mode)
        
        jobs = jobs_query.order_by(JobPosting.created_at.desc()).all()
        
        # Ensure user isolation: only show submissions by this candidate
        user_id = session["user_id"]
        my_submissions = ResumeSubmission.query.filter_by(
            candidate_id=user_id
        ).all()
        
        return render_template(
            "candidate_dashboard.html",
            jobs=jobs,
            submissions=my_submissions,
            search_query=query,
            selected_job_type=job_type,
            selected_work_mode=work_mode,
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
            dest = handle_upload(file, app.config["UPLOAD_FOLDER"], app.config["ALLOWED_EXTENSIONS"])
            parsed, scoring, submission = process_resume(dest, job)
            # Ensure user isolation: link submission to current user
            user_id = session["user_id"]
            submission.candidate_id = user_id
            submission.candidate_name = request.form.get("name", "Candidate")
            submission.email = request.form.get("email", "unknown@example.com")
            db.session.commit()
            flash(f"Resume scored: {scoring['score']}", "success")
        except ValueError as exc:
            # Resume detection or validation errors
            flash(f"Upload failed: {exc}", "danger")
        except Exception as exc:  # pragma: no cover - runtime guard
            flash(f"Upload failed: {exc}", "danger")
        return redirect(url_for("candidate_dashboard"))

    @app.route("/api/job/<int:job_id>/submissions")
    @role_required("recruiter")
    def api_submissions(job_id):
        # Ensure user isolation: only allow access to own jobs
        job = JobPosting.query.filter_by(id=job_id, recruiter_id=session["user_id"]).first_or_404()
        payload = [sub.as_dict() for sub in job.submissions]
        return jsonify(payload)
    
    # Job search and discovery routes
    @app.route("/candidate/jobs/search")
    @role_required("candidate")
    def search_jobs():
        query = request.args.get("q", "").strip()
        job_type = request.args.get("job_type", "")
        work_mode = request.args.get("work_mode", "")
        
        jobs_query = JobPosting.query
        
        # Search by title, description, or company
        if query:
            jobs_query = jobs_query.filter(
                db.or_(
                    JobPosting.title.ilike(f"%{query}%"),
                    JobPosting.description.ilike(f"%{query}%"),
                    JobPosting.company_name.ilike(f"%{query}%"),
                    JobPosting.required_skills.ilike(f"%{query}%"),
                )
            )
        
        # Filter by job type
        if job_type:
            jobs_query = jobs_query.filter(JobPosting.job_type == job_type)
        
        # Filter by work mode
        if work_mode:
            jobs_query = jobs_query.filter(JobPosting.work_mode == work_mode)
        
        jobs = jobs_query.order_by(JobPosting.created_at.desc()).all()
        
        return render_template(
            "candidate_dashboard.html",
            jobs=jobs,
            submissions=ResumeSubmission.query.filter_by(candidate_id=session["user_id"]).all(),
            search_query=query,
            selected_job_type=job_type,
            selected_work_mode=work_mode,
        )
    
    @app.route("/candidate/jobs/<int:job_id>")
    @role_required("candidate")
    def job_details(job_id):
        job = JobPosting.query.get_or_404(job_id)
        return render_template("job_details.html", job=job)
    
    # Recruiter decision control routes
    @app.route("/recruiter/candidate/<int:submission_id>/status", methods=["POST"])
    @role_required("recruiter")
    def update_candidate_status(submission_id):
        submission = ResumeSubmission.query.get_or_404(submission_id)
        # Ensure user isolation: only allow access to own job's submissions
        job = JobPosting.query.filter_by(id=submission.job_id, recruiter_id=session["user_id"]).first_or_404()
        
        new_status = request.json.get("status")
        valid_statuses = ["pending", "shortlisted", "rejected", "under_review", "selected"]
        
        if new_status not in valid_statuses:
            return jsonify({"error": "Invalid status"}), 400
        
        submission.status = new_status
        db.session.commit()
        
        return jsonify({"success": True, "status": new_status})


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

