from lineaihelper.services.base_service import BaseService


class HelpService(BaseService):
    async def execute(self, args: str) -> str:
        return (
            "[LineNexus Commands]\n"
            "/stock [symbol] - Stock analysis\n"
            "/chat [content] - AI chat\n"
            "/help - Show this help"
        )
