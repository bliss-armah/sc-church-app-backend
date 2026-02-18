from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID
import enum


class GenderEnum(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class MembershipStatusEnum(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    VISITOR = "visitor"


class MemberBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100, description="Member's first name")
    second_name: Optional[str] = Field(None, max_length=100, description="Member's middle name")
    other_names: Optional[str] = Field(None, max_length=255, description="Additional names")
    last_name: str = Field(..., min_length=1, max_length=100, description="Member's last name")
    date_of_birth: date = Field(..., description="Member's date of birth")
    gender: GenderEnum = Field(..., description="Member's gender")
    phone_number: Optional[str] = Field(None, max_length=20, description="Contact phone number")
    email: Optional[EmailStr] = Field(None, description="Contact email address")
    address: Optional[str] = Field(None, description="Physical address")
    membership_status: MembershipStatusEnum = Field(
        default=MembershipStatusEnum.VISITOR,
        description="Current membership status"
    )
    date_joined: date = Field(..., description="Date member joined the church")
    notes: Optional[str] = Field(None, description="Additional notes about the member")
    
    @field_validator('date_of_birth')
    @classmethod
    def validate_date_of_birth(cls, v: date) -> date:
        if v > date.today():
            raise ValueError('Date of birth cannot be in the future')
        if v.year < 1900:
            raise ValueError('Date of birth must be after 1900')
        return v
    
    @field_validator('date_joined')
    @classmethod
    def validate_date_joined(cls, v: date) -> date:
        if v > date.today():
            raise ValueError('Date joined cannot be in the future')
        return v
    
    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_names(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip()


class MemberCreate(MemberBase):
    """Schema for creating a new member"""
    pass


class MemberUpdate(BaseModel):
    """Schema for updating a member - all fields optional"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    second_name: Optional[str] = Field(None, max_length=100)
    other_names: Optional[str] = Field(None, max_length=255)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    membership_status: Optional[MembershipStatusEnum] = None
    date_joined: Optional[date] = None
    notes: Optional[str] = None
    
    @field_validator('date_of_birth')
    @classmethod
    def validate_date_of_birth(cls, v: Optional[date]) -> Optional[date]:
        if v is not None:
            if v > date.today():
                raise ValueError('Date of birth cannot be in the future')
            if v.year < 1900:
                raise ValueError('Date of birth must be after 1900')
        return v
    
    @field_validator('date_joined')
    @classmethod
    def validate_date_joined(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v > date.today():
            raise ValueError('Date joined cannot be in the future')
        return v


class MemberResponse(MemberBase):
    """Schema for member response"""
    id: UUID
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MemberListResponse(BaseModel):
    """Schema for paginated member list response"""
    items: List[MemberResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
