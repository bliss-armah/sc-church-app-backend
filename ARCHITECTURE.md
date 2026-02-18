# Architecture Documentation

## Overview

The Church Management System follows a clean, layered architecture with clear separation of concerns. This design makes the system maintainable, testable, and easily extensible.

## Architecture Layers

### 1. Presentation Layer (API Endpoints)

**Location:** `app/api/v1/endpoints/`

**Responsibility:** Handle HTTP requests and responses

- Receive and validate request data
- Call appropriate service methods
- Return formatted responses
- Handle HTTP-specific concerns (status codes, headers)

**Example:**

```python
@router.post("/", response_model=MemberResponse)
def create_member(member_data: MemberCreate, db: Session = Depends(get_db)):
    return MemberService.create_member(db, member_data)
```

### 2. Business Logic Layer (Services)

**Location:** `app/services/`

**Responsibility:** Implement business rules and logic

- Validate business rules
- Coordinate between multiple models
- Handle complex operations
- Raise business-specific exceptions

**Example:**

```python
class MemberService:
    @staticmethod
    def create_member(db: Session, member_data: MemberCreate) -> Member:
        # Check business rules (e.g., email uniqueness)
        # Create and save member
        # Return result
```

### 3. Data Access Layer (Models)

**Location:** `app/models/`

**Responsibility:** Define database schema and relationships

- Map Python classes to database tables
- Define relationships between entities
- Specify constraints and indexes

**Example:**

```python
class Member(Base):
    __tablename__ = "members"
    id = Column(UUID, primary_key=True)
    first_name = Column(String, nullable=False)
```

### 4. Data Transfer Objects (Schemas)

**Location:** `app/schemas/`

**Responsibility:** Define API contracts and validation

- Validate input data
- Define response formats
- Ensure type safety
- Document API structure

**Example:**

```python
class MemberCreate(BaseModel):
    first_name: str = Field(..., min_length=1)
    email: Optional[EmailStr] = None
```

## Key Design Patterns

### 1. Dependency Injection

Used for database sessions and future authentication:

```python
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 2. Repository Pattern (via Services)

Services act as repositories, abstracting data access:

```python
MemberService.get_member(db, member_id)  # Instead of direct DB queries
```

### 3. Soft Delete Pattern

Data is marked as deleted, not physically removed:

```python
member.is_deleted = True  # Soft delete
# vs
db.delete(member)  # Hard delete (not used)
```

### 4. UUID Primary Keys

Using UUIDs instead of auto-incrementing integers:

- Better for distributed systems
- No information leakage
- Easier merging of data

## Data Flow

### Creating a Member

```
1. Client sends POST request
   ↓
2. FastAPI validates request against MemberCreate schema
   ↓
3. Endpoint receives validated data
   ↓
4. Endpoint calls MemberService.create_member()
   ↓
5. Service checks business rules (email uniqueness)
   ↓
6. Service creates Member model instance
   ↓
7. Service saves to database via SQLAlchemy
   ↓
8. Service returns Member instance
   ↓
9. FastAPI serializes to MemberResponse schema
   ↓
10. Client receives JSON response
```

## Database Design

### Member Table Schema

```sql
CREATE TABLE members (
    id UUID PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    second_name VARCHAR(100),
    other_names VARCHAR(255),
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(10) NOT NULL,
    phone_number VARCHAR(20),
    email VARCHAR(255) UNIQUE,
    address TEXT,
    membership_status VARCHAR(20) NOT NULL DEFAULT 'visitor',
    date_joined DATE NOT NULL,
    notes TEXT,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_members_first_name ON members(first_name);
CREATE INDEX idx_members_last_name ON members(last_name);
CREATE INDEX idx_members_email ON members(email);
CREATE INDEX idx_members_phone ON members(phone_number);
CREATE INDEX idx_members_dob ON members(date_of_birth);
CREATE INDEX idx_members_status ON members(membership_status);
CREATE INDEX idx_members_deleted ON members(is_deleted);
```

### Why These Indexes?

- **Name indexes**: Fast member lookup by name
- **Email/Phone indexes**: Quick contact information searches
- **Date of birth index**: Age-based queries and birthday reminders
- **Status index**: Filter active/inactive members efficiently
- **Deleted index**: Exclude soft-deleted records quickly

## Configuration Management

### Environment-Based Configuration

```python
class Settings(BaseSettings):
    DATABASE_URL: str
    DEBUG: bool = True

    class Config:
        env_file = ".env"
```

**Benefits:**

- Different configs for dev/staging/production
- Secrets not in code
- Easy to change without code modifications

## Error Handling Strategy

### HTTP Status Codes

- `200 OK`: Successful GET, PUT, DELETE
- `201 Created`: Successful POST
- `400 Bad Request`: Business rule violation
- `404 Not Found`: Resource doesn't exist
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Unexpected errors

### Error Response Format

```json
{
  "detail": "Human-readable error message"
}
```

## Security Considerations

### Current Implementation

- Input validation via Pydantic
- SQL injection prevention via SQLAlchemy ORM
- Email uniqueness enforcement
- Soft deletes for data retention

### Future Enhancements

- JWT-based authentication
- Role-based access control (RBAC)
- Rate limiting
- HTTPS enforcement
- Password hashing (bcrypt)
- Audit logging

## Scalability Considerations

### Current Design Supports

- Horizontal scaling (stateless API)
- Database connection pooling
- Pagination for large datasets
- Indexed queries for performance

### Future Optimizations

- Caching layer (Redis)
- Read replicas for database
- Background job processing (Celery)
- CDN for static assets
- Load balancing

## Testing Strategy

### Unit Tests

Test individual components in isolation:

```python
def test_member_service_create():
    # Test MemberService.create_member()
```

### Integration Tests

Test API endpoints with database:

```python
def test_create_member_endpoint():
    response = client.post("/api/v1/members/", json=data)
    assert response.status_code == 201
```

### Test Database

Use separate test database or in-memory SQLite for tests.

## Migration Strategy

### Alembic Workflow

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Review generated migration file
# Edit if necessary

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### Best Practices

- Always review auto-generated migrations
- Test migrations on staging before production
- Keep migrations small and focused
- Never edit applied migrations
- Backup database before migrations

## Extension Points

### Adding New Modules

The architecture makes it easy to add:

1. New models (attendance, donations, etc.)
2. New endpoints (just add router)
3. New business logic (add service methods)
4. New relationships (SQLAlchemy relationships)

### Example: Adding Attendance Module

```
1. Create app/models/attendance.py
2. Create app/schemas/attendance.py
3. Create app/services/attendance.py
4. Create app/api/v1/endpoints/attendance.py
5. Register router in app/api/v1/router.py
6. Create migration: alembic revision --autogenerate
```

## Performance Monitoring

### Key Metrics to Track

- API response times
- Database query performance
- Error rates
- Active connections
- Memory usage

### Tools

- FastAPI built-in metrics
- Database query logging
- APM tools (New Relic, DataDog)
- Prometheus + Grafana

## Deployment Architecture

### Recommended Setup

```
[Load Balancer]
      ↓
[API Servers] (multiple instances)
      ↓
[PostgreSQL] (with read replicas)
      ↓
[Backup Storage]
```

### Environment Variables

- `DATABASE_URL`: Production database connection
- `DEBUG`: Set to False in production
- `CORS_ORIGINS`: Allowed frontend domains
- `SECRET_KEY`: For JWT signing (future)

## Code Organization Principles

### Single Responsibility

Each module has one clear purpose:

- Models: Database schema
- Schemas: Validation
- Services: Business logic
- Endpoints: HTTP handling

### DRY (Don't Repeat Yourself)

- Reusable service methods
- Shared schemas
- Common dependencies

### Open/Closed Principle

- Easy to extend (add new modules)
- No need to modify existing code

### Dependency Inversion

- Depend on abstractions (interfaces)
- Services don't know about HTTP
- Endpoints don't know about database details
