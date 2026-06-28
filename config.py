import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
BASE_DIR_ABS = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")
    WTF_CSRF_ENABLED = True
    SEED_DEMO_USERS = os.getenv("SEED_DEMO_USERS", "false").lower() == "true"

    _env_db_url = os.environ.get("DATABASE_URL")
    if _env_db_url and _env_db_url.startswith("sqlite:///"):
        _sqlite_path = _env_db_url[len("sqlite:///") :]
        if not os.path.isabs(_sqlite_path):
            _env_db_url = "sqlite:///" + os.path.join(BASE_DIR_ABS, _sqlite_path)

    SQLALCHEMY_DATABASE_URI = _env_db_url or (
        "sqlite:///" + os.path.join(BASE_DIR_ABS, "instance", "app.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.getenv(
        "UPLOAD_FOLDER", str(BASE_DIR.joinpath("instance", "uploads"))
    )
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"pdf", "docx", "doc"}

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("FLASK_ENV", "production") != "development"
    PERMANENT_SESSION_LIFETIME = 3600

    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    _raw_mail_port = os.getenv("MAIL_PORT", "587")
    try:
        MAIL_PORT = int(_raw_mail_port)
    except (TypeError, ValueError):
        MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv(
        "MAIL_DEFAULT_SENDER", "noreply@recruitment.app"
    )

    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    GROQ_API_URL = os.getenv(
        "GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions"
    )


def ensure_instance_dirs():
    uploads = Path(Config.UPLOAD_FOLDER)
    uploads.mkdir(parents=True, exist_ok=True)
    instance = Path(BASE_DIR_ABS).joinpath("instance")
    instance.mkdir(parents=True, exist_ok=True)
