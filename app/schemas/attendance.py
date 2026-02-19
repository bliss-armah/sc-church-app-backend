from pydantic import Field
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID
import enum

from app.schemas.base import CamelModel


class AttendanceStatusEnum(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


class AttendanceCreate(CamelModel):
    """Schema for marking a single member's attendance"""
    member_id: UUID = Field(..., description="UUID of the member")
    status: AttendanceStatusEnum = Field(
        default=AttendanceStatusEnum.PRESENT,
        description="Attendance status: present, absent, late, or excused"
    )
    attendance_date: Optional[date] = Field(
        default=None,
        description="Date of attendance. Defaults to today if not provided."
    )
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes")


class AttendanceBulkCreate(CamelModel):
    """Schema for marking attendance for multiple members at once"""
    member_ids: List[UUID] = Field(..., min_length=1, description="List of member UUIDs")
    status: AttendanceStatusEnum = Field(
        default=AttendanceStatusEnum.PRESENT,
        description="Attendance status applied to all members in the list"
    )
    attendance_date: Optional[date] = Field(
        default=None,
        description="Date of attendance. Defaults to today if not provided."
    )
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes")


class AttendanceUpdate(CamelModel):
    """Schema for updating an attendance record — all fields optional"""
    status: Optional[AttendanceStatusEnum] = None
    notes: Optional[str] = Field(None, max_length=500)


class AttendanceResponse(CamelModel):
    """Schema for attendance response, includes denormalized member name"""
    id: UUID
    member_id: UUID
    member_name: Optional[str] = Field(None, description="Full name of the member")
    attendance_date: date
    status: AttendanceStatusEnum
    check_in_time: datetime
    notes: Optional[str]
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class AttendanceListResponse(CamelModel):
    """Schema for paginated attendance list response"""
    items: List[AttendanceResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ---------------------------------------------------------------------------
# QR Code self-service flow schemas
# ---------------------------------------------------------------------------

class QRLookupRequest(CamelModel):
    """Step 1 — member enters phone number at the QR landing page"""
    phone_number: str = Field(..., description="Member's registered phone number")


class QRLookupResponse(CamelModel):
    """Step 1 response — returned to the frontend for member to confirm identity"""
    member_id: UUID
    member_name: str = Field(..., description="Full name for the member to confirm")
    membership_status: str
    already_marked_today: bool = Field(
        ..., description="True if attendance already recorded for today"
    )


class QRConfirmRequest(CamelModel):
    """Step 2 — member confirms their identity and self-marks attendance"""
    member_id: UUID = Field(..., description="UUID returned from Step 1 lookup")
    attendance_date: Optional[date] = Field(
        default=None,
        description="Defaults to today"
    )


class BulkAttendanceResult(CamelModel):
    """Schema for bulk attendance creation result"""
    created: List[AttendanceResponse]
    skipped: List[UUID] = Field(
        default_factory=list,
        description="Member IDs skipped because a record already exists for that date"
    )
    total_created: int
    total_skipped: int
