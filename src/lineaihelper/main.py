import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
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
from lineaihelper.logging_config import setup_logging

# 初始化日誌
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 生命週期管理：在啟動時初始化非同步用戶端與分發器，關閉時釋放資源。
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


# --- 異常處理層 (Exception Handling Layer) ---

@app.exception_handler(InvalidSignatureError)
async def invalid_signature_handler(request: Request, exc: InvalidSignatureError):
    logger.error("無效的 LINE 簽章")
    return JSONResponse(status_code=400, content={"detail": "Invalid signature"})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全域異常攔截，作為最後一道防線"""
    logger.exception(f"全域攔截到未處理異常: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )


# --- 路由與控制器 (Routes & Controllers) ---

@app.get("/")
def read_root():
    return {"status": "ok", "message": "LineNexus (Async) is running."}


@app.post("/callback")
async def callback(request: Request):
    """
    LINE Webhook 回呼入口
    """
    signature = request.headers.get("X-Line-Signature")
    if not signature:
        logger.warning("遺失 X-Line-Signature 標頭")
        raise HTTPException(status_code=400, detail="Missing signature")

    body = await request.body()
    body_str = body.decode("utf-8")

    # 若 handle 噴錯，會自動由全域 exception_handler 捕捉
    handler.handle(body_str, signature)

    return "OK"


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event: MessageEvent):
    """
    處理文字訊息事件 (透過 Dispatcher)
    """
    user_text = event.message.text.strip()
    logger.info(f"收到訊息: {user_text}")

    line_bot_api: AsyncMessagingApi = app.state.line_bot_api
    dispatcher: CommandDispatcher = app.state.dispatcher

    async def process_and_reply():
        try:
            # Dispatcher 內部已具備完整的業務異常攔截 (⚠️/❌)
            reply_text = await dispatcher.parse_and_execute(user_text)

            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_text)],
                )
            )
        except Exception as e:
            # 這裡的錯誤通常是 LINE API 通訊失敗 (例如 reply_token 過期)
            logger.error(f"發送回覆訊息失敗: {e}")

    asyncio.create_task(process_and_reply())


def start():
    uvicorn.run(
        "lineaihelper.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
    )


if __name__ == "__main__":
    start()