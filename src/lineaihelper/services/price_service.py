from typing import Optional

from lineaihelper.exceptions import ExternalAPIError, ServiceError
from lineaihelper.providers.base_provider import BaseDataProvider
from lineaihelper.providers.stock_provider import YahooFinanceProvider
from lineaihelper.services.base_service import BaseService


class PriceService(BaseService):
    def __init__(self, provider: Optional[BaseDataProvider] = None):
        self.provider = provider or YahooFinanceProvider()

    async def execute(self, args: str) -> str:
        if not args:
            raise ServiceError("請提供股票或代碼，例如: .price 2330")

        symbol = args.strip()

        try:
            quote = await self.provider.get_quote(symbol)
            history = await self.provider.get_history(
                symbol, period="1mo", interval="1d"
            )
        except ExternalAPIError as e:
            raise ServiceError(f"資料檢索失敗: {str(e)}") from e

        # 格式化報價
        change_val = quote.change or 0
        pct_val = quote.change_percent or 0
        change_icon = "📈" if change_val >= 0 else "📉"

        lines = [
            f"【股票報價】{quote.symbol}",
            f"目前價格: {quote.current_price} {quote.currency}",
            f"今日漲跌: {change_val:+.2f} ({pct_val:+.2f}%) {change_icon}",
            "",
            "【最近 5 日 K 線】",
        ]

        for b in history.bars[-5:]:
            lines.append(
                f"- {b.timestamp.strftime('%m/%d')}: "
                f"C:{b.close:<7} V:{b.volume:,}"
            )

        return "\n".join(lines)
