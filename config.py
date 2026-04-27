import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
BASE_DIR_ABS = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")

    # Prefer DATABASE_URL, but ensure SQLite points to an absolute file path.
    _env_db_url = os.environ.get("DATABASE_URL")
    if _env_db_url and _env_db_url.startswith("sqlite:///"):
        # Convert relative sqlite path (e.g. sqlite:///instance/app.db) to absolute.
        _sqlite_path = _env_db_url[len("sqlite:///") :]
        if not os.path.isabs(_sqlite_path):
            _env_db_url = "sqlite:///" + os.path.join(BASE_DIR_ABS, _sqlite_path)

    SQLALCHEMY_DATABASE_URI = (
        _env_db_url
        or ("sqlite:///" + os.path.join(BASE_DIR_ABS, "instance", "app.db"))
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.getenv(
        "UPLOAD_FOLDER", str(BASE_DIR.joinpath("instance", "uploads"))
    )
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB per resume
    ALLOWED_EXTENSIONS = {"pdf", "docx"}


def ensure_instance_dirs():
    uploads = Path(Config.UPLOAD_FOLDER)
    uploads.mkdir(parents=True, exist_ok=True)
    instance = Path(BASE_DIR_ABS).joinpath("instance")
    instance.mkdir(parents=True, exist_ok=True)

