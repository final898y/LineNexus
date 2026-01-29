from typing import Dict

from google import genai
from loguru import logger

from lineaihelper.exceptions import LineNexusError
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
        解析使用者文字並分發給對應服務，並處理所有業務與系統異常。
        """
        if not user_text.startswith("/"):
            return f"LineNexus (Async) received: {user_text}"

        parts = user_text.split(" ", 1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        logger.info(f"Dispatching command: {command}")

        try:
            service = self.services.get(command)
            if service:
                return await service.execute(args)
            else:
                return f"Unknown command: {command}, type /help for info."
        except LineNexusError as e:
            # 攔截自定義的業務邏輯錯誤
            logger.warning(f"Service error in {command}: {e.message}")
            return f"⚠️ {e.message}"
        except Exception as e:
            # 攔截未預期的系統錯誤
            logger.exception(f"Unexpected error in {command}: {e}")
            return "❌ 系統發生未知錯誤，請稍後再試或聯繫管理員。"
