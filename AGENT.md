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

### ✅ 推薦的工具與指令

*   **套件管理**: `uv` (例如 `uv run`, `uv add`, `uv sync`)。
*   **Linter/Formatter**: `ruff` (嚴格遵守 `ruff.toml`)。
*   **Log**: 使用 `loguru`，禁止使用 `print()`。
*   **Test**: 使用 `pytest`，測試檔案位於 `tests/`。