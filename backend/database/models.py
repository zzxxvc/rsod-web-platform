from sqlalchemy import (
    Column, Integer, String, Float, Text,
    Boolean, DateTime, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(50))
    role = Column(String(20), default="user")
    avatar_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    detections = relationship("DetectionRecord", back_populates="user", cascade="all, delete-orphan")
    ai_qas = relationship("AiQaRecord", back_populates="user", cascade="all, delete-orphan")
    # 添加对话和消息的关系
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")


class DetectionRecord(Base):
    __tablename__ = "detection_records"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(20), nullable=False)
    status = Column(String(20), default="pending")
    model_name = Column(String(50), nullable=False)
    model_version = Column(String(20), default="1.0.0")
    total_objects = Column(Integer, default=0)
    detection_time = Column(Float)
    original_image_key = Column(String(500))
    result_image_key = Column(String(500))
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="detections")
    results = relationship("DetectionResult", back_populates="record", cascade="all, delete-orphan")


class DetectionResult(Base):
    __tablename__ = "detection_results"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    record_id = Column(UUID(as_uuid=True), ForeignKey("detection_records.id", ondelete="CASCADE"), nullable=False)
    x1 = Column(Float, nullable=False)
    y1 = Column(Float, nullable=False)
    x2 = Column(Float, nullable=False)
    y2 = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    class_id = Column(Integer, nullable=False)
    class_name = Column(String(50), nullable=False)
    chinese_name = Column(String(50))

    record = relationship("DetectionRecord", back_populates="results")


class TargetCategory(Base):
    __tablename__ = "target_categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    chinese_name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    icon_url = Column(String(500))
    color = Column(String(20), default="#10b981")
    enabled = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AiQaRecord(Base):
    __tablename__ = "ai_qa_records"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text)
    model_name = Column(String(50))
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="ai_qas")


class ModelVersion(Base):
    __tablename__ = "model_versions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)
    version = Column(String(20), nullable=False)
    description = Column(Text)
    model_key = Column(String(500))
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# 添加 Conversation 和 Message 模型
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), default="新对话")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")
    user = relationship("User", back_populates="messages")