from fastapi import Request
from fastapi.responses import JSONResponse
from linebot.v3.exceptions import InvalidSignatureError
from loguru import logger


async def invalid_signature_handler(
    request: Request, exc: InvalidSignatureError
) -> JSONResponse:
    """處理 LINE Webhook 簽章無效錯誤"""
    logger.error("無效的 LINE 簽章")
    return JSONResponse(status_code=400, content={"detail": "Invalid signature"})


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全域異常攔截，作為最後一道防線"""
    logger.exception(f"全域攔截到未處理異常: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
