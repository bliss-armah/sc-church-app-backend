# Church Management System - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites

- Python 3.11 or higher
- PostgreSQL (optional - SQLite works for development)

### Option 1: Quick Start Script (Recommended)

```bash
cd server
chmod +x run.sh
./run.sh
```

The script will:

1. Create a virtual environment
2. Install dependencies
3. Set up configuration
4. Run database migrations
5. Start the server

### Option 2: Manual Setup

```bash
# 1. Navigate to server directory
cd server

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env
# Edit .env if needed

# 5. Run migrations
alembic upgrade head

# 6. Start the server
uvicorn app.main:app --reload
```

### Access the API

- **API Documentation (Swagger):** http://localhost:8000/docs
- **Alternative Docs (ReDoc):** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

## 📝 Try It Out

### 1. Create Your First Member

Open http://localhost:8000/docs and try the `POST /api/v1/members` endpoint:

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-05-15",
  "gender": "male",
  "date_joined": "2024-01-15",
  "email": "john.doe@example.com",
  "phone_number": "+1234567890",
  "membership_status": "active"
}
```

### 2. List All Members

Try `GET /api/v1/members?page=1&page_size=20`

### 3. Search Members

Try `GET /api/v1/members?search=john`

## 📚 Documentation

- **API Examples:** See `server/EXAMPLES.md`
- **Architecture:** See `server/ARCHITECTURE.md`
- **Extension Guide:** See `server/EXTENSION_GUIDE.md`

## 🗄️ Database Configuration

### Using SQLite (Default - Development)

No setup needed! The database file will be created automatically.

### Using PostgreSQL (Recommended for Production)

1. Create a database:

```sql
CREATE DATABASE cms_db;
```

2. Update `.env`:

```
DATABASE_URL=postgresql://username:password@localhost:5432/cms_db
```

3. Run migrations:

```bash
alembic upgrade head
```

## 🧪 Running Tests

```bash
cd server
pytest
```

## 📦 Project Structure

```
server/
├── app/
│   ├── api/v1/endpoints/    # API endpoints
│   ├── models/              # Database models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   ├── config.py            # Configuration
│   ├── database.py          # Database setup
│   └── main.py              # FastAPI app
├── alembic/                 # Database migrations
├── tests/                   # Test files
└── requirements.txt         # Dependencies
```

## 🔧 Common Tasks

### Create a Database Migration

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Rollback Migration

```bash
alembic downgrade -1
```

### View Current Migration

```bash
alembic current
```

### View Migration History

```bash
alembic history
```

## 🎯 Next Steps

1. **Explore the API** using the interactive docs at `/docs`
2. **Read the examples** in `EXAMPLES.md`
3. **Understand the architecture** in `ARCHITECTURE.md`
4. **Plan extensions** using `EXTENSION_GUIDE.md`

## 🆘 Troubleshooting

### Port Already in Use

```bash
# Use a different port
uvicorn app.main:app --reload --port 8001
```

### Database Connection Error

- Check your `DATABASE_URL` in `.env`
- Ensure PostgreSQL is running (if using PostgreSQL)
- For SQLite, ensure write permissions in the directory

### Import Errors

```bash
# Ensure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## 📞 Support

For issues or questions:

1. Check the documentation files
2. Review the API examples
3. Examine the test files for usage patterns

## 🎉 You're Ready!

Your Church Management System backend is now running. Start building your frontend or use the API directly!
