from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.crud import crud_item
from app.database import get_async_session
from app.schemas import item_schema, user_schema

router = APIRouter(
    prefix="/items",
    tags=["items"]
)

@router.get("/", response_model=list[item_schema.ItemPydantic])
async def read_items(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    search: Annotated[str | None, Query()] = "",
    skip: Annotated[int | None, Query(ge=0)] = 0,
    limit: Annotated[int | None, Query(ge=1, le=100)] = 10
):
    items = await crud_item.get_items(session, search, skip, limit)
    return items

@router.post("/create_item", response_model=item_schema.ItemPydantic)
async def create_item(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[user_schema.UserInDB, Depends(get_current_user)],
    item_data: Annotated[item_schema.ItemCreate, Body()]
):
    new_item = await crud_item.create_item(session, user, item_data)
    return new_item

@router.patch("/update/{item_id}", response_model=item_schema.ItemPydantic)
async def update_item(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[user_schema.UserInDB, Depends(get_current_user)],
    item_data: Annotated[item_schema.ItemUpdate, Body()],
    item_id: int
):
    item_db = await crud_item.get_item_by_id(session, item_id)
    if not item_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if item_db.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You not the owner of the item")
    updated_item = await crud_item.update_item(session, item_db, item_data)
    return updated_item

@router.delete("/delete/{item_id}")
async def delete_item(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[user_schema.UserInDB, Depends(get_current_user)],
    item_id: int
):
    item = await crud_item.get_item_by_id(session, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if item.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You not the owner of the item")
    return await crud_item.delete_item(session, item)

@router.get("/item/{item_id}", response_model=item_schema.ItemPydantic)
async def read_item(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    item_id: int
):
    item = await crud_item.get_item_by_id(session, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item
