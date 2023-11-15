from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status, Security, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connect import get_database_session
from src.schemas import UserSchema, UserResponseSchema, TokenSchema, RequestEmailSchema
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.email_letters import send_email
from src.conf import messages

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserSchema,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_database_session),
):
    """
    Register a new user.

    Checks if a user with the provided email already exists. If not, creates a new user and sends a confirmation email.
    """
    existing_user = await repository_users.get_user_by_email(user_data.email, db)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=messages.ACCOUNT_EXIST)

    user_data.password = auth_service.get_password_hash(user_data.password)
    new_user = await repository_users.create_user(user_data, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post("/login", response_model=TokenSchema)
async def authenticate_user(
    login_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_database_session)
):
    """
    Authenticate a user.

    Validates the user's credentials and returns an access token and a refresh token if successful.
    """
    user = await repository_users.get_user_by_email(login_data.username, db)
    if user is None or not user.confirmed or not auth_service.verify_password(login_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_CREDENTIALS)

    user.last_login_at = datetime.utcnow()
    db.add(user)
    await db.commit()

    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_refresh_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/refresh_token", response_model=TokenSchema)
async def refresh_user_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(get_database_session),
):
    """
    Refresh the user's access token.

    Validates the refresh token and returns new access and refresh tokens.
    """
    refresh_token = credentials.credentials
    email = await auth_service.decode_refresh_token(refresh_token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != refresh_token:
        await repository_users.update_refresh_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_REFRESH_TOKEN)

    new_access_token = await auth_service.create_access_token(data={"sub": email})
    new_refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_refresh_token(user, new_refresh_token, db)
    return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}


@router.post("/request_email")
async def request_email_confirmation(
    email_request: RequestEmailSchema,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_database_session),
):
    """
    Request email confirmation.

    Sends a confirmation email to the user if they haven't confirmed their email yet.
    """
    user = await repository_users.get_user_by_email(email_request.email, db)
    if user and not user.confirmed:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
        return {"message": messages.CHECK_EMAIL_CONFIRMED}
    return {"message": messages.EMAIL_ALREADY_CONFIRMED}


@router.get("/confirmed_email/{token}")
async def confirm_email(
    token: str, db: AsyncSession = Depends(get_database_session)
):
    """
    Confirm the user's email address.

    Validates the confirmation token and marks the user's email as confirmed.
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None or user.confirmed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.INVALID_CONFIRMATION_TOKEN)

    await repository_users.confirm_user_email(email, db)
    return {"message": messages.EMAIL_CONFIRMED}
