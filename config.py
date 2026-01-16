import os
from pathlib import Path

BASE_DIR = Path(__file__).parent


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR.joinpath('instance', 'app.db')}",
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
    instance = BASE_DIR.joinpath("instance")
    instance.mkdir(parents=True, exist_ok=True)

