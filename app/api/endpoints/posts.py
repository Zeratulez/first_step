import json
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.redis_client import invalidate_cache, redis_client
from app.crud import crud_comments, crud_likes, crud_posts
from app.database import get_async_session
from app.schemas import comment_schema, post_like_schema, post_schema, user_schema

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)


@router.get("/", response_model=list[post_schema.PostPydantic])
async def get_posts(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    search: Annotated[str | None, Query()] = "",
    skip: Annotated[int | None, Query(ge=0)] = 0,
    limit: Annotated[int | None, Query(ge=1, le=100)] = 10,
):
    cache_key = f"posts:search={search}:skip={skip}:limit={limit}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    posts = await crud_posts.get_posts(session, search, skip, limit)
    posts_data = [post_schema.PostPydantic.model_validate(post).model_dump(mode="json") for post in posts]
    await redis_client.set(cache_key, json.dumps(posts_data), ex=300, nx=True)
    return posts

@router.post("/create_post", response_model=post_schema.PostPydantic)
async def create_post(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[user_schema.UserInDB, Depends(get_current_user)],
    post_data: Annotated[post_schema.PostCreate, Body()],
):
    new_post = await crud_posts.create_post(session, user, post_data)
    await invalidate_cache()
    return new_post

@router.patch("/update/{post_id}", response_model=post_schema.PostPydantic)
async def update_post(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[user_schema.UserInDB, Depends(get_current_user)],
    post_data: Annotated[post_schema.PostUpdate, Body()],
    post_id: int,
):
    post_db = await crud_posts.get_post_by_id(session, post_id)
    if not post_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post_db.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You not the author of the post")
    updated_post = await crud_posts.update_post(session, post_db, post_data)
    await invalidate_cache(post_id)
    return updated_post

@router.delete("/delete/{post_id}")
async def delete_post(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[user_schema.UserInDB, Depends(get_current_user)],
    post_id: int
):
    post = await crud_posts.get_post_by_id(session, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You not the author of the post")
    await invalidate_cache(post_id)
    return await crud_posts.delete_post(session, post)

@router.get("/post/{post_id}", response_model=post_schema.PostPydantic)
async def get_post(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    post_id: int
):
    cache_key = f"post:{post_id}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    post = await crud_posts.get_post_by_id(session, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    post_data = post_schema.PostPydantic.model_validate(post).model_dump(mode="json")
    await redis_client.set(cache_key, json.dumps(post_data), ex=60, nx=True)
    return post

@router.get("/{post_id}/comments", response_model=list[comment_schema.CommentPydantic])
async def get_post_comments(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    post_id: int,
    skip: Annotated[int | None, Query(ge=0)] = 0,
    limit: Annotated[int | None, Query(ge=1, le=100)] = 10,
):
    post = await crud_posts.get_post_by_id(session, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    comments = await crud_comments.get_post_comments(session, post_id, skip, limit)
    return comments

@router.post("/{post_id}/create_comment", response_model=comment_schema.CommentPydantic)
async def create_comment(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    comment_data: Annotated[comment_schema.CommentCreate, Body()],
    user: Annotated[user_schema.UserInDB, Depends(get_current_user)],
    post_id: int,
):
    post = await crud_posts.get_post_by_id(session, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    new_comment = await crud_comments.create_comment(session, comment_data, user, post_id)
    return new_comment

@router.post("/{post_id}/like", response_model=post_like_schema.PostLikePydantic | dict)
async def like_post(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[user_schema.UserInDB, Depends(get_current_user)],
    post_id: int
):
    post = await crud_posts.get_post_by_id(session, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    like = await crud_likes.like_post(session, user, post)
    return like
