"""
数据库连接和会话管理模块
使用 SQLAlchemy 2.0 async 风格
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# 创建异步数据库引擎
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # 开发模式下打印 SQL
    pool_pre_ping=True,  # 连接前检查
    pool_size=5,
    max_overflow=10,
)

# 创建异步会话工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ORM 基类
class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话（依赖注入用）
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    初始化数据库（创建所有表）
    注意：生产环境应使用 Alembic 迁移
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    关闭数据库连接
    """
    await engine.dispose()
