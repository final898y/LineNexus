# 專案開發計畫與任務清單 (Project Development Plan & Task List)

本文件旨在闡明 Line AI Helper 專案從設計到實現的具體步驟，包含詳細的資料流程、開發流程，以及一份可執行的任務清單。

---

## 1. 資料流程設計 (Data Flow Design)

在我們選定的「乾淨架構」下，一次典型的股票查詢請求，其資料流程如下：

1.  **API 層 (`/callback`)**:
    *   **接收**: 接收來自 LINE Platform 的 Webhook HTTP POST 請求 (JSON 格式)。
    *   **資料模型**: 使用 `line-bot-sdk` 內建的事件模型來解析請求。
    *   **傳遞**: 從請求中提取關鍵資訊 (如 `user_id`, `text`)，並將其作為簡單的參數傳遞給應用層的 Use Case 進行處理。

2.  **應用層 (`AnalyzeStockUseCase`)**:
    *   **接收**: 從 API 層接收到 `user_id` 和 `text`。
    *   **資料流程**:
        1.  呼叫 `IStockService` **介面**，傳入 `text`，獲取標準化的 `StockData` 物件 (一個定義在領域層的 `Domain Model`)。
        2.  呼叫 `IAIService` **介面**，傳入 `StockData`，獲取 `AnalysisResult` 物件 (另一個 `Domain Model`)。
        3.  建立一個 `UserQuery` 領域物件，包含 `user_id`, `text`, `AnalysisResult` 等資訊。
        4.  呼叫 `IQueryRepository` **介面**，將 `UserQuery` 領域物件傳入，以儲存到資料庫中。
        5.  呼叫 `IMessageSender` **介面**，傳入 `user_id` 和 `AnalysisResult.text` 以回傳訊息給使用者。
    *   **設計關鍵**: 這一層完全是圍繞著純粹的 Python 物件和抽象介面來運作，它不知道有 HTTP、SQL 或任何外部函式庫的存在，確保了業務邏輯的獨立性。

3.  **基礎設施層 (Adapters & Repositories)**:
    *   **`YFinanceService`** (實作 `IStockService` 介面):
        *   **API 請求**: 內部呼叫 `yfinance` 函式庫，例如 `yfinance.Ticker("...").history(...)`。
        *   **資料模型轉換**: 將 `yfinance` 回傳的 `pandas.DataFrame` 格式，轉換為我們在領域層定義的標準 `StockData` 物件。
    *   **`GeminiService`** (實作 `IAIService` 介面):
        *   **API 請求**: 構造一個 HTTP POST 請求到 Google Gemini API。
        *   **資料模型轉換**: 將 Gemini API 回傳的 JSON 回應，解析成我們領域層的 `AnalysisResult` 物件。
    *   **`PostgresRepository`** (實作 `IQueryRepository` 介面):
        *   **資料庫請求**: 接收應用層傳來的 `UserQuery` 領域物件，將其轉換為 `SQLAlchemy` 的 ORM 模型，然後執行 `INSERT` SQL 操作。

這個流程確保了每一層的職責單一且清晰，資料在跨越不同層級時會被標準化，從而實現了高度的解耦和可維護性。

---

## 2. 專案製作流程 (Project Production Flow)

我們將遵循一個由內而外的開發順序，以確保架構的穩固性：

1.  **初始化 (Initialization)**: 建立專案的基礎，包含所有依賴和符合乾淨架構的資料夾結構。
2.  **由內而外定義 (Inside-Out Definition)**: 從專案的最核心開始，首先定義 `Domain` 層的資料模型，然後是 `Application` 層的業務流程介面 (Ports) 和使用案例 (Use Cases)。
3.  **實作基礎設施 (Infrastructure Implementation)**: 實作所有與外部世界的串接，包含資料庫的連線與操作、對 `yfinance` 和 `Gemini` 等外部 API 的呼叫。
4.  **組裝與整合 (Assembly & Integration)**: 完成最外層的 `API` 路由，並透過依賴注入 (Dependency Injection) 將所有實作好的基礎設施服務「注入」到應用層中，將整個流程串連起來。
5.  **完善與健壯化 (Refinement & Robustness)**: 在所有關鍵路徑上加入結構化的日誌和明確的錯誤處理機制，並開始撰寫單元測試與整合測試。
6.  **部署 (Deployment)**: 將應用程式容器化 (Dockerize)，並撰寫部署相關的文件。

---

## 3. 任務清單 (Task List)

以下是我們將逐步完成的詳細任務列表：

- [ ] **1. 專案初始化與結構建立 (Project Initialization & Scaffolding)**
  - [ ] 1.1. 根據乾淨架構建立完整的資料夾結構 (api, application, domain, infrastructure)。
  - [ ] 1.2. 安裝核心依賴 (fastapi, uvicorn, pydantic, sqlalchemy, psycopg2-binary, google-generativeai, yfinance, line-bot-sdk)。
  - [ ] 1.3. 設定基礎的 FastAPI main.py，包含應用程式實例與根路由。
- [ ] **2. 領域層與應用層定義 (Domain & Application Layer Definition)**
  - [ ] 2.1. 在 domain/models.py 中定義核心 Pydantic 模型 (例如 UserQuery, StockAnalysis)。
  - [ ] 2.2. 在 application/ports/ 中定義所有抽象介面 (IStockService, IAIService, IQueryRepository, IMessageSender)。
  - [ ] 2.3. 在 application/use_cases/ 中建立 AnalyzeStockUseCase 的基本骨架，並定義其依賴的抽象介面。
- [ ] **3. 基礎設施層 - 資料庫 (Infrastructure - Database)**
  - [ ] 3.1. 在 infrastructure/database/connection.py 中設定 SQLAlchemy 引擎與連線至 PostgreSQL。
  - [ ] 3.2. 在 infrastructure/database/models.py 中建立 query_logs 的 SQLAlchemy ORM 模型。
  - [ ] 3.3. 實作一個簡單的資料庫遷移(migration)腳本或方式來建立資料表。
  - [ ] 3.4. 在 infrastructure/database/postgres_repository.py 中實作 IQueryRepository 介面。
- [ ] **4. 基礎設施層 - 外部服務 (Infrastructure - External Services)**
  - [ ] 4.1. 在 infrastructure/adapters/yfinance_service.py 中實作 IStockService 介面。
  - [ ] 4.2. 在 infrastructure/adapters/gemini_service.py 中實作 IAIService 介面。
  - [ ] 4.3. 在 infrastructure/adapters/line_service.py 中實作 IMessageSender 介面。
- [ ] **5. 介面層與依賴注入 (Interface Layer & Dependency Injection)**
  - [ ] 5.1. 在 api/routers/callback.py 中完成 /callback 路由的邏輯。
  - [ ] 5.2. 在 main.py 中設定依賴注入 (Dependency Injection)，將具體的 Infrastructure 服務注入到 Use Case。
  - [ ] 5.3. 實現完整的端到端 (End-to-End) 流程，從接收 LINE 訊息到回傳分析結果。
- [ ] **6. LOG 與錯誤處理 (Logging & Error Handling)**
  - [ ] 6.1. 根據 SDD 設計，在專案中全面導入結構化日誌。
  - [ ] 6.2. 在 Use Case 和 Adapters 中加入適當的 try-except 區塊，進行錯誤處理與日誌記錄。
- [ ] **7. 測試撰寫 (Testing)**
  - [ ] 7.1. 為 AnalyzeStockUseCase 撰寫單元測試 (Unit Tests)，使用 Mock 物件模擬外部依賴。
  - [ ] 7.2. 為 /callback 端點撰寫整合測試 (Integration Tests)。
- [ ] **8. 容器化與部署 (Containerization & Deployment)**
  - [ ] 8.1. 撰寫 Dockerfile。
  - [ ] 8.2. 撰寫 docker-compose.yml 以方便本地啟動應用程式和 PostgreSQL 資料庫。
  - [ ] 8.3. 更新 README.md 或 docs/DEPLOYMENT.md，提供部署說明。
