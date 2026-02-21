from typing import Annotated
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.models.user import User
from sqlalchemy.orm import Session
from app.database import get_session
from app.schemas.user import UserInDB
from passlib.context import  CryptContext
from app.api.config import Settings
from pydantic import BaseModel
from jose import jwt, JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
password_hash = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                     session: Annotated[Session, Depends(get_session)]) -> UserInDB:
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, Settings.SECRET_KEY, algorithms=[Settings.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = session.query(User).filter(User.username == token_data.username)
    if user is None:
        raise credentials_exception
    return UserInDB.model_validate(user)


def verify_password(plain_password, hashed_password):

    return password_hash.verify(plain_password, hashed_password)


def hash_password(plain_password):

    return password_hash.hash(plain_password)


def authenticate_user(user: Annotated[UserInDB, Depends(get_current_user)], password: str):

    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Settings.SECRET_KEY, algorithm=Settings.ALGORITHM)
    return encoded_jwt