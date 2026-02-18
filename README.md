# Church Management System (CMS) - Backend API

A FastAPI-based backend for managing church operations, starting with member management.

## Features (MVP)

- **Member Management**: Complete CRUD operations for church members
- **Clean Architecture**: Separation of concerns with routers, services, schemas, and models
- **Database**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- **Validation**: Pydantic schemas with comprehensive validation
- **Extensible**: Ready for future modules (attendance, donations, groups, etc.)

## Project Structure

```
cms-backend/
├── server/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── config.py               # Configuration management
│   │   ├── database.py             # Database connection and session
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py             # Dependency injection
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── router.py       # API router aggregation
│   │   │       └── endpoints/
│   │   │           ├── __init__.py
│   │   │           └── members.py  # Member endpoints
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── member.py           # SQLAlchemy models
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── member.py           # Pydantic schemas
│   │   └── services/
│   │       ├── __init__.py
│   │       └── member.py           # Business logic
│   ├── alembic/                    # Database migrations
│   ├── tests/                      # Test suite
│   ├── .env.example
│   ├── .gitignore
│   └── requirements.txt
└── README.md
```

## Quick Start

### Option 1: Docker (Recommended) 🐳

**Easiest way - no Python installation needed!**

```bash
docker compose up
```

Then visit http://localhost:8000/docs

See [DOCKER.md](DOCKER.md) for complete Docker guide.

### Option 2: Local Python Setup

```bash
./run.sh
```

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

## Full Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 14+ (or SQLite for local development)

### Installation

Follow the detailed steps in [QUICKSTART.md](QUICKSTART.md) or use the quick start script above.

## API Endpoints

### Members

- `POST /api/v1/members` - Create a new member
- `GET /api/v1/members` - List all members (paginated)
- `GET /api/v1/members/{member_id}` - Get member by ID
- `PUT /api/v1/members/{member_id}` - Update member
- `DELETE /api/v1/members/{member_id}` - Soft delete member

## Future Extensions

The architecture is designed to easily add:

- **Authentication & Authorization**: JWT-based auth with role-based access control
- **Attendance Tracking**: Track service attendance with member relationships
- **Donations Management**: Financial contributions and reporting
- **Groups & Ministries**: Small groups, committees, and ministry teams
- **Events Management**: Church events and member participation
- **Communications**: Email/SMS notifications and announcements

### Adding New Modules

1. Create model in `app/models/`
2. Create schemas in `app/schemas/`
3. Create service in `app/services/`
4. Create endpoints in `app/api/v1/endpoints/`
5. Register router in `app/api/v1/router.py`
6. Create migration: `alembic revision --autogenerate -m "description"`

## Development

### Running Tests

```bash
pytest
```

### Creating Migrations

```bash
alembic revision --autogenerate -m "description of changes"
alembic upgrade head
```

## License

MIT
