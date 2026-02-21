from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from typing import Annotated
from app.schemas.item import ItemPydantic, ItemCreate, ItemUpdate, ItemInDB
from app.database import get_session
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.item import Item
from app.schemas.user import UserInDB
from app.api.dependencies import get_current_user

router = APIRouter(
    prefix="/items",
    tags=["items"]
)


@router.get("/", response_model=list[ItemPydantic])
def get_items(search: Annotated[str | None, Query()],
              session: Annotated[Session, Depends(get_session)],
              skip: Annotated[int| None, Query(ge=0)] = None,
              limit: Annotated[int | None, Query(ge= 1, le=100)] = None):
    
    query = select(Item).filter(Item.name.contains(search)).offset(skip).limit(limit)
    result = session.execute(query)
    if len(result.scalars().all()) == 0:
        raise HTTPException(status_code=404, detail="Items not found")
    return result.scalars().all()

@router.post("/create", response_model=ItemPydantic)
def create_item(session: Annotated[Session, Depends(get_session)],
                item: Annotated[ItemCreate, Body()],
                user: Annotated[UserInDB, Depends(get_current_user)]):
    
    new_item = Item(**item.model_dump(), owner_id=user.id)
    session.add(new_item)
    session.commit()
    session.refresh(new_item)
    return new_item

@router.put("/update/{item_id}", response_model=ItemPydantic)
def update_item(session: Annotated[Session, Depends(get_session)],
                item_id: int,
                user: Annotated[UserInDB, Depends(get_current_user)],
                item: Annotated[ItemUpdate, Body()]):
    
    item_db = session.get(Item, item_id)
    if not item_db:
        raise HTTPException(status_code=404, detail="Item not found")
    elif item_db.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You not the owner of the Item")
    item_data = item.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(item_db, key, value)
    session.commit()
    session.refresh(item_db)
    return item_db

@router.post("/delete/{item_id}")
def delete_item(session: Annotated[Session, Depends(get_session)],
                item_id: int,
                user: Annotated[UserInDB, Depends(get_current_user)]):
    
    item = session.get(Item, item_id)
    if user.id != item.owner_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You not the owner of the Item")
    session.delete(item)
    session.flush()
    session.commit()
    return {"message": "item deleted"}

@router.get("/{item_id}", response_model=ItemPydantic)
def get_item(item_id: int, session: Annotated[Session, Depends(get_session)]):

    item = session.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item