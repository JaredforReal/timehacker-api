from dotenv import load_dotenv
from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.middleware import setup_cors
from app.models.schemas import HealthResponse, MessageResponse

# 加载环境变量
load_dotenv()

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

# 设置中间件
setup_cors(app)

# 注册路由
app.include_router(api_router)


@app.get("/", response_model=HealthResponse)
async def health_check():
    """
    健康检查端点
    """
    return HealthResponse(
        status="ok", message="TimeHacker API is running", version=settings.app_version
    )


@app.get("/api/", response_model=MessageResponse)
async def read_root():
    """
    API根端点
    """
    return MessageResponse(message="Hello from TimeHacker API")
