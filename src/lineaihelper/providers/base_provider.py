from abc import ABC, abstractmethod

from lineaihelper.models.market_data import KLineData, PriceQuote


class BaseDataProvider(ABC):
    """資料提供者抽象基底類別"""

    @abstractmethod
    async def get_quote(self, symbol: str) -> PriceQuote:
        """獲取即時報價"""
        pass

    @abstractmethod
    async def get_history(
        self, symbol: str, interval: str = "1d", period: str = "1mo"
    ) -> KLineData:
        """獲取歷史 K 線數據"""
        pass

    @abstractmethod
    def can_handle(self, symbol: str) -> bool:
        """判斷此 Provider 是否能處理該代碼"""
        pass
