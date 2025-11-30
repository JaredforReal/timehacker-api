"""
依赖注入
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_async_session
from app.services.auth_service import AuthService
from app.services.pomodoro_service import PomodoroService
from app.services.profile_service import ProfileService
from app.services.todo_service import TodoService


# 数据库会话依赖 - 由各端点直接使用 get_async_session


# 服务依赖 - 需要传入数据库会话
async def get_auth_service(db: AsyncSession) -> AuthService:
    return AuthService(db)


async def get_todo_service(db: AsyncSession) -> TodoService:
    return TodoService(db)


async def get_pomodoro_service(db: AsyncSession) -> PomodoroService:
    return PomodoroService(db)


async def get_profile_service(db: AsyncSession) -> ProfileService:
    return ProfileService(db)
