import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from bkend import models, crud
from bkend.schemas import VoteType, ArticleCreate

TEST_DB_URL = os.environ["DATABASE_URL"]


@pytest.fixture()
def in_memory_db():
    engine = create_engine(TEST_DB_URL, future=True)
    models.Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        models.Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_create_user_and_lookup(in_memory_db):
    db = in_memory_db
    user = crud.create_user(db, email="alice@example.com", hashed_password="hashed")
    assert user.id is not None
    fetched = crud.get_user_by_email(db, email="alice@example.com")
    assert fetched is not None
    assert fetched.email == "alice@example.com"


def test_article_crud_and_votes(in_memory_db):
    db = in_memory_db
    # create user
    user = crud.create_user(db, email="bob@example.com", hashed_password="pw")
    # create article
    article_data = ArticleCreate(title="Hello", content="World", image_url="url")
    article = crud.create_article(db, article_data ,author_id=user.id)
    assert article.id is not None
    # initially no votes
    art = crud.get_article_with_votes(db, article.id, user.id)
    assert art is not None
    assert art["upvotes"] == 0
    assert art["downvotes"] == 0
    assert art["user_vote"] is None
    # add upvote
    crud.add_or_toggle_vote(db, article_id=article.id, user_id=user.id, vote_type=VoteType.UPVOTE)
    art = crud.get_article_with_votes(db, article.id, user.id)
    assert art is not None
    assert art["upvotes"] == 1
    assert art["user_vote"] == VoteType.UPVOTE.value
    # toggle same vote (removes it)
    crud.add_or_toggle_vote(db, article_id=article.id, user_id=user.id, vote_type=VoteType.UPVOTE)
    art = crud.get_article_with_votes(db, article.id, user.id)
    assert art is not None
    assert art["upvotes"] == 0
    assert art["user_vote"] is None
    # change vote to downvote
    crud.add_or_toggle_vote(db, article_id=article.id, user_id=user.id, vote_type=VoteType.DOWNVOTE)
    art = crud.get_article_with_votes(db, article.id, user.id)
    assert art is not None
    assert art["downvotes"] == 1
    assert art["user_vote"] == VoteType.DOWNVOTE.value
    # remove vote
    ok = crud.remove_vote(db, article_id=article.id, user_id=user.id)
    assert ok is True
    art = crud.get_article_with_votes(db, article.id, user.id)
    assert art is not None
    assert art["downvotes"] == 0


def test_update_and_delete_article(in_memory_db):
    db = in_memory_db
    user = crud.create_user(db, email="carol@example.com", hashed_password="pw")
    article_data = ArticleCreate(title="Old", content="Body", image_url="url")
    article = crud.create_article(db, article_data, author_id=user.id)
    updated = crud.update_article(db, article_id=article.id, title="New", image_url="u2", content=None)
    assert updated is not None
    assert updated.title == "New"
    assert updated.image_url == "u2"
    ok = crud.delete_article(db, article_id=article.id)
    assert ok is True
    missing = crud.get_article_with_votes(db, article_id=article.id, current_user_id=user.id)
    assert missing is None
