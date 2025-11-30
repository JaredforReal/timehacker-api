"""
用户资料服务
"""
import uuid
from datetime import datetime

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.orm import Profile
from app.models.schemas import AvatarUploadResponse, ProfileResponse, ProfileUpdate


class ProfileService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_profile(self, user_id: uuid.UUID) -> ProfileResponse:
        """
        获取用户个人资料
        """
        result = await self.db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            # 创建默认资料
            profile = Profile(
                user_id=user_id,
                name="",
                school=""
            )
            self.db.add(profile)
            await self.db.commit()
            await self.db.refresh(profile)
        
        return ProfileResponse(
            id=str(profile.id),
            user_id=str(profile.user_id),
            name=profile.name,
            school=profile.school,
            avatar=profile.avatar,
            created_at=profile.created_at,
            updated_at=profile.updated_at
        )

    async def update_profile(
        self, profile_data: ProfileUpdate, user_id: uuid.UUID
    ) -> ProfileResponse:
        """
        更新用户个人资料
        """
        result = await self.db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            # 创建新资料
            profile = Profile(
                user_id=user_id,
                name=profile_data.name or "",
                school=profile_data.school or "",
                avatar=profile_data.avatar
            )
            self.db.add(profile)
        else:
            # 更新现有资料
            update_data = profile_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(profile, field, value)
        
        await self.db.commit()
        await self.db.refresh(profile)
        
        return ProfileResponse(
            id=str(profile.id),
            user_id=str(profile.user_id),
            name=profile.name,
            school=profile.school,
            avatar=profile.avatar,
            created_at=profile.created_at,
            updated_at=profile.updated_at
        )

    async def upload_avatar(
        self, avatar: UploadFile, user_id: uuid.UUID
    ) -> AvatarUploadResponse:
        """
        上传用户头像到腾讯云 COS
        """
        try:
            from qcloud_cos import CosConfig, CosS3Client
            
            # 初始化 COS 客户端
            config = CosConfig(
                Region=settings.cos_region,
                SecretId=settings.cos_secret_id,
                SecretKey=settings.cos_secret_key
            )
            client = CosS3Client(config)
            
            # 读取文件内容
            contents = await avatar.read()
            
            # 生成文件名
            timestamp = int(datetime.utcnow().timestamp())
            file_key = f"avatars/{user_id}/{timestamp}.png"
            
            # 上传到 COS
            client.put_object(
                Bucket=settings.cos_bucket,
                Body=contents,
                Key=file_key,
                ContentType=avatar.content_type or "image/png"
            )
            
            # 构建公开访问 URL
            avatar_url = f"https://{settings.cos_bucket}.cos.{settings.cos_region}.myqcloud.com/{file_key}"
            
            # 更新数据库中的头像 URL
            result = await self.db.execute(
                select(Profile).where(Profile.user_id == user_id)
            )
            profile = result.scalar_one_or_none()
            
            if profile:
                profile.avatar = avatar_url
            else:
                profile = Profile(
                    user_id=user_id,
                    name="",
                    school="",
                    avatar=avatar_url
                )
                self.db.add(profile)
            
            await self.db.commit()
            
            return AvatarUploadResponse(url=avatar_url)
            
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="COS SDK 未安装"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"头像上传失败: {str(e)}"
            )
