from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class PriceQuote(BaseModel):
    """即時報價模型"""

    symbol: str
    current_price: float
    currency: str = "USD"
    change: Optional[float] = None
    change_percent: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class KLineBar(BaseModel):
    """單根 K 線模型"""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class KLineData(BaseModel):
    """K 線序列模型"""

    symbol: str
    interval: str  # e.g., "1d", "1h"
    bars: List[KLineBar]

    @property
    def last_close(self) -> float:
        return self.bars[-1].close if self.bars else 0.0


class TechnicalIndicators(BaseModel):
    """技術指標數據"""

    ma5: Optional[float] = None
    ma10: Optional[float] = None
    ma20: Optional[float] = None
    ma60: Optional[float] = None
    rsi: Optional[float] = None
    macd_diff: Optional[float] = None
    macd_dea: Optional[float] = None
    macd_hist: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None


class EnrichedKLineData(BaseModel):
    """富集後的 K 線數據 (包含原始 K 線與技術指標)"""

    symbol: str
    interval: str
    bars: List[KLineBar]
    indicators: TechnicalIndicators
