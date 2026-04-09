from sqlalchemy import select
from sqlalchemy.orm import contains_eager
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.models.user import User
from app.schemas import comment_schema, user_schema

async def get_comment_by_id(session: AsyncSession, comment_id: int):
    return await session.get(Comment, comment_id)

async def get_comments_by_username(
        session: AsyncSession,
        username: str,
        skip: int,
        limit: int,
):
    query = (select(Comment)
            .join(Comment.user)
            .filter(User.username == username)
            .options(contains_eager(Comment.user))
            .offset(skip)
            .limit(limit))
    result = await session.execute(query)
    return result.scalars().all()

async def get_post_comments(
        session: AsyncSession,
        post_id: int,
        skip: int,
        limit: int,
):
    query = select(Comment).filter(Comment.post_id == post_id).offset(skip).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()

async def create_comment(
        session: AsyncSession,
        comment_data: comment_schema.CommentCreate,
        user: user_schema.UserInDB,
        post_id: int,
):
    new_comment = Comment(**comment_data.model_dump(), author_id=user.id, post_id=post_id)
    session.add(new_comment)
    await session.commit()
    await session.refresh(new_comment)
    return new_comment

async def update_comment(
        session: AsyncSession,
        comment_data: comment_schema.CommentUpdate,
        comment_db: Comment,
):
    for key, value in comment_data.model_dump(exclude_unset=True).items():
        setattr(comment_db, key, value)
    await session.commit()
    await session.refresh(comment_db)
    return comment_db

async def delete_comment(
        session: AsyncSession,
        comment: Comment,
):
    await session.delete(comment)
    await session.commit()
    return {"message": "comment deleted"}