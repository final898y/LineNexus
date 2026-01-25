# 股市分析小幫手 (Line AI Helper)

本專案是一個基於 LINE 聊天機器人的 AI 股市分析小幫手。使用者可以透過 LINE，輸入台股的代碼或名稱，後端伺服器將自動抓取最新的 K 線數據，並結合大型語言模型（LLM）分析，提供簡易的投資見解與建議。

## 專案架構

本專案採用分離式架構，由 LINE 使用者介面、後端應用程式伺服器與外部 API 服務組成。

```mermaid
graph TD
    A[使用者] -- 傳送股票代碼/名稱 --> B(LINE App)
    B -- Webhook --> C{後端伺服器 (Python/FastAPI)}
    C -- 1. 驗證請求 --> C
    C -- 2. 查詢股票資料 --> D[股市資料 API<br>(e.g., yfinance)]
    D -- 回傳 K 線數據 --> C
    C -- 3. 準備 Prompt --> E[大型語言模型 AI<br>(e.g., Google Gemini)]
    E -- 回傳分析建議 --> C
    C -- 4. 格式化訊息 --> F[LINE Messaging API]
    F -- 推播訊息 --> B
    B -- 顯示結果 --> A
```

### 架構說明

1.  **使用者介面**: 使用者在 LINE App 中與機器人互動。
2.  **後端伺服器**:
    *   使用 **FastAPI** 建立，接收來自 LINE Platform 的 Webhook 請求。
    *   驗證訊息來源是否為合法的 LINE 請求。
    *   使用 `yfinance` 等函式庫抓取指定股票的歷史 K 線資料。
    *   將整理後的數據與預設的 Prompt 結合，呼叫大型語言模型（如 Google Gemini）進行分析。
    *   將 AI 生成的建議格式化後，透過 LINE Messaging API 回傳給使用者。
3.  **外部服務**:
    *   **LINE Platform**: 管理機器人帳號與 Webhook 設定。
    *   **Yahoo Finance**: 作為 K 線數據來源。
    *   **Google Gemini (或其他 LLM)**: 提供 AI 分析能力。

## 技術棧 (Technology Stack)

*   **後端**: Python 3.14+
*   **Web 框架**: FastAPI
*   **LINE Bot**: line-bot-sdk
*   **股票資料**: yfinance
*   **AI 模型**: google-generativeai
*   **套件管理**: uv
*   **Web 伺服器**: Uvicorn (via FastAPI)
*   **日誌**: Loguru
*   **測試**: Pytest

## 環境設置

1.  **複製專案庫**
    ```bash
    git clone https://github.com/your-username/LineAiHelper.git
    cd LineAiHelper
    ```

2.  **環境與依賴管理**
    本專案使用 `uv` 進行高效的 Python 環境與套件管理。

    **A. 首次設定與同步環境**
    ```bash
    # 1. 建立虛擬環境 (如果尚未建立)
    uv venv

    # 2. 同步環境，`uv` 會讀取 `pyproject.toml` 並安裝所有依賴
    uv sync
    ```
    `uv sync` 會確保您的虛擬環境與專案定義的依賴完全一致，多退少補。

    **B. 新增或移除套件**
    當您需要為專案新增或移除套件時，`uv` 可以自動為您更新 `pyproject.toml`。

    *   **新增套件**:
        ```bash
        # 新增一個執行時依賴 (例如 line-bot-sdk)
        uv add line-bot-sdk

        # 新增一個僅在開發時使用的依賴 (例如 pytest)
        uv add --dev pytest
        ```
        此指令會自動將套件新增到 `pyproject.toml` 檔案中。

    *   **移除套件**:
        ```bash
        uv remove line-bot-sdk
        ```
        此指令會自動從 `pyproject.toml` 檔案中移除套件。

    *注意: `uv` 會自動偵測並使用 `.venv` 虛擬環境，因此在執行 `uv run` 或 `uv` 系列指令時，通常不需要手動啟用。*

3.  **設定環境變數**
    複製 `.env.example` 檔案並重新命名為 `.env`。
    ```bash
    cp .env.example .env
    ```
    接著，填入您在 LINE Developer Console 和 Google AI Studio 取得的金鑰。
    ```ini
    # .env
    LINE_CHANNEL_ACCESS_TOKEN="YOUR_LINE_CHANNEL_ACCESS_TOKEN"
    LINE_CHANNEL_SECRET="YOUR_LINE_CHANNEL_SECRET"
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    ```

## 日誌與測試 (Logging & Testing)

### 日誌系統 (Loguru)
本專案使用 `loguru` 進行日誌管理，支援自動輪換 (Rotation) 與壓縮。
*   **日誌位置**: 專案根目錄下的 `logs/` 資料夾。
*   **檔案格式**: `lineaihelper_{YYYY-MM-DD}.log`
*   **設定檔**: `src/lineaihelper/logging_config.py`

### 自動化測試 (Pytest)
專案包含完整的測試架構，使用 `pytest` 與 `TestClient`。

**執行測試**:
```bash
uv run pytest
```

**產生覆蓋率報告**:
```bash
uv run pytest --cov=src
```

## 專案結構 (Project Structure)

```text
LineAiHelper/
├── .vscode/                # VS Code 設定 (Formatter, Linter)
├── docs/                   # 專案文件 (架構設計, 開發計畫)
├── logs/                   # (自動產生) 應用程式日誌
├── src/
│   └── lineaihelper/
│       ├── __init__.py
│       ├── main.py         # 應用程式入口
│       └── logging_config.py # 日誌配置
├── tests/                  # 測試程式碼
│   ├── conftest.py         # Pytest Fixtures
│   └── test_main.py        # API 整合測試
├── .env.example            # 環境變數範例
├── pyproject.toml          # 專案依賴與設定
├── ruff.toml               # Linter/Formatter 設定
└── README.md               # 專案說明文件
```

## 如何運行

1.  **啟動後端伺服器**
    使用 `uv run` 執行 `fastapi dev` 來啟動開發伺服器，它會自動啟用熱重載 (hot-reloading)。
    ```bash
    uv run fastapi dev src/lineaihelper/main.py
    ```
    此命令會啟動一個監聽在 `http://127.0.0.1:8000` 的伺服器。`fastapi dev` 是開發 `fastapi` 應用程式的推薦方式。

2.  **設定公開網址 (Webhook)**
    LINE Webhook 需要一個公開的 HTTPS 網址。在本地開發時，您可以使用 `ngrok` 或 `cloudflared` 等工具來建立一個通往您本地伺服器的安全通道。

    **使用 ngrok 的範例:**
    ```bash
    ngrok http 8000
    ```
    `ngrok` 會產生一個類似 `https://xxxxxxxx.ngrok-free.app` 的網址。

3.  **設定 LINE Webhook**
    *   前往 [LINE Developers Console](https://developers.line.biz/console/)。
    *   選擇您的 Provider 及對應的 Channel。
    *   在 "Messaging API" 頁籤中，找到 "Webhook settings"。
    *   將 `ngrok` 產生的網址貼到 "Webhook URL" 欄位，並在後面加上 `/callback` (例如: `https://xxxxxxxx.ngrok-free.app/callback`)。
    *   啟用 "Use webhook"。

4.  **開始測試**
    在 LINE App 中找到您的機器人，傳送一個台股代碼（例如 `2330`）或名稱（例如 `台積電`），看看它是否能正確回覆分析結果！

## 未來展望

*   [ ] 支援多種股票市場（美股、日股等）。
*   [ ] 提供更豐富的圖表視覺化，例如直接繪製 K 線圖回傳。
*   [ ] 增加更多技術指標分析（RSI, MACD, 布林通道等）。
*   [ ] 建立使用者偏好設定，提供個人化的分析角度。
*   [ ] 優化 Prompt，讓 AI 的回答更具深度與準確性。

## 授權

本專案採用 MIT 授權。詳情請見 `LICENSE` 檔案。
