import os
from pathlib import Path

BASE_DIR = Path(__file__).parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    # Use a relative SQLite path by default to avoid Windows URL parsing issues
    # when the project lives under a path with spaces (e.g. "ZEESHAN FYP").
    # Flask-SQLAlchemy resolves relative SQLite paths against `app.instance_path`.
    # Using `../instance/app.db` ensures the final path is `<project>/instance/app.db`
    # (and avoids embedding a Windows path with spaces into the SQLite URL).
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///../instance/app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.getenv(
        "UPLOAD_FOLDER", str(BASE_DIR.joinpath("instance", "uploads"))
    )
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB per resume
    ALLOWED_EXTENSIONS = {"pdf", "docx"}


def ensure_instance_dirs():
    uploads = Path(Config.UPLOAD_FOLDER)
    uploads.mkdir(parents=True, exist_ok=True)
    instance = BASE_DIR.joinpath("instance")
    instance.mkdir(parents=True, exist_ok=True)

