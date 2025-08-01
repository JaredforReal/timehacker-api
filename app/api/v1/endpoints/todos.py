from typing import Any

from fastapi import APIRouter, Depends, status

from app.core.security import get_current_user
from app.dependencies import get_todo_service
from app.models.schemas import TodoCreate, TodoResponse, TodoUpdate
from app.services.todo_service import TodoService

router = APIRouter()


@router.get("/todos", response_model=list[TodoResponse])
async def get_todos(
    current_user: Any = Depends(get_current_user),
    todo_service: TodoService = Depends(get_todo_service),
):
    """
    获取当前用户的所有Todo
    """
    return await todo_service.get_todos(current_user.user.id)


@router.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo: TodoCreate,
    current_user: Any = Depends(get_current_user),
    todo_service: TodoService = Depends(get_todo_service),
):
    """
    创建新的Todo
    """
    return await todo_service.create_todo(todo, current_user.user.id)


@router.put("/todos/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: str,
    todo: TodoUpdate,
    current_user: Any = Depends(get_current_user),
    todo_service: TodoService = Depends(get_todo_service),
):
    """
    更新Todo
    """
    return await todo_service.update_todo(todo_id, todo, current_user.user.id)


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: str,
    current_user: Any = Depends(get_current_user),
    todo_service: TodoService = Depends(get_todo_service),
):
    """
    删除Todo
    """
    await todo_service.delete_todo(todo_id, current_user.user.id)
    return None
