# 乾淨架構精髓與領域模型設計

本文件旨在深入闡述「乾淨架構 (Clean Architecture)」的核心思想，並根據 Line AI Helper 專案的具體需求，設計出清晰、獨立的領域模型 (Domain Models)。

---

## 1. 乾淨架構的精髓 (The Essence of Clean Architecture)

乾淨架構的核心在於「依賴倒置原則 (Dependency Inversion Principle)」。您應該先專注於設計理想中的 Domain 層，而不需要先考慮外部 API 的具體實作。

### 1.1. 設計流程

1.  **設計領域層 (Domain Layer)**
    *   先思考應用程式真正需要的資訊，設計出最乾淨且理想的領域模型。
2.  **定義應用層需求 (Application Layer - Ports)**
    *   由 Use Case 定義所需的服務介面 (Ports)，例如定義一個資料抓取的抽象介面。
3.  **實作基礎設施層 (Infrastructure Layer - Adapters)**
    *   在此層級才去研究外部 API 的規格，並撰寫 Adapter 來實作 Ports。Adapter 負責將外部複雜的資料轉換成內部定義的乾淨模型。

### 1.2. 核心優勢

*   **獨立性**: 核心業務邏輯可以獨立進行測試，完全不受外部 API 變動的影響。
*   **可替換性**: 若未來更換數據供應商，僅需實作新的 Adapter，核心程式碼無需修改。

---

## 2. 專案領域模型設計 (Project Domain Models)

本專案使用 Pydantic 定義領域模型，以提供強型別校驗與資料驗證。模型位於 `src/lineaihelper/models/`。

### 2.1. StockKLineData - 單日 K 線資料
代表單一交易日的基礎數據單位。

```python
from datetime import date
from pydantic import BaseModel, Field

class StockKLineData(BaseModel):
    trade_date: date = Field(..., description="交易日期")
    open_price: float = Field(..., description="開盤價")
    high_price: float = Field(..., description="最高價")
    low_price: float = Field(..., description="最低價")
    close_price: float = Field(..., description="收盤價")
    volume: int = Field(..., description="成交量")

    class Config:
        from_attributes = True
```

### 2.2. StockData - 股票歷史資料
代表一支股票在一段時間內的 K 線歷史資料集合。

```python
from typing import List
from pydantic import BaseModel, Field

class StockData(BaseModel):
    symbol: str = Field(..., description="股票代碼")
    klines: List[StockKLineData] = Field(..., description="K 線數據列表")

    class Config:
        from_attributes = True
```

### 2.3. AnalysisResult - AI 分析結果
代表從大型語言模型 (LLM) 取得的處理結果。

```python
from pydantic import BaseModel, Field

class AnalysisResult(BaseModel):
    summary_text: str = Field(..., description="由 AI 生成的市場分析文字")

    class Config:
        from_attributes = True
```

### 2.4. UserQuery - 使用者查詢紀錄
代表一次完整的業務互動事件。

```python
from datetime import datetime
from pydantic import BaseModel, Field

class UserQuery(BaseModel):
    user_id: str = Field(..., description="LINE 使用者 ID")
    original_text: str = Field(..., description="原始輸入文字")
    stock_symbol: str = Field(..., description="解析出的股票代碼")
    stock_data: StockData = Field(..., description="獲取的股票歷史資料")
    analysis_result: AnalysisResult = Field(..., description="生成的 AI 分析結果")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="建立時間 (UTC)")

    class Config:
        from_attributes = True
```