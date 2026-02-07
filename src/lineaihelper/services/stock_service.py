import asyncio
from typing import List, Optional

from google import genai

from lineaihelper.exceptions import ExternalAPIError, ServiceError, handle_gemini_error
from lineaihelper.models.market_data import KLineBar
from lineaihelper.prompt_engine import PromptEngine
from lineaihelper.providers.base_provider import BaseDataProvider
from lineaihelper.providers.stock_provider import YahooFinanceProvider
from lineaihelper.services.base_service import BaseService
from lineaihelper.services.technical_analysis_service import TechnicalAnalysisService


class StockService(BaseService):
    """
    股票分析服務，整合市場數據提供者、技術分析與 AI 輔助判讀。
    """

    def __init__(
        self,
        gemini_client: genai.Client,
        provider: Optional[BaseDataProvider] = None,
        prompt_engine: Optional[PromptEngine] = None,
        ta_service: Optional[TechnicalAnalysisService] = None,
    ):
        """
        初始化股票服務。

        Args:
            gemini_client: Google GenAI 用戶端。
            provider: 市場數據提供者 (預設使用 YahooFinanceProvider)。
            prompt_engine: 提示詞引擎。
            ta_service: 技術分析服務。
        """
        self.gemini_client = gemini_client
        self.provider = provider or YahooFinanceProvider()
        self.prompt_engine = prompt_engine or PromptEngine()
        self.ta_service = ta_service or TechnicalAnalysisService()

    async def execute(self, args: str) -> str:
        """
        執行股票分析指令。

        Args:
            args: 指令參數，格式為 "代碼 [策略]"。

        Returns:
            str: AI 產生的分析報告。

        Raises:
            ServiceError: 當參數無效時拋出。
            ExternalAPIError: 當外部數據或 AI 服務異常時拋出。
        """
        if not args:
            raise ServiceError("請提供股票或代碼，例如: .stock 2330 [strategy]")

        parts = args.strip().split()
        symbol = parts[0]
        strategy = parts[1] if len(parts) > 1 else "general"

        # 1. 抓取多週期歷史 K 線與即時報價
        # 直接拋出 ExternalAPIError，由全域 Exception Handler 處理
        quote_task = self.provider.get_quote(symbol)
        daily_task = self.provider.get_history(symbol, period="6mo", interval="1d")
        weekly_task = self.provider.get_history(symbol, period="1y", interval="1wk")
        monthly_task = self.provider.get_history(symbol, period="2y", interval="1mo")

        quote, daily_h, weekly_h, monthly_h = await asyncio.gather(
            quote_task, daily_task, weekly_task, monthly_task
        )

        # 2. 技術指標計算
        enriched_daily = self.ta_service.compute_indicators(daily_h)

        # 3. 準備多週期數據摘要
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

        prompt = self.prompt_engine.render(
            "stock",
            {
                "quote": quote,
                "indicators": enriched_daily.indicators,
                "strategy": strategy,
                "daily_summary": daily_summary,
                "weekly_summary": weekly_summary,
                "monthly_summary": monthly_summary,
            },
        )

        # 4. AI 分析
        try:
            response = await self.gemini_client.aio.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )
            if not response or not response.text:
                raise ExternalAPIError("AI 分析回傳空內容")
            return response.text
        except Exception as e:
            handle_gemini_error(e, default_msg="AI 分析目前無法使用")
