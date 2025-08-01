from fastapi import Depends
from supabase import Client

from app.models.database import get_supabase_client
from app.services.auth_service import AuthService
from app.services.pomodoro_service import PomodoroService
from app.services.profile_service import ProfileService
from app.services.todo_service import TodoService


# Supabase客户端依赖
def get_supabase() -> Client:
    return get_supabase_client()


# 服务依赖
def get_auth_service(supabase: Client = Depends(get_supabase)) -> AuthService:
    return AuthService(supabase)


def get_todo_service(supabase: Client = Depends(get_supabase)) -> TodoService:
    return TodoService(supabase)


def get_pomodoro_service(supabase: Client = Depends(get_supabase)) -> PomodoroService:
    return PomodoroService(supabase)


def get_profile_service(supabase: Client = Depends(get_supabase)) -> ProfileService:
    return ProfileService(supabase)
