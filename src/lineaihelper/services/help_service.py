from lineaihelper.services.base_service import BaseService


class HelpService(BaseService):
    async def execute(self, args: str) -> str:
        return (
            "[LineNexus Commands]\n"
            ".stock [symbol] - AI 技術分析報告\n"
            ".price [symbol] - 即時報價與近期 K 線\n"
            ".chat [content] - AI 聊天對話\n"
            ".help - 顯示此指令列表"
        )
