from unittest.mock import Mock

import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core.security import get_current_user


class TestSecurity:
    """测试安全模块"""

    @pytest.mark.asyncio
    async def test_get_current_user_success(self, mock_supabase_client, mock_user):
        """测试成功获取当前用户"""
        # 准备测试数据
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="valid.jwt.token"
        )

        # 模拟Supabase返回用户
        mock_supabase_client.auth.get_user.return_value = mock_user

        # 调用函数
        result = await get_current_user(credentials, mock_supabase_client)

        # 验证结果
        assert result == mock_user
        mock_supabase_client.auth.get_user.assert_called_once_with("valid.jwt.token")

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token_format(self, mock_supabase_client):
        """测试无效的令牌格式"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="invalid.token"  # 不是3部分的JWT
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, mock_supabase_client)

        assert exc_info.value.status_code == 401
        assert "Invalid token format" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_no_user_returned(self, mock_supabase_client):
        """测试Supabase未返回用户"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="valid.jwt.token"
        )

        # 模拟Supabase返回None
        mock_supabase_client.auth.get_user.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, mock_supabase_client)

        assert exc_info.value.status_code == 401
        assert "Invalid token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_anonymous_user(self, mock_supabase_client):
        """测试匿名用户被拒绝"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="valid.jwt.token"
        )

        # 模拟匿名用户
        mock_user = Mock()
        mock_user.user = Mock()
        mock_user.user.is_anonymous = True
        mock_supabase_client.auth.get_user.return_value = mock_user

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, mock_supabase_client)

        assert exc_info.value.status_code == 403
        assert "Anonymous access denied" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_expired_token(self, mock_supabase_client):
        """测试过期令牌"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="valid.jwt.token"
        )

        # 模拟JWT过期异常
        mock_supabase_client.auth.get_user.side_effect = jwt.ExpiredSignatureError()

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, mock_supabase_client)

        assert exc_info.value.status_code == 401
        assert "Token expired" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_jwt(self, mock_supabase_client):
        """测试无效JWT令牌"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="valid.jwt.token"
        )

        # 模拟JWT无效异常
        mock_supabase_client.auth.get_user.side_effect = jwt.InvalidTokenError()

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, mock_supabase_client)

        assert exc_info.value.status_code == 401
        assert "Invalid token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_general_exception(self, mock_supabase_client):
        """测试一般异常处理"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="valid.jwt.token"
        )

        # 模拟一般异常
        mock_supabase_client.auth.get_user.side_effect = Exception(
            "Database connection error"
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, mock_supabase_client)

        assert exc_info.value.status_code == 500
        assert "Auth error: Database connection error" in exc_info.value.detail
