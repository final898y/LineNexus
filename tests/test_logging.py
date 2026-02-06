import json
from unittest.mock import MagicMock, patch
import pytest
from loguru import logger
from lineaihelper.logging_config import serialize, setup_logging

def test_serialize_output() -> None:
    """測試日誌序列化功能是否產生正確的 JSON 格式"""
    test_record = {
        "time": MagicMock(),
        "level": MagicMock(),
        "message": "test message",
        "name": "test_module",
        "function": "test_func",
        "line": 10,
        "extra": {"trace_id": "test-trace-123"},
        "exception": None
    }
    # 模擬物件屬性
    test_record["time"].isoformat.return_value = "2026-02-07T00:00:00"
    test_record["level"].name = "INFO"
    
    output = serialize(test_record)
    data = json.loads(output)
    
    assert data["message"] == "test message"
    assert data["extra"]["trace_id"] == "test-trace-123"
    assert data["level"] == "INFO"
    assert "timestamp" in data

def test_setup_logging_json_mode() -> None:
    """測試在 LOG_JSON=True 時初始化日誌系統是否不噴錯"""
    with patch("lineaihelper.logging_config.settings") as mock_settings:
        mock_settings.LOG_JSON = True
        try:
            setup_logging()
            # 觸發一次日誌輸出以確保 sink 正常運作
            logger.info("Test JSON log sink")
        except KeyError as e:
            pytest.fail(f"KeyError detected in JSON logging: {e}. Check if format_map is being misused.")
        except Exception as e:
            pytest.fail(f"setup_logging failed in JSON mode: {e}")
        finally:
            # 測試完畢後恢復日誌設定，避免影響其他測試
            setup_logging()