from fastapi import APIRouter, Depends, status, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.background import BackgroundTasks

from src.conf import messages
from src.database.connect import get_database_session
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.schemas import UserResponseSchema, RequestEmailSchema, ResetPasswordSchema
from src.services.email_letters import send_reset_password_email

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserResponseSchema)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    Endpoint to get the current logged-in user's data.

    Uses JWT token to identify the current user and returns the user's information.
    """
    return current_user


@router.post("/reset_password_email")
async def reset_password_email(
    body: RequestEmailSchema,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_database_session),
):
    """
    Endpoint to initiate a password reset process by sending an email.

    Accepts an email address and sends a password reset link to that email if it exists in the database.
    """
    user = await repository_users.get_user_by_email(body.email, db)
    background_tasks.add_task(
        send_reset_password_email, user.email, user.username, request.base_url
    )
    return {"message": messages.PASSWORD_RESET_EMAIL_SUCCESS}


@router.post("/reset_password/{token}")
async def reset_password(
    token: str, body: ResetPasswordSchema, db: AsyncSession = Depends(get_database_session)
):
    """
    Endpoint to reset a user's password using a token received via email.

    Verifies the token and allows the user to set a new password.
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND
        )

    hashed_password = auth_service.get_password_hash(body.new_password)
    await repository_users.update_user_password(user, hashed_password, db)

    return {"message": messages.PASSWORD_RESET_SUCCESS}


@router.get("/user/{user_id}/activity")
async def get_user_activity(
    user_id: int,
    db: AsyncSession = Depends(get_database_session),
):
    """
    Endpoint to get a specific user's activity data, like last login and last request times.

    Requires the user's ID and returns their last login and request timestamps.
    """
    user = await repository_users.get_user_activity_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail=messages.USER_NOT_FOUND)

    return {
        "last_login_at": user.last_login_at,
        "last_request_at": user.last_request_at
    }
