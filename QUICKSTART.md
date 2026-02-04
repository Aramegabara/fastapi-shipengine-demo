# Quick Start Guide

## Installation Steps

### 1. Create .env file

```bash
cp .env.example .env
```

Edit `.env` and update values if needed (database password is already set to `p4ssword`).

### 2. Install dependencies

Using pip:
```bash
pip install -r requirements.txt
```

Or using Poetry:
```bash
poetry install
```

### 3. Setup PostgreSQL

Create database:
```bash
createdb fastapi_batches
```

Or using psql:
```sql
CREATE DATABASE fastapi_batches;
```

### 4. Run migrations

```bash
alembic upgrade head
```

### 5. Create superuser

```bash
python src/scripts/create_superuser.py
```

Default credentials:
- Email: geraskov94@gmail.com
- Password: p4ssword

### 6. Start Redis

Using Docker:
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

Or install Redis locally.

### 7. Run application

Development mode:
```bash
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

Production mode:
```bash
uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Using Docker Compose (Easiest)

```bash
docker-compose up -d
```

This will start:
- PostgreSQL on port 5432
- Redis on port 6379
- FastAPI app on port 8000

## Access API

- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## Testing

Run tests:
```bash
pytest
```

With coverage:
```bash
pytest --cov=src tests/
```

## API Usage Examples

### 1. Login

```bash
curl -X POST "http://localhost:8000/api/v1/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=geraskov94@gmail.com&password=p4ssword"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Add items to batch

```bash
curl -X POST "http://localhost:8000/api/v1/batches/se-28529731/add" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_ids": ["se-28529731"],
    "rate_ids": ["se-28529731"]
  }'
```

### 3. Get batch information

```bash
curl -X GET "http://localhost:8000/api/v1/batches/se-28529731" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Get batch errors

```bash
curl -X GET "http://localhost:8000/api/v1/batches/se-28529731/errors?page=1&pagesize=25" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Process batch labels

```bash
curl -X POST "http://localhost:8000/api/v1/batches/se-28529731/process/labels" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ship_date": "2026-02-10T10:00:00",
    "label_layout": "4x6",
    "label_format": "pdf",
    "display_scheme": "label"
  }'
```

### 6. Remove items from batch

```bash
curl -X POST "http://localhost:8000/api/v1/batches/se-28529731/remove" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_ids": ["se-28529731"],
    "rate_ids": []
  }'
```

## Troubleshooting

### Database connection error

Make sure PostgreSQL is running and credentials in `.env` are correct.

### Redis connection error

Make sure Redis is running on port 6379 or update `REDIS_URL` in `.env`.

### Migration errors

Drop and recreate database:
```bash
dropdb fastapi_batches
createdb fastapi_batches
alembic upgrade head
```

### Import errors

Make sure you're running commands from the project root directory.

## Project Structure

```
RECRUT/
├── src/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Core configuration
│   │   ├── crud/          # Database operations
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── utils/         # Utility functions
│   │   └── main.py        # FastAPI application
│   └── scripts/           # Utility scripts
├── migrations/            # Alembic migrations
├── tests/                 # Test suite
├── docker-compose.yml     # Docker configuration
├── Dockerfile            # Docker image
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
└── README.md           # Full documentation
```

## Features Implemented

✅ FastAPI with async/await
✅ PostgreSQL with SQLAlchemy 2.0
✅ Redis caching
✅ JWT authentication
✅ Batches CRUD operations
✅ Error handling
✅ Pagination
✅ Docker support
✅ Database migrations
✅ Tests with pytest
✅ API documentation
✅ Type safety with Pydantic

## Contact

Author: Artur
Email: geraskov94@gmail.com
