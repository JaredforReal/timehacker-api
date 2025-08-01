from typing import Any

from fastapi import APIRouter, Depends, File, UploadFile

from app.core.security import get_current_user
from app.dependencies import get_profile_service
from app.models.schemas import AvatarUploadResponse, ProfileResponse, ProfileUpdate
from app.services.profile_service import ProfileService

router = APIRouter()


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    current_user: Any = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
):
    """
    获取个人资料
    """
    return await profile_service.get_profile(current_user.user.id)


@router.put("/profile", response_model=ProfileResponse)
async def update_profile(
    profile: ProfileUpdate,
    current_user: Any = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
):
    """
    更新个人资料
    """
    return await profile_service.update_profile(profile, current_user.user.id)


@router.post("/profile/avatar", response_model=AvatarUploadResponse)
async def upload_avatar(
    avatar: UploadFile = File(...),
    current_user: Any = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
):
    """
    上传头像
    """
    return await profile_service.upload_avatar(avatar, current_user.user.id)
