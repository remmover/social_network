from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf import messages
from src.database.connect import get_database_session
from src.database.models import User
from src.repository import analytics as repository_analytics
from src.schemas import PostAnalyticsListResponseSchema
from src.services.auth import auth_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/post/{post_id}/likes-dislikes", response_model=PostAnalyticsListResponseSchema)
async def get_post_likes_dislikes(
    post_id: int,
    start_date: date,
    end_date: date,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_database_session),
):
    """
    Retrieve likes and dislikes analytics for a specific post.

    Accepts a post ID and a date range. Returns the analytics data for likes and dislikes on the post within the
    specified date range. Raises a 400 HTTPException if the start date is later than the end date.
    """
    if start_date > end_date:
        raise HTTPException(status_code=400, detail=messages.INVALID_DATE_RANGE)

    analytics_data = await repository_analytics.get_post_analytics(
        post_id, start_date, end_date, current_user, db
    )
    response_model = PostAnalyticsListResponseSchema(analytics_data=analytics_data)
    return response_model
