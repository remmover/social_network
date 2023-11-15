from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf import messages
from src.database.models import Post, User, PostReaction


async def create_post(content: str, user: User, db: AsyncSession) -> Post:
    """
    Create a new post in the database.

    Accepts the post content as a string, the User object, and an AsyncSession instance.
    Returns the created Post object.
    """
    new_post = Post(post=content, user_id=user.id)
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return new_post


async def update_or_create_reaction(reaction: PostReaction, new_reaction: str, post: Post, db: AsyncSession):
    """
    Update an existing PostReaction or create a new one.

    Modifies the Post object's likes or dislikes count accordingly.
    """
    if reaction:
        stmt = update(PostReaction).where(PostReaction.id == reaction.id).values(reaction=new_reaction)
        await db.execute(stmt)
        if new_reaction == 'like':
            post.likes += 1
            post.dislikes -= 1
        else:
            post.likes -= 1
            post.dislikes += 1
    else:
        new_reaction_obj = PostReaction(post_id=post.id, user_id=post.user_id, reaction=new_reaction)
        db.add(new_reaction_obj)
        if new_reaction == 'like':
            post.likes += 1
        else:
            post.dislikes += 1


async def like_post(post_id: int, user: User, db: AsyncSession) -> Post:
    """
    Like a post by a user.

    Accepts the post ID, the User object, and an AsyncSession instance.
    Updates the PostReaction to 'like' if it exists, or creates a new one. Also updates the Post's likes count.
    Raises an HTTPException if the post does not exist or if the user has already liked the post.
    """
    existing_reaction = await get_post_reaction(post_id, user.id, db)
    post = await get_post_by_id(post_id, db)

    if existing_reaction and existing_reaction.reaction == 'like':
        raise HTTPException(status_code=400, detail=messages.ALREADY_LIKED)

    await update_or_create_reaction(existing_reaction, 'like', post, db)
    await db.commit()
    await db.refresh(post)
    return post


async def dislike_post(post_id: int, user: User, db: AsyncSession) -> Post:
    """
    Dislike a post by a user.

    Accepts the post ID, the User object, and an AsyncSession instance.
    Updates the PostReaction to 'dislike' if it exists, or creates a new one. Also updates the Post's dislikes count.
    Raises an HTTPException if the post does not exist or if the user has already disliked the post.
    """
    existing_reaction = await get_post_reaction(post_id, user.id, db)
    post = await get_post_by_id(post_id, db)

    if existing_reaction and existing_reaction.reaction == 'dislike':
        raise HTTPException(status_code=400, detail=messages.ALREADY_UNLIKED)

    await update_or_create_reaction(existing_reaction, 'dislike', post, db)
    await db.commit()
    await db.refresh(post)
    return post


async def get_post_reaction(post_id: int, user_id: int, db: AsyncSession) -> PostReaction:
    """
    Retrieve a PostReaction for a specific post and user.

    Returns the PostReaction object if it exists, otherwise None.
    """
    stmt = select(PostReaction).where(
        PostReaction.user_id == user_id,
        PostReaction.post_id == post_id
    )
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_post_by_id(post_id: int, db: AsyncSession) -> Post:
    """
    Retrieve a Post by its ID.

    Returns the Post object if found, otherwise raises an HTTPException with a 404 status code.
    """
    stmt = select(Post).where(Post.id == post_id)
    result = await db.execute(stmt)
    try:
        return result.scalars().one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail=messages.POST_NOT_FOUND)
