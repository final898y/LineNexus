from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from lineaihelper.exceptions import ExternalAPIError, ServiceError
from lineaihelper.models.market_data import KLineBar, KLineData, PriceQuote
from lineaihelper.services.stock_service import StockService


@pytest.fixture
def mock_provider() -> MagicMock:
    provider = MagicMock()
    provider.get_quote = AsyncMock()
    provider.get_history = AsyncMock()
    return provider


@pytest.mark.asyncio
async def test_stock_service_execute_success(mock_provider: MagicMock) -> None:
    mock_gemini = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Stock Analysis Result"
    mock_gemini.aio.models.generate_content = AsyncMock(return_value=mock_response)

    # 準備足夠的 Mock 數據以便計算指標
    mock_provider.get_quote.return_value = PriceQuote(
        symbol="2330.TW", current_price=100.0, currency="TWD", change_percent=1.5
    )

    # 產生 65 根 K 線以滿足 MA60 計算
    bars = [
        KLineBar(
            timestamp=datetime.now() - timedelta(days=i),
            open=90,
            high=110,
            low=85,
            close=100,
            volume=1000,
        )
        for i in range(70)
    ]

    mock_provider.get_history.return_value = KLineData(
        symbol="2330.TW",
        interval="1d",
        bars=bars,
    )

    service = StockService(mock_gemini, provider=mock_provider)
    response = await service.execute("2330 momentum")

    assert response == "Stock Analysis Result"
    mock_provider.get_quote.assert_called_once_with("2330")
    # 確認 get_history 被呼叫了 3 次 (日, 週, 月)
    assert mock_provider.get_history.call_count == 3


@pytest.mark.asyncio
async def test_stock_service_no_args() -> None:
    mock_gemini = MagicMock()
    service = StockService(mock_gemini)

    with pytest.raises(ServiceError) as excinfo:
        await service.execute("")
    assert "請提供股票" in str(excinfo.value)


@pytest.mark.asyncio
async def test_stock_service_data_fetch_error(mock_provider: MagicMock) -> None:
    mock_gemini = MagicMock()
    mock_provider.get_quote.side_effect = ExternalAPIError("Provider Error")

    service = StockService(mock_gemini, provider=mock_provider)

    with pytest.raises(ExternalAPIError) as excinfo:
        await service.execute("2330")
    assert "Provider Error" in str(excinfo.value)


@pytest.mark.asyncio
async def test_stock_service_ai_error(mock_provider: MagicMock) -> None:
    mock_gemini = MagicMock()
    mock_gemini.aio.models.generate_content.side_effect = Exception("Gemini Down")

    mock_provider.get_quote.return_value = PriceQuote(
        symbol="2330.TW", current_price=100.0
    )
    mock_provider.get_history.return_value = KLineData(
        symbol="2330.TW", interval="1d", bars=[]
    )

    service = StockService(mock_gemini, provider=mock_provider)

    with pytest.raises(ExternalAPIError) as excinfo:
        await service.execute("2330")
    assert "AI 分析目前無法使用" in str(excinfo.value)
