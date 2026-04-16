from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.comment import Comment
    from app.models.post import Post
    from app.models.user import User

class PostLike(Base):
    __tablename__ = "post_likes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship(
        "app.models.user.User",
        back_populates="posts_likes"
    )

    post: Mapped["Post"] = relationship(
        "app.models.post.Post",
        back_populates="users_likes"
    )

    __table_args__ = (
        Index("user_post_index", "user_id", "post_id"),
        UniqueConstraint("user_id", "post_id", name="unique_user_post_like"),
    )


class CommentLike(Base):
    __tablename__ = "comment_likes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    comment_id: Mapped[int] = mapped_column(ForeignKey("comments.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship(
        "app.models.user.User",
        back_populates="comments_likes"
    )

    comment: Mapped["Comment"] = relationship(
        "app.models.comment.Comment",
        back_populates="users_likes",
    )

    __table_args__ = (
        Index("user_comment_index", "user_id", "comment_id"),
        UniqueConstraint("user_id", "comment_id", name="unique_user_comment_like"),
    )