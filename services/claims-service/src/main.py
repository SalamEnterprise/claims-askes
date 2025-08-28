"""
Claims Service - Main Application
Microservice for claims processing and management
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from src.config.settings import settings
from src.api.v1 import endpoints
from src.utils.logging import setup_logging
from src.events.consumers import start_event_consumers
from src.database import init_db

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info(f"Starting {settings.SERVICE_NAME} service...")
    
    # Initialize database
    await init_db()
    
    # Start event consumers
    if settings.ENABLE_EVENT_CONSUMERS:
        await start_event_consumers()
    
    logger.info(f"{settings.SERVICE_NAME} service started successfully")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.SERVICE_NAME} service...")
    # Cleanup resources here
    

# Create FastAPI application
app = FastAPI(
    title=f"{settings.SERVICE_NAME} Service",
    description="Microservice for claims processing and management",
    version=settings.VERSION,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(
    endpoints.router,
    prefix="/api/v1"
)

# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": settings.VERSION
    }

@app.get("/ready")
async def readiness_check():
    """Readiness check - verify dependencies"""
    # TODO: Check database connection
    # TODO: Check Redis connection
    # TODO: Check RabbitMQ connection
    return {
        "status": "ready",
        "service": settings.SERVICE_NAME
    }