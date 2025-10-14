import asyncio
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from bkend import models, crud, main as app_main
from bkend.schemas import VoteType, UserCreate, ArticleCreate, ArticleUpdate, VoteCreate


@pytest.fixture()
def in_memory_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    models.init_db(engine_override=engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def test_register_endpoint(in_memory_session):
    db = in_memory_session
    user_in = UserCreate(email="unit@example.com", password="pw")
    # Monkeypatch password hasher to avoid passlib/bcrypt backend issues in tests
    orig_hasher = app_main.get_password_hash
    app_main.get_password_hash = lambda p: "hashed_test"
    try:
        result = app_main.register(user_in, db)
    finally:
        app_main.get_password_hash = orig_hasher
    assert result.email == "unit@example.com"
    # duplicate registration should raise HTTPException
    with pytest.raises(Exception):
        app_main.register(user_in, db)


def test_article_crud_and_vote_flow(in_memory_session):
    db = in_memory_session
    # create admin user and promote
    admin = crud.create_user(db, email="ad@example.com", hashed_password="pw")
    admin.is_admin = True
    db.commit()

    # create voter user
    voter = crud.create_user(db, email="voter2@example.com", hashed_password="pw")

    # create article via endpoint
    art_in = ArticleCreate(title="Unit Article", content="body")
    created = app_main.create_article(art_in, current_user=admin, db=db)
    assert created["title"] == "Unit Article"
    article_id = created["id"]

    # get articles list via endpoint
    articles = app_main.get_articles(current_user=voter, db=db)
    assert any(a["id"] == article_id for a in articles)

    # vote via endpoint
    vote_in = VoteCreate(vote_type=VoteType.UPVOTE)
    resp = app_main.vote_article(article_id=article_id, vote=vote_in, current_user=voter, db=db)
    assert resp["message"] == "Vote recorded successfully"

    # check article shows upvote
    article = app_main.get_article(article_id=article_id, current_user=voter, db=db)
    assert article["upvotes"] == 1
    assert article["user_vote"] == "upvote"

    # remove vote
    resp = app_main.remove_vote(article_id=article_id, current_user=voter, db=db)
    assert resp["message"] == "Vote removed successfully"
    article = app_main.get_article(article_id=article_id, current_user=voter, db=db)
    assert article["upvotes"] == 0


def test_update_and_delete_endpoints(in_memory_session):
    db = in_memory_session
    admin = crud.create_user(db, email="ad2@example.com", hashed_password="pw")
    admin.is_admin = True
    db.commit()

    # create article
    art = crud.create_article(db, title="TBD", content="c", author_id=admin.id)

    # update
    updated = app_main.update_article(article_id=art.id, article_update=ArticleUpdate(title="NewTitle"), current_user=admin, db=db)
    assert updated["title"] == "NewTitle"

    # delete
    resp = app_main.delete_article(article_id=art.id, current_user=admin, db=db)
    assert resp is None

    # get should raise HTTPException
    with pytest.raises(Exception):
        app_main.get_article(article_id=art.id, current_user=admin, db=db)


def test_admin_users_endpoint_access_control(in_memory_session):
    db = in_memory_session
    # create non-admin user
    user = crud.create_user(db, email="normal@example.com", hashed_password="pw")

    # non-admin should be rejected: call the async admin-check helper directly
    with pytest.raises(Exception):
        asyncio.run(app_main.get_admin_user(user))

    # create admin user and ensure access
    admin = crud.create_user(db, email="admin@example.com", hashed_password="pw")
    admin.is_admin = True
    db.commit()

    users = app_main.list_all_users(current_user=admin, db=db)
    assert isinstance(users, list)
    assert any(u.email == "admin@example.com" for u in users)
