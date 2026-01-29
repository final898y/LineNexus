from google import genai
from loguru import logger

from lineaihelper.services.base_service import BaseService
from lineaihelper.exceptions import ServiceError, ExternalAPIError


class ChatService(BaseService):
    def __init__(self, gemini_client: genai.Client):
        self.gemini_client = gemini_client

    async def execute(self, args: str) -> str:
        if not args:
            raise ServiceError("請提供聊天內容，例如: /chat 你好")

        try:
            response = await self.gemini_client.aio.models.generate_content(
                model="gemini-2.5-flash", contents=args
            )
            
            if not response or not response.text:
                raise ExternalAPIError("AI 回傳了空內容，請換個方式問問看。")
                
            return response.text
        except Exception as e:
            if isinstance(e, ExternalAPIError):
                raise
            
            error_msg = str(e)
            if "quota" in error_msg.lower():
                raise ExternalAPIError("AI 額度已達上限，請明天再試或稍後再撥。", original_exception=e)
            
            raise ExternalAPIError("AI 暫時無法回應，請稍後再試。", original_exception=e)