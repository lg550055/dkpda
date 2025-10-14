from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from .types import VoteType


class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    is_admin: bool
    created_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str

class ArticleCreate(BaseModel):
    title: str
    content: str

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    created_at: datetime
    updated_at: datetime
    upvotes: int
    downvotes: int
    user_vote: Optional[str] = None

    class Config:
        orm_mode = True

class VoteCreate(BaseModel):
    vote_type: VoteType
