"""Prometheus 指标。"""

from prometheus_client import Counter, Gauge, Histogram

# ============ HTTP 指标（由 instrumentator 自动生成） ============

# ============ 业务指标 ============

user_registrations_total = Counter(
    "user_registrations_total",
    "用户注册总数",
)

user_logins_total = Counter(
    "user_logins_total",
    "用户登录总数",
    ["status"],  # status: success / failure
)

posts_created_total = Counter(
    "posts_created_total",
    "文章创建总数",
    ["status"],  # status: draft / published / archived
)

comments_created_total = Counter(
    "comments_created_total",
    "评论创建总数",
)

likes_total = Counter(
    "likes_total",
    "点赞总数",
    ["action"],  # action: like / unlike
)

cache_hits_total = Counter(
    "cache_hits_total",
    "缓存命中总数",
    ["key_prefix"],
)

cache_misses_total = Counter(
    "cache_misses_total",
    "缓存未命中总数",
    ["key_prefix"],
)

# ============ 数据库指标 ============

db_queries_total = Counter(
    "db_queries_total",
    "数据库查询总数",
)

db_query_duration_seconds = Histogram(
    "db_query_duration_seconds",
    "数据库查询耗时",
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0],
)

# ============ 队列指标 ============

celery_tasks_total = Counter(
    "celery_tasks_total",
    "Celery 任务总数",
    ["task_name", "status"],  # status: success / failure
)

active_workers = Gauge(
    "active_workers",
    "活跃 Worker 数",
)
