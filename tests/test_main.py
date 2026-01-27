from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from linebot.v3.webhooks import MessageEvent, TextMessageContent

from lineaihelper.main import app, handle_message


def test_read_root(client):
    """測試根路徑 / 健康檢查"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "LineNexus" in response.json()["message"]


def test_callback_no_signature(client):
    """測試缺乏簽章時應回傳 400"""
    response = client.post("/callback", json={})
    assert response.status_code == 400
    assert response.json()["detail"] == "Missing signature"


@patch("lineaihelper.main.handler.handle")
def test_callback_success(mock_handle, client):
    """測試成功的 Webhook 流程 (Mock 驗證)"""
    # 模擬 LINE 的 Webhook payload
    payload = {
        "destination": "xxxxxxxxxx",
        "events": [
            {
                "type": "message",
                "message": {"type": "text", "id": "123456", "text": "Hello"},
                "timestamp": 123456789,
                "source": {"type": "user", "userId": "U123456"},
                "replyToken": "dummy_reply_token",
                "mode": "active",
            }
        ],
    }

    # 執行 POST 請求
    headers = {"X-Line-Signature": "dummy_signature"}
    response = client.post("/callback", json=payload, headers=headers)

    # 驗證
    assert response.status_code == 200
    assert response.text == '"OK"'
    mock_handle.assert_called_once()


def test_invalid_signature(client):
    """測試無效簽章 (不 Mock handle)"""
    # 當我們傳入無效簽章且不 Mock handle 時，handler 應拋出 InvalidSignatureError
    headers = {"X-Line-Signature": "wrong_signature"}
    response = client.post("/callback", content="invalid body", headers=headers)

    # 應回傳 400
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid signature"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "text, expected_fragment, should_call_gemini, should_call_stock",
    [
        ("/stock 2330", "Gemini Analysis Result", True, True),
        ("/stock", "請提供股票代碼", False, False),
        ("/chat hello", "Gemini Chat Response", True, False),
        ("/chat", "請輸入聊天內容", False, False),
        ("/help", "【LineNexus 指令列表】", False, False),
        ("/unknown", "未知指令：/unknown", False, False),
        ("hello world", "LineNexus (Async) 收到：hello world", False, False),
    ],
)
async def test_handle_message_commands(
    text, expected_fragment, should_call_gemini, should_call_stock
):
    """測試 handle_message 的指令解析邏輯 (含 Mock 外部服務)"""

    # Mock asyncio.create_task 以捕捉內部定義的 process_and_reply 協程
    with patch("lineaihelper.main.asyncio.create_task") as mock_create_task, \
         patch("lineaihelper.main.client") as mock_client, \
         patch("lineaihelper.main.yf.Ticker") as mock_ticker:

        # 1. 設定 Mock 行為
        # Mock Line API
        mock_api = AsyncMock()
        app.state.line_bot_api = mock_api

        # Mock Gemini Response (New SDK Structure)
        mock_gemini_response = MagicMock()
        mock_gemini_response.text = expected_fragment if should_call_gemini else "Default AI Response"
        
        # Configure client.aio.models.generate_content
        # Note: client.aio is accessed as a property, so we mock it.
        # .aio.models.generate_content is the async method.
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_gemini_response)

        # Mock yfinance
        mock_stock_info = {
            "longName": "TSMC",
            "currentPrice": 1000,
            "trailingPE": 20,
            "trailingEps": 50,
            "longBusinessSummary": "TSMC is a great company."
        }
        mock_ticker.return_value.info = mock_stock_info

        # 2. 建立 Mock Event
        event = MagicMock(spec=MessageEvent)
        event.reply_token = "dummy_token"
        event.message = MagicMock(spec=TextMessageContent)
        event.message.text = text

        # 3. 執行被測函式
        handle_message(event)

        # 4. 驗證是否有建立非同步任務
        mock_create_task.assert_called_once()
        # 取得被排程的協程 (coroutine)
        coro = mock_create_task.call_args[0][0]

        # 5. 手動執行該協程
        await coro

        # 6. 驗證結果
        # 確認是否呼叫了 reply_message
        mock_api.reply_message.assert_called_once()
        reply_req = mock_api.reply_message.call_args[0][0]
        reply_text = reply_req.messages[0].text
        assert expected_fragment in reply_text

        # 驗證 Gemini 是否被呼叫
        if should_call_gemini:
            mock_client.aio.models.generate_content.assert_called_once()
        else:
            mock_client.aio.models.generate_content.assert_not_called()

        # 驗證 yfinance 是否被呼叫
        if should_call_stock:
            mock_ticker.assert_called_once()
        else:
            mock_ticker.assert_not_called()
