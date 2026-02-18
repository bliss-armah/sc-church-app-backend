# Extension Guide

This guide explains how to extend the Church Management System with new modules after the MVP.

## Architecture Overview

The system follows a clean, layered architecture:

```
Presentation Layer (API Endpoints)
         ↓
Business Logic Layer (Services)
         ↓
Data Access Layer (Models)
         ↓
Database (PostgreSQL/SQLite)
```

## Adding a New Module

Follow these steps to add a new module (e.g., Attendance, Donations, Groups):

### 1. Create the Database Model

Create a new file in `app/models/` (e.g., `attendance.py`):

```python
from sqlalchemy import Column, String, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.database import Base

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=False)
    service_date = Column(Date, nullable=False, index=True)
    service_type = Column(String(50), nullable=False)  # Sunday, Midweek, etc.
    checked_in_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    member = relationship("Member", backref="attendance_records")
```

Update `app/models/__init__.py`:

```python
from app.models.member import Member
from app.models.attendance import Attendance

__all__ = ["Member", "Attendance"]
```

### 2. Create Pydantic Schemas

Create `app/schemas/attendance.py`:

```python
from pydantic import BaseModel, Field
from datetime import date, datetime
from uuid import UUID

class AttendanceBase(BaseModel):
    member_id: UUID
    service_date: date
    service_type: str = Field(..., max_length=50)

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceResponse(AttendanceBase):
    id: UUID
    checked_in_at: datetime

    class Config:
        from_attributes = True
```

Update `app/schemas/__init__.py` to export the new schemas.

### 3. Create Service Layer

Create `app/services/attendance.py`:

```python
from sqlalchemy.orm import Session
from uuid import UUID
from app.models.attendance import Attendance
from app.schemas.attendance import AttendanceCreate
from fastapi import HTTPException, status

class AttendanceService:
    @staticmethod
    def record_attendance(db: Session, attendance_data: AttendanceCreate) -> Attendance:
        # Verify member exists
        from app.services.member import MemberService
        MemberService.get_member(db, attendance_data.member_id)

        attendance = Attendance(**attendance_data.model_dump())
        db.add(attendance)
        db.commit()
        db.refresh(attendance)
        return attendance

    @staticmethod
    def get_member_attendance(db: Session, member_id: UUID):
        return db.query(Attendance).filter(
            Attendance.member_id == member_id
        ).order_by(Attendance.service_date.desc()).all()
```

### 4. Create API Endpoints

Create `app/api/v1/endpoints/attendance.py`:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from app.api.deps import get_db
from app.schemas.attendance import AttendanceCreate, AttendanceResponse
from app.services.attendance import AttendanceService

router = APIRouter()

@router.post("/", response_model=AttendanceResponse)
def record_attendance(
    attendance_data: AttendanceCreate,
    db: Session = Depends(get_db)
):
    return AttendanceService.record_attendance(db, attendance_data)

@router.get("/member/{member_id}", response_model=list[AttendanceResponse])
def get_member_attendance(
    member_id: UUID,
    db: Session = Depends(get_db)
):
    return AttendanceService.get_member_attendance(db, member_id)
```

### 5. Register the Router

Update `app/api/v1/router.py`:

```python
from app.api.v1.endpoints import members, attendance

api_router = APIRouter()

api_router.include_router(members.router, prefix="/members", tags=["members"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["attendance"])
```

### 6. Create Database Migration

```bash
cd server
alembic revision --autogenerate -m "add attendance table"
alembic upgrade head
```

## Common Module Examples

### Donations Module

**Key Features:**

- Track financial contributions
- Link to members
- Support different donation types (tithe, offering, special)
- Generate reports

**Model Fields:**

- `id`, `member_id`, `amount`, `donation_type`, `donation_date`, `payment_method`, `notes`

### Groups/Ministries Module

**Key Features:**

- Create groups (small groups, committees, ministries)
- Manage group membership
- Track group leaders
- Schedule group meetings

**Models:**

- `Group`: id, name, description, leader_id, created_at
- `GroupMembership`: id, group_id, member_id, role, joined_at

### Events Module

**Key Features:**

- Create church events
- Track event attendance
- Manage event volunteers

**Models:**

- `Event`: id, name, description, event_date, location
- `EventParticipant`: id, event_id, member_id, role

## Adding Authentication

When ready to add authentication:

1. **Install dependencies:**

```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

2. **Create User model** with password hashing
3. **Create authentication service** with JWT token generation
4. **Add login endpoint**
5. **Create dependency** for protected routes:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Verify token and return user
    pass
```

6. **Protect endpoints:**

```python
@router.get("/protected")
def protected_route(current_user = Depends(get_current_user)):
    return {"user": current_user}
```

## Best Practices

1. **Always use services** for business logic, not in endpoints
2. **Validate input** with Pydantic schemas
3. **Use proper HTTP status codes**
4. **Add indexes** to frequently queried fields
5. **Use relationships** for related data
6. **Create migrations** for all schema changes
7. **Write tests** for new functionality
8. **Document endpoints** with docstrings
9. **Handle errors gracefully** with proper error messages
10. **Use soft deletes** for important data

## Database Relationships

### One-to-Many Example

```python
# In Member model
attendance_records = relationship("Attendance", back_populates="member")

# In Attendance model
member = relationship("Member", back_populates="attendance_records")
```

### Many-to-Many Example

```python
# Association table
group_members = Table('group_members', Base.metadata,
    Column('group_id', UUID, ForeignKey('groups.id')),
    Column('member_id', UUID, ForeignKey('members.id'))
)

# In Group model
members = relationship("Member", secondary=group_members, back_populates="groups")

# In Member model
groups = relationship("Group", secondary=group_members, back_populates="members")
```

## Testing New Modules

Create test files in `server/tests/`:

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_attendance():
    response = client.post("/api/v1/attendance/", json={
        "member_id": "...",
        "service_date": "2024-01-21",
        "service_type": "Sunday Service"
    })
    assert response.status_code == 201
```

## Performance Optimization

1. **Add database indexes** for frequently queried fields
2. **Use eager loading** for relationships: `.options(joinedload(Member.attendance_records))`
3. **Implement caching** for frequently accessed data
4. **Use pagination** for large datasets
5. **Add database connection pooling** for production

## Deployment Considerations

1. Use environment variables for all configuration
2. Set up proper logging
3. Use PostgreSQL in production (not SQLite)
4. Enable HTTPS
5. Set up database backups
6. Monitor API performance
7. Implement rate limiting
8. Add health check endpoints
