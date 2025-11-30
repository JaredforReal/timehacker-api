"""
番茄钟服务
"""
import uuid
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import PomodoroSession, PomodoroSettings
from app.models.schemas import (
    PomodoroSessionCreate,
    PomodoroSessionResponse,
    PomodoroSettings as PomodoroSettingsSchema,
    PomodoroSettingsResponse,
)


class PomodoroService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(
        self, session_data: PomodoroSessionCreate, user_id: uuid.UUID
    ) -> PomodoroSessionResponse:
        """
        创建番茄钟会话
        """
        # 解析 completedAt
        completed_at = None
        if session_data.completedAt:
            try:
                completed_at = datetime.fromisoformat(
                    session_data.completedAt.replace("Z", "+00:00")
                )
            except ValueError:
                pass
        
        new_session = PomodoroSession(
            user_id=user_id,
            title=session_data.title,
            duration=session_data.duration,
            completed_at=completed_at
        )
        self.db.add(new_session)
        await self.db.commit()
        await self.db.refresh(new_session)
        
        return PomodoroSessionResponse(
            id=str(new_session.id),
            user_id=str(new_session.user_id),
            title=new_session.title,
            duration=new_session.duration,
            completedAt=new_session.completed_at.isoformat() if new_session.completed_at else None,
            created_at=new_session.created_at,
            updated_at=new_session.updated_at
        )

    async def get_sessions(self, user_id: uuid.UUID) -> list[PomodoroSessionResponse]:
        """
        获取番茄钟会话列表（最近50条）
        """
        result = await self.db.execute(
            select(PomodoroSession)
            .where(PomodoroSession.user_id == user_id)
            .order_by(PomodoroSession.completed_at.desc())
            .limit(50)
        )
        sessions = result.scalars().all()
        
        return [
            PomodoroSessionResponse(
                id=str(session.id),
                user_id=str(session.user_id),
                title=session.title,
                duration=session.duration,
                completedAt=session.completed_at.isoformat() if session.completed_at else None,
                created_at=session.created_at,
                updated_at=session.updated_at
            )
            for session in sessions
        ]

    async def get_settings(self, user_id: uuid.UUID) -> PomodoroSettingsResponse:
        """
        获取番茄钟设置
        """
        result = await self.db.execute(
            select(PomodoroSettings).where(PomodoroSettings.user_id == user_id)
        )
        settings = result.scalar_one_or_none()
        
        if not settings:
            # 创建默认设置
            settings = PomodoroSettings(
                user_id=user_id,
                work_time=25,
                short_break_time=5,
                long_break_time=15,
                sessions_until_long_break=4
            )
            self.db.add(settings)
            await self.db.commit()
            await self.db.refresh(settings)
        
        return PomodoroSettingsResponse(
            workTime=settings.work_time,
            shortBreakTime=settings.short_break_time,
            longBreakTime=settings.long_break_time,
            sessionsUntilLongBreak=settings.sessions_until_long_break
        )

    async def update_settings(
        self, settings_data: PomodoroSettingsSchema, user_id: uuid.UUID
    ) -> PomodoroSettingsResponse:
        """
        更新番茄钟设置
        """
        # 验证设置值
        if (
            settings_data.workTime < 1
            or settings_data.shortBreakTime < 1
            or settings_data.longBreakTime < 1
            or settings_data.sessionsUntilLongBreak < 1
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="所有设置值必须大于0"
            )
        
        result = await self.db.execute(
            select(PomodoroSettings).where(PomodoroSettings.user_id == user_id)
        )
        settings = result.scalar_one_or_none()
        
        if settings:
            # 更新现有设置
            settings.work_time = settings_data.workTime
            settings.short_break_time = settings_data.shortBreakTime
            settings.long_break_time = settings_data.longBreakTime
            settings.sessions_until_long_break = settings_data.sessionsUntilLongBreak
        else:
            # 创建新设置
            settings = PomodoroSettings(
                user_id=user_id,
                work_time=settings_data.workTime,
                short_break_time=settings_data.shortBreakTime,
                long_break_time=settings_data.longBreakTime,
                sessions_until_long_break=settings_data.sessionsUntilLongBreak
            )
            self.db.add(settings)
        
        await self.db.commit()
        await self.db.refresh(settings)
        
        return PomodoroSettingsResponse(
            workTime=settings.work_time,
            shortBreakTime=settings.short_break_time,
            longBreakTime=settings.long_break_time,
            sessionsUntilLongBreak=settings.sessions_until_long_break
        )
