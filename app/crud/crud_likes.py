from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.models.like import PostLike, CommentLike
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment

def like_post(
        session: Session,
        user: User,
        post: Post,
):
    query = select(PostLike).filter(and_(PostLike.user_id == user.id, PostLike.post_id == post.id))
    already_liked = session.scalar(query)
    if not already_liked:
        like = PostLike(user_id=user.id, post_id=post.id)
        session.add(like)
        session.commit()
        session.refresh(like)
        return like
    else:
        session.delete(already_liked)
        session.commit()
        return {"message": "Removed from liked posts"}

def like_comment(
        session: Session,
        user: User,
        comment: Comment,
):
    query = select(CommentLike).filter(and_(CommentLike.user_id == user.id, CommentLike.comment_id == comment.id))
    already_liked = session.scalar(query)
    if not already_liked:
        like = CommentLike(user_id=user.id, comment_id=comment.id)
        session.add(like)
        session.commit()
        session.refresh(like)
        return like
    else:
        session.delete(already_liked)
        session.commit()
        return {"message": "Removed from liked comments"}