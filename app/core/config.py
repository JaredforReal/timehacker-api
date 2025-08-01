from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 应用设置
    app_name: str = "TimeHacker API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Supabase设置
    supabase_url: str = Field(alias="SUPABASE_URL")
    supabase_key: str = Field(alias="SUPABASE_KEY")

    # 服务器设置
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS设置
    allowed_origins: list[str] = [
        "http://localhost:5173",
        "https://www.timehacker.cn",
        "https://timehacker.cn",
        "https://api.timehacker.cn",
        "http://117.72.112.49",
    ]

    # 其他设置
    site_url: str = Field(default="https://www.timehacker.cn", alias="SITE_URL")

    class Config:
        env_file = ".env"
        case_sensitive = False


# 创建全局设置实例
settings = Settings()
