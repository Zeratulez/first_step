from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Body, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import EmailStr

from app.schemas import user_schema
from app.crud import crud_user
from app.database import get_session
from app.api.endpoints.users import change_password
from app.api.dependencies import hash_password, create_access_token, authenticate_user, Token, verify_password_reset_token, generate_reset_token
from app.core.config import settings

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/register", response_model=user_schema.UserPydantic)
def register_user(
    session: Annotated[Session, Depends(get_session)],
    user: Annotated[user_schema.UserCreate, Body()]
):
    hashed_password = hash_password(user.password)
    if crud_user.get_user_by_username(session, user.username) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this nickname already exists")
    return crud_user.create_user(session, user, hashed_password)


@router.post("/login", response_model=Token)
def login_for_access_token(
    session: Annotated[Session, Depends(get_session)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(session, form_data.username, form_data.password)
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
def reset_password(
    session: Annotated[Session, Depends(get_session)],
    body: Annotated[str, Body()],
    new_password: Annotated[str, Body()],
):
    email = verify_password_reset_token(body)
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    user = crud_user.get_user_by_email(session, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account with this email does not exist")
    elif not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not active")
    hashed_password = hash_password(new_password)
    return crud_user.change_password(session, user, hashed_password)
    
