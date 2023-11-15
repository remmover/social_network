from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf import messages
from src.database.connect import get_database_session
from src.database.models import User
from src.repository import posts as repository_posts
from src.schemas import PostCreateResponseSchema, PostLikeResponseSchema, PostDislikeResponseSchema
from src.services.auth import auth_service

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/", response_model=PostCreateResponseSchema)
async def create_post(
    content: str,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_database_session),
):
    """
    Create a new post.

    Accepts the post content as a string and adds it to the database, associating it with the current user.
    Raises an HTTPException if a post with the same content already exists.
    """
    try:
        new_post = await repository_posts.create_post(content, current_user, db)
    except IntegrityError:
        raise HTTPException(status_code=400, detail=messages.POST_EXISTS)
    return new_post


@router.post("/like", response_model=PostLikeResponseSchema)
async def like_post(
    post_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_database_session),
):
    """
    Like a post.

    Allows the current user to like a post identified by its ID. Raises an HTTPException if the post has already been
    liked.
    """
    try:
        like = await repository_posts.like_post(post_id, current_user, db)
    except IntegrityError:
        raise HTTPException(status_code=400, detail=messages.ALREADY_LIKED)
    return like


@router.post("/unlike", response_model=PostDislikeResponseSchema)
async def unlike_post(
    post_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_database_session),
):
    """
    Unlike a post.

    Allows the current user to unlike a post identified by its ID. Raises an HTTPException if the post has not been
    liked yet.
    """
    try:
        unlike = await repository_posts.dislike_post(post_id, current_user, db)
    except IntegrityError:
        raise HTTPException(status_code=400, detail=messages.ALREADY_UNLIKED)
    return unlike
