from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Body, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from app.schemas import user_schema
from app.crud import crud_user
from app.database import get_async_session
from app.api.dependencies import hash_password, authenticate_user, Token
from app.core.security import create_access_token, hash_password, verify_password_reset_token
from app.core.config import settings

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/register", response_model=user_schema.UserPydantic)
async def register_user(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user_data: Annotated[user_schema.UserCreate, Body()]
):
    user = await crud_user.get_user_by_username(session, user_data.username)
    hashed_password = hash_password(user_data.password)
    if user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this nickname already exists")
    return await crud_user.create_user(session, user_data, hashed_password)


@router.post("/login", response_model=Token)
async def login_for_access_token(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")

@router.post("/reset_password")
async def reset_password(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    email_body: Annotated[str, Body()],
    new_password: Annotated[str, Body()],
):
    email = verify_password_reset_token(email_body)
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    user = await crud_user.get_user_by_email(session, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account with this email does not exist")
    elif not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not active")
    hashed_password = hash_password(new_password)
    return await crud_user.change_password(session, user, hashed_password)
    
