from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from app.models.schemas import PomodoroSessionCreate, PomodoroSettings
from app.services.pomodoro_service import PomodoroService


class TestPomodoroService:
    @pytest.fixture
    def sample_session_data(self):
        return {
            "id": "1",
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "工作任务",
            "duration": 25,
            "completedat": "2025-01-01T10:00:00Z",
            "created_at": "2025-01-01T09:00:00Z",
        }

    @pytest.fixture
    def sample_settings_data(self):
        return {
            "id": "1",
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "worktime": 25,
            "shortbreaktime": 5,
            "longbreaktime": 15,
            "sessionsuntillongbreak": 4,
        }

    @pytest.mark.asyncio
    async def test_get_sessions_success(
        self, mock_supabase_client, sample_session_data
    ):
        """测试成功获取番茄钟会话列表"""
        # 准备模拟数据
        mock_response = Mock()
        mock_response.data = [sample_session_data]
        mock_response.error = None

        mock_supabase_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = (
            mock_response
        )

        # 创建服务实例
        service = PomodoroService(mock_supabase_client)
        user_id = "123e4567-e89b-12d3-a456-426614174000"

        # 执行测试
        result = await service.get_sessions(user_id)

        # 验证结果
        assert len(result) == 1
        assert result[0]["id"] == "1"
        assert result[0]["user_id"] == user_id
        assert result[0]["completedAt"] == "2025-01-01T10:00:00Z"

        # 验证数据库调用
        mock_supabase_client.table.assert_called_with("pomodoro_sessions")
        mock_supabase_client.table.return_value.select.assert_called_with("*")
        mock_supabase_client.table.return_value.select.return_value.eq.assert_called_with(
            "user_id", user_id
        )

    @pytest.mark.asyncio
    async def test_get_sessions_database_error(self, mock_supabase_client):
        """测试获取会话时数据库错误"""
        # 模拟数据库错误
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.side_effect = Exception(
            "Database connection error"
        )

        service = PomodoroService(mock_supabase_client)
        user_id = "123e4567-e89b-12d3-a456-426614174000"

        # 验证抛出异常
        with pytest.raises(HTTPException) as exc_info:
            await service.get_sessions(user_id)

        assert exc_info.value.status_code == 500
        assert "Database error" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_create_session_success(
        self, mock_supabase_client, sample_session_data
    ):
        """测试成功创建番茄钟会话"""
        # 准备模拟数据
        mock_response = Mock()
        mock_response.data = [sample_session_data]
        mock_response.error = None

        mock_supabase_client.table.return_value.insert.return_value.execute.return_value = (
            mock_response
        )

        # 创建服务实例
        service = PomodoroService(mock_supabase_client)
        user_id = "123e4567-e89b-12d3-a456-426614174000"

        # 创建请求数据（使用实际的模式）
        session_data = PomodoroSessionCreate(
            title="工作任务", duration=25, completedAt="2025-01-01T10:00:00Z"
        )

        # 执行测试
        result = await service.create_session(session_data, user_id)

        # 验证结果
        assert result["id"] == "1"
        assert result["user_id"] == user_id
        assert result["duration"] == 25

        # 验证数据库调用
        mock_supabase_client.table.assert_called_with("pomodoro_sessions")
        mock_supabase_client.table.return_value.insert.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_session_failed(self, mock_supabase_client):
        """测试创建会话失败"""
        # 准备模拟数据 - 创建失败
        mock_response = Mock()
        mock_response.data = None
        mock_response.error = None

        mock_supabase_client.table.return_value.insert.return_value.execute.return_value = (
            mock_response
        )

        service = PomodoroService(mock_supabase_client)
        user_id = "123e4567-e89b-12d3-a456-426614174000"

        session_data = PomodoroSessionCreate(
            title="工作任务", duration=25, completedAt="2025-01-01T10:00:00Z"
        )

        # 验证抛出异常
        with pytest.raises(HTTPException) as exc_info:
            await service.create_session(session_data, user_id)

        assert exc_info.value.status_code == 400
        assert "Failed to create pomodoro session" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_create_session_database_error(self, mock_supabase_client):
        """测试创建会话时数据库错误"""
        # 模拟数据库错误
        mock_supabase_client.table.return_value.insert.return_value.execute.side_effect = Exception(
            "Database connection error"
        )

        service = PomodoroService(mock_supabase_client)
        user_id = "123e4567-e89b-12d3-a456-426614174000"

        session_data = PomodoroSessionCreate(
            title="工作任务", duration=25, completedAt="2025-01-01T10:00:00Z"
        )

        # 验证抛出异常
        with pytest.raises(HTTPException) as exc_info:
            await service.create_session(session_data, user_id)

        assert exc_info.value.status_code == 500
        assert "Database error" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_settings_success(
        self, mock_supabase_client, sample_settings_data
    ):
        """测试成功获取番茄钟设置"""
        # 准备模拟数据
        mock_response = Mock()
        mock_response.data = [sample_settings_data]
        mock_response.error = None

        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value = (
            mock_response
        )

        # 创建服务实例
        service = PomodoroService(mock_supabase_client)
        user_id = "123e4567-e89b-12d3-a456-426614174000"

        # 执行测试
        result = await service.get_settings(user_id)

        # 验证结果
        assert result.workTime == 25
        assert result.shortBreakTime == 5
        assert result.longBreakTime == 15
        assert result.sessionsUntilLongBreak == 4

        # 验证数据库调用
        mock_supabase_client.table.assert_called_with("pomodoro_settings")

    @pytest.mark.asyncio
    async def test_get_settings_create_default(self, mock_supabase_client):
        """测试获取设置时创建默认设置"""
        # 第一次调用返回空（没有设置）
        mock_response_empty = Mock()
        mock_response_empty.data = []
        mock_response_empty.error = None

        # 第二次调用返回创建的默认设置
        default_settings = {
            "id": "1",
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "worktime": 25,
            "shortbreaktime": 5,
            "longbreaktime": 15,
            "sessionsuntillongbreak": 4,
        }
        mock_response_created = Mock()
        mock_response_created.data = [default_settings]
        mock_response_created.error = None

        # 设置两个不同的table()调用
        mock_table_select = Mock()
        mock_table_insert = Mock()

        # 第一次调用table()用于select，第二次用于insert
        mock_supabase_client.table.side_effect = [mock_table_select, mock_table_insert]

        # 设置select调用链
        mock_table_select.select.return_value.eq.return_value.execute.return_value = (
            mock_response_empty
        )

        # 设置insert调用链
        mock_table_insert.insert.return_value.execute.return_value = (
            mock_response_created
        )

        service = PomodoroService(mock_supabase_client)
        user_id = "123e4567-e89b-12d3-a456-426614174000"

        # 执行测试
        result = await service.get_settings(user_id)

        # 验证结果
        assert result.workTime == 25
        assert result.shortBreakTime == 5

        # 验证调用了插入操作
        mock_table_insert.insert.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_settings_create_default_fallback(self, mock_supabase_client):
        """测试获取设置时创建默认设置失败的回退机制"""
        # 查询返回空
        mock_response_empty = Mock()
        mock_response_empty.data = []
        mock_response_empty.error = None

        # 创建失败
        mock_response_failed = Mock()
        mock_response_failed.data = None
        mock_response_failed.error = None

        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value = (
            mock_response_empty
        )
        mock_supabase_client.table.return_value.insert.return_value.execute.return_value = (
            mock_response_failed
        )

        service = PomodoroService(mock_supabase_client)
        user_id = "123e4567-e89b-12d3-a456-426614174000"

        # 执行测试
        result = await service.get_settings(user_id)

        # 验证返回默认值
        assert result.workTime == 25
        assert result.shortBreakTime == 5
        assert result.longBreakTime == 15
        assert result.sessionsUntilLongBreak == 4

    @pytest.mark.asyncio
    async def test_get_settings_database_error(self, mock_supabase_client):
        """测试获取设置时数据库错误"""
        # 模拟数据库错误
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception(
            "Database connection error"
        )

        service = PomodoroService(mock_supabase_client)
        user_id = "123e4567-e89b-12d3-a456-426614174000"

        # 验证抛出异常
        with pytest.raises(HTTPException) as exc_info:
            await service.get_settings(user_id)

        assert exc_info.value.status_code == 500
        assert "Database error" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_update_settings_success(
        self, mock_supabase_client, sample_settings_data
    ):
        """测试成功更新番茄钟设置"""
        # 模拟已存在的设置
        mock_existing_response = Mock()
        mock_existing_response.data = [sample_settings_data]
        mock_existing_response.error = None

        # 模拟更新成功
        updated_settings = sample_settings_data.copy()
        updated_settings["worktime"] = 30

        mock_update_response = Mock()
        mock_update_response.data = [updated_settings]
        mock_update_response.error = None

        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value = (
            mock_existing_response
        )
        mock_supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value = (
            mock_update_response
        )

        # 创建服务实例
        service = PomodoroService(mock_supabase_client)
        user_id = "123e4567-e89b-12d3-a456-426614174000"

        # 创建更新数据
        settings_data = PomodoroSettings(
            workTime=30, shortBreakTime=5, longBreakTime=15, sessionsUntilLongBreak=4
        )

        # 执行测试
        result = await service.update_settings(settings_data, user_id)

        # 验证结果
        assert result.workTime == 30

        # 验证数据库调用
        mock_supabase_client.table.return_value.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_settings_create_new(
        self, mock_supabase_client, sample_settings_data
    ):
        """测试更新设置时创建新设置"""
        # 模拟不存在的设置
        mock_existing_response = Mock()
        mock_existing_response.data = []
        mock_existing_response.error = None

        # 模拟创建成功
        mock_create_response = Mock()
        mock_create_response.data = [sample_settings_data]
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

        service = PomodoroService(mock_supabase_client)
        user_id = "123e4567-e89b-12d3-a456-426614174000"

        settings_data = PomodoroSettings(
            workTime=25, shortBreakTime=5, longBreakTime=15, sessionsUntilLongBreak=4
        )

        # 执行测试
        result = await service.update_settings(settings_data, user_id)

        # 验证结果
        assert result.workTime == 25

        # 验证调用了插入操作
        mock_table_insert.insert.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_settings_validation_error(self, mock_supabase_client):
        """测试更新设置时验证错误"""
        service = PomodoroService(mock_supabase_client)
        user_id = "123e4567-e89b-12d3-a456-426614174000"

        # 创建无效的设置数据（值小于1）
        settings_data = PomodoroSettings(
            workTime=0,  # 无效值
            shortBreakTime=5,
            longBreakTime=15,
            sessionsUntilLongBreak=4,
        )

        # 验证抛出异常
        with pytest.raises(HTTPException) as exc_info:
            await service.update_settings(settings_data, user_id)

        assert exc_info.value.status_code == 400
        assert "All settings values must be greater than 0" in str(
            exc_info.value.detail
        )

    @pytest.mark.asyncio
    async def test_update_settings_failed(self, mock_supabase_client):
        """测试更新设置失败"""
        # 模拟已存在的设置
        mock_existing_response = Mock()
        mock_existing_response.data = [{"id": "1"}]
        mock_existing_response.error = None

        # 模拟更新失败
        mock_update_response = Mock()
        mock_update_response.data = None
        mock_update_response.error = None

        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value = (
            mock_existing_response
        )
        mock_supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value = (
            mock_update_response
        )

        service = PomodoroService(mock_supabase_client)
        user_id = "123e4567-e89b-12d3-a456-426614174000"

        settings_data = PomodoroSettings(
            workTime=25, shortBreakTime=5, longBreakTime=15, sessionsUntilLongBreak=4
        )

        # 验证抛出异常
        with pytest.raises(HTTPException) as exc_info:
            await service.update_settings(settings_data, user_id)

        assert exc_info.value.status_code == 400
        assert "Failed to update pomodoro settings" in str(exc_info.value.detail)
