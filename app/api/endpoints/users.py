from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, Body, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import item_schema, user_schema
from app.crud import crud_user
from app.api.dependencies import get_current_user
from app.core.security import verify_password, hash_password
from app.database import get_async_session

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

@router.patch("/me/change_password")
async def change_password(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[user_schema.UserInDB, Depends(get_current_user)],
    password_data: Annotated[user_schema.UpdatePassword, Body()],
):
    verified = verify_password(password_data.current_password, user.hashed_password)
    if not verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")
    if password_data.new_password == password_data.current_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password cannot be the same as the current one")
    hashed_password = hash_password(password_data.new_password)
    user_db = await crud_user.get_user_by_id(session, user.id)
    return await crud_user.change_password(session, user_db, hashed_password)
    
