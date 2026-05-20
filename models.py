from datetime import datetime
from typing import Optional

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # "recruiter" or "candidate"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class JobPosting(db.Model):
    __tablename__ = "job_postings"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.Text, nullable=False)
    recruiter_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    recruiter = db.relationship("User", backref="jobs")
    # New fields for job discovery
    job_type = db.Column(db.String(20), default="Full-time")  # Full-time, Part-time, Internship, Contract
    work_mode = db.Column(db.String(20), default="Onsite")  # Remote, Onsite, Hybrid
    company_name = db.Column(db.String(120), nullable=True)
    location = db.Column(db.String(120), nullable=True)
    experience_level = db.Column(db.String(50), nullable=True)  # Entry, Mid, Senior, Executive


class ResumeSubmission(db.Model):
    __tablename__ = "resume_submissions"
    id = db.Column(db.Integer, primary_key=True)
    candidate_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    parsed_summary = db.Column(db.JSON)
    score = db.Column(db.Float)
    explanation = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    job_id = db.Column(db.Integer, db.ForeignKey("job_postings.id"))
    job = db.relationship("JobPosting", backref="submissions")
    candidate_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    candidate = db.relationship("User", backref="submissions")
    # Resume detection metadata
    is_resume_valid = db.Column(db.Boolean, default=True)
    detection_details = db.Column(db.JSON, nullable=True)
    # Feedback history tracking
    feedback_history = db.Column(db.JSON, default=list)  # Store history of feedback versions
    # Recruiter decision control
    status = db.Column(db.String(20), default="pending")  # pending, shortlisted, rejected, under_review, selected
    # Skill inference data
    inferred_skills = db.Column(db.JSON, nullable=True)  # Skills inferred from experience/projects
    explicit_skills = db.Column(db.JSON, nullable=True)  # Explicitly listed skills
    # Score breakdown columns
    keyword_score = db.Column(db.Float, default=0.0)
    semantic_score = db.Column(db.Float, default=0.0)
    experience_score = db.Column(db.Float, default=0.0)
    format_score = db.Column(db.Float, default=0.0)
    skill_gap = db.Column(db.Text, default="")

    @property
    def resume_path(self) -> str:
        return self.file_path

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "candidate_name": self.candidate_name,
            "email": self.email,
            "score": self.score,
            "explanation": self.explanation,
            "job_id": self.job_id,
            "created_at": self.created_at.isoformat(),
            "is_resume_valid": self.is_resume_valid,
        }


def seed_demo_users(db_session) -> None:
    demos = [
        ("recruiter@demo.com", "recruiter", "demo123"),
        ("candidate@demo.com", "candidate", "demo123"),
    ]
    for email, role, password in demos:
        if not User.query.filter_by(email=email).first():
            user = User(email=email, role=role)
            user.set_password(password)
            db_session.add(user)
    db_session.commit()

