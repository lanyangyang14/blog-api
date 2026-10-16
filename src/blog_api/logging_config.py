"""日志配置。"""

import json
import logging
import logging.config
from contextvars import ContextVar
from datetime import datetime
from pathlib import Path
from typing import Any

from blog_api.config import settings

# 全局 trace_id（用 ContextVar 保证线程/协程隔离）
trace_id_var: ContextVar[str] = ContextVar("trace_id", default="-")


def get_trace_id() -> str:
    return trace_id_var.get()


def set_trace_id(trace_id: str) -> None:
    trace_id_var.set(trace_id)


class TraceIdFilter(logging.Filter):
    """给日志记录注入 trace_id。"""

    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = get_trace_id()
        return True


class JsonFormatter(logging.Formatter):
    """JSON 格式化器。"""

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "time": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
            "function": record.funcName,
            "trace_id": getattr(record, "trace_id", "-"),
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data, ensure_ascii=False, default=str)


class ConsoleFormatter(logging.Formatter):
    """控制台格式化器，带颜色。"""

    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[35m",
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, "")
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging() -> None:
    """配置日志。"""

    handlers: dict[str, Any] = {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG" if settings.is_development else "INFO",
            "formatter": "console",
            "stream": "ext://sys.stdout",
            "filters": ["trace_id"],
        },
    }

    logger_handlers = ["console"]

    if settings.is_development:
        log_dir = Path(settings.log_dir)
        log_dir.mkdir(exist_ok=True)

        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "json",
            "filters": ["trace_id"],
            "filename": str(log_dir / "app.log"),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8",
        }
        handlers["error_file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "json",
            "filters": ["trace_id"],
            "filename": str(log_dir / "error.log"),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8",
        }
        logger_handlers = ["console", "file", "error_file"]

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "trace_id": {
                "()": "blog_api.logging_config.TraceIdFilter",
            },
        },
        "formatters": {
            "console": {
                "()": "blog_api.logging_config.ConsoleFormatter",
                "format": "%(asctime)s | %(levelname)s | [%(trace_id)s] | %(name)s | %(message)s",
                "datefmt": "%H:%M:%S",
            },
            "json": {
                "()": "blog_api.logging_config.JsonFormatter",
            },
        },
        "handlers": handlers,
        "loggers": {
            "blog_api": {
                "level": settings.log_level,
                "handlers": logger_handlers,
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "WARNING",  # 屏蔽 access 日志
                "handlers": ["console"],
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
        },
        "root": {
            "level": "WARNING",
            "handlers": ["console"],
        },
    }

    logging.config.dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    """获取 logger。"""
    return logging.getLogger(name)
