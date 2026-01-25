from unittest.mock import MagicMock, patch

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
                "message": {
                    "type": "text",
                    "id": "123456",
                    "text": "Hello"
                },
                "timestamp": 123456789,
                "source": {
                    "type": "user",
                    "userId": "U123456"
                },
                "replyToken": "dummy_reply_token",
                "mode": "active"
            }
        ]
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
    # 這裡我們使用一個錯誤的簽章
    headers = {"X-Line-Signature": "wrong_signature"}
    response = client.post("/callback", content="invalid body", headers=headers)
    
    # 應回傳 400 (由 main.py 中的 except InvalidSignatureError 捕捉)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid signature"