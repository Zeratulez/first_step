from pydantic import BaseModel, ConfigDict, Field


class PostBase(BaseModel):
    title: str = Field(min_length=3, max_length=30)
    content: str

class PostPydantic(PostBase):
    id: int
    author_id: int

    model_config = ConfigDict(from_attributes=True)

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    title: str | None = Field(default=None, min_length=3, max_length=30)
    content: str | None = None

class PostInDB(PostBase):
    id: int
    author_id: int

    model_config = ConfigDict(from_attributes=True)