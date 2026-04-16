from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post
from app.models.user import User
from tests.utils.users import create_random_user
from tests.utils.utils import random_lower_string


async def create_random_post(db_session: AsyncSession, user: User = None):
    if user is None:
        user = await create_random_user(db_session)
    post = Post(
        title=random_lower_string(),
        content=random_lower_string(),
        author_id=user.id
    )
    db_session.add(post)
    await db_session.commit()
    await db_session.refresh(post)
    return post