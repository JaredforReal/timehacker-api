from fastapi import HTTPException, UploadFile, status
from supabase import Client

from app.models.schemas import AvatarUploadResponse, ProfileResponse, ProfileUpdate


class ProfileService:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def get_profile(self, user_id: str) -> ProfileResponse:
        """
        获取用户个人资料
        """
        try:
            response = (
                self.supabase.table("profiles")
                .select("*")
                .eq("id", str(user_id))
                .single()
                .execute()
            )

            if not response.data:
                # 如果没有找到个人资料，创建一个空的
                default_profile = {
                    "id": str(user_id),
                    "name": "",
                    "school": "",
                    "avatar": None,
                }

                create_response = (
                    self.supabase.table("profiles").insert(default_profile).execute()
                )

                if create_response.data:
                    return create_response.data[0]
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to create profile",
                    )

            return response.data
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def update_profile(
        self, profile: ProfileUpdate, user_id: str
    ) -> ProfileResponse:
        """
        更新用户个人资料
        """
        try:
            # 检查是否已存在个人资料
            existing = (
                self.supabase.table("profiles")
                .select("*")
                .eq("id", str(user_id))
                .execute()
            )

            if not existing.data:
                # 如果没有找到个人资料，创建一个新的
                default_profile = {
                    "id": str(user_id),
                    "name": profile.name if profile.name else "",
                    "school": profile.school if profile.school else "",
                    "avatar": profile.avatar,
                }

                create_response = (
                    self.supabase.table("profiles").insert(default_profile).execute()
                )

                if create_response.data:
                    return create_response.data[0]
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to create profile",
                    )

            # 更新现有个人资料
            update_data = profile.model_dump(exclude_unset=True)
            response = (
                self.supabase.table("profiles")
                .update(update_data)
                .eq("id", str(user_id))
                .execute()
            )

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to update profile",
                )

            return response.data[0]
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def upload_avatar(
        self, avatar: UploadFile, user_id: str
    ) -> AvatarUploadResponse:
        """
        上传用户头像
        """
        try:
            # 读取文件内容
            contents = await avatar.read()

            # 上传到Supabase存储
            file_path = f"public/{user_id}.png"
            response = self.supabase.storage.from_("avatars").upload(
                file_path, contents, {"upsert": True}
            )

            if response.error:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to upload avatar: {response.error.message}",
                )

            # 获取公共URL
            url_response = self.supabase.storage.from_("avatars").get_public_url(
                file_path
            )

            # 更新用户头像URL
            self.supabase.table("profiles").update(
                {"avatar": url_response.data.get("publicUrl")}
            ).eq("id", str(user_id)).execute()

            return AvatarUploadResponse(url=url_response.data.get("publicUrl"))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error uploading avatar: {str(e)}",
            )
