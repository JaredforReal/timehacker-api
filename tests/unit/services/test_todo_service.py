from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from app.models.schemas import TodoCreate, TodoUpdate
from app.services.todo_service import TodoService


class TestTodoService:
    """测试Todo服务"""

    def test_init(self, mock_supabase_client):
        """测试服务初始化"""
        service = TodoService(mock_supabase_client)
        assert service.supabase == mock_supabase_client

    @pytest.mark.asyncio
    async def test_get_todos_success(self, mock_supabase_client, sample_todo_data):
        """测试成功获取todos"""
        user_id = "test-user-id"

        # 模拟Supabase响应
        mock_response = Mock()
        mock_response.data = [sample_todo_data]

        mock_table = mock_supabase_client.table.return_value
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.execute.return_value = mock_response

        # 调用服务
        service = TodoService(mock_supabase_client)
        result = await service.get_todos(user_id)

        # 验证结果
        assert result == [sample_todo_data]

        # 验证调用参数
        mock_supabase_client.table.assert_called_once_with("todos")
        mock_table.select.assert_called_once_with("*")
        mock_table.eq.assert_called_once_with("user_id", user_id)
        mock_table.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_todos_database_error(self, mock_supabase_client):
        """测试获取todos时数据库错误"""
        user_id = "test-user-id"

        # 模拟数据库异常
        mock_table = mock_supabase_client.table.return_value
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.execute.side_effect = Exception("Database connection error")

        service = TodoService(mock_supabase_client)

        with pytest.raises(HTTPException) as exc_info:
            await service.get_todos(user_id)

        assert exc_info.value.status_code == 500
        assert "Internal Server Error" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_create_todo_success(self, mock_supabase_client, sample_todo_data):
        """测试成功创建todo"""
        todo_create = TodoCreate(title="Test Todo", description="Test Description")
        user_id = "test-user-id"

        # 模拟Supabase响应
        mock_response = Mock()
        mock_response.data = [sample_todo_data]

        mock_table = mock_supabase_client.table.return_value
        mock_table.insert.return_value = mock_table
        mock_table.execute.return_value = mock_response

        service = TodoService(mock_supabase_client)
        result = await service.create_todo(todo_create, user_id)

        # 验证结果
        assert result == sample_todo_data

        # 验证调用参数
        expected_data = {
            "title": "Test Todo",
            "description": "Test Description",
            "user_id": user_id,
        }
        mock_table.insert.assert_called_once_with(expected_data)

    @pytest.mark.asyncio
    async def test_create_todo_no_data_returned(self, mock_supabase_client):
        """测试创建todo失败（无数据返回）"""
        todo_create = TodoCreate(title="Test Todo")
        user_id = "test-user-id"

        # 模拟Supabase返回空数据
        mock_response = Mock()
        mock_response.data = None

        mock_table = mock_supabase_client.table.return_value
        mock_table.insert.return_value = mock_table
        mock_table.execute.return_value = mock_response

        service = TodoService(mock_supabase_client)

        with pytest.raises(HTTPException) as exc_info:
            await service.create_todo(todo_create, user_id)

        assert exc_info.value.status_code == 400
        assert "Failed to create todo" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_create_todo_database_error(self, mock_supabase_client):
        """测试创建todo时数据库错误"""
        todo_create = TodoCreate(title="Test Todo")
        user_id = "test-user-id"

        mock_table = mock_supabase_client.table.return_value
        mock_table.insert.side_effect = Exception("Database error")

        service = TodoService(mock_supabase_client)

        with pytest.raises(HTTPException) as exc_info:
            await service.create_todo(todo_create, user_id)

        assert exc_info.value.status_code == 500
        assert "Database error: Database error" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_update_todo_success(self, mock_supabase_client, sample_todo_data):
        """测试成功更新todo"""
        todo_id = "todo-123"
        todo_update = TodoUpdate(title="Updated Title", is_completed=True)
        user_id = "test-user-id"

        # 模拟验证todo存在
        mock_existing_response = Mock()
        mock_existing_response.data = [sample_todo_data]

        # 模拟更新响应
        updated_todo = sample_todo_data.copy()
        updated_todo["title"] = "Updated Title"
        updated_todo["is_completed"] = True
        mock_update_response = Mock()
        mock_update_response.data = [updated_todo]

        mock_table = mock_supabase_client.table.return_value
        # 设置不同的返回值给不同的调用
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.update.return_value = mock_table
        mock_table.execute.side_effect = [mock_existing_response, mock_update_response]

        service = TodoService(mock_supabase_client)
        result = await service.update_todo(todo_id, todo_update, user_id)

        # 验证结果
        assert result == updated_todo

        # 验证调用次数
        assert mock_table.execute.call_count == 2
        mock_table.update.assert_called_once_with(
            {"title": "Updated Title", "is_completed": True}
        )

    @pytest.mark.asyncio
    async def test_update_todo_not_found(self, mock_supabase_client):
        """测试更新不存在的todo"""
        todo_id = "nonexistent-id"
        todo_update = TodoUpdate(title="Updated Title")
        user_id = "test-user-id"

        # 模拟todo不存在
        mock_response = Mock()
        mock_response.data = []

        mock_table = mock_supabase_client.table.return_value
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.execute.return_value = mock_response

        service = TodoService(mock_supabase_client)

        with pytest.raises(HTTPException) as exc_info:
            await service.update_todo(todo_id, todo_update, user_id)

        assert exc_info.value.status_code == 404
        assert "Todo not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_update_todo_update_failed(
        self, mock_supabase_client, sample_todo_data
    ):
        """测试更新todo失败"""
        todo_id = "todo-123"
        todo_update = TodoUpdate(title="Updated Title")
        user_id = "test-user-id"

        # 模拟验证todo存在
        mock_existing_response = Mock()
        mock_existing_response.data = [sample_todo_data]

        # 模拟更新失败
        mock_update_response = Mock()
        mock_update_response.data = None

        mock_table = mock_supabase_client.table.return_value
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.update.return_value = mock_table
        mock_table.execute.side_effect = [mock_existing_response, mock_update_response]

        service = TodoService(mock_supabase_client)

        with pytest.raises(HTTPException) as exc_info:
            await service.update_todo(todo_id, todo_update, user_id)

        assert exc_info.value.status_code == 400
        assert "Failed to update todo" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_delete_todo_success(self, mock_supabase_client, sample_todo_data):
        """测试成功删除todo"""
        todo_id = "todo-123"
        user_id = "test-user-id"

        # 模拟验证todo存在
        mock_existing_response = Mock()
        mock_existing_response.data = [sample_todo_data]

        mock_table = mock_supabase_client.table.return_value
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.delete.return_value = mock_table
        mock_table.execute.return_value = mock_existing_response

        service = TodoService(mock_supabase_client)
        result = await service.delete_todo(todo_id, user_id)

        # 验证结果（删除操作返回None）
        assert result is None

        # 验证删除操作被调用
        mock_table.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_todo_not_found(self, mock_supabase_client):
        """测试删除不存在的todo"""
        todo_id = "nonexistent-id"
        user_id = "test-user-id"

        # 模拟todo不存在
        mock_response = Mock()
        mock_response.data = []

        mock_table = mock_supabase_client.table.return_value
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.execute.return_value = mock_response

        service = TodoService(mock_supabase_client)

        with pytest.raises(HTTPException) as exc_info:
            await service.delete_todo(todo_id, user_id)

        assert exc_info.value.status_code == 404
        assert "Todo not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_delete_todo_database_error(
        self, mock_supabase_client, sample_todo_data
    ):
        """测试删除todo时数据库错误"""
        todo_id = "todo-123"
        user_id = "test-user-id"

        # 模拟验证存在，但删除时出错
        mock_table = mock_supabase_client.table.return_value
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.execute.side_effect = Exception("Database error")

        service = TodoService(mock_supabase_client)

        with pytest.raises(HTTPException) as exc_info:
            await service.delete_todo(todo_id, user_id)

        assert exc_info.value.status_code == 500
        assert "Database error: Database error" in exc_info.value.detail
