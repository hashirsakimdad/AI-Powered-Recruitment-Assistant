import json
import os
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_migrate import Migrate

from app_helpers import ensure_breakdown_columns
from blueprints import register_blueprints
from config import Config, ensure_instance_dirs
from extensions import csrf, limiter, mail
from models import User, db, seed_demo_users


def create_app(config_overrides=None):
    ensure_instance_dirs()
    app = Flask(
        __name__,
        instance_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), "instance"),
    )
    app.config.from_object(Config)
    if config_overrides:
        app.config.update(config_overrides)
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

    @app.template_filter("from_json")
    def from_json_filter(value):
        try:
            return json.loads(value or "[]")
        except (TypeError, json.JSONDecodeError):
            return []

    @app.context_processor
    def inject_helpers():
        from urllib.parse import urlencode

        def pagination_url(page_num):
            args = request.args.to_dict(flat=True)
            args.pop("page", None)
            args["page"] = page_num
            qs = urlencode(args)
            return f"{request.path}?{qs}" if qs else f"{request.path}?page={page_num}"

        return dict(pagination_url=pagination_url)

    @app.route("/")
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

    if not app.config.get("TESTING"):
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
