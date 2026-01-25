"""FastAPI application main entry point."""

from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.redis.redis_manager import redis_manager
from app.database.database import engine, SessionLocal, get_db
from app.modules.auth.routes import router as auth_router
from app.modules.newsletters.newsletter_templates.routes import router as newsletter_router
from app.modules.subscribers.routes import public_router as subscription_router
from app.modules.subscribers.routes import protected_router as subscriber_management_router
from app.modules.billing.routes import router as billing_router
from app.modules.campaign.routes import router as campaign_router
from app.utils import constants


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Handles startup and shutdown events.
    """
    # Startup
    await redis_manager.redis_connect(constants.REDIS_URL)
    
    yield
    
    # Shutdown
    await redis_manager.redis_disconnect()


# Create FastAPI app
app = FastAPI(
    title="SkyMail",
    description="Newsletter service platform for companies",
    version="0.1.0",
    lifespan=lifespan
)

# ==================== MIDDLEWARE CONFIGURATION ====================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Frontend development
        "http://localhost:8000",  # API development
        constants.FRONTEND_URL,
        "*"  # Allow all in development (restrict in production)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Accept",
        "Origin"
    ],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Session Middleware for Google OAuth
app.add_middleware(
    SessionMiddleware,
    secret_key=constants.GOOGLE_OAUTH_SESSION_KEY,
    session_cookie="skymail_session",
    max_age=3600 * 24 * 7  # 7 days
)

# ==================== ROUTES ====================

# Health check endpoint
@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    description="Check if the API is running"
)
async def health():
    """Health check endpoint."""
    return {
        "message": "Service is healthy!",
        "status": "operational",
        "service": "SkyMail"
    }


# Include authentication routes
app.include_router(auth_router)

# Include newsletter routes
app.include_router(newsletter_router)

# Include campaign routes
app.include_router(campaign_router)

# Include public subscription routes (CORS enabled)
app.include_router(subscription_router)

# Include protected subscriber management routes
app.include_router(subscriber_management_router)

# Include billing routes
app.include_router(billing_router)

# ==================== ROOT ENDPOINT ====================

@app.get(
    "/",
    tags=["Root"],
    summary="API Information",
    description="Get API information"
)
async def root():
    """Root endpoint with API information."""
    return {
        "service": "SkyMail",
        "description": "Newsletter service platform for companies",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=constants.SERVER_HOST,
        port=constants.SERVER_PORT,
        reload=True,
        log_level="info"
    )
