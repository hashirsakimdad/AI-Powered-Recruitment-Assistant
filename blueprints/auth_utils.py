from functools import wraps

from flask import flash, redirect, session, url_for


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to access this page", "warning")
            return redirect(url_for("auth.login"))
        return fn(*args, **kwargs)

    return wrapper


def role_required(role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                flash("Please login to access this page", "warning")
                return redirect(url_for("auth.login"))
            if session.get("role") != role:
                flash("Unauthorized access", "danger")
                return redirect(url_for("auth.login"))
            return fn(*args, **kwargs)

        return wrapper

    return decorator
