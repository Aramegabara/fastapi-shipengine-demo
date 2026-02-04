# FastAPI Batches CRUD

A production-ready FastAPI boilerplate with async PostgreSQL, Redis caching, JWT authentication, and Batches CRUD operations.

## Features

- ⚡ **FastAPI** - Modern, fast web framework
- 🗄️ **PostgreSQL** - Async database with SQLAlchemy 2.0
- 🔴 **Redis** - Caching and session management
- 🔐 **JWT Authentication** - Secure user authentication
- 📦 **Batches CRUD** - Complete batch operations management
- 🐳 **Docker** - Containerized deployment
- ✅ **Testing** - Pytest with async support
- 📝 **Type Safety** - Pydantic v2 models

## Project Structure

```
src/
├── app/
│   ├── main.py              # FastAPI application instance
│   ├── api/
│   │   ├── dependencies.py  # Shared dependencies
│   │   ├── v1/
│   │   │   ├── login.py     # Authentication endpoints
│   │   │   ├── users.py     # User management
│   │   │   └── batches.py   # Batch operations endpoints
│   ├── core/
│   │   ├── config.py        # Application settings
│   │   ├── security.py      # JWT and password handling
│   │   └── database.py      # Database connection
│   ├── models/
│   │   ├── user.py          # User model
│   │   └── batch.py         # Batch models
│   ├── schemas/
│   │   ├── user.py          # User schemas
│   │   └── batch.py         # Batch schemas
│   ├── crud/
│   │   ├── crud_base.py     # Base CRUD class
│   │   ├── crud_user.py     # User operations
│   │   └── crud_batch.py    # Batch operations
│   └── utils/
│       ├── cache.py         # Redis caching utilities
│       └── helpers.py       # Helper functions
├── migrations/              # Alembic migrations
└── tests/                   # Test suite
```

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Docker (optional)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd RECRUT
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy environment variables:
```bash
cp .env.example .env
```

5. Update `.env` with your credentials:
```env
DATABASE_URL=postgresql+asyncpg://postgres:p4ssword@localhost:5432/fastapi_batches
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
```

### Database Setup

1. Create database:
```bash
createdb fastapi_batches
```

2. Run migrations:
```bash
alembic upgrade head
```

3. Create initial superuser:
```bash
python src/scripts/create_superuser.py
```

### Run Application

Development mode:
```bash
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

Access API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Docker Deployment

Build and run with Docker Compose:

```bash
docker-compose up -d
```

## API Endpoints

### Authentication
- `POST /api/v1/login` - Login and get JWT token
- `POST /api/v1/logout` - Logout user

### Users
- `GET /api/v1/users/me` - Get current user
- `POST /api/v1/users` - Create new user (superuser only)
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PUT /api/v1/users/{user_id}` - Update user (superuser only)
- `DELETE /api/v1/users/{user_id}` - Delete user (superuser only)

### Batches
- `POST /api/v1/batches/{batch_id}/add` - Add shipments/rates to batch
- `GET /api/v1/batches/{batch_id}` - Get batch details with caching
- `GET /api/v1/batches/{batch_id}/errors` - Get batch errors (paginated)
- `POST /api/v1/batches/{batch_id}/process/labels` - Process batch labels
- `POST /api/v1/batches/{batch_id}/remove` - Remove items from batch
- `DELETE /api/v1/batches/{batch_id}` - Delete batch completely

## Testing

Run tests with coverage:

```bash
pytest --cov=src tests/
```

## Development

Format code:
```bash
black src/
```

Lint code:
```bash
ruff src/
```

Type check:
```bash
mypy src/
```

## Environment Variables

See `.env.example` for all available configuration options.

## License

MIT

## Author

Artur (geraskov94@gmail.com)
