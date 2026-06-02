import os
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_migrate import Migrate

from app_helpers import ensure_breakdown_columns
from blueprints import register_blueprints
from config import Config, ensure_instance_dirs
from extensions import csrf, limiter, mail
from models import db, seed_demo_users


def create_app():
    ensure_instance_dirs()
    app = Flask(
        __name__,
        instance_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), "instance"),
    )
    app.config.from_object(Config)
    db.init_app(app)
    Migrate(app, db)
    csrf.init_app(app)
    limiter.init_app(app)
    mail.init_app(app)

    @app.errorhandler(429)
    def ratelimit_handler(e):
        if request.endpoint == "auth.login":
            flash("Too many login attempts. Please wait a minute.", "danger")
            return render_template("login.html"), 429
        return render_template("rate_limit.html"), 429

    @app.before_request
    def ensure_upload_dir():
        Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    register_blueprints(app)

    @app.route("/")
    def index():
        if "user_id" in session:
            role = session.get("role")
            if role == "recruiter":
                return redirect(url_for("recruiter.dashboard"))
            if role == "admin":
                return redirect(url_for("admin.dashboard"))
            return redirect(url_for("candidate.dashboard"))
        return render_template("index.html")

    with app.app_context():
        os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)
        os.makedirs(os.path.join(app.root_path, "instance", "uploads"), exist_ok=True)
        db.create_all()
        ensure_breakdown_columns()
        seed_demo_users(db.session)
    return app


app = create_app()

if __name__ == "__main__":
    debug = os.getenv("FLASK_ENV", "production") == "development"
    app.run(debug=debug, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
