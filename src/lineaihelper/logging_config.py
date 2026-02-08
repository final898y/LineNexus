import json
import sys
from typing import Any

from loguru import logger

from lineaihelper.config import settings


def serialize(record: Any) -> str:
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
    if record.get("exception"):
        subset["exception"] = {
            "type": record["exception"].type.__name__,
            "message": str(record["exception"].value),
            "traceback": record["exception"].traceback,
        }
    return json.dumps(subset, ensure_ascii=False)


def setup_logging() -> None:
    """
    配置結構化日誌（包含 INFO / ERROR 分流）
    """

    # ==============================
    # 1. 移除預設 handler
    # ==============================
    # 避免重複輸出 log（很重要）
    logger.remove()

    # ==============================
    # 2. 設定 Console 輸出
    # ==============================
    if settings.LOG_JSON:
        # JSON 格式輸出用的 sink
        def json_sink(msg: Any) -> None:
            sys.stdout.write(serialize(msg.record) + "\n")

        logger.add(
            json_sink,
            level="INFO",  # Console 顯示 INFO 以上
        )

    else:
        # 一般文字格式輸出
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level> "
            "<cyan>{extra[trace_id]}</cyan>"
        )

        logger.add(
            sys.stdout,
            format=log_format,
            level="INFO",
            colorize=True,
        )

    # ==============================
    # 3. INFO 日誌檔案（一般紀錄）
    # ==============================
    logger.add(
        "logs/linenexus_info_{time:YYYY-MM-DD}.log",
        # 檔案滿 200MB 就切新檔
        rotation="200 MB",
        # 保留 7 天
        retention="7 days",
        # 壓縮舊檔
        compression="zip",
        encoding="utf-8",
        # 只收 INFO ~ WARNING
        level="INFO",
        # 非同步寫入（避免卡主程式）
        enqueue=True,
        serialize=True,
        # 過濾 ERROR 以上（避免重複）
        filter=lambda record: record["level"].no < 40,
    )

    # ==============================
    # 4. ERROR 日誌檔案（錯誤專用）
    # ==============================
    logger.add(
        "logs/linenexus_error_{time:YYYY-MM-DD}.log",
        rotation="100 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
        # 只收 ERROR 以上
        level="ERROR",
        enqueue=True,
        serialize=True,
    )

    # ==============================
    # 5. 預設 trace_id
    # ==============================
    logger.configure(extra={"trace_id": "system"})

    logger.info("日誌系統初始化完成（INFO / ERROR 分流）")
