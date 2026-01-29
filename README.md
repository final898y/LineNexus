# LineNexus | AI 指令樞紐

本專案是一個基於 LINE 聊天機器人的 AI 多功能助手。採用指令式 (Command-based) 架構與 **Clean Architecture** 概念，使用者可以透過特定指令進行台股分析、AI 聊天或其他擴展功能。

---

## 🚀 專案核心架構

本專案引入 **Dispatcher (分發器)** 與 **Service (服務層)** 模式，確保功能模組化且易於測試與擴展。

```mermaid
graph TD
    A[使用者] -- 傳送指令 e.g., /stock 2330 --> B(LINE App)
    B -- Webhook --> C{後端伺服器 (FastAPI)}
    C -- 1. 簽章驗證 & 全域異常攔截 --> C
    C -- 2. 指令分發 --> D[CommandDispatcher]
    D -- 3. 業務異常攔截 ⚠️/❌ --> D
    D -- 4. 呼叫 Service --> E{功能模組 Services}
    E -- /stock --> E1[StockService]
    E -- /chat --> E2[ChatService]
    E -- /help --> E3[HelpService]
    E1 -- 抓取數據 --> F[Yahoo Finance]
    E1 -- AI 分析 --> G[Google Gemini]
    E2 -- AI 對話 --> G
    C -- 5. 回傳訊息 --> H[LINE Messaging API]
    H -- 推播訊息 --> B
    B -- 顯示結果 --> A
```

### 架構特色

*   **指令分發器 (Dispatcher)**: 負責解析指令標籤，並統一處理業務異常 (Business Logic Exceptions)。
*   **服務層 (Services)**: 每個功能模組獨立運作，強制實作 `BaseService` 介面。
*   **雙層異常處理**:
    *   **系統層 (FastAPI)**: 攔截 500/400 錯誤，確保 HTTP 狀態碼正確。
    *   **業務層 (Dispatcher)**: 攔截邏輯錯誤（如配額不足、找不到代碼），回傳友善的 `⚠️` 或 `❌` 提示。

---

## 🛠️ 技術棧 (Technology Stack)

*   **Runtime**: Python 3.12+
*   **Web Framework**: FastAPI
*   **Package Manager**: `uv` (高效能替代 pip/poetry)
*   **Static Analysis**: `ruff` (Linter/Formatter), `mypy` (Static Type Checker)
*   **Logging**: `loguru`
*   **Testing**: `pytest` (搭配 `pytest-asyncio` & `anyio`)

---

## 📦 環境設置

1.  **環境管理**
    本專案使用 `uv` 進行管理，請確保已安裝 `uv`。
    ```bash
    uv venv
    uv sync
    ```

2.  **設定環境變數**
    複製 `.env.example` 並填入金鑰：
    ```ini
    LINE_CHANNEL_ACCESS_TOKEN="YOUR_TOKEN"
    LINE_CHANNEL_SECRET="YOUR_SECRET"
    GEMINI_API_KEY="YOUR_KEY"
    ```

---

## 🧪 品質保證 (QA)

我們堅持 **測試與開發並行 (DoD)** 的原則。

*   **執行所有測試**
    ```bash
    uv run pytest
    ```
*   **程式碼風格檢查 (Lint)**
    ```bash
    uv run ruff check .
    ```
*   **靜態型別檢查 (Type Check)**
    ```bash
    uv run mypy .
    ```

---

## 📁 專案結構 (Project Structure)

```text
LineAiHelper/
├── docs/                   # 研發計畫與設計文件
├── src/lineaihelper/
│   ├── main.py             # 進入點、Lifespan 與全域異常攔截
│   ├── dispatcher.py       # 指令分發與業務異常轉換
│   ├── exceptions.py       # 自定義業務異常類別
│   ├── services/           # 功能模組
│   │   ├── __init__.py     # 服務匯出控制
│   │   ├── base_service.py # 抽象基礎類別
│   │   ├── stock_service.py
│   │   └── chat_service.py
│   └── config.py           # Pydantic Settings
├── tests/                  # 測試架構
│   ├── services/           # 針對各模組的單元測試
│   └── test_dispatcher.py  # 路由與分發測試
├── mypy.ini                # Mypy 設定 (含 Pydantic 插件)
├── ruff.toml               # Ruff 風格設定
└── pyproject.toml          # 專案依賴管理
```

## ⌨️ 指令互動

| 指令 | 說明 | 範例 |
| :--- | :--- | :--- |
| `/stock [代碼]` | 股市分析與 AI 投資見解 | `/stock 2330` |
| `/chat [訊息]` | AI 一般性對話 | `/chat 今天天氣如何？` |
| `/help` | 顯示指令列表 | `/help` |

## 授權

本專案採用 MIT 授權。
