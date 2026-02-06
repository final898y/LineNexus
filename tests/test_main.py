from unittest.mock import MagicMock, patch

from linebot.v3.exceptions import InvalidSignatureError


def test_read_root(client: MagicMock) -> None:
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "LineNexus"
    assert data["status"] == "up"


def test_health_check(client: MagicMock) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_callback_no_signature(client: MagicMock) -> None:
    response = client.post("/callback")
    assert response.status_code == 400
    assert response.json()["detail"] == "Missing signature"


def test_callback_invalid_signature(client: MagicMock) -> None:
    with patch("lineaihelper.main.handler.handle") as mock_handle:
        mock_handle.side_effect = InvalidSignatureError()
        response = client.post(
            "/callback",
            headers={"X-Line-Signature": "invalid_sig"},
            content="test body",
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid signature"


def test_callback_success(client: MagicMock) -> None:
    with patch("lineaihelper.main.handler.handle") as mock_handle:
        response = client.post(
            "/callback",
            headers={"X-Line-Signature": "valid_sig"},
            content="test body",
        )
        assert response.status_code == 200
        assert response.text == '"OK"'
        mock_handle.assert_called_once()


def test_start() -> None:
    with patch("uvicorn.run") as mock_run:
        from lineaihelper.main import start

        start()
        mock_run.assert_called_once()
