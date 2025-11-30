"""
用户资料 API 端点
"""
import uuid

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.models.database import get_async_session
from app.models.orm import User
from app.models.schemas import AvatarUploadResponse, ProfileResponse, ProfileUpdate
from app.services.profile_service import ProfileService

router = APIRouter()


def get_profile_service(db: AsyncSession) -> ProfileService:
    return ProfileService(db)


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    获取个人资料
    """
    profile_service = get_profile_service(db)
    return await profile_service.get_profile(current_user.id)


@router.put("/profile", response_model=ProfileResponse)
async def update_profile(
    profile: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    更新个人资料
    """
    profile_service = get_profile_service(db)
    return await profile_service.update_profile(profile, current_user.id)


@router.post("/profile/avatar", response_model=AvatarUploadResponse)
async def upload_avatar(
    avatar: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    上传头像
    """
    profile_service = get_profile_service(db)
    return await profile_service.upload_avatar(avatar, current_user.id)
