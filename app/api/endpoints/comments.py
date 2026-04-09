from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import comment_schema, user_schema, comment_like_schema
from app.database import get_async_session
from app.crud import crud_comments, crud_likes
from app.api.dependencies import get_current_user

router = APIRouter(
    prefix="/comments",
    tags=["comments"]
)

@router.get("/", response_model=list[comment_schema.CommentPydantic])
async def get_comments_by_username(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    username: str,
    skip: Annotated[int | None, Query(ge=0)] = 0,
    limit: Annotated[int | None, Query(ge=1, le=100)] = 100,
):
    comments = await crud_comments.get_comments_by_username(session, username, skip, limit)
    return comments

@router.get("/{comment_id}", response_model=comment_schema.CommentPydantic)
async def get_comment(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        comment_id: int,
):
    comment = await crud_comments.get_comment_by_id(session, comment_id)
    return comment

@router.patch("/update/{comment_id}", response_model=comment_schema.CommentPydantic)
async def update_comment(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        user: Annotated[user_schema.UserInDB, Depends(get_current_user)],
        comment_data: Annotated[comment_schema.CommentUpdate, Body()],
        comment_id: int,
):
    comment_db = await crud_comments.get_comment_by_id(session, comment_id)
    if not comment_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment_db.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You not the author of the comment")
    updated_comment = await crud_comments.update_comment(session, comment_data, comment_db)
    return updated_comment

@router.delete("/delete/{comment_id}")
async def delete_comment(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[user_schema.UserInDB, Depends(get_current_user)],
    comment_id: int,
):
    comment = await crud_comments.get_comment_by_id(session, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You not the author of the comment")
    return await crud_comments.delete_comment(session, comment)

@router.post("/{comment_id}/like", response_model=comment_like_schema.CommentLikePydantic | dict)
async def like_comment(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[user_schema.UserInDB, Depends(get_current_user)],
    comment_id: int,
):
    comment = await crud_comments.get_comment_by_id(session, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    like = await crud_likes.like_comment(session, user, comment)
    return like