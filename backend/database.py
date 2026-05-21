# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# 固定用 skin.db，不再变！
DB_URL = "sqlite:///./skin.db"

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