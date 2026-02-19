from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime

from fastapi import HTTPException, status

from app.models.attendance import Attendance, AttendanceStatusEnum
from app.models.member import Member, MembershipStatusEnum
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceBulkCreate,
    AttendanceUpdate,
    QRLookupRequest,
    QRLookupResponse,
    QRConfirmRequest,
)


def _build_response_dict(record: Attendance) -> dict:
    """Build a response dict with denormalized member_name."""
    member_name = None
    if record.member:
        parts = [record.member.first_name]
        if record.member.second_name:
            parts.append(record.member.second_name)
        parts.append(record.member.last_name)
        member_name = " ".join(parts)

    return {
        "id": record.id,
        "member_id": record.member_id,
        "member_name": member_name,
        "attendance_date": record.attendance_date,
        "status": record.status,
        "check_in_time": record.check_in_time,
        "notes": record.notes,
        "is_deleted": record.is_deleted,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
    }


class AttendanceService:
    """Service layer for attendance business logic."""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_member_or_404(db: Session, member_id: UUID) -> Member:
        member = db.query(Member).filter(
            Member.id == member_id,
            Member.is_deleted == False
        ).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Member {member_id} not found"
            )
        return member

    @staticmethod
    def _get_member_by_phone(db: Session, phone_number: str) -> Member:
        """Look up any active, non-deleted member by phone number."""
        member = db.query(Member).filter(
            Member.phone_number == phone_number,
            Member.is_deleted == False,
        ).first()

        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No member found with that phone number. Please contact the church office."
            )

        return member
    

    @staticmethod
    def _get_record_or_404(db: Session, attendance_id: UUID) -> Attendance:
        record = (
            db.query(Attendance)
            .options(joinedload(Attendance.member))
            .filter(Attendance.id == attendance_id, Attendance.is_deleted == False)
            .first()
        )
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance record not found"
            )
        return record

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    @staticmethod
    def mark_attendance(db: Session, data: AttendanceCreate) -> dict:
        """Mark attendance for a single member. Raises 409 on duplicate."""
        AttendanceService._get_member_or_404(db, data.member_id)

        target_date = data.attendance_date or date.today()

        # Duplicate guard (handles race conditions via DB unique constraint too)
        existing = db.query(Attendance).filter(
            Attendance.member_id == data.member_id,
            Attendance.attendance_date == target_date,
            Attendance.is_deleted == False
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Attendance already recorded for this member "
                    f"on {target_date.isoformat()}."
                )
            )

        record = Attendance(
            member_id=data.member_id,
            attendance_date=target_date,
            status=data.status,
            check_in_time=datetime.utcnow(),
            notes=data.notes,
        )
        db.add(record)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Duplicate attendance record for this member and date."
            )

        db.refresh(record)
        # Eager-load member after commit
        record = AttendanceService._get_record_or_404(db, record.id)
        return _build_response_dict(record)

    # ------------------------------------------------------------------
    # QR Code self-service — two-step flow
    # ------------------------------------------------------------------

    @staticmethod
    def lookup_by_phone(db: Session, data: QRLookupRequest) -> QRLookupResponse:
        """
        Step 1 — Member enters their phone number at the QR landing page.
        Returns their name and ID so the frontend can ask them to confirm identity.
        Does NOT write anything to the database.
        """
        member = AttendanceService._get_member_by_phone(db, data.phone_number)

        # Build full name
        parts = [member.first_name]
        if member.second_name:
            parts.append(member.second_name)
        parts.append(member.last_name)
        member_name = " ".join(parts)

        # Check whether already marked today so the frontend can show a helpful message
        already_marked = db.query(Attendance).filter(
            Attendance.member_id == member.id,
            Attendance.attendance_date == date.today(),
            Attendance.is_deleted == False,
        ).first() is not None

        return QRLookupResponse(
            member_id=member.id,
            member_name=member_name,
            membership_status=member.membership_status.value,
            already_marked_today=already_marked,
        )

    @staticmethod
    def confirm_and_mark(db: Session, data: QRConfirmRequest) -> dict:
        """
        Step 2 — Member confirms their identity and self-marks as present.
        Status is always PRESENT (self-service via QR cannot mark absent/late).
        Raises 409 if already marked for the target date.
        """
        target_date = data.attendance_date or date.today()

        # Verify the member_id is valid (prevents forged UUIDs)
        AttendanceService._get_member_or_404(db, data.member_id)

        existing = db.query(Attendance).filter(
            Attendance.member_id == data.member_id,
            Attendance.attendance_date == target_date,
            Attendance.is_deleted == False,
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"You have already been marked as present on {target_date.isoformat()}.",
            )

        record = Attendance(
            member_id=data.member_id,
            attendance_date=target_date,
            status=AttendanceStatusEnum.PRESENT,
            check_in_time=datetime.utcnow(),
            notes="Self-checked via QR code",
        )
        db.add(record)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Attendance already recorded for this member and date.",
            )

        db.refresh(record)
        record = AttendanceService._get_record_or_404(db, record.id)
        return _build_response_dict(record)


    @staticmethod
    def bulk_mark_attendance(db: Session, data: AttendanceBulkCreate) -> dict:
        """
        Mark attendance for multiple members at once.
        Members that already have a record for the date are skipped (not errored).
        """
        target_date = data.attendance_date or date.today()
        created_list: List[dict] = []
        skipped_ids: List[UUID] = []

        for member_id in data.member_ids:
            # Validate member exists
            member = db.query(Member).filter(
                Member.id == member_id,
                Member.is_deleted == False
            ).first()
            if not member:
                skipped_ids.append(member_id)
                continue

            existing = db.query(Attendance).filter(
                Attendance.member_id == member_id,
                Attendance.attendance_date == target_date,
                Attendance.is_deleted == False
            ).first()
            if existing:
                skipped_ids.append(member_id)
                continue

            record = Attendance(
                member_id=member_id,
                attendance_date=target_date,
                status=data.status,
                check_in_time=datetime.utcnow(),
                notes=data.notes,
            )
            db.add(record)

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="One or more duplicate attendance records encountered during bulk insert."
            )

        # Re-query freshly created records for the date to build response
        created_records = (
            db.query(Attendance)
            .options(joinedload(Attendance.member))
            .filter(
                Attendance.member_id.in_(data.member_ids),
                Attendance.attendance_date == target_date,
                Attendance.is_deleted == False
            )
            .all()
        )
        for r in created_records:
            created_list.append(_build_response_dict(r))

        return {
            "created": created_list,
            "skipped": skipped_ids,
            "total_created": len(created_list),
            "total_skipped": len(skipped_ids),
        }

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    @staticmethod
    def get_attendance(db: Session, attendance_id: UUID) -> dict:
        record = AttendanceService._get_record_or_404(db, attendance_id)
        return _build_response_dict(record)

    @staticmethod
    def get_attendance_records(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        member_id: Optional[UUID] = None,
        attendance_date: Optional[date] = None,
        status_filter: Optional[AttendanceStatusEnum] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> tuple[List[dict], int]:
        """Return paginated attendance records with optional filters."""
        query = (
            db.query(Attendance)
            .options(joinedload(Attendance.member))
            .filter(Attendance.is_deleted == False)
        )

        if member_id:
            query = query.filter(Attendance.member_id == member_id)
        if attendance_date:
            query = query.filter(Attendance.attendance_date == attendance_date)
        if status_filter:
            query = query.filter(Attendance.status == status_filter)
        if from_date:
            query = query.filter(Attendance.attendance_date >= from_date)
        if to_date:
            query = query.filter(Attendance.attendance_date <= to_date)

        total = query.count()
        records = (
            query.order_by(Attendance.attendance_date.desc(), Attendance.check_in_time.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [_build_response_dict(r) for r in records], total

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    @staticmethod
    def update_attendance(db: Session, attendance_id: UUID, data: AttendanceUpdate) -> dict:
        record = AttendanceService._get_record_or_404(db, attendance_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(record, field, value)

        db.commit()
        db.refresh(record)
        record = AttendanceService._get_record_or_404(db, record.id)
        return _build_response_dict(record)

    # ------------------------------------------------------------------
    # Delete (soft)
    # ------------------------------------------------------------------

    @staticmethod
    def delete_attendance(db: Session, attendance_id: UUID) -> dict:
        record = AttendanceService._get_record_or_404(db, attendance_id)
        record.is_deleted = True
        db.commit()
        db.refresh(record)
        return _build_response_dict(record)
