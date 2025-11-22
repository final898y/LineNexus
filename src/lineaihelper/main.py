from typing import Union
from fastapi import FastAPI

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