from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.like import CommentLike
    from app.models.post import Post
    from app.models.user import User

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"))

    user: Mapped["User"] = relationship(
        "app.models.user.User",
        back_populates="comments"
    )

    post: Mapped["Post"] = relationship(
        "app.models.post.Post",
        back_populates="comments"
    )

    users_likes: Mapped[list["CommentLike"]] = relationship(
        "app.models.like.CommentLike",
        back_populates="comment"
    )
    liked_by: Mapped[list["User"]] = relationship(
        "app.models.user.User",
        secondary="comment_likes",
        back_populates="liked_comment",
        viewonly=True
    )

    __table_args__ = (
        Index("author_and_post_index", "author_id", "post_id"),
    )