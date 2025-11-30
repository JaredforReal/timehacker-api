"""
安全模块：JWT 认证、密码哈希
"""
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.database import get_async_session

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer Token 验证
security = HTTPBearer()


class TokenData(BaseModel):
    """JWT Token 载荷"""
    user_id: str
    email: str
    exp: datetime


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def create_access_token(user_id: uuid.UUID, email: str) -> str:
    """
    创建 Access Token (短期)
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(user_id: uuid.UUID) -> tuple[str, str, datetime]:
    """
    创建 Refresh Token (长期)
    返回: (原始token, token哈希, 过期时间)
    """
    raw_token = secrets.token_urlsafe(32)
    token_hash = pwd_context.hash(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    return raw_token, token_hash, expires_at


def verify_refresh_token(raw_token: str, token_hash: str) -> bool:
    """验证 Refresh Token"""
    return pwd_context.verify(raw_token, token_hash)


def decode_access_token(token: str) -> TokenData:
    """
    解码并验证 Access Token
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        email = payload.get("email")
        exp = payload.get("exp")
        
        if not user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        return TokenData(
            user_id=user_id,
            email=email,
            exp=datetime.fromtimestamp(exp, tz=timezone.utc)
        )
    
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    """
    获取当前认证用户（依赖注入）
    """
    from app.models.orm import User
    
    token = credentials.credentials
    token_data = decode_access_token(token)
    
    # 查询用户
    result = await db.execute(
        select(User).where(User.id == uuid.UUID(token_data.user_id))
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    return user


def create_password_reset_token() -> tuple[str, str, datetime]:
    """
    创建密码重置令牌
    返回: (原始token, token哈希, 过期时间)
    """
    raw_token = secrets.token_urlsafe(32)
    token_hash = pwd_context.hash(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)  # 1小时有效
    return raw_token, token_hash, expires_at
