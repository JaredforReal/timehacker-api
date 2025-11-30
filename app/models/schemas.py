from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# ============ 用户认证相关 ============

class UserRegister(BaseModel):
    """用户注册请求"""
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    """用户登录请求"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """登录成功响应（带刷新令牌）"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str


class TokenResponseWithRefresh(BaseModel):
    """完整的 Token 响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str


class AccessTokenResponse(BaseModel):
    """刷新令牌响应"""
    access_token: str
    token_type: str = "bearer"


class PasswordResetRequest(BaseModel):
    """请求密码重置"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """执行密码重置"""
    token: str
    new_password: str = Field(min_length=6, max_length=128)


class UserResponse(BaseModel):
    """用户信息响应"""
    id: str
    email: str
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Todo 相关模型 ============

class TodoCreate(BaseModel):
    """创建待办"""
    title: str = Field(max_length=500)
    description: str | None = None
    # 日历排程字段（可选）
    start_at: datetime | None = None
    end_at: datetime | None = None
    all_day: bool = False
    color: str | None = None


class TodoUpdate(BaseModel):
    """更新待办"""
    title: str | None = None
    description: str | None = None
    is_completed: bool | None = None
    # 日历排程字段
    start_at: datetime | None = None
    end_at: datetime | None = None
    all_day: bool | None = None
    color: str | None = None


class TodoResponse(BaseModel):
    """待办响应"""
    id: str
    user_id: str
    title: str
    description: str | None
    is_completed: bool
    # 日历排程字段
    start_at: datetime | None = None
    end_at: datetime | None = None
    all_day: bool = False
    color: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ 番茄钟相关模型 ============

class PomodoroSessionCreate(BaseModel):
    """创建番茄钟会话"""
    title: str
    duration: int
    completedAt: str  # 前端传 ISO 字符串


class PomodoroSessionResponse(BaseModel):
    """番茄钟会话响应"""
    id: str
    user_id: str
    title: str | None = None
    duration: int
    completedAt: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PomodoroSettings(BaseModel):
    """番茄钟设置（前端兼容格式）"""
    workTime: int
    shortBreakTime: int
    longBreakTime: int
    sessionsUntilLongBreak: int


class PomodoroSettingsResponse(BaseModel):
    """番茄钟设置响应"""
    workTime: int
    shortBreakTime: int
    longBreakTime: int
    sessionsUntilLongBreak: int


# ============ 个人资料相关模型 ============

class ProfileResponse(BaseModel):
    """个人资料响应"""
    id: str
    user_id: str
    name: str | None = None
    school: str | None = None
    avatar: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    """更新个人资料"""
    name: str | None = None
    school: str | None = None
    avatar: str | None = None


class AvatarUploadResponse(BaseModel):
    """头像上传响应"""
    url: str


# ============ 通用响应模型 ============

class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    message: str
    version: str
