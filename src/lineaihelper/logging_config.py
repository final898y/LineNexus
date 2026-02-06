import json
import sys
from typing import Any, Dict

from loguru import logger

from lineaihelper.config import settings


def serialize(record: Dict[str, Any]) -> str:
    """
    將 Loguru 紀錄序列化為自定義 JSON 格式。
    """
    subset = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["name"],
        "function": record["function"],
        "line": record["line"],
        "extra": record["extra"],
    }
    if record["exception"]:
        subset["exception"] = str(record["exception"])
    return json.dumps(subset, ensure_ascii=False)


def setup_logging() -> None:
    """
    配置結構化日誌。
    """
    # 移除 Loguru 預設的處理器
    logger.remove()

    # 1. 配置控制台輸出 (Stdout)
    if settings.LOG_JSON:
        # 使用自定義 sink 函數直接輸出 JSON，避免 Loguru 再次解析大括號
        logger.add(
            lambda msg: sys.stdout.write(serialize(msg.record) + "\n"),
            level="INFO",
        )
    else:
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level> "
            " <cyan>{extra[trace_id]}</cyan>"
        )
        logger.add(
            sys.stdout,
            format=log_format,
            level="INFO",
            colorize=True,
        )

    # 2. 配置檔案儲存 (始終使用 JSON 格式以便後續分析)
    logger.add(
        "logs/lineaihelper_{time:YYYY-MM-DD}.log",
        rotation="500 MB",
        retention="10 days",
        compression="zip",
        encoding="utf-8",
        level="INFO",
        enqueue=True,
        serialize=True,  # 使用 Loguru 內建的序列化
    )

    logger.configure(extra={"trace_id": "system"})
    logger.info("日誌系統初始化完成 (Loguru)")