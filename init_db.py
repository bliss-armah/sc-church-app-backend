"""
Database initialization script
Run this to create initial database tables without using Alembic
Useful for quick testing or development setup
"""
from app.database import engine, Base
from app.models import Member

def init_db():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    print("\nTables created:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")

if __name__ == "__main__":
    init_db()
