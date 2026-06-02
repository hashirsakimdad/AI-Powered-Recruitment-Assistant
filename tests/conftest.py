import os

import pytest

from app import create_app
from models import User, db as _db


@pytest.fixture
def app():
    os.environ["SEED_DEMO_USERS"] = "true"
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
            "SEED_DEMO_USERS": True,
        }
    )
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


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
