from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.models import Item, User
from tests.utils.items import create_random_item
from tests.utils.users import random_user_token

def test_create_item(db_session: Session, client: TestClient, user_token):
    data = {"name": "bar", "description": "karamba", "price": 10, "tax": 2.5}
    response = client.post(
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

def test_read_item(db_session: Session, client: TestClient, test_item: Item):
    data = jsonable_encoder(test_item)
    response = client.get(
        f"/items/{test_item.id}",
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["description"] == data["description"]
    assert content["id"] == data["id"]
    assert content["owner_id"] == data["owner_id"]

def test_read_item_not_found(db_session: Session, client: TestClient):
    response = client.get(
        "/items/-1",
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

def test_read_items(db_session: Session, client: TestClient):
    create_random_item(db_session)
    create_random_item(db_session)
    response = client.get(
        "/items/",
    )
    assert response.status_code == 200
    print(response.json())
    assert len(response.json()) == 2

def test_update_item(db_session: Session, client: TestClient, test_item: Item, user_token):
    data = {"name": "updated_name", "description": "updated_description", "price": 100, "tax": 50}
    response = client.patch(
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

def test_update_item_not_found(db_session: Session, client: TestClient, user_token):
    data = {"name": "updated_name", "description": "updated_description", "price": 100, "tax": 50}
    response = client.patch(
        "/items/update/-1",
        headers=user_token,
        json=data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

def test_update_item_not_owner(db_session: Session, client: TestClient, test_item: Item):
    headers = random_user_token(db_session, client)
    data = {"name": "updated_name", "description": "updated_description", "price": 100, "tax": 50}
    response = client.patch(
        f"/items/update/{test_item.id}",
        headers=headers,
        json=data
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "You not the owner of the item"

def test_delete_item(db_session: Session, client: TestClient, test_item: Item, user_token):
    response = client.delete(
        f"items/delete/{test_item.id}",
        headers=user_token,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "item deleted"

def test_delete_item_not_found(db_session: Session, client: TestClient, user_token):
    response = client.delete(
        "items/delete/-1",
        headers=user_token,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

def test_delete_item_not_owner(db_session: Session, client: TestClient, test_item: Item):
    headers = random_user_token(db_session, client)
    response = client.delete(
        f"/items/delete/{test_item.id}",
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "You not the owner of the item"