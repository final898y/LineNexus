from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from lineaihelper.exceptions import ExternalAPIError, ServiceError
from lineaihelper.models.market_data import KLineBar, KLineData, PriceQuote
from lineaihelper.services.price_service import PriceService


@pytest.fixture
def mock_provider() -> MagicMock:
    provider = MagicMock()
    provider.get_quote = AsyncMock()
    provider.get_history = AsyncMock()
    return provider


@pytest.mark.asyncio
async def test_price_service_execute_success(mock_provider: MagicMock) -> None:
    # 準備 Mock 數據
    mock_provider.get_quote.return_value = PriceQuote(
        symbol="2330.TW",
        current_price=100.0,
        currency="TWD",
        change=1.5,
        change_percent=1.5,
    )
    mock_provider.get_history.return_value = KLineData(
        symbol="2330.TW",
        interval="1d",
        bars=[
            KLineBar(
                timestamp=datetime(2023, 10, 27),
                open=90,
                high=110,
                low=85,
                close=100,
                volume=1000,
            )
        ],
    )

    service = PriceService(provider=mock_provider)
    response = await service.execute("2330")

    assert "【股票報價】2330.TW" in response
    assert "目前價格: 100.0 TWD" in response
    assert "10/27" in response
    mock_provider.get_quote.assert_called_once_with("2330")


@pytest.mark.asyncio
async def test_price_service_no_args() -> None:
    service = PriceService()

    with pytest.raises(ServiceError) as excinfo:
        await service.execute("")
    assert "請提供股票" in str(excinfo.value)


@pytest.mark.asyncio
async def test_price_service_data_fetch_error(mock_provider: MagicMock) -> None:
    mock_provider.get_quote.side_effect = ExternalAPIError("Provider Error")

    service = PriceService(provider=mock_provider)

    with pytest.raises(ServiceError) as excinfo:
        await service.execute("2330")
    assert "資料檢索失敗" in str(excinfo.value)
