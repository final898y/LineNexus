# 乾淨架構精髓與領域模型設計

本文件旨在深入闡述「乾淨架構 (Clean Architecture)」的核心思想，並根據 `Line AI Helper` 專案的具體需求，設計出清晰、獨立的領域模型 (Domain Models)。

---

## 1. 乾淨架構的精髓 (The Essence of Clean Architecture)

您的問題是：「我是不是應該先查詢各外接 API 的設計，才能開始設計自己的 Domain 層？」

**簡單的答案是：正好相反。您應該先專注於設計自己理想中的 Domain 層，而「不用」先去管外部 API 長什麼樣子。**

這就是「乾淨架構」最强大的地方，我們稱之為「**依賴倒置 (Dependency Inversion Principle)**」。

### 1.1. 設計流程

1.  **先設計您自己的理想世界 (Domain Layer)**
    *   您應該先思考：「對我的應用程式來說，一個最乾淨、最理想的『股票分析』物件應該長什麼樣子？」
    *   您會設計出一個或多個只包含您的應用程式真正需要的資訊的「領域模型」，這些模型非常乾淨，沒有任何跟外部 API 相關的雜訊。

2.  **由「應用層」定義需求 (Application Layer - Ports)**
    *   接下來，您的應用層 Use Case (`AnalyzeStockUseCase`) 會定義它需要什麼樣的服務介面 (Ports)。
    *   例如，它會宣告：「我需要一個 `IStockDataService`，它要能接收一個股票代碼，然後回傳給我一個理想的 `StockData` 物件。」

3.  **最後才由「基礎設施層」去適應外部世界 (Infrastructure Layer - Adapters)**
    *   **這一步才是您去研究外部 API 的地方。**
    *   您會建立一個 `YFinanceAdapter` 來實作 `IStockDataService` 這個介面。
    *   在這個 Adapter 裡，您會去呼叫 `yfinance`。`yfinance` 可能會回傳一個包含幾十個欄位的複雜物件。
    *   **Adapter 的工作**：就是扮演「翻譯官」和「過濾器」的角色。它負責從 `yfinance` 的複雜回傳資料中，挑出您需要的欄位，把它們填入您自己定義的、乾淨的 `StockData` 物件中，最後再回傳給應用層。

### 1.2. 一個比喻：插座與電器

*   **Domain Model (您的電器)**: 您的筆記型電腦，它只需要一個標準的兩孔或三孔插頭。它不在乎電是從核電廠、火力發電廠還是太陽能板來的。
*   **Port (插座)**: 牆上的標準插座，這是一個標準介面。
*   **Adapter (變壓器/轉接頭)**: 如果您從台灣（110V）帶電腦去歐洲（220V），您需要一個變壓器。這個變壓器的責任就是把外部不標準的電力（220V），轉換成您的電器需要的標準電力（110V）。

在這個比喻中，研究外部 API 就相當於去研究歐洲的電壓標準，但這個研究是為了**製造變壓器 (Adapter)**，而不是為了**改造您的電腦 (Domain)**。

### 1.3. 核心優勢

*   **獨立性**: 您的核心業務邏輯（Domain & Application）非常乾淨，可以獨立進行測試，完全不受外部 API 變動的影響。
*   **可替換性**: 未來如果您想從 `yfinance` 更換成另一個股票 API，您需要做的**僅僅是**再寫一個新的 Adapter。您的所有核心程式碼一行都不用改！

---

## 2. 專案領域模型設計 (Project Domain Models)

根據以上原則，我們為 `Line AI Helper` 專案設計以下領域模型。我們將使用 `Pydantic` 來定義這些模型，它能提供資料驗證、清晰的結構，並與 FastAPI 完美整合。

這些模型將會放在 `src/lineaihelper/domain/models.py` 檔案中。

### 2.1. `StockKLineData` - 單日 K 線資料

代表單一一天的 K 線數據，是一個最基礎的資料單位。

```python
from datetime import date
from pydantic import BaseModel, Field

class StockKLineData(BaseModel):
    """
    代表單日的 K 線數據模型
    """
    trade_date: date = Field(..., description="交易日期")
    open_price: float = Field(..., description="開盤價")
    high_price: float = Field(..., description="最高價")
    low_price: float = Field(..., description="最低價")
    close_price: float = Field(..., description="收盤價")
    volume: int = Field(..., description="成交量")

    class Config:
        # Pydantic V2
        from_attributes = True
        # Pydantic V1
        # orm_mode = True
```

### 2.2. `StockData` - 股票歷史資料

代表一支股票在一段時間內的完整 K 線歷史資料。

```python
from typing import List

class StockData(BaseModel):
    """
    代表一支股票的歷史 K 線數據集合
    """
    symbol: str = Field(..., description="股票代碼")
    klines: List[StockKLineData] = Field(..., description="一段時間內的 K 線數據列表")

    class Config:
        from_attributes = True
```

### 2.3. `AnalysisResult` - AI 分析結果

代表從大型語言模型 (LLM) 取得的分析結果。

```python
class AnalysisResult(BaseModel):
    """
    代表 AI 分析後的結果
    """
    summary_text: str = Field(..., description="由 AI 生成的市場分析或總結文字")

    class Config:
        from_attributes = True
```

### 2.4. `UserQuery` - 使用者查詢的完整紀錄

這是我們最核心的領域物件之一，它代表了一次完整且成功的使用者互動事件，從使用者輸入到系統回覆的完整過程。

```python
from datetime import datetime

class UserQuery(BaseModel):
    """
    代表一次完整的使用者查詢事件
    """
    user_id: str = Field(..., description="發出請求的 LINE 使用者 ID")
    original_text: str = Field(..., description="使用者輸入的原始文字")
    stock_symbol: str = Field(..., description="從文字中成功解析出的股票代碼")
    
    stock_data: StockData = Field(..., description="為本次查詢所獲取的股票歷史資料")
    analysis_result: AnalysisResult = Field(..., description="為本次查詢所生成的 AI 分析結果")
    
    created_at: datetime = Field(default_factory=datetime.utcnow, description="查詢事件建立的時間 (UTC)")

    class Config:
        from_attributes = True
```
