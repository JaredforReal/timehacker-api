from unittest.mock import Mock, patch

from supabase import Client

from app.models.database import (
    get_supabase_client,
    reset_supabase_client,
    set_supabase_client,
)


class TestSupabaseDatabase:
    """测试Supabase数据库连接"""

    def test_get_supabase_client_singleton(self):
        """测试Supabase客户端单例模式"""
        # 重置客户端确保干净状态
        reset_supabase_client()

        with patch("app.models.database.create_client") as mock_create:
            mock_client = Mock(spec=Client)
            mock_create.return_value = mock_client

            # 第一次调用应该创建客户端
            client1 = get_supabase_client()
            assert client1 == mock_client
            assert mock_create.call_count == 1

            # 第二次调用应该返回同一个实例
            client2 = get_supabase_client()
            assert client2 == mock_client
            assert client1 is client2
            assert mock_create.call_count == 1  # 没有再次调用create_client

    def test_set_supabase_client(self):
        """测试手动设置Supabase客户端"""
        reset_supabase_client()

        mock_client = Mock(spec=Client)
        set_supabase_client(mock_client)

        # 获取客户端应该返回我们设置的客户端
        client = get_supabase_client()
        assert client is mock_client

    def test_reset_supabase_client(self):
        """测试重置Supabase客户端"""
        # 先设置一个客户端
        mock_client = Mock(spec=Client)
        set_supabase_client(mock_client)

        # 确认客户端已设置
        assert get_supabase_client() is mock_client

        # 重置客户端
        reset_supabase_client()

        # 下次调用应该创建新的客户端
        with patch("app.models.database.create_client") as mock_create:
            new_mock_client = Mock(spec=Client)
            mock_create.return_value = new_mock_client

            client = get_supabase_client()
            assert client is new_mock_client
            assert mock_create.call_count == 1

    @patch("app.models.database.settings")
    @patch("app.models.database.create_client")
    def test_client_creation_with_settings(self, mock_create, mock_settings):
        """测试使用配置创建客户端"""
        reset_supabase_client()

        # 模拟配置
        mock_settings.supabase_url = "https://test.supabase.co"
        mock_settings.supabase_key = "test-key"

        mock_client = Mock(spec=Client)
        mock_create.return_value = mock_client

        client = get_supabase_client()

        # 验证使用正确的参数调用create_client
        mock_create.assert_called_once_with("https://test.supabase.co", "test-key")
        assert client is mock_client
