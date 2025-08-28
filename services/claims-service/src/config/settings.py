"""
Claims Service Configuration
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Service Information
    SERVICE_NAME: str = "claims-service"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://claims_service_user:claims_pass_dev@localhost:5432/claims_askes"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40
    DATABASE_POOL_TIMEOUT: int = 30
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_POOL_SIZE: int = 10
    
    # RabbitMQ
    RABBITMQ_URL: str = "amqp://admin:admin@localhost:5672/"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002"
    ]
    
    # Service URLs (for inter-service communication)
    MEMBER_SERVICE_URL: str = "http://localhost:8002"
    PROVIDER_SERVICE_URL: str = "http://localhost:8003"
    BENEFIT_SERVICE_URL: str = "http://localhost:8004"
    AUTHORIZATION_SERVICE_URL: str = "http://localhost:8005"
    
    # Feature Flags
    ENABLE_EVENT_CONSUMERS: bool = True
    ENABLE_CACHE: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()