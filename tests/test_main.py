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

    headers = {"X-Line-Signature": "dummy_signature"}
    response = client.post("/callback", json=payload, headers=headers)

    assert response.status_code == 200
    assert response.text == '"OK"'
    mock_handle.assert_called_once()


@pytest.mark.asyncio
async def test_handle_message_via_dispatcher():
    """測試 handle_message 是否正確呼叫 Dispatcher"""

    with patch("lineaihelper.main.asyncio.create_task") as mock_create_task:
        # Mock API and Dispatcher in app.state
        mock_api = AsyncMock()
        mock_dispatcher = AsyncMock()
        mock_dispatcher.parse_and_execute.return_value = "Dispatcher Reply"

        app.state.line_bot_api = mock_api
        app.state.dispatcher = mock_dispatcher

        # Create Mock Event
        event = MagicMock(spec=MessageEvent)
        event.reply_token = "dummy_token"
        event.message = MagicMock(spec=TextMessageContent)
        event.message.text = "/chat hello"

        # Execute
        handle_message(event)

        # Verify task creation
        mock_create_task.assert_called_once()
        coro = mock_create_task.call_args[0][0]

        # Run the task
        await coro

        # Verify calls
        mock_dispatcher.parse_and_execute.assert_called_once_with("/chat hello")
        mock_api.reply_message.assert_called_once()
