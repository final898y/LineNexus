def test_read_root(client):
    """測試根路徑 / 回傳 Hello World"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_read_item(client):
    """測試帶有 query parameter 的項目查詢"""
    item_id = 5
    q = "somequery"
    response = client.get(f"/items/{item_id}?q={q}")
    assert response.status_code == 200
    assert response.json() == {"item_id": item_id, "q": q}


def test_read_item_no_query(client):
    """測試不帶 query parameter 的項目查詢"""
    item_id = 10
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json() == {"item_id": item_id, "q": None}
