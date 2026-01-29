from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from lineaihelper.services.stock_service import StockService

@pytest.mark.asyncio
async def test_stock_service_execute_success():
    # Arrange
    mock_gemini = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Stock Analysis Result"
    mock_gemini.aio.models.generate_content = AsyncMock(return_value=mock_response)

    service = StockService(mock_gemini)

    # Mock yfinance inside the service module
    with patch("lineaihelper.services.stock_service.yf.Ticker") as mock_ticker:
        mock_ticker.return_value.info = {
            "longName": "Test Stock",
            "currentPrice": 100,
            "regularMarketPrice": 100,
            "trailingPE": 10,
            "trailingEps": 5,
            "longBusinessSummary": "Summary",
        }

        # Act
        response = await service.execute("2330")

        # Assert
        assert response == "Stock Analysis Result"
        mock_ticker.assert_called_once_with("2330.TW")
        mock_gemini.aio.models.generate_content.assert_called_once()

@pytest.mark.asyncio
async def test_stock_service_no_args():
    mock_gemini = MagicMock()
    service = StockService(mock_gemini)
    
    response = await service.execute("")
    assert "Please provide stock symbol" in response

@pytest.mark.asyncio
async def test_stock_service_api_error():
    # Arrange
    mock_gemini = MagicMock()
    service = StockService(mock_gemini)

    with patch("lineaihelper.services.stock_service.yf.Ticker") as mock_ticker:
        # Simulate an error from yfinance
        mock_ticker.side_effect = Exception("API Error")
        
        # Act
        response = await service.execute("2330")
        
        # Assert
        assert "Error looking up 2330.TW" in response
