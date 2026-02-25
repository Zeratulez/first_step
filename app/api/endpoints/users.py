from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from sqlalchemy.orm import Session

from app.schemas import item_schema, user_schema
from app.crud import crud_user
from app.api.dependencies import get_current_user
from app.database import get_session

router = APIRouter(
    prefix="/user",
    tags=["user"]
)