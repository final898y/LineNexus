import asyncio
import textwrap
from typing import List, Optional

from google import genai

from lineaihelper.exceptions import ExternalAPIError, ServiceError
from lineaihelper.models.market_data import KLineBar
from lineaihelper.providers.base_provider import BaseDataProvider
from lineaihelper.providers.stock_provider import YahooFinanceProvider
from lineaihelper.services.base_service import BaseService


class StockService(BaseService):
    def __init__(
        self, gemini_client: genai.Client, provider: Optional[BaseDataProvider] = None
    ):
        self.gemini_client = gemini_client
        # 預設使用 YahooFinanceProvider，未來可從外部注入不同的 Provider
        self.provider = provider or YahooFinanceProvider()

    async def execute(self, args: str) -> str:
        if not args:
            raise ServiceError("請提供股票或代碼，例如: /stock 2330")

        symbol = args.strip()

        # 1. 抓取多週期歷史 K 線與即時報價
        try:
            quote_task = self.provider.get_quote(symbol)
            # 日線：3 個月，用於觀察短期均線與型態
            daily_task = self.provider.get_history(symbol, period="3mo", interval="1d")
            # 週線：1 年，用於觀察中長期趨勢
            weekly_task = self.provider.get_history(symbol, period="1y", interval="1wk")
            # 月線：2 年，用於觀察長期基期
            monthly_task = self.provider.get_history(
                symbol, period="2y", interval="1mo"
            )

            quote, daily_h, weekly_h, monthly_h = await asyncio.gather(
                quote_task, daily_task, weekly_task, monthly_task
            )
        except ExternalAPIError as e:
            raise ServiceError(f"資料檢索失敗: {str(e)}") from e

        # 2. 準備多週期數據摘要
        def format_bars(bars: List[KLineBar], count: int) -> str:
            return "\n".join(
                [
                    f"- {b.timestamp.strftime('%Y-%m-%d')}: "
                    f"O:{b.open}, H:{b.high}, L:{b.low}, C:{b.close}, V:{b.volume}"
                    for b in bars[-count:]
                ]
            )

        daily_summary = format_bars(daily_h.bars, 22)  # 約一個月的交易日
        weekly_summary = format_bars(weekly_h.bars, 12)  # 約三個月的週線
        monthly_summary = format_bars(monthly_h.bars, 12)  # 一年的月線

        prompt = textwrap.dedent(f"""
            你是一位具有10年以上經驗的台股技術分析師，
            擅長以清楚、理性的方式向一般投資人說明盤勢，
            請依據以下資料提供專業分析。

            【基本資料】
            代碼：{quote.symbol}
            目前價格：{quote.current_price} {quote.currency}
            漲跌幅：{quote.change_percent or 0:.2f}%

            【日 K 線（近一個月）】
            {daily_summary}

            【週 K 線（近 12 週）】
            {weekly_summary}

            【月 K 線（近 12 個月）】
            {monthly_summary}

            【分析要求】
            請依下列結構回覆：

            一、趨勢總覽（短中長期方向）
            二、技術指標分析（價格與均線、量價關係）
            三、支撐與壓力位置
            四、短期操作建議
            五、主要風險提醒

            分析原則：
            1. 內容須依據提供資料推論，不可憑空假設。
            2. 若資料不足，請明確說明「資料不足，無法判斷」。
            3. 避免誇大或過度樂觀語氣。
            4. 使用繁體中文撰寫。
            5. 文字清楚、有條理、適合一般投資人閱讀。
        """).strip()

        # 3. AI 分析
        try:
            response = await self.gemini_client.aio.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )
            if not response or not response.text:
                raise ExternalAPIError("AI 分析回傳空內容")
            return response.text
        except Exception as e:
            raise ExternalAPIError(
                "AI 分析目前無法使用，請稍後再試。", original_exception=e
            ) from e
