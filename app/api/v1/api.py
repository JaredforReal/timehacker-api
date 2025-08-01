from fastapi import APIRouter

from app.api.v1.endpoints import auth, pomodoro, profile, todos

api_router = APIRouter()

# 包含所有端点路由
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(todos.router, tags=["todos"])
api_router.include_router(pomodoro.router, tags=["pomodoro"])
api_router.include_router(profile.router, tags=["profile"])
