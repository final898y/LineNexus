from google import genai

from lineaihelper.exceptions import ExternalAPIError, ServiceError
from lineaihelper.providers.base_provider import BaseDataProvider
from lineaihelper.providers.stock_provider import YahooFinanceProvider
from lineaihelper.services.base_service import BaseService


class StockService(BaseService):
    def __init__(self, gemini_client: genai.Client, provider: BaseDataProvider = None):
        self.gemini_client = gemini_client
        # 預設使用 YahooFinanceProvider，未來可從外部注入不同的 Provider
        self.provider = provider or YahooFinanceProvider()

    async def execute(self, args: str) -> str:
        if not args:
            raise ServiceError("請提供股票或代碼，例如: /stock 2330")

        symbol = args.strip()

        # 1. 抓取即時報價與歷史 K 線 (為了技術分析)
        try:
            quote = await self.provider.get_quote(symbol)
            # 預設抓取過去一個月的日線數據
            history = await self.provider.get_history(
                symbol, period="1mo", interval="1d"
            )
        except ExternalAPIError as e:
            raise ServiceError(f"資料檢索失敗: {str(e)}") from e

        # 2. 準備技術分析摘要
        bars_summary = "\n".join(
            [
                f"- {b.timestamp.strftime('%Y-%m-%d')}: "
                f"O:{b.open}, H:{b.high}, L:{b.low}, C:{b.close}, V:{b.volume}"
                for b in history.bars[-5:]  # 只取最近 5 天顯示在 Prompt 中作為範例
            ]
        )

        prompt = (
            f"你是一位專業的投資分析師。請針對以下數據提供繁體中文分析報告：\n\n"
            f"【基本資料】\n"
            f"代碼：{quote.symbol}\n"
            f"目前價格：{quote.current_price} {quote.currency}\n"
            f"漲跌幅：{quote.change_percent or 0:.2f}%\n\n"
            f"【近期 K 線數據 (最近 5 天)】\n"
            f"{bars_summary}\n\n"
            f"【分析要求】\n"
            f"1. 根據最近一個月的價格走勢進行技術分析總結。\n"
            f"2. 說明目前的支撐與壓力位（若可判斷）。\n"
            f"3. 給予短期的操作建議與風險提示。\n"
            f"請以專業、客觀且簡潔的口吻回覆。"
        )

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
