import os
import re
from urllib.parse import urlsplit

from dotenv import load_dotenv
from sqlalchemy.engine import URL
from sqlalchemy.engine.url import make_url

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


def _build_uri_from_parts() -> str:
    host = (os.environ.get("HOYBOOKING_DB_HOST") or os.environ.get("MYSQLHOST") or "127.0.0.1").strip()
    user = (os.environ.get("HOYBOOKING_DB_USER") or os.environ.get("MYSQLUSER") or "root").strip()
    password = os.environ.get("HOYBOOKING_DB_PASSWORD")
    if password is None:
        password = os.environ.get("MYSQLPASSWORD", "")
    name = (os.environ.get("HOYBOOKING_DB_NAME") or os.environ.get("MYSQLDATABASE") or "hoybooking").strip()
    charset = (os.environ.get("HOYBOOKING_DB_CHARSET") or "utf8mb4").strip()

    port = _env_int_or_none("HOYBOOKING_DB_PORT")
    if port is None:
        port = _env_int_or_none("MYSQLPORT")

    # Allow host values that already contain ':port'.
    if ":" in host and not host.startswith("["):
        host_part, maybe_port = host.rsplit(":", 1)
        parsed_inline_port = None
        try:
            parsed_inline_port = int(maybe_port)
        except Exception:
            parsed_inline_port = None
        if parsed_inline_port is not None:
            host = host_part
            if port is None:
                port = parsed_inline_port

    return str(
        URL.create(
            drivername="mysql+pymysql",
            username=user,
            password=password,
            host=host,
            port=port,
            database=name,
            query={"charset": charset},
        )
    )


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
        _candidate_url = _raw_url.replace("mysql://", "mysql+pymysql://", 1)
        try:
            # Validate URL early to avoid Flask-SQLAlchemy init crash.
            make_url(_candidate_url)
            SQLALCHEMY_DATABASE_URI = _candidate_url
        except Exception:
            # Railway/Render can provide malformed URL with empty port (host:/db).
            _fixed_url = re.sub(r"(@[^/:]+):/(?=[^/])", r"\1/", _candidate_url)
            try:
                make_url(_fixed_url)
                SQLALCHEMY_DATABASE_URI = _fixed_url
            except Exception:
                # Last-resort: derive from split env vars (Railway MYSQLHOST/MYSQLPORT/etc).
                parts = urlsplit(_raw_url)
                os.environ.setdefault("MYSQLHOST", parts.hostname or "")
                os.environ.setdefault("MYSQLPORT", str(parts.port or ""))
                os.environ.setdefault("MYSQLUSER", parts.username or "")
                os.environ.setdefault("MYSQLPASSWORD", parts.password or "")
                os.environ.setdefault("MYSQLDATABASE", (parts.path or "").lstrip("/"))
                SQLALCHEMY_DATABASE_URI = _build_uri_from_parts()
    else:
        SQLALCHEMY_DATABASE_URI = _build_uri_from_parts()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

