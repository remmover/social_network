from datetime import date
from fastapi import HTTPException
from sqlalchemy import func, case, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.conf import messages
from src.database.models import PostReaction, User, Post


async def get_post_analytics(
    post_id,
    date_from: date,
    date_to: date,
    user: User,
    db: AsyncSession,
):
    """
    Get analytics data for a specific post within a specified date range.

    Args:
        post_id: The ID of the post for which analytics data is requested.
        date_from (date): The start date for the analytics data.
        date_to (date): The end date for the analytics data.
        user (User): The user requesting the analytics data.
        db (AsyncSession): The asynchronous database session.

    Returns:
        list[dict]: A list of dictionaries containing analytics data for each date within the specified range.
            Each dictionary contains the date, the number of 'likes', and the number of 'dislikes'.

    Raises:
        HTTPException: If the user does not have access to view the analytics data for the post.
    """
    owner_check_stmt = select(Post.user_id).where(Post.id == post_id)
    owner_result = await db.execute(owner_check_stmt)
    owner = owner_result.scalar_one_or_none()

    if owner != user.id:
        raise HTTPException(status_code=400, detail=messages.NOT_ACCESS_ANALYTICS)

    stmt = (
        select(
            func.date(PostReaction.created_at).label('date'),
            func.count(case((PostReaction.reaction == 'like', 1), else_=0)).label('likes'),
            func.count(case((PostReaction.reaction == 'dislike', 1), else_=0)).label('dislikes')
        )
        .where(
            and_(
                PostReaction.post_id == post_id,
                PostReaction.created_at >= date_from,
                PostReaction.created_at <= date_to
            )
        )
        .group_by(func.date(PostReaction.created_at))
    )

    result = await db.execute(stmt)
    reactions_data = result.all()

    return reactions_data
