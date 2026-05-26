# database/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL

# 根据数据库类型设置不同的连接参数
if DATABASE_URL.startswith("sqlite"):
    # SQLite 配置
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    # PostgreSQL 配置（用于 Docker）
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,      # 连接池预检，防止使用失效连接
        pool_size=10,            # 连接池大小
        max_overflow=20,         # 最大溢出连接数
        echo=False               # 设为 True 可以查看 SQL 日志
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """依赖注入：获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()