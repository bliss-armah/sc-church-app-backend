from pydantic import Field, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID
import enum

from app.schemas.base import CamelModel


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"


class UserBase(CamelModel):
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., min_length=3, max_length=100, description="Username for login")
    full_name: str = Field(..., min_length=1, max_length=255, description="User's full name")
    role: UserRole = Field(default=UserRole.USER, description="User role (admin or user)")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Username cannot be empty or whitespace')
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v.strip().lower()


class UserCreate(UserBase):
    """Schema for creating a new user (admin only)"""
    password: str = Field(..., min_length=8, description="Initial password (user must change on first login)")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v


class UserUpdate(CamelModel):
    """Schema for updating user (admin only)"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserChangePassword(CamelModel):
    """Schema for user changing their own password"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v


class UserResetPassword(CamelModel):
    """Schema for admin resetting user password"""
    new_password: str = Field(..., min_length=8, description="New password")
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v


class UserResponse(CamelModel):
    """Schema for user response (without password)"""
    id: UUID
    email: EmailStr
    username: str
    full_name: str
    role: UserRole
    is_active: bool
    must_change_password: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]


class UserListResponse(CamelModel):
    """Schema for paginated user list response"""
    items: list[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class Token(CamelModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(CamelModel):
    """Schema for token payload data"""
    user_id: Optional[UUID] = None
    username: Optional[str] = None
    role: Optional[UserRole] = None


class LoginRequest(CamelModel):
    """Schema for login request"""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")
