"""
待办事项 API 端点
"""
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.models.database import get_async_session
from app.models.orm import User
from app.models.schemas import TodoCreate, TodoResponse, TodoUpdate
from app.services.todo_service import TodoService

router = APIRouter()


def get_todo_service(db: AsyncSession) -> TodoService:
    return TodoService(db)


@router.get("/todos", response_model=list[TodoResponse])
async def get_todos(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    获取当前用户的所有Todo
    """
    todo_service = get_todo_service(db)
    return await todo_service.get_todos(current_user.id)


@router.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo: TodoCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    创建新的Todo
    """
    todo_service = get_todo_service(db)
    return await todo_service.create_todo(todo, current_user.id)


@router.put("/todos/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: str,
    todo: TodoUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    更新Todo
    """
    todo_service = get_todo_service(db)
    return await todo_service.update_todo(todo_id, todo, current_user.id)


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    删除Todo
    """
    todo_service = get_todo_service(db)
    await todo_service.delete_todo(todo_id, current_user.id)
    return None
