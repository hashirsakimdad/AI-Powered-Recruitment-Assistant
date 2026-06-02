from blueprints.admin import admin_bp
from blueprints.api import api_bp
from blueprints.auth import auth_bp
from blueprints.candidate import candidate_bp
from blueprints.recruiter import recruiter_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(recruiter_bp)
    app.register_blueprint(candidate_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)
