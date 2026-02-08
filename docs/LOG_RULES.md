# Python 專案日誌規範 (Python Logging Standards)

本文件定義 LineNexus 專案的日誌 (Logging) 實作標準與開發規範，旨在確保系統具備良好的可觀測性 (Observability) 與維運效能。

---

## 1. 設計目標 (Design Objectives)

*   **結構化 (Structured)**：支援 JSON 格式輸出，便於集中式日誌管理系統 (如 ELK, CloudWatch) 解析。
*   **可追蹤性 (Traceability)**：每一筆日誌必須包含 `trace_id`，以串聯單次請求的完整生命週期。
*   **權責分流 (Separation of Concerns)**：區分一般資訊 (INFO) 與錯誤紀錄 (ERROR)，並實作自動化的檔案滾動與保留原則。
*   **一致性 (Consistency)**：全專案統一使用 `loguru` 作為日誌框架。

---

## 2. 日誌欄位規範 (Field Specifications)

### 2.1 核心固定欄位
系統自動記錄於每一筆日誌中的基礎欄位：

| 欄位名稱 | 說明 | 格式範例 |
| :--- | :--- | :--- |
| `timestamp` | 發生時間 (ISO 8601) | `2026-02-08T21:30:11.123` |
| `level` | 日誌等級 | `INFO`, `ERROR`, `WARNING` |
| `message` | 事件說明訊息 | `Process started` |
| `module` | 原始碼模組名稱 | `lineaihelper.services.stock_service` |
| `function` | 執行函式名稱 | `get_price` |
| `line` | 程式碼行號 | `42` |
| `trace_id` | 請求追蹤識別碼 | `uuid-string` |

### 2.2 動態擴展欄位 (Extra Context)
針對特定業務情境，應透過 `extra` 參數提供的欄位：

| 類別 | 建議欄位名稱 | 說明 |
| :--- | :--- | :--- |
| 使用者相關 | `user_id` | LINE 使用者唯一識別碼 |
| 外部請求 | `request_id`, `line_request_id` | 外部 API 的請求編號 |
| 業務流程 | `order_id`, `stock_symbol` | 特定業務物件的識別碼 |

---

## 3. 實作配置 (Implementation Configuration)

系統實作於 `src/lineaihelper/logging_config.py`，具體行為如下：

### 3.1 輸出分流機制
*   **Console (標準輸出)**：
    *   開發環境 (`LOG_JSON=False`)：輸出易於閱讀的彩色文字格式。
    *   正式環境 (`LOG_JSON=True`)：輸出結構化 JSON 格式。
*   **檔案儲存 (`/logs` 目錄)**：
    *   `linenexus_info_{date}.log`：紀錄 INFO 以上等級之日誌，過濾掉 ERROR 等級以保持簡潔。具備 200MB 滾動與 7 天保留期。
    *   `linenexus_error_{date}.log`：僅記錄 ERROR 以上等級。具備 100MB 滾動與 30 天保留期，確保關鍵錯誤資訊被長期保存。

### 3.2 序列化邏輯
系統實作自定義 `serialize` 函式，確保在輸出 JSON 時，包含完整的 Traceback 資訊與 Context 資料，並處理非 ASCII 字元的編碼問題。

---

## 4. 開發規範 (Development Standards)

### 4.1 禁止行為
*   禁止使用 `print()` 輸出資訊。
*   禁止在日誌訊息中使用 `f-string` 拼接變數（這會導致日誌聚合困難）。
*   禁止將敏感資訊（如 API Keys, 密碼）寫入日誌。

### 4.2 建議作法
*   **使用結構化參數**：將變數放入 `extra` 參數中。
    ```python
    # 正確做法
    logger.info("Stock price updated", extra={"symbol": "AAPL", "price": 150.5})

    # 錯誤做法
    logger.info(f"Stock price for AAPL is 150.5")
    ```
*   **例外處理**：擷取 Exception 時，務必使用 `logger.exception()`，這會自動捕捉 Stack Trace。
    ```python
    try:
        perform_action()
    except Exception:
        logger.exception("Action failed", extra={"context": "business_logic"})
    ```

---

## 5. 日誌等級定義 (Log Level Definitions)

| 等級 (Level) | 用途描述 |
| :--- | :--- |
| **DEBUG** | 僅用於開發階段，紀錄詳細的狀態變更或變數內容。 |
| **INFO** | 紀錄關鍵業務流程的起點與終點，以及正常的系統行為。 |
| **WARNING** | 紀錄非預期但不會導致功能失敗的異常（如：重試機制觸發）。 |
| **ERROR** | 紀錄導致特定功能失敗的錯誤。 |
| **CRITICAL** | 紀錄將導致系統停止運作或核心服務崩潰的嚴重事故。 |