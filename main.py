from fastapi import FastAPI

from app.api.endpoints import items, auth

ap = FastAPI()

ap.include_router(items.router)
ap.include_router(auth.router)

