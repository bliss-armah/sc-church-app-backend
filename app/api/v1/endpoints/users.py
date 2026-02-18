from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
import math

from app.api.deps import get_db, require_admin
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    UserResetPassword,
    UserRole
)
from app.services.user import UserService
from app.config import settings
from app.models.user import User

router = APIRouter()


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user (Admin only)"
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a new user account (Admin only).
    
    - **email**: Unique email address
    - **username**: Unique username (3-100 characters, alphanumeric with hyphens/underscores)
    - **full_name**: User's full name
    - **password**: Initial password (must be 8+ chars with uppercase, lowercase, and number)
    - **role**: User role (admin or user)
    
    **Note:** New users will have `must_change_password` set to true.
    """
    return UserService.create_user(db, user_data)


@router.get(
    "/",
    response_model=UserListResponse,
    summary="List all users (Admin only)"
)
def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(
        settings.DEFAULT_PAGE_SIZE,
        ge=1,
        le=settings.MAX_PAGE_SIZE,
        description="Items per page"
    ),
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get a paginated list of users (Admin only).
    
    - **page**: Page number (starts at 1)
    - **page_size**: Number of items per page
    - **role**: Filter by role (admin or user)
    - **is_active**: Filter by active status
    """
    skip = (page - 1) * page_size
    users, total = UserService.get_users(
        db,
        skip=skip,
        limit=page_size,
        role=role,
        is_active=is_active
    )
    
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    
    return UserListResponse(
        items=users,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID (Admin only)"
)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get a specific user by their UUID (Admin only).
    """
    return UserService.get_user(db, user_id)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user (Admin only)"
)
def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update a user's information (Admin only).
    
    Only provided fields will be updated.
    """
    return UserService.update_user(db, user_id, user_data)


@router.post(
    "/{user_id}/reset-password",
    response_model=UserResponse,
    summary="Reset user password (Admin only)"
)
def reset_user_password(
    user_id: UUID,
    password_data: UserResetPassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Reset a user's password (Admin only).
    
    The user will be required to change their password on next login.
    """
    return UserService.reset_password(db, user_id, password_data)


@router.delete(
    "/{user_id}",
    response_model=UserResponse,
    summary="Delete user (Admin only)"
)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Soft delete a user (Admin only).
    
    The user will be marked as deleted and deactivated.
    Cannot delete the last admin user.
    """
    return UserService.delete_user(db, user_id)
