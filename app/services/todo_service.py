"""
待办事项服务
"""
import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import Todo
from app.models.schemas import TodoCreate, TodoResponse, TodoUpdate


class TodoService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_todos(self, user_id: uuid.UUID) -> list[TodoResponse]:
        """
        获取用户的所有待办
        """
        result = await self.db.execute(
            select(Todo)
            .where(Todo.user_id == user_id)
            .order_by(Todo.created_at.desc())
        )
        todos = result.scalars().all()
        
        return [
            TodoResponse(
                id=str(todo.id),
                user_id=str(todo.user_id),
                title=todo.title,
                description=todo.description,
                is_completed=todo.is_completed,
                start_at=todo.start_at,
                end_at=todo.end_at,
                all_day=todo.all_day,
                color=todo.color,
                created_at=todo.created_at,
                updated_at=todo.updated_at
            )
            for todo in todos
        ]

    async def create_todo(self, todo_data: TodoCreate, user_id: uuid.UUID) -> TodoResponse:
        """
        创建待办
        """
        new_todo = Todo(
            user_id=user_id,
            title=todo_data.title,
            description=todo_data.description,
            start_at=todo_data.start_at,
            end_at=todo_data.end_at,
            all_day=todo_data.all_day,
            color=todo_data.color
        )
        self.db.add(new_todo)
        await self.db.commit()
        await self.db.refresh(new_todo)
        
        return TodoResponse(
            id=str(new_todo.id),
            user_id=str(new_todo.user_id),
            title=new_todo.title,
            description=new_todo.description,
            is_completed=new_todo.is_completed,
            start_at=new_todo.start_at,
            end_at=new_todo.end_at,
            all_day=new_todo.all_day,
            color=new_todo.color,
            created_at=new_todo.created_at,
            updated_at=new_todo.updated_at
        )

    async def update_todo(
        self, todo_id: str, todo_data: TodoUpdate, user_id: uuid.UUID
    ) -> TodoResponse:
        """
        更新待办
        """
        result = await self.db.execute(
            select(Todo).where(
                Todo.id == uuid.UUID(todo_id),
                Todo.user_id == user_id
            )
        )
        todo = result.scalar_one_or_none()
        
        if not todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="待办不存在"
            )
        
        # 更新字段（只更新传入的非 None 值）
        update_data = todo_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(todo, field, value)
        
        await self.db.commit()
        await self.db.refresh(todo)
        
        return TodoResponse(
            id=str(todo.id),
            user_id=str(todo.user_id),
            title=todo.title,
            description=todo.description,
            is_completed=todo.is_completed,
            start_at=todo.start_at,
            end_at=todo.end_at,
            all_day=todo.all_day,
            color=todo.color,
            created_at=todo.created_at,
            updated_at=todo.updated_at
        )

    async def delete_todo(self, todo_id: str, user_id: uuid.UUID) -> None:
        """
        删除待办
        """
        result = await self.db.execute(
            select(Todo).where(
                Todo.id == uuid.UUID(todo_id),
                Todo.user_id == user_id
            )
        )
        todo = result.scalar_one_or_none()
        
        if not todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="待办不存在"
            )
        
        await self.db.delete(todo)
        await self.db.commit()
