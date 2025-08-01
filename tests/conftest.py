from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from supabase import Client

from app.main import app
from app.models.database import reset_supabase_client, set_supabase_client


@pytest.fixture
def mock_supabase_client():
    """创建Mock的Supabase客户端"""
    mock_client = Mock(spec=Client)

    # Mock auth methods
    mock_client.auth = Mock()
    mock_client.auth.sign_in_with_password = Mock()
    mock_client.auth.get_user = Mock()
    mock_client.auth.reset_password_for_email = Mock()

    # Mock table methods
    mock_table = Mock()
    mock_table.select = Mock(return_value=mock_table)
    mock_table.insert = Mock(return_value=mock_table)
    mock_table.update = Mock(return_value=mock_table)
    mock_table.delete = Mock(return_value=mock_table)
    mock_table.eq = Mock(return_value=mock_table)
    mock_table.order = Mock(return_value=mock_table)
    mock_table.limit = Mock(return_value=mock_table)
    mock_table.single = Mock(return_value=mock_table)
    mock_table.execute = Mock()

    mock_client.table = Mock(return_value=mock_table)

    # Mock storage methods
    mock_storage = Mock()
    mock_storage.upload = Mock()
    mock_storage.get_public_url = Mock()
    mock_client.storage = Mock()
    mock_client.storage.from_ = Mock(return_value=mock_storage)

    return mock_client


@pytest.fixture
def client_with_mock_supabase(mock_supabase_client):
    """创建使用Mock Supabase的测试客户端"""
    # 设置Mock客户端
    set_supabase_client(mock_supabase_client)

    # 创建测试客户端
    client = TestClient(app)

    yield client, mock_supabase_client

    # 清理
    reset_supabase_client()


@pytest.fixture
def mock_user():
    """创建Mock用户对象"""
    mock_user = Mock()
    mock_user.user = Mock()
    mock_user.user.id = "test-user-id"
    mock_user.user.email = "test@example.com"
    mock_user.user.is_anonymous = False
    return mock_user


@pytest.fixture
def mock_auth_session():
    """创建Mock认证会话"""
    mock_session = Mock()
    mock_session.access_token = "test-access-token"
    mock_session.refresh_token = "test-refresh-token"
    return mock_session


@pytest.fixture
def sample_todo_data():
    """示例Todo数据"""
    return {
        "id": "todo-1",
        "user_id": "test-user-id",
        "title": "Test Todo",
        "description": "Test Description",
        "is_completed": False,
        "created_at": "2025-08-01T00:00:00Z",
        "updated_at": "2025-08-01T00:00:00Z",
    }


@pytest.fixture
def sample_pomodoro_data():
    """示例番茄钟数据"""
    return {
        "id": "pomodoro-1",
        "user_id": "test-user-id",
        "title": "Test Session",
        "duration": 25,
        "completedAt": "2025-08-01T00:00:00Z",
        "created_at": "2025-08-01T00:00:00Z",
    }


@pytest.fixture
def sample_profile_data():
    """示例个人资料数据"""
    return {
        "id": "test-user-id",
        "name": "Test User",
        "school": "Test School",
        "avatar": "https://example.com/avatar.png",
    }
