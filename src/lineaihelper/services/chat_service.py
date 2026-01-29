from google import genai
from loguru import logger

from lineaihelper.services.base_service import BaseService


class ChatService(BaseService):
    def __init__(self, gemini_client: genai.Client):
        self.gemini_client = gemini_client

    async def execute(self, args: str) -> str:
        if not args:
            return "Please provide content, e.g., /chat hello"

        try:
            # 使用 Gemini 進行對話
            response = await self.gemini_client.aio.models.generate_content(
                model="gemini-2.5-flash", contents=args
            )
            return response.text
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return "AI is currently unavailable."
