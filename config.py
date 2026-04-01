import os

from dotenv import load_dotenv

# Load environment variables from the project root `.env` (if present).
# This makes it work even if you start `python app.py` from another directory.
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


def _env_int(name: str, default: int) -> int:
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


class Config:
    SECRET_KEY = os.environ.get("HOYBOOKING_SECRET_KEY", "dev-secret-change-me")

    DB_HOST = os.environ.get("HOYBOOKING_DB_HOST", "127.0.0.1")
    # Default for local MySQL. Override with HOYBOOKING_DB_PORT if needed.
    DB_PORT = _env_int("HOYBOOKING_DB_PORT", 3306)
    DB_USER = os.environ.get("HOYBOOKING_DB_USER", "root")
    DB_PASSWORD = os.environ.get("HOYBOOKING_DB_PASSWORD", "")
    DB_NAME = os.environ.get("HOYBOOKING_DB_NAME", "hoybooking")
    DB_CHARSET = os.environ.get("HOYBOOKING_DB_CHARSET", "utf8mb4")

    # SQLAlchemy will use PyMySQL as the MySQL driver.
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        f"?charset={DB_CHARSET}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

