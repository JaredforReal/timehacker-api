from fastapi import APIRouter, Depends

from app.dependencies import get_auth_service
from app.models.schemas import (
    MessageResponse,
    PasswordResetRequest,
    TokenResponse,
    UserLogin,
)
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/token", response_model=TokenResponse)
async def login(user: UserLogin, auth_service: AuthService = Depends(get_auth_service)):
    """
    用户登录
    """
    return await auth_service.login(user)


@router.post("/auth/reset-password", response_model=MessageResponse)
async def request_password_reset(
    reset_request: PasswordResetRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    请求密码重置
    """
    return await auth_service.request_password_reset(reset_request)
