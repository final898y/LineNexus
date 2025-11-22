# 📘 Git 專案規範（Side Project 專用）

> 本文件提供此專案的 Git 工作流程、分支規範、Commit 準則、PR
> 流程與常見注意事項。\
> 目標是讓專案在多人或長期維護時保持乾淨、可讀、易於協作。

## 1. 🧭 工作流程（每日操作指引）

### ✔️ 開始工作前

    git checkout develop
    git pull origin develop

### ✔️ 開新功能分支

    git checkout -b feature/功能名稱

### ✔️ 提交 Commit

    git add .
    git commit -m "feat: 新增登入 API"

### ✔️ 推送到遠端

    git push origin feature/功能名稱

### ✔️ 發 PR（Pull Request）

在 GitHub / GitLab 建立 PR → 指向 `develop`。

## 2. 🌿 分支策略

    main       → 正式版（部署）
    develop    → 日常開發主線
    feature/*  → 新功能
    bugfix/*   → 修 bug
    hotfix/*   → 緊急修正式機問題

## 3. 📝 Commit Message 規範

Commit Message 格式應為：`<type>(<scope>): <subject>`

- `<type>`: Commit 的類型。
- `<scope>`: (可選) 本次 Commit 影響的範圍，例如模組、功能名稱。
- `<subject>`: 簡潔地描述本次 Commit 的內容，祈使句開頭，不需句點。

### Type 類別說明

| Type       | 說明                                                               | 範例                                           |
| :--------- | :----------------------------------------------------------------- | :--------------------------------------------- |
| `feat`     | 新增功能 (A new feature)                                           | `feat(api): 新增使用者登入 API`                |
| `fix`      | 修正錯誤 (A bug fix)                                               | `fix(auth): 修正 JWT 過期判定錯誤`             |
| `docs`     | 只修改文件 (Documentation only changes)                            | `docs: 更新 README 的專案啟動說明`             |
| `style`    | 不影響程式碼運作的調整 (例如空白、格式、補分號)                    | `style: 調整程式碼排版與多餘的空白`            |
| `refactor` | 重構程式碼，沒有新增功能或修正錯誤                               | `refactor: 重構使用者認證模組`                 |
| `perf`     | 改善效能的調整 (A code change that improves performance)           | `perf(db): 優化使用者查詢的 SQL 語句`           |
| `test`     | 新增或修改測試                                                   | `test: 增加登入功能的單元測試`                 |
| `build`    | 影響建置系統或外部依賴的變更 (例如 pip, poetry) | `build: 升級 FastAPI 版本至 0.100.0`           |
| `ci`       | 修改 CI 設定檔或腳本 (例如 GitHub Actions)                         | `ci: 修正部署腳本中的環境變數`                 |
| `chore`    | 其他不修改 `src` 或 `test` 的變更 (例如更新 `.gitignore`)           | `chore: 在 .gitignore 新增 log 檔案的忽略規則` |

## 4. 🔀 Pull Request（PR）規範

PR Template：

    ## Summary
    ## Changes
    ## Test
    ## Others

原則： - 小 PR（150 行內） - 自我檢查一次再送審

## 5. 🚫 .gitignore（Python + FastAPI）

    __pycache__/
    *.py[cod]
    venv/
    .venv/
    .env
    .DS_Store
    *.log
    .vscode/
    .idea/
    *.sqlite3
    .pytest_cache/
    .coverage
    htmlcov/
    build/
    dist/
    *.egg-info/
    poetry.lock
    uv.lock
    .uv/

## 6. ⚠️ 常見注意事項

-   不要 commit `.env`
-   不要 commit venv
-   不要在 `main` 開發
-   避免巨型 commit / 巨型 PR

## 7. 🚀 Git Cheat Sheet

    git checkout develop
    git pull
    git checkout -b feature/x
    git add .
    git commit -m "feat: xxx"
    git push origin feature/x
