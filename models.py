import os
from datetime import datetime
from typing import Optional

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # recruiter, candidate, admin
    is_active = db.Column(db.Boolean, default=True, nullable=False)
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
    job_type = db.Column(db.String(20), default="Full-time")
    work_mode = db.Column(db.String(20), default="Onsite")
    company_name = db.Column(db.String(120), nullable=True)
    location = db.Column(db.String(120), nullable=True)
    experience_level = db.Column(db.String(50), nullable=True)
    salary_range = db.Column(db.String(80), nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)


class ResumeSubmission(db.Model):
    __tablename__ = "resume_submissions"
    __table_args__ = (
        db.UniqueConstraint("candidate_id", "job_id", name="uq_candidate_job"),
    )
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
    is_resume_valid = db.Column(db.Boolean, default=True)
    detection_details = db.Column(db.JSON, nullable=True)
    feedback_history = db.Column(db.JSON, default=list)
    status = db.Column(
        db.String(20), default="pending"
    )  # pending, shortlisted, rejected, under_review, selected
    scoring_status = db.Column(
        db.String(20), default="processing"
    )  # processing, scored, failed
    inferred_skills = db.Column(db.JSON, nullable=True)
    explicit_skills = db.Column(db.JSON, nullable=True)
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
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_resume_valid": self.is_resume_valid,
            "scoring_status": self.scoring_status,
            "status": self.status,
            "inferred_skills": self.inferred_skills,
            "explicit_skills": self.explicit_skills,
        }


def seed_demo_users(db_session) -> None:
    """Seed demo accounts only in development or when SEED_DEMO_USERS=true."""
    flask_env = os.getenv("FLASK_ENV", "production")
    seed_flag = os.getenv("SEED_DEMO_USERS", "").lower() == "true"
    if flask_env != "development" and not seed_flag:
        return

    demos = [
        ("recruiter@example.com", "recruiter", "recruiter123"),
        ("candidate@example.com", "candidate", "candidate123"),
        ("admin@example.com", "admin", "admin123"),
    ]
    for email, role, password in demos:
        if not User.query.filter_by(email=email).first():
            user = User(email=email, role=role, is_active=True)
            user.set_password(password)
            db_session.add(user)
    db_session.commit()

