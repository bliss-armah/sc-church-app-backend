from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1.router import api_router
from app.database import engine, Base, SessionLocal
from app.services.user import UserService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create default admin user if no users exist
db = SessionLocal()
try:
    admin = UserService.create_default_admin(db)
    if admin:
        print(f"✅ Default admin user created:")
        print(f"   Username: admin")
        print(f"   Password: Admin@123")
        print(f"   ⚠️  Please change the password after first login!")
finally:
    db.close()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for Church Management System with Authentication",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Tell FastAPI to serialise every response_model using its camelCase aliases.
# This means every endpoint automatically returns camelCase JSON without any
# per-endpoint changes.
from fastapi.routing import APIRoute
from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel as PydanticBaseModel

class _AliasJSONResponse(JSONResponse):
    """Renders Pydantic models using their aliases (camelCase) globally."""
    def render(self, content) -> bytes:
        if isinstance(content, PydanticBaseModel):
            return content.model_dump_json(by_alias=True).encode("utf-8")
        return super().render(content)

app.router.default_response_class = _AliasJSONResponse


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["root"])
def read_root():
    """Root endpoint - API health check"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health", tags=["root"])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
