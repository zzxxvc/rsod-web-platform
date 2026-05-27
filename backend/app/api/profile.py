from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_current_user
from app.models.schemas import ProfileStatsResponse, ProfileStats, UserProfileResponse, UserProfile
from app.services.detection_store import get_user_stats
from database import get_db
from database.models import User

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me", response_model=UserProfileResponse)
def get_profile_me(current_user: User = Depends(get_current_user)):
    return UserProfileResponse(
        success=True,
        message="获取成功",
        data=UserProfile(
            username=current_user.username,
            email=current_user.email,
            nickname=current_user.nickname,
            role=current_user.role or "user",
        ),
    )


@router.get("/stats", response_model=ProfileStatsResponse)
def get_profile_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    raw = get_user_stats(db, current_user)
    return ProfileStatsResponse(
        success=True,
        message="获取成功",
        data=ProfileStats(**raw),
    )
