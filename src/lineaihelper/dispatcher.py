from typing import Dict

from google import genai
from loguru import logger

from lineaihelper.services import BaseService, ChatService, HelpService, StockService


class CommandDispatcher:
    def __init__(self, gemini_client: genai.Client):
        # 註冊指令對應的服務
        self.services: Dict[str, BaseService] = {
            "/stock": StockService(gemini_client),
            "/chat": ChatService(gemini_client),
            "/help": HelpService(),
        }

    async def parse_and_execute(self, user_text: str) -> str:
        """
        解析使用者文字並分發給對應服務。
        """
        if not user_text.startswith("/"):
            # 非指令文字目前僅做 Echo (或是可視為一般聊天)
            return f"LineNexus (Async) received: {user_text}"

        parts = user_text.split(" ", 1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        logger.info(f"Dispatching command: {command}")

        service = self.services.get(command)
        if service:
            return await service.execute(args)
        else:
            return f"Unknown command: {command}, type /help for info."