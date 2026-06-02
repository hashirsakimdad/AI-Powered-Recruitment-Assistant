from models import JobPosting, User, db


def test_create_job(recruiter_client, app):
    resp = recruiter_client.post(
        "/recruiter/jobs/new",
        data={
            "title": "Backend Engineer",
            "description": "Build APIs",
            "required_skills": "Python, Flask",
            "job_type": "Full-time",
            "work_mode": "Remote",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    with app.app_context():
        job = JobPosting.query.filter_by(title="Backend Engineer").first()
        assert job is not None


def test_recruiter_cannot_see_other_recruiter_jobs(app, client):
    with app.app_context():
        r1 = User(email="r1@test.com", role="recruiter")
        r1.set_password("Password1")
        r2 = User(email="r2@test.com", role="recruiter")
        r2.set_password("Password1")
        db.session.add_all([r1, r2])
        db.session.commit()
        j1 = JobPosting(
            title="Job A",
            description="d",
            required_skills="x",
            recruiter_id=r1.id,
        )
        j2 = JobPosting(
            title="Job B",
            description="d",
            required_skills="y",
            recruiter_id=r2.id,
        )
        db.session.add_all([j1, j2])
        db.session.commit()
        job_b_id = j2.id

    client.post("/login", data={"email": "r1@test.com", "password": "Password1"})
    resp = client.get(f"/recruiter/reports/{job_b_id}")
    assert resp.status_code == 404


def test_download_report_unauthorized(app, client):
    with app.app_context():
        r1 = User(email="ra@test.com", role="recruiter")
        r1.set_password("Password1")
        r2 = User(email="rb@test.com", role="recruiter")
        r2.set_password("Password1")
        db.session.add_all([r1, r2])
        db.session.commit()
        job = JobPosting(
            title="Secret",
            description="d",
            required_skills="x",
            recruiter_id=r2.id,
        )
        db.session.add(job)
        db.session.commit()
        job_id = job.id

    client.post("/login", data={"email": "ra@test.com", "password": "Password1"})
    resp = client.get(f"/recruiter/reports/{job_id}")
    assert resp.status_code == 404
