from abc import ABC, abstractmethod

class BaseService(ABC):
    """
    所有業務邏輯服務的基礎抽象類別 (Abstract Base Class)。
    強制子類別實作 execute 方法。
    """

    @abstractmethod
    async def execute(self, args: str) -> str:
        """
        執行服務邏輯。

        Args:
            args (str): 指令參數 (去除指令本身後的剩餘字串)

        Returns:
            str: 要回傳給使用者的訊息
        """
        pass
