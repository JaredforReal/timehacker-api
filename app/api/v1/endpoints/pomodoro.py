from typing import Any

from fastapi import APIRouter, Depends, status

from app.core.security import get_current_user
from app.dependencies import get_pomodoro_service
from app.models.schemas import (
    PomodoroSessionCreate,
    PomodoroSessionResponse,
    PomodoroSettings,
)
from app.services.pomodoro_service import PomodoroService

router = APIRouter()


@router.post(
    "/pomodoro/sessions",
    response_model=PomodoroSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_pomodoro_session(
    session: PomodoroSessionCreate,
    current_user: Any = Depends(get_current_user),
    pomodoro_service: PomodoroService = Depends(get_pomodoro_service),
):
    """
    创建番茄钟会话
    """
    return await pomodoro_service.create_session(session, current_user.user.id)


@router.get("/pomodoro/sessions", response_model=list[PomodoroSessionResponse])
async def get_pomodoro_sessions(
    current_user: Any = Depends(get_current_user),
    pomodoro_service: PomodoroService = Depends(get_pomodoro_service),
):
    """
    获取番茄钟会话列表
    """
    return await pomodoro_service.get_sessions(current_user.user.id)


@router.get("/pomodoro/settings", response_model=PomodoroSettings)
async def get_pomodoro_settings(
    current_user: Any = Depends(get_current_user),
    pomodoro_service: PomodoroService = Depends(get_pomodoro_service),
):
    """
    获取番茄钟设置
    """
    return await pomodoro_service.get_settings(current_user.user.id)


@router.put("/pomodoro/settings", response_model=PomodoroSettings)
async def update_pomodoro_settings(
    settings: PomodoroSettings,
    current_user: Any = Depends(get_current_user),
    pomodoro_service: PomodoroService = Depends(get_pomodoro_service),
):
    """
    更新番茄钟设置
    """
    return await pomodoro_service.update_settings(settings, current_user.user.id)
