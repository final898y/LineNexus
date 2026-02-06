# 軟體設計文件 (Software Design Document) - LineNexus

**版本**: 2.0.0
**日期**: 2026-02-05
**專案名稱**: LineNexus | AI 指令樞紐

---

## 1. 簡介

### 1.1. 文件目的
本文件詳述「LineNexus」系統的架構設計、技術選型與開發指南。本專案嚴格遵循 **Clean Architecture** 與 **SOLID 原則**，並引入 **AI 工程化 (AI Engineering)** 實踐，旨在建立一個可維護、可測試且具備高度擴展性的 AI 代理平台。

### 1.2. 專案概述
LineNexus 是一個基於 LINE 的 **指令式 AI 代理 (Command-based AI Agent)**。系統採用「分發器 (Dispatcher)」模式處理使用者意圖，核心邏輯與外部框架（LINE, FastAPI, Database）徹底解耦。AI 能力透過 **Prompt as Code** 的方式進行管理，確保提示詞的可追溯性與迭代效率。

### 1.3. 專案範疇

#### 1.3.1. 範圍內 (In-Scope)
*   **指令分發核心**: 支援 `.command` 語法的動態分發與參數解析。
*   **多模態業務服務**:
    *   **股市分析**: 整合 `BaseDataProvider` 介面，提供彈性的數據來源（台股、美股、加密貨幣）。
    *   **AI 聊天**: 基於版本化 Prompt 的通用對話服務。
    *   **純數據查詢**: 不經 AI 處理的即時報價服務。
*   **AI 工程化基礎建設**: 實作 `PromptEngine`，支援 Jinja2 模板渲染、Markdown 外部儲存與版本控制。
*   **依賴反轉架構**: 透過 Dependency Injection (DI) 管理外部依賴。

#### 1.3.2. 範圍外 (Out-of-Scope)
*   **交易執行**: 系統僅提供資訊與建議，不涉及實際下單。
*   **使用者帳戶管理系統 (IAM)**: 依賴 LINE User ID 識別，暫不實作獨立登入系統。

---

## 2. 系統架構 (Clean Architecture)

本專案採用 **Clean Architecture (洋蔥架構)**，由內而外分為四層，依賴關係**只能由外向內**。

```mermaid
graph TD
    subgraph Infrastructure [Infrastructure Layer]
        FastAPI[FastAPI / Webhook]
        LineAPI[LINE Messaging API]
        DB[(PostgreSQL)]
        Gemini[Gemini API]
        PromptFiles[Markdown Prompts]
    end

    subgraph Adapters [Interface Adapters Layer]
        Dispatcher[Command Dispatcher]
        Presenters[Response Presenters]
        Gateways[Data Providers / Repositories]
        PromptEng[Prompt Engine]
    end

    subgraph UseCases [Application Business Rules]
        StockSvc[Stock Service]
        ChatSvc[Chat Service]
        PriceSvc[Price Service]
        BaseSvc[Base Service Interface]
    end

    subgraph Entities [Enterprise Business Rules]
        Models[Domain Models (KLine, Quote)]
        Exceptions[Business Exceptions]
    end

    %% Dependency Rule: Outer layers depend on inner layers
    Infrastructure --> Adapters
    Adapters --> UseCases
    UseCases --> Entities

    %% Specific Flows
    FastAPI -- "Request" --> Dispatcher
    Dispatcher -- "DTO" --> BaseSvc
    StockSvc -- "Interface" --> Gateways
    Gateways -- "Impl" --> Gemini & DB
    StockSvc -- "Interface" --> PromptEng
    PromptEng -- "Read" --> PromptFiles
```

### 2.1. 層級職責說明

1.  **Entities (Domain Models)**:
    *   定義核心業務物件（如 `StockQuote`, `KLineBar`）。
    *   純 Python Data Classes，**不依賴任何外部庫**。
2.  **Use Cases (Services)**:
    *   封裝具體的應用邏輯（如「分析台股趨勢」）。
    *   定義 `Input Port` (execute 方法參數) 與 `Output Port` (回傳結果)。
    *   透過介面 (Interface) 呼叫外部資源，**不直接依賴實作**。
3.  **Interface Adapters**:
    *   **Dispatcher**: 將 LINE Webhook 事件轉換為 Service 能理解的輸入。
    *   **PromptEngine**: 將 Service 的意圖轉換為 LLM 能理解的 Prompt 字串。
    *   **Providers**: 實作 Use Case 定義的介面（如 `YahooFinanceProvider` 實作 `BaseDataProvider`）。
4.  **Infrastructure**:
    *   框架與驅動程式（FastAPI, `line-bot-sdk`, `google-genai`）。
    *   資料庫與檔案系統。

---

## 3. SOLID 原則實踐

本專案在設計上嚴格落實 SOLID 原則：

### 3.1. 單一職責原則 (SRP)
*   **Service**: 只專注於業務邏輯流（獲取數據 -> 組裝 -> 分析），不負責「如何抓數據」或「Prompt 具體內容」。
*   **PromptEngine**: 只負責讀取檔案與渲染模板，不涉及業務邏輯。
*   **Dispatcher**: 只負責路由分發，不處理具體指令內容。

### 3.2. 開放封閉原則 (OCP)
*   **新增指令**: 只需新增一個繼承 `BaseService` 的類別並註冊，**無需修改 Dispatcher 核心邏輯**。
*   **修改 AI 行為**: 只需新增或修改 `src/lineaihelper/prompts/` 下的 Markdown 檔案，**無需修改 Python 程式碼**。
*   **更換數據源**: 若要從 Yahoo 換成 Binance，只需實作 `BaseDataProvider` 的新子類別，**無需修改 Service 程式碼**。

### 3.3. 里氏替換原則 (LSP)
*   所有 `Service` 皆可互換地被 Dispatcher 呼叫。
*   所有 `DataProvider` (Yahoo, Mock, Crypto) 皆可互換地被 Service 使用，確保單元測試時能輕鬆 Mock 外部 API。

### 3.4. 介面隔離原則 (ISP)
*   `BaseDataProvider` 定義了細粒度的介面（`get_quote`, `get_history`），避免 Service 依賴它不需要的方法。

### 3.5. 依賴反轉原則 (DIP)
*   **High-level modules (Services) should not depend on low-level modules (YahooFinanceProvider). Both should depend on abstractions.**
*   `StockService` 建構時透過 `__init__` 注入 `BaseDataProvider` (抽象介面)，而非在內部實例化具體的 Provider。

---

## 4. AI 工程化 (AI Engineering)

### 4.1. Prompt as Code
將 Prompt 視為程式碼資產進行管理：
*   **檔案化**: 儲存於 `src/lineaihelper/prompts/{service_name}/`。
*   **格式**: 使用 Markdown + YAML Frontmatter。
*   **模板**: 使用 Jinja2 (`{{ variable }}`) 進行動態變數注入。

### 4.2. 版本控制 (Versioning)
*   每個 Prompt 檔案命名包含版本或用途（如 `v1.md`, `latest.md`）。
*   在 YAML Header 中記錄 `version`, `author`, `model` 等元數據。
*   Runtime Log 會記錄當次執行所使用的 Prompt 版本，便於追蹤 AI 幻覺問題。

---

## 5. 詳細設計

### 5.1. 指令解析與分發
*   **語法**: `.[指令] [參數]` (e.g., `.stock 2330`)
*   **流程**:
    1.  `Dispatcher` 接收文字。
    2.  檢查 `.` 前綴。
    3.  解析指令關鍵字 (`stock`)。
    4.  查找對應 Service 實例。
    5.  呼叫 `service.execute(args)`。

### 5.2. 異常處理策略
*   **ServiceError**: 業務邏輯錯誤（如「無此代碼」），回傳友善提示給使用者。
*   **ExternalAPIError**: 外部依賴失敗（如「Yahoo API timeout」），記錄 Error Log 並回傳「系統忙碌中」。
*   **Unhandled Exception**: 系統層級錯誤（Bug），由 FastAPI 全域攔截，回傳 500 並發送 Alert。

---

## 6. 技術棧 (Technology Stack)
*   **Language**: Python 3.14
*   **Framework**: FastAPI
*   **Dependency Injection**: 手動注入 (Constructor Injection)
*   **AI SDK**: Google GenAI (Gemini)
*   **Prompt Engine**: Jinja2 + PyYAML
*   **Linter**: Ruff
*   **Type Checker**: Mypy (Strict mode)
*   **Testing**: Pytest (Asyncio)

---

## 7. 擴展藍圖 (Roadmap)

1.  **Repository Pattern**: 實作 `PostgresRepository`，將資料存取邏輯從 Service 分離（Phase 3）。
2.  **Service Registry**: 實作自動化註冊機制，透過 Decorator 自動掃描並註冊指令，消除 Dispatcher 中的靜態 Mapping。
3.  **多輪對話 Context**: 在 `ChatService` 引入 `ConversationRepository`，實現具備記憶的對話體驗。
