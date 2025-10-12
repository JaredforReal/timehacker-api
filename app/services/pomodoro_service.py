from fastapi import HTTPException, status
from supabase import Client

from app.models.schemas import (
    PomodoroSessionCreate,
    PomodoroSessionResponse,
    PomodoroSettings,
)


class PomodoroService:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def create_session(
        self, session: PomodoroSessionCreate, user_id: str
    ) -> PomodoroSessionResponse:
        """
        创建番茄钟会话
        """
        try:
            session_data = {
                "title": session.title,
                "duration": session.duration,
                "completedat": session.completedAt,
                "user_id": str(user_id),
            }

            response = (
                self.supabase.table("pomodoro_sessions").insert(session_data).execute()
            )

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create pomodoro session",
                )

            result = dict(response.data[0])
            if "completedat" in result:
                result["completedAt"] = result.pop("completedat")

            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def get_sessions(self, user_id: str) -> list[PomodoroSessionResponse]:
        """
        获取用户的番茄钟会话列表
        """
        try:
            response = (
                self.supabase.table("pomodoro_sessions")
                .select("*")
                .eq("user_id", str(user_id))
                .order("completedat", desc=True)
                .limit(50)
                .execute()
            )

            result = []
            for session in response.data:
                session_dict = dict(session)
                # 兼容大小写与命名差异
                if "completedat" in session_dict:
                    session_dict["completedAt"] = session_dict.pop("completedat")
                # 标题字段兜底
                if "title" not in session_dict:
                    session_dict["title"] = None
                result.append(session_dict)

            return result
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def get_settings(self, user_id: str) -> PomodoroSettings:
        """
        获取用户的番茄钟设置
        """
        try:
            response = (
                self.supabase.table("pomodoro_settings")
                .select("*")
                .eq("user_id", str(user_id))
                .execute()
            )

            if response.data and len(response.data) > 0:
                settings = dict(response.data[0])
                return self._convert_settings_from_db(settings)

            # 如果未找到设置，创建默认设置
            default_settings = {
                "user_id": str(user_id),
                "worktime": 25,
                "shortbreaktime": 5,
                "longbreaktime": 15,
                "sessionsuntillongbreak": 4,
            }

            create_response = (
                self.supabase.table("pomodoro_settings")
                .insert(default_settings)
                .execute()
            )

            if create_response.data:
                settings = dict(create_response.data[0])
                return self._convert_settings_from_db(settings)
            else:
                return PomodoroSettings(
                    workTime=25,
                    shortBreakTime=5,
                    longBreakTime=15,
                    sessionsUntilLongBreak=4,
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def update_settings(
        self, settings: PomodoroSettings, user_id: str
    ) -> PomodoroSettings:
        """
        更新用户的番茄钟设置
        """
        try:
            # 验证设置值
            if (
                settings.workTime < 1
                or settings.shortBreakTime < 1
                or settings.longBreakTime < 1
                or settings.sessionsUntilLongBreak < 1
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="All settings values must be greater than 0",
                )

            settings_data = self._convert_settings_to_db(settings, user_id)

            # 检查是否已存在设置
            existing = (
                self.supabase.table("pomodoro_settings")
                .select("*")
                .eq("user_id", str(user_id))
                .execute()
            )

            if existing.data and len(existing.data) > 0:
                response = (
                    self.supabase.table("pomodoro_settings")
                    .update(settings_data)
                    .eq("user_id", str(user_id))
                    .execute()
                )
            else:
                response = (
                    self.supabase.table("pomodoro_settings")
                    .insert(settings_data)
                    .execute()
                )

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to update pomodoro settings",
                )

            settings_dict = dict(response.data[0])
            return self._convert_settings_from_db(settings_dict)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    def _convert_settings_from_db(self, db_settings: dict) -> PomodoroSettings:
        """
        将数据库中的设置转换为响应模型
        """
        return PomodoroSettings(
            workTime=db_settings.get("worktime", 25),
            shortBreakTime=db_settings.get("shortbreaktime", 5),
            longBreakTime=db_settings.get("longbreaktime", 15),
            sessionsUntilLongBreak=db_settings.get("sessionsuntillongbreak", 4),
        )

    def _convert_settings_to_db(self, settings: PomodoroSettings, user_id: str) -> dict:
        """
        将设置模型转换为数据库格式
        """
        return {
            "user_id": str(user_id),
            "worktime": settings.workTime,
            "shortbreaktime": settings.shortBreakTime,
            "longbreaktime": settings.longBreakTime,
            "sessionsuntillongbreak": settings.sessionsUntilLongBreak,
        }
