from datetime import datetime

from pydantic import BaseModel, EmailStr


# 用户认证相关
class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr
    site_url: str | None = None


# Todo相关模型
class TodoCreate(BaseModel):
    title: str
    description: str | None = None


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_completed: bool | None = None


class TodoResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: str | None
    is_completed: bool
    created_at: str
    updated_at: str


# 番茄钟相关模型
class PomodoroSessionCreate(BaseModel):
    title: str
    duration: int
    completedAt: str


class PomodoroSessionUpdate(BaseModel):
    completed: bool | None = None
    end_time: datetime | None = None


class PomodoroSessionResponse(BaseModel):
    id: str
    user_id: str
    # 兼容前端显示所需字段
    title: str | None = None
    duration: int
    # 兼容旧字段与新字段
    completed: bool | None = None
    completedAt: str | None = None
    # 历史字段保留，便于后续扩展
    task_id: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    created_at: datetime
    updated_at: datetime


class PomodoroSettingsUpdate(BaseModel):
    work_duration: int | None = None
    short_break: int | None = None
    long_break: int | None = None
    sessions_until_long_break: int | None = None
    auto_start_breaks: bool | None = None
    auto_start_pomodoros: bool | None = None


class PomodoroSettingsResponse(BaseModel):
    id: str
    user_id: str
    work_duration: int
    short_break: int
    long_break: int
    sessions_until_long_break: int
    auto_start_breaks: bool
    auto_start_pomodoros: bool
    created_at: datetime
    updated_at: datetime


# 保持向后兼容的完整设置模型
class PomodoroSettings(BaseModel):
    workTime: int
    shortBreakTime: int
    longBreakTime: int
    sessionsUntilLongBreak: int


# 个人资料相关模型
class ProfileResponse(BaseModel):
    id: str
    name: str | None = None
    school: str | None = None
    avatar: str | None = None


class ProfileUpdate(BaseModel):
    name: str | None = None
    school: str | None = None
    avatar: str | None = None


# 通用响应模型
class MessageResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    message: str
    version: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class AvatarUploadResponse(BaseModel):
    url: str
