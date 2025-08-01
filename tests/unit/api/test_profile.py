from io import BytesIO
from unittest.mock import AsyncMock, Mock

from fastapi import status


class TestProfileAPI:
    """个人资料 API测试"""

    def test_get_profile_success(self, client):
        """测试获取个人资料成功"""
        from app.core.security import get_current_user
        from app.dependencies import get_profile_service
        from app.main import app

        # Mock认证用户
        mock_user = Mock()
        mock_user.user.id = "test-user-id"

        # Mock profile service
        mock_service = AsyncMock()
        mock_profile = {
            "id": "test-user-id",
            "name": "Test User",
            "school": "Test University",
            "avatar": "https://example.com/avatar.png",
        }
        mock_service.get_profile.return_value = mock_profile

        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_profile_service] = lambda: mock_service

        try:
            response = client.get("/profile")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == "test-user-id"
            assert data["name"] == "Test User"
            assert data["school"] == "Test University"
            assert data["avatar"] == "https://example.com/avatar.png"
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()

    def test_update_profile_success(self, client):
        """测试更新个人资料成功"""
        from app.core.security import get_current_user
        from app.dependencies import get_profile_service
        from app.main import app

        # Mock认证用户
        mock_user = Mock()
        mock_user.user.id = "test-user-id"

        # Mock profile service
        mock_service = AsyncMock()
        mock_updated_profile = {
            "id": "test-user-id",
            "name": "Updated User",
            "school": "Updated University",
            "avatar": "https://example.com/avatar.png",
        }
        mock_service.update_profile.return_value = mock_updated_profile

        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_profile_service] = lambda: mock_service

        profile_data = {"name": "Updated User", "school": "Updated University"}

        try:
            response = client.put("/profile", json=profile_data)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["name"] == "Updated User"
            assert data["school"] == "Updated University"
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()

    def test_upload_avatar_success(self, client):
        """测试上传头像成功"""
        from app.core.security import get_current_user
        from app.dependencies import get_profile_service
        from app.main import app

        # Mock认证用户
        mock_user = Mock()
        mock_user.user.id = "test-user-id"

        # Mock profile service
        mock_service = AsyncMock()
        mock_upload_response = {"url": "https://example.com/new-avatar.png"}
        mock_service.upload_avatar.return_value = mock_upload_response

        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_profile_service] = lambda: mock_service

        # 创建模拟文件
        file_content = b"fake image content"
        files = {"avatar": ("test_avatar.png", BytesIO(file_content), "image/png")}

        try:
            response = client.post("/profile/avatar", files=files)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["url"] == "https://example.com/new-avatar.png"
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()

    def test_update_profile_partial_success(self, client):
        """测试部分更新个人资料成功"""
        from app.core.security import get_current_user
        from app.dependencies import get_profile_service
        from app.main import app

        # Mock认证用户
        mock_user = Mock()
        mock_user.user.id = "test-user-id"

        # Mock profile service
        mock_service = AsyncMock()
        mock_updated_profile = {
            "id": "test-user-id",
            "name": "Only Name Updated",
            "school": "Original School",
            "avatar": None,
        }
        mock_service.update_profile.return_value = mock_updated_profile

        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_profile_service] = lambda: mock_service

        # 只更新name字段
        profile_data = {"name": "Only Name Updated"}

        try:
            response = client.put("/profile", json=profile_data)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["name"] == "Only Name Updated"
            assert data["school"] == "Original School"
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()

    def test_upload_avatar_missing_file(self, client):
        """测试上传头像缺少文件"""
        from app.core.security import get_current_user
        from app.dependencies import get_profile_service
        from app.main import app

        # Mock认证用户
        mock_user = Mock()
        mock_user.user.id = "test-user-id"

        # Mock profile service
        mock_service = AsyncMock()

        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_profile_service] = lambda: mock_service

        try:
            # 没有提供文件
            response = client.post("/profile/avatar")

            # 应该返回422（缺少必需的文件参数）
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()

    def test_profile_unauthorized(self, client):
        """测试未认证访问个人资料API"""
        # 不设置认证mock，应该返回401或403
        response = client.get("/profile")

        # 应该是认证错误
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]

    def test_update_profile_empty_data(self, client):
        """测试更新个人资料空数据"""
        from app.core.security import get_current_user
        from app.dependencies import get_profile_service
        from app.main import app

        # Mock认证用户
        mock_user = Mock()
        mock_user.user.id = "test-user-id"

        # Mock profile service
        mock_service = AsyncMock()
        mock_profile = {
            "id": "test-user-id",
            "name": None,
            "school": None,
            "avatar": None,
        }
        mock_service.update_profile.return_value = mock_profile

        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_profile_service] = lambda: mock_service

        # 空的更新数据（应该是有效的，因为所有字段都是可选的）
        profile_data = {}

        try:
            response = client.put("/profile", json=profile_data)

            assert response.status_code == status.HTTP_200_OK
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()
