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
