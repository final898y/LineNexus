import uuid
from collections.abc import Callable

from fastapi import Request, Response
from loguru import logger


async def add_trace_id_middleware(request: Request, call_next: Callable) -> Response:
    """
    為每個請求生成 Trace ID 並注入日誌上下文。
    """
    request_id = request.headers.get("X-linenexus-request-ID", str(uuid.uuid4()))
    line_id = request.headers.get("x-line-request-id", "N/A")
    with logger.contextualize(trace_id=request_id, line_request_id=line_id):
        logger.info("開始處理請求")
        response: Response = await call_next(request)
        response.headers["X-linenexus-request-ID"] = request_id
        return response
