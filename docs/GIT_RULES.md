# Git 專案協作規範

本文件定義了本專案的 Git 工作流程、分支策略、Commit 準則與協作規範。目標是確保專案在人類開發者與 AI Agent 協作時，代碼庫保持乾淨、可追溯且符合標準。

---

## 1. AI Agent 操作指引 (AI-Specific Guidelines)

AI Agent 在執行任何 Git 操作前，必須嚴格遵守以下流程，以確保變更內容的正確性。

### 1.1. 提交前的標準作業程序 (Pre-Commit SOP)
AI Agent 不能僅依賴記憶或假設來撰寫 Commit Message，必須實際檢查檔案變更。

1.  **檢查狀態**: 執行 `git status` 確認哪些檔案被修改。
2.  **暫存變更**: 執行 `git add <file>`。
3.  **檢查差異 (關鍵步驟)**:
    *   必須執行 `git diff --staged` (或 `git diff --cached`) 並詳讀內容。
    *   必須確認變更邏輯正確，且無誤刪程式碼、遺留除錯語句或包含機密資訊。
4.  **生成訊息**: 根據實際變更內容，撰寫符合 Conventional Commits 規範的訊息。

### 1.2. 禁止行為
*   禁止推測: 不要在未執行 `git diff` 的情況下直接提交。
*   禁止盲目推送: 除非使用者明確要求，否則不要自動執行 `git push`。
*   禁止提交機密: 嚴格檢查是否包含 .env 或 API Key。

---

## 2. 分支策略 (Branching Strategy)

本專案採用簡化的 Git Flow 策略。

*   **main**: 正式發布分支。
*   **develop**: 日常開發主幹。
*   **feature/**: 新功能開發。
*   **bugfix/**: 一般錯誤修復。
*   **hotfix/**: 緊急修復線上問題。

---

## 3. Commit Message 規範

Commit Message 應包含清晰的主旨與詳細的變更清單。遵循 `<type>(<scope>): <subject>` 格式。

### 3.1. 訊息格式 (Message Format)

```text
<type>(<scope>): <subject>

- 變更細項說明 1
- 變更細項說明 2
- 修正了某某邏輯
```

*   **主旨 (Subject)**: 簡短描述變更核心內容，不加句號。
*   **內容 (Body)**: 強烈建議使用清單符號 `-`。當變更包含多個檔案或邏輯調整時，必須列出細項說明，並與主旨之間保留一格空行。

### 3.2. Type 類別說明

*   **feat**: 新增功能 (New Feature)
*   **fix**: 修補 Bug (Bug Fix)
*   **docs**: 僅修改文件 (Documentation)
*   **style**: 格式調整 (空白、縮排、不影響運作)
*   **refactor**: 重構程式碼 (無新增功能或修復 Bug)
*   **perf**: 效能優化
*   **test**: 增加或修改測試
*   **build/ci**: 影響建置或 CI/CD 流程
*   **chore**: 其他雜項 (更新 .gitignore 等)

---

## 4. 忽略檔案設定 (.gitignore)

*   **安全性**: .env, *.key
*   **環境**: venv/, .venv/
*   **快取**: __pycache__/, *.pyc
*   **日誌**: logs/, *.log