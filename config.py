import os

from dotenv import load_dotenv
from sqlalchemy.engine import URL

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


def _env_int_or_none(name: str):
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


class Config:
    SECRET_KEY = os.environ.get("HOYBOOKING_SECRET_KEY", "dev-secret-change-me")

    DB_HOST = os.environ.get("HOYBOOKING_DB_HOST", "127.0.0.1")
    # Default for local MySQL. Override with HOYBOOKING_DB_PORT if needed.
    DB_PORT = _env_int("HOYBOOKING_DB_PORT", 3306)
    DB_USER = os.environ.get("HOYBOOKING_DB_USER", "root")
    DB_PASSWORD = os.environ.get("HOYBOOKING_DB_PASSWORD", "")
    DB_NAME = os.environ.get("HOYBOOKING_DB_NAME", "hoybooking")
    DB_CHARSET = os.environ.get("HOYBOOKING_DB_CHARSET", "utf8mb4")

    # Prefer explicit app vars; fallback to Railway-provided MYSQL_URL style vars.
    _raw_url = (
        os.environ.get("HOYBOOKING_DATABASE_URL")
        or os.environ.get("MYSQL_URL")
        or os.environ.get("MYSQL_PUBLIC_URL")
        or ""
    ).strip()
    if _raw_url:
        SQLALCHEMY_DATABASE_URI = _raw_url.replace("mysql://", "mysql+pymysql://", 1)
    else:
        _port = _env_int_or_none("HOYBOOKING_DB_PORT")
        SQLALCHEMY_DATABASE_URI = str(
            URL.create(
                drivername="mysql+pymysql",
                username=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=_port,
                database=DB_NAME,
                query={"charset": DB_CHARSET},
            )
        )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

