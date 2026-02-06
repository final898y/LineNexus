# LineNexus 開發計畫與任務清單 (Project Development Plan)

**版本**: 2.1.0
**日期**: 2026-02-05

本文件定義了 **LineNexus | AI 指令樞紐** 的開發路徑。我們採取 **「MVP 優先，逐步重構」** 的策略，但堅持 **「測試與開發並行」** 的原則，確保系統在演進過程中始終維持高品質。

---

## 1. 開發原則 (Development Principles) - *Updated*

為了確保程式碼品質與可維護性，所有開發任務必須遵守以下 **Definition of Done (DoD)**：

1.  **功能實作 (Implementation)**: 程式碼需符合 PEP 8 風格規範 (透過 `ruff` 檢查)。
2.  **同步測試 (Tests Included)**: 
    *   **新功能**: 必須包含對應的 Unit Test (單元測試)。
    *   **Bug 修復**: 必須包含能重現該 Bug 的測試案例 (Regression Test)。
    *   **重構**: 必須確保現有測試全數通過 (Green)。
3.  **Schema as Code**: 所有資料庫變更必須透過 **Migration Scripts (Alembic)** 進行，嚴禁手動修改 DB Schema。
4.  **文件更新 (Documentation)**: 若修改了架構或指令用法，需同步更新 `README.md` 或 API 文件。

---

## 2. MVP 資料流程 (MVP Data Flow)

1.  **接收 (Webhook)**: `main.py` 接收 LINE 傳來的文字訊息 (賦予 Request ID)。
2.  **解析 (Dispatcher)**: 透過簡單的文字處理 (如 `startswith(".")`) 判斷指令類型。
3.  **分發 (Services)**: 透過 `CommandDispatcher` 將請求分派給具體的 `Service` 類別。
4.  **執行 (Domain Logic)**:
    *   `StockService`: 抓取數據 -> 透過 `PromptEngine` 渲染提示詞 -> 丟給 Gemini -> 取得建議。
    *   `PriceService`: 抓取數據 -> 格式化回傳。
    *   `ChatService`: 透過 `PromptEngine` 載入人設 -> 丟給 Gemini 進行對話。
5.  **回傳 (Line API)**: 將結果透過 `line-bot-sdk` 推播回使用者。

---

## 3. 開發策略：從實作到重構 (Evolutionary Strategy)

*   **第一階段：連通性 (The Connectivity)** - *Completed*
    *   目標：建立與 LINE Platform 的連線，完成 Hello World。
*   **第二階段：模組化 (The Modularization)** - *Completed*
    *   目標：建立 Service 層與 Dispatcher，分離職責。
*   **第 2.5 階段：AI 工程化基礎建設 (AI Engineering Infrastructure)** - *Completed*
    *   目標：將 Prompt 與程式碼解耦，建立版本化管理機制。
    *   重點：實作 `PromptEngine`、外部 Markdown 管理與 Jinja2 變數注入。
*   **第三階段：持久化與本地環境標準化 (Persistence & Local Std)** - *Current*
    *   目標：引入 PostgreSQL，並建立標準化開發環境。
    *   重點：使用 **Alembic** 管理 DB 版本，使用 **Docker Compose** 統一本地環境，實作 Repository Pattern。
*   **第四階段：DevOps 與自動化 (DevOps & Automation)**
    *   目標：建立 CI/CD 流水線與容器化部署。
    *   重點：GitHub Actions, Pre-commit hooks, Dockerfile 優化。
*   **第五階段：多元數據與技術分析強化 (Market Data Evolution)**
    *   目標：引入 Data Provider 模式，支援多來源數據。
*   **第六階段：系統韌性與可觀測性 (Resilience & Observability)**
    *   目標：強化系統在高併發下的穩定性。
    *   重點：Rate Limiting, Circuit Breaker, Request Tracing (Loguru + Correlation ID)。

---

## 4. 任務清單 (Task List)

### Phase 1: 基礎連通與 MVP 骨架 (Hello LineNexus)
- [x] **1.1. 建立基礎 Webhook**
- [x] **1.2. 實作簡易指令解析**
- [x] **1.3. 串接 Stock MVP 流程**

### Phase 2: 指令分發器與服務模組化 (The Hub Architecture)
- [x] **2.1. 重構 Dispatcher**
- [x] **2.2. 建立 Service 體系** (Stock, Chat, Help)
- [x] **2.3. 增強錯誤處理機制**
- [x] **2.4. 靜態型別強化 (Static Type Safety)**

### Phase 2.5: AI 工程化基礎建設 (Prompt as Code)
- [x] **2.5.1. 建立 Prompt Loader 機制**
- [x] **2.5.2. 外部化 Prompt 管理**
- [x] **2.5.3. 實作 Prompt 版本化**
- [x] **2.5.4. 單元測試與驗證**

### Phase 3: 持久化與本地環境標準化 (Persistence & Local Std)
- [x] **3.1. 結構化日誌與基礎可觀測性 (Observability Foundation)**
  - 實作 `loguru` 的 JSON 格式輸出 (僅限生產環境)，便於 ELK/Loki 聚合。
  - 實作 Request ID Middleware，注入 `trace_id` 至所有日誌與回應標頭。
  - 實作 `/health` 端點，支援容器化環境的 Liveness/Readiness Probes。
- [ ] **3.2. 開發環境容器化**
  - 撰寫 `docker-compose.yml` (PostgreSQL)。
  - 確保 `uv` 能正確讀取 `.env` 連接本地 Docker DB。
- [ ] **3.3. 資料庫架構與遷移 (Schema as Code)**
  - 設定 `SQLAlchemy` (Async Engine)。
  - 初始化 **Alembic** 環境。
  - 建立初始 Migration Script (`create_users_table`, `create_chat_logs_table`)。
- [ ] **3.4. 實作 Repository 模式**
  - 建立 `UserRepository` 與 `ChatHistoryRepository`。
  - **DoD**: 撰寫針對 Repository 的整合測試 (Integration Test)。

### Phase 4: DevOps 與自動化 (DevOps & Automation)
- [ ] **4.1. 部署容器化**
  - 撰寫 Multi-stage Build `Dockerfile` (優化 Image 大小)。
- [ ] **4.2. CI/CD Pipeline**
  - 設定 GitHub Actions (Lint, Test, Build)。
- [ ] **4.3. 程式碼品質閘門**
  - 設定 Pre-commit hooks (防止爛 code 進 repo)。

### Phase 5: 多元數據與技術分析強化 (Market Data Evolution)
- [x] **5.1. 數據抽象化 (Data Provider Pattern)**
- [x] **5.2. 引入 Domain Models**
- [ ] **5.3. 支援加密貨幣** (Binance API 實作)
- [x] **5.4. 強化 AI 技術分析邏輯**

### Phase 6: 系統韌性與全方位可觀測性 (Resilience & Full Observability)
- [ ] **6.1. 外部 API 韌性防護**
  - 針對 Yahoo/Gemini API 實作 Retry 機制 (使用 `tenacity`)。
  - 實作 Circuit Breaker (斷路器) 防止連鎖崩潰。
- [ ] **6.2. 效能指標監控 (Metrics)**
  - 整合 Prometheus 監控，記錄 RED 指標 (Requests, Errors, Duration) 與 Token 消耗。
  - 建立 Grafana Dashboard 模板進行視覺化監控。
- [ ] **6.3. 鏈路追蹤 (Tracing)**
  - 導入 OpenTelemetry (OTel) 標準，實現標準化的 Trace 與 Span 管理。
- [ ] **6.4. 主動告警機制 (Alerting)**
  - 整合 Sentry (錯誤追蹤) 或實作 Error Hook 進行即時告警 (Slack/LINE)。

---

## 5. 指令擴展清單 (Planned Commands)
- `.stock [symbol]` - 股市 AI 技術分析
- `.price [symbol]` - 即時報價查詢
- `.chat [message]` - AI 助手對話
- `.help` - 功能說明
- `/weather [city]` - (Future) 天氣預報
- `/news` - (Future) 財經頭條
