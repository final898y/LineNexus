from typing import Any, Optional

import pandas as pd
import pandas_ta as ta  # noqa: F401

from lineaihelper.models.market_data import (
    EnrichedKLineData,
    KLineData,
    TechnicalIndicators,
)


class TechnicalAnalysisService:
    """
    技術分析服務，負責計算 K 線數據的技術指標。
    """

    def compute_indicators(self, data: KLineData) -> EnrichedKLineData:
        """
        計算技術指標並返回富集後的數據。

        Args:
            data (KLineData): 原始 K 線數據

        Returns:
            EnrichedKLineData: 包含技術指標的富集數據
        """
        if not data.bars:
            return EnrichedKLineData(
                symbol=data.symbol,
                interval=data.interval,
                bars=data.bars,
                indicators=TechnicalIndicators(),
            )

        # 1. 轉換為 Pandas DataFrame
        df = pd.DataFrame([bar.model_dump() for bar in data.bars])
        df.set_index("timestamp", inplace=True)

        # 2. 計算指標
        # 移動平均線 (MA)
        df.ta.sma(length=5, append=True)
        df.ta.sma(length=10, append=True)
        df.ta.sma(length=20, append=True)
        df.ta.sma(length=60, append=True)

        # 相對強弱指標 (RSI)
        df.ta.rsi(length=14, append=True)

        # 指數平滑異同移動平均線 (MACD)
        df.ta.macd(fast=12, slow=26, signal=9, append=True)

        # 布林通道 (Bollinger Bands)
        df.ta.bbands(length=20, std=2, append=True)

        # 3. 提取最後一筆數據作為當前指標
        last_row = df.iloc[-1]

        def get_val(col: str) -> Optional[float]:
            val: Any = last_row.get(col)
            if val is None or pd.isna(val):
                return None
            return float(val)

        # 根據 pandas-ta 的欄位命名慣例提取
        indicators = TechnicalIndicators(
            ma5=get_val("SMA_5"),
            ma10=get_val("SMA_10"),
            ma20=get_val("SMA_20"),
            ma60=get_val("SMA_60"),
            rsi=get_val("RSI_14"),
            macd_diff=get_val("MACD_12_26_9"),
            macd_dea=get_val("MACDs_12_26_9"),
            macd_hist=get_val("MACDh_12_26_9"),
            bb_upper=get_val("BBU_20_2.0_2.0"),
            bb_middle=get_val("BBM_20_2.0_2.0"),
            bb_lower=get_val("BBL_20_2.0_2.0"),
        )

        return EnrichedKLineData(
            symbol=data.symbol,
            interval=data.interval,
            bars=data.bars,
            indicators=indicators,
        )
