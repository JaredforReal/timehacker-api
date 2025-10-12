# TimeHacker API 重构项目

一个现代化的时间管理 API 服务，基于 FastAPI 构建，支持 Todo 管理和番茄钟计时功能。

## 项目完成度与规划

- **当前完成度**: FastAPI 服务已实现 `todos`、`pomodoro`、`profile`、`auth` 等核心路由，结合 Supabase 完成数据访问与认证；依赖注入、分层架构、覆盖各层的 Pytest 单元测试及 pre-commit 流程均已落地，可支撑基础的番茄钟与待办协同能力。
- **已知缺口**: 缺少注册、刷新令牌等认证扩展能力，数据库 Schema 管理依赖 Supabase 控制台而非代码迁移，日志与可观测性只保留了 `print` 调试信息，异步任务与限流策略尚未实现。
- **建议迭代**:

1. 引入 Alembic 或 Supabase migration CLI 管理数据库版本，补充 Seed 数据与本地模拟。
2. 扩展 `AuthService` 支持注册、Refresh Token、角色/权限控制，并为密码重置邮件引入异步队列。
3. 增加结构化日志、Prometheus/OTel 监控与告警，结合 docker-compose 提供一键启动的整体验证环境。
4. 对 Todos/Pomodoro 添加审计字段与乐观锁，避免并发覆盖，同时补充端到端测试覆盖。

## 快速开始

### 环境要求

- Python 3.11+
- Supabase 项目
- Docker (可选，用于部署)

### 本地开发

1. **克隆项目**

```bash
git clone https://github.com/JaredforReal/timehacker-api.git
cd timehacker-api/backend
```

2. **安装依赖**

```bash
# 安装开发环境依赖（包含所有工具）
pip install -r requirements/dev.txt

# 或只安装生产依赖
pip install -r requirements/prod.txt
```

3. **配置环境变量**

```bash
cp .env.example .env
# 编辑 .env 文件，配置Supabase连接信息
```

4. **启动开发服务器**

```bash
uvicorn main:app --reload
```

访问 http://localhost:8000/docs 查看 API 文档

### 生产部署

项目支持 Docker 容器化部署，详细部署指南请参考 [DEPLOYMENT.md](DEPLOYMENT.md)

**快速部署命令**：

```bash
chmod +x scripts/*.sh
./scripts/deploy.sh
```

## 项目架构

本项目采用现代化的 FastAPI 架构设计，遵循分层架构和依赖注入原则。

```
backend/
├── app/
│   ├── core/              # 核心组件
│   │   ├── config.py      # 配置管理（Pydantic BaseSettings）
│   │   ├── security.py    # 安全模块（JWT/OAuth2）
│   │   └── middleware.py  # 自定义中间件
│   │
│   ├── api/               # API端点
│   │   └── v1/            # API版本控制
│   │       ├── endpoints/ # 路由端点
│   │       │   ├── auth.py      # 认证相关端点
│   │       │   ├── todos.py     # Todo管理端点
│   │       │   ├── pomodoro.py  # 番茄钟端点
│   │       │   └── profile.py   # 个人资料端点
│   │       └── api.py     # 路由聚合
│   │
│   ├── services/          # 业务逻辑层
│   │   ├── auth_service.py     # 认证服务
│   │   ├── todo_service.py     # Todo业务逻辑
│   │   ├── pomodoro_service.py # 番茄钟业务逻辑
│   │   └── profile_service.py  # 个人资料业务逻辑
│   │
│   ├── models/            # 数据模型
│   │   ├── schemas.py     # Pydantic模型
│   │   └── database.py    # 数据库客户端
│   │
│   ├── dependencies.py    # 全局依赖注入
│   ├── utils/             # 工具函数
│   └── main.py            # 应用入口
│
├── tests/                 # 测试套件
├── requirements/          # 分环境依赖管理
│   ├── dev.txt           # 开发环境依赖（包含代码质量工具）
│   └── prod.txt          # 生产环境依赖
├── scripts/               # 自动化脚本
│   ├── check_quality.sh  # 代码质量检查
│   ├── fix_code.sh       # 代码格式修复
│   └── deploy.sh         # 部署脚本
├── main.py                # 启动入口
└── .env.example           # 环境变量模板
```

## 架构特点

### 1. 分层架构

- **API 层**: 处理 HTTP 请求和响应
- **服务层**: 包含业务逻辑
- **数据层**: 数据库操作和数据模型

### 2. 依赖注入

- 统一的依赖管理
- 便于测试和模块替换
- 清晰的组件边界

### 3. 配置管理

- 使用 Pydantic 进行配置验证
- 环境变量自动映射
- 类型安全的配置

### 4. 安全模块

- 统一的认证处理
- JWT 令牌验证
- 用户权限管理

## 技术栈

- **FastAPI**: 现代 Python Web 框架
- **Pydantic**: 数据验证和设置管理
- **Supabase**: 后端即服务平台
- **Uvicorn**: ASGI 服务器
- **Docker**: 容器化部署
- **Nginx**: 反向代理和负载均衡

## 开发工具

### 代码质量

- **Black**: 代码格式化
- **isort**: 导入排序
- **Ruff**: 现代化代码检查
- **Flake8**: 传统代码检查
- **Mypy**: 类型检查
- **Bandit**: 安全扫描
- **Pre-commit**: Git 提交钩子

### 测试工具

- **Pytest**: 测试框架
- **Coverage**: 测试覆盖率

### 质量检查命令

```bash
# 检查代码质量
./scripts/check_quality.sh

# 自动修复格式问题
./scripts/fix_code.sh

# 运行测试
pytest tests/ -v --cov=app

# 安装Git钩子
pre-commit install
```

## 运行项目

### 开发环境

```bash
# 安装开发依赖（包含所有工具）
pip install -r requirements/dev.txt

# 启动开发服务器
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 生产环境

```bash
# 安装生产依赖
pip install -r requirements/prod.txt

# 使用Gunicorn启动
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker 部署

```bash
# 构建镜像
docker build -t timehacker-api .

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

## API 端点

API 访问地址：`https://api.my-domain.com`

### 认证相关

- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/reset-password` - 密码重置
- `POST /api/v1/auth/logout` - 用户登出

### Todo 管理

- `GET /api/v1/todos` - 获取 Todo 列表
- `POST /api/v1/todos` - 创建 Todo
- `PUT /api/v1/todos/{id}` - 更新 Todo
- `DELETE /api/v1/todos/{id}` - 删除 Todo
- `PATCH /api/v1/todos/{id}/complete` - 标记完成

### 番茄钟管理

- `POST /api/v1/pomodoro/sessions` - 开始番茄钟会话
- `GET /api/v1/pomodoro/sessions` - 获取会话历史
- `PATCH /api/v1/pomodoro/sessions/{id}/complete` - 完成会话
- `GET /api/v1/pomodoro/settings` - 获取番茄钟设置
- `PUT /api/v1/pomodoro/settings` - 更新设置

### 个人资料

- `GET /api/v1/profile` - 获取个人资料
- `PUT /api/v1/profile` - 更新个人资料
- `POST /api/v1/profile/avatar` - 上传头像

### 系统信息

- `GET /health` - 健康检查
- `GET /docs` - API 文档 (Swagger)
- `GET /redoc` - API 文档 (ReDoc)

## 环境配置

### 环境变量

```env
# 应用配置
ENVIRONMENT=development  # development/production
DEBUG=true
SECRET_KEY=your_super_secret_key_here

# Supabase配置
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# 域名配置
API_DOMAIN=api.my-domain.com
FRONTEND_DOMAIN=my-domain.com
ALLOWED_ORIGINS=https://my-domain.com,https://www.my-domain.com

# CORS配置
CORS_ALLOWED_ORIGINS=["https://my-domain.com", "https://www.my-domain.com"]
```

## 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行带覆盖率的测试
pytest tests/ -v --cov=app --cov-report=html

# 运行特定测试文件
pytest tests/test_auth.py -v

# 运行特定测试
pytest tests/test_auth.py::test_user_login -v
```

## 部署

详细的生产环境部署指南请参考 [DEPLOYMENT.md](DEPLOYMENT.md)

### 域名架构

- **前端**: `https://my-domain.com` 和 `https://www.my-domain.com`
- **API**: `https://api.my-domain.com`

### 快速部署

```bash
# 克隆项目到服务器
git clone https://github.com/JaredforReal/timehacker-api.git
cd timehacker-api/backend

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 运行部署脚本
chmod +x scripts/*.sh
./scripts/deploy.sh
```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- 遵循 PEP 8 代码风格
- 使用 Black 进行代码格式化
- 添加适当的类型注解
- 编写测试用例
- 提交前运行 `./scripts/check_quality.sh`

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- 项目地址: [https://github.com/JaredforReal/timehacker-api](https://github.com/JaredforReal/timehacker-api)
- 问题反馈: [Issues](https://github.com/JaredforReal/timehacker-api/issues)
