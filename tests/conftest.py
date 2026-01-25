import pytest
from fastapi.testclient import TestClient
from lineaihelper.main import app

@pytest.fixture
def client():
    """
    建立一個支援 lifespan 的 TestClient fixture。
    """
    # 使用 with 語句確保 FastAPI 的 lifespan (startup/shutdown) 被執行
    with TestClient(app) as c:
        yield c