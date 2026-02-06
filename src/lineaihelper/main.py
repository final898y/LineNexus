import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from google import genai
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    AsyncApiClient,
    AsyncMessagingApi,
    Configuration,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from loguru import logger

from lineaihelper.config import settings
from lineaihelper.dispatcher import CommandDispatcher
from lineaihelper.exception_handlers import (
    global_exception_handler,
    invalid_signature_handler,
)
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
    signature = request.headers.get("X-Line-Signature")
    if not signature:
        logger.warning("遺失 X-Line-Signature 標頭")
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
    logger.info(f"收到訊息: {user_text}")

    line_bot_api: AsyncMessagingApi = app.state.line_bot_api
    dispatcher: CommandDispatcher = app.state.dispatcher

    async def process_and_reply() -> None:
        try:
            reply_text = await dispatcher.parse_and_execute(user_text)
            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_text)],
                )
            )
        except Exception as e:
            logger.error(f"發送回覆訊息失敗: {e}")

    asyncio.create_task(process_and_reply())


def start() -> None:
    uvicorn.run(
        "lineaihelper.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
    )


if __name__ == "__main__":
    start()
