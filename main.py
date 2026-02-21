from typing import Annotated
from fastapi import FastAPI, Body
from pydantic import BaseModel, Field

from app.crud import crud_item

ap = FastAPI()

ap.include_router(crud_item.router)