from pydantic import BaseModel
from typing import Optional
import os

# 获取项目根目录（backend/app/ -> backend/ -> 项目根目录）
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
BACKEND_ROOT = os.path.join(PROJECT_ROOT, "backend")


class Settings(BaseModel):
    APP_NAME: str = "RSOD Detection Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 使用绝对路径，基于backend目录
    STATIC_DIR: str = os.path.join(BACKEND_ROOT, "static")
    UPLOAD_DIR: str = os.path.join(BACKEND_ROOT, "static", "uploads")
    RESULT_DIR: str = os.path.join(BACKEND_ROOT, "static", "results")
    
    YOLO_MODEL_PATH: str = os.path.join(BACKEND_ROOT, "app", "models", "yolo11n.pt")
    CONFIDENCE_THRESHOLD: float = 0.5
    IOU_THRESHOLD: float = 0.45
    
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"]


def get_settings() -> Settings:
    settings = Settings()
    
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    if hasattr(settings, key):
                        try:
                            setattr(settings, key, type(getattr(settings, key))(value))
                        except ValueError:
                            pass
    
    return settings


settings = get_settings()