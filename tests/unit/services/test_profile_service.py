from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException, UploadFile

from app.models.schemas import ProfileUpdate
from app.services.profile_service import ProfileService


class TestProfileService:
    @pytest.fixture
    def sample_profile_data(self):
        return {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "张三",
            "school": "北京大学",
            "avatar": "https://example.com/avatar.png",
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }

    @pytest.fixture
    def sample_avatar_file(self):
        """创建一个模拟的头像文件"""
        file_content = b"fake image content"
        file = Mock(spec=UploadFile)
        file.read = AsyncMock(return_value=file_content)
        file.filename = "avatar.png"
        file.content_type = "image/png"
        return file

    @pytest.mark.asyncio
    async def test_get_profile_success(self, mock_supabase_client, sample_profile_data):
        """测试成功获取用户个人资料"""
        # 准备模拟数据
        mock_response = Mock()
        mock_response.data = sample_profile_data
        mock_response.error = None

        mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = (
            mock_response
        )

        # 创建服务实例
        service = ProfileService(mock_supabase_client)
        user_id = "123e4567-e89b-12d3-a456-426614174000"

        # 执行测试
        result = await service.get_profile(user_id)

        # 验证结果
        assert result["id"] == user_id
        assert result["name"] == "张三"
        assert result["school"] == "北京大学"

        # 验证数据库调用
        mock_supabase_client.table.assert_called_with("profiles")
        mock_supabase_client.table.return_value.select.assert_called_with("*")
        mock_supabase_client.table.return_value.select.return_value.eq.assert_called_with(
            "id", user_id
        )

    @pytest.mark.asyncio
    async def test_get_profile_create_default(self, mock_supabase_client):
        """测试获取个人资料时创建默认资料"""
        user_id = "123e4567-e89b-12d3-a456-426614174000"

        # 第一次查询返回空（没有个人资料）
        mock_response_empty = Mock()
        mock_response_empty.data = None
        mock_response_empty.error = None

        # 创建默认个人资料的响应
        default_profile = {"id": user_id, "name": "", "school": "", "avatar": None}
        mock_response_created = Mock()
        mock_response_created.data = [default_profile]
        mock_response_created.error = None

        # 设置两个不同的table()调用
        mock_table_select = Mock()
        mock_table_insert = Mock()

        # 第一次调用table()用于select，第二次用于insert
        mock_supabase_client.table.side_effect = [mock_table_select, mock_table_insert]

        # 设置select调用链
        mock_table_select.select.return_value.eq.return_value.single.return_value.execute.return_value = (
            mock_response_empty
        )

        # 设置insert调用链
        mock_table_insert.insert.return_value.execute.return_value = (
            mock_response_created
        )

        service = ProfileService(mock_supabase_client)

        # 执行测试
        result = await service.get_profile(user_id)

        # 验证结果
        assert result["id"] == user_id
        assert result["name"] == ""
        assert result["school"] == ""
        assert result["avatar"] is None

        # 验证调用了插入操作
        mock_table_insert.insert.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_profile_create_default_failed(self, mock_supabase_client):
        """测试创建默认个人资料失败"""
        user_id = "123e4567-e89b-12d3-a456-426614174000"

        # 查询返回空
        mock_response_empty = Mock()
        mock_response_empty.data = None
        mock_response_empty.error = None

        # 创建失败
        mock_response_failed = Mock()
        mock_response_failed.data = None
        mock_response_failed.error = None

        mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = (
            mock_response_empty
        )
        mock_supabase_client.table.return_value.insert.return_value.execute.return_value = (
            mock_response_failed
        )

        service = ProfileService(mock_supabase_client)

        # 验证抛出异常
        with pytest.raises(HTTPException) as exc_info:
            await service.get_profile(user_id)

        assert exc_info.value.status_code == 400
        assert "Failed to create profile" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_profile_database_error(self, mock_supabase_client):
        """测试获取个人资料时数据库错误"""
        # 模拟数据库错误
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.side_effect = Exception(
            "Database connection error"
        )

        service = ProfileService(mock_supabase_client)
        user_id = "123e4567-e89b-12d3-a456-426614174000"

        # 验证抛出异常
        with pytest.raises(HTTPException) as exc_info:
            await service.get_profile(user_id)

        assert exc_info.value.status_code == 500
        assert "Database error" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_update_profile_success(
        self, mock_supabase_client, sample_profile_data
    ):
        """测试成功更新用户个人资料"""
        user_id = "123e4567-e89b-12d3-a456-426614174000"

        # 模拟已存在的个人资料
        mock_existing_response = Mock()
        mock_existing_response.data = [sample_profile_data]
        mock_existing_response.error = None

        # 模拟更新成功
        updated_profile = sample_profile_data.copy()
        updated_profile["name"] = "李四"
        updated_profile["school"] = "清华大学"

        mock_update_response = Mock()
        mock_update_response.data = [updated_profile]
        mock_update_response.error = None

        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value = (
            mock_existing_response
        )
        mock_supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value = (
            mock_update_response
        )

        # 创建服务实例
        service = ProfileService(mock_supabase_client)

        # 创建更新数据
        profile_update = ProfileUpdate(name="李四", school="清华大学")

        # 执行测试
        result = await service.update_profile(profile_update, user_id)

        # 验证结果
        assert result["name"] == "李四"
        assert result["school"] == "清华大学"

        # 验证数据库调用
        mock_supabase_client.table.return_value.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_profile_create_new(self, mock_supabase_client):
        """测试更新个人资料时创建新资料"""
        user_id = "123e4567-e89b-12d3-a456-426614174000"

        # 模拟不存在的个人资料
        mock_existing_response = Mock()
        mock_existing_response.data = []
        mock_existing_response.error = None

        # 模拟创建成功
        new_profile = {"id": user_id, "name": "新用户", "school": "新学校", "avatar": None}
        mock_create_response = Mock()
        mock_create_response.data = [new_profile]
        mock_create_response.error = None

        # 设置两个不同的table()调用
        mock_table_select = Mock()
        mock_table_insert = Mock()

        # 第一次调用table()用于select，第二次用于insert
        mock_supabase_client.table.side_effect = [mock_table_select, mock_table_insert]

        # 设置select调用链
        mock_table_select.select.return_value.eq.return_value.execute.return_value = (
            mock_existing_response
        )

        # 设置insert调用链
        mock_table_insert.insert.return_value.execute.return_value = (
            mock_create_response
        )

        service = ProfileService(mock_supabase_client)

        profile_update = ProfileUpdate(name="新用户", school="新学校")

        # 执行测试
        result = await service.update_profile(profile_update, user_id)

        # 验证结果
        assert result["name"] == "新用户"
        assert result["school"] == "新学校"

        # 验证调用了插入操作
        mock_table_insert.insert.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_profile_failed(
        self, mock_supabase_client, sample_profile_data
    ):
        """测试更新个人资料失败"""
        user_id = "123e4567-e89b-12d3-a456-426614174000"

        # 模拟已存在的个人资料
        mock_existing_response = Mock()
        mock_existing_response.data = [sample_profile_data]
        mock_existing_response.error = None

        # 模拟更新失败
        mock_update_response = Mock()
        mock_update_response.data = None
        mock_update_response.error = None

        # 设置两个不同的table()调用
        mock_table_select = Mock()
        mock_table_update = Mock()

        # 第一次调用table()用于select，第二次用于update
        mock_supabase_client.table.side_effect = [mock_table_select, mock_table_update]

        # 设置select调用链
        mock_table_select.select.return_value.eq.return_value.execute.return_value = (
            mock_existing_response
        )

        # 设置update调用链
        mock_table_update.update.return_value.eq.return_value.execute.return_value = (
            mock_update_response
        )

        service = ProfileService(mock_supabase_client)

        profile_update = ProfileUpdate(name="测试")

        # 验证抛出异常
        with pytest.raises(HTTPException) as exc_info:
            await service.update_profile(profile_update, user_id)

        assert exc_info.value.status_code == 400
        assert "Failed to update profile" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_upload_avatar_success(
        self, mock_supabase_client, sample_avatar_file
    ):
        """测试成功上传头像"""
        user_id = "123e4567-e89b-12d3-a456-426614174000"

        # 模拟存储上传成功
        mock_upload_response = Mock()
        mock_upload_response.error = None
        mock_upload_response.data = {"path": f"public/{user_id}.png"}

        # 模拟获取公共URL成功
        avatar_url = (
            f"https://example.com/storage/v1/object/public/avatars/public/{user_id}.png"
        )
        mock_url_response = Mock()
        mock_url_response.data = {"publicUrl": avatar_url}

        # 模拟更新个人资料成功
        mock_profile_update_response = Mock()
        mock_profile_update_response.data = [{"avatar": avatar_url}]
        mock_profile_update_response.error = None

        # 设置存储相关的模拟
        mock_storage = Mock()
        mock_storage.upload.return_value = mock_upload_response
        mock_storage.get_public_url.return_value = mock_url_response

        mock_supabase_client.storage.from_.return_value = mock_storage
        mock_supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value = (
            mock_profile_update_response
        )

        # 创建服务实例
        service = ProfileService(mock_supabase_client)

        # 执行测试
        result = await service.upload_avatar(sample_avatar_file, user_id)

        # 验证结果
        assert result.url == avatar_url

        # 验证存储调用
        mock_supabase_client.storage.from_.assert_called_with("avatars")
        mock_storage.upload.assert_called_once()
        mock_storage.get_public_url.assert_called_with(f"public/{user_id}.png")

        # 验证数据库更新调用
        mock_supabase_client.table.return_value.update.assert_called_with(
            {"avatar": avatar_url}
        )

    @pytest.mark.asyncio
    async def test_upload_avatar_storage_error(
        self, mock_supabase_client, sample_avatar_file
    ):
        """测试上传头像存储错误"""
        user_id = "123e4567-e89b-12d3-a456-426614174000"

        # 模拟存储上传失败
        mock_upload_response = Mock()
        mock_upload_response.error = Mock()
        mock_upload_response.error.message = "Storage upload failed"

        mock_storage = Mock()
        mock_storage.upload.return_value = mock_upload_response

        mock_supabase_client.storage.from_.return_value = mock_storage

        service = ProfileService(mock_supabase_client)

        # 验证抛出异常
        with pytest.raises(HTTPException) as exc_info:
            await service.upload_avatar(sample_avatar_file, user_id)

        assert exc_info.value.status_code == 400
        assert "Failed to upload avatar" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_upload_avatar_general_error(
        self, mock_supabase_client, sample_avatar_file
    ):
        """测试上传头像时一般错误"""
        user_id = "123e4567-e89b-12d3-a456-426614174000"

        # 模拟读取文件时出现异常
        sample_avatar_file.read.side_effect = Exception("File read error")

        service = ProfileService(mock_supabase_client)

        # 验证抛出异常
        with pytest.raises(HTTPException) as exc_info:
            await service.upload_avatar(sample_avatar_file, user_id)

        assert exc_info.value.status_code == 500
        assert "Error uploading avatar" in str(exc_info.value.detail)
