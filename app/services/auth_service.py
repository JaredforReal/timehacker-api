"""
认证服务：注册、登录、刷新令牌、密码重置
"""
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_password_reset_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_refresh_token,
)
from app.models.orm import PasswordResetToken, Profile, RefreshToken, User
from app.models.schemas import (
    AccessTokenResponse,
    MessageResponse,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, user_data: UserRegister) -> UserResponse:
        """
        用户注册
        """
        # 检查邮箱是否已注册
        result = await self.db.execute(
            select(User).where(User.email == user_data.email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已被注册"
            )
        
        # 创建用户
        password_hash = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            password_hash=password_hash,
            is_verified=False,
            is_active=True
        )
        self.db.add(new_user)
        await self.db.flush()
        
        # 创建空的个人资料
        profile = Profile(id=new_user.id)
        self.db.add(profile)
        
        await self.db.commit()
        await self.db.refresh(new_user)
        
        return UserResponse(
            id=str(new_user.id),
            email=new_user.email,
            is_verified=new_user.is_verified,
            created_at=new_user.created_at
        )

    async def login(self, user_login: UserLogin) -> TokenResponse:
        """
        用户登录
        """
        # 查询用户
        result = await self.db.execute(
            select(User).where(User.email == user_login.email)
        )
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(user_login.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱或密码错误"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账号已被禁用"
            )
        
        # 生成 tokens
        access_token = create_access_token(user.id, user.email)
        raw_refresh, token_hash, expires_at = create_refresh_token(user.id)
        
        # 保存 refresh token
        refresh_token_record = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        self.db.add(refresh_token_record)
        await self.db.commit()
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh,
            token_type="bearer"
        )

    async def refresh(self, request: RefreshTokenRequest) -> AccessTokenResponse:
        """
        刷新 Access Token
        """
        # 查找所有未过期的 refresh tokens
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.expires_at > datetime.now(timezone.utc)
            )
        )
        tokens = result.scalars().all()
        
        # 验证 token
        valid_token = None
        for token in tokens:
            if verify_refresh_token(request.refresh_token, token.token_hash):
                valid_token = token
                break
        
        if not valid_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效或已过期的刷新令牌"
            )
        
        # 获取用户
        result = await self.db.execute(
            select(User).where(User.id == valid_token.user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在或已被禁用"
            )
        
        # 生成新的 access token
        access_token = create_access_token(user.id, user.email)
        
        return AccessTokenResponse(
            access_token=access_token,
            token_type="bearer"
        )

    async def logout(self, user_id: uuid.UUID, refresh_token: str | None = None) -> MessageResponse:
        """
        用户登出（使 refresh token 失效）
        """
        if refresh_token:
            # 删除特定的 refresh token
            result = await self.db.execute(
                select(RefreshToken).where(RefreshToken.user_id == user_id)
            )
            tokens = result.scalars().all()
            
            for token in tokens:
                if verify_refresh_token(refresh_token, token.token_hash):
                    await self.db.delete(token)
                    break
        else:
            # 删除该用户所有的 refresh tokens
            await self.db.execute(
                delete(RefreshToken).where(RefreshToken.user_id == user_id)
            )
        
        await self.db.commit()
        return MessageResponse(message="登出成功")

    async def request_password_reset(self, request: PasswordResetRequest) -> MessageResponse:
        """
        请求密码重置（发送邮件）
        """
        # 查询用户
        result = await self.db.execute(
            select(User).where(User.email == request.email)
        )
        user = result.scalar_one_or_none()
        
        # 即使用户不存在也返回成功（防止邮箱枚举攻击）
        if not user:
            return MessageResponse(message="如果该邮箱已注册，您将收到密码重置邮件")
        
        # 创建重置令牌
        raw_token, token_hash, expires_at = create_password_reset_token()
        
        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            used=False
        )
        self.db.add(reset_token)
        await self.db.commit()
        
        # TODO: 发送邮件
        # 目前先返回 token（生产环境应改为邮件发送）
        # await send_password_reset_email(user.email, raw_token)
        
        return MessageResponse(message="如果该邮箱已注册，您将收到密码重置邮件")

    async def reset_password(self, request: PasswordResetConfirm) -> MessageResponse:
        """
        执行密码重置
        """
        # 查找有效的重置令牌
        result = await self.db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.expires_at > datetime.now(timezone.utc),
                PasswordResetToken.used == False  # noqa: E712
            )
        )
        tokens = result.scalars().all()
        
        valid_token = None
        for token in tokens:
            # passlib 的 verify 可以验证任何哈希
            from app.core.security import pwd_context
            if pwd_context.verify(request.token, token.token_hash):
                valid_token = token
                break
        
        if not valid_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效或已过期的重置令牌"
            )
        
        # 更新密码
        result = await self.db.execute(
            select(User).where(User.id == valid_token.user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        user.password_hash = get_password_hash(request.new_password)
        valid_token.used = True
        
        # 使所有 refresh tokens 失效
        await self.db.execute(
            delete(RefreshToken).where(RefreshToken.user_id == user.id)
        )
        
        await self.db.commit()
        
        return MessageResponse(message="密码重置成功")
