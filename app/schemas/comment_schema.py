from pydantic import BaseModel, Field, ConfigDict

class CommentBase(BaseModel):
    content: str

class CommentPydantic(CommentBase):
    id: int
    author_id: int
    post_id: int

    model_config = ConfigDict(from_attributes=True)

class CommentCreate(CommentBase):
    pass

class CommentUpdate(CommentBase):
    content: str | None = None

class CommentInDB(CommentBase):
    id: int
    author_id: int
    post_id: int

    model_config = ConfigDict(from_attributes=True)