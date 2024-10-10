import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import app


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as client:
        yield client


@pytest.mark.asyncio
async def test_create_new_item(client: TestClient):
    item_data = {
        "title": "New API Item",
        "description": "Item Description",
        "ingredients": []
    }

    response = client.post("/item", json=item_data)
    assert response.status_code == 200
    assert response.json()["title"] == "New API Item"


@pytest.mark.asyncio
async def test_get_items(client: TestClient):
    response = client.get("/item")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)


@pytest.mark.asyncio
async def test_update_one_item(client: TestClient):
    item_data = {
        "title": "Another API Item",
        "description": "Description",
        "ingredients": []
    }
    create_response = client.post("/item", json=item_data)
    item_id = create_response.json()["id"]

    updated_data = {
        "title": "Updated API Item",
        "description": "Updated Description",
        "ingredients": []
    }
    update_response = client.put(f"/item/{item_id}", json=updated_data)
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated API Item"


@pytest.mark.asyncio
async def test_delete_one_item(client: TestClient):
    item_data = {
        "title": "Delete Me",
        "description": "Item Description",
        "ingredients": []
    }
    create_response = client.post("/item", json=item_data)
    item_id = create_response.json()["id"]

    delete_response = client.delete(f"/item/{item_id}")
    assert delete_response.status_code == 204

    # Confirm deletion
    get_response = client.get(f"/item/{item_id}")
    assert get_response.status_code == 404  # Should return 404 as the item is deleted


@pytest.mark.asyncio
async def test_create_item_with_invalid_data(client: TestClient):
    invalid_item = {
        "title": "",  # пустое название
        "description": "",  # пустое описание
        "ingredients": []
    }

    response = client.post("/item", json=invalid_item)
    assert response.status_code == 400  # Ожидаем ошибку 400


@pytest.mark.asyncio
async def test_get_nonexistent_item(client: TestClient):
    response = client.get("/item/9999")  # несуществующий item_id
    assert response.status_code == 404  # Ожидаем ошибку 404


@pytest.mark.asyncio
async def test_update_item_with_invalid_data(client: TestClient):
    valid_item = {
        "title": "Valid Title",
        "description": "Valid Description"
    }

    # Сначала создадим элемент
    response = client.post("/item", json=valid_item)
    item_id = response.json().get("id")

    invalid_update_data = {
        "title": "",  # пустое название
        "description": "Updated Description"
    }

    response = client.put(f"/item/{item_id}", json=invalid_update_data)
    assert response.status_code == 400  # Ожидаем ошибку 400


@pytest.mark.asyncio
async def test_delete_nonexistent_item(client: TestClient):
    response = client.delete("/item/9999")  # несуществующий item_id
    assert response.status_code == 404  # Ожидаем ошибку 404