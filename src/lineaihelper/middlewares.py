import uuid
from collections.abc import Callable

from fastapi import Request, Response
from loguru import logger


async def add_trace_id_middleware(request: Request, call_next: Callable) -> Response:
    """
    注入 trace_id / request_id 至 logging context
    """

    # 全鏈路追蹤 ID（優先沿用）
    trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))

    # 單次 request ID（一定新產生）
    request_id = str(uuid.uuid4())

    # 第三方 LINE ID
    line_id = request.headers.get("X-line-request-id", "N/A")

    with logger.contextualize(
        trace_id=trace_id,
        request_id=request_id,
        line_request_id=line_id,
    ):
        logger.info("開始處理請求")

        response: Response = await call_next(request)

        # 回傳 trace_id，讓下游服務接
        response.headers["X-Trace-ID"] = trace_id
        response.headers["X-Request-ID"] = request_id

        return response
