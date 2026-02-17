import logging
import sys
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.ai.ai_service_manager import ai_service_manager
from app.api import chat, coping, dashboard, mood, users
from app.core.config import get_settings
from app.core.exceptions import CustomHTTPException
from app.core.logging import setup_logging
from app.database.database import Base, engine

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting AI Mental Health Companion API")

    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)

    yield

    # Shutdown
    logger.info("Shutting down AI Mental Health Companion API")


# Create FastAPI app
app = FastAPI(
    title="AI Mental Health Companion API",
    description="A supportive, privacy-first API providing emotional support, mood tracking, and personalized coping tools",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

# Add trusted host middleware for security
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)


# Custom exception handler
@app.exception_handler(CustomHTTPException)
async def custom_http_exception_handler(request, exc: CustomHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "type": exc.error_type,
            "timestamp": exc.timestamp.isoformat(),
        },
    )


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "An internal server error occurred. Our team has been notified.",
            "type": "internal_server_error",
        },
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "AI Mental Health Companion API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }


# AI Services health check endpoint
@app.get("/health/ai")
async def ai_health_check():
    """Health check endpoint for AI services"""
    try:
        health_status = await ai_service_manager.health_check()
        return {
            "status": "healthy"
            if health_status["overall_status"] == "healthy"
            else "degraded",
            "ai_services": health_status,
            "gemini_enabled": settings.GEMINI_ENABLED,
            "ai_model_type": settings.AI_MODEL_TYPE,
        }
    except Exception as e:
        logger.error(f"AI health check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "gemini_enabled": settings.GEMINI_ENABLED,
            "ai_model_type": settings.AI_MODEL_TYPE,
        }


# AI Services statistics endpoint
@app.get("/health/ai/stats")
async def ai_statistics():
    """Get comprehensive AI service statistics"""
    try:
        stats = ai_service_manager.get_service_statistics()
        return stats
    except Exception as e:
        logger.error(f"Failed to get AI statistics: {e}")
        return {"error": str(e)}


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to AI Mental Health Companion API",
        "description": "A supportive, privacy-first API for emotional well-being",
        "version": "1.0.0",
        "documentation": "/docs"
        if settings.ENVIRONMENT != "production"
        else "Contact support for documentation",
        "support": {
            "crisis_hotline": "988",
            "crisis_text": "Text HOME to 741741",
            "note": "This API is not a replacement for professional mental health care",
        },
    }


# Include routers
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])

app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])

app.include_router(mood.router, prefix="/api/v1/mood", tags=["mood"])

app.include_router(coping.router, prefix="/api/v1/coping", tags=["coping"])

app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])


# Middleware to add request ID and logging
@app.middleware("http")
async def add_request_id_and_logging(request, call_next):
    import time
    import uuid

    request_id = str(uuid.uuid4())
    start_time = time.time()

    # Add request ID to headers
    request.state.request_id = request_id

    # Log incoming request
    logger.info(
        f"Incoming request",
        extra={
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else "unknown",
        },
    )

    response = await call_next(request)

    # Calculate processing time
    process_time = time.time() - start_time

    # Add custom headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)

    # Log response
    logger.info(
        f"Request completed",
        extra={
            "request_id": request_id,
            "status_code": response.status_code,
            "process_time": process_time,
        },
    )

    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level="info",
    )
