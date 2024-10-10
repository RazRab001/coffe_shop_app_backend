from typing import List

from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette import status

from src.dependencies import get_db
from src.comment.schema import GettingCommentForItem, GettingCommentForUser, CreatingComment
from src.comment.service import create_comment_for_item, create_comment_for_user, get_comments_for_user, get_comments_for_item, delete_comment

router = APIRouter(
    prefix="/comment",
)


@router.post("/item/{item_id}", response_model=GettingCommentForItem)
async def create_item_comment(item_id: int, comment: CreatingComment, db: AsyncSession = Depends(get_db)) -> GettingCommentForItem:
    created_comment = await create_comment_for_item(item_id, comment, db)
    if not created_comment:
        raise HTTPException(status_code=400, detail="Failed to create comment")
    return created_comment


@router.post("/user/{user_id}", response_model=GettingCommentForUser)
async def create_user_comment(user_id: UUID, comment: CreatingComment, db: AsyncSession = Depends(get_db)) -> GettingCommentForUser:
    created_comment = await create_comment_for_user(user_id, comment, db)
    if not created_comment:
        raise HTTPException(status_code=400, detail="Failed to create comment")
    return created_comment


@router.get("/item/{item_id}", response_model=List[GettingCommentForItem])
async def get_item_comments(item_id: int, db: AsyncSession = Depends(get_db)) -> List[GettingCommentForItem]:
    try:
        return await get_comments_for_item(item_id, db)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@router.get("/user/{user_id}", response_model=List[GettingCommentForUser])
async def get_user_comments(user_id: UUID, db: AsyncSession = Depends(get_db)) -> List[GettingCommentForUser]:
    try:
        return await get_comments_for_user(user_id, db)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_one_item(comment_id: int, db: AsyncSession = Depends(get_db)) -> None:
    await delete_comment(comment_id, db)
