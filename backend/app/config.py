# app/config.py
import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from app.utils.paths import Paths


def _abs_backend_path(*parts: str) -> str:
    """始终返回 backend 下的绝对路径，避免受启动目录影响。"""
    return str(Paths.backend().joinpath(*parts).resolve())


def _resolve_path_value(value: str) -> str:
    """环境变量/ .env 中的路径统一解析为绝对路径。"""
    p = Path(value)
    if not p.is_absolute():
        p = Paths.backend() / p
    return str(p.resolve())


class Settings(BaseModel):
    APP_NAME: str = "RSOD Detection Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    DATABASE_URL: str = "postgresql://rsod_user:rsod_password@localhost:5432/rsod_db"

    STATIC_DIR: str = _abs_backend_path("static")
    UPLOAD_DIR: str = _abs_backend_path("static", "uploads")
    RESULT_DIR: str = _abs_backend_path("static", "results")

    YOLO_MODEL_PATH: str = _abs_backend_path("app", "models", "yolo11n.pt")
    CONFIDENCE_THRESHOLD: float = 0.5
    IOU_THRESHOLD: float = 0.45

    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]


_PATH_KEYS = frozenset({"STATIC_DIR", "UPLOAD_DIR", "RESULT_DIR", "YOLO_MODEL_PATH"})


def get_settings() -> Settings:
    settings = Settings()

    if os.getenv("DATABASE_URL"):
        settings.DATABASE_URL = os.getenv("DATABASE_URL")

    env_file = Paths.backend() / ".env"
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    if hasattr(settings, key):
                        try:
                            if value.lower() in ("true", "false"):
                                value = value.lower() == "true"
                            cast = type(getattr(settings, key))
                            parsed = cast(value)
                            if key in _PATH_KEYS and isinstance(parsed, str):
                                parsed = _resolve_path_value(parsed)
                            setattr(settings, key, parsed)
                        except ValueError:
                            pass

    return settings


settings = get_settings()
DATABASE_URL = settings.DATABASE_URL
