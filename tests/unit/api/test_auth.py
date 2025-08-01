from unittest.mock import patch

from fastapi import status


class TestAuthAPI:
    """认证API测试"""

    @patch("app.dependencies.get_auth_service")
    def test_login_success(self, mock_get_auth_service, client, mock_auth_service):
        """测试成功登录"""
        # 设置auth_service的login方法直接返回成功响应
        mock_auth_service.login.return_value = {
            "access_token": "fake-token",
            "token_type": "bearer",
        }
        mock_get_auth_service.return_value = mock_auth_service

        login_data = {"email": "test@example.com", "password": "testpassword"}

        response = client.post("/token", json=login_data)

        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"

    @patch("app.dependencies.get_auth_service")
    def test_login_invalid_email(self, mock_get_auth_service, client):
        """测试无效邮箱格式"""
        mock_get_auth_service.return_value = None

        login_data = {"email": "invalid-email", "password": "testpassword"}

        response = client.post("/token", json=login_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @patch("app.dependencies.get_auth_service")
    def test_login_missing_fields(self, mock_get_auth_service, client):
        """测试缺失字段"""
        mock_get_auth_service.return_value = None

        login_data = {
            "email": "test@example.com"
            # 缺少password字段
        }

        response = client.post("/token", json=login_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @patch("app.dependencies.get_auth_service")
    def test_password_reset_success(
        self, mock_get_auth_service, client, mock_auth_service
    ):
        """测试成功请求密码重置"""
        mock_get_auth_service.return_value = mock_auth_service

        reset_data = {"email": "test@example.com", "site_url": "https://example.com"}

        response = client.post("/auth/reset-password", json=reset_data)

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()

    @patch("app.dependencies.get_auth_service")
    def test_password_reset_invalid_email(self, mock_get_auth_service, client):
        """测试无效邮箱格式的密码重置"""
        mock_get_auth_service.return_value = None

        reset_data = {"email": "invalid-email", "site_url": "https://example.com"}

        response = client.post("/auth/reset-password", json=reset_data)

        # Pydantic验证应该返回422
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @patch("app.dependencies.get_auth_service")
    def test_password_reset_missing_email(self, mock_get_auth_service, client):
        """测试缺少邮箱的密码重置"""
        mock_get_auth_service.return_value = None

        reset_data = {
            "site_url": "https://example.com"
            # 缺少email字段
        }

        response = client.post("/auth/reset-password", json=reset_data)

        # Pydantic验证应该返回422
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
