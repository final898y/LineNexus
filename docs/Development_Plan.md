# LineNexus 開發計畫與任務清單 (Project Development Plan)

**版本**: 2.3.0

本文件定義了 LineNexus 的開發路徑。我們採取「MVP 優先，逐步重構」的策略，並堅持「測試與開發並行」原則。

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

## 2. 發展階段概覽

1.  **第一階段：連通性 (The Connectivity)**: 建立基礎連線。
2.  **第二階段：模組化 (The Modularization)**: 職責分離與 Service 體系。
3.  **第 2.5 階段：AI 工程化基礎建設 (Prompt as Code)**: Prompt 與程式碼解耦。
4.  **第三階段：持久化與本地環境標準化 (Persistence & Local Std)**: 資料庫與 Repository 模式。
5.  **第四階段：DevOps 與自動化 (DevOps & Automation)**: CI/CD 與容器化。
6.  **第五階段：多元數據與技術分析強化 (Market Data Evolution)**: 指標豐富化與流派分析。
7.  **第六階段：系統韌性與全方位可觀測性 (Resilience & Full Observability)**: 穩定性與監控。

---

## 3. 詳細任務清單 (Detailed Task List)

### Phase 1: 基礎連通與 MVP 骨架
- [x] 1.1. 建立基礎 Webhook 與 LINE 平台連通
- [x] 1.2. 實作簡易指令解析邏輯 (Prefix-based)
- [x] 1.3. 串接 Stock 最小可行性產品流程

### Phase 2: 指令分發器與服務模組化
- [x] 2.1. 重構 Dispatcher 實作動態路由
- [x] 2.2. 建立 Service 體系 (Stock, Chat, Help)
- [x] 2.3. 增強全域錯誤處理機制
- [x] 2.4. 導入靜態型別強化 (Mypy Strict mode)

### Phase 2.5: AI 工程化基礎建設 (Prompt as Code)
- [x] 2.5.1. 建立 Prompt Loader 機制支援外部檔案
- [x] 2.5.2. 外部化 Markdown Prompt 管理
- [x] 2.5.3. 實作 Prompt 版本化追蹤機制
- [x] 2.5.4. 建立針對 Prompt 渲染的單元測試

### Phase 3: 持久化與本地環境標準化
- [x] 3.1. 實作結構化日誌與基礎可觀測性 (Loguru + Request ID)
- [x] 3.2. 導入 Domain Models (Pydantic 模型定義)
- [ ] 3.3. 開發環境容器化 (Docker Compose - PostgreSQL)
- [ ] 3.4. 資料庫架構與遷移管理 (SQLAlchemy + Alembic)
- [ ] 3.5. 實作 Repository 模式隔離資料存取層

### Phase 4: DevOps 與自動化
- [ ] 4.1. 撰寫 Multi-stage Dockerfile 進行部署優化
- [ ] 4.2. 建立 GitHub Actions CI 流水線 (Lint, Test, Type Check)
- [ ] 4.3. 設定 Pre-commit hooks 品質閘門

### Phase 5: 多元數據與技術分析強化 (Market Data Evolution)
- [x] 5.1. 實作數據抽象化介面 (Data Provider Pattern)
- [ ] 5.2. 支援加密貨幣數據源 (Binance API)
- [ ] 5.3. 支援美股數據源 (Yahoo Finance 擴展)
- [x] 5.4. 強化 AI 技術分析 Prompt 邏輯
- [x] 5.5. 實作技術指標計算核心 (TechnicalAnalysisService)
- [x] 5.6. 擴展領域模型以支援富集數據 (Enriched Stock Data Models)
- [x] 5.7. 實作多流派分流分析邏輯 (Multi-strategy Prompting)

### Phase 6: 系統韌性與全方位可觀測性
- [ ] 6.1. 實作外部 API Retry 與 Circuit Breaker (Tenacity)
- [ ] 6.2. 實作全域異常處理並符合 RFC 7807 規範
- [ ] 6.3. 整合 Prometheus RED 指標監控
- [ ] 6.4. 導入 OpenTelemetry 鏈路追蹤 (Tracing)

---

## 4. 指令擴展清單 (Planned Commands)
- .stock [symbol] [strategy] - 股市 AI 分析 (strategy: trend, momentum, general)
- .price [symbol] - 即時報價查詢
- .chat [message] - AI 助手對話
- .help - 功能說明