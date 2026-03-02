from sqlalchemy import select
from sqlalchemy.orm import Session, contains_eager

from app.models.comment import Comment
from app.models.user import User
from app.schemas import comment_schema, user_schema

def get_comment_by_id(session: Session, comment_id: int):
    return session.get(Comment, comment_id)

def get_comments_by_username(
        session: Session,
        username: str,
        skip: int,
        limit: int,
):
    query = (select(Comment)
            .join(Comment.user)
            .filter(User.username.contains(username))
            .options(contains_eager(Comment.user))
            .offset(skip)
            .limit(limit))
    result = session.execute(query).scalars().all()
    return result

def get_post_comments(
        session: Session,
        post_id: int,
        skip: int,
        limit: int,
):
    query = select(Comment).filter(Comment.post_id == post_id).offset(skip).limit(limit)
    result = session.execute(query).scalars().all()
    return result

def create_comment(
        session: Session,
        comment_data: comment_schema.CommentCreate,
        user: user_schema.UserInDB,
        post_id: int,
):
    new_comment = Comment(**comment_data.model_dump(), author_id=user.id, post_id=post_id)
    session.add(new_comment)
    session.commit()
    session.refresh(new_comment)
    return new_comment

def update_comment(
        session: Session,
        comment_data: comment_schema.CommentUpdate,
        comment_db: Comment,
):
    for key, value in comment_data.model_dump(exclude_unset=True).items():
        setattr(comment_db, key, value)
    session.commit()
    session.refresh(comment_db)
    return comment_db

def delete_comment(
        session: Session,
        comment: Comment,
):
    session.delete(comment)
    session.commit()
    return {"message": "comment deleted"}