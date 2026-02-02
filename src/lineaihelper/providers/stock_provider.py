import asyncio

import yfinance as yf

from lineaihelper.exceptions import ExternalAPIError
from lineaihelper.models.market_data import KLineBar, KLineData, PriceQuote
from lineaihelper.providers.base_provider import BaseDataProvider


class YahooFinanceProvider(BaseDataProvider):
    """基於 Yahoo Finance 的資料提供者"""

    def _format_symbol(self, symbol: str) -> str:
        """處理台股代碼格式，例如 2330 -> 2330.TW"""
        s = symbol.strip().upper()
        # 如果是純數字，預設視為台股
        if s.isdigit():
            return f"{s}.TW"
        return s

    async def get_quote(self, symbol: str) -> PriceQuote:
        formatted_symbol = self._format_symbol(symbol)
        try:
            # yfinance 是同步的，在非同步環境建議跑在 thread pool
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(
                None, lambda: yf.Ticker(formatted_symbol)
            )
            info = ticker.info

            if not info or "regularMarketPrice" not in info:
                # 有些代碼可能需要從 fast_info 拿
                price = ticker.fast_info.get("last_price")
                if price is None:
                    raise ExternalAPIError(f"找不到代碼 {symbol} 的報價數據")
            else:
                price = info["regularMarketPrice"]

            return PriceQuote(
                symbol=formatted_symbol,
                current_price=price,
                currency=info.get("currency", "USD"),
                change=info.get("regularMarketChange"),
                change_percent=info.get("regularMarketChangePercent"),
            )
        except Exception as e:
            raise ExternalAPIError(f"Yahoo Finance 查詢失敗: {str(e)}") from e

    async def get_history(
        self, symbol: str, interval: str = "1d", period: str = "1mo"
    ) -> KLineData:
        formatted_symbol = self._format_symbol(symbol)
        try:
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(
                None, lambda: yf.Ticker(formatted_symbol)
            )
            df = await loop.run_in_executor(
                None, lambda: ticker.history(period=period, interval=interval)
            )

            if df.empty:
                raise ExternalAPIError(f"找不到代碼 {symbol} 的歷史數據")

            bars = []
            for index, row in df.iterrows():
                bars.append(
                    KLineBar(
                        timestamp=index.to_pydatetime(),
                        open=row["Open"],
                        high=row["High"],
                        low=row["Low"],
                        close=row["Close"],
                        volume=int(row["Volume"]),
                    )
                )

            return KLineData(symbol=formatted_symbol, interval=interval, bars=bars)
        except Exception as e:
            raise ExternalAPIError(f"Yahoo Finance 歷史數據查詢失敗: {str(e)}") from e

    def can_handle(self, symbol: str) -> bool:
        # Yahoo Finance 基本上支援大部分常見代碼
        return True
