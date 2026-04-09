from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.like import PostLike, CommentLike
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment

async def like_post(
        session: AsyncSession,
        user: User,
        post: Post,
):
    query = select(PostLike).filter(and_(PostLike.user_id == user.id, PostLike.post_id == post.id))
    already_liked = await session.scalar(query)
    if not already_liked:
        like = PostLike(user_id=user.id, post_id=post.id)
        session.add(like)
        await session.commit()
        await session.refresh(like)
        return like
    else:
        await session.delete(already_liked)
        await session.commit()
        return {"message": "Removed from liked posts"}

async def like_comment(
        session: AsyncSession,
        user: User,
        comment: Comment,
):
    query = select(CommentLike).filter(and_(CommentLike.user_id == user.id, CommentLike.comment_id == comment.id))
    already_liked = await session.scalar(query)
    if not already_liked:
        like = CommentLike(user_id=user.id, comment_id=comment.id)
        session.add(like)
        await session.commit()
        await session.refresh(like)
        return like
    else:
        await session.delete(already_liked)
        await session.commit()
        return {"message": "Removed from liked comments"}