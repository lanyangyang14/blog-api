# Blog API

[![CI](https://github.com/lanyangyang14/blog-api/actions/workflows/ci.yml/badge.svg)](https://github.com/lanyangyang14/blog-api/actions/workflows/ci.yml)

一个功能完整的博客后端 API，基于 **FastAPI + SQLAlchemy 2.0 + PostgreSQL + Redis**。

## ✨ 功能

- 🔐 **用户认证**：JWT 注册、登录、当前用户
- 📝 **文章管理**：CRUD、分页、搜索、草稿/发布
- 📂 **分类和标签**：多对多关系
- 💬 **评论**：支持嵌套回复、软删除
- 👍 **点赞**：点赞/取消、计数缓存
- 🔍 **查询优化**：预加载、分页、限流
- ⚡ **Redis 缓存**：点赞数缓存
- 🚦 **限流**：防刷
- 📊 **日志**：结构化、可追踪
- 🧪 **测试**：48+ 单元/集成测试，覆盖率 85%+
- 🐳 **Docker 化**：一键部署
- 🔄 **CI/CD**：GitHub Actions

## 🛠️ 技术栈

| 层次 | 技术 |
| :--- | :--- |
| **Web 框架** | FastAPI |
| **ORM** | SQLAlchemy 2.0 |
| **数据库** | PostgreSQL 16 |
| **迁移** | Alembic |
| **缓存** | Redis 7 |
| **认证** | JWT (python-jose) |
| **密码哈希** | pwdlib (Argon2) |
| **配置** | pydantic-settings |
| **日志** | logging + JSON |
| **测试** | pytest + httpx |
| **代码质量** | ruff + mypy + pre-commit |
| **部署** | Docker + docker-compose + Nginx |
| **CI/CD** | GitHub Actions |

## 🏗️ 架构

**分层原则：**
- **API 层**：处理 HTTP 请求/响应
- **Service 层**：业务逻辑、事务
- **Repository 层**：数据访问
- **Model 层**：ORM 定义

## 🚀 快速开始

### 前置要求

- Python 3.11+
- Docker（可选，用于容器化部署）
- PostgreSQL 14+（如果不用 Docker）
- Redis 7+（如果不用 Docker）

### 方式 1：本地开发

```bash
# 1. 克隆
git clone https://github.com/lanyangyang14/blog-api.git
cd blog-api

# 2. 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. 安装依赖
pip install -e ".[dev]"

# 4. 配置
cp .env.example .env
# 编辑 .env，设置 SECRET_KEY

# 5. 启动 PostgreSQL 和 Redis（用 Docker）
docker run -d --name pg -p 5432:5432 \
  -e POSTGRES_USER=bloguser \
  -e POSTGRES_PASSWORD=blogpass \
  -e POSTGRES_DB=blogdb \
  postgres:16-alpine

docker run -d --name redis -p 6379:6379 redis:7-alpine

# 6. 跑迁移
alembic upgrade head

# 7. 启动
uvicorn blog_api.main:app --reloadgit
