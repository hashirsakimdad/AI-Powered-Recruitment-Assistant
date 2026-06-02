import json

import bleach
from sqlalchemy import desc, inspect, nullslast, text

from models import ResumeSubmission, db

ALLOWED_TAGS = []


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
            ("scoring_status", "VARCHAR(20) DEFAULT 'scored'"),
            ("expires_at", "DATETIME"),
            ("is_active", "BOOLEAN DEFAULT 1"),
        ]
        user_cols = {c["name"] for c in insp.get_columns("users")} if "users" in insp.get_table_names() else set()
        if "is_active" not in user_cols and "users" in insp.get_table_names():
            db.session.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1"))
        job_cols = (
            {c["name"] for c in insp.get_columns("job_postings")}
            if "job_postings" in insp.get_table_names()
            else set()
        )
        if "expires_at" not in job_cols and "job_postings" in insp.get_table_names():
            db.session.execute(text("ALTER TABLE job_postings ADD COLUMN expires_at DATETIME"))
        if "is_active" not in job_cols and "job_postings" in insp.get_table_names():
            db.session.execute(text("ALTER TABLE job_postings ADD COLUMN is_active BOOLEAN DEFAULT 1"))
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
    target = db.session.get(ResumeSubmission, submission_id)
    if not target or target.score is None:
        return 0
    below = sum(1 for s in all_scores if s < target.score)
    return round((below / len(all_scores)) * 100)
