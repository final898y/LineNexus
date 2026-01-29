from typing import Optional


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
