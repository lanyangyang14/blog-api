# ============ 构建阶段 ============
FROM python:3.13-slim AS builder

WORKDIR /app

# 装构建工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY pyproject.toml README.md ./
COPY src/ ./src/

# 装依赖到独立目录
RUN pip install --no-cache-dir --user -e .

# ============ 运行阶段 ============
FROM python:3.13-slim

WORKDIR /app

# 创建非 root 用户
RUN useradd -m -u 1000 appuser

# 从构建阶段复制已安装的依赖
COPY --from=builder /root/.local /home/appuser/.local

# 复制源码
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser alembic/ ./alembic/
COPY --chown=appuser:appuser alembic.ini pyproject.toml README.md ./

# 设置 PATH
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER appuser

EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health', timeout=3).raise_for_status()" || exit 1

CMD ["uvicorn", "blog_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
