from unittest.mock import AsyncMock, Mock

from fastapi import status


class TestPomodoroAPI:
    """番茄钟 API测试"""

    def test_create_pomodoro_session_success(self, client):
        """测试创建番茄钟会话成功"""
        from app.core.security import get_current_user
        from app.dependencies import get_pomodoro_service
        from app.main import app

        # Mock认证用户
        mock_user = Mock()
        mock_user.user.id = "test-user-id"

        # Mock pomodoro service
        mock_service = AsyncMock()
        mock_session = {
            "id": "session-1",
            "user_id": "test-user-id",
            "task_id": None,
            "duration": 25,
            "completed": False,
            "start_time": None,
            "end_time": None,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        mock_service.create_session.return_value = mock_session

        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_pomodoro_service] = lambda: mock_service

        session_data = {
            "title": "Work Session",
            "duration": 25,
            "completedAt": "2024-01-01T00:25:00Z",
        }

        try:
            response = client.post("/pomodoro/sessions", json=session_data)

            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["duration"] == 25
            assert data["user_id"] == "test-user-id"
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()

    def test_get_pomodoro_sessions_success(self, client):
        """测试获取番茄钟会话列表成功"""
        from app.core.security import get_current_user
        from app.dependencies import get_pomodoro_service
        from app.main import app

        # Mock认证用户
        mock_user = Mock()
        mock_user.user.id = "test-user-id"

        # Mock pomodoro service
        mock_service = AsyncMock()
        mock_sessions = [
            {
                "id": "session-1",
                "user_id": "test-user-id",
                "task_id": None,
                "duration": 25,
                "completed": True,
                "start_time": "2024-01-01T00:00:00Z",
                "end_time": "2024-01-01T00:25:00Z",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:25:00Z",
            },
            {
                "id": "session-2",
                "user_id": "test-user-id",
                "task_id": None,
                "duration": 25,
                "completed": False,
                "start_time": "2024-01-01T01:00:00Z",
                "end_time": None,
                "created_at": "2024-01-01T01:00:00Z",
                "updated_at": "2024-01-01T01:00:00Z",
            },
        ]
        mock_service.get_sessions.return_value = mock_sessions

        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_pomodoro_service] = lambda: mock_service

        try:
            response = client.get("/pomodoro/sessions")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 2
            assert data[0]["completed"] is True
            assert data[1]["completed"] is False
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()

    def test_get_pomodoro_settings_success(self, client):
        """测试获取番茄钟设置成功"""
        from app.core.security import get_current_user
        from app.dependencies import get_pomodoro_service
        from app.main import app

        # Mock认证用户
        mock_user = Mock()
        mock_user.user.id = "test-user-id"

        # Mock pomodoro service
        mock_service = AsyncMock()
        mock_settings = {
            "workTime": 25,
            "shortBreakTime": 5,
            "longBreakTime": 15,
            "sessionsUntilLongBreak": 4,
        }
        mock_service.get_settings.return_value = mock_settings

        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_pomodoro_service] = lambda: mock_service

        try:
            response = client.get("/pomodoro/settings")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["workTime"] == 25
            assert data["shortBreakTime"] == 5
            assert data["longBreakTime"] == 15
            assert data["sessionsUntilLongBreak"] == 4
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()

    def test_update_pomodoro_settings_success(self, client):
        """测试更新番茄钟设置成功"""
        from app.core.security import get_current_user
        from app.dependencies import get_pomodoro_service
        from app.main import app

        # Mock认证用户
        mock_user = Mock()
        mock_user.user.id = "test-user-id"

        # Mock pomodoro service
        mock_service = AsyncMock()
        mock_updated_settings = {
            "workTime": 30,
            "shortBreakTime": 10,
            "longBreakTime": 20,
            "sessionsUntilLongBreak": 3,
        }
        mock_service.update_settings.return_value = mock_updated_settings

        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_pomodoro_service] = lambda: mock_service

        settings_data = {
            "workTime": 30,
            "shortBreakTime": 10,
            "longBreakTime": 20,
            "sessionsUntilLongBreak": 3,
        }

        try:
            response = client.put("/pomodoro/settings", json=settings_data)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["workTime"] == 30
            assert data["shortBreakTime"] == 10
            assert data["longBreakTime"] == 20
            assert data["sessionsUntilLongBreak"] == 3
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()

    def test_create_session_validation_error(self, client):
        """测试创建会话验证错误"""
        from app.core.security import get_current_user
        from app.dependencies import get_pomodoro_service
        from app.main import app

        # Mock认证用户
        mock_user = Mock()
        mock_user.user.id = "test-user-id"

        # Mock pomodoro service
        mock_service = AsyncMock()

        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_pomodoro_service] = lambda: mock_service

        # 缺少必需的字段
        session_data = {
            "duration": 25
            # 缺少title和completedAt
        }

        try:
            response = client.post("/pomodoro/sessions", json=session_data)

            # Pydantic验证应该返回422
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()

    def test_pomodoro_unauthorized(self, client):
        """测试未认证访问番茄钟API"""
        # 不设置认证mock，应该返回401或403
        response = client.get("/pomodoro/sessions")

        # 应该是认证错误
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]
