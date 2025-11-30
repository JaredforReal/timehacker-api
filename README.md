# TimeHacker API

一个现代化的时间管理 API 服务，基于 FastAPI 构建，支持 Todo 管理、日历排程和番茄钟计时功能。

## 项目完成度与规划

- **当前完成度**: FastAPI 服务已实现完整的 `todos`（含日历排程）、`pomodoro`、`profile`、`auth` 等核心路由；采用自建 PostgreSQL + SQLAlchemy 2.0 异步 ORM，自建 JWT 认证（Access Token + Refresh Token），头像存储使用腾讯云 COS；依赖注入、分层架构、Pytest 单元测试及 pre-commit 流程均已落地。
- **已知缺口**: 邮箱验证/密码重置暂无邮件发送实现（需接入 SMTP 服务），日志与可观测性只保留了 print 调试信息，异步任务与限流策略尚未实现。
- **建议迭代**:
  1. 接入 SMTP 服务完成邮件验证与密码重置邮件发送
  2. 增加结构化日志、Prometheus/OTel 监控与告警
  3. 对 Todos/Pomodoro 添加审计字段与乐观锁，避免并发覆盖
  4. 补充端到端测试覆盖

## 技术栈

- **FastAPI**: 现代 Python Web 框架
- **SQLAlchemy 2.0**: 异步 ORM（asyncpg 驱动）
- **PostgreSQL 16**: 关系型数据库
- **JWT**: 自建认证（python-jose + passlib）
- **腾讯云 COS**: 头像文件存储
- **Docker**: 容器化部署
- **Nginx**: 反向代理

## 快速开始

### 环境要求

- Python 3.11+
- PostgreSQL 16+ (或使用 Docker)
- Docker & Docker Compose (推荐)

### 使用 Docker Compose 启动

```bash
# 克隆项目
git clone https://github.com/JaredforReal/timehacker-api.git
cd timehacker-api/backend

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库密码、JWT 密钥、COS 密钥等

# 启动服务（包含 PostgreSQL + API + Nginx）
docker-compose up -d

# 查看日志
docker-compose logs -f api
```

### 本地开发

```bash
# 安装依赖
pip install -r requirements/dev.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，设置 DATABASE_URL 指向本地 PostgreSQL

# 启动开发服务器
uvicorn main:app --reload
```

访问 http://localhost:8000/docs 查看 API 文档

## 项目架构

```
backend/
├── app/
│   ├── core/              # 核心组件
│   │   ├── config.py      # 配置管理（PostgreSQL/JWT/COS）
│   │   ├── security.py    # JWT认证、密码哈希
│   │   └── middleware.py  # 自定义中间件
│   │
│   ├── api/v1/            # API端点
│   │   └── endpoints/     # 路由端点
│   │       ├── auth.py    # 认证（登录/注册/刷新/登出）
│   │       ├── todos.py   # Todo管理（含日历排程）
│   │       ├── pomodoro.py# 番茄钟
│   │       └── profile.py # 个人资料
│   │
│   ├── services/          # 业务逻辑层
│   ├── models/
│   │   ├── orm.py         # SQLAlchemy ORM 模型
│   │   ├── schemas.py     # Pydantic 请求/响应模型
│   │   └── database.py    # 数据库连接管理
│   │
│   └── dependencies.py    # 全局依赖注入
│
├── init-db/               # 数据库初始化脚本
│   └── 01-init.sql        # 建表SQL
├── tests/                 # 测试套件
├── requirements/          # 依赖管理
├── docker-compose.yml     # Docker编排
└── .env.example           # 环境变量模板
```

## API 端点

### 认证相关

- `POST /register` - 用户注册
- `POST /token` - 用户登录（返回 access_token + refresh_token）
- `POST /refresh` - 刷新访问令牌
- `POST /logout` - 用户登出（撤销刷新令牌）
- `POST /forgot-password` - 请求密码重置
- `POST /reset-password` - 确认密码重置

### Todo 管理（含日历排程）

- `GET /todos` - 获取待办列表
- `POST /todos` - 创建待办（支持 start_at, end_at, all_day, color）
- `PUT /todos/{id}` - 更新待办
- `DELETE /todos/{id}` - 删除待办

### 番茄钟管理

- `POST /pomodoro/sessions` - 创建番茄钟会话
- `GET /pomodoro/sessions` - 获取会话历史
- `GET /pomodoro/settings` - 获取番茄钟设置
- `PUT /pomodoro/settings` - 更新设置

### 个人资料

- `GET /profile` - 获取个人资料
- `PUT /profile` - 更新个人资料
- `POST /profile/avatar` - 上传头像（腾讯云 COS）

## 环境配置

```env
# 应用配置
ENVIRONMENT=production
DEBUG=false

# 数据库配置
DATABASE_URL=postgresql+asyncpg://timehacker:password@postgres:5432/timehacker
POSTGRES_PASSWORD=your_secure_password

# JWT 配置
JWT_SECRET_KEY=your-super-secret-jwt-key  # 使用 python -c "import secrets; print(secrets.token_urlsafe(32))" 生成
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# 腾讯云 COS 配置
COS_SECRET_ID=your-cos-secret-id
COS_SECRET_KEY=your-cos-secret-key
COS_BUCKET=your-bucket-name-1234567890
COS_REGION=ap-guangzhou

# CORS配置
CORS_ALLOWED_ORIGINS=["https://your-domain.com"]
```

## 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行带覆盖率的测试
pytest tests/ -v --cov=app --cov-report=html
```

## 许可证

MIT License
