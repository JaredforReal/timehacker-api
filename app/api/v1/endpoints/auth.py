"""
认证相关 API 端点
"""
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_async_session
from app.models.schemas import (
    MessageResponse,
    PasswordResetConfirm,
    PasswordResetRequest,
    TokenRefreshRequest,
    TokenResponse,
    TokenResponseWithRefresh,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter()


def get_auth_service(db: AsyncSession) -> AuthService:
    return AuthService(db)


@router.post("/register", response_model=UserResponse)
async def register(
    user: UserRegister,
    db: AsyncSession = Depends(get_async_session),
):
    """
    用户注册
    """
    auth_service = get_auth_service(db)
    return await auth_service.register(user)


@router.post("/token", response_model=TokenResponseWithRefresh)
async def login(
    user: UserLogin,
    db: AsyncSession = Depends(get_async_session),
):
    """
    用户登录
    """
    auth_service = get_auth_service(db)
    return await auth_service.login(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_request: TokenRefreshRequest,
    db: AsyncSession = Depends(get_async_session),
):
    """
    刷新访问令牌
    """
    auth_service = get_auth_service(db)
    return await auth_service.refresh_token(refresh_request.refresh_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    refresh_request: TokenRefreshRequest,
    db: AsyncSession = Depends(get_async_session),
):
    """
    用户登出（撤销刷新令牌）
    """
    auth_service = get_auth_service(db)
    await auth_service.logout(refresh_request.refresh_token)
    return MessageResponse(message="登出成功")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    reset_request: PasswordResetRequest,
    db: AsyncSession = Depends(get_async_session),
):
    """
    请求密码重置
    """
    auth_service = get_auth_service(db)
    return await auth_service.forgot_password(reset_request.email)


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    reset_confirm: PasswordResetConfirm,
    db: AsyncSession = Depends(get_async_session),
):
    """
    确认密码重置
    """
    auth_service = get_auth_service(db)
    return await auth_service.reset_password(reset_confirm.token, reset_confirm.new_password)
