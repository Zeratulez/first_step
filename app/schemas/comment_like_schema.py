from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CommentLikeBase(BaseModel):
    user_id: int
    comment_id: int

class CommentLikePydantic(CommentLikeBase):
    id: int

class CommentLikeInDB(CommentLikeBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)