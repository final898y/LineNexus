from typing import NoReturn, Optional

from google.genai import errors


class LineNexusError(Exception):
    """LineNexus 專案的基礎異常類別"""

    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        self.message = message
        self.original_exception = original_exception
        super().__init__(self.message)


class ServiceError(LineNexusError):
    """業務邏輯服務層發生的異常"""

    pass


class ExternalAPIError(LineNexusError):
    """外部 API (如 Gemini, yfinance) 呼叫失敗時的異常"""

    pass


def handle_gemini_error(e: Exception, default_msg: str = "AI 暫時無法回應") -> NoReturn:
    """
    統一處理 Google GenAI API 異常轉換。

    Args:
        e: 擷取到的原始異常。
        default_msg: 當無法識別具體錯誤類型時使用的預設訊息。

    Raises:
        ExternalAPIError: 轉換後的專案標準異常。
    """
    if isinstance(e, errors.ClientError):
        # 處理 4xx 錯誤，如配額超出 (ResourceExhausted) 或參數錯誤
        error_msg = str(e).lower()
        if "quota" in error_msg or "exhausted" in error_msg:
            raise ExternalAPIError(
                "AI 額度已達上限，請明天再試或稍後再撥。", original_exception=e
            ) from e
        raise ExternalAPIError(
            f"請求 AI 時發生用戶端錯誤: {e.status}", original_exception=e
        ) from e

    if isinstance(e, errors.ServerError):
        # 處理 5xx 錯誤
        raise ExternalAPIError(
            "AI 伺服器暫時忙碌中，請稍後再試。", original_exception=e
        ) from e

    if isinstance(e, errors.APIError):
        # 處理其他 GenAI API 錯誤
        raise ExternalAPIError(
            f"AI 服務發生異常 ({e.code})，請稍後再試。", original_exception=e
        ) from e

    # 如果是已經封裝過的異常，直接拋出
    if isinstance(e, (ExternalAPIError, ServiceError)):
        raise e

    # 其他未知異常
    raise ExternalAPIError(f"{default_msg}，請稍後再試。", original_exception=e) from e
