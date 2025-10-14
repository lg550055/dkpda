from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select, func
from sqlalchemy.orm import sessionmaker, Session
from . import models
from . import schemas
from .types import VoteType
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, List
from .crud import (
    get_user_by_email,
    create_user,
    create_article as crud_create_article,
    get_articles_with_votes,
    get_article_with_votes,
    update_article as crud_update_article,
    delete_article as crud_delete_article,
    add_or_toggle_vote,
    remove_vote as crud_remove_vote,
)
from .models import User, Article, Vote

# Configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
DATABASE_URL = "sqlite:///./articles.db"

# Database setup (use models module)
# SessionLocal is a simple factory returning SQLAlchemy Session instances
engine = models.engine
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, class_=Session)
models.init_db()

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(title="Article Voting System")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if not isinstance(sub, str):
            raise credentials_exception
        token_data = schemas.TokenData(email=sub)
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

async def get_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user

# API Endpoints
@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    db_user = create_user(db, email=user.email, hashed_password=hashed_password)
    return db_user

@app.post("/token", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/articles", response_model=schemas.ArticleResponse, status_code=status.HTTP_201_CREATED)
def create_article(article: schemas.ArticleCreate, current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    db_article = crud_create_article(db, title=article.title, content=article.content, author_id=current_user.id)
    return {**db_article.__dict__, "upvotes": 0, "downvotes": 0, "user_vote": None}

@app.get("/articles", response_model=List[schemas.ArticleResponse])
def get_articles(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_articles_with_votes(db, current_user.id)

@app.get("/articles/{article_id}", response_model=schemas.ArticleResponse)
def get_article(article_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    article = get_article_with_votes(db, article_id, current_user.id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@app.put("/articles/{article_id}", response_model=schemas.ArticleResponse)
def update_article(article_id: int, article_update: schemas.ArticleUpdate, current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    db_article = crud_update_article(db, article_id=article_id, title=article_update.title, content=article_update.content)
    if not db_article:
        raise HTTPException(status_code=404, detail="Article not found")
    upvotes = db.execute(select(func.count()).select_from(Vote).where(Vote.article_id == db_article.id, Vote.vote_type == VoteType.UPVOTE)).scalar_one()
    downvotes = db.execute(select(func.count()).select_from(Vote).where(Vote.article_id == db_article.id, Vote.vote_type == VoteType.DOWNVOTE)).scalar_one()
    return {**db_article.__dict__, "upvotes": upvotes, "downvotes": downvotes, "user_vote": None}

@app.delete("/articles/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(article_id: int, current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    ok = crud_delete_article(db, article_id=article_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Article not found")
    return None

@app.post("/articles/{article_id}/vote", status_code=status.HTTP_200_OK)
def vote_article(article_id: int, vote: schemas.VoteCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    article = db.execute(select(Article).where(Article.id == article_id)).scalars().first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    add_or_toggle_vote(db, article_id=article_id, user_id=current_user.id, vote_type=vote.vote_type)
    return {"message": "Vote recorded successfully"}

@app.delete("/articles/{article_id}/vote", status_code=status.HTTP_200_OK)
def remove_vote(article_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ok = crud_remove_vote(db, article_id=article_id, user_id=current_user.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Vote not found")
    return {"message": "Vote removed successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
