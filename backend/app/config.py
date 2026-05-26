from pydantic import BaseModel
from typing import Optional
import os
from pathlib import Path


class Settings(BaseModel):
    APP_NAME: str = "RSOD Detection Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    STATIC_DIR: str = "static"
    UPLOAD_DIR: str = "static/uploads"
    RESULT_DIR: str = "static/results"
    
    YOLO_MODEL_PATH: str = ""
    CONFIDENCE_THRESHOLD: float = 0.5
    IOU_THRESHOLD: float = 0.45
    
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.YOLO_MODEL_PATH:
            backend_dir = Path(__file__).parent.parent
            project_root = backend_dir.parent
            model_path = project_root / "yolo11n.pt"
            if model_path.exists():
                self.YOLO_MODEL_PATH = str(model_path)
            else:
                self.YOLO_MODEL_PATH = "yolo11n.pt"


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