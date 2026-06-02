import io

from models import JobPosting, ResumeSubmission, User, db


def _minimal_pdf():
    return io.BytesIO(b"%PDF-1.4 minimal test content for upload validation bypass")


def test_duplicate_submission_blocked(candidate_client, app):
    with app.app_context():
        recruiter = User(email="rec@test.com", role="recruiter")
        recruiter.set_password("Password1")
        db.session.add(recruiter)
        db.session.commit()
        job = JobPosting(
            title="Test Role",
            description="desc",
            required_skills="Python",
            recruiter_id=recruiter.id,
        )
        db.session.add(job)
        db.session.commit()
        job_id = job.id
        candidate = User.query.filter_by(email="candidate@example.com").first()
        existing = ResumeSubmission(
            candidate_name="Test",
            email="c@test.com",
            file_path="/tmp/x.pdf",
            job_id=job_id,
            candidate_id=candidate.id,
            scoring_status="scored",
        )
        db.session.add(existing)
        db.session.commit()

    resp = candidate_client.post(
        f"/candidate/upload/{job_id}",
        data={
            "name": "Test",
            "email": "c@test.com",
            "resume": (_minimal_pdf(), "resume.pdf"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert b"already applied" in resp.data
    with app.app_context():
        count = ResumeSubmission.query.filter_by(
            candidate_id=User.query.filter_by(email="candidate@example.com").first().id,
            job_id=job_id,
        ).count()
        assert count == 1


def test_candidate_cannot_access_recruiter_routes(candidate_client):
    resp = candidate_client.get("/recruiter/dashboard", follow_redirects=False)
    assert resp.status_code in (302, 403)
