from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post
from app.schemas import post_schema, user_schema


async def get_posts(
        session: AsyncSession,
        search: str,
        skip: int,
        limit: int,
):
    query = select(Post).filter(Post.title.contains(search)).offset(skip).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()

async def create_post(
        session: AsyncSession,
        user: user_schema.UserInDB,
        post_data: post_schema.PostCreate,
):
    new_post = Post(**post_data.model_dump(), author_id=user.id)
    session.add(new_post)
    await session.commit()
    await session.refresh(new_post)
    return new_post

async def get_post_by_id(session: AsyncSession, post_id: int):
    return await session.get(Post, post_id)

async def update_post(
        session: AsyncSession,
        post_db: Post,
        post_data: post_schema.PostUpdate
):
    for key, value in post_data.model_dump(exclude_unset=True).items():
        setattr(post_db, key, value)
    await session.commit()
    await session.refresh(post_db)
    return post_db

async def delete_post(session: AsyncSession, post: Post):
    await session.delete(post)
    await session.commit()
    return {"message": "post deleted"}