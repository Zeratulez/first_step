from typing import Annotated
from fastapi import FastAPI, Body
from pydantic import BaseModel, Field

from app.crud import crud_item, crud_user

ap = FastAPI()

ap.include_router(crud_item.router)
ap.include_router(crud_user.router)

