from datetime import datetime, timedelta

import pytest

from lineaihelper.models.market_data import KLineBar, KLineData
from lineaihelper.services.technical_analysis_service import TechnicalAnalysisService


@pytest.fixture
def sample_kline_data() -> KLineData:
    """產生 100 根測試用的 K 線數據，確保足以計算 MA60"""
    bars = []
    base_time = datetime(2025, 1, 1)
    for i in range(100):
        bars.append(
            KLineBar(
                timestamp=base_time + timedelta(days=i),
                open=100.0 + i,
                high=105.0 + i,
                low=95.0 + i,
                close=102.0 + i,
                volume=1000 + i * 10,
            )
        )
    return KLineData(symbol="TEST", interval="1d", bars=bars)


def test_compute_indicators_success(sample_kline_data: KLineData) -> None:
    service = TechnicalAnalysisService()
    enriched_data = service.compute_indicators(sample_kline_data)

    assert enriched_data.symbol == "TEST"
    assert enriched_data.interval == "1d"
    assert len(enriched_data.bars) == 100

    indicators = enriched_data.indicators
    # 驗證 MA 是否有計算出來
    assert indicators.ma5 is not None
    assert indicators.ma10 is not None
    assert indicators.ma20 is not None
    assert indicators.ma60 is not None
    assert indicators.rsi is not None
    assert indicators.macd_diff is not None
    assert indicators.bb_upper is not None

    # 簡單驗證數值合理性 (遞增數列的 MA5 應該接近最後幾項的平均)
    # 最後幾項 close: 102+95...102+99 (197...201)
    # 預期 ma5 接近 199
    assert 190 < (indicators.ma5 or 0) < 210


def test_compute_indicators_empty() -> None:
    service = TechnicalAnalysisService()
    empty_data = KLineData(symbol="EMPTY", interval="1d", bars=[])
    enriched_data = service.compute_indicators(empty_data)

    assert enriched_data.symbol == "EMPTY"
    assert enriched_data.indicators.ma5 is None
