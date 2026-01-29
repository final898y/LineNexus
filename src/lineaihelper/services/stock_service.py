import asyncio
import yfinance as yf
from google import genai
from loguru import logger

from lineaihelper.services.base_service import BaseService
from lineaihelper.exceptions import ServiceError, ExternalAPIError


class StockService(BaseService):
    def __init__(self, gemini_client: genai.Client):
        self.gemini_client = gemini_client

    async def execute(self, args: str) -> str:
        if not args:
            raise ServiceError("請提供股票代碼，例如: /stock 2330")

        symbol = args.strip()
        if symbol.isdigit() and len(symbol) == 4:
            symbol = f"{symbol}.TW"

        # 1. 抓取資料
        def fetch_data():
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                if not info or ("regularMarketPrice" not in info and "currentPrice" not in info):
                    return None
                return info
            except Exception as e:
                raise ExternalAPIError(f"抓取股票 {symbol} 資料時發生錯誤", original_exception=e)

        info = await asyncio.to_thread(fetch_data)
        if not info:
            raise ServiceError(f"找不到股票代碼 '{symbol}'，請確認後再試一次。")

        # 2. 準備 AI 分析
        stock_data = {
            "name": info.get("longName", symbol),
            "price": info.get("currentPrice", info.get("regularMarketPrice", "N/A")),
            "pe": info.get("trailingPE", "N/A"),
            "eps": info.get("trailingEps", "N/A"),
            "summary": info.get("longBusinessSummary", "")[:500],
        }

        prompt = (
            f"Please analyze the following stock data (Traditional Chinese):\n"
            f"Stock: {stock_data['name']} ({symbol})\n"
            f"Price: {stock_data['price']}\n"
            f"PE: {stock_data['pe']}\n"
            f"EPS: {stock_data['eps']}\n"
            f"Summary: {stock_data['summary']}...\n"
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
            if isinstance(e, ExternalAPIError):
                raise
            raise ExternalAPIError("AI 分析目前無法使用，請稍後再試。", original_exception=e)