# Bookmarks API

A RESTful API for saving, tagging, and searching web bookmarks.

## Tech Stack

- Python 3.13
- FastAPI
- SQLAlchemy + Alembic
- SQLite
- JWT Authentication

## Getting Started

1. Clone the repo

2. Create a virtual environment and activate it
```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Copy the example env file and update values
```bash
cp .env.example .env
```

5. Run migrations
```bash
alembic upgrade head
```

6. Start the server
```bash
uvicorn app.main:app --reload
```

7. Visit http://localhost:8000/docs

## Running Tests

```bash
pytest -v
```

## API Endpoints

### Auth
- POST /api/auth/register
- POST /api/auth/login

### Bookmarks
- GET /api/bookmarks
- POST /api/bookmarks
- GET /api/bookmarks/{id}
- PUT /api/bookmarks/{id}
- DELETE /api/bookmarks/{id}
- GET /api/bookmarks/stats