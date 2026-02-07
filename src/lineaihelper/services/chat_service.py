from typing import Optional

from google import genai

from lineaihelper.exceptions import ExternalAPIError, ServiceError, handle_gemini_error
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
            raise ServiceError("請提供聊天內容，例如: .chat 你好")

        prompt = self.prompt_engine.render("chat", {"message": args})

        try:
            response = await self.gemini_client.aio.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )

            if not response or not response.text:
                raise ExternalAPIError("AI 回傳了空內容，請換個方式問問看。")

            return response.text
        except Exception as e:
            handle_gemini_error(e)
