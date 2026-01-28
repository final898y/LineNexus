import asyncio
from contextlib import asynccontextmanager

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
from lineaihelper.logging_config import setup_logging

# 初始化日誌
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 生命週期管理：在啟動時初始化非同步用戶端與分發器，關閉時釋放資源。
    """
    # 啟動時初始化 LINE Client
    configuration = Configuration(access_token=settings.LINE_CHANNEL_ACCESS_TOKEN)
    async_api_client = AsyncApiClient(configuration)
    app.state.line_bot_api = AsyncMessagingApi(async_api_client)

    # 初始化 Gemini Client 與 Dispatcher
    gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
    app.state.dispatcher = CommandDispatcher(gemini_client)

    logger.info("LINE 用戶端與指令分發器已初始化")

    yield

    # 關閉時釋放
    await async_api_client.close()
    logger.info("LINE 非同步用戶端已關閉")


# 建立 FastAPI 應用程式實例，並注入 lifespan
app = FastAPI(lifespan=lifespan)

# WebhookHandler 仍然使用同步方式解析簽章
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)


@app.exception_handler(InvalidSignatureError)
async def invalid_signature_handler(request: Request, exc: InvalidSignatureError):
    logger.error("無效的 LINE 簽章")
    return HTTPException(status_code=400, detail="Invalid signature")


@app.get("/")
def read_root():
    logger.info("收到首頁健康檢查請求")
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

    try:
        handler.handle(body_str, signature)
    except InvalidSignatureError:
        raise
    except Exception as e:
        logger.exception(f"處理 Webhook 時發生錯誤: {e}")
        raise HTTPException(status_code=500, detail="Internal Error") from e

    return "OK"


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event: MessageEvent):
    """
    處理文字訊息事件 (透過 Dispatcher)
    """
    user_text = event.message.text.strip()
    logger.info(f"收到訊息: {user_text}")

    # 從 app.state 取得全域物件
    line_bot_api: AsyncMessagingApi = app.state.line_bot_api
    dispatcher: CommandDispatcher = app.state.dispatcher

    async def process_and_reply():
        try:
            # 委託給 Dispatcher 處理邏輯
            reply_text = await dispatcher.parse_and_execute(user_text)

            # 發送回覆
            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_text)],
                )
            )
        except Exception as e:
            logger.error(f"處理訊息時發生錯誤: {e}")
            try:
                await line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="系統發生錯誤，請稍後再試。")],
                    )
                )
            except Exception:
                pass

    # 將任務丟入當前的事件迴圈中執行
    asyncio.create_task(process_and_reply())


def start():
    """啟動函式"""
    logger.info(f"LineNexus 正在啟動於 {settings.APP_HOST}:{settings.APP_PORT} (Debug: {settings.DEBUG})...")
    uvicorn.run(
        "lineaihelper.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG
    )


if __name__ == "__main__":
    start()
