from __future__ import annotations
from sqlalchemy import String, Index
from sqlalchemy.orm import Mapped, mapped_column,relationship
from app.database import Base



class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    username: Mapped[str] = mapped_column(String(30))
    hashed_password: Mapped[str]
    is_active: Mapped[bool]

    items: Mapped[list["Item"]] = relationship(
        "app.models.item.Item",
        back_populates="user"
    )

    __table_args__ = (
        Index("username_index", "username"),
    )
