# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# 获取当前文件所在目录（backend/），然后定位到项目根目录
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, "backend", "skin.db")
DB_URL = f"sqlite:///{DB_PATH.replace(os.sep, '/')}"

engine = create_engine(
    DB_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 强制建表！！！
def create_tables():
    Base.metadata.create_all(bind=engine)