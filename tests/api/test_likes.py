from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_likes import like_comment, like_post
from app.models import User
from tests.utils.comments import create_random_comment
from tests.utils.posts import create_random_post


async def test_like_post(db_session: AsyncSession, client: AsyncClient, test_user: User, user_token):
    post = await create_random_post(db_session)
    response = await client.post(
        f"/posts/{post.id}/like",
        headers=user_token,
    )
    assert response.status_code == 200
    user_likes = await post.awaitable_attrs.users_likes
    assert len(user_likes) >= 1

async def test_unlike_post(db_session: AsyncSession, client: AsyncClient, test_user: User, user_token):
    post = await create_random_post(db_session)
    await like_post(db_session, test_user, post)
    response = await client.post(
        f"/posts/{post.id}/like",
        headers=user_token,
    )
    assert response.status_code == 200
    user_likes = await post.awaitable_attrs.users_likes
    assert len(user_likes) == 0

async def test_like_comment(db_session: AsyncSession, client: AsyncClient, test_user: User, user_token):
    post = await create_random_post(db_session)
    comment = await create_random_comment(db_session, post=post)
    response = await client.post(
        f"/comments/{comment.id}/like",
        headers=user_token
    )
    assert response.status_code == 200
    user_likes = await comment.awaitable_attrs.users_likes
    assert len(user_likes) >= 1

async def test_unlike_comment(db_session: AsyncSession, client: AsyncClient, test_user: User, user_token):
    post = await create_random_post(db_session)
    comment = await create_random_comment(db_session, post=post)
    await like_comment(db_session, test_user, comment)
    response = await client.post(
        f"/comments/{comment.id}/like",
        headers=user_token
    )
    assert response.status_code == 200
    user_likes = await comment.awaitable_attrs.users_likes
    assert len(user_likes) == 0