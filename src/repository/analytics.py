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

    post = await db.get(Post, post_id)
    if post is None or post.user_id != user.id:
        raise HTTPException(status_code=403, detail=messages.NOT_ACCESS_ANALYTICS)

    stmt = select(PostReaction).where(
        and_(
            PostReaction.post_id == post_id,
            PostReaction.created_at.between(date_from, date_to)
        )
    )

    results = await db.execute(stmt)
    analytics_data = results.scalars().all()

    num_likes = sum(1 for r in analytics_data if r.reaction == 'like')
    num_dislikes = sum(1 for r in analytics_data if r.reaction == 'dislike')

    return {'likes': num_likes, 'dislikes': num_dislikes}
