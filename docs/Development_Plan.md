# LineNexus 開發計畫與任務清單 (Project Development Plan)

本文件定義了 **LineNexus | AI 指令樞紐** 的開發路徑。我們採取 **「MVP 優先，逐步重構」** 的策略，但堅持 **「測試與開發並行」** 的原則，確保系統在演進過程中始終維持高品質。

---

## 1. 開發原則 (Development Principles) - *Updated*

為了確保程式碼品質與可維護性，所有開發任務必須遵守以下 **Definition of Done (DoD)**：

1.  **功能實作 (Implementation)**: 程式碼需符合 PEP 8 風格規範 (透過 `ruff` 檢查)。
2.  **同步測試 (Tests Included)**: 
    *   **新功能**: 必須包含對應的 Unit Test (單元測試)。
    *   **Bug 修復**: 必須包含能重現該 Bug 的測試案例 (Regression Test)。
    *   **重構**: 必須確保現有測試全數通過 (Green)。
3.  **文件更新 (Documentation)**: 若修改了架構或指令用法，需同步更新 `README.md` 或 API 文件。

---

## 2. MVP 資料流程 (MVP Data Flow)

1.  **接收 (Webhook)**: `main.py` 接收 LINE 傳來的文字訊息。
2.  **解析 (Dispatcher)**: 透過簡單的文字處理 (如 `startswith("/")`) 判斷指令類型。
3.  **分發 (Services)**: 透過 `CommandDispatcher` 將請求分派給具體的 `Service` 類別。
4.  **執行 (Domain Logic)**:
    *   `StockService`: 抓取 `yfinance` 數據 -> 丟給 Gemini -> 取得建議。
    *   `ChatService`: 直接丟給 Gemini 進行對話。
5.  **回傳 (Line API)**: 將結果透過 `line-bot-sdk` 推播回使用者。

---

## 3. 開發策略：從實作到重構 (Evolutionary Strategy)

*   **第一階段：連通性 (The Connectivity)** - *Completed*
    *   目標：建立與 LINE Platform 的連線，完成 Hello World。
*   **第二階段：模組化 (The Modularization)** - *Current*
    *   目標：建立 Service 層與 Dispatcher，分離職責。
    *   重點：確保每個 Service 都有獨立的單元測試。
*   **第三階段：持久化 (The Persistence)**
    *   目標：引入資料庫 (PostgreSQL)，記錄對話與使用者狀態。
    *   重點：使用 Repository Pattern 隔離資料庫操作，方便測試 Mock。
*   **第四階段：部署與維運 (Deployment & Ops)**
    *   目標：容器化與 CI/CD 自動化。

---

## 4. 任務清單 (Task List)

### Phase 1: 基礎連通與 MVP 骨架 (Hello LineNexus)
- [x] **1.1. 建立基礎 Webhook**
  - 實作 `/callback` 路由，能接收並原樣回傳 (Echo) 使用者訊息。
- [x] **1.2. 實作簡易指令解析**
  - 在 `main.py` 中撰寫簡單判斷。
- [x] **1.3. 串接 Stock MVP 流程**
  - 整合 `yfinance` 與 `Gemini API`。

### Phase 2: 指令分發器與服務模組化 (The Hub Architecture)
- [x] **2.1. 重構 Dispatcher**
  - 建立 `src/lineaihelper/dispatcher.py`。
- [x] **2.2. 建立 Service 體系**
  - 建立 `src/lineaihelper/services/` (Base, Stock, Chat, Help)。
  - **DoD**: 完成對應的 Unit Tests (`tests/services/`).
- [ ] **2.3. 增強錯誤處理機制**
  - 在 Service 層統一捕捉 Exception 並回傳友善錯誤訊息。
  - **DoD**: 增加測試案例模擬 API 失敗的情境。

### Phase 3: 資料持久化與日誌 (Persistence & Logging)
- [ ] **3.1. 結構化日誌導入**
  - 使用 `loguru` 取代 print，並設定 log rotation。
- [ ] **3.2. 資料庫環境準備**
  - 設定 PostgreSQL (Local or Docker)。
  - 設定 `SQLAlchemy` 或 `Tortoise-ORM` (非同步優先)。
- [ ] **3.3. 實作 Repository 模式**
  - 建立 `UserRepository` 與 `ChatHistoryRepository`。
  - **DoD**: 撰寫針對 Repository 的整合測試 (使用 TestContainer 或 SQLite 記憶體資料庫)。

### Phase 4: 部署與維運 (Deployment & Ops)
- [ ] **4.1. 容器化**
  - 撰寫 `Dockerfile` 與 `.dockerignore`。
- [ ] **4.2. CI/CD Pipeline**
  - 設定 GitHub Actions。
  - 自動執行 `uv run ruff check` 與 `uv run pytest`。
- [ ] **4.3. 生產環境配置**
  - 確保 API Key 等敏感資訊透過環境變數注入。

---

## 5. 指令擴展清單 (Planned Commands)
- `/stock [symbol]` - (MVP) 股市分析
- `/chat [message]` - (MVP) AI 聊天
- `/help` - (MVP) 功能說明
- `/weather [city]` - (Future) 天氣預報
- `/news` - (Future) 財經頭條
