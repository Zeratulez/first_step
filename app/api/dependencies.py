import logging
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

logger = logging.getLogger(__name__)

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
    logger.info("Attempt to get current user")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        logger.info("Decoding jwt token")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            logger.warning("User is not found from jwt token")
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        logger.warning("JWTError raised")
        raise credentials_exception
    query = select(User).filter(User.username == token_data.username)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    if user is None:
        logger.warning("User is not found in DB")
        raise credentials_exception
    user = UserInDB.model_validate(user)
    if not user.is_active:
        logger.warning("User is not active", extra={"username": user.username})
        raise HTTPException(status_code=400, detail="Inactive user")
    logger.info("Successfully get current user")
    return user


async def authenticate_user(session: AsyncSession, username: str, password: str) -> UserInDB | None:
    logger.info("Authentication attempt", extra={"username": username})
    user =  await crud_user.get_user_by_username(session, username)
    if not user:
        logger.warning("Authentication failed: user not found", extra={"username": username})
        return False
    if not verify_password(password, user.hashed_password):
        logger.warning("Authentication failed: wrong password", extra={"username": username})
        return False
    logger.info("Authentication successful", extra={"username": username})
    return UserInDB.model_validate(user)