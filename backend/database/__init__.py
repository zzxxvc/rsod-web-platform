# database/__init__.py
from .base import Base
from .session import get_db, SessionLocal, engine
from .models import (
    User,
    DetectionRecord,
    DetectionResult,
    TargetCategory,
    AiQaRecord,
    ModelVersion,
    Conversation,
    Message,
)


def create_tables():
    """创建所有表"""
    from . import models  # 导入模型以确保注册
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """删除所有表（慎用）"""
    Base.metadata.drop_all(bind=engine)


__all__ = [
    "Base",
    "get_db",
    "create_tables",
    "drop_tables",
    "SessionLocal",
    "engine",
    "User",
    "DetectionRecord",
    "DetectionResult",
    "TargetCategory",
    "AiQaRecord",
    "ModelVersion",
    "Conversation",
    "Message",
]