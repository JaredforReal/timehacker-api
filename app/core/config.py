from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 应用设置
    app_name: str = "TimeHacker API"
    app_version: str = "1.0.0"
    debug: bool = False

    # 数据库设置 (PostgreSQL)
    database_url: str = Field(
        default="postgresql+asyncpg://timehacker:password@localhost:5432/timehacker",
        alias="DATABASE_URL"
    )

    # JWT 认证设置
    secret_key: str = Field(alias="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # 服务器设置
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS设置
    allowed_origins: list[str] = [
        "http://localhost:5173",
        "https://www.timehacker.cn",
        "https://timehacker.cn",
        "https://api.timehacker.cn",
    ]

    # 前端地址（用于密码重置邮件链接等）
    frontend_url: str = Field(default="https://www.timehacker.cn", alias="FRONTEND_URL")

    # 腾讯云 COS 设置（头像存储）
    cos_secret_id: str = Field(default="", alias="COS_SECRET_ID")
    cos_secret_key: str = Field(default="", alias="COS_SECRET_KEY")
    cos_bucket: str = Field(default="", alias="COS_BUCKET")
    cos_region: str = Field(default="ap-guangzhou", alias="COS_REGION")

    # 邮件设置（密码重置）
    smtp_host: str = Field(default="smtp.qq.com", alias="SMTP_HOST")
    smtp_port: int = Field(default=465, alias="SMTP_PORT")
    smtp_user: str = Field(default="", alias="SMTP_USER")
    smtp_password: str = Field(default="", alias="SMTP_PASSWORD")
    smtp_from_email: str = Field(default="", alias="SMTP_FROM_EMAIL")

    class Config:
        env_file = ".env"
        case_sensitive = False


# 创建全局设置实例
settings = Settings()
