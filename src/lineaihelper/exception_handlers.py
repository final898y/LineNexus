from fastapi import Request
from fastapi.responses import JSONResponse
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import ApiException, ErrorResponse
from loguru import logger

from lineaihelper.exceptions import LineNexusError


async def invalid_signature_handler(
    request: Request, exc: InvalidSignatureError
) -> JSONResponse:
    """處理 LINE Webhook 簽章無效錯誤"""
    logger.error("無效的 LINE 簽章", extra={"error": str(exc)})
    return JSONResponse(status_code=400, content={"detail": "Invalid signature"})


async def line_api_exception_handler(
    request: Request | None, exc: ApiException
) -> JSONResponse:
    """處理 LINE Messaging API 的通訊異常"""

    request_id = exc.headers.get("x-line-request-id") if exc.headers else "N/A"

    error_body = ErrorResponse.from_json(exc.body) if exc.body else "No body"

    logger.error(
        "LINE API 異常",
        extra={
            "status": exc.status,
            "request_id": request_id,
            "body": error_body,
        },
    )

    return JSONResponse(
        status_code=502,
        content={
            "detail": "LINE API communication error",
            "request_id": request_id,
        },
    )


async def business_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """處理專案自定義的業務邏輯異常"""
    if not isinstance(exc, LineNexusError):
        # 正常不應進入此分支，因為已針對 LineNexusError 註冊
        return await global_exception_handler(request, exc)

    # 在 Log 中記錄詳細資訊，方便追蹤
    logger.warning(
        "業務邏輯異常",
        extra={
            "type": exc.__class__.__name__,
            "message": exc.message,
            "original_reason": str(exc.original_exception),
        },
    )
    # 僅回傳對用戶有意義的訊息
    return JSONResponse(
        status_code=400,
        content={
            "detail": exc.message,
        },
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全域異常攔截，作為最後一道防線"""
    logger.exception("全域攔截到未處理異常", extra={"error": str(exc)})
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
