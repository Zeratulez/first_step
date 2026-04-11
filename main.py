from fastapi import FastAPI

from app.api.endpoints import items, auth, posts, comments, users
from app.core.logging import setup_logging
from app.middleware.logging import LoggingMiddleware

setup_logging(is_production=False)

ap = FastAPI()
ap.add_middleware(LoggingMiddleware)

ap.include_router(items.router)
ap.include_router(auth.router)
ap.include_router(posts.router)
ap.include_router(comments.router)
ap.include_router(users.router)