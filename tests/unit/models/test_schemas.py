from datetime import UTC

import pytest
from pydantic import ValidationError

from app.models.schemas import (
    AvatarUploadResponse,
    HealthResponse,
    MessageResponse,
    PasswordResetRequest,
    PomodoroSessionCreate,
    PomodoroSessionResponse,
    PomodoroSettings,
    ProfileResponse,
    ProfileUpdate,
    TodoCreate,
    TodoResponse,
    TodoUpdate,
    TokenResponse,
    UserLogin,
)


class TestSchemas:
    """测试数据模式"""

    # 用户认证相关模型测试
    def test_user_login_valid(self):
        """测试有效的用户登录数据"""
        data = {"email": "test@example.com", "password": "password123"}
        login = UserLogin(**data)
        assert login.email == "test@example.com"
        assert login.password == "password123"

    def test_user_login_invalid_email(self):
        """测试无效邮箱格式"""
        with pytest.raises(ValidationError):
            UserLogin(email="invalid-email", password="password123")

    def test_password_reset_request(self):
        """测试密码重置请求"""
        # 只有邮箱
        reset1 = PasswordResetRequest(email="test@example.com")
        assert reset1.email == "test@example.com"
        assert reset1.site_url is None

        # 包含site_url
        reset2 = PasswordResetRequest(
            email="test@example.com", site_url="https://custom.com"
        )
        assert reset2.site_url == "https://custom.com"

    def test_token_response(self):
        """测试令牌响应模型"""
        token = TokenResponse(access_token="test-token", token_type="bearer")
        assert token.access_token == "test-token"
        assert token.token_type == "bearer"

    # Todo相关模型测试
    def test_todo_create_valid(self):
        """测试有效的Todo创建数据"""
        todo = TodoCreate(title="Test Todo", description="Test Description")
        assert todo.title == "Test Todo"
        assert todo.description == "Test Description"

        # 只有标题
        todo_minimal = TodoCreate(title="Minimal Todo")
        assert todo_minimal.title == "Minimal Todo"
        assert todo_minimal.description is None

    def test_todo_create_invalid(self):
        """测试无效的Todo创建数据"""
        with pytest.raises(ValidationError):
            TodoCreate()  # 缺少必需的title

    def test_todo_update_partial(self):
        """测试Todo更新的部分字段"""
        # 所有字段都是可选的
        todo_update = TodoUpdate()
        assert todo_update.title is None
        assert todo_update.description is None
        assert todo_update.is_completed is None

        # 只更新部分字段
        todo_update = TodoUpdate(title="Updated Title", is_completed=True)
        assert todo_update.title == "Updated Title"
        assert todo_update.description is None
        assert todo_update.is_completed is True

    def test_todo_response_complete(self):
        """测试完整的Todo响应数据"""
        data = {
            "id": "todo-123",
            "user_id": "user-456",
            "title": "Test Todo",
            "description": "Test Description",
            "is_completed": False,
            "created_at": "2025-08-01T00:00:00Z",
            "updated_at": "2025-08-01T00:00:00Z",
        }
        todo = TodoResponse(**data)
        assert todo.id == "todo-123"
        assert todo.user_id == "user-456"
        assert todo.title == "Test Todo"
        assert todo.is_completed is False

    # 番茄钟相关模型测试
    def test_pomodoro_session_create(self):
        """测试番茄钟会话创建"""
        session = PomodoroSessionCreate(
            title="Study Session", duration=25, completedAt="2025-08-01T00:00:00Z"
        )
        assert session.title == "Study Session"
        assert session.duration == 25
        assert session.completedAt == "2025-08-01T00:00:00Z"

    def test_pomodoro_session_response(self):
        """测试番茄钟会话响应"""
        from datetime import datetime

        now = datetime.now(UTC)

        data = {
            "id": "session-123",
            "user_id": "user-456",
            "task_id": "task-789",
            "duration": 25,
            "completed": True,
            "start_time": now,
            "end_time": now,
            "created_at": now,
            "updated_at": now,
        }
        session = PomodoroSessionResponse(**data)
        assert session.id == "session-123"
        assert session.duration == 25
        assert session.completed

    def test_pomodoro_settings_valid(self):
        """测试有效的番茄钟设置"""
        settings = PomodoroSettings(
            workTime=25, shortBreakTime=5, longBreakTime=15, sessionsUntilLongBreak=4
        )
        assert settings.workTime == 25
        assert settings.shortBreakTime == 5
        assert settings.longBreakTime == 15
        assert settings.sessionsUntilLongBreak == 4

    def test_pomodoro_settings_invalid(self):
        """测试无效的番茄钟设置"""
        with pytest.raises(ValidationError):
            PomodoroSettings()  # 缺少必需字段

    # 个人资料相关模型测试
    def test_profile_response_complete(self):
        """测试完整的个人资料响应"""
        profile = ProfileResponse(
            id="user-123",
            name="Test User",
            school="Test School",
            avatar="https://example.com/avatar.png",
        )
        assert profile.id == "user-123"
        assert profile.name == "Test User"
        assert profile.school == "Test School"
        assert profile.avatar == "https://example.com/avatar.png"

    def test_profile_response_minimal(self):
        """测试最小的个人资料响应"""
        profile = ProfileResponse(id="user-123")
        assert profile.id == "user-123"
        assert profile.name is None
        assert profile.school is None
        assert profile.avatar is None

    def test_profile_update_partial(self):
        """测试个人资料部分更新"""
        # 所有字段都是可选的
        update = ProfileUpdate()
        assert update.name is None
        assert update.school is None
        assert update.avatar is None

        # 部分更新
        update = ProfileUpdate(name="New Name")
        assert update.name == "New Name"
        assert update.school is None

    # 通用响应模型测试
    def test_message_response(self):
        """测试消息响应模型"""
        message = MessageResponse(message="Operation successful")
        assert message.message == "Operation successful"

    def test_health_response(self):
        """测试健康检查响应模型"""
        health = HealthResponse(status="ok", message="API is running", version="1.0.0")
        assert health.status == "ok"
        assert health.message == "API is running"
        assert health.version == "1.0.0"

    def test_avatar_upload_response(self):
        """测试头像上传响应模型"""
        response = AvatarUploadResponse(url="https://example.com/avatar.png")
        assert response.url == "https://example.com/avatar.png"
