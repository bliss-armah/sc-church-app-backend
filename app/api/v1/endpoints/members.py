from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
import math

from app.api.deps import get_db, require_member_access
from app.schemas.member import (
    MemberCreate,
    MemberUpdate,
    MemberResponse,
    MemberListResponse,
    MembershipStatusEnum
)
from app.services.member import MemberService
from app.config import settings
from app.models.user import User

router = APIRouter()


@router.post(
    "/",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new member"
)
def create_member(
    member_data: MemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_member_access)
):
    """
    Create a new church member with the following information:
    
    - **first_name**: Required - Member's first name
    - **last_name**: Required - Member's last name
    - **date_of_birth**: Required - Must be a valid past date
    - **gender**: Required - male, female, or other
    - **date_joined**: Required - Date member joined the church
    - **membership_status**: Optional - active, inactive, or visitor (default: visitor)
    - **email**: Optional - Must be unique if provided
    - **phone_number**: Optional - Contact phone
    - **address**: Optional - Physical address
    - **second_name**: Optional - Middle name
    - **other_names**: Optional - Additional names
    - **notes**: Optional - Additional information
    
    **Authentication required:** Any authenticated user can create members.
    """
    return MemberService.create_member(db, member_data)


@router.get(
    "/",
    response_model=MemberListResponse,
    summary="List all members"
)
def list_members(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(
        settings.DEFAULT_PAGE_SIZE,
        ge=1,
        le=settings.MAX_PAGE_SIZE,
        description="Items per page"
    ),
    membership_status: Optional[MembershipStatusEnum] = Query(
        None,
        description="Filter by membership status"
    ),
    search: Optional[str] = Query(
        None,
        description="Search by name, email, or phone"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_member_access)
):
    """
    Get a paginated list of church members.
    
    - **page**: Page number (starts at 1)
    - **page_size**: Number of items per page
    - **membership_status**: Filter by status (active, inactive, visitor)
    - **search**: Search by name, email, or phone number
    
    **Authentication required:** Any authenticated user can view members.
    """
    skip = (page - 1) * page_size
    members, total = MemberService.get_members(
        db,
        skip=skip,
        limit=page_size,
        membership_status=membership_status,
        search=search
    )
    
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    
    return MemberListResponse(
        items=members,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get(
    "/{member_id}",
    response_model=MemberResponse,
    summary="Get member by ID"
)
def get_member(
    member_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_member_access)
):
    """
    Get a specific member by their UUID.
    
    **Authentication required:** Any authenticated user can view member details.
    """
    return MemberService.get_member(db, member_id)


@router.put(
    "/{member_id}",
    response_model=MemberResponse,
    summary="Update member"
)
def update_member(
    member_id: UUID,
    member_data: MemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_member_access)
):
    """
    Update a member's information. Only provided fields will be updated.
    
    **Authentication required:** Any authenticated user can update members.
    """
    return MemberService.update_member(db, member_id, member_data)


@router.delete(
    "/{member_id}",
    response_model=MemberResponse,
    summary="Delete member"
)
def delete_member(
    member_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_member_access)
):
    """
    Soft delete a member. The member will be marked as deleted but not removed from the database.
    
    **Authentication required:** Any authenticated user can delete members.
    """
    return MemberService.delete_member(db, member_id)
