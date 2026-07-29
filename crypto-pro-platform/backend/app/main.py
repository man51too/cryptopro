"""
CryptoPro AI - Main Application Entry Point

Professional-grade cryptocurrency analysis and prediction platform.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import logging

from .core.config import settings
from .core.database import init_db, close_db
from .api.v1.endpoints import coins, ai_predictions, dashboard


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting CryptoPro AI Platform...")
    await init_db()
    logger.info("Database initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CryptoPro AI Platform...")
    await close_db()
    logger.info("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
## CryptoPro AI Platform

Professional cryptocurrency analysis and ATH recovery prediction platform.

### Features

- **ATH Recovery Scanner**: Scan top 1000 cryptocurrencies for ATH recovery opportunities
- **AI Predictions**: Advanced machine learning models for price prediction
- **Technical Analysis**: Professional-grade technical indicators
- **Real-time Updates**: WebSocket-based live data streaming
- **Dashboard**: Comprehensive market overview and analytics

### API Sections

- **Coins**: Cryptocurrency data and ATH analysis
- **AI Predictions**: ML-powered predictions and scores
- **Dashboard**: Market overview and statistics
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(coins.router, prefix="/api/v1/coins", tags=["Coins"])
app.include_router(ai_predictions.router, prefix="/api/v1/ai", tags=["AI Predictions"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "environment": settings.FASTAPI_ENV,
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }


@app.websocket("/ws/market")
async def websocket_market(websocket: WebSocket):
    """
    WebSocket endpoint for real-time market data.
    
    Clients can connect to receive live price updates and AI score changes.
    """
    await websocket.accept()
    
    # Track connection
    logger.info(f"WebSocket client connected")
    
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            
            # Process message (subscribe to specific coins, etc.)
            # For now, echo back acknowledgment
            await websocket.send_json({
                "type": "acknowledgment",
                "message": f"Received: {data}",
                "status": "connected"
            })
            
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else 4,
    )
