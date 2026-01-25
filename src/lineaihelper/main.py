from typing import Union

import uvicorn
from fastapi import FastAPI
from loguru import logger

from lineaihelper.logging_config import setup_logging

# 初始化日誌
setup_logging()

# 建立 FastAPI 應用程式實例
app = FastAPI()


# 定義根路徑的路由 (Route)
@app.get("/")
def read_root():
    logger.info("收到首頁請求 - Hello World")
    return {"Hello": "World"}


# 定義帶有參數的路徑
@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    logger.info(f"查詢項目: item_id={item_id}, q={q}")
    return {"item_id": item_id, "q": q}


# --- 啟動邏輯 ---
def start():
    """
    這是為了讓 pyproject.toml 中的 [project.scripts] 呼叫的入口函式。
    當你在終端機執行 `uv run dev` 時，就是執行這個函式。
    """
    logger.info("應用程式正在啟動...")
    # uvicorn.run 的第一個參數必須是字串格式的 "套件名.模組名:app物件名"
    # reload=True 代表程式碼修改後會自動重啟，開發時很好用
    uvicorn.run("lineaihelper.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    start()
