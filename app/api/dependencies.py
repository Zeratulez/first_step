from typing import Annotated
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status, Path
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from jose import jwt, JWTError

from app.models.user import User
from app.database import get_async_session
from app.crud import crud_user
from app.core.config import settings
from app.schemas.user_schema import UserInDB
from app.core.security import verify_password, hash_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: Annotated[AsyncSession, Depends(get_async_session)]
) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    query = select(User).filter(User.username == token_data.username)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    user = UserInDB.model_validate(user)
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


async def authenticate_user(session: AsyncSession, username: str, password: str) -> UserInDB | None:
    user =  await crud_user.get_user_by_username(session, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return UserInDB.model_validate(user)