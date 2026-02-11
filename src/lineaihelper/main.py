import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from google import genai
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    ApiException,
    AsyncApiClient,
    AsyncMessagingApi,
    Configuration,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from loguru import logger

from lineaihelper.config import settings
from lineaihelper.context import line_inbound_id_var, request_id_var, trace_id_var
from lineaihelper.dispatcher import CommandDispatcher
from lineaihelper.exception_handlers import (
    business_exception_handler,
    global_exception_handler,
    invalid_signature_handler,
    line_api_exception_handler,
)
from lineaihelper.exceptions import LineNexusError
from lineaihelper.logging_config import setup_logging
from lineaihelper.middlewares import add_trace_id_middleware

# 初始化日誌
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    FastAPI 生命週期管理
    """
    configuration = Configuration(access_token=settings.LINE_CHANNEL_ACCESS_TOKEN)
    async_api_client = AsyncApiClient(configuration)
    app.state.line_bot_api = AsyncMessagingApi(async_api_client)

    gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
    app.state.dispatcher = CommandDispatcher(gemini_client)

    logger.info("LINE 用戶端與指令分發器已初始化")
    yield
    await async_api_client.close()
    logger.info("LINE 非同步用戶端已關閉")


app = FastAPI(lifespan=lifespan)
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)

# 註冊 Middleware
app.middleware("http")(add_trace_id_middleware)

# 註冊 Exception Handlers
app.add_exception_handler(InvalidSignatureError, invalid_signature_handler)
app.add_exception_handler(ApiException, line_api_exception_handler)
app.add_exception_handler(LineNexusError, business_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)


# --- 路由與控制器 (Routes & Controllers) ---


@app.get("/")
def read_root() -> dict:
    return {
        "app": settings.APP_NAME,
        "version": "2.1.0",
        "environment": settings.ENVIRONMENT,
        "status": "up",
    }


@app.get("/health")
def health_check() -> dict:
    """
    健康檢查端點
    """
    return {"status": "healthy", "service": settings.APP_NAME}


@app.post("/callback")
async def callback(request: Request) -> str:
    """
    LINE Webhook 回呼入口
    """
    signature = request.headers.get("x-line-signature")
    if not signature:
        logger.warning("遺失 x-line-signature 標頭")
        raise HTTPException(status_code=400, detail="Missing signature")

    body = await request.body()
    body_str = body.decode("utf-8")
    handler.handle(body_str, signature)
    return "OK"


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event: MessageEvent) -> None:
    """
    處理文字訊息事件
    """
    user_text = event.message.text.strip()
    logger.info(
        "收到使用者訊息",
        extra={
            "user_text": user_text,
            "reply_token": event.reply_token,
        },
    )

    line_bot_api: AsyncMessagingApi = app.state.line_bot_api
    dispatcher: CommandDispatcher = app.state.dispatcher

    # 先擷取目前的 Context 變數，用於傳遞給背景任務
    t_id = trace_id_var.get()
    r_id = request_id_var.get()
    l_in_id = line_inbound_id_var.get()

    async def process_and_reply(
        trace_id: str, request_id: str, line_inbound_id: str
    ) -> None:
        # 在背景任務中重新注入 Context
        with logger.contextualize(
            trace_id=trace_id,
            request_id=request_id,
            line_inbound_id=line_inbound_id,
        ):
            try:
                reply_text = await dispatcher.parse_and_execute(user_text)
                response = await line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=reply_text)],
                    )
                )
                # LINE 回傳的 Request ID（發送回覆的追蹤碼）
                line_outbound_id = response.headers.get("x-line-request-id")
                logger.info(
                    "訊息回覆成功",
                    extra={
                        "line_outbound_id": line_outbound_id,
                        "reply_token": event.reply_token,
                        "user_text": user_text,
                    },
                )

            except ApiException as e:
                # 復用集中管理的處理邏輯 (傳入 None 作為 Request)
                await line_api_exception_handler(None, e)
            except Exception:
                logger.exception(
                    "發送回覆訊息時發生非預期錯誤",
                    extra={
                        "user_text": user_text,
                        "reply_token": event.reply_token,
                    },
                )

    asyncio.create_task(process_and_reply(t_id, r_id, l_in_id))


def start() -> None:
    uvicorn.run(
        "lineaihelper.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
    )


if __name__ == "__main__":
    start()
