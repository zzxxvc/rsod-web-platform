from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# 1. 用户表
class User(Base):
    __tablename__ = "auth_user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    email = Column(String(100))
    create_time = Column(DateTime, default=datetime.utcnow)

# 2. 对话表
class Conversation(Base):
    __tablename__ = "conversation"

    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    user_id = Column(Integer, ForeignKey("auth_user.id"))  # 关键！
    create_time = Column(DateTime, default=datetime.utcnow)

# 3. 消息表
class Message(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversation.id"))
    content = Column(Text)
    role = Column(String(10))  # user / assistant
    user_id = Column(Integer, ForeignKey("auth_user.id"))  # 关键！
    create_time = Column(DateTime, default=datetime.utcnow)