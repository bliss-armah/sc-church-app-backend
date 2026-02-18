from sqlalchemy import Column, String, Date, DateTime, Boolean, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from datetime import datetime
from app.database import Base


class GenderEnum(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class MembershipStatusEnum(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    VISITOR = "visitor"


class Member(Base):
    __tablename__ = "members"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Name fields (high importance - indexed)
    first_name = Column(String(100), nullable=False, index=True)
    second_name = Column(String(100), nullable=True)  # Middle name
    other_names = Column(String(255), nullable=True)  # Additional names
    last_name = Column(String(100), nullable=False, index=True)
    
    # Personal information
    date_of_birth = Column(Date, nullable=False, index=True)
    gender = Column(SQLEnum(GenderEnum), nullable=False)
    
    # Contact information
    phone_number = Column(String(20), nullable=True, index=True)
    email = Column(String(255), nullable=True, unique=True, index=True)
    address = Column(Text, nullable=True)
    
    # Membership information
    membership_status = Column(
        SQLEnum(MembershipStatusEnum),
        nullable=False,
        default=MembershipStatusEnum.VISITOR,
        index=True
    )
    date_joined = Column(Date, nullable=False, index=True)
    
    # Additional information
    notes = Column(Text, nullable=True)
    
    # Soft delete
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Member {self.first_name} {self.last_name}>"
