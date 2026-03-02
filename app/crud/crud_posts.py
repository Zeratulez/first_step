from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.post import Post
from app.schemas import post_schema, user_schema


def get_posts(
        session: Session,
        search: str,
        skip: int,
        limit: int,
):
    query = select(Post).filter(Post.title.contains(search)).offset(skip).limit(limit)
    result = session.scalars(query).all()
    return result

def create_post(
        session: Session,
        user: user_schema.UserInDB,
        post_data: post_schema.PostCreate,
):
    new_post = Post(**post_data.model_dump(), author_id=user.id)
    session.add(new_post)
    session.commit()
    session.refresh(new_post)
    return new_post

def get_post_by_id(session: Session, post_id: int):
    return session.get(Post, post_id)

def update_post(
        session: Session,
        post_db: Post,
        post_data: post_schema.PostUpdate
):
    for key, value in post_data.model_dump(exclude_unset=True).items():
        setattr(post_db, key, value)
    session.commit()
    session.refresh(post_db)
    return post_db

def delete_post(session: Session, post: Post):
    session.delete(post)
    session.commit()
    return {"message": "post deleted"}