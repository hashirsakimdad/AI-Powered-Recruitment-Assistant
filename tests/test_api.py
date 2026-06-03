from models import JobPosting, ResumeSubmission, User, db


def test_submission_status_requires_auth(client):
    rv = client.get("/api/submission/1/status")
    assert rv.status_code in (302, 401, 403)


def test_submission_status_candidate_isolation(client, app):
    with app.app_context():
        recruiter = User(email="rec_api@test.com", role="recruiter", is_active=True)
        recruiter.set_password("Test1234!")
        candidate = User(email="cand_api@test.com", role="candidate", is_active=True)
        candidate.set_password("Test1234!")
        other = User(email="other_api@test.com", role="candidate", is_active=True)
        other.set_password("Test1234!")
        db.session.add_all([recruiter, candidate, other])
        db.session.commit()
        job = JobPosting(
            title="API Job",
            description="desc",
            required_skills="Python",
            recruiter_id=recruiter.id,
            is_active=True,
        )
        db.session.add(job)
        db.session.commit()
        sub = ResumeSubmission(
            candidate_id=other.id,
            candidate_name="Other",
            email=other.email,
            file_path="/fake/path.pdf",
            job_id=job.id,
            scoring_status="scored",
            status="pending",
        )
        db.session.add(sub)
        db.session.commit()
        sub_id = sub.id

    client.post(
        "/login",
        data={"email": "cand_api@test.com", "password": "Test1234!"},
        follow_redirects=True,
    )
    rv = client.get(f"/api/submission/{sub_id}/status")
    assert rv.status_code == 403


def test_api_submissions_recruiter_only(client, app):
    with app.app_context():
        recruiter = User(email="rec_subs@test.com", role="recruiter", is_active=True)
        recruiter.set_password("Test1234!")
        candidate = User(email="cand_subs@test.com", role="candidate", is_active=True)
        candidate.set_password("Test1234!")
        db.session.add_all([recruiter, candidate])
        db.session.commit()
        job = JobPosting(
            title="Subs Job",
            description="desc",
            required_skills="Python",
            recruiter_id=recruiter.id,
            is_active=True,
        )
        db.session.add(job)
        db.session.commit()
        job_id = job.id

    client.post(
        "/login",
        data={"email": "cand_subs@test.com", "password": "Test1234!"},
        follow_redirects=True,
    )
    rv = client.get(f"/api/job/{job_id}/submissions")
    assert rv.status_code in (302, 403)

    client.post("/logout", follow_redirects=True)
    client.post(
        "/login",
        data={"email": "rec_subs@test.com", "password": "Test1234!"},
        follow_redirects=True,
    )
    rv = client.get(f"/api/job/{job_id}/submissions")
    assert rv.status_code == 200
    assert isinstance(rv.get_json(), list)
