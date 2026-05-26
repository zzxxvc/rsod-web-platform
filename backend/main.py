from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from app.config import settings
from app.api.detection import router as detection_router
from app.utils.file_utils import ensure_directories

# 导入你自己的文件
from database import engine, Base, get_db, create_tables
from models import User, Conversation, Message, DetectionRecord
from app.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

ensure_directories()
create_tables()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="遥感目标检测平台后端API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

app.include_router(detection_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/profile")
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    detection_count = db.query(DetectionRecord).filter(DetectionRecord.user_id == current_user.id).count()
    conversation_count = db.query(Conversation).filter(Conversation.user_id == current_user.id).count()
    return {
        "success": True,
        "data": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "create_time": current_user.create_time.isoformat() if current_user.create_time else None,
            "detection_count": detection_count,
            "conversation_count": conversation_count,
        },
    }


class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class CreateConversationRequest(BaseModel):
    title: str

class MessageRequest(BaseModel):
    content: str
    role: str

# --- 注册接口 ---
@app.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    username = request.username
    password = request.password

    # 检查用户是否已存在
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    hashed_password = get_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "注册成功", "user_id": new_user.id}

# --- 登录接口，获取token ---
@app.post("/token")
def login_for_access_token(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- 获取当前用户的对话列表（只能看到自己的） ---
@app.get("/conversations")
def get_my_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    convs = db.query(Conversation).filter(Conversation.user_id == current_user.id).all()
    return convs

# --- 创建对话（自动绑定当前用户） ---
@app.post("/conversations")
def create_conversation(
    request: CreateConversationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_conv = Conversation(title=request.title, user_id=current_user.id)
    db.add(new_conv)
    db.commit()
    db.refresh(new_conv)
    return new_conv

# --- 获取对话下的消息（必须是自己的对话才能看） ---
@app.get("/conversations/{conv_id}/messages")
def get_messages(
    conv_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 先判断对话是否属于当前用户
    conv = db.query(Conversation).filter(Conversation.id == conv_id, Conversation.user_id == current_user.id).first()
    if not conv:
        raise HTTPException(status_code=403, detail="你无权查看此对话")
    messages = db.query(Message).filter(Message.conversation_id == conv_id, Message.user_id == current_user.id).all()
    return messages

# --- 给对话发消息（自动绑定用户） ---
@app.post("/conversations/{conv_id}/messages")
def send_message(
    conv_id: int,
    request: MessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 先判断对话是否属于当前用户
    conv = db.query(Conversation).filter(Conversation.id == conv_id, Conversation.user_id == current_user.id).first()
    if not conv:
        raise HTTPException(status_code=403, detail="你无权操作此对话")
    new_msg = Message(
        conversation_id=conv_id,
        user_id=current_user.id,
        content=request.content,
        role=request.role
    )
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return new_msg

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)