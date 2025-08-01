from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from app.models.schemas import PasswordResetRequest, TokenResponse, UserLogin
from app.services.auth_service import AuthService


class TestAuthService:
    """测试认证服务"""

    def test_init(self, mock_supabase_client):
        """测试服务初始化"""
        service = AuthService(mock_supabase_client)
        assert service.supabase == mock_supabase_client

    @pytest.mark.asyncio
    async def test_login_success(self, mock_supabase_client, mock_auth_session):
        """测试成功登录"""
        # 准备测试数据
        user_login = UserLogin(email="test@example.com", password="password123")

        # 模拟Supabase响应
        mock_response = Mock()
        mock_response.session = mock_auth_session
        mock_supabase_client.auth.sign_in_with_password.return_value = mock_response

        # 调用服务
        service = AuthService(mock_supabase_client)
        result = await service.login(user_login)

        # 验证结果
        assert isinstance(result, TokenResponse)
        assert result.access_token == "test-access-token"
        assert result.token_type == "bearer"

        # 验证调用参数
        mock_supabase_client.auth.sign_in_with_password.assert_called_once_with(
            {"email": "test@example.com", "password": "password123"}
        )

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, mock_supabase_client):
        """测试无效凭证登录"""
        user_login = UserLogin(email="test@example.com", password="wrongpassword")

        # 模拟Supabase抛出异常
        mock_supabase_client.auth.sign_in_with_password.side_effect = Exception(
            "Invalid credentials"
        )

        service = AuthService(mock_supabase_client)

        with pytest.raises(HTTPException) as exc_info:
            await service.login(user_login)

        assert exc_info.value.status_code == 401
        assert "Invalid credentials" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_request_password_reset_success(self, mock_supabase_client):
        """测试成功的密码重置请求"""
        reset_request = PasswordResetRequest(
            email="test@example.com", site_url="https://custom.com"
        )

        # 模拟Supabase成功响应
        mock_response = Mock()
        mock_response.error = None
        mock_supabase_client.auth.reset_password_for_email.return_value = mock_response

        service = AuthService(mock_supabase_client)
        result = await service.request_password_reset(reset_request)

        assert result == {"message": "Password reset email sent"}

        # 验证调用参数
        mock_supabase_client.auth.reset_password_for_email.assert_called_once_with(
            "test@example.com", {"redirectTo": "https://custom.com/reset-password"}
        )

    @pytest.mark.asyncio
    async def test_request_password_reset_default_site_url(self, mock_supabase_client):
        """测试使用默认site_url的密码重置"""
        reset_request = PasswordResetRequest(email="test@example.com")

        mock_response = Mock()
        mock_response.error = None
        mock_supabase_client.auth.reset_password_for_email.return_value = mock_response

        service = AuthService(mock_supabase_client)

        with patch("app.services.auth_service.settings") as mock_settings:
            mock_settings.site_url = "https://default.com"
            await service.request_password_reset(reset_request)

        # 应该使用默认URL
        mock_supabase_client.auth.reset_password_for_email.assert_called_once_with(
            "test@example.com", {"redirectTo": "https://default.com/reset-password"}
        )

    @pytest.mark.asyncio
    async def test_request_password_reset_no_email(self, mock_supabase_client):
        """测试缺少邮箱的密码重置请求"""
        # 这种情况在Pydantic验证时就会失败，但我们测试服务层的处理
        service = AuthService(mock_supabase_client)

        # 创建一个模拟的请求对象，绕过Pydantic验证
        reset_request = Mock()
        reset_request.email = ""
        reset_request.site_url = None

        with pytest.raises(HTTPException) as exc_info:
            await service.request_password_reset(reset_request)

        assert exc_info.value.status_code == 400
        assert "Email is required" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_request_password_reset_supabase_error(self, mock_supabase_client):
        """测试Supabase返回错误"""
        reset_request = PasswordResetRequest(email="test@example.com")

        # 模拟Supabase错误响应
        mock_response = Mock()
        mock_response.error = Mock()
        mock_response.error.message = "Email not found"
        mock_supabase_client.auth.reset_password_for_email.return_value = mock_response

        service = AuthService(mock_supabase_client)

        with pytest.raises(HTTPException) as exc_info:
            await service.request_password_reset(reset_request)

        assert exc_info.value.status_code == 400
        assert "Failed to send reset email: Email not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_request_password_reset_general_exception(self, mock_supabase_client):
        """测试一般异常处理"""
        reset_request = PasswordResetRequest(email="test@example.com")

        # 模拟一般异常
        mock_supabase_client.auth.reset_password_for_email.side_effect = Exception(
            "Network error"
        )

        service = AuthService(mock_supabase_client)

        with pytest.raises(HTTPException) as exc_info:
            await service.request_password_reset(reset_request)

        assert exc_info.value.status_code == 500
        assert "Error requesting password reset: Network error" in exc_info.value.detail
