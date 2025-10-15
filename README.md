# dkpda
Your source of daily satire

### Backend
FastAPI powering CRUD operations of articles, users, and voting.
Implemented with FastAPI, SQLAlchemy 2.0 style ORM, and Pydantic v2 schemas.
Unit tests are under `bkend/tests/`.

#### Quick start

These instructions assume you're working on Linux and will use the project's
virtualenv located at `bkend/venv/` (created previously). If you don't have a
virtualenv yet, create one and install dependencies from
`bkend/requirements.txt`.

1. Activate the virtualenv (optional but recommended):

```bash
source bkend/venv/bin/activate
```

2. Install dependencies (if not already installed):

```bash
pip install -r bkend/requirements.txt
```

#### Run the app

Preferred: run the package as a module from the repository root:

```bash
uvicorn bkend.main:app --reload
```

Avoid running `python main.py` from inside the `bkend/` directory since that
can change import resolution behaviour and accidentally shadow standard library modules.

#### Run tests

Run the test suite using the project's Python interpreter (virtualenv):

```bash
cd /path/to/dkpda
/path/to/dkpda/bkend/venv/bin/python -m pytest
```

You should see the unit tests pass (the project currently includes CRUD and
API unit tests).
