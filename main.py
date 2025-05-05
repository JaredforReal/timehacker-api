from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()
app = FastAPI()

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 直接从环境变量获取
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# 数据模型
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

# 认证依赖
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    try:
        user = supabase.auth.get_user(credentials.credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

# API端点
@app.get("/api/")
async def read_root():
    return {"message": "Hello from API"}

@app.get("/todos", response_model=List[TodoResponse])
async def get_todos(user = Depends(get_current_user)):
    response = supabase.table("todos").select("*").eq("user_id", user.user.id).execute()
    return response.data

@app.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoCreate, user = Depends(get_current_user)):
    todo_data = todo.dict()
    todo_data["user_id"] = user.user.id
    response = supabase.table("todos").insert(todo_data).execute()
    return response.data[0]

@app.put("/todos/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: str, todo: TodoUpdate, user = Depends(get_current_user)):
    existing = supabase.table("todos").select("*").eq("id", todo_id).eq("user_id", user.user.id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    response = supabase.table("todos").update(todo.dict(exclude_unset=True)).eq("id", todo_id).execute()
    return response.data[0]

@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: str, user = Depends(get_current_user)):
    existing = supabase.table("todos").select("*").eq("id", todo_id).eq("user_id", user.user.id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    supabase.table("todos").delete().eq("id", todo_id).execute()
    return None

# 健康检查端点
@app.get("/")
async def health_check():
    return {"status": "ok", "message": "Todo API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)