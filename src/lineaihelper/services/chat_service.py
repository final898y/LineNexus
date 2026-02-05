from typing import Optional

from google import genai

from lineaihelper.exceptions import ExternalAPIError, ServiceError
from lineaihelper.prompt_engine import PromptEngine
from lineaihelper.services.base_service import BaseService


class ChatService(BaseService):
    def __init__(
        self,
        gemini_client: genai.Client,
        prompt_engine: Optional[PromptEngine] = None,
    ):
        self.gemini_client = gemini_client
        self.prompt_engine = prompt_engine or PromptEngine()

    async def execute(self, args: str) -> str:
        if not args:
            raise ServiceError("請提供聊天內容，例如: /chat 你好")

        prompt = self.prompt_engine.render("chat", {"message": args})

        try:
            response = await self.gemini_client.aio.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )

            if not response or not response.text:
                raise ExternalAPIError("AI 回傳了空內容，請換個方式問問看。")

            return response.text
        except Exception as e:
            if isinstance(e, ExternalAPIError):
                raise

            error_msg = str(e)
            if "quota" in error_msg.lower():
                raise ExternalAPIError(
                    "AI 額度已達上限，請明天再試或稍後再撥。", original_exception=e
                ) from e

            raise ExternalAPIError(
                "AI 暫時無法回應，請稍後再試。", original_exception=e
            ) from e
