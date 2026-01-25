import sys

from loguru import logger


def setup_logging():
    """
    配置 Loguru 日誌系統。
    包含控制台輸出與檔案儲存，支援日誌輪換、壓縮與 UTF-8 編碼。
    """
    # 移除 Loguru 預設的處理器
    logger.remove()

    # 1. 配置控制台輸出 (Stdout)
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stdout,
        format=log_format,
        level="INFO",
        colorize=True,
    )

    # 2. 配置檔案儲存
    logger.add(
        "logs/lineaihelper_{time:YYYY-MM-DD}.log",
        rotation="500 MB",  # 超過 500MB 換檔
        retention="10 days",  # 保留 10 天
        compression="zip",  # 壓縮舊檔案
        encoding="utf-8",  # 支援中文
        level="INFO",
        enqueue=True,  # 線程安全/非同步寫入
    )

    logger.info("日誌系統初始化完成 (Loguru)")
