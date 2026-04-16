from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from tests.utils.comments import create_random_comment
from tests.utils.posts import create_random_post


async def test_get_post_comments(db_session: AsyncSession, client: AsyncClient):
    post = await create_random_post(db_session)
    comment = await create_random_comment(db_session, post=post)
    response = await client.get(
        f"/posts/{post.id}/comments",
    )
    assert response.status_code == 200
    assert response.json()[0]["content"] == jsonable_encoder(comment)["content"]

async def test_create_comment(db_session: AsyncSession, client: AsyncClient, test_user: User, user_token):
    post = await create_random_post(db_session, test_user)
    data = {"content": "Some cool comment"}
    response = await client.post(
        f"/posts/{post.id}/create_comment",
        headers=user_token,
        json=data
    )
    assert response.status_code == 200
    content = response.json()
    assert content["content"] == data["content"]
    assert "id" in content
    assert content["author_id"] == test_user.id
    assert content["post_id"] == post.id

async def test_create_comment_but_post_not_exist(db_session: AsyncSession, client: AsyncClient, test_user: User, user_token):
    data = {"content": "blablabla"}
    response = await client.post(
        "/posts/-1/create_comment",
        headers=user_token,
        json=data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"