import pytest
from datetime import date, timedelta
from fastapi import HTTPException
from src.database.models import User, Post, PostReaction
from src.repository.analytics import get_post_analytics

# Replace with your actual import

# Mock Data
post_id = 1
user_id = 1
other_user_id = 2
user = User(id=user_id)
other_user = User(id=other_user_id)
date_from = date.today() - timedelta(days=7)
date_to = date.today()

@pytest.mark.asyncio
async def test_access_control(db_mock, post_mock):  # db_mock and post_mock are hypothetical fixtures
    # Assuming post_mock sets up a post belonging to 'other_user'
    with pytest.raises(HTTPException) as exc_info:
        await get_post_analytics(post_id, date_from, date_to, user, db_mock)
    assert exc_info.value.status_code == 400
    assert "not allowed to access analytics" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_date_range_filtering(db_mock, reactions_mock):  # reactions_mock is a hypothetical fixture
    # Assuming reactions_mock sets up reactions within and outside the date range
    analytics_data = await get_post_analytics(post_id, date_from, date_to, user, db_mock)
    for data in analytics_data:
        assert date_from <= data['date'] <= date_to

@pytest.mark.asyncio
async def test_reaction_counts(db_mock, reactions_mock):
    # reactions_mock should set up a known number of likes and dislikes
    analytics_data = await get_post_analytics(post_id, date_from, date_to, user, db_mock)
    for data in analytics_data:
        assert data['likes'] == expected_likes  # expected_likes should be set by the mock
        assert data['dislikes'] == expected_dislikes  # expected_dislikes should be set by the mock

@pytest.mark.asyncio
async def test_no_reactions_case(db_mock, empty_reactions_mock):  # empty_reactions_mock is a hypothetical fixture
    analytics_data = await get_post_analytics(post_id, date_from, date_to, user, db_mock)
    assert len(analytics_data) == 0 or all(data['likes'] == 0 and data['dislikes'] == 0 for data in analytics_data)

@pytest.mark.asyncio
async def test_invalid_date_range(db_mock):
    invalid_date_from = date_to + timedelta(days=1)
    with pytest.raises(ValueError):  # Assuming function raises ValueError for invalid date range
        await get_post_analytics(post_id, invalid_date_from, date_to, user, db_mock)

@pytest.mark.asyncio
async def test_non_existent_post(db_mock):
    non_existent_post_id = 9999  # Assuming this post ID does not exist in the mock
    with pytest.raises(HTTPException) as exc_info:
        await get_post_analytics(non_existent_post_id, date_from, date_to, user, db_mock)
    assert exc_info.value.status_code == 404

@pytest.mark.asyncio
async def test_data_format(db_mock, reactions_mock):
    analytics_data = await get_post_analytics(post_id, date_from, date_to, user, db_mock)
    for data in analytics_data:
        assert 'date' in data and isinstance(data['date'], date)
        assert 'likes' in data and isinstance(data['likes'], int)
        assert 'dislikes' in data and isinstance(data['dislikes'], int)
