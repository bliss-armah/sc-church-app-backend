from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from fastapi import HTTPException, status
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserChangePassword, UserResetPassword
from app.core.security import get_password_hash, verify_password


class UserService:
    """Service layer for user management and authentication"""
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user (admin only)"""
        # Check if email already exists
        existing_user = db.query(User).filter(
            User.email == user_data.email,
            User.is_deleted == False
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists"
            )
        
        # Check if username already exists
        existing_user = db.query(User).filter(
            User.username == user_data.username.lower(),
            User.is_deleted == False
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this username already exists"
            )
        
        # Create user
        user = User(
            email=user_data.email,
            username=user_data.username.lower(),
            full_name=user_data.full_name,
            role=user_data.role,
            hashed_password=get_password_hash(user_data.password),
            must_change_password=True,  # Force password change on first login
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate a user by username/email and password"""
        # Try to find by username or email
        user = db.query(User).filter(
            ((User.username == username.lower()) | (User.email == username.lower())),
            User.is_deleted == False
        ).first()
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        return user
    
    @staticmethod
    def get_user(db: Session, user_id: UUID) -> User:
        """Get a user by ID"""
        user = db.query(User).filter(
            User.id == user_id,
            User.is_deleted == False
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    
    @staticmethod
    def get_users(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[User], int]:
        """Get paginated list of users with optional filters"""
        query = db.query(User).filter(User.is_deleted == False)
        
        # Filter by role
        if role:
            query = query.filter(User.role == role)
        
        # Filter by active status
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
        
        return users, total
    
    @staticmethod
    def update_user(db: Session, user_id: UUID, user_data: UserUpdate) -> User:
        """Update a user (admin only)"""
        user = UserService.get_user(db, user_id)
        
        # Check email uniqueness if being updated
        if user_data.email and user_data.email != user.email:
            existing_user = db.query(User).filter(
                User.email == user_data.email,
                User.is_deleted == False,
                User.id != user_id
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A user with this email already exists"
                )
        
        # Update only provided fields
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def change_password(
        db: Session,
        user: User,
        password_data: UserChangePassword
    ) -> User:
        """Change user's own password"""
        # Verify current password
        if not verify_password(password_data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        user.hashed_password = get_password_hash(password_data.new_password)
        user.must_change_password = False
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def reset_password(
        db: Session,
        user_id: UUID,
        password_data: UserResetPassword
    ) -> User:
        """Reset user password (admin only)"""
        user = UserService.get_user(db, user_id)
        
        # Update password
        user.hashed_password = get_password_hash(password_data.new_password)
        user.must_change_password = True  # Force password change on next login
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: UUID) -> User:
        """Soft delete a user (admin only)"""
        user = UserService.get_user(db, user_id)
        
        # Prevent deleting the last super_admin
        if user.role == UserRole.SUPER_ADMIN:
            admin_count = db.query(User).filter(
                User.role == UserRole.SUPER_ADMIN,
                User.is_deleted == False
            ).count()
            if admin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete the last super admin user"
                )
        
        user.is_deleted = True
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def create_default_admin(db: Session) -> Optional[User]:
        """Create default admin user if no users exist"""
        # Check if any users exist
        user_count = db.query(User).filter(User.is_deleted == False).count()
        if user_count > 0:
            return None
        
        # Create default admin
        admin = User(
            email="admin@cms.com",
            username="admin",
            full_name="System Administrator",
            role=UserRole.SUPER_ADMIN,
            hashed_password=get_password_hash("Admin@123"),
            must_change_password=True,
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        return admin
