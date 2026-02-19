from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from datetime import date
import math

from app.api.deps import get_db, require_user_or_admin
from app.models.user import User
from app.models.attendance import AttendanceStatusEnum
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceBulkCreate,
    AttendanceUpdate,
    AttendanceResponse,
    AttendanceListResponse,
    BulkAttendanceResult,
    QRLookupRequest,
    QRLookupResponse,
    QRConfirmRequest,
)
from app.services.attendance import AttendanceService
from app.config import settings

router = APIRouter()


# ---------------------------------------------------------------------------
# QR Code self-service (PUBLIC — no authentication required)
# ---------------------------------------------------------------------------

@router.post(
    "/qr/lookup",
    response_model=QRLookupResponse,
    summary="[QR — Step 1] Look up member by phone number",
)
def qr_lookup(data: QRLookupRequest, db: Session = Depends(get_db)):
    """
    **Step 1 of QR self-check-in.**

    The member scans the church QR code, lands on the frontend page,
    and types their phone number. This endpoint looks them up and returns
    their name and ID for confirmation — nothing is written to the database.

    - **phone_number**: The member's registered phone number
    - Returns `member_id`, `member_name`, `membership_status`, `already_marked_today`

    > **Public endpoint** — no authentication token required.
    """
    return AttendanceService.lookup_by_phone(db, data)


@router.post(
    "/qr/confirm",
    response_model=AttendanceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="[QR — Step 2] Confirm identity and mark self as present",
)
def qr_confirm(data: QRConfirmRequest, db: Session = Depends(get_db)):
    """
    **Step 2 of QR self-check-in.**

    After the member confirms their name on the frontend, they submit their
    `member_id` (returned from Step 1). This writes a **PRESENT** attendance
    record for today (or the provided `attendance_date`).

    - **member_id**: UUID from Step 1 response
    - **attendance_date**: Optional — defaults to today
    - Status is always **present** (self-service cannot mark absent/late/excused)
    - Returns **409** if already marked for that date

    > **Public endpoint** — no authentication token required.
    """
    return AttendanceService.confirm_and_mark(db, data)


# ---------------------------------------------------------------------------
# Mark single
# ---------------------------------------------------------------------------

@router.post(
    "/",
    response_model=AttendanceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Mark attendance for a single member",
)
def mark_attendance(
    data: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user_or_admin),
):
    """
    Record attendance for one member.

    - **member_id**: UUID of an existing member (required)
    - **status**: `present` | `absent` | `late` | `excused`  (default: `present`)
    - **attendance_date**: Defaults to today if omitted
    - **notes**: Optional free-text notes

    Returns **409** if the member already has an attendance record for that date.
    """
    return AttendanceService.mark_attendance(db, data)


# ---------------------------------------------------------------------------
# Bulk mark
# ---------------------------------------------------------------------------

@router.post(
    "/bulk",
    response_model=BulkAttendanceResult,
    status_code=status.HTTP_201_CREATED,
    summary="Bulk-mark attendance for multiple members",
)
def bulk_mark_attendance(
    data: AttendanceBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user_or_admin),
):
    """
    Mark the same attendance status for a list of members (e.g., a Sunday service).

    - **member_ids**: List of member UUIDs (required)
    - **status**: Applied to every member in the list (default: `present`)
    - **attendance_date**: Defaults to today if omitted
    - **notes**: Optional notes applied to all records

    Members who already have a record for that date are returned in `skipped`
    instead of raising an error — allowing partial success.
    """
    return AttendanceService.bulk_mark_attendance(db, data)


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------

@router.get(
    "/",
    response_model=AttendanceListResponse,
    summary="List attendance records",
)
def list_attendance(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(
        settings.DEFAULT_PAGE_SIZE,
        ge=1,
        le=settings.MAX_PAGE_SIZE,
        description="Items per page",
    ),
    member_id: Optional[UUID] = Query(None, description="Filter by member UUID"),
    attendance_date: Optional[date] = Query(None, description="Filter by exact date (YYYY-MM-DD)"),
    status_filter: Optional[AttendanceStatusEnum] = Query(
        None, alias="status", description="Filter by attendance status"
    ),
    from_date: Optional[date] = Query(None, description="Start of date range (inclusive)"),
    to_date: Optional[date] = Query(None, description="End of date range (inclusive)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user_or_admin),
):
    """
    Paginated list of attendance records.

    **Filters (all optional, combinable):**
    - `member_id` — Show only records for one member
    - `attendance_date` — Exact date
    - `status` — `present`, `absent`, `late`, or `excused`
    - `from_date` / `to_date` — Date range
    """
    skip = (page - 1) * page_size
    records, total = AttendanceService.get_attendance_records(
        db,
        skip=skip,
        limit=page_size,
        member_id=member_id,
        attendance_date=attendance_date,
        status_filter=status_filter,
        from_date=from_date,
        to_date=to_date,
    )
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    return AttendanceListResponse(
        items=records,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


# ---------------------------------------------------------------------------
# Get single
# ---------------------------------------------------------------------------

@router.get(
    "/{attendance_id}",
    response_model=AttendanceResponse,
    summary="Get a single attendance record",
)
def get_attendance(
    attendance_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user_or_admin),
):
    """Fetch a specific attendance record by its UUID."""
    return AttendanceService.get_attendance(db, attendance_id)


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

@router.put(
    "/{attendance_id}",
    response_model=AttendanceResponse,
    summary="Update an attendance record",
)
def update_attendance(
    attendance_id: UUID,
    data: AttendanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user_or_admin),
):
    """
    Patch an existing attendance record. Only provided fields are updated.

    - **status**: Change to `present`, `absent`, `late`, or `excused`
    - **notes**: Update or clear the notes
    """
    return AttendanceService.update_attendance(db, attendance_id, data)


# ---------------------------------------------------------------------------
# Soft delete
# ---------------------------------------------------------------------------

@router.delete(
    "/{attendance_id}",
    response_model=AttendanceResponse,
    summary="Soft-delete an attendance record",
)
def delete_attendance(
    attendance_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user_or_admin),
):
    """
    Soft-delete an attendance record. The record is marked as deleted
    but not removed from the database.
    """
    return AttendanceService.delete_attendance(db, attendance_id)
