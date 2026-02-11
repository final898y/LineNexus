from contextvars import ContextVar

# 定義全局追蹤 Context
trace_id_var: ContextVar[str] = ContextVar("trace_id", default="system")
request_id_var: ContextVar[str] = ContextVar("request_id", default="system")
line_inbound_id_var: ContextVar[str] = ContextVar("line_inbound_id", default="N/A")
