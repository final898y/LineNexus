# 📘 Git 專案協作規範

本文件定義了本專案的 Git 工作流程、分支策略、Commit 準則與協作規範。
目標是確保專案在人類開發者與 **AI Agent** 協作時，代碼庫保持乾淨、可追溯且符合標準。

---

## 1. 🤖 AI Agent 操作指引 (AI-Specific Guidelines)

**AI Agent 在執行任何 Git 操作前，必須嚴格遵守以下流程，以確保變更內容的正確性。**

### 1.1. 提交前的確認 (Pre-Commit Check)
AI Agent **不能**僅依賴記憶或假設來撰寫 Commit Message，必須實際檢查檔案變更。

1.  **檢查狀態**: 執行 `git status` 確認哪些檔案被修改。
2.  **暫存變更**: 執行 `git add <file>` 或 `git add .`。
3.  **檢查差異 (關鍵步驟)**:
    *   執行 `git diff --staged` (或 `git diff --cached`)。
    *   **必須讀取並分析** diff 的輸出內容，確認變更邏輯與預期相符。
4.  **生成訊息**: 根據 diff 的內容，撰寫符合 Conventional Commits 規範的訊息（包含細項清單）。

### 1.2. 禁止行為
*   🚫 **禁止推測**: 不要在未執行 `git diff` 的情況下直接 Commit。
*   🚫 **禁止盲目推送**: 除非使用者明確要求，否則不要自動執行 `git push`。
*   🚫 **禁止提交機密**: 嚴格檢查是否包含 `.env` 或 API Key。

---

## 2. 🌿 分支策略 (Branching Strategy)

本專案採用簡化的 Git Flow 策略。

*   **main**: 正式發布分支。
*   **develop**: 日常開發主幹。
*   **feature/***: 新功能開發。
*   **bugfix/***: 一般錯誤修復。
*   **hotfix/***: 緊急修復線上問題。

---

## 3. 📝 Commit Message 規範

Commit Message 應包含清晰的主旨與詳細的變更清單。

### 3.1. 訊息格式 (Message Format)

```text
<type>(<scope>): <subject>

- 變更細項說明 1
- 變更細項說明 2
- 修正了某某邏輯
```

*   **主旨 (Subject)**: 簡短描述變更核心內容，不加句號。
*   **內容 (Body)**: **強烈建議使用清單符號 `-`**。當變更包含多個檔案或邏輯調整時，必須列出細項說明，並與主旨之間保留一格空行。

### 3.2. Type 類別說明與範例

*   **feat**: 新增功能 (New Feature)
    *   範例:
        ```text
        feat(api): 實作股票查詢介面

        - 新增 /callback Webhook 端點
        - 整合 yfinance 資料抓取邏輯
        - 加入初步的錯誤處理機制
        ```
*   **fix**: 修補 Bug (Bug Fix)
    *   範例:
        ```text
        fix(parser): 修正代碼解析溢位問題

        - 調整正規表達式以支援多位數代碼
        - 修正 null 值處理不當導致的崩潰
        ```
*   **docs**: 僅修改文件 (Documentation)
*   **style**: 格式調整 (空白、縮排、分號，不影響運作)
*   **refactor**: 重構程式碼 (無新增功能或修復 Bug)
*   **perf**: 效能優化
*   **test**: 增加或修改測試
*   **build/ci**: 影響建置或 CI/CD 流程
*   **chore**: 其他雜項 (更新 .gitignore 等)

---

## 4. 🔄 開發工作流程 (Workflow)

### 4.1. 提交變更步驟
1.  `git add .`
2.  **確認變更 (AI 必做)**: `git diff --staged`
3.  **撰寫並提交**: `git commit` (確保包含 `-` 開頭的細項說明)

---

## 5. 🚫 忽略檔案設定 (.gitignore)

*   **安全性**: `.env`, `*.key`
*   **環境**: `venv/`, `.venv/`
*   **快取**: `__pycache__/`, `*.pyc`
*   **日誌**: `logs/`, `*.log`

---

## 6. 🚀 Git Cheat Sheet

*   **查看狀態**: `git status`
*   **查看暫存差異**: `git diff --staged`
*   **檢視歷史**: `git log --oneline -n 5`
