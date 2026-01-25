import pytest
from fastapi.testclient import TestClient

from lineaihelper.main import app


@pytest.fixture
def client():
    """
    建立一個共用的 TestClient fixture。
    這樣每個測試函式只需要請求 `client` 參數即可使用。
    """
    return TestClient(app)
