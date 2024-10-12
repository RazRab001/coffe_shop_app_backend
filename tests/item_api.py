import pytest
from httpx import AsyncClient
from fastapi import status

from src.product.schema import IngredientValueType


@pytest.mark.asyncio
async def test_create_item_success(ac: AsyncClient):

    response = await ac.post("/api/v1/item", json={
        "title": "New Test Item",
        "description": "A description for a new item",
        "ingredients": [
            {"name": "milk", "value": 0.3, "value_type": IngredientValueType.KILOGRAM}
        ],
        "cost": 125.98
    })
    print("Response from test_create_item_success:", response.json())
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "New Test Item"
    assert data["description"] == "A description for a new item"
    assert len(data["ingredients"]) == 1
    assert data["ingredients"][0]["value"] == 0.3
    assert data["ingredients"][0]["value_type"] == "kilogram"
    item_id = data["id"]

    response = await ac.delete(f"/api/v1/item/{item_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    #print("Response from delete item in test_create_item_success:", response.json())

@pytest.mark.asyncio
async def test_create_item_unique_constraint_violation(ac: AsyncClient):
    response = await ac.post("/api/v1/item", json={
        "title": "New Test Item",
        "description": "A description for a new item",
        "ingredients": [
            {"name": "milk", "value": 0.3, "value_type": IngredientValueType.KILOGRAM}
        ],
        "cost": 125.98
    })
    print("Response from test_create_item_success:", response.json())
    assert response.status_code == status.HTTP_201_CREATED
    item_id = response.json()["id"]

    response = await ac.post("/api/v1/item", json={
        "title": "New Test Item",
        "description": "A description for a new item",
        "ingredients": [
            {"name": "milk", "value": 0.3, "value_type": IngredientValueType.KILOGRAM}
        ],
        "cost": 125.98
    })
    print("Response from test_create_item_unique_constraint_violation:", response.json())
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Unique constraint violation, likely a duplicate entry."
    response = await ac.delete(f"/api/v1/item/{item_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_create_item_invalid_data(ac: AsyncClient):

    response = await ac.post("/api/v1/item", json={
        "title": "",
        "description": "A description for a new item",
        "ingredients": [
            {"name": "milk", "value": 0.3, "value_type": IngredientValueType.KILOGRAM}
        ],
        "cost": 125.98
    })
    print("Response from test_create_item_invalid_data:", response.json())
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_items_success(ac: AsyncClient):
    response = await ac.post("/api/v1/item", json={
        "title": "Test1",
        "description": "A description for a new item",
        "ingredients": [
            {"name": "milk", "value": 0.3, "value_type": IngredientValueType.KILOGRAM}
        ],
        "cost": 125.98
    })
    item_id1 = response.json()["id"]

    response = await ac.post("/api/v1/item", json={
        "title": "Test2",
        "description": "A description for a new item",
        "ingredients": [
            {"name": "milk", "value": 0.3, "value_type": IngredientValueType.KILOGRAM}
        ],
        "cost": 125.98
    })
    item_id2 = response.json()["id"]

    response = await ac.get("/api/v1/item")
    print("Response from test_get_items_success:", response.json())  # Выводим респонс
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    response = await ac.delete(f"/api/v1/item/{item_id1}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = await ac.delete(f"/api/v1/item/{item_id2}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.asyncio
async def test_update_item_success(ac: AsyncClient):
    response = await ac.post("/api/v1/item", json={
        "title": "New Item",
        "description": "A description for a new item",
        "ingredients": [
            {"name": "milk", "value": 0.3, "value_type": IngredientValueType.KILOGRAM}
        ],
        "cost": 125.98
    })
    print("Response from test_update_item_success (creation):", response.json())  # Выводим респонс
    item_id = response.json()["id"]

    update_response = await ac.put(f"/api/v1/item/{item_id}", json={
        "title": "Updated Item",
        "description": "Updated description",
        "ingredients": [
            {"name": "milk", "value": 0.3, "value_type": IngredientValueType.KILOGRAM}
        ],
        "cost": 125.98
    })
    print("Response from test_update_item_success (update):", update_response.json())  # Выводим респонс

    assert update_response.status_code == status.HTTP_200_OK
    data = update_response.json()
    assert data["title"] == "Updated Item"
    assert data["description"] == "Updated description"

@pytest.mark.asyncio
async def test_delete_item_success(ac: AsyncClient):
    global product_id

    response = await ac.post("/api/v1/item", json={
        "title": "New Item",
        "description": "A description for a new item",
        "ingredients": [
            {"name": "milk", "value": 0.3, "value_type": IngredientValueType.KILOGRAM}
        ],
        "cost": 125.98
    })
    print("Response from test_delete_item_success (creation):", response.json())  # Выводим респонс
    item_id = response.json()["id"]

    delete_response = await ac.delete(f"/api/v1/item/{item_id}")
    print("Response from test_delete_item_success (delete):", delete_response.status_code)  # Выводим респонс
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_item_not_found(ac: AsyncClient):
    response = await ac.delete("/api/v1/item/9999")
    print("Response from test_delete_item_not_found:", response.json())  # Выводим респонс
    assert response.status_code == status.HTTP_204_NO_CONTENT
