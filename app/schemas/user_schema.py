from pydantic import BaseModel, Field, EmailStr, ConfigDict


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: EmailStr

class UserPydantic(UserBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    username: str | None = Field(default=None, min_length=3, max_length=30)
    email: EmailStr | None = None
    password: str | None = None

class UserInDB(UserBase):
    id: int
    hashed_password: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True) 