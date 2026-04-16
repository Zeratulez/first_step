from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import crud_user
from app.models import User


async def test_create_user(db_session: AsyncSession, client: AsyncClient):
    response = await client.post(
        "/auth/register",
        json={"username": "foo",
              "email": "foo@example.com",
              "password": "123"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "foo"

async def test_authenticate_user(db_session: AsyncSession, client: AsyncClient, test_user: User):
    response = await client.post(
        "/auth/login",
        data={"username": test_user.username, "password": "123"}
    )
    assert response.status_code == 200

async def test_not_authenticate_user(db_session: AsyncSession, client: AsyncClient):
    response = await client.post(
        "/auth/login",
        data={"username": "fake_name", "password": "fake_password"}
    )
    assert response.status_code == 401

async def test_user_already_exists(db_session: AsyncSession, client: AsyncClient, test_user: User):
    user = jsonable_encoder(test_user)
    response = await client.post(
        "/auth/register",
        json={"username": user["username"],
              "email": user["email"],
              "password": "123"}
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "User with this nickname already exists"

async def test_authenticate_user_wrong_username(db_session: AsyncSession, client: AsyncClient, test_user: User):
    response = await client.post(
        "/auth/login",
        data={"username": "wrong_username", "password": "123"}
    )
    assert response.status_code == 401

async def test_authenticate_user_wrong_password(db_session: AsyncSession, client: AsyncClient, test_user: User):
    response = await client.post(
        "/auth/login",
        data={"username": test_user.username, "password": "wrong_password"}
    )
    assert response.status_code == 401

async def test_get_user_by_username(db_session: AsyncSession, test_user: User):
    user = await crud_user.get_user_by_username(db_session, test_user.username)
    assert user.username == test_user.username
    assert user.is_active == True

async def test_get_nonexisting_user_by_username(db_session: AsyncSession):
    user = await crud_user.get_user_by_username(db_session, "fake_username")
    assert user is None

async def test_get_user_by_id(db_session: AsyncSession, test_user: User):
    user = await crud_user.get_user_by_id(db_session, test_user.id)
    assert user.username == test_user.username
    assert user.is_active == True

async def test_get_nonexisting_user_by_id(db_session: AsyncSession):
    user = await crud_user.get_user_by_id(db_session, -1)
    assert user is None