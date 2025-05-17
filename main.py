# Standard library imports
import os
import jwt
import logging
import time

# Third-party imports
from dotenv import load_dotenv
from typing import List, Optional
from pydantic import BaseModel

# FastAPI imports
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Redis-FastAPI imports
from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from contextlib import asynccontextmanager
from fastapi_cache.backends.inmemory import InMemoryBackend 

# Database imports
from supabase import create_client, Client
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
import os
import jwt

# 加载环境变量
load_dotenv()

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 缓存配置
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Redis配置
        redis = aioredis.from_url(
            os.getenv("REDIS_URL"),
            encoding="utf-8",
            decode_responses=True
        )
        await redis.ping()
        logger.info("Redis connection established")
        
        FastAPICache.init(
            RedisBackend(redis),
            prefix="fastapi-cache"
        )
        logger.info("FastAPICache initialized")
    except Exception as e:
        logger.warning(f"Redis connection failed: {str(e)}")
        logger.info("Using in-memory cache")
        FastAPICache.init(InMemoryBackend())

    yield

    try:
        if hasattr(FastAPICache, "_backend") and hasattr(FastAPICache._backend, "redis"):
            await FastAPICache._backend.redis.close()
            logger.info("Redis connection closed")
    except Exception as e:
        logger.error(f"Error closing Redis connection: {str(e)}")

app = FastAPI(lifespan=lifespan)

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],  # 允许所有来源
    allow_origins=["http://localhost:5173",
                   "https://www.timehacker.cn",
                   "https://timehacker.cn",
                   "https://api.timehacker.cn",
                   "http://117.72.112.49",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# 直接从环境变量获取
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# TodoList数据模型
class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None

class TodoResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str]
    is_completed: bool
    created_at: str
    updated_at: str
    
class UserLogin(BaseModel):
    email: str
    password: str

# 番茄钟数据模型
class PomodoroSessionCreate(BaseModel):
    title: str
    duration: int
    completedAt: str

class PomodoroSessionResponse(BaseModel):
    id: str
    user_id: str
    title: str
    duration: int
    completedAt: str
    created_at: str

class PomodoroSettings(BaseModel):
    workTime: int
    shortBreakTime: int
    longBreakTime: int
    sessionsUntilLongBreak: int

# 个人资料模型
class ProfileResponse(BaseModel):
    id: str
    name: Optional[str] = None
    school: Optional[str] = None
    avatar: Optional[str] = None
    
class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    school: Optional[str] = None
    avatar: Optional[str] = None

# 认证依赖
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    try:
        token = credentials.credentials
        # 验证token格式
        if len(token.split(".")) != 3:
            raise HTTPException(status_code=401, detail="Invalid token format")
            
        user = supabase.auth.get_user(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
            
        # 验证用户状态
        if user.user.is_anonymous:
            raise HTTPException(status_code=403, detail="Anonymous access denied")
            
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auth error: {str(e)}")


# API端点
@app.get("/api/")
@cache(expire=30)  # Cache for 30 seconds
async def read_root():
    return {"message": "Hello from API"}

# Health check endpoint
@app.get("/")
@cache(expire=30)  # Cache for 30 seconds
async def health_check():
    return {
        "status": "ok", 
        "message": "Todo API is running",
        "version": "1.1.0"  # Consider adding version info
    }

@app.post("/token")
async def login(user: UserLogin):
    try:
        # 调用 Supabase 登录接口
        response = supabase.auth.sign_in_with_password({
            "email": user.email,
            "password": user.password
        })
        return {
            "access_token": response.session.access_token,
            "token_type": "bearer"
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

@app.get("/todos", response_model=List[TodoResponse])
@cache(expire=60)  # Cache for 60 seconds
async def get_todos(user = Depends(get_current_user)):
    try:
        response = supabase.table("todos").select("*").eq("user_id", user.user.id).execute()
        return response.data
    except Exception as e:
        print(f"Error fetching todos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )

# TodoList API
@app.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoCreate, user = Depends(get_current_user)):
    try:
        todo_data = todo.dict()
        todo_data["user_id"] = str(user.user.id)  # Ensure user_id is string if your DB uses UUID
        response = supabase.table("todos").insert(todo_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create todo"
            )
            
        return response.data[0]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@app.put("/todos/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: str, 
    todo: TodoUpdate, 
    user = Depends(get_current_user)
):
    try:
        # First verify the todo exists and belongs to the user
        existing = supabase.table("todos")\
            .select("*")\
            .eq("id", todo_id)\
            .eq("user_id", str(user.user.id))\
            .execute()
            
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Todo not found"
            )
        
        # Update only the fields that were provided
        update_data = todo.dict(exclude_unset=True)
        response = supabase.table("todos")\
            .update(update_data)\
            .eq("id", todo_id)\
            .execute()
            
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update todo"
            )
            
        return response.data[0]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: str, user = Depends(get_current_user)):
    try:
        # Combine check and delete in one operation for efficiency
        response = supabase.table("todos")\
            .delete()\
            .eq("id", todo_id)\
            .eq("user_id", str(user.user.id))\
            .execute()
            
        # Check if anything was deleted
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Todo not found"
            )
        
        # Invalidate relevant caches to ensure data consistency
        await FastAPICache.clear(namespace="fastapi-cache")
        
        return None
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

# 番茄钟 API 端点
@app.post("/pomodoro/sessions", response_model=PomodoroSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_pomodoro_session(session: PomodoroSessionCreate, user = Depends(get_current_user)):
    try:
        session_data = {
            "title": session.title,
            "duration": session.duration,
            "completedat": session.completedAt,  # 注意这里转换为小写
            "user_id": str(user.user.id)
        }
        
        response = supabase.table("pomodoro_sessions").insert(session_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create pomodoro session"
            )
            
        result = dict(response.data[0])
        if "completedat" in result:
            result["completedAt"] = result.pop("completedat")
        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@app.get("/pomodoro/sessions", response_model=List[PomodoroSessionResponse])
@cache(expire=60)  # Cache for 60 seconds
async def get_pomodoro_sessions(user = Depends(get_current_user)):
    try:
        response = supabase.table("pomodoro_sessions")\
            .select("*")\
            .eq("user_id", str(user.user.id))\
            .order("completedat", desc=True)\
            .limit(50)\
            .execute()
        
        result = []
        for session in response.data:
            session_dict = dict(session)
            if "completedat" in session_dict:
                session_dict["completedAt"] = session_dict.pop("completedat")
            result.append(session_dict)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@app.get("/pomodoro/settings", response_model=PomodoroSettings)
@cache(expire=60)  # Cache for 60 seconds
async def get_pomodoro_settings(user = Depends(get_current_user)):
    try:
        # 获取用户的番茄钟设置
        response = supabase.table("pomodoro_settings")\
            .select("*")\
            .eq("user_id", str(user.user.id))\
            .execute()
        
        # 如果找到设置则返回
        if response.data and len(response.data) > 0:
            settings = dict(response.data[0])
            converted_settings = {
                "workTime": settings.get("worktime", 25),
                "shortBreakTime": settings.get("shortbreaktime", 5),
                "longBreakTime": settings.get("longbreaktime", 15),
                "sessionsUntilLongBreak": settings.get("sessionsuntillongbreak", 4)
            }
            return converted_settings
        
        # 如果未找到，则使用默认设置并创建
        default_settings = {
            "user_id": str(user.user.id),
            "worktime": 25,
            "shortbreaktime": 5,
            "longbreaktime": 15,
            "sessionsuntillongbreak": 4
        }
        
        create_response = supabase.table("pomodoro_settings")\
            .insert(default_settings)\
            .execute()
        
        if create_response.data:
            settings = dict(create_response.data[0])
            converted_settings = {
                "workTime": settings.get("worktime", 25),
                "shortBreakTime": settings.get("shortbreaktime", 5),
                "longBreakTime": settings.get("longbreaktime", 15),
                "sessionsUntilLongBreak": settings.get("sessionsuntillongbreak", 4)
            }
            return converted_settings
        else:
            return {
                "workTime": 25,
                "shortBreakTime": 5,
                "longBreakTime": 15,
                "sessionsUntilLongBreak": 4
            }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@app.put("/pomodoro/settings", response_model=PomodoroSettings)
async def update_pomodoro_settings(settings: PomodoroSettings, user = Depends(get_current_user)):
    try:
        # Log inputs for debugging
        logger.info(f"Updating settings for user: {user.user.id}")
        logger.info(f"New settings: {settings.dict()}")

        # Validate settings values
        if (settings.workTime < 1 or settings.shortBreakTime < 1 or 
            settings.longBreakTime < 1 or settings.sessionsUntilLongBreak < 1):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All settings values must be greater than 0"
            )
        
        # Convert to database format with lowercase keys
        settings_data = {
            "user_id": str(user.user.id),
            "worktime": settings.workTime,
            "shortbreaktime": settings.shortBreakTime,
            "longbreaktime": settings.longBreakTime,
            "sessionsuntillongbreak": settings.sessionsUntilLongBreak
        }
        
        # 首先检查是否已存在设置
        existing = supabase.table("pomodoro_settings")\
            .select("*")\
            .eq("user_id", str(user.user.id))\
            .execute()
        
        if existing.data and len(existing.data) > 0:
            # 更新现有设置
            response = supabase.table("pomodoro_settings")\
                .update(settings_data)\
                .eq("user_id", str(user.user.id))\
                .execute()
        else:
            # 创建新设置
            response = supabase.table("pomodoro_settings")\
                .insert(settings_data)\
                .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update pomodoro settings"
            )
            
        settings = dict(response.data[0])
        converted_settings = {
            "workTime": settings["worktime"],
            "shortBreakTime": settings["shortbreaktime"],
            "longBreakTime": settings["longbreaktime"],
            "sessionsUntilLongBreak": settings["sessionsuntillongbreak"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


# 获取个人资料
@app.get("/profile", response_model=ProfileResponse)
async def get_profile(user = Depends(get_current_user)):
    try:
        response = supabase.table("profiles")\
            .select("*")\
            .eq("id", str(user.user.id))\
            .single()\
            .execute()
            
        if not response.data:
            # 如果没有找到个人资料，创建一个空的
            default_profile = {
                "id": str(user.user.id),
                "name": "",
                "school": "",
                "avatar": None
            }
            
            create_response = supabase.table("profiles")\
                .insert(default_profile)\
                .execute()
                
            if create_response.data:
                return create_response.data[0]
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create profile"
                )
        
        return response.data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

# 更新个人资料
@app.put("/profile", response_model=ProfileResponse)
async def update_profile(profile: ProfileUpdate, user = Depends(get_current_user)):
    try:
        # 检查是否已存在个人资料
        existing = supabase.table("profiles")\
            .select("*")\
            .eq("id", str(user.user.id))\
            .execute()
            
        if not existing.data:
            # 如果没有找到个人资料，创建一个新的
            default_profile = {
                "id": str(user.user.id),
                "name": profile.name if profile.name else "",
                "school": profile.school if profile.school else "",
                "avatar": profile.avatar
            }
            
            create_response = supabase.table("profiles")\
                .insert(default_profile)\
                .execute()
                
            if create_response.data:
                return create_response.data[0]
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create profile"
                )
        # 更新现有个人资料
        update_data = profile.dict(exclude_unset=True)
        response = supabase.table("profiles")\
            .update(update_data)\
            .eq("id", str(user.user.id))\
            .execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

# 上传头像
@app.post("/profile/avatar", response_model=dict)
async def upload_avatar(avatar: UploadFile = File(...), user = Depends(get_current_user)):
    try:
        # 读取文件内容
        contents = await avatar.read()
        
        # 上传到Supabase存储
        file_path = f"public/{user.user.id}.png"
        response = supabase.storage.from_("avatars").upload(file_path, contents, {"upsert": True})
            
        if response.error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to upload avatar: {response.error.message}"
            )
            
        # 获取公共URL
        url_response = supabase.storage.from_("avatars").get_public_url(file_path)
            
        # 更新用户头像URL
        supabase.table("profiles")\
            .update({"avatar": url_response.data.get("publicUrl")})\
            .eq("id", str(user.user.id))\
            .execute()
            
        return {"url": url_response.data.get("publicUrl")}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading avatar: {str(e)}"
        )
        
# 密码重置请求
@app.post("/auth/reset-password")
async def request_password_reset(reset_data: dict):
    try:
        email = reset_data.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )
            
        # 获取前端URL用于重定向
        site_url = reset_data.get("site_url", os.getenv("SITE_URL", "https://www.timehacker.cn"))
        
        response = supabase.auth.reset_password_for_email(
            email,
            {"redirectTo": f"{site_url}/reset-password"}
        )
        
        if response.error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to send reset email: {response.error.message}"
            )
            
        return {"message": "Password reset email sent"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error requesting password reset: {str(e)}"
        )
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)