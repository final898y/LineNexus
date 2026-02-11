import uuid
from collections.abc import Callable

from fastapi import Request, Response
from loguru import logger

from lineaihelper.context import line_inbound_id_var, request_id_var, trace_id_var


async def add_trace_id_middleware(request: Request, call_next: Callable) -> Response:
    """
    注入 trace_id / request_id 至 logging context。
    使用全小寫 Header 名稱符合 HTTP/2 規範。
    """

    # 1. 全鏈路追蹤 ID (優先從標頭獲取)
    trace_id = request.headers.get("x-trace-id", str(uuid.uuid4()))

    # 2. 單次請求 ID (本次服務生成的唯一識別碼)
    request_id = str(uuid.uuid4())

    # 3. LINE 原始請求 ID (從 LINE Webhook 進來的)
    line_inbound_id = request.headers.get("x-line-request-id", "N/A")

    # 設定 ContextVar (用於跨非同步任務傳遞)
    t_token = trace_id_var.set(trace_id)
    r_token = request_id_var.set(request_id)
    l_token = line_inbound_id_var.set(line_inbound_id)

    with logger.contextualize(
        trace_id=trace_id,
        request_id=request_id,
        line_inbound_id=line_inbound_id,
    ):
        logger.info(
            "開始處理請求",
            extra={
                "method": request.method,
                "path": request.url.path,
            },
        )

        try:
            response: Response = await call_next(request)

            # 回傳追蹤 ID 供客戶端或下游服務使用
            response.headers["x-trace-id"] = trace_id
            response.headers["x-request-id"] = request_id

            return response
        finally:
            # 清理 ContextVar (雖然 ContextVar 是 task-local，但仍建議養成好習慣)
            trace_id_var.reset(t_token)
            request_id_var.reset(r_token)
            line_inbound_id_var.reset(l_token)
