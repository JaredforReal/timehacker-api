from fastapi import HTTPException, status
from supabase import Client

from app.models.schemas import TodoCreate, TodoResponse, TodoUpdate


class TodoService:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def get_todos(self, user_id: str) -> list[TodoResponse]:
        """
        获取用户的所有Todo
        """
        try:
            response = (
                self.supabase.table("todos")
                .select("*")
                .eq("user_id", user_id)
                .execute()
            )

            return response.data
        except Exception as e:
            print(f"Error fetching todos: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def create_todo(self, todo: TodoCreate, user_id: str) -> TodoResponse:
        """
        创建新的Todo
        """
        try:
            todo_data = todo.model_dump()
            todo_data["user_id"] = str(user_id)

            response = self.supabase.table("todos").insert(todo_data).execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create todo",
                )

            return response.data[0]
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def update_todo(
        self, todo_id: str, todo: TodoUpdate, user_id: str
    ) -> TodoResponse:
        """
        更新Todo
        """
        try:
            # 验证Todo存在且属于当前用户
            existing = (
                self.supabase.table("todos")
                .select("*")
                .eq("id", todo_id)
                .eq("user_id", str(user_id))
                .execute()
            )

            if not existing.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
                )

            # 更新Todo
            update_data = todo.model_dump(exclude_unset=True)
            response = (
                self.supabase.table("todos")
                .update(update_data)
                .eq("id", todo_id)
                .execute()
            )

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to update todo",
                )

            return response.data[0]
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def delete_todo(self, todo_id: str, user_id: str) -> None:
        """
        删除Todo
        """
        try:
            # 验证Todo存在且属于当前用户
            existing = (
                self.supabase.table("todos")
                .select("*")
                .eq("id", todo_id)
                .eq("user_id", str(user_id))
                .execute()
            )

            if not existing.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
                )

            # 删除Todo
            self.supabase.table("todos").delete().eq("id", todo_id).execute()

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )
