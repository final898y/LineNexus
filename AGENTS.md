# Agent 行為規範 (AGENTS.md)

本文件定義了 AI Agent 在本專案中互動與執行任務時必須遵守的規範，旨在確保代碼品質達到企業級工程標準。

## 1. 語言與認知

*   **輸出語言**: 必須使用 **繁體中文 (Traditional Chinese)** 回覆。
*   **專業術語**: 專有名詞（如 FastAPI, Pytest, Loguru）應保留英文，必要時可加註中文說明。
*   **檔案可見性 (File Visibility)**:
    *   Agent 的搜尋與列表工具預設會忽略 .gitignore 中的檔案。
    *   若需操作這些檔案，必須直接指定完整路徑進行讀取或寫入。

## 2. Git 操作規範 (Git Operations)

Agent 必須嚴格執行以下流程，以確保代碼庫的可追溯性與整潔。

### 2.1. 提交前的標準作業程序 (Pre-Commit SOP)
1.  **加入暫存**: 執行 `git add <file>`。
2.  **強制檢查差異**: 必須執行 `git diff --staged` 並詳讀內容。
    *   禁止盲目提交。
    *   必須確認變更邏輯正確，且無誤刪程式碼或遺留除錯語句。
3.  **提交 (Commit)**:
    *   使用 `git commit`。
    *   變更內容若涉及多個模組，必須在提交訊息中包含細項說明清單。

### 2.2. Commit Message 格式
遵循 `<type>(<scope>): <subject>` 格式，並使用 `-` 列出細項。
類型包括：feat, fix, refactor, docs, test, chore, style。

## 3. 環境與指令規範 (Windows PowerShell)

本專案運行於 Windows (win32) 環境，預設 Shell 為 PowerShell (pwsh)。

### 指令語法限制

*   **連接指令**: PowerShell 不支援 `&&`。
    *   錯誤範例: `cd src && python main.py`
    *   正確範例: `cd src; python main.py`
*   **環境變數設定**:
    *   錯誤範例: `export VAR=1`
    *   正確範例: `$env:VAR="1"`

## 4. 業界標準與工程卓越 (Engineering Excellence)

### 4.1. 架構與設計原則
*   **Clean Architecture**: 嚴格分離 Domain、Service 與 Interface (API/Provider) 層次。
*   **SOLID 原則**: 特別注重單一職責 (SRP) 與開閉原則 (OCP)。
*   **DRY & KISS**: 避免過度工程化，保持代碼簡潔且不重複。

### 4.2. API 版本控制 (API Versioning)
*   **版本定義方式**: 採用 URL 版本化，例如 `/api/v1/resource`。
*   **相容性規範**: 
    *   任何破壞性變更 (Breaking Changes) 必須升級主版本號 (Major Version)。
    *   舊版本 API 應保留一段時間的相容性，並在文檔中標註 `Deprecated`。
*   **語意化版本 (SemVer)**: 內部邏輯變更遵循主版本.次版本.修訂版規範。

### 4.3. 錯誤處理與可觀測性 (Error Handling & Observability)
*   **結構化日誌**: 使用 `loguru` 並透過 `logger.bind()` 注入 Context (如 Request ID, User ID)。
*   **異常體系**: 禁止直接使用廣義 `Exception`。必須根據業務邏輯定義具備語意化的自定義異常類。
*   **優雅失敗**: API 必須捕捉所有未處理異常，並回傳符合 RFC 7807 規範的標準化錯誤回應。

### 4.4. 資安規範 (Security Standards)
*   **機敏資訊**: 嚴禁將 API Key 或 Token 寫入代碼或日誌。所有金鑰必須透過環境變數注入。
*   **輸入驗證**: 對所有外部輸入執行嚴格的型別檢查與合法性驗證 (使用 Pydantic 等工具)。

### 4.5. 測試策略 (Testing Strategy)
*   **測試金字塔**:
    *   Unit Tests: 測試單一函式與 Domain Logic，必須 Mock 外部依賴。
    *   Integration Tests: 測試 Service 與資料庫或外部 API 的整合行為。
*   **AAA 模式**: 測試案例應清晰劃分 Arrange, Act, Assert 三個階段。

### 4.6. 文件同步 (Documentation as Code)
*   **即時更新**: 任何架構或 API 變更，必須同步更新 `docs/` 下的對應文檔。
*   **代碼註釋**: 使用 Google Style Python Docstrings 規範所有公開類別與函式。

## 5. 開發與驗證強制流程 (Mandatory Workflow)

完成開發或重構後，必須依序執行以下流程：

1.  **實作 (Implement)**: 撰寫程式碼與對應的測試案例。
2.  **單元測試 (Test)**: 執行 `uv run test`。
3.  **品質檢查 (Lint)**: 執行 `uv run lint`。
4.  **型別檢查 (Type Check)**: 執行 `uv run type-check`。
5.  **提交驗證 (Commit)**: 按照 Git SOP 進行提交。

## 6. 指令快捷腳本 (Scripts)

優先使用 `pyproject.toml` 中定義的腳本：
*   `uv run dev`: 啟動開發伺服器。
*   `uv run test`: 執行所有測試。
*   `uv run lint`: 執行代碼檢查。
*   `uv run format`: 執行自動格式化。
*   `uv run type-check`: 執行靜態型別檢查。
