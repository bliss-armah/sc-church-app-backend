from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from uuid import UUID
from app.models.member import Member
from app.schemas.member import MemberCreate, MemberUpdate
from fastapi import HTTPException, status


class MemberService:
    """Service layer for member business logic"""
    
    @staticmethod
    def create_member(db: Session, member_data: MemberCreate) -> Member:
        """Create a new member"""
        # Check if email already exists
        if member_data.email:
            existing_member = db.query(Member).filter(
                Member.email == member_data.email,
                Member.is_deleted == False
            ).first()
            if existing_member:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A member with this email already exists"
                )
        
        member = Member(**member_data.model_dump())
        db.add(member)
        db.commit()
        db.refresh(member)
        return member
    
    @staticmethod
    def get_member(db: Session, member_id: UUID) -> Member:
        """Get a member by ID"""
        member = db.query(Member).filter(
            Member.id == member_id,
            Member.is_deleted == False
        ).first()
        
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )
        return member
    
    @staticmethod
    def get_members(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        membership_status: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[Member], int]:
        """Get paginated list of members with optional filters"""
        query = db.query(Member).filter(Member.is_deleted == False)
        
        # Filter by membership status
        if membership_status:
            query = query.filter(Member.membership_status == membership_status)
        
        # Search by name, email, or phone
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Member.first_name.ilike(search_term)) |
                (Member.last_name.ilike(search_term)) |
                (Member.email.ilike(search_term)) |
                (Member.phone_number.ilike(search_term))
            )
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        members = query.order_by(Member.last_name, Member.first_name).offset(skip).limit(limit).all()
        
        return members, total
    
    @staticmethod
    def update_member(db: Session, member_id: UUID, member_data: MemberUpdate) -> Member:
        """Update a member"""
        member = MemberService.get_member(db, member_id)
        
        # Check email uniqueness if being updated
        if member_data.email and member_data.email != member.email:
            existing_member = db.query(Member).filter(
                Member.email == member_data.email,
                Member.is_deleted == False,
                Member.id != member_id
            ).first()
            if existing_member:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A member with this email already exists"
                )
        
        # Update only provided fields
        update_data = member_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(member, field, value)
        
        db.commit()
        db.refresh(member)
        return member
    
    @staticmethod
    def delete_member(db: Session, member_id: UUID) -> Member:
        """Soft delete a member"""
        member = MemberService.get_member(db, member_id)
        member.is_deleted = True
        db.commit()
        db.refresh(member)
        return member
