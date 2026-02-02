# Agent 行為規範 (AGENT.md)

本文件定義了 AI Agent 在本專案中互動與執行任務時必須遵守的規範。

## 1. 語言與認知

*   **輸出語言**: 必須使用 **繁體中文 (Traditional Chinese)** 回覆。
*   **專業術語**: 專有名詞（如 `FastAPI`, `Pytest`, `Loguru`）應保留英文，必要時可加註中文說明。
*   **檔案可見性 (File Visibility)**:
    *   Agent 的搜尋與列表工具預設會**忽略** `.gitignore` 中的檔案（如 `.env`, `venv/`, `logs/`）。
    *   若需操作這些檔案，必須**直接指定完整路徑**進行讀取或寫入，無法透過全域搜尋找到它們。

## 2. Git 操作規範 (Git Operations)

本專案由人類與 AI 協作，Agent 必須嚴格執行以下流程以確保代碼庫的乾淨與可追溯性。

### 2.1. 提交前的 SOP (Pre-Commit)
1.  **加入暫存**: `git add <file>`。
2.  **強制檢查差異**: **必須**執行 `git diff --staged`。
    *   ❌ 禁止盲目 Commit。
    *   ✅ 必須讀取 diff 內容，確認變更邏輯正確且無誤刪。
3.  **提交 (Commit)**:
    *   使用 `git commit`。
    *   若變更內容複雜，**必須**包含細項說明清單。

### 2.2. Commit Message 格式
遵循 `<type>(<scope>): <subject>` 格式，並使用 `-` 列出細項。

*   **CLI 技巧**: 在 PowerShell 中若要輸入多行 Commit Message，可使用多個 `-m` 參數：
    ```powershell
    git commit -m "feat(api): 實作股票查詢功能" -m "- 新增 Webhook 端點" -m "- 整合 yfinance"
    ```

## 3. 環境與指令規範 (Windows PowerShell)

本專案運行於 **Windows (win32)** 環境，預設 Shell 為 **PowerShell (pwsh)**。

### ⚠️ 禁止使用的語法

*   **禁止使用 `&&` 連接指令**: PowerShell 不支援。
    *   ❌ 錯誤: `cd src && python main.py`
    *   ✅ 正確: 分次執行，或使用分號 `cd src; python main.py`

*   **環境變數設定**:
    *   ❌ 錯誤: `export VAR=1`
    *   ✅ 正確: `$env:VAR="1"`

## 4. 業界標準與工程卓越 (Engineering Excellence)

Agent 在進行系統設計與開發時，必須遵循以下業界標準：

### 4.1. 架構與設計原則
*   **Clean Architecture**: 嚴格分離領域邏輯 (Domain)、應用邏輯 (Service) 與外部介面 (API/Provider)。
*   **SOLID 原則**: 特別注意單一職責 (SRP) 與開閉原則 (OCP)，確保功能擴展時不需大規模修改現有代碼。
*   **DRY & KISS**: 保持代碼簡潔且不重複，避免過度工程化 (Over-engineering)。

### 4.2. 資安規範 (Security Standards)
*   **機敏資訊防護**: 嚴禁在代碼或 Log 中洩漏 API Key、Token 或使用者個資。所有金鑰必須透過 `$env:VAR` 或 `.env` 注入。
*   **輸入驗證 (Input Validation)**: 對於所有外部輸入（來自 LINE 或 API）必須進行嚴格的型別檢查與合法性驗證，防止注入攻擊。
*   **相依性安全**: 引入新套件前需確認其必要性與安全性，優先使用專案已建立的生態系 (如 `uv`, `fastapi`, `pydantic`)。

## 5. 開發與驗證強制流程 (Mandatory Workflow)

Agent 在完成任何功能開發或重構後，**必須自動執行**以下驗證流程，不得僅憑直覺判斷：

1.  **實作 (Implement)**: 根據需求撰寫程式碼與**對應的測試案例**。
2.  **單元測試 (Test)**: 執行 `uv run pytest` (或 `uv run test`)，確保新舊功能皆通過。
3.  **品質檢查 (Lint)**: 執行 `uv run ruff check . --fix` (或 `uv run lint`)，修復風格問題。
4.  **型別檢查 (Type Check)**: 執行 `uv run mypy .` (或 `uv run type-check`)，確保型別安全。
5.  **提交驗證 (Commit)**: 按照 Git SOP 進行提交。

---

## 6. 指令快捷鍵與快捷腳本 (Scripts)

為了提高效率，請優先使用 `pyproject.toml` 中定義的腳本：
*   `uv run dev`: 啟動開發伺服器。
*   `uv run test`: 執行所有測試。
*   `uv run lint`: 執行代碼檢查。
*   `uv run format`: 執行自動格式化。
*   `uv run type-check`: 執行靜態型別檢查。