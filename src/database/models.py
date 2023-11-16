from datetime import date
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy import Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.connect import Base


class User(Base):
    """
    Represents a user in the application.

    Attributes:
        id (int): The unique identifier for the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        password (str): The hashed password of the user.
        created_at (date): The date and time when the user account was created.
        updated_at (date): The date and time when the user account was last updated.
        last_login_at (date): The date and time of the user's last login.
        last_request_at (date): The date and time of the user's last request.
        refresh_token (str): The refresh token for the user's session.
        confirmed (bool): Indicates if the user's email address has been confirmed.
        is_active (bool): Indicates if the user's account is active.

    Relationships:
        posts (relationship): A one-to-many relationship with the Post model, representing the user's posts.
        comments (relationship): A one-to-many relationship with the Comment model, representing the user's comments.
    """
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(250), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[date] = mapped_column("created_at", DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column("updated_at", DateTime, default=func.now(), onupdate=func.now())
    last_login_at: Mapped[date] = mapped_column(DateTime, nullable=True)
    last_request_at: Mapped[date] = mapped_column(DateTime, nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Post(Base):
    """
    Represents a post in the application.

    Attributes:
        id (int): The unique identifier for the post.
        post (str): The content of the post.
        likes (int): The number of likes received by the post.
        dislikes (int): The number of dislikes received by the post.
        created_at (date): The date and time when the post was created.

    Relationships:
        user (relationship): A many-to-one relationship with the User model, representing the post's author.
        comments (relationship): A one-to-many relationship with the Comment model, representing the post's comments.
    """
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post: Mapped[str] = mapped_column(Text, nullable=False)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    dislikes: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[date] = mapped_column("created_at", DateTime, default=func.now())
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship("User", backref="posts", lazy="joined")


class PostReaction(Base):
    """
    Represents a reaction to a post in the application.

    Attributes:
        id (int): The unique identifier for the reaction.
        post_id (int): The ID of the post to which the reaction is associated.
        user_id (int): The ID of the user who reacted to the post.
        reaction (str): The type of reaction, either 'like' or 'dislike'.
        created_at (date): The date and time when the reaction was created.
        updated_at (date): The date and time when the reaction was last updated.

    Constraints:
        UniqueConstraint: Ensures that there is only one reaction per user for a post.

    Relationships:
        None
    """
    __tablename__ = "post_reactions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    reaction: Mapped[str] = mapped_column(String(10))  # 'like' or 'dislike'
    created_at: Mapped[date] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column("updated_at", DateTime, default=func.now(), onupdate=func.now())
    __table_args__ = (UniqueConstraint('post_id', 'user_id', name='_post_user_uc'),)


class Comment(Base):
    """
    Represents a comment on a post in the application.

    Attributes:
        id (int): The unique identifier for the comment.
        comment (str): The content of the comment.
        created_at (date): The date and time when the comment was created.
        updated_at (date): The date and time when the comment was last updated.

    Relationships:
        post (relationship): A many-to-one relationship with the Post model, representing the commented post.
        user (relationship): A many-to-one relationship with the User model, representing the comment's author.
    """
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[date] = mapped_column("created_at", DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column("updated_at", DateTime, default=func.now(), onupdate=func.now())
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("posts.id"), nullable=False)
    post: Mapped["Post"] = relationship("Post", backref="comments", lazy="joined")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship("User", backref="comments", lazy="joined")
