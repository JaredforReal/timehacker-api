from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def client(client_with_mock_supabase):
    """创建测试客户端，直接使用已验证的mock客户端"""
    client, mock_supabase = client_with_mock_supabase

    # 为API测试设置特定的auth mock响应
    mock_session = Mock()
    mock_session.access_token = "test-access-token"

    mock_response = Mock()
    mock_response.session = mock_session

    mock_supabase.auth.sign_in_with_password.return_value = mock_response

    # 设置密码重置mock - 需要模拟Supabase响应结构
    mock_reset_response = Mock()
    mock_reset_response.error = None  # 成功情况下error为None
    mock_supabase.auth.reset_password_for_email.return_value = mock_reset_response

    return client


@pytest.fixture
def mock_auth_user():
    """模拟认证用户数据"""
    return {
        "user": {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "test@example.com",
        }
    }


@pytest.fixture
def auth_headers(mock_auth_user):
    """模拟认证头部"""
    with patch("app.core.security.get_current_user") as mock_get_current_user:
        mock_get_current_user.return_value = mock_auth_user
        yield {"Authorization": "Bearer test-token"}


@pytest.fixture
def mock_auth_service():
    """模拟认证服务"""

    mock_service = Mock()
    # 直接设置成功的返回值，而不是AsyncMock
    mock_service.login.return_value = {
        "access_token": "fake-token",
        "token_type": "bearer",
    }
    mock_service.request_password_reset.return_value = {
        "message": "Password reset email sent"
    }
    return mock_service


@pytest.fixture
def mock_todo_service():
    """模拟Todo服务"""
    from unittest.mock import AsyncMock

    mock_service = Mock()
    mock_service.get_todos = AsyncMock(
        return_value=[
            {
                "id": "1",
                "title": "Test Todo",
                "description": "Test Description",
                "completed": False,
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00",
            }
        ]
    )
    mock_service.create_todo = AsyncMock(
        return_value={
            "id": "1",
            "title": "New Todo",
            "description": "New Description",
            "completed": False,
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00",
        }
    )
    mock_service.update_todo = AsyncMock(
        return_value={
            "id": "1",
            "title": "Updated Todo",
            "description": "Updated Description",
            "completed": True,
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00",
        }
    )
    mock_service.delete_todo = AsyncMock(return_value=None)
    return mock_service


@pytest.fixture
def mock_pomodoro_service():
    """模拟Pomodoro服务"""
    from unittest.mock import AsyncMock

    mock_service = Mock()
    mock_service.get_sessions = AsyncMock(
        return_value=[
            {
                "id": "1",
                "title": "Work Session",
                "duration": 25,
                "completed": "2025-01-01T00:00:00",
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00",
            }
        ]
    )
    mock_service.create_session = AsyncMock(
        return_value={
            "id": "1",
            "title": "Work Session",
            "duration": 25,
            "completed": "2025-01-01T00:00:00",
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00",
        }
    )
    mock_service.get_settings = AsyncMock(
        return_value={
            "workTime": 25,
            "shortBreakTime": 5,
            "longBreakTime": 15,
            "intervalCount": 4,
        }
    )
    mock_service.update_settings = AsyncMock(
        return_value={
            "workTime": 30,
            "shortBreakTime": 10,
            "longBreakTime": 20,
            "intervalCount": 4,
        }
    )
    return mock_service


@pytest.fixture
def mock_profile_service():
    """模拟Profile服务"""
    from unittest.mock import AsyncMock

    mock_service = Mock()
    mock_service.get_profile = AsyncMock(
        return_value={
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "Test User",
            "school": "Test University",
            "avatar_url": None,
        }
    )
    mock_service.update_profile = AsyncMock(
        return_value={
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "Updated User",
            "school": "Updated University",
            "avatar_url": None,
        }
    )
    mock_service.upload_avatar = AsyncMock(
        return_value={"avatar_url": "https://example.com/avatar.png"}
    )
    return mock_service
