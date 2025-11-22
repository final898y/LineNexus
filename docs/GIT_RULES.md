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

格式：

    <type>: <描述>

常用 type： - feat - fix - docs - refactor - style - test - chore

範例：

    feat: 新增使用者登入 API
    fix: 修正 JWT 過期判定錯誤
    docs: 更新 README 的啟動流程

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
