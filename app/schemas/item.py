from pydantic import BaseModel, Field, ConfigDict


class ItemBase(BaseModel):
    name: str
    description: str | None = None
    price: float = Field(ge=0)
    tax: float | None = None


class ItemPydantic(ItemBase):
    id: int
    owner_id: int
    
    model_config = ConfigDict(from_attributes=True)

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    name: str | None = None
    description: str | None = None
    price: float | None = Field(default=None, ge=0)
    tax: float | None = None

class ItemInDB(ItemBase):
    id: int
    owner_id: int
