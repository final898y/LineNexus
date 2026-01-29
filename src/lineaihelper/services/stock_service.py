import asyncio
import yfinance as yf
from google import genai
from loguru import logger

from lineaihelper.services.base_service import BaseService


class StockService(BaseService):
    def __init__(self, gemini_client: genai.Client):
        self.gemini_client = gemini_client

    async def execute(self, args: str) -> str:
        if not args:
            return "Please provide stock symbol, e.g., /stock 2330"

        symbol = args.strip()
        # 簡易判斷台股代碼
        if symbol.isdigit() and len(symbol) == 4:
            symbol = f"{symbol}.TW"

        try:
            # 在執行緒中執行同步的 yfinance 呼叫，避免阻塞 Event Loop
            def fetch_data():
                ticker = yf.Ticker(symbol)
                info = ticker.info
                # 簡單的防呆，若抓不到通常會拋錯或回傳空
                return {
                    "symbol": symbol,
                    "name": info.get("longName", symbol),
                    "price": info.get(
                        "currentPrice", info.get("regularMarketPrice", "N/A")
                    ),
                    "pe": info.get("trailingPE", "N/A"),
                    "eps": info.get("trailingEps", "N/A"),
                    "summary": info.get("longBusinessSummary", "")[:500],
                }

            stock_data = await asyncio.to_thread(fetch_data)

            # 組裝 Prompt
            prompt = (
                f"Please analyze the following stock data (Traditional Chinese):\n"
                f"Stock: {stock_data['name']} ({stock_data['symbol']})\n"
                f"Price: {stock_data['price']}\n"
                f"PE: {stock_data['pe']}\n"
                f"EPS: {stock_data['eps']}\n"
                f"Summary: {stock_data['summary']}...\n"
            )

            # 呼叫 Gemini 分析
            response = await self.gemini_client.aio.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )
            return response.text

        except Exception as e:
            logger.error(f"Stock lookup failed: {e}")
            return f"Error looking up {symbol}. Please check the symbol."
