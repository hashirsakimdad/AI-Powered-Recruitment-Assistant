import os

import pytest
from sqlalchemy.pool import StaticPool

from app import create_app
from models import User, db as _db


@pytest.fixture
def app():
    os.environ["SEED_DEMO_USERS"] = "true"
    app = create_app(
        {
            "TESTING": True,
            "RATELIMIT_ENABLED": False,
            "WTF_CSRF_ENABLED": False,
            "SEED_DEMO_USERS": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SQLALCHEMY_ENGINE_OPTIONS": {
                "connect_args": {"check_same_thread": False},
                "poolclass": StaticPool,
            },
        }
    )
    with app.app_context():
        _db.create_all()
        from models import seed_demo_users

        seed_demo_users(_db.session)
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def rate_limit_app():
    """App with rate limiting enabled for login tests."""
    app = create_app(
        {
            "TESTING": True,
            "RATELIMIT_ENABLED": True,
            "WTF_CSRF_ENABLED": False,
            "SEED_DEMO_USERS": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SQLALCHEMY_ENGINE_OPTIONS": {
                "connect_args": {"check_same_thread": False},
                "poolclass": StaticPool,
            },
        }
    )
    with app.app_context():
        _db.create_all()
        from models import seed_demo_users

        seed_demo_users(_db.session)
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def rate_limit_client(rate_limit_app):
    return rate_limit_app.test_client()


@pytest.fixture
def recruiter_client(client):
    client.post(
        "/login",
        data={"email": "recruiter@example.com", "password": "recruiter123"},
        follow_redirects=True,
    )
    return client


@pytest.fixture
def candidate_client(client):
    client.post(
        "/login",
        data={"email": "candidate@example.com", "password": "candidate123"},
        follow_redirects=True,
    )
    return client


def create_user(email: str, role: str, password: str = "Password1"):
    user = User(email=email, role=role)
    user.set_password(password)
    _db.session.add(user)
    _db.session.commit()
    return user
