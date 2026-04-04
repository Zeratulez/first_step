from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
from pydantic import EmailStr

from app.core.config import settings


password_hash = PasswordHash.recommended()

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def hash_password(plain_password):
    return password_hash.hash(plain_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password_reset_token(token: str):
    token_data = generate_reset_token(token)
    try:
        decoded_token = jwt.decode(token_data, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return decoded_token["sub"]
    except JWTError:
        return None
    
def generate_reset_token(email: EmailStr):
    expire = datetime.now(timezone.utc) + timedelta(minutes=10)
    to_encode = {"sub": email, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt