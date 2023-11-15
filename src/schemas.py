from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CommentResponseSchema(BaseModel):
    id: int
    created_at: datetime
    comment: str
    post_id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)


class CommentShowSchema(BaseModel):
    comment: str


class CommentShowAllSchema(BaseModel):
    comments: List[CommentShowSchema]


class CommentUpdateSchema(BaseModel):
    comment_id: int
    post_id: int
    comment: str = Field(max_length=300)


class PostAnalyticsResponseSchema(BaseModel):
    date: str
    likes: int
    dislikes: int


class PostAnalyticsListResponseSchema(BaseModel):
    analytics_data: List[PostAnalyticsResponseSchema]


class PostCreateResponseSchema(BaseModel):
    post: str


class PostDislikeResponseSchema(BaseModel):
    post: str
    dislikes: int


class PostLikeResponseSchema(BaseModel):
    post: str
    likes: int


class RequestEmailSchema(BaseModel):
    email: EmailStr


class ResetPasswordSchema(BaseModel):
    new_password: str
    r_new_password: str


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponseSchema(BaseModel):
    id: int
    username: str
    email: str
    model_config = ConfigDict(from_attributes=True)


class UserSchema(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: EmailStr
    password: str = Field(min_length=6, max_length=10)
