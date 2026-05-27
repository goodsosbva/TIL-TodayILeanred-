from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import os


def _load_env_file() -> None:
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} is not configured")

    return value


@dataclass(frozen=True)
class Settings:
    database_username: str
    database_password: str
    database_host: str
    database_port: int
    database_name: str
    jwt_secret: str
    email_sender: str
    email_password: str
    email_host: str
    email_port: int
    celery_broker_url: str
    celery_backend_url: str
    app_host: str
    app_port: int


@lru_cache
def get_settings() -> Settings:
    _load_env_file()

    return Settings(
        database_username=_get_required_env("DATABASE_USERNAME"),
        database_password=_get_required_env("DATABASE_PASSWORD"),
        database_host=_get_required_env("DATABASE_HOST"),
        database_port=int(_get_required_env("DATABASE_PORT")),
        database_name=_get_required_env("DATABASE_NAME"),
        jwt_secret=_get_required_env("JWT_SECRET"),
        email_sender=_get_required_env("EMAIL_SENDER"),
        email_password=_get_required_env("EMAIL_PASSWORD").replace(" ", ""),
        email_host=_get_required_env("EMAIL_HOST"),
        email_port=int(_get_required_env("EMAIL_PORT")),
        celery_broker_url=_get_required_env("CELERY_BROKER_URL"),
        celery_backend_url=_get_required_env("CELERY_BACKEND_URL"),
        app_host=_get_required_env("APP_HOST"),
        app_port=int(_get_required_env("APP_PORT")),
    )
