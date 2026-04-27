from enum import Enum
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

# Enum used by request/response schemas. Kept here to avoid creating a
# separate top-level module (like `types.py`) which can shadow stdlib
# modules and cause import-time issues. Keeping the enum next to the schemas
# that consume it reduces import-time complications.
class VoteType(Enum):
    UPVOTE = "upvote"
    DOWNVOTE = "downvote"

class Category(Enum):
    CRONY = "CRONY"
    NONSENSE = "NONSENSE"
    AI = "AI"
    GRIFT = "GRIFT"
    GRAFT = "GRAFT"


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
    image_url: str
    category: Category | None = None

class ArticleUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    category: Category | None = None
    image_url: str | None = None

class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str
    image_url: str
    author_id: int
    category: Category
    created_at: datetime
    updated_at: datetime
    upvotes: int
    downvotes: int
    user_vote: str | None = None

    model_config = ConfigDict(from_attributes=True)

class VoteCreate(BaseModel):
    vote_type: VoteType
