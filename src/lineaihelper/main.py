import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request
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
from lineaihelper.logging_config import setup_logging

# 初始化日誌
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 生命週期管理：在啟動時初始化非同步用戶端，關閉時釋放資源。
    """
    # 啟動時初始化
    configuration = Configuration(access_token=settings.LINE_CHANNEL_ACCESS_TOKEN)
    async_api_client = AsyncApiClient(configuration)
    app.state.line_bot_api = AsyncMessagingApi(async_api_client)
    logger.info("LINE 非同步用戶端已初始化")

    yield

    # 關閉時釋放
    await async_api_client.close()
    logger.info("LINE 非同步用戶端已關閉")


# 建立 FastAPI 應用程式實例，並注入 lifespan
app = FastAPI(lifespan=lifespan)

# WebhookHandler 仍然使用同步方式解析簽章
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)


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
        # handler.handle 是同步解析，但它觸發的 handle_message 會非同步執行回覆
        handler.handle(body_str, signature)
    except InvalidSignatureError as e:
        logger.error("無效的 LINE 簽章")
        raise HTTPException(status_code=400, detail="Invalid signature") from e
    except Exception as e:
        logger.exception(f"處理 Webhook 時發生錯誤: {e}")
        raise HTTPException(status_code=500, detail="Internal Error") from e

    return "OK"


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event: MessageEvent):
    """
    處理文字訊息事件 (Simple Command Dispatcher)
    """
    user_text = event.message.text.strip()
    logger.info(f"收到訊息: {user_text}")

    # 從 app.state 取得全域的非同步 API 物件
    line_bot_api: AsyncMessagingApi = app.state.line_bot_api

    # 簡易指令解析 (1.2)
    reply_text = ""
    if user_text.startswith("/"):
        parts = user_text.split(" ", 1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if command == "/stock":
            if not args:
                reply_text = "請提供股票代碼，例如：/stock 2330"
            else:
                reply_text = f"收到股票分析指令，代碼：{args} (功能開發中)"
        elif command == "/chat":
            if not args:
                reply_text = "請輸入聊天內容，例如：/chat 你好"
            else:
                reply_text = f"收到 AI 聊天指令：{args} (功能開發中)"
        elif command == "/help":
            reply_text = (
                "【LineNexus 指令列表】\n"
                "/stock [代碼] - 查詢股票資訊\n"
                "/chat [內容] - 與 AI 對話\n"
                "/help - 顯示此說明"
            )
        else:
            reply_text = f"未知指令：{command}，請輸入 /help 查看說明。"
    else:
        # 非指令文字：目前維持 Echo
        reply_text = f"LineNexus (Async) 收到：{user_text}"

    # 定義一個非同步任務來發送回覆
    async def send_reply():
        try:
            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_text)],
                )
            )
        except Exception as e:
            logger.error(f"非同步回覆失敗: {e}")

    # 將任務丟入當前的事件迴圈中執行
    asyncio.create_task(send_reply())


def start():
    """啟動函式"""
    logger.info("LineNexus 正在啟動...")
    uvicorn.run("lineaihelper.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    start()
