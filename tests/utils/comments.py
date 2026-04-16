from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User
from tests.utils.posts import create_random_post
from tests.utils.users import create_random_user
from tests.utils.utils import random_lower_string


async def create_random_comment(db_session: AsyncSession, user: User = None, post: Post = None):
    if user is None:
        user = await create_random_user(db_session)
    if post is None:
        post = await create_random_post(db_session)
    comment = Comment(
        content=random_lower_string(),
        author_id=user.id,
        post_id=post.id
    )
    db_session.add(comment)
    await db_session.commit()
    await db_session.refresh(comment)
    return comment