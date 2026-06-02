from functools import wraps

from flask import flash, redirect, session, url_for

from models import User, db


def _active_session_user():
    """Return the logged-in user if session is valid and account is active."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    user = db.session.get(User, user_id)
    if not user or not user.is_active:
        session.clear()
        return None
    return user


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if _active_session_user() is None:
            flash("Please login to access this page", "warning")
            return redirect(url_for("auth.login"))
        return fn(*args, **kwargs)

    return wrapper


def role_required(role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = _active_session_user()
            if user is None:
                flash("Please login to access this page", "warning")
                return redirect(url_for("auth.login"))
            if user.role != role:
                flash("Unauthorized access", "danger")
                return redirect(url_for("auth.login"))
            return fn(*args, **kwargs)

        return wrapper

    return decorator
