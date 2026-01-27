# LineNexus 開發計畫與任務清單 (Project Development Plan)

本文件定義了 **LineNexus | AI 指令樞紐** 的開發路徑。我們採取 **「MVP 優先，逐步重構」** 的策略：先完成端到端的指令流程，確保功能運作，再逐步導入乾淨架構 (Clean Architecture) 以提升擴展性。

---

## 1. MVP 資料流程 (MVP Data Flow)

在第一階段，我們追求最簡捷的路徑，讓指令能正確觸發 AI：

1.  **接收 (Webhook)**: `main.py` 接收 LINE 傳來的文字訊息。
2.  **解析 (Dispatcher)**: 透過簡單的文字處理 (如 `startswith("/")`) 判斷指令類型。
3.  **執行 (Services)**:
    *   若是 `/stock`：抓取數據 -> 丟給 Gemini -> 取得建議。
    *   若是 `/chat`：直接丟給 Gemini 進行對話。
4.  **回傳 (Line API)**: 將結果透過 `line-bot-sdk` 推播回使用者。

---

## 2. 開發策略：從實作到重構 (Evolutionary Strategy)

*   **第一階段：連通性 (The Connectivity)**
    *   目標：讓 LINE 傳送 `/stock 2330` 後，能收到 AI 的回覆。
    *   重點：快速整合 `yfinance` 與 `Gemini API`，不糾結層次結構。
*   **第二階段：結構化 (The Refactoring)**
    *   目標：將邏輯從 `main.py` 移出，建立 `Dispatcher` 與 `services/` 模組。
    *   重點：定義 `BaseService` 抽象介面，實現「外掛式」擴展功能。
*   **第三階段：健壯化 (The Robustness)**
    *   目標：增加錯誤處理、結構化日誌與資料庫紀錄。
    *   重點：引入 PostgreSQL 儲存對話紀錄，並撰寫 Pytest 測試。

---

## 3. 任務清單 (Task List)

### Phase 1: 基礎連通與 MVP 骨架 (Hello LineNexus)
- [x] **1.1. 建立基礎 Webhook**
  - 實作 `/callback` 路由，能接收並原樣回傳 (Echo) 使用者訊息。
  - 使用 `ngrok` 完成本地與 LINE Platform 的連通。
- [x] **1.2. 實作簡易指令解析**
  - 在 `main.py` 中撰寫簡單判斷，區分「指令文字」與「一般文字」。
- [x] **1.3. 串接 Stock MVP 流程**
  - 整合 `yfinance` 獲取數據。
  - 整合 `Gemini API` (google-genai) 進行簡單分析。
  - 確保 `/stock [代碼]` 能成功回傳。

### Phase 2: 指令分發器與服務模組化 (The Hub Architecture)
- [ ] **2.1. 重構 Dispatcher**
  - 建立 `src/lineaihelper/dispatcher.py`。
  - 將指令解析邏輯封裝進 Dispatcher。
- [ ] **2.2. 建立 Service 體系**
  - 建立 `src/lineaihelper/services/` 資料夾。
  - 實作 `stock_service.py` 與 `chat_service.py`。
  - 實作 `/help` 指令服務。

### Phase 3: 資料持久化與日誌 (Persistence & Logging)
- [ ] **3.1. 結構化日誌導入**
  - 使用 `loguru` 記錄每個指令的處理時長與結果。
- [ ] **3.2. 資料庫設定 (PostgreSQL)**
  - 建立對話紀錄與使用者偏好設定的資料表。
  - 實作 Repository 模式進行資料存取。

### Phase 4: 品質優化與自動化測試 (Quality Assurance)
- [ ] **4.1. 錯誤處理強化**
  - 針對 API 逾時、無效股票代碼等異常情況回傳友善提示。
- [ ] **4.2. 撰寫整合測試**
  - 使用 `pytest` 測試 Dispatcher 的分發邏輯是否正確。
- [ ] **4.3. 部署準備**
  - 撰寫 `Dockerfile` 與環境變數檢核機制。

---

## 4. 指令擴展清單 (Planned Commands)
- `/stock [symbol]` - (MVP) 股市分析
- `/chat [message]` - (MVP) AI 聊天
- `/help` - (MVP) 功能說明
- `/weather [city]` - (Future) 天氣預報
- `/news` - (Future) 財經頭條