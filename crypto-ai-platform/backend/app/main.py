"""
Main FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys

from app.core.config import settings
from app.core.database import init_db
from app.api import coins, ai_predictions, users, dashboard


# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL,
)
logger.add(
    settings.LOG_FILE,
    rotation="500 MB",
    retention="10 days",
    level=settings.LOG_LEVEL,
)


def create_application() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AI-powered cryptocurrency ATH recovery prediction platform",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    
    # Configure CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    application.include_router(coins.router, prefix="/api/v1/coins", tags=["Coins"])
    application.include_router(ai_predictions.router, prefix="/api/v1/ai", tags=["AI Predictions"])
    application.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
    application.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
    
    @application.get("/")
    async def root():
        """Root endpoint"""
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running",
            "docs": "/docs",
        }
    
    @application.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy"}
    
    @application.on_event("startup")
    async def startup_event():
        """Application startup event"""
        logger.info("Starting up Crypto AI Platform...")
        try:
            init_db()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
    
    @application.on_event("shutdown")
    async def shutdown_event():
        """Application shutdown event"""
        logger.info("Shutting down Crypto AI Platform...")
    
    return application


# Create the application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
