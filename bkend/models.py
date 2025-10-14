from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, create_engine
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, Session, declarative_base, mapped_column, relationship

from .schemas import VoteType

DATABASE_URL = "sqlite:///./articles.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True,
)
SessionLocal = Session
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    votes: Mapped[List["Vote"]] = relationship(
        "Vote",
        back_populates="user",
    )


class Article(Base):
    __tablename__ = "articles"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    author_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
    author: Mapped[Optional[User]] = relationship("User")
    votes: Mapped[List["Vote"]] = relationship(
        "Vote",
        back_populates="article",
        cascade="all, delete-orphan",
    )


class Vote(Base):
    __tablename__ = "votes"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), nullable=False)
    vote_type: Mapped[VoteType] = mapped_column(
        SQLEnum(VoteType),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    user: Mapped[User] = relationship("User", back_populates="votes")
    article: Mapped[Article] = relationship("Article", back_populates="votes")


def init_db(base=None, engine_override=None):
    """Initialize DB tables. Pass a specific Base or engine_override for tests if needed."""
    base = base or Base
    eng = engine_override or engine
    base.metadata.create_all(bind=eng)
