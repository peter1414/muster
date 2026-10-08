"""
Configuration objects, split by environment.

Everything that matters in production is pulled from the environment —
see .env.example for the full list. The only hardcoded fallback is the
SQLite URI for zero-setup local dev, and a dev-only SECRET_KEY that the
app factory refuses to use in production.
"""
import os
from datetime import timedelta


def _normalize_db_url(url: str) -> str:
    # Some hosts (Heroku-style) still hand out "postgres://" URLs; SQLAlchemy
    # 1.4+ requires the "postgresql://" scheme.
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ERROR_MESSAGE_KEY = "error"

    SQLALCHEMY_DATABASE_URI = _normalize_db_url(
        os.environ.get("DATABASE_URL", "sqlite:///muster.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")
    RATELIMIT_ENABLED = True

    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")

    # Password reset tokens are signed with itsdangerous and expire after
    # this many seconds. See muster/auth.py.
    PASSWORD_RESET_MAX_AGE = 60 * 60  # 1 hour

    # No transactional email provider is wired up yet (see README). While
    # this is False, reset links/tokens are returned directly in the API
    # response and logged, instead of emailed, so the flow is usable in
    # dev/staging. Set an EMAIL_BACKEND and flip this before going live.
    EMAIL_SENDING_CONFIGURED = bool(os.environ.get("EMAIL_BACKEND"))


class DevConfig(BaseConfig):
    DEBUG = True
    SECRET_KEY = BaseConfig.SECRET_KEY or "dev-secret-change-this-before-you-ever-deploy"
    JWT_SECRET_KEY = BaseConfig.JWT_SECRET_KEY or SECRET_KEY


class TestConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    SECRET_KEY = "test-secret-key-at-least-32-bytes-long-000"
    JWT_SECRET_KEY = "test-secret-key-at-least-32-bytes-long-000"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    RATELIMIT_ENABLED = False


class ProdConfig(BaseConfig):
    DEBUG = False
    # SECRET_KEY intentionally has NO fallback here — create_app() raises at
    # startup if it's missing rather than silently running on a guessable key.


CONFIG_BY_NAME = {
    "development": DevConfig,
    "testing": TestConfig,
    "production": ProdConfig,
}
