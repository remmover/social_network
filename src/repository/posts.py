from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf import messages
from src.database.models import Post, User, PostReaction


async def create_post(content: str, user: User, db: AsyncSession) -> Post:
    """
    Create a new post in the database.

    Parameters:
        - content (str): The content of the post.
        - user (User): The User object associated with the post.
        - db (AsyncSession): The AsyncSession instance.

    Returns:
        Post: The created Post object.
    """
    new_post = Post(post=content, user_id=user.id)
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return new_post


async def like_post(post_id: int, user: User, db: AsyncSession) -> Post:
    """
    Like a post and update the corresponding reactions in the database.

    Parameters:
        - post_id (int): The ID of the post to be liked.
        - user (User): The User object performing the like.
        - db (AsyncSession): The AsyncSession instance.

    Returns:
        Post: The updated Post object.
    """
    stmt = select(PostReaction).where(
        PostReaction.user_id == user.id,
        PostReaction.post_id == post_id
    )
    result = await db.execute(stmt)
    existing_reaction = result.scalars().first()

    stmt = select(Post).where(Post.id == post_id)
    result = await db.execute(stmt)
    try:
        post = result.scalars().one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail=messages.POST_NOT_FOUND)

    if existing_reaction:
        if existing_reaction.reaction == 'like':
            raise HTTPException(status_code=400, detail=messages.ALREADY_LIKED)
        else:

            stmt = (
                update(PostReaction)
                .where(PostReaction.id == existing_reaction.id)
                .values(reaction='like')
            )
            await db.execute(stmt)
            post.likes += 1
            post.dislikes -= 1
    else:

        new_reaction = PostReaction(
            post_id=post_id,
            user_id=user.id,
            reaction='like'
        )
        db.add(new_reaction)
        post.likes += 1

    await db.commit()
    await db.refresh(post)

    return post


async def dislike_post(post_id: int, user: User, db: AsyncSession) -> Post:
    """
    Dislike a post and update the corresponding reactions in the database.

    Parameters:
        - post_id (int): The ID of the post to be disliked.
        - user (User): The User object performing the dislike.
        - db (AsyncSession): The AsyncSession instance.

    Returns:
        Post: The updated Post object.
    """
    stmt = select(PostReaction).where(
        PostReaction.user_id == user.id,
        PostReaction.post_id == post_id
    )
    result = await db.execute(stmt)
    existing_reaction = result.scalars().first()

    stmt = select(Post).where(Post.id == post_id)
    result = await db.execute(stmt)
    try:
        post = result.scalars().one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail=messages.POST_NOT_FOUND)

    if existing_reaction:
        if existing_reaction.reaction == 'dislike':
            raise HTTPException(status_code=400, detail=messages.ALREADY_UNLIKED)
        else:

            stmt = (
                update(PostReaction)
                .where(PostReaction.id == existing_reaction.id)
                .values(reaction='dislike')
            )
            await db.execute(stmt)
            post.likes -= 1
            post.dislikes += 1
    else:

        new_reaction = PostReaction(
            post_id=post_id,
            user_id=user.id,
            reaction='dislike'
        )
        db.add(new_reaction)
        post.dislikes += 1

    await db.commit()
    await db.refresh(post)

    return post
