from typing import Optional, List
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, delete, select, UUID
from datetime import datetime
from src.comment.model import comment, comment_user, comment_item
from src.comment.schema import CreatingComment, GettingCommentForItem, GettingCommentForUser


async def create_comment_for_item(item_id: int, comment_data: CreatingComment, db: AsyncSession) -> Optional[GettingCommentForItem]:
    try:
        stmt = insert(comment).values(
            value=comment_data.stars,
            body=comment_data.comment,
            date=datetime.utcnow()
        ).returning(comment.c.id, comment.c.value, comment.c.body, comment.c.date)
        result = await db.execute(stmt)
        await db.commit()

        comment_row = result.fetchone()

        if comment_row:
            stmt_item = insert(comment_item).values(
                comment_id=comment_row.id,
                item_id=item_id
            )
            await db.execute(stmt_item)
            await db.commit()

            return GettingCommentForItem(
                id=comment_row.id,
                stars=comment_row.value,
                comment=comment_row.body,
                item_id=item_id,
                date=comment_row.date.isoformat()
            )

    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Error creating comment for item: {e}")
        raise e


async def create_comment_for_user(user_id: UUID, comment_data: CreatingComment, db: AsyncSession) -> Optional[GettingCommentForUser]:
    try:
        stmt = insert(comment).values(
            value=comment_data.stars,
            body=comment_data.comment,
            date=datetime.utcnow()
        ).returning(comment.c.id, comment.c.value, comment.c.body, comment.c.date)
        result = await db.execute(stmt)
        await db.commit()

        comment_row = result.fetchone()

        if comment_row:
            stmt_user = insert(comment_user).values(
                comment_id=comment_row.id,
                user_id=user_id
            )
            await db.execute(stmt_user)
            await db.commit()

            return GettingCommentForUser(
                id=comment_row.id,
                stars=comment_row.value,
                comment=comment_row.body,
                user_id=user_id,
                date=comment_row.date.isoformat()
            )

    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Error creating comment for user: {e}")
        raise e


async def get_comments_for_item(item_id: int, db: AsyncSession) -> List[GettingCommentForItem]:
    try:
        stmt = select(comment.c.id, comment.c.value, comment.c.body, comment.c.date).join(comment_item).where(comment_item.c.item_id == item_id)
        result = await db.execute(stmt)
        comments = result.fetchall()

        return [
            GettingCommentForItem(
                id=row.id,
                stars=row.value,
                comment=row.body,
                item_id=item_id,
                date=row.date.isoformat()
            )
            for row in comments
        ]

    except SQLAlchemyError as e:
        print(f"Error retrieving comments for item: {e}")
        raise e


async def get_comments_for_user(user_id: UUID, db: AsyncSession) -> List[GettingCommentForUser]:
    try:
        stmt = select(comment.c.id, comment.c.value, comment.c.body, comment.c.date).join(comment_user).where(comment_user.c.user_id == user_id)
        result = await db.execute(stmt)
        comments = result.fetchall()

        return [
            GettingCommentForUser(
                id=row.id,
                stars=row.value,
                comment=row.body,
                user_id=user_id,
                date=row.date.isoformat()
            )
            for row in comments
        ]

    except SQLAlchemyError as e:
        print(f"Error retrieving comments for user: {e}")
        raise e


async def delete_comment(comment_id: int, db: AsyncSession) -> bool:
    try:
        await db.execute(delete(comment_user).where(comment_user.c.comment_id == comment_id))
        await db.execute(delete(comment_item).where(comment_item.c.comment_id == comment_id))

        stmt = delete(comment).where(comment.c.id == comment_id)
        result = await db.execute(stmt)
        await db.commit()

        return result.rowcount > 0

    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Error deleting comment: {e}")
        raise e
