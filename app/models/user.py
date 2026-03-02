from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import String, Index
from sqlalchemy.orm import Mapped, mapped_column,relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.item import Item
    from app.models.post import Post
    from app.models.comment import Comment
    from app.models.like import PostLike, CommentLike

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    username: Mapped[str] = mapped_column(String(30))
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)

    items: Mapped[list["Item"]] = relationship(
        "app.models.item.Item",
        back_populates="user"
    )

    posts: Mapped[list["Post"]] = relationship(
        "app.models.post.Post",
        back_populates="user"
    )

    comments: Mapped[list["Comment"]] = relationship(
        "app.models.comment.Comment",
        back_populates="user"
    )

    posts_likes: Mapped[list["PostLike"]] = relationship(
        "app.models.like.PostLike",
        back_populates="user"
    )
    liked_posts: Mapped[list["Post"]] = relationship(
        "app.models.post.Post",
        secondary="post_likes",
        back_populates="liked_by",
        viewonly=True
    )

    comments_likes: Mapped[list["CommentLike"]] = relationship(
        "app.models.like.CommentLike",
        back_populates="user"
    )
    liked_comment: Mapped[list["Comment"]] = relationship(
        "app.models.comment.Comment",
        secondary="comment_likes",
        back_populates="liked_by",
        viewonly=True
    )

    __table_args__ = (
        Index("username_index", "username"),
    )
