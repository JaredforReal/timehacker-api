from supabase import Client, create_client

from app.core.config import settings

# 全局Supabase客户端实例（单例模式）
_supabase_client: Client = None


def get_supabase_client() -> Client:
    """
    获取Supabase客户端实例（单例模式）
    """
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(settings.supabase_url, settings.supabase_key)
    return _supabase_client


def set_supabase_client(client: Client) -> None:
    """
    设置Supabase客户端实例（主要用于测试）
    """
    global _supabase_client
    _supabase_client = client


def reset_supabase_client() -> None:
    """
    重置Supabase客户端实例（主要用于测试清理）
    """
    global _supabase_client
    _supabase_client = None
