from models import JobPosting, ResumeSubmission, User, db


def test_resume_submission_as_dict(app):
    with app.app_context():
        user = User(email="dict@test.com", role="candidate", is_active=True)
        user.set_password("Test1234!")
        recruiter = User(email="dict_rec@test.com", role="recruiter", is_active=True)
        recruiter.set_password("Test1234!")
        db.session.add_all([user, recruiter])
        db.session.commit()
        job = JobPosting(
            title="Dict Job",
            description="desc",
            required_skills="Python",
            recruiter_id=recruiter.id,
            salary_range="$80k-$120k",
            is_active=True,
        )
        db.session.add(job)
        db.session.commit()
        sub = ResumeSubmission(
            candidate_id=user.id,
            candidate_name="Test",
            email=user.email,
            file_path="/tmp/x.pdf",
            job_id=job.id,
            score=85.0,
            scoring_status="scored",
            status="shortlisted",
            inferred_skills=["Python"],
            explicit_skills=["Flask"],
        )
        db.session.add(sub)
        db.session.commit()
        data = sub.as_dict()
        assert data["status"] == "shortlisted"
        assert data["scoring_status"] == "scored"
        assert data["inferred_skills"] == ["Python"]
        assert data["explicit_skills"] == ["Flask"]


def test_unique_candidate_job_constraint(app):
    with app.app_context():
        user = User(email="uniq@test.com", role="candidate", is_active=True)
        user.set_password("Test1234!")
        recruiter = User(email="uniq_rec@test.com", role="recruiter", is_active=True)
        recruiter.set_password("Test1234!")
        db.session.add_all([user, recruiter])
        db.session.commit()
        job = JobPosting(
            title="Unique Job",
            description="desc",
            required_skills="Python",
            recruiter_id=recruiter.id,
            is_active=True,
        )
        db.session.add(job)
        db.session.commit()
        sub1 = ResumeSubmission(
            candidate_id=user.id,
            candidate_name="Test",
            email=user.email,
            file_path="/tmp/a.pdf",
            job_id=job.id,
            scoring_status="scored",
        )
        db.session.add(sub1)
        db.session.commit()
        sub2 = ResumeSubmission(
            candidate_id=user.id,
            candidate_name="Test",
            email=user.email,
            file_path="/tmp/b.pdf",
            job_id=job.id,
            scoring_status="processing",
        )
        db.session.add(sub2)
        import pytest
        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            db.session.commit()
