from sqlalchemy import Column, String, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from datetime import datetime
from app.database import Base


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    CALLING_TEAM = "calling_team"
    TEXTING_TEAM = "texting_team"


class User(Base):
    __tablename__ = "users"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # User information
    full_name = Column(String(255), nullable=False)
    role = Column(
        SQLEnum(UserRole, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=UserRole.CALLING_TEAM,
        index=True
    )
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    must_change_password = Column(Boolean, default=True, nullable=False)
    
    # Soft delete
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<User {self.username} ({self.role})>"

