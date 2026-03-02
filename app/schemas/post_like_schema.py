from datetime import datetime
from pydantic import BaseModel, ConfigDict

class PostLikeBase(BaseModel):
    user_id: int
    post_id: int

class PostLikePydantic(PostLikeBase):
    id: int

class PostLikeInDB(PostLikeBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)