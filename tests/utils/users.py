from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models import User
from tests.utils.utils import random_lower_string


async def create_random_user(db_session: AsyncSession):
    user = User(
        username=random_lower_string(),
        email=f"{random_lower_string()}@{random_lower_string()}.com",
        hashed_password=hash_password("123"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

async def random_user_token(db_session: AsyncSession, client: AsyncClient):
    user = await create_random_user(db_session)
    response = await client.post(
        "/auth/login",
        data={"username": user.username, "password": "123"},
    )
    a_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers