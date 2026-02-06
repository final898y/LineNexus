import uuid
from collections.abc import Callable

from fastapi import Request, Response
from loguru import logger


async def add_trace_id_middleware(request: Request, call_next: Callable) -> Response:
    """
    為每個請求生成 Trace ID 並注入日誌上下文。
    """
    trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
    with logger.contextualize(trace_id=trace_id):
        response: Response = await call_next(request)
        response.headers["X-Trace-ID"] = trace_id
        return response
