from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Post, PostLike, User
from tests.utils.posts import create_random_post
from tests.utils.users import random_user_token


async def test_create_post(db_session: AsyncSession, client: AsyncClient, user_token):
    data = {"title": "Testing post", "content": "blablabla"}
    response = await client.post(
        "posts/create_post",
        headers=user_token,
        json=data
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["content"] == data["content"]
    assert "id" in content
    assert "author_id" in content

async def test_get_post(db_session: AsyncSession, client: AsyncClient, test_user: User):
    post = await create_random_post(db_session, test_user)
    data = jsonable_encoder(post)
    response = await client.get(
        f"/posts/post/{post.id}",
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["content"] == data["content"]
    assert content["id"] == data["id"]
    assert content["author_id"] == data["author_id"]

async def test_get_post_not_found(db_session: AsyncSession, client: AsyncClient):
    response = await client.get(
        "/posts/post/-1",
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"

async def test_get_posts(db_session: AsyncSession, client: AsyncClient, test_user: User):
    await create_random_post(db_session, test_user)
    await create_random_post(db_session, test_user)
    response = await client.get(
        "/posts/",
    )
    assert response.status_code == 200
    assert len(response.json()) >= 2

async def test_update_post(db_session: AsyncSession, client: AsyncClient, test_user: User, user_token):
    post = await create_random_post(db_session, test_user)
    data = {"title": "updated title", "content": "Updated content"}
    response = await client.patch(
        f"/posts/update/{post.id}",
        headers=user_token,
        json=data
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["content"] == data["content"]
    assert content["id"] == post.id
    assert content["author_id"] == test_user.id

async def test_update_post_not_author(db_session: AsyncSession, client: AsyncClient):
    post = await create_random_post(db_session)
    headers = await random_user_token(db_session, client)
    data = {"title": "updated title", "content": "Updated content"}
    response = await client.patch(
        f"/posts/update/{post.id}",
        headers=headers,
        json=data,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "You not the author of the post"

async def test_update_post_not_found(db_session: AsyncSession, client: AsyncClient, test_user: User, user_token):
    data = {"title": "updated title", "content": "Updated content"}
    response = await client.patch(
        "/posts/update/-1",
        headers=user_token,
        json=data

    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"

async def test_delete_post(db_session: AsyncSession, client: AsyncClient, test_user: User, user_token):
    post = await create_random_post(db_session, test_user)
    response = await client.delete(
        f"/posts/delete/{post.id}",
        headers=user_token,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "post deleted"

async def test_delete_post_not_found(db_session: AsyncSession, client: AsyncClient, user_token):
    response = await client.delete(
        "/posts/delete/-1",
        headers=user_token
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"

async def test_delete_post_not_author(db_session: AsyncSession, client: AsyncClient, user_token):
    post = await create_random_post(db_session)
    response = await client.delete(
        f"/posts/delete/{post.id}",
        headers=user_token,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "You not the author of the post"