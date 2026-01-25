# 軟體設計文件 (Software Design Document) - Line AI Helper

**版本**: 1.0.0
**日期**: 2025-11-23

---

## 1. 簡介

### 1.1. 文件目的

本文件旨在詳細闡述「股市分析小幫手 (Line AI Helper)」專案的系統架構、詳細設計、技術選型與開發部署流程。其主要目標是作為專案開發、維護和未來擴展的技術藍圖與核心指引，確保團隊成員對系統有共同的理解。

### 1.2. 專案概述

本專案是一個整合大型語言模型（LLM）的 LINE 聊天機器人，旨在提供台股市場的簡易智慧分析。使用者透過 LINE 傳送股票代碼或名稱，後端系統將自動抓取即時金融數據，提交給 AI 模型進行分析，並將分析結果以友善的格式回傳給使用者。

### 1.3. 專案範疇

#### 1.3.1. 範圍內 (In-Scope)

*   **LINE 機器人互動**: 接收使用者訊息，並回傳格式化訊息。
*   **股票資料查詢**: 支援以台股代碼或名稱查詢。
*   **K 線數據抓取**: 從外部 API 獲取股票的歷史 K 線數據（開、高、低、收、量）。
*   **AI 分析整合**: 將股票數據傳送至大型語言模型（LLM），生成分析見解。
*   **非同步 Web 應用**: 使用 FastAPI 處理來自 LINE 的 Webhook 請求。

#### 1.3.2. 範圍外 (Out-of-Scope)

*   **使用者身份驗證與管理**: 不涉及使用者登入或個人化設定。
*   **交易功能**: 不提供任何下單、交易或帳務管理功能。
*   **即時報價**: 非即時串流報價，數據有一定延遲。
*   **複雜圖表繪製**: 初期版本不包含在後端動態生成 K 線圖圖片。
*   **多市場支援**: 初期版本僅專注於台灣股市 (TWSE)。

### 1.4. 名詞定義與縮寫

| 詞彙    | 全名                        | 說明                                          |
| :------ | :-------------------------- | :-------------------------------------------- |
| **AI**  | Artificial Intelligence     | 人工智慧，此處特指大型語言模型。              |
| **API** | Application Programming Interface | 應用程式介面，用於不同服務間的資料交換。    |
| **LLM** | Large Language Model        | 大型語言模型，如 Google Gemini。            |
| **SDK** | Software Development Kit    | 軟體開發套件。                                |
| **Webhook** | Webhook                   | 由事件觸發的 HTTP 回呼 (Callback) 機制。      |
| **FastAPI** | FastAPI                   | 一個基於 Python 3.8+ 的現代、高效能 Web 框架。 |
| **uv**  | uv                          | 一個極速的 Python 套件安裝與解析器。          |
| **K 線**  | Candlestick Chart         | 呈現特定時間內股價變動的圖表。              |

---

## 2. 系統架構

### 2.1. 高階架構圖

本系統採用標準的事件驅動與微服務架構，核心由一個後端應用程式負責協調各方服務。

```mermaid
graph TD
    A[使用者] -- "傳送股票代碼/名稱" --> B(LINE App)
    B -- "Webhook 觸發" --> C{後端伺服器 (FastAPI)}
    subgraph "後端伺服器內部邏輯"
        C -- "1. 驗證請求合法性" --> C
        C -- "2. 查詢股票數據" --> D[股市資料 API<br>(yfinance)]
        D -- "回傳 K 線數據" --> C
        C -- "3. 準備 Prompt" --> E[大型語言模型 AI<br>(Google Gemini)]
        E -- "回傳分析建議" --> C
        C -- "4. 格式化訊息" --> F[LINE Messaging API]
    end
    F -- "推播訊息" --> B
    B -- "顯示分析結果" --> A
```

### 2.2. 元件說明

1.  **使用者介面 (Client)**
    *   **LINE App**: 使用者與系統互動的唯一介面，負責傳送文字訊息及顯示回覆。

2.  **後端伺服器 (Backend Server)**
    *   **描述**: 系統核心，負責所有業務邏輯的處理與服務調度。
    *   **技術**: 使用 Python 與 FastAPI 框架開發。
    *   **職責**:
        *   提供一個公開的 `/callback` 端點以接收 LINE Platform 的 Webhook 事件。
        *   使用 LINE Bot SDK 驗證請求簽章，確保訊息來源合法。
        *   解析使用者訊息，提取股票代碼或名稱。
        *   呼叫外部股市資料 API (yfinance) 以獲取數據。
        *   建構 Prompt (包含指令與 K 線數據)，並呼叫 LLM 進行分析。
        *   解析 LLM 回應，並將其封裝成 LINE Message Objects。
        *   透過 LINE Messaging API 將結果回傳給使用者。

3.  **外部服務 (External Services)**
    *   **LINE Platform**: 提供機器人帳號管理、Messaging API 和 Webhook 功能。
    *   **股市資料 API (yfinance)**: 提供股票歷史 K 線數據的公開來源。
    *   **大型語言模型 (LLM)**: 本專案使用 Google Gemini，提供自然語言分析與生成能力。

### 2.3. 資料流程

1.  **請求發起**: 使用者在 LINE 中傳送一則包含股票代碼（如 "2330"）或名稱（如 "台積電"）的訊息。
2.  **Webhook 觸發**: LINE Platform 接收到訊息後，向後端伺服器預先設定的 Webhook URL (`/callback`) 發送一個 HTTP POST 請求。
3.  **請求處理**:
    *   後端伺服器接收到請求，首先驗證其 X-Line-Signature 標頭以確認請求合法性。
    *   驗證通過後，解析請求內文，取得使用者 ID 和訊息內容。
4.  **資料獲取**: 伺服器根據訊息內容，使用 `yfinance` 函式庫向 Yahoo Finance 抓取該股票最近一段時間的 K 線數據。
5.  **AI 分析**:
    *   伺服器將獲取到的 K 線數據（通常是 CSV 或 JSON 格式）與一個預設的 Prompt 模板結合。
    *   Prompt 範例：「你是一位台灣股市分析專家，請根據以下 K 線數據，用繁體中文提供對這支股票的簡短分析與未來展望...」。
    *   伺服器將完整的 Prompt 發送給 Google Gemini API。
6.  **回應生成與回傳**:
    *   Gemini API 回傳分析結果的文字。
    *   伺服器將此文字封裝成一個或多個 LINE `TextMessage` 物件。
    *   伺服器呼叫 LINE Messaging API 的 "Reply Message" 功能，將訊息回傳給原始使用者。
7.  **結果呈現**: 使用者在 LINE App 中看到 AI 生成的股市分析結果。

---

## 3. 細節設計

### 3.1. API 端點設計

#### `POST /callback`

*   **目的**: 接收來自 LINE Platform 的所有 Webhook 事件。
*   **方法**: `POST`
*   **請求標頭**:
    *   `Content-Type: application/json`
    *   `X-Line-Signature`: LINE 平台用於驗證請求來源的簽章。
*   **請求內文 (Body)**: LINE 事件物件陣列。
    ```json
    {
      "destination": "YOUR_USER_ID",
      "events": [
        {
          "type": "message",
          "message": {
            "type": "text",
            "id": "14353798921116",
            "text": "2330"
          },
          "webhookEventId": "01FZ74A0F_...",
          "deliveryContext": { "isRedelivery": false },
          "timestamp": 1625665242211,
          "source": {
            "type": "user",
            "userId": "U_USER_ID_..."
          },
          "replyToken": "REPLY_TOKEN_...",
          "mode": "active"
        }
      ]
    }
    ```
*   **成功回應**:
    *   **狀態碼**: `200 OK`
    *   **內文**: 空
*   **失敗回應**:
    *   **狀態碼**: `400 Bad Request` (若請求無效)、`401 Unauthorized` (若簽章驗證失敗)。

### 3.2. 核心模組規劃

為了保持程式碼的清晰與可維護性，後端邏輯應拆分為以下幾個模組：

*   **`main.py`**:
    *   功能：FastAPI 應用程式的進入點。
    *   職責：建立 FastAPI 實例、掛載 API 路由 (`/callback`)、處理 Webhook 的主要分派邏輯。

*   **`line_handler.py`**:
    *   功能：處理所有與 LINE 平台相關的邏輯。
    *   職責：驗證簽章、解析事件物件、從事件中提取訊息、呼叫 `line-bot-sdk` 回傳訊息。

*   **`stock_service.py`**:
    *   功能：封裝所有與股票資料獲取相關的邏輯。
    *   職責：提供一個函式，接收股票代碼，使用 `yfinance` 查詢並回傳格式化的 K 線數據。處理查詢失敗或查無此股的例外情況。

*   **`ai_service.py`**:
    *   功能：封裝與大型語言模型 (LLM) 互動的邏輯。
    *   職責：提供一個函式，接收數據與 Prompt，呼叫 Gemini API，並回傳純文字的分析結果。

*   **`config.py`**:
    *   功能：集中管理環境變數。
    *   職責：讀取 `.env` 檔案，並以強型別的方式提供給應用程式各模組使用（例如使用 Pydantic）。

### 3.3. 資料模型

*   **`StockData`**: 代表從 `yfinance` 獲取的 K 線數據結構，可以是 `pandas.DataFrame` 或轉換後的 `List[Dict]`。
    *   欄位: `Date`, `Open`, `High`, `Low`, `Close`, `Volume`

*   **`AnalysisResult`**: 代表從 AI 模型回傳的分析結果。
    *   格式: 純文字字串。

### 3.4. 程式碼架構：乾淨架構 (Clean Architecture)

根據討論，本專案將採用**乾淨架構**以實現高度模組化、可測試性與長期可維護性。此架構的核心思想是「依賴倒置」，確保核心業務邏輯獨立於外部框架和工具。

#### 3.4.1. 核心分層與職責

*   **A. 領域層 (Domain Layer)**: 專案的心臟，定義核心業務物件(Entities)和規則。它完全獨立，不知道外部世界的存在。
    *   **實現**: `src/lineaihelper/domain/models.py` 將定義如 `StockAnalysis` 等 Pydantic 模型，代表核心資料結構。

*   **B. 應用層 (Application Layer)**: 負責協調領域層完成具體的使用案例(Use Cases)，定義業務流程。此層只依賴於領域層和抽象介面(Ports)。
    *   **實現**: `src/lineaihelper/application/use_cases/analyze_stock.py` 將建立一個 `AnalyzeStockUseCase` 類別，其流程為：
        1.  呼叫抽象的 `IStockService` 介面獲取股票資料。
        2.  呼叫抽象的 `IAIService` 介面進行 AI 分析。
        3.  呼叫抽象的 `IQueryRepository` 介面儲存查詢紀錄。
        4.  呼叫抽象的 `IMessageSender` 介面回傳訊息。

*   **C. 基礎設施層 (Infrastructure Layer)**: 負責所有外部工具的「具體實現」，實作應用層定義的抽象介面。
    *   **實現**:
        *   `infrastructure/adapters/yfinance_adapter.py`：實作 `IStockService`，真正呼叫 `yfinance`。
        *   `infrastructure/adapters/gemini_adapter.py`：實作 `IAIService`，真正呼叫 Gemini API。
        *   `infrastructure/database/postgres_repository.py`：實作 `IQueryRepository`，使用 `SQLAlchemy` 操作 PostgreSQL。

*   **D. 介面層 (Interface Layer)**: 系統的進入點，此處指 FastAPI 的路由。
    *   **實現**: `src/lineaihelper/api/routers/callback.py` 將包含 `/callback` 路由，負責接收請求、透過依賴注入(Dependency Injection)組裝並執行 `AnalyzeStockUseCase`。

#### 3.4.2. 最終資料夾結構

```
src/lineaihelper/
├── __init__.py
├── main.py                 # D. 介面層: FastAPI 應用入口，組裝依賴注入
│
├── api/                    # D. 介面層: API 路由
│   └── routers/
│       └── callback.py
│
├── application/            # B. 應用層
│   ├── use_cases/
│   │   └── analyze_stock.py
│   └── ports/              # 抽象介面 (Ports)
│       ├── ai_service.py
│       ├── stock_data_service.py
│       ├── message_sender.py
│       └── query_repository.py
│
├── domain/                 # A. 領域層
│   └── models.py           # 核心業務模型 (Entities)
│
└── infrastructure/         # C. 基礎設施層
    ├── adapters/           # 外部服務的具體實現
    │   ├── gemini_service.py
    │   ├── yfinance_service.py
    │   └── line_service.py
    └── database/           # 資料庫的具體實現
        ├── connection.py   # SQLAlchemy 連線設定
        ├── models.py       # SQLAlchemy 的 Table 模型
        └── postgres_repository.py
```

---

## 4. 資料庫與資料持久化

根據決策，本專案將使用 PostgreSQL 作為主要資料庫，以確保正式環境的穩定性與效能。

### 4.1. 技術選型

*   **資料庫**: **PostgreSQL**
*   **ORM (Object-Relational Mapping)**: **SQLAlchemy 2.0**，與 FastAPI 及 Pydantic 有良好的整合性，可讓我們用 Python 物件來操作資料庫，同時保留未來遷移的彈性。

### 4.2. 資料表綱要 (Schema)

為了儲存使用者查詢歷史，將建立一個 `query_logs` 資料表：

| 欄位名稱       | 資料型別      | 說明                             |
| :------------- | :------------ | :------------------------------- |
| `id`           | `BIGINT` (PK) | 流水號 (Primary Key)             |
| `user_id`      | `VARCHAR`     | LINE 使用者的唯一 ID             |
| `query_text`   | `TEXT`        | 使用者輸入的原始查詢文字         |
| `stock_symbol` | `VARCHAR`     | 成功解析出的股票代碼，可為空   |
| `llm_response` | `TEXT`        | AI 模型回覆的內容摘要            |
| `status`       | `VARCHAR`     | 處理狀態 (e.g., SUCCESS, FAILED) |
| `created_at`   | `TIMESTAMPZ`  | 查詢建立時間                     |

---

## 5. 記錄 (Logging)

日誌系統對於偵錯、監控與問題追蹤至關重要。本專案採用 **Loguru** 作為日誌處理工具，並將配置邏輯獨立於核心業務代碼之外。

### 5.1. 實作方式

*   **獨立配置**: 使用單獨的 `logging_config.py` 模組，在應用程式啟動時（`main.py`）進行初始化。
*   **Loguru 整合**: 相比於內建的 `logging` 模組，Loguru 提供更直觀的 API、自動化的日誌輪換 (Rotation) 與壓縮，並支援非同步寫入。
*   **支援中文**: 強制使用 `UTF-8` 編碼，確保中文字元在日誌檔案中正確顯示。

### 5.2. 日誌級別與內容

*   **`DEBUG`**: 詳細的技術性資訊，用於開發環境排錯。包含請求的完整內文與系統內部狀態。
*   **`INFO`**: 關鍵的正常流程。例如：「Webhook 驗證通過」、「成功解析股票代碼」、「AI 分析完成」。
*   **`WARNING`**: 非預期但不會導致請求失敗的情況。例如：「API 回應延遲較長」、「查無特定日期的 K 線數據」。
*   **`ERROR`**: 導致請求失敗的錯誤。例如：「yfinance 服務不可用」、「Gemini API 認證失敗」、「資料庫連線中斷」。

### 5.3. 儲存與輪換策略

*   **檔案儲存**: 日誌會儲存於專案根目錄的 `logs/` 資料夾中。
*   **檔名格式**: `lineaihelper_{time:YYYY-MM-DD}.log`。
*   **輪換 (Rotation)**: 設定為每 500 MB 或每日輪換一次。
*   **保留 (Retention)**: 僅保留最近 10 天的日誌。
*   **壓縮 (Compression)**: 舊日誌將自動壓縮為 `.zip` 以節省空間。

---

## 6. 技術棧

| 類別        | 技術/函式庫           | 用途                                    |
| :---------- | :---------------------- | :-------------------------------------- |
| **後端語言**  | Python 3.9+             | 主要開發語言。                          |
| **Web 框架**  | FastAPI                 | 高效能的非同步 Web 框架，用於建立 API。 |
| **LINE 整合** | `line-bot-sdk`          | 處理 LINE Messaging API 的官方套件。    |
| **股票資料**  | `yfinance`              | 從 Yahoo Finance 抓取金融數據。         |
| **AI 模型**   | `google-generativeai`   | 與 Google Gemini API 互動的官方套件。 |
| **日誌處理**  | `loguru`                | 現代化的日誌管理工具。                  |
| **代碼檢查**  | `ruff`                  | 極速的 Python Linter & Formatter。      |
| **資料庫**    | PostgreSQL              | 關聯式資料庫，用於儲存查詢紀錄。        |
| **ORM**       | SQLAlchemy              | 資料庫操作工具。                        |
| **套件管理**  | `uv`                    | 高效的 Python 環境與依賴管理工具。      |
| **Web 伺服器** | Uvicorn                 | ASGI 伺服器，用於運行 FastAPI 應用程式。 |

---

## 7. 開發與部署

### 7.1. 環境設置

1.  **複製專案**:
    ```bash
    git clone https://github.com/your-username/LineAiHelper.git
    cd LineAiHelper
    ```

2.  **建立虛擬環境與安裝依賴**:
    本專案使用 `uv` 管理環境。
    ```bash
    # 建立 .venv 虛擬環境
    uv venv

    # 根據 pyproject.toml 安裝所有依賴
    uv sync
    ```

3.  **設定環境變數**:
    複製 `.env.example` 為 `.env`，並填入您的金鑰與資料庫連線資訊。
    ```bash
    cp .env.example .env
    ```
    **`.env` 檔案內容**:
    ```ini
    LINE_CHANNEL_ACCESS_TOKEN="YOUR_LINE_CHANNEL_ACCESS_TOKEN"
    LINE_CHANNEL_SECRET="YOUR_LINE_CHANNEL_SECRET"
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    DATABASE_URL="postgresql://user:password@host:port/dbname"
    ```

### 7.2. 本地開發

1.  **啟動開發伺服器**:
    ```bash
    uv run dev
    ```
    伺服器將運行在 `http://127.0.0.1:8000`。

2.  **建立公開通道 (Webhook)**:
    使用 `ngrok` 或其他類似工具。
    ```bash
    ngrok http 8000
    ```

3.  **設定 LINE Webhook**:
    *   前往 [LINE Developers Console](https://developers.line.biz/console/)。
    *   將 Webhook URL 設為 `[你的 ngrok 網址]/callback`。
    *   啟用 "Use webhook"。

### 7.3. 部署策略 (Production)

對於生產環境，建議使用容器化技術進行部署。

1.  **容器化**:
    *   建立一個 `Dockerfile`，基於 Python 官方映像檔。
    *   在 Dockerfile 中，複製專案檔案，並使用 `uv sync` 安裝依賴。
    *   使用 `uvicorn` 作為正式的 ASGI 伺服器。
        ```bash
        CMD ["uv", "run", "uvicorn", "lineaihelper.main:app", "--host", "0.0.0.0", "--port", "8080"]
        ```

2.  **託管平台**:
    *   可將容器映像檔部署至雲端服務，如 **Google Cloud Run**, **AWS App Runner**, 或 **Heroku**。
    *   在託管平台上設定好環境變數。

---

## 8. 未來工作與藍圖

以下為專案未來可能的功能擴展方向：

-   [ ] **多市場支援**: 擴展股票資料來源，支援美股、日股等。
-   [ ] **圖表視覺化**: 整合 `matplotlib` 或 `plotly`，將 K 線圖或技術指標以圖片形式回傳給使用者。
-   [ ] **進階技術指標**: 增加 RSI, MACD, 布林通道等技術指標的計算與分析。
-   [ ] **使用者偏好設定**: 允許使用者設定感興趣的股票清單、分析風格偏好等。
-   [ ] **Prompt 優化**: 透過 Prompt Engineering 技術，持續優化 AI 的分析品質與準確性。
-   [ ] **非同步任務處理**: 對於耗時較長的操作（如複雜分析），改用背景任務佇列（如 Celery）處理，避免請求超時。

---

## 9. 附錄

### 9.1. 環境變數說明

| 變數名稱                    | 必要 | 說明                                       | 來源                       |
| :-------------------------- | :--- | :----------------------------------------- | :------------------------- |
| `LINE_CHANNEL_ACCESS_TOKEN` | 是   | LINE Messaging API 的長期存取權杖。        | LINE Developers Console    |
| `LINE_CHANNEL_SECRET`       | 是   | 用於驗證 Webhook 請求來源的頻道密鑰。    | LINE Developers Console    |
| `GEMINI_API_KEY`            | 是   | 用於存取 Google Gemini API 的金鑰。        | Google AI Studio           |
| `DATABASE_URL`              | 是   | PostgreSQL 資料庫的連線字串。            | 自行設定/雲端資料庫提供商 |

