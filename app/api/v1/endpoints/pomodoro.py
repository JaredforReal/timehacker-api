"""
番茄钟 API 端点
"""
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.models.database import get_async_session
from app.models.orm import User
from app.models.schemas import (
    PomodoroSessionCreate,
    PomodoroSessionResponse,
    PomodoroSettings,
    PomodoroSettingsResponse,
)
from app.services.pomodoro_service import PomodoroService

router = APIRouter()


def get_pomodoro_service(db: AsyncSession) -> PomodoroService:
    return PomodoroService(db)


@router.post(
    "/pomodoro/sessions",
    response_model=PomodoroSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_pomodoro_session(
    session: PomodoroSessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    创建番茄钟会话
    """
    pomodoro_service = get_pomodoro_service(db)
    return await pomodoro_service.create_session(session, current_user.id)


@router.get("/pomodoro/sessions", response_model=list[PomodoroSessionResponse])
async def get_pomodoro_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    获取番茄钟会话列表
    """
    pomodoro_service = get_pomodoro_service(db)
    return await pomodoro_service.get_sessions(current_user.id)


@router.get("/pomodoro/settings", response_model=PomodoroSettingsResponse)
async def get_pomodoro_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    获取番茄钟设置
    """
    pomodoro_service = get_pomodoro_service(db)
    return await pomodoro_service.get_settings(current_user.id)


@router.put("/pomodoro/settings", response_model=PomodoroSettingsResponse)
async def update_pomodoro_settings(
    settings: PomodoroSettings,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    更新番茄钟设置
    """
    pomodoro_service = get_pomodoro_service(db)
    return await pomodoro_service.update_settings(settings, current_user.id)
