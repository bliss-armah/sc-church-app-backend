from typing import Generator
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.database import SessionLocal
from app.core.security import decode_access_token
from app.models.user import User, UserRole
from app.schemas.user import TokenData


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/token")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.
    Ensures proper session cleanup after request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False
    ).first()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (not deleted, is active).
    """
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Require that the current user has super_admin role.
    """
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin privileges required"
        )
    return current_user


async def require_member_access(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Require super_admin, calling_team, or texting_team role.
    All authenticated roles can access member data.
    """
    return current_user


async def require_attendance_access(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Require super_admin or calling_team to access attendance data.
    """
    if current_user.role == UserRole.TEXTING_TEAM:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Attendance access requires calling_team or super_admin role"
        )
    return current_user
