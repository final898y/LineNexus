# LineNexus | AI 指令樞紐

本專案是一個基於 LINE 聊天機器人的 AI 多功能助手。採用指令式 (Command-based) 架構，使用者可以透過特定指令進行台股分析、AI 聊天或其他擴展功能。

## 專案架構

本專案採用分離式架構，由 LINE 使用者介面、後端應用程式伺服器與外部 API 服務組成，並引入 **Dispatcher (分發器)** 模式以支援多功能擴展。

```mermaid
graph TD
    A[使用者] -- 傳送指令 e.g., /stock 2330 --> B(LINE App)
    B -- Webhook --> C{後端伺服器 (FastAPI)}
    C -- 1. 驗證請求 --> C
    C -- 2. 指令解析 --> D[指令分發器 Dispatcher]
    D -- 3. 呼叫對應服務 --> E{功能模組 Services}
    E -- /stock --> E1[股市分析服務]
    E -- /chat --> E2[AI 聊天服務]
    E1 -- 抓取數據 --> F[Yahoo Finance]
    E1 -- AI 分析 --> G[Google Gemini]
    E2 -- AI 對話 --> G
    C -- 4. 格式化訊息 --> H[LINE Messaging API]
    H -- 推播訊息 --> B
    B -- 顯示結果 --> A
```

### 架構說明

1.  **使用者介面**: 使用者在 LINE App 中透過指令與機器人互動。
2.  **指令分發器 (Dispatcher)**: 負責解析使用者輸入的文字，識別指令標籤（如 `/stock`）並將任務分派給對應的 Service。
3.  **功能服務層 (Services)**:
    *   **Stock Service**: 處理股市資料抓取與 AI 投資見解生成。
    *   **Chat Service**: 處理一般性的 AI 對話與問答。
4.  **外部服務**:
    *   **LINE Platform**: 管理機器人帳號與 Webhook。
    *   **Yahoo Finance**: 股市數據來源。
    *   **Google Gemini**: 提供核心 AI 分析能力。

## 指令互動規範

| 指令 | 說明 | 範例 |
| :--- | :--- | :--- |
| `/stock [代碼]` | 針對特定台股進行 K 線分析與 AI 見解 | `/stock 2330` |
| `/chat [訊息]` | 與 AI 進行一般性對話或問答 | `/chat 為什麼今天股市大跌？` |
| `/help` | 顯示所有可用的指令列表 | `/help` |

## 技術棧 (Technology Stack)

*   **後端**: Python 3.14+
*   **Web 框架**: FastAPI
*   **LINE Bot**: line-bot-sdk
*   **股票資料**: yfinance
*   **AI 模型**: google-generativeai
*   **套件管理**: uv
*   **Web 伺服器**: Uvicorn
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
    uv venv
    uv sync
    ```

3.  **設定環境變數**
    複製 `.env.example` 檔案並重新命名為 `.env`，填入必要金鑰。
    ```ini
    LINE_CHANNEL_ACCESS_TOKEN="YOUR_LINE_CHANNEL_ACCESS_TOKEN"
    LINE_CHANNEL_SECRET="YOUR_LINE_CHANNEL_SECRET"
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    ```

## 專案結構 (Project Structure)

```text
LineAiHelper/
├── docs/                   # 專案文件
├── logs/                   # (自動產生) 應用程式日誌
├── src/
│   └── lineaihelper/
│       ├── main.py         # 接收 Webhook 與基礎驗證
│       ├── dispatcher.py   # [核心] 解析指令並分發任務
│       ├── services/       # [擴展] 存放所有功能模組
│       │   ├── base.py     # Service 抽象基礎類別
│       │   ├── stock_service.py
│       │   └── chat_service.py
│       └── logging_config.py
├── tests/                  # 測試程式碼
├── pyproject.toml          # 專案依賴
└── README.md
```

## 如何運行

1.  **啟動開發伺服器**
    ```bash
    uv run fastapi dev src/lineaihelper/main.py
    ```

2.  **設定 Webhook**
    使用 `ngrok` 建立安全通道：
    ```bash
    ngrok http 8000
    ```
    將網址填入 LINE Developer Console 的 Webhook URL (加上 `/callback`)。

3.  **開始測試**
    在 LINE 中傳送 `/stock 2330` 或 `/chat 你好` 即可看到回覆。

## 未來展望

*   [ ] 支援多種股票市場（美股、日股）。
*   [ ] 增加 `/weather` 指令查詢即時天氣。
*   [ ] 提供 K 線圖視覺化回傳。
*   [ ] 建立使用者偏好設定指令 (e.g., `/settings`)。

## 授權

本專案採用 MIT 授權。