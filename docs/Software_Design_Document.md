# 軟體設計文件 (Software Design Document) - LineNexus

**版本**: 2.1.0
**專案名稱**: LineNexus | AI 指令樞紐

---

## 1. 簡介

### 1.1. 文件目的
本文件詳述「LineNexus」系統的架構設計、技術選型與開發指南。本專案嚴格遵循 Clean Architecture 與 SOLID 原則，並引入 AI 工程化 (AI Engineering) 實踐，旨在建立一個可維護、可測試且具備高度擴展性的 AI 代理平台。

### 1.2. 專案概述
LineNexus 是一個基於 LINE 的指令式 AI 代理 (Command-based AI Agent)。系統採用「分發器 (Dispatcher)」模式處理使用者意圖，核心邏輯與外部框架（LINE, FastAPI, Database）徹底解耦。AI 能力透過 Prompt as Code 的方式進行管理。

---

## 2. 系統架構 (Clean Architecture)

本專案採用 Clean Architecture (洋蔥架構)，由內而外分為四層，依賴關係只能由外向內。

1.  **Entities (Domain Models)**: 定義核心業務物件。純 Python Data Classes，不依賴任何外部庫。
2.  **Use Cases (Services)**: 封裝具體的應用邏輯。定義介面以呼叫外部資源。
3.  **Interface Adapters**: 將外部請求轉換為內部 Service 能理解的輸入（如 Dispatcher, Providers）。
4.  **Infrastructure**: 框架與驅動程式（FastAPI, line-bot-sdk, google-genai）。

---

## 3. SOLID 原則實踐

本專案在設計上嚴格落實 SOLID 原則：

1.  **單一職責原則 (SRP)**: 模組僅負責單一邏輯（如 Service 僅處理業務流）。
2.  **開放封閉原則 (OCP)**: 新增指令或數據源時，無需修改核心邏輯，僅需實作新類別。
3.  **里氏替換原則 (LSP)**: 所有介面實作皆可互換而不破壞系統。
4.  **介面隔離原則 (ISP)**: 介面應細粒度化，避免依賴不需要的方法。
5.  **依賴反轉原則 (DIP)**: 高層模組不依賴低層模組，兩者皆依賴抽象。

---

## 4. API 規範與版本控制

### 4.1. API 版本控制 (Versioning)
*   **URL 版本化**: 外部接口採用 `/api/v1/` 命名空間。
*   **版本演進**: 破壞性變更 (Breaking Changes) 必須提升主版本號。

### 4.2. 錯誤處理 (Error Handling)
*   **異常分級**: 系統定義 `BaseAppException` 作為基準，區分 `DomainException` 與 `SystemException`。
*   **標準化回應**: 所有 API 錯誤回應應符合 RFC 7807 (Problem Details for HTTP APIs) 規範。
*   **無靜默失敗**: 禁止捕獲異常而不進行適當處置或記錄。

---

## 5. 可觀測性與日誌 (Observability)

### 5.1. 結構化日誌 (Structured Logging)
*   **工具**: 使用 `loguru` 進行日誌管理。
*   **上下文綁定**: 透過 `logger.bind(request_id=...)` 在所有相關日誌中注入追蹤碼。
*   **分級規範**:
    *   INFO: 重要業務流程節點。
    *   WARNING: 可預期的非致命錯誤（如外部 API 超時）。
    *   ERROR: 導致請求失敗的異常。

### 5.2. 追蹤 (Tracing)
*   **Request ID**: 每個 Webhook 請求在進入系統時會被賦予唯一的 Request ID，並貫穿整個處理生命週期。

---

## 6. AI 工程化 (AI Engineering)

### 6.1. Prompt as Code
*   **檔案化**: 儲存於 `src/lineaihelper/prompts/`。
*   **模板**: 使用 Jinja2 進行動態變數注入。
*   **版本控制**: Runtime 會記錄當次執行所使用的 Prompt 版本。

---

## 7. 技術棧 (Technology Stack)
*   **Language**: Python 3.12+
*   **Framework**: FastAPI
*   **AI SDK**: Google GenAI (Gemini)
*   **Linter/Formatter**: Ruff
*   **Type Checker**: Mypy (Strict mode)
*   **Testing**: Pytest (Asyncio)