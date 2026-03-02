from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.comment import Comment
    from app.models.like import PostLike

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(30))
    content: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    user: Mapped["User"] = relationship(
        "app.models.user.User",
        back_populates="posts"
    )

    comments: Mapped[list["Comment"]] = relationship(
        "app.models.comment.Comment",
        back_populates="post"
    )

    users_likes: Mapped[list["PostLike"]] = relationship(
        "app.models.like.PostLike",
        back_populates="post"
    )
    liked_by: Mapped[list["User"]] = relationship(
        "app.models.user.User",
        secondary="post_likes",
        back_populates="liked_posts",
        viewonly=True
    )

    __table_args__ = (
        Index("title_index", "title"),
    )