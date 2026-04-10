import logging
from fastapi import FastAPI

from app.api.endpoints import items, auth, posts, comments, users

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler()]
)

ap = FastAPI()

ap.include_router(items.router)
ap.include_router(auth.router)
ap.include_router(posts.router)
ap.include_router(comments.router)
ap.include_router(users.router)