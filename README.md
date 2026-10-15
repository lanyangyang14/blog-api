# Blog API


![CI](https://github.com/sanjing/blog-api/actions/workflows/ci.yml/badge.svg)
![Coverage](https://codecov.io/gh/sanjing/blog-api/branch/main/graph/badge.svg)

A blog API built with FastAPI, SQLAlchemy 2.0, and PostgreSQL/SQLite.
A blog API built with FastAPI, SQLAlchemy 2.0, and PostgreSQL/SQLite.

## 功能

- 用户注册/登录（JWT）
- 文章 CRUD（Markdown）
- 分类、标签
- 评论（支持嵌套）
- 点赞
- 搜索
- 分页、排序、过滤

## 技术栈

- FastAPI
- SQLAlchemy 2.0
- Alembic
- Pydantic v2
- pytest
- Docker

## 快速开始

### 1. 克隆项目

\`\`\`bash
git clone <your-repo-url>
cd blog-api
\`\`\`

### 2. 创建虚拟环境

\`\`\`bash
python -m venv .venv
.venv\Scripts\activate   # Windows
\`\`\`

### 3. 安装依赖

\`\`\`bash
pip install -e ".[dev]"
\`\`\`

### 4. 配置环境

\`\`\`bash
cp .env.example .env
# 编辑 .env，设置 SECRET_KEY
\`\`\`

### 5. 初始化数据库

\`\`\`bash
alembic upgrade head
\`\`\`

### 6. 启动服务

\`\`\`bash
uvicorn blog_api.main:app --reload
\`\`\`

访问 http://localhost:8000/docs

## 开发

### 代码格式化

\`\`\`bash
ruff format .
ruff check --fix .
\`\`\`

### 类型检查

\`\`\`bash
mypy src/
\`\`\`

### 测试

\`\`\`bash
pytest
pytest --cov=src
\`\`\`

## License

MIT

## Docker 部署

### 本地运行

\`\`\`bash
# 设置 SECRET_KEY
export SECRET_KEY="your-secret-key-at-least-32-chars"

# 启动
docker compose up -d --build

# 跑迁移
docker compose run --rm migrate

# 访问
# http://localhost:8000/docs
\`\`\`

### 停止

\`\`\`bash
docker compose down
\`\`\`

### 查看日志

\`\`\`bash
docker compose logs -f app
\`\`\`
