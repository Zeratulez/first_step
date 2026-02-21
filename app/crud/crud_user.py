from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import Annotated
from app.schemas.user import UserCreate, UserPydantic
from app.database import get_session
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.user import User

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

@router.post("/create_user")
def create_user(session: Annotated[Session, Depends(get_session)], user: Annotated[UserCreate, Body()]):
    pass