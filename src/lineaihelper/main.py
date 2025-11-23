from typing import Union
from fastapi import FastAPI
import uvicorn  # 引入 uvicorn 伺服器模組

# 建立 FastAPI 應用程式實例
app = FastAPI()

# 定義根路徑的路由 (Route)
# 當使用者訪問 http://127.0.0.1:8000/ 時觸發
@app.get("/")
def read_root():
    return {"Hello": "World"}

# 定義帶有參數的路徑
# 例如訪問 http://127.0.0.1:8000/items/5?q=somequery
@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    # FastAPI 會自動將 item_id 轉為整數，並讀取 q 查詢參數
    return {"item_id": item_id, "q": q}

# --- 新增的啟動邏輯 ---

def start():
    """
    這是為了讓 pyproject.toml 中的 [project.scripts] 呼叫的入口函式。
    當你在終端機執行 `uv run dev` 時，就是執行這個函式。
    """
    # uvicorn.run 的第一個參數必須是字串格式的 "套件名.模組名:app物件名"
    # reload=True 代表程式碼修改後會自動重啟，開發時很好用
    uvicorn.run("lineaihelper.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    # 這是為了讓你可以直接用 `python src/lineaihelper/main.py` 執行 (如果不透過 uv)
    start()