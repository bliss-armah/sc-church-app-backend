from fastapi import APIRouter
from app.api.v1.endpoints import members, auth, users

api_router = APIRouter()

# Authentication endpoints (public)
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

# User management endpoints (admin only)
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

# Member management endpoints (authenticated users)
api_router.include_router(
    members.router,
    prefix="/members",
    tags=["members"]
)

# Future routers can be added here:
# api_router.include_router(attendance.router, prefix="/attendance", tags=["attendance"])
# api_router.include_router(donations.router, prefix="/donations", tags=["donations"])
# api_router.include_router(groups.router, prefix="/groups", tags=["groups"])
