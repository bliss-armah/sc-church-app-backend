# Development Tips & Tricks

Quick reference for common development tasks and useful commands.

## 🚀 Starting Development

### First Time Setup

```bash
cd server
./run.sh
```

### Daily Development

```bash
cd server
source venv/bin/activate
uvicorn app.main:app --reload
```

### Different Port

```bash
uvicorn app.main:app --reload --port 8001
```

### With Custom Host

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🗄️ Database Commands

### Create Migration

```bash
alembic revision --autogenerate -m "add new field to member"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback Last Migration

```bash
alembic downgrade -1
```

### View Current Version

```bash
alembic current
```

### View Migration History

```bash
alembic history --verbose
```

### Rollback to Specific Version

```bash
alembic downgrade <revision_id>
```

### Quick DB Init (Without Alembic)

```bash
python init_db.py
```

## 🧪 Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_members.py
```

### Run Specific Test

```bash
pytest tests/test_members.py::test_create_member
```

### Run with Coverage

```bash
pytest --cov=app tests/
```

### Run with Verbose Output

```bash
pytest -v
```

## 🔍 Debugging

### Check Python Syntax

```bash
python -m py_compile app/main.py
```

### Interactive Python Shell with App Context

```bash
python
>>> from app.database import SessionLocal
>>> from app.models import Member
>>> db = SessionLocal()
>>> members = db.query(Member).all()
>>> print(members)
```

### View Database (SQLite)

```bash
sqlite3 cms.db
.tables
.schema members
SELECT * FROM members;
.quit
```

### View Database (PostgreSQL)

```bash
psql -d cms_db
\dt
\d members
SELECT * FROM members;
\q
```

## 📝 Code Quality

### Format Code (if black installed)

```bash
black app/
```

### Lint Code (if flake8 installed)

```bash
flake8 app/
```

### Type Check (if mypy installed)

```bash
mypy app/
```

## 🔧 Useful Python Commands

### Install New Package

```bash
pip install package-name
pip freeze > requirements.txt
```

### Update All Packages

```bash
pip list --outdated
pip install --upgrade package-name
```

### Create Requirements from Current Environment

```bash
pip freeze > requirements.txt
```

## 🌐 API Testing

### Using curl

**Create Member:**

```bash
curl -X POST http://localhost:8000/api/v1/members \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-01-01",
    "gender": "male",
    "date_joined": "2024-01-15",
    "email": "john@example.com"
  }'
```

**List Members:**

```bash
curl http://localhost:8000/api/v1/members
```

**Get Member:**

```bash
curl http://localhost:8000/api/v1/members/{member_id}
```

**Update Member:**

```bash
curl -X PUT http://localhost:8000/api/v1/members/{member_id} \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890"}'
```

**Delete Member:**

```bash
curl -X DELETE http://localhost:8000/api/v1/members/{member_id}
```

### Using HTTPie (if installed)

```bash
# Install: pip install httpie

# Create member
http POST localhost:8000/api/v1/members \
  first_name=John \
  last_name=Doe \
  date_of_birth=1990-01-01 \
  gender=male \
  date_joined=2024-01-15

# List members
http GET localhost:8000/api/v1/members

# Get member
http GET localhost:8000/api/v1/members/{member_id}
```

## 🐛 Common Issues & Solutions

### Issue: Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --reload --port 8001
```

### Issue: Database Locked (SQLite)

```bash
# Close all connections and restart server
# Or switch to PostgreSQL for development
```

### Issue: Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Migration Conflicts

```bash
# View current state
alembic current

# View history
alembic history

# Downgrade and reapply
alembic downgrade -1
alembic upgrade head
```

### Issue: Pydantic Validation Errors

- Check the API docs at `/docs` for required fields
- Ensure date formats are YYYY-MM-DD
- Check enum values (gender, membership_status)

## 📊 Monitoring

### View Logs

```bash
# Server logs are in terminal where uvicorn is running
# Add logging to app:

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Message here")
```

### Database Query Logging

```python
# In app/database.py, add echo=True
engine = create_engine(
    settings.DATABASE_URL,
    echo=True  # Logs all SQL queries
)
```

## 🎯 Quick Snippets

### Add New Endpoint

```python
# In app/api/v1/endpoints/members.py
@router.get("/stats")
def get_member_stats(db: Session = Depends(get_db)):
    total = db.query(Member).count()
    active = db.query(Member).filter(
        Member.membership_status == "active"
    ).count()
    return {"total": total, "active": active}
```

### Add New Service Method

```python
# In app/services/member.py
@staticmethod
def get_active_members(db: Session) -> List[Member]:
    return db.query(Member).filter(
        Member.membership_status == "active",
        Member.is_deleted == False
    ).all()
```

### Add Database Index

```python
# In model, add index=True to column
email = Column(String(255), unique=True, index=True)

# Then create migration
alembic revision --autogenerate -m "add email index"
alembic upgrade head
```

## 🔐 Environment Variables

### Development

```bash
export DEBUG=True
export DATABASE_URL=sqlite:///./cms.db
```

### Production

```bash
export DEBUG=False
export DATABASE_URL=postgresql://user:pass@host:5432/db
export CORS_ORIGINS='["https://yourdomain.com"]'
```

## 📦 Deployment Prep

### Generate Requirements

```bash
pip freeze > requirements.txt
```

### Test Production Settings

```bash
export DEBUG=False
uvicorn app.main:app
```

### Database Backup (PostgreSQL)

```bash
pg_dump cms_db > backup.sql
```

### Database Restore (PostgreSQL)

```bash
psql cms_db < backup.sql
```

## 🎓 Learning Resources

### FastAPI Docs

- https://fastapi.tiangolo.com/

### SQLAlchemy Docs

- https://docs.sqlalchemy.org/

### Pydantic Docs

- https://docs.pydantic.dev/

### Alembic Docs

- https://alembic.sqlalchemy.org/

## 💡 Pro Tips

1. **Use the interactive docs** at `/docs` - it's the fastest way to test
2. **Check logs** when things go wrong - errors are usually clear
3. **Use migrations** for all schema changes - never edit the database directly
4. **Write tests** as you add features - future you will thank you
5. **Keep services thin** - complex logic should be well-organized
6. **Use type hints** - they catch bugs before runtime
7. **Validate early** - use Pydantic schemas for all input
8. **Index wisely** - add indexes to frequently queried fields
9. **Soft delete** - never hard delete important data
10. **Document as you go** - add docstrings to new functions

## 🚀 Performance Tips

1. **Use pagination** for large datasets
2. **Add database indexes** to frequently queried fields
3. **Use eager loading** for relationships: `.options(joinedload(...))`
4. **Cache frequently accessed data** (add Redis later)
5. **Use connection pooling** in production
6. **Monitor slow queries** with database logging
7. **Optimize N+1 queries** with proper joins

## 🎉 Happy Coding!

Remember: The interactive docs at http://localhost:8000/docs are your best friend!
