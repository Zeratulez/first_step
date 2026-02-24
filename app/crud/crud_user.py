from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from typing import Annotated
from app.schemas.user import UserCreate, UserPydantic
from app.database import get_session
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.user import User
from fastapi.security import OAuth2PasswordRequestForm
from app.api.dependencies import Token, authenticate_user, create_access_token, hash_password
from app.api.config import settings

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

@router.post("/register", response_model=UserPydantic)
def create_user(session: Annotated[Session, Depends(get_session)], user: Annotated[UserCreate, Body()]):
    hashed_password = hash_password(user.password)
    if session.query(User).filter(User.username == user.username).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exsits")
    new_user = User(**user.model_dump(exclude="password"), hashed_password=hashed_password, is_active=True)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@router.post("/token")
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)],
) -> Token:
    
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")