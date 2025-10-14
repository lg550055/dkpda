import enum
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


# Enum used by request/response schemas. Kept here to avoid creating a
# separate top-level module (like `types.py`) which can shadow stdlib modules
# and cause import-time issues. This keeps the enum next to the schemas that
# consume it.
class VoteType(enum.Enum):
    UPVOTE = "upvote"
    DOWNVOTE = "downvote"


class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    is_admin: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

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

    model_config = ConfigDict(from_attributes=True)

class VoteCreate(BaseModel):
    vote_type: VoteType
