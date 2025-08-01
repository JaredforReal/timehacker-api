from fastapi import HTTPException, status
from supabase import Client

from app.core.config import settings
from app.models.schemas import PasswordResetRequest, TokenResponse, UserLogin


class AuthService:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def login(self, user_login: UserLogin) -> TokenResponse:
        """
        用户登录
        """
        try:
            response = self.supabase.auth.sign_in_with_password(
                {"email": user_login.email, "password": user_login.password}
            )

            return TokenResponse(
                access_token=response.session.access_token, token_type="bearer"
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

    async def request_password_reset(self, reset_request: PasswordResetRequest) -> dict:
        """
        请求密码重置
        """
        try:
            if not reset_request.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Email is required"
                )

            site_url = reset_request.site_url or settings.site_url

            response = self.supabase.auth.reset_password_for_email(
                reset_request.email, {"redirectTo": f"{site_url}/reset-password"}
            )

            if response.error:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to send reset email: {response.error.message}",
                )

            return {"message": "Password reset email sent"}

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error requesting password reset: {str(e)}",
            )
