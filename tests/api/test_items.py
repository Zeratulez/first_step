from httpx import AsyncClient
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Item, User
from tests.utils.items import create_random_item
from tests.utils.users import random_user_token

async def test_create_item(db_session: AsyncSession, client: AsyncClient, user_token):
    data = {"name": "bar", "description": "karamba", "price": 10, "tax": 2.5}
    response = await client.post(
        "/items/create_item",
        headers=user_token,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["description"] == data["description"]
    assert "id" in content
    assert "owner_id" in content

async def test_read_item(db_session: AsyncSession, client: AsyncClient, test_item: Item):
    data = jsonable_encoder(test_item)
    response = await client.get(
        f"/items/item/{test_item.id}",
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["description"] == data["description"]
    assert content["id"] == data["id"]
    assert content["owner_id"] == data["owner_id"]

async def test_read_item_not_found(db_session: AsyncSession, client: AsyncClient):
    response = await client.get(
        "/items/item/-1",
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

async def test_read_items(db_session: AsyncSession, client: AsyncClient):
    await create_random_item(db_session)
    await create_random_item(db_session)
    response = await client.get(
        "/items/",
    )
    assert response.status_code == 200
    assert len(response.json()) >= 2

async def test_update_item(db_session: AsyncSession, client: AsyncClient, test_item: Item, user_token):
    data = {"name": "updated_name", "description": "updated_description", "price": 100, "tax": 50}
    response = await client.patch(
        f"/items/update/{test_item.id}",
        headers=user_token,
        json=data
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["description"] == data["description"]
    assert content["price"] == data["price"]
    assert content["tax"] == data["tax"]
    assert content["id"] == test_item.id
    assert content["owner_id"] == test_item.owner_id

async def test_update_item_not_found(db_session: AsyncSession, client: AsyncClient, user_token):
    data = {"name": "updated_name", "description": "updated_description", "price": 100, "tax": 50}
    response = await client.patch(
        "/items/update/-1",
        headers=user_token,
        json=data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

async def test_update_item_not_owner(db_session: AsyncSession, client: AsyncClient, test_item: Item):
    headers = await random_user_token(db_session, client)
    data = {"name": "updated_name", "description": "updated_description", "price": 100, "tax": 50}
    response = await client.patch(
        f"/items/update/{test_item.id}",
        headers=headers,
        json=data
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "You not the owner of the item"

async def test_delete_item(db_session: AsyncSession, client: AsyncClient, test_item: Item, user_token):
    response = await client.delete(
        f"items/delete/{test_item.id}",
        headers=user_token,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "item deleted"

async def test_delete_item_not_found(db_session: AsyncSession, client: AsyncClient, user_token):
    response = await client.delete(
        "items/delete/-1",
        headers=user_token,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

async def test_delete_item_not_owner(db_session: AsyncSession, client: AsyncClient, test_item: Item):
    headers = await random_user_token(db_session, client)
    response = await client.delete(
        f"/items/delete/{test_item.id}",
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "You not the owner of the item"