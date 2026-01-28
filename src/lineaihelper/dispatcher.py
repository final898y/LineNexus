import asyncio

import yfinance as yf
from google import genai
from loguru import logger


class CommandDispatcher:
    def __init__(self, gemini_client: genai.Client):
        self.gemini_client = gemini_client

    async def parse_and_execute(self, user_text: str) -> str:
        if not user_text.startswith("/"):
            return f"LineNexus (Async) received: {user_text}"

        parts = user_text.split(" ", 1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        logger.info(f"Dispatching command: {command}")

        if command == "/stock":
            return await self._handle_stock(args)
        elif command == "/chat":
            return await self._handle_chat(args)
        elif command == "/help":
            return self._handle_help()
        else:
            return f"Unknown command: {command}, type /help for info."

    async def _handle_stock(self, args: str) -> str:
        if not args:
            return "Please provide stock symbol, e.g., /stock 2330"

        symbol = args.strip()
        if symbol.isdigit() and len(symbol) == 4:
            symbol = f"{symbol}.TW"

        try:

            def fetch_data():
                ticker = yf.Ticker(symbol)
                info = ticker.info
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

            prompt = (
                f"Please analyze the following stock data (Traditional Chinese):\n"
                f"Stock: {stock_data['name']} ({stock_data['symbol']})\n"
                f"Price: {stock_data['price']}\n"
                f"PE: {stock_data['pe']}\n"
                f"EPS: {stock_data['eps']}\n"
                f"Summary: {stock_data['summary']}...\n"
            )

            response = await self.gemini_client.aio.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Stock lookup failed: {e}")
            return f"Error looking up {symbol}. Please check the symbol."

    async def _handle_chat(self, args: str) -> str:
        if not args:
            return "Please provide content, e.g., /chat hello"

        try:
            response = await self.gemini_client.aio.models.generate_content(
                model="gemini-2.5-flash", contents=args
            )
            return response.text
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return "AI is currently unavailable."

    def _handle_help(self) -> str:
        return (
            "[LineNexus Commands]\n"
            "/stock [symbol] - Stock analysis\n"
            "/chat [content] - AI chat\n"
            "/help - Show this help"
        )
