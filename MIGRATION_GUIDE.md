# Database Migration Guide

Complete guide for safely running database migrations without losing data.

## 🎯 Overview

This guide covers how to:

- Create new migrations when adding features
- Apply migrations safely without data loss
- Handle migration conflicts
- Backup and restore data
- Rollback migrations if needed

## 📋 Prerequisites

- Docker Compose setup running
- Database with existing data
- Access to the server directory

## 🚀 Standard Migration Workflow

### 1. Before Making Changes

Always backup your data first:

```bash
# Backup database
docker compose exec db pg_dump -U cms_user cms_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Or compressed backup
docker compose exec db pg_dump -U cms_user cms_db | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

### 2. Make Code Changes

Add your new models, modify existing ones, etc.

Example: Adding a new field to Member model:

```python
# In app/models/member.py
class Member(Base):
    # ... existing fields ...
    emergency_contact = Column(String(255), nullable=True)  # New field
```

### 3. Create Migration

```bash
# Generate migration automatically
docker compose exec api alembic revision --autogenerate -m "add emergency contact to members"
```

**Important:** Always review the generated migration file before applying!

### 4. Review Migration File

```bash
# List migration files
ls alembic/versions/

# View the latest migration
cat alembic/versions/$(ls alembic/versions/*.py | tail -1)
```

Check that the migration:

- ✅ Only adds/modifies what you intended
- ✅ Doesn't drop important columns
- ✅ Has proper default values for NOT NULL columns
- ✅ Handles data type changes correctly

### 5. Apply Migration

```bash
# Apply migration
docker compose exec api alembic upgrade head

# Check migration status
docker compose exec api alembic current
```

### 6. Verify Changes

```bash
# Check database schema
docker compose exec db psql -U cms_user -d cms_db -c "\d members"

# Test API endpoints
curl http://localhost:8000/api/v1/members
```

## 🔄 Common Migration Scenarios

### Adding a New Table

```python
# 1. Create new model in app/models/
class Event(Base):
    __tablename__ = "events"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    # ... other fields

# 2. Update app/models/__init__.py
from app.models.event import Event
__all__ = ["Member", "User", "Event"]

# 3. Create migration
docker compose exec api alembic revision --autogenerate -m "add events table"

# 4. Apply migration
docker compose exec api alembic upgrade head
```

### Adding a Column

```python
# 1. Add column to model
class Member(Base):
    # ... existing fields ...
    phone_secondary = Column(String(20), nullable=True)  # New optional field

# 2. Create migration
docker compose exec api alembic revision --autogenerate -m "add secondary phone to members"

# 3. Apply migration
docker compose exec api alembic upgrade head
```

### Adding a Required Column with Default

```python
# 1. Add column to model
class Member(Base):
    # ... existing fields ...
    status = Column(String(20), nullable=False, default="active")

# 2. Create migration
docker compose exec api alembic revision --autogenerate -m "add status to members"

# 3. Review migration - should include default value
# 4. Apply migration
docker compose exec api alembic upgrade head
```

### Modifying Column Type

```python
# 1. Change model
class Member(Base):
    # Change from String(20) to String(50)
    phone_number = Column(String(50), nullable=True)

# 2. Create migration
docker compose exec api alembic revision --autogenerate -m "increase phone number length"

# 3. Apply migration
docker compose exec api alembic upgrade head
```

### Adding Relationships

```python
# 1. Add relationship to models
class Member(Base):
    # ... existing fields ...
    events = relationship("EventParticipant", back_populates="member")

class Event(Base):
    # ... existing fields ...
    participants = relationship("EventParticipant", back_populates="event")

class EventParticipant(Base):
    __tablename__ = "event_participants"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"))
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"))

    member = relationship("Member", back_populates="events")
    event = relationship("Event", back_populates="participants")

# 2. Create migration
docker compose exec api alembic revision --autogenerate -m "add event participants relationship"

# 3. Apply migration
docker compose exec api alembic upgrade head
```

## 🛡️ Safety Best Practices

### 1. Always Backup First

```bash
# Create backup before any migration
docker compose exec db pg_dump -U cms_user cms_db > backup_before_migration.sql
```

### 2. Test on Copy First (Production)

```bash
# For production, test on a copy first
# 1. Create database copy
# 2. Test migration on copy
# 3. If successful, apply to production
```

### 3. Review Generated Migrations

Never blindly apply auto-generated migrations:

```bash
# View migration before applying
cat alembic/versions/latest_migration.py

# Look for:
# - Unexpected DROP statements
# - Missing default values for NOT NULL columns
# - Data type changes that might lose data
```

### 4. Use Transactions

Alembic uses transactions by default, but verify:

```python
# In alembic/env.py, ensure:
with connectable.connect() as connection:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        transaction_per_migration=True  # This ensures each migration is in a transaction
    )
```

## 🚨 Handling Migration Errors

### Migration Fails Midway

```bash
# Check current migration status
docker compose exec api alembic current

# Check migration history
docker compose exec api alembic history

# If migration failed, it should auto-rollback
# But verify database state
docker compose exec db psql -U cms_user -d cms_db -c "\d"
```

### Rollback Migration

```bash
# Rollback to previous migration
docker compose exec api alembic downgrade -1

# Rollback to specific revision
docker compose exec api alembic downgrade <revision_id>

# Check status
docker compose exec api alembic current
```

### Fix and Retry

```bash
# 1. Fix the issue in code or migration file
# 2. If you edited migration file, apply it
docker compose exec api alembic upgrade head

# 3. If you changed model, create new migration
docker compose exec api alembic revision --autogenerate -m "fix previous migration"
docker compose exec api alembic upgrade head
```

## 🔄 Data Migration Examples

### Populate New Column with Data

Sometimes you need to populate a new column with calculated values:

```python
# In migration file (manual edit after auto-generation)
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add column
    op.add_column('members', sa.Column('full_name', sa.String(255), nullable=True))

    # Populate with existing data
    connection = op.get_bind()
    connection.execute(
        "UPDATE members SET full_name = CONCAT(first_name, ' ', last_name) WHERE full_name IS NULL"
    )

    # Make it NOT NULL after populating
    op.alter_column('members', 'full_name', nullable=False)

def downgrade():
    op.drop_column('members', 'full_name')
```

### Split Column Data

```python
# Example: Split full_name into first_name and last_name
def upgrade():
    # Add new columns
    op.add_column('members', sa.Column('first_name', sa.String(100), nullable=True))
    op.add_column('members', sa.Column('last_name', sa.String(100), nullable=True))

    # Migrate data
    connection = op.get_bind()
    connection.execute("""
        UPDATE members
        SET first_name = SPLIT_PART(full_name, ' ', 1),
            last_name = SPLIT_PART(full_name, ' ', 2)
        WHERE full_name IS NOT NULL
    """)

    # Make required and drop old column
    op.alter_column('members', 'first_name', nullable=False)
    op.alter_column('members', 'last_name', nullable=False)
    op.drop_column('members', 'full_name')
```

## 📊 Migration Status Commands

```bash
# Show current migration
docker compose exec api alembic current

# Show migration history
docker compose exec api alembic history

# Show pending migrations
docker compose exec api alembic heads

# Show migration details
docker compose exec api alembic show <revision_id>

# Check if database is up to date
docker compose exec api alembic check
```

## 🔧 Troubleshooting

### "Target database is not up to date"

```bash
# Check current status
docker compose exec api alembic current

# Apply pending migrations
docker compose exec api alembic upgrade head
```

### "Multiple heads detected"

```bash
# View heads
docker compose exec api alembic heads

# Merge heads
docker compose exec api alembic merge -m "merge heads" <head1> <head2>
docker compose exec api alembic upgrade head
```

### "Can't locate revision"

```bash
# Check available revisions
docker compose exec api alembic history

# Reset to specific revision
docker compose exec api alembic stamp <revision_id>
```

## 💾 Backup and Restore

### Create Backup

```bash
# Full backup
docker compose exec db pg_dump -U cms_user cms_db > backup.sql

# Compressed backup
docker compose exec db pg_dump -U cms_user cms_db | gzip > backup.sql.gz

# Schema only
docker compose exec db pg_dump -U cms_user -s cms_db > schema_backup.sql

# Data only
docker compose exec db pg_dump -U cms_user -a cms_db > data_backup.sql
```

### Restore Backup

```bash
# Stop API to prevent connections
docker compose stop api

# Restore full backup
docker compose exec -T db psql -U cms_user -d cms_db < backup.sql

# Restore compressed backup
gunzip -c backup.sql.gz | docker compose exec -T db psql -U cms_user -d cms_db

# Start API
docker compose start api
```

## 📝 Migration Checklist

Before applying any migration:

- [ ] ✅ Database backup created
- [ ] ✅ Migration file reviewed
- [ ] ✅ No unexpected DROP statements
- [ ] ✅ Default values for NOT NULL columns
- [ ] ✅ Data type changes are safe
- [ ] ✅ Foreign key constraints are correct
- [ ] ✅ Indexes are appropriate
- [ ] ✅ Test environment validated (if production)

After applying migration:

- [ ] ✅ Migration status verified
- [ ] ✅ Database schema checked
- [ ] ✅ API endpoints tested
- [ ] ✅ Data integrity verified
- [ ] ✅ Application functionality confirmed

## 🎯 Best Practices Summary

1. **Always backup** before migrations
2. **Review auto-generated** migrations
3. **Test on copy** for production
4. **Use descriptive** migration messages
5. **Keep migrations small** and focused
6. **Don't edit applied** migrations
7. **Handle data migration** explicitly
8. **Verify after applying** migrations
9. **Have rollback plan** ready
10. **Document complex** migrations

## 🔮 Advanced Topics

### Custom Migration Scripts

```bash
# Create empty migration for custom logic
docker compose exec api alembic revision -m "custom data migration"

# Edit the generated file to add custom logic
```

### Branching and Merging

```bash
# Create branch
docker compose exec api alembic revision -m "feature branch"

# Merge branches
docker compose exec api alembic merge -m "merge feature" <head1> <head2>
```

### Production Deployment

```bash
# In production, run migrations during deployment
docker compose -f docker-compose.prod.yml exec api alembic upgrade head
```

This guide ensures you can safely evolve your database schema without losing precious data! 🛡️
