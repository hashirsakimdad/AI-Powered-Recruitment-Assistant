from email_validator import EmailNotValidError, validate_email
from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from sqlalchemy.exc import IntegrityError

from app_helpers import clean_text
from extensions import limiter
from models import User, db
from utils.auth_utils import validate_password

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    user_id = session.get("user_id")
    if user_id:
        user = db.session.get(User, user_id)
        if not user or not user.is_active:
            session.clear()
            return render_template("index.html")
        role = user.role
        if role == "recruiter":
            return redirect(url_for("recruiter.dashboard"))
        if role == "admin":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("candidate.dashboard"))
    return render_template("index.html")


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute", methods=["POST"])
def login():
    if request.method == "POST":
        email = clean_text(request.form.get("email"))
        password = request.form.get("password") or ""
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if not user.is_active:
                current_app.logger.warning(
                    "Failed login attempt (deactivated): email=%s ip=%s",
                    email,
                    request.remote_addr,
                )
                flash("Your account has been deactivated. Please contact support.", "danger")
                return render_template("login.html")
            session.clear()
            session.permanent = True
            session["user_id"] = user.id
            session["role"] = user.role
            current_app.logger.info(
                "Login: user_id=%s role=%s ip=%s",
                user.id,
                user.role,
                request.remote_addr,
            )
            flash("Welcome back!", "success")
            if user.role == "recruiter":
                return redirect(url_for("recruiter.dashboard"))
            if user.role == "admin":
                return redirect(url_for("admin.dashboard"))
            return redirect(url_for("candidate.dashboard"))
        current_app.logger.warning(
            "Failed login attempt: email=%s ip=%s",
            email,
            request.remote_addr,
        )
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

        try:
            valid = validate_email(email, check_deliverability=False)
            email = valid.email
        except EmailNotValidError as exc:
            flash(str(exc), "danger")
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
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Email already registered. Please login instead.", "danger")
            return redirect(url_for("auth.login"))

        flash("Account created successfully! Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("signup.html")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Logged out", "info")
    return redirect(url_for("auth.login"))
