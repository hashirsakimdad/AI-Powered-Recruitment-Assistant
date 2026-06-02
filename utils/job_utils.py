from datetime import datetime

from models import JobPosting, db


def get_filtered_jobs(query_str: str, job_type: str, work_mode: str):
    """Return active, non-expired jobs matching optional search filters."""
    jobs_query = JobPosting.query.filter(JobPosting.is_active.is_(True))
    jobs_query = jobs_query.filter(
        db.or_(
            JobPosting.expires_at.is_(None),
            JobPosting.expires_at > datetime.utcnow(),
        )
    )
    if query_str:
        jobs_query = jobs_query.filter(
            db.or_(
                JobPosting.title.ilike(f"%{query_str}%"),
                JobPosting.description.ilike(f"%{query_str}%"),
                JobPosting.company_name.ilike(f"%{query_str}%"),
                JobPosting.required_skills.ilike(f"%{query_str}%"),
            )
        )
    if job_type:
        jobs_query = jobs_query.filter(JobPosting.job_type == job_type)
    if work_mode:
        jobs_query = jobs_query.filter(JobPosting.work_mode == work_mode)
    return jobs_query.order_by(JobPosting.created_at.desc())
