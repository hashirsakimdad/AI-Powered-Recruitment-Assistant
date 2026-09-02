import json
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFError

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
        flash("Too many requests. Please wait a moment and try again.", "warning")
        return redirect(request.referrer or url_for("auth.login")), 429

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return jsonify(
            {"error": "CSRF token missing or invalid. Please refresh the page."}
        ), 400

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

    if not app.config.get("TESTING"):
        with app.app_context():
            os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)
            os.makedirs(os.path.join(app.root_path, "instance", "uploads"), exist_ok=True)
            db.create_all()
            ensure_breakdown_columns()
            if app.config.get("SEED_DEMO_USERS", False):
                seed_demo_users(db.session)

    if not app.debug and not app.config.get("TESTING"):
        log_dir = os.path.join(os.path.dirname(__file__), "instance", "logs")
        os.makedirs(log_dir, exist_ok=True)
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, "app.log"),
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
        )
        file_handler.setFormatter(
            logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
        )
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info("Application startup complete")

    return app


app = create_app()

if __name__ == "__main__":
    debug = os.getenv("FLASK_ENV", "production") == "development"
    app.run(debug=debug, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
