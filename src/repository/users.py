from datetime import datetime
from typing import Optional, Union

from sqlalchemy import select, func
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request

from src.database.connect import get_database_session
from src.database.models import User
from src.schemas import UserSchema
from src.services.auth import auth_service


async def create_user(user_data: UserSchema, db: AsyncSession) -> User:
    """
    Create a new user in the database.

    Accepts user data in the form of UserSchema and an AsyncSession instance for database operations.
    Returns the newly created User object.
    """
    new_user = User(**user_data.dict())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def confirm_user_email(email: str, db: AsyncSession) -> None:
    """
    Confirm a user's email.

    Accepts an email string and an AsyncSession instance. Marks the user's email as confirmed in the database.
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def get_user_by_email(email: str, db: AsyncSession) -> Optional[User]:
    """
    Retrieve a user by email.

    Accepts an email string and an AsyncSession instance. Returns the User object if found, otherwise None.
    """
    stmt = select(User).filter(func.lower(User.email) == func.lower(email))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_user_password(user: User, new_password: str, db: AsyncSession) -> None:
    """
    Update a user's password.

    Accepts a User object, the new password string, and an AsyncSession instance. Updates the user's password in the
    database.
    """
    user.password = new_password
    await db.commit()


async def update_refresh_token(user: User, token: Union[str, None], db: AsyncSession) -> None:
    """
    Update a user's refresh token.

    Accepts a User object, a refresh token string or None, and an AsyncSession instance. Updates the user's refresh
    token in the database.
    """
    user.refresh_token = token
    await db.commit()


async def update_user_last_request(request: Request, call_next):
    """
    Middleware function to update the last request time for the authenticated user.

    Accepts a Request object and the call_next function. Extracts the user's token, identifies the user, and updates
    their last request time in the database.
    """
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token = token.split(" ", 1)[1]
    else:
        token = None

    response = await call_next(request)

    if token:
        current_user = await auth_service.get_current_user(token)
        if current_user:
            async for db in get_database_session():
                current_user.last_request_at = datetime.utcnow()
                db.add(current_user)
                await db.commit()
                break

    return response


async def get_user_activity_by_id(user_id: int, db: AsyncSession) -> Optional[User]:
    """
    Retrieve a user's activity by their ID.

    Accepts a user ID and an AsyncSession instance. Returns the User object with activity data if found, otherwise None.
    """
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    try:
        return result.scalars().one()
    except NoResultFound:
        return None
