from unittest.mock import AsyncMock, Mock

from fastapi import status


class TestTodosAPI:
    """Todo API测试"""

    def test_get_todos_success(self, client):
        """测试获取todos成功"""
        from app.core.security import get_current_user
        from app.dependencies import get_todo_service
        from app.main import app

        # Mock认证用户
        mock_user = Mock()
        mock_user.user.id = "test-user-id"

        # Mock todo service
        mock_service = AsyncMock()
        mock_todos = [
            {
                "id": "todo-1",
                "user_id": "test-user-id",
                "title": "Test Todo 1",
                "description": "Test Description 1",
                "is_completed": False,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
            {
                "id": "todo-2",
                "user_id": "test-user-id",
                "title": "Test Todo 2",
                "description": None,
                "is_completed": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
        ]
        mock_service.get_todos.return_value = mock_todos

        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_todo_service] = lambda: mock_service

        try:
            response = client.get("/todos")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 2
            assert data[0]["title"] == "Test Todo 1"
            assert data[1]["is_completed"] is True
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()

    def test_create_todo_success(self, client):
        """测试创建todo成功"""
        from app.core.security import get_current_user
        from app.dependencies import get_todo_service
        from app.main import app

        # Mock认证用户
        mock_user = Mock()
        mock_user.user.id = "test-user-id"

        # Mock todo service
        mock_service = AsyncMock()
        mock_created_todo = {
            "id": "new-todo-id",
            "user_id": "test-user-id",
            "title": "New Todo",
            "description": "New Description",
            "is_completed": False,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        mock_service.create_todo.return_value = mock_created_todo

        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_todo_service] = lambda: mock_service

        todo_data = {"title": "New Todo", "description": "New Description"}

        try:
            response = client.post("/todos", json=todo_data)

            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["title"] == "New Todo"
            assert data["description"] == "New Description"
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()

    def test_update_todo_success(self, client):
        """测试更新todo成功"""
        from app.core.security import get_current_user
        from app.dependencies import get_todo_service
        from app.main import app

        # Mock认证用户
        mock_user = Mock()
        mock_user.user.id = "test-user-id"

        # Mock todo service
        mock_service = AsyncMock()
        mock_updated_todo = {
            "id": "todo-1",
            "user_id": "test-user-id",
            "title": "Updated Todo",
            "description": "Updated Description",
            "is_completed": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
        }
        mock_service.update_todo.return_value = mock_updated_todo

        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_todo_service] = lambda: mock_service

        update_data = {"title": "Updated Todo", "description": "Updated Description"}

        try:
            response = client.put("/todos/todo-1", json=update_data)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["title"] == "Updated Todo"
            assert data["description"] == "Updated Description"
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()

    def test_delete_todo_success(self, client):
        """测试删除todo成功"""
        from app.core.security import get_current_user
        from app.dependencies import get_todo_service
        from app.main import app

        # Mock认证用户
        mock_user = Mock()
        mock_user.user.id = "test-user-id"

        # Mock todo service
        mock_service = AsyncMock()
        mock_service.delete_todo.return_value = None

        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_todo_service] = lambda: mock_service

        try:
            response = client.delete("/todos/todo-1")

            assert response.status_code == status.HTTP_204_NO_CONTENT
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()

    def test_create_todo_validation_error(self, client):
        """测试创建todo验证错误"""
        from app.core.security import get_current_user
        from app.dependencies import get_todo_service
        from app.main import app

        # Mock认证用户
        mock_user = Mock()
        mock_user.user.id = "test-user-id"

        # Mock todo service
        mock_service = AsyncMock()

        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_todo_service] = lambda: mock_service

        # 缺少必需的title字段
        todo_data = {"description": "Missing title"}

        try:
            response = client.post("/todos", json=todo_data)

            # Pydantic验证应该返回422
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()

    def test_todos_unauthorized(self, client):
        """测试未认证访问todos"""
        # 不设置认证mock，应该返回401或403
        response = client.get("/todos")

        # 应该是认证错误
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]
