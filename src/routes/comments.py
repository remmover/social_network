from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf import messages
from src.database.connect import get_database_session
from src.database.models import Post, User
from src.schemas import CommentShowAllSchema, CommentUpdateSchema, CommentResponseSchema
from src.services.auth import auth_service
from src.repository import comments as repository_comments

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/", response_model=CommentResponseSchema)
async def create_comment(
    post_id: int,
    comment: str,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_database_session),
):
    """
    Create a new comment for a specific post.

    Accepts a post ID and comment content. Validates if the post exists before creating the comment.
    Raises a 404 HTTPException if the post is not found.
    """
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail=messages.POST_NOT_FOUND)

    new_comment = await repository_comments.create_new_comment(
        comment, current_user.id, post_id, db
    )
    return new_comment


@router.put("/update")
async def update_comment(
    body: CommentUpdateSchema,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_database_session),
):
    """
    Update an existing comment.

    Accepts a CommentUpdateSchema containing the comment ID and new content.
    Returns the updated comment or raises a 404 HTTPException if the comment is not found.
    """
    updated_comment = await repository_comments.update_comment_text(body, current_user, db)

    if not updated_comment:
        raise HTTPException(status_code=404, detail=messages.COMMENT_NOT_FOUND)

    return {
        "comment_id": updated_comment.id,
        "post_id": updated_comment.post_id,
        "comment": updated_comment.comment,
        "message": messages.COMMENT_UPDATED
    }


@router.get("/posts/{post_id}/comments/", response_model=CommentShowAllSchema)
async def get_comments(
    post_id: int = Path(..., description="The ID of the post"),
    db: AsyncSession = Depends(get_database_session),
):
    """
    Get all comments for a specific post.

    Accepts a post ID and returns all associated comments. Raises a 404 HTTPException if no comments are found.
    """
    comments = await repository_comments.get_comments_for_post(post_id, db)
    if comments:
        return {"comments": comments}

    raise HTTPException(status_code=404, detail=messages.COMMENT_NOT_FOUND)
