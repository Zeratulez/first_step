from fastapi import FastAPI

from app.api.endpoints import items, auth, posts, comments

ap = FastAPI()

ap.include_router(items.router)
ap.include_router(auth.router)
ap.include_router(posts.router)
ap.include_router(comments.router)
