from sqlalchemy import Column, Date, DateTime, ForeignKey, String, Enum as SQLEnum, UniqueConstraint, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum
from datetime import datetime
from app.database import Base


class AttendanceStatusEnum(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    member_id = Column(
        UUID(as_uuid=True),
        ForeignKey("members.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    attendance_date = Column(Date, nullable=False, index=True)

    status = Column(
        SQLEnum(AttendanceStatusEnum),
        nullable=False,
        default=AttendanceStatusEnum.PRESENT
    )

    check_in_time = Column(DateTime, default=datetime.utcnow, nullable=False)

    notes = Column(Text, nullable=True)

    marked_by = Column(UUID(as_uuid=True), nullable=True)  # future admin reference

    is_deleted = Column(Boolean, default=False, nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("member_id", "attendance_date", name="uq_member_attendance_date"),
    )

    member = relationship("Member", backref="attendance_records")
