from dotenv import load_dotenv
#在backend/.env文件中配置BAILIAN_API_KEY=你的阿里云百炼API密钥
load_dotenv()

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.api.detection import router as detection_router
from app.api.qa import router as qa_router
from app.api.profile import router as profile_router
from app.auth_config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from app.config import settings
from app.deps import get_current_user
from app.utils.file_utils import ensure_directories
from database import get_db, Base, engine, create_tables
from database.models import User, Conversation, Message

# 导入所有模型以确保表被创建
from database import models

# 确保目录存在
ensure_directories()

# 创建数据库表
create_tables()

import logging

from app.services.detection_service import detection_service

_logger = logging.getLogger(__name__)
_det_ok, _det_msg = detection_service.readiness()
if _det_ok:
    _logger.info("检测服务就绪: %s", settings.YOLO_MODEL_PATH)
else:
    _logger.warning("检测服务未就绪: %s", _det_msg)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="遥感目标检测平台后端API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")
# 与前端 baseURL（/api）对齐：/api/detection/...
app.include_router(detection_router, prefix="/api")
app.include_router(qa_router, prefix="/api")
app.include_router(profile_router, prefix="/api")

# --- 认证配置 ---
SECRET_KEY = "your-secret-key-here-keep-it-safe"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/register")
def register(
        username: str,
        email: str,
        password: str,
        db: Session = Depends(get_db)
):
    # 检查用户名是否存在
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 检查邮箱是否存在
    existing_email = db.query(User).filter(User.email == email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    hashed_password = get_password_hash(password)
    new_user = User(
        username=username,
        email=email,
        password_hash=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "注册成功", "user_id": str(new_user.id)}


@app.post("/token")
def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/conversations")
def get_my_conversations(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    return db.query(Conversation).filter(Conversation.user_id == current_user.id).all()


@app.post("/conversations")
def create_conversation(
        title: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    new_conv = Conversation(title=title, user_id=current_user.id)
    db.add(new_conv)
    db.commit()
    db.refresh(new_conv)
    return new_conv


@app.get("/conversations/{conv_id}/messages")
def get_messages(
        conv_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conv_id, Conversation.user_id == current_user.id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=403, detail="你无权查看此对话")
    return (
        db.query(Message)
        .filter(Message.conversation_id == conv_id, Message.user_id == current_user.id)
        .all()
    )


@app.post("/conversations/{conv_id}/messages")
def send_message(
        conv_id: int,
        content: str,
        role: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conv_id, Conversation.user_id == current_user.id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=403, detail="你无权操作此对话")
    new_msg = Message(
        conversation_id=conv_id,
        user_id=current_user.id,
        content=content,
        role=role,
    )
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return new_msg


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )