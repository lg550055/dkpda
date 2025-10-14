from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import Article, User, Vote
from .schemas import VoteType

# Users
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.execute(select(User).where(User.email == email)).scalars().first()

def create_user(db: Session, email: str, hashed_password: str) -> User:
    user = User(email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Articles
def create_article(db: Session, title: str, content: str, author_id: int) -> Article:
    article = Article(title=title, content=content, author_id=author_id)
    db.add(article)
    db.commit()
    db.refresh(article)
    return article

def get_articles_with_votes(db: Session, current_user_id: int) -> List[Dict[str, Any]]:
    articles = db.execute(select(Article)).scalars().all()
    result = []
    for article in articles:
        upvotes = db.execute(select(func.count()).select_from(Vote).where(Vote.article_id == article.id, Vote.vote_type == VoteType.UPVOTE)).scalar_one()
        downvotes = db.execute(select(func.count()).select_from(Vote).where(Vote.article_id == article.id, Vote.vote_type == VoteType.DOWNVOTE)).scalar_one()
        user_vote = db.execute(select(Vote).where(Vote.article_id == article.id, Vote.user_id == current_user_id)).scalars().first()
        user_vote_type = user_vote.vote_type.value if user_vote else None
        result.append({**article.__dict__, "upvotes": upvotes, "downvotes": downvotes, "user_vote": user_vote_type})
    return result

def get_article_with_votes(db: Session, article_id: int, current_user_id: int) -> Optional[Dict[str, Any]]:
    article = db.execute(select(Article).where(Article.id == article_id)).scalars().first()
    if not article:
        return None
    upvotes = db.execute(select(func.count()).select_from(Vote).where(Vote.article_id == article.id, Vote.vote_type == VoteType.UPVOTE)).scalar_one()
    downvotes = db.execute(select(func.count()).select_from(Vote).where(Vote.article_id == article.id, Vote.vote_type == VoteType.DOWNVOTE)).scalar_one()
    user_vote = db.execute(select(Vote).where(Vote.article_id == article.id, Vote.user_id == current_user_id)).scalars().first()
    user_vote_type = user_vote.vote_type.value if user_vote else None
    return {**article.__dict__, "upvotes": upvotes, "downvotes": downvotes, "user_vote": user_vote_type}

def update_article(db: Session, article_id: int, title: Optional[str], content: Optional[str]) -> Optional[Article]:
    article = db.execute(select(Article).where(Article.id == article_id)).scalars().first()
    if not article:
        return None
    if title is not None:
        article.title = title
    if content is not None:
        article.content = content
    article.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(article)
    return article

def delete_article(db: Session, article_id: int) -> bool:
    article = db.execute(select(Article).where(Article.id == article_id)).scalars().first()
    if not article:
        return False
    db.delete(article)
    db.commit()
    return True

# Votes
def get_user_vote(db: Session, article_id: int, user_id: int) -> Optional[Vote]:
    return db.execute(select(Vote).where(Vote.article_id == article_id, Vote.user_id == user_id)).scalars().first()

def add_or_toggle_vote(db: Session, article_id: int, user_id: int, vote_type: VoteType) -> None:
    existing_vote = get_user_vote(db, article_id, user_id)
    if existing_vote:
        if existing_vote.vote_type == vote_type:
            db.delete(existing_vote)
        else:
            existing_vote.vote_type = vote_type
    else:
        new_vote = Vote(user_id=user_id, article_id=article_id, vote_type=vote_type)
        db.add(new_vote)
    db.commit()

def remove_vote(db: Session, article_id: int, user_id: int) -> bool:
    vote = get_user_vote(db, article_id, user_id)
    if not vote:
        return False
    db.delete(vote)
    db.commit()
    return True
