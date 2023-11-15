from datetime import datetime
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Comment, User
from src.schemas import CommentUpdateSchema


async def create_new_comment(comment: str, user_id: User, post_id: int, db: AsyncSession) -> Comment:
    """
    Create a new comment and store it in the database.

    Args:
        comment (str): The text of the comment.
        user_id (User): The user who is creating the comment.
        post_id (int): The ID of the post the comment is associated with.
        db (AsyncSession): The asynchronous database session.

    Returns:
        Comment: The newly created comment.
    """
    comment = Comment(
        comment=comment,
        user_id=user_id,
        post_id=post_id,
    )

    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def get_comments_for_post(post_id: int, db: AsyncSession):
    """
    Retrieve comments for a specific post.

    Args:
        post_id (int): The ID of the post.

    Returns:
        List[Comment]: A list of comments associated with the post, ordered by creation date.
    """
    stmt = (
        select(Comment)
        .where(Comment.post_id == post_id)
        .order_by(desc(Comment.created_at))
    )
    results = await db.execute(stmt)
    comments = results.scalars().all()
    return comments


async def update_comment_text(comment_update: CommentUpdateSchema, user: User, db: AsyncSession):
    """
    Update the text of a comment if the user has permission.

    Args:
        comment_update (CommentUpdateSchema): The updated comment data.
        user (User): The user who is updating the comment.
        db (AsyncSession): The asynchronous database session.

    Returns:
        Comment: The updated comment or None if the comment doesn't exist or the user doesn't have permission.
    """
    sq = select(Comment).filter(and_(Comment.id == comment_update.comment_id,
                                     or_(Comment.user_id == user.id)))

    result = await db.execute(sq)
    comment = result.scalar_one_or_none()

    if comment:
        comment.comment = comment_update.comment
        comment.updated_at = datetime.now()
        await db.commit()
    return comment
