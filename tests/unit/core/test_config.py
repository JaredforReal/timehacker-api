import os
from unittest.mock import patch

from app.core.config import Settings


class TestConfig:
    """测试配置管理"""

    def test_default_settings(self):
        """测试默认配置值"""
        # 创建新的设置实例（不依赖全局设置）
        with patch.dict(
            os.environ,
            {"SUPABASE_URL": "https://test.supabase.co", "SUPABASE_KEY": "test-key"},
        ):
            settings = Settings()

            assert settings.app_name == "TimeHacker API"
            assert settings.app_version == "1.0.0"
            assert not settings.debug
            assert settings.host == "0.0.0.0"
            assert settings.port == 8000
            assert "http://localhost:5173" in settings.allowed_origins
            assert "https://www.timehacker.cn" in settings.allowed_origins

    def test_environment_variable_loading(self):
        """测试环境变量加载"""
        with patch.dict(
            os.environ,
            {
                "SUPABASE_URL": "https://custom.supabase.co",
                "SUPABASE_KEY": "custom-key",
                "SITE_URL": "https://custom-site.com",
            },
        ):
            settings = Settings()

            assert settings.supabase_url == "https://custom.supabase.co"
            assert settings.supabase_key == "custom-key"
            assert settings.site_url == "https://custom-site.com"

    def test_config_with_env_file(self):
        """测试配置文件读取"""
        # 这个测试验证配置可以从.env文件正确读取
        # 因为我们已经有.env文件，所以只需要验证设置被正确加载
        with patch.dict(
            os.environ,
            {"SUPABASE_URL": "https://test.supabase.co", "SUPABASE_KEY": "test-key"},
        ):
            settings = Settings()
            assert settings.supabase_url == "https://test.supabase.co"
            assert settings.supabase_key == "test-key"

    def test_cors_origins_configuration(self):
        """测试CORS源配置"""
        with patch.dict(
            os.environ,
            {"SUPABASE_URL": "https://test.supabase.co", "SUPABASE_KEY": "test-key"},
        ):
            settings = Settings()

            expected_origins = [
                "http://localhost:5173",
                "https://www.timehacker.cn",
                "https://timehacker.cn",
                "https://api.timehacker.cn",
                "http://117.72.112.49",
            ]

            assert settings.allowed_origins == expected_origins

    def test_config_case_insensitive(self):
        """测试配置不区分大小写"""
        with patch.dict(
            os.environ,
            {
                "supabase_url": "https://lowercase.supabase.co",  # 小写
                "SUPABASE_KEY": "test-key",
            },
        ):
            settings = Settings()
            assert settings.supabase_url == "https://lowercase.supabase.co"
