import pytest


def test_login_success(client):
    resp = client.post(
        "/login",
        data={"email": "recruiter@example.com", "password": "recruiter123"},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "recruiter/dashboard" in resp.location


def test_login_invalid_password(client):
    resp = client.post(
        "/login",
        data={"email": "recruiter@example.com", "password": "wrong"},
        follow_redirects=True,
    )
    assert b"Invalid credentials" in resp.data


def test_login_rate_limit(rate_limit_client):
    # Login route limit is 10 per minute (see auth.login decorator).
    for _ in range(10):
        rate_limit_client.post(
            "/login",
            data={"email": "recruiter@example.com", "password": "wrong"},
        )
    resp = rate_limit_client.post(
        "/login",
        data={"email": "recruiter@example.com", "password": "wrong"},
    )
    assert resp.status_code == 429


def test_signup_duplicate_email(client, app):
    with app.app_context():
        from models import User, db

        user = User(email="dup@test.com", role="candidate")
        user.set_password("Password1")
        db.session.add(user)
        db.session.commit()

    resp = client.post(
        "/signup",
        data={
            "email": "dup@test.com",
            "password": "Password1",
            "confirm_password": "Password1",
            "role": "candidate",
        },
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "/login" in resp.location


def test_signup_password_mismatch(client):
    resp = client.post(
        "/signup",
        data={
            "email": "newuser@test.com",
            "password": "Password1",
            "confirm_password": "Password2",
            "role": "candidate",
        },
        follow_redirects=True,
    )
    assert b"Passwords do not match" in resp.data


def test_signup_weak_password(client):
    resp = client.post(
        "/signup",
        data={
            "email": "weak@test.com",
            "password": "short",
            "confirm_password": "short",
            "role": "candidate",
        },
        follow_redirects=True,
    )
    assert b"Password must be at least 8 characters" in resp.data
