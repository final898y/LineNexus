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
    "text, expected_fragment",
    [
        ("/stock 2330", "收到股票分析指令，代碼：2330"),
        ("/stock", "請提供股票代碼"),
        ("/chat hello", "收到 AI 聊天指令：hello"),
        ("/chat", "請輸入聊天內容"),
        ("/help", "【LineNexus 指令列表】"),
        ("/unknown", "未知指令：/unknown"),
        ("hello world", "LineNexus (Async) 收到：hello world"),
    ],
)
async def test_handle_message_commands(text, expected_fragment):
    """測試 handle_message 的指令解析邏輯"""

    # Mock asyncio.create_task 以捕捉內部定義的 send_reply 協程
    with patch("lineaihelper.main.asyncio.create_task") as mock_create_task:
        # Mock app.state 中的 Line API
        mock_api = AsyncMock()
        # 由於 app 是全域變數，直接設定 state
        app.state.line_bot_api = mock_api

        # 建立 Mock Event
        event = MagicMock(spec=MessageEvent)
        event.reply_token = "dummy_token"
        event.message = MagicMock(spec=TextMessageContent)
        event.message.text = text

        # 執行被測函式
        handle_message(event)

        # 驗證是否有建立非同步任務
        mock_create_task.assert_called_once()
        # 取得被排程的協程 (coroutine)
        coro = mock_create_task.call_args[0][0]

        # 手動執行該協程
        await coro

        # 驗證是否呼叫了 reply_message
        mock_api.reply_message.assert_called_once()

        # 檢查回覆內容
        reply_req = mock_api.reply_message.call_args[0][0]
        reply_text = reply_req.messages[0].text
        assert expected_fragment in reply_text
