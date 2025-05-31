# FastAPI Backend Application

This is a FastAPI backend application following a layered architecture pattern. The application is structured to separate concerns into different layers:

- **Models Layer**: Contains database models and domain entities
- **Services Layer**: Implements business logic
- **Repositories Layer**: Handles data access and persistence
- **API Layer**: Manages HTTP endpoints and request/response handling
- **Core Layer**: Contains configuration and shared utilities

## Project Structure

```
backend/
├── app/                    # Application package
│   ├── core/              # Core functionality
│   ├── api/               # API endpoints
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   └── repositories/      # Data access layer
├── tests/                 # Test files
└── alembic/              # Database migrations
```

## Setup

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   Create a `.env` file in the root directory with necessary environment variables.

4. Run the application:

```bash
uvicorn app.main:app --reload
```

## Development

- The application uses FastAPI for the web framework
- SQLAlchemy for database ORM
- Alembic for database migrations
- Pydantic for data validation
- Pytest for testing

## API Documentation

Once the application is running, you can access:

- Swagger UI documentation at `/docs`
- ReDoc documentation at `/redoc`
