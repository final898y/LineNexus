# LineNexus 開發計畫與任務清單 (Project Development Plan)

**版本**: 2.2.0

本文件定義了 LineNexus 的開發路徑。我們採取「MVP 優先，逐步重構」的策略，並堅持「測試與開發並行」的原則。

---

## 1. 開發原則 (Development Principles)

所有開發任務必須遵守以下「完成定義 (Definition of Done, DoD)」：

1.  **功能實作**: 程式碼需符合 PEP 8 風格且通過 ruff 檢查。
2.  **自動化測試**: 
    *   新功能必須包含 Unit Test (單元測試)。
    *   Bug 修復必須包含 Regression Test (回歸測試)。
    *   重構必須確保現有測試全數通過。
3.  **架構一致性**: 遵循 Clean Architecture，確保層級依賴正確。
4.  **可觀測性**: 所有關鍵變更需包含對應的日誌記錄與 Request ID 追蹤。
5.  **文件更新**: 若修改架構或 API 介面，需同步更新 docs/ 下的文檔。

---

## 2. 發展階段

### 第一階段：連通性 (The Connectivity) - 已完成
*   建立與 LINE Platform 的連線 Webhook。

### 第二階段：模組化 (The Modularization) - 已完成
*   建立 Service 層與 Dispatcher，分離處理職責。
*   實作錯誤處理機制。

### 第三階段：AI 工程化基礎建設 (Prompt as Code) - 已完成
*   將 Prompt 與程式碼解耦，建立版本化管理機制。
*   實作 PromptEngine 支援 Jinja2 模板。

### 第四階段：持久化與本地環境標準化 (Persistence & Local Std) - 進行中
*   **4.1. 結構化日誌與基礎可觀測性**:
    *   實作 loguru 的結構化輸出。
    *   實作 Request ID Middleware，將 trace_id 注入日誌與 Response。
    *   確保錯誤回應符合 RFC 7807 規範。
*   **4.2. 資料庫架構 (Schema as Code)**:
    *   設定 SQLAlchemy 並使用 Alembic 管理 Migration。
    *   實作 Repository 模式隔離資料存取。

### 第五階段：DevOps 與自動化 (DevOps & Automation)
*   建立 CI/CD 流水線 (GitHub Actions)。
*   實作容器化部署 (Dockerfile & Docker Compose)。

### 第六階段：系統韌性與全方位可觀測性 (Resilience & Full Observability)
*   **6.1. 穩定性強化**:
    *   針對外部 API 實作 Retry 與 Circuit Breaker。
*   **6.2. 監控與告警**:
    *   整合 Prometheus 監控 RED 指標。
    *   建立主動告警機制。

---

## 3. 任務清單 (Task List)

### 基礎建設
- [x] 實作 Dispatcher 與 Service 體系
- [x] 建立 Prompt 載入與版本化機制
- [x] 實作結構化日誌記錄器
- [ ] 設定 Alembic 遷移環境

### 業務功能
- [x] 股市 AI 技術分析 (StockService)
- [x] 通用 AI 對話 (ChatService)
- [ ] 支援多來源數據 (Crypto/US Stock)

### 工程卓越
- [x] 實作 Domain Models (Pydantic)
- [ ] 設定 GitHub Actions 自動化測試
- [ ] 實作全域異常處理與 RFC 7807 回應格式