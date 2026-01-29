from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from lineaihelper.services.stock_service import StockService
from lineaihelper.exceptions import ServiceError, ExternalAPIError

@pytest.mark.asyncio
async def test_stock_service_execute_success():
    mock_gemini = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Stock Analysis Result"
    mock_gemini.aio.models.generate_content = AsyncMock(return_value=mock_response)

    service = StockService(mock_gemini)

    with patch("lineaihelper.services.stock_service.yf.Ticker") as mock_ticker:
        mock_ticker.return_value.info = {
            "regularMarketPrice": 100,
            "longName": "Test Stock",
        }
        response = await service.execute("2330")
        assert response == "Stock Analysis Result"

@pytest.mark.asyncio
async def test_stock_service_no_args():
    mock_gemini = MagicMock()
    service = StockService(mock_gemini)
    
    with pytest.raises(ServiceError) as excinfo:
        await service.execute("")
    assert "請提供股票代碼" in str(excinfo.value)

@pytest.mark.asyncio
async def test_stock_service_not_found():
    mock_gemini = MagicMock()
    service = StockService(mock_gemini)

    with patch("lineaihelper.services.stock_service.yf.Ticker") as mock_ticker:
        mock_ticker.return_value.info = {}
        with pytest.raises(ServiceError) as excinfo:
            await service.execute("INVALID")
        assert "找不到股票代碼" in str(excinfo.value)

@pytest.mark.asyncio
async def test_stock_service_ai_error():
    mock_gemini = MagicMock()
    mock_gemini.aio.models.generate_content.side_effect = Exception("Gemini Down")
    service = StockService(mock_gemini)

    with patch("lineaihelper.services.stock_service.yf.Ticker") as mock_ticker:
        mock_ticker.return_value.info = {"regularMarketPrice": 100}
        with pytest.raises(ExternalAPIError) as excinfo:
            await service.execute("2330")
        assert "AI 分析目前無法使用" in str(excinfo.value)