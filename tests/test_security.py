from tests.conftest import create_user
from models import JobPosting, User


class TestLogin:
    def test_login_deactivated_user(self, client, app):
        with app.app_context():
            from models import User, db

            user = User(email="inactive@test.com", role="candidate", is_active=False)
            user.set_password("Test1234!")
            db.session.add(user)
            db.session.commit()

        rv = client.post(
            "/login",
            data={"email": "inactive@test.com", "password": "Test1234!"},
            follow_redirects=True,
        )
        assert b"deactivated" in rv.data.lower()


class TestAuthorization:
    def test_unauthenticated_redirect_to_login(self, client):
        rv = client.get("/recruiter/dashboard", follow_redirects=False)
        assert rv.status_code == 302
        assert "/login" in rv.headers["Location"]


class TestInputSanitization:
    def test_xss_in_job_title_sanitized(self, client, app):
        with app.app_context():
            create_user("recruiter_xss@test.com", "recruiter", "Test1234!")
        client.post(
            "/login",
            data={"email": "recruiter_xss@test.com", "password": "Test1234!"},
            follow_redirects=True,
        )
        rv = client.post(
            "/recruiter/jobs/new",
            data={
                "title": '<script>alert("xss")</script>',
                "description": "Test",
                "required_skills": "Python",
                "job_type": "Full-time",
                "work_mode": "Remote",
            },
            follow_redirects=True,
        )
        assert rv.status_code == 200
        with app.app_context():
            from models import JobPosting

            job = JobPosting.query.filter_by(recruiter_id=User.query.filter_by(email="recruiter_xss@test.com").first().id).order_by(JobPosting.id.desc()).first()
            assert job is not None
            assert "<script>" not in job.title
