from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app_helpers import clean_text
from extensions import limiter
from models import User, db
from utils.auth_utils import validate_password

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute", methods=["POST"])
def login():
    if request.method == "POST":
        email = clean_text(request.form.get("email"))
        password = request.form.get("password") or ""
        user = User.query.filter_by(email=email).first()
        if user and not user.is_active:
            flash("Account deactivated", "danger")
            return render_template("login.html")
        if user and user.check_password(password):
            session.permanent = True
            session["user_id"] = user.id
            session["role"] = user.role
            flash("Welcome back!", "success")
            if user.role == "recruiter":
                return redirect(url_for("recruiter.dashboard"))
            if user.role == "admin":
                return redirect(url_for("admin.dashboard"))
            return redirect(url_for("candidate.dashboard"))
        flash("Invalid credentials", "danger")
    return render_template("login.html")


@auth_bp.route("/signup", methods=["GET", "POST"])
@limiter.limit("20 per hour", methods=["POST"])
def signup():
    if request.method == "POST":
        email = clean_text(request.form.get("email"))
        password = request.form.get("password") or ""
        confirm_password = request.form.get("confirm_password") or ""
        role = clean_text(request.form.get("role"))

        if not email or not password or not role:
            flash("All fields are required", "danger")
            return render_template("signup.html")

        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return render_template("signup.html")

        pwd_error = validate_password(password)
        if pwd_error:
            flash(pwd_error, "danger")
            return render_template("signup.html")

        if role not in ["candidate", "recruiter"]:
            flash("Invalid role selected", "danger")
            return render_template("signup.html")

        if User.query.filter_by(email=email).first():
            flash("Email already registered. Please login instead.", "danger")
            return redirect(url_for("auth.login"))

        user = User(email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Account created successfully! Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("signup.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out", "info")
    return redirect(url_for("auth.login"))
