# Claims Service

## Overview

The Claims Service is the core microservice responsible for managing the entire claims lifecycle from submission to payment. It handles claim creation, validation, status management, and orchestrates the claims workflow.

## Table of Contents
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Events](#events)
- [Configuration](#configuration)
- [Testing](#testing)
- [Deployment](#deployment)
- [Monitoring](#monitoring)

## Architecture

### Service Responsibilities
- Claim submission and validation
- Claim status management
- Document attachment handling
- Workflow orchestration
- Event publishing for downstream services

### Technology Stack
- **Language**: Python 3.11+
- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL 15+ (claims_service schema)
- **ORM**: SQLAlchemy 2.0 + Alembic
- **Cache**: Redis with redis-py
- **Message Queue**: Celery with Redis
- **API Client**: httpx for async HTTP
- **Validation**: Pydantic 2.0+
- **Testing**: pytest, pytest-asyncio, pytest-cov

### Domain Model
```python
# Domain model following DDD principles
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from enum import Enum

class ClaimStatus(Enum):
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"

@dataclass
class ClaimItem:
    """Entity representing a line item in a claim"""
    id: str
    benefit_code: str
    amount: float
    quantity: int
    status: str

@dataclass
class ClaimDocument:
    """Entity representing attached documents"""
    id: str
    document_type: str
    file_path: str
    uploaded_at: datetime

@dataclass
class Claim:
    """Aggregate Root for claims domain"""
    id: str
    claim_number: str
    member_id: str
    provider_id: str
    status: ClaimStatus
    items: List[ClaimItem]
    documents: List[ClaimDocument]
    total_amount: float
    created_at: datetime
```

## Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Redis 7+ (for both caching and message queue)

### Installation

1. **Clone the service** (if working standalone)
```bash
git clone <repository>
cd services/claims-service
```

2. **Set up virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
# Or using poetry
poetry install
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run database migrations**
```bash
alembic upgrade head
```

6. **Start Celery worker** (in separate terminal)
```bash
celery -A src.workers.celery_app worker --loglevel=info
```

7. **Start the service**
```bash
# Development
uvicorn src.main:app --reload --port 8001

# Production with Gunicorn
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001

# Production with Hypercorn (alternative)
hypercorn src.main:app --bind 0.0.0.0:8001 --workers 4
```

## API Documentation

### Base URL
- Development: `http://localhost:8001`
- Production: `https://api.claims-askes.com/claims`

### Authentication
All endpoints require JWT authentication:
```http
Authorization: Bearer <jwt_token>
```

### Main Endpoints

#### Submit Claim
```http
POST /api/v1/claims
Content-Type: application/json

{
  "member_id": "uuid",
  "provider_id": "uuid",
  "claim_type": "cashless|reimbursement",
  "service_type": "inpatient|outpatient",
  "service_date": "2024-01-15",
  "items": [...]
}
```

#### Get Claim
```http
GET /api/v1/claims/{claim_id}
```

#### List Claims
```http
GET /api/v1/claims?member_id={uuid}&status={status}&page=1&size=20
```

#### Update Claim Status
```http
PATCH /api/v1/claims/{claim_id}/status
```

#### Upload Document
```http
POST /api/v1/claims/{claim_id}/documents
Content-Type: multipart/form-data
```

### API Documentation URLs
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`
- OpenAPI Schema: `http://localhost:8001/openapi.json`

## Database Schema

### Schema: `claims_service`

#### Tables

**claim**
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| claim_number | VARCHAR(50) | Unique claim number |
| member_id | UUID | Reference to member service |
| provider_id | UUID | Reference to provider service |
| policy_id | UUID | Reference to policy service |
| claim_type | VARCHAR(20) | cashless/reimbursement |
| service_type | VARCHAR(20) | inpatient/outpatient/dental/optical |
| status | VARCHAR(30) | Claim status |
| submission_date | TIMESTAMP | When claim was submitted |
| created_at | TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | Last update time |

**claim_item**
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| claim_id | UUID | Foreign key to claim |
| benefit_code | VARCHAR(50) | Benefit identifier |
| charged_amount | DECIMAL(15,2) | Amount charged |
| approved_amount | DECIMAL(15,2) | Amount approved |

**claim_document**
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| claim_id | UUID | Foreign key to claim |
| document_type | VARCHAR(50) | Type of document |
| file_path | VARCHAR(500) | Storage path |

## Events

### Published Events

#### ClaimSubmitted
```json
{
  "event_type": "claim.submitted",
  "claim_id": "uuid",
  "member_id": "uuid",
  "provider_id": "uuid",
  "timestamp": "2024-01-20T10:00:00Z"
}
```

#### ClaimStatusChanged
```json
{
  "event_type": "claim.status_changed",
  "claim_id": "uuid",
  "old_status": "submitted",
  "new_status": "processing",
  "timestamp": "2024-01-20T10:00:00Z"
}
```

### Consumed Events
- `member.updated` - Update member cache
- `provider.updated` - Update provider cache
- `adjudication.completed` - Update claim with adjudication results

## Configuration

### Environment Variables

```bash
# Service Configuration
SERVICE_NAME=claims-service
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://claims_service_user:password@localhost:5432/claims_askes
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery Broker (Redis)
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Security
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256

# Service Discovery
MEMBER_SERVICE_URL=http://localhost:8002
PROVIDER_SERVICE_URL=http://localhost:8003
BENEFIT_SERVICE_URL=http://localhost:8004
```

### Feature Flags
```python
ENABLE_CACHE = True
ENABLE_EVENT_PUBLISHING = True
ENABLE_ASYNC_PROCESSING = True
```

## Testing

### Unit Tests
```bash
# Run unit tests
pytest tests/unit -v

# With coverage
pytest tests/unit --cov=src --cov-report=html --cov-report=term

# Run with markers
pytest -m "not slow" -v  # Skip slow tests
pytest -m database -v    # Only database tests
```

### Integration Tests
```bash
# Run integration tests
pytest tests/integration -v

# Specific test file
pytest tests/integration/test_claim_api.py -v

# Run with test database
DATABASE_URL=postgresql://test_user:pass@localhost/test_db pytest tests/integration
```

### Test Coverage
Minimum required coverage: 80%

### Testing Structure
```
tests/
├── unit/
│   ├── test_models.py
│   ├── test_schemas.py
│   ├── test_services.py
│   ├── test_repositories.py
│   └── test_utils.py
├── integration/
│   ├── test_api.py
│   ├── test_database.py
│   ├── test_celery_tasks.py
│   └── test_events.py
├── fixtures/
│   ├── claim_fixtures.py
│   └── database_fixtures.py
└── conftest.py  # Pytest configuration
```

### Example Test
```python
# tests/unit/test_services.py
import pytest
from unittest.mock import Mock, AsyncMock
from src.services.claim_service import ClaimService
from src.schemas.claim import ClaimCreate

@pytest.mark.asyncio
async def test_submit_claim():
    # Arrange
    mock_repo = Mock()
    mock_repo.create = AsyncMock(return_value={"id": "123", "status": "submitted"})
    service = ClaimService(mock_repo)
    
    claim_data = ClaimCreate(
        member_id="member-123",
        provider_id="provider-456",
        service_date="2024-01-15",
        items=[{"benefit_code": "CONS-GP", "amount": 500000}]
    )
    
    # Act
    result = await service.submit_claim(claim_data)
    
    # Assert
    assert result["id"] == "123"
    assert result["status"] == "submitted"
    mock_repo.create.assert_called_once()
```

## Deployment

### Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run as non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
# Build image
docker build -t claims-service:latest .

# Run container
docker run -d \
  --name claims-service \
  -p 8001:8000 \
  -e DATABASE_URL=postgresql://user:pass@db:5432/claims \
  -e REDIS_URL=redis://redis:6379 \
  -e CELERY_BROKER_URL=amqp://rabbitmq:5672 \
  claims-service:latest

# Run with docker-compose
docker-compose up -d
```

### Kubernetes

Apply deployment:
```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### Health Checks
- Liveness: `/health`
- Readiness: `/ready`

## Monitoring

### Metrics
Service exposes Prometheus metrics at `/metrics`:
- `claims_submitted_total` - Total claims submitted
- `claims_processing_duration` - Processing time histogram
- `claims_status_count` - Claims by status

### Logging
Structured JSON logging with correlation IDs:
```json
{
  "timestamp": "2024-01-20T10:00:00Z",
  "level": "INFO",
  "service": "claims-service",
  "correlation_id": "abc-123",
  "message": "Claim submitted successfully"
}
```

### Alerts
Key alerts configured:
- High error rate (>1%)
- Processing delays (>5s)
- Database connection issues
- Queue lag

## Project Structure

```
claims-service/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── claims.py    # Claims endpoints
│   │   │   ├── documents.py # Document endpoints
│   │   │   └── health.py    # Health check
│   │   └── dependencies.py  # Dependency injection
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # Settings management
│   │   ├── security.py      # Security utilities
│   │   └── exceptions.py    # Custom exceptions
│   ├── models/
│   │   ├── __init__.py
│   │   ├── claim.py         # SQLAlchemy models
│   │   ├── claim_item.py
│   │   └── document.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── claim.py         # Pydantic schemas
│   │   ├── response.py
│   │   └── request.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── claim_service.py # Business logic
│   │   ├── validation_service.py
│   │   └── eligibility_service.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── claim_repository.py
│   │   └── base_repository.py
│   ├── workers/
│   │   ├── __init__.py
│   │   ├── celery_app.py    # Celery configuration
│   │   └── tasks.py          # Async tasks
│   └── utils/
│       ├── __init__.py
│       ├── database.py       # Database utilities
│       └── cache.py          # Redis utilities
├── migrations/               # Alembic migrations
│   ├── alembic.ini
│   └── versions/
├── tests/
├── requirements.txt
├── pyproject.toml           # Poetry configuration
├── Dockerfile
└── .env.example
```

## Code Examples

### FastAPI Application Setup
```python
# src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from src.api.v1 import claims, documents, health
from src.core.config import settings
from src.utils.database import engine, Base
from src.utils.cache import redis_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await redis_client.ping()
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    await redis_client.close()

app = FastAPI(
    title="Claims Service",
    description="Claims processing microservice",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(claims.router, prefix="/api/v1/claims", tags=["claims"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(health.router, prefix="/health", tags=["health"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.DEBUG
    )
```

### API Endpoint Example
```python
# src/api/v1/claims.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.claim import ClaimCreate, ClaimResponse, ClaimUpdate
from src.services.claim_service import ClaimService
from src.api.dependencies import get_db, get_current_user
from src.core.exceptions import ClaimNotFoundError

router = APIRouter()

@router.post("/", response_model=ClaimResponse, status_code=status.HTTP_201_CREATED)
async def submit_claim(
    claim_data: ClaimCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Submit a new insurance claim"""
    service = ClaimService(db)
    try:
        claim = await service.submit_claim(claim_data, current_user.id)
        return claim
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{claim_id}", response_model=ClaimResponse)
async def get_claim(
    claim_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get claim details by ID"""
    service = ClaimService(db)
    try:
        claim = await service.get_claim(claim_id, current_user.id)
        return claim
    except ClaimNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )

@router.get("/", response_model=List[ClaimResponse])
async def list_claims(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List claims with pagination and filtering"""
    service = ClaimService(db)
    claims = await service.list_claims(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status
    )
    return claims
```

### Service Layer Example
```python
# src/services/claim_service.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import uuid
from datetime import datetime

from src.models.claim import Claim, ClaimItem
from src.schemas.claim import ClaimCreate, ClaimUpdate
from src.repositories.claim_repository import ClaimRepository
from src.workers.tasks import process_claim_async
from src.utils.cache import cache_key, invalidate_cache

class ClaimService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ClaimRepository(db)
    
    async def submit_claim(self, claim_data: ClaimCreate, user_id: str) -> Claim:
        """Submit a new claim and trigger async processing"""
        
        # Generate claim number
        claim_number = await self._generate_claim_number()
        
        # Create claim entity
        claim = Claim(
            id=str(uuid.uuid4()),
            claim_number=claim_number,
            member_id=claim_data.member_id,
            provider_id=claim_data.provider_id,
            service_date=claim_data.service_date,
            status="submitted",
            created_by=user_id,
            created_at=datetime.utcnow()
        )
        
        # Add claim items
        for item_data in claim_data.items:
            item = ClaimItem(
                id=str(uuid.uuid4()),
                claim_id=claim.id,
                benefit_code=item_data.benefit_code,
                amount=item_data.amount,
                quantity=item_data.quantity
            )
            claim.items.append(item)
        
        # Save to database
        saved_claim = await self.repository.create(claim)
        
        # Trigger async processing
        process_claim_async.delay(claim.id)
        
        # Invalidate cache
        await invalidate_cache(f"claims:user:{user_id}")
        
        return saved_claim
    
    async def _generate_claim_number(self) -> str:
        """Generate unique claim number"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = str(uuid.uuid4())[:6].upper()
        return f"CLM-{timestamp}-{random_suffix}"
```

### Celery Task Example
```python
# src/workers/tasks.py
from celery import Celery
from src.core.config import settings
from src.services.validation_service import ValidationService
from src.services.eligibility_service import EligibilityService

# Configure Celery with Redis
celery_app = Celery(
    "claims_worker",
    broker=settings.CELERY_BROKER_URL,  # redis://localhost:6379/1
    backend=settings.CELERY_RESULT_BACKEND  # redis://localhost:6379/2
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    redis_max_connections=50,
    redis_socket_keepalive=True,
    redis_socket_keepalive_options={
        1: 3,  # TCP_KEEPIDLE
        2: 3,  # TCP_KEEPINTVL
        3: 3,  # TCP_KEEPCNT
    }
)

@celery_app.task(bind=True, max_retries=3)
def process_claim_async(self, claim_id: str):
    """Asynchronously process claim validation and eligibility"""
    try:
        # Validate claim
        validation_service = ValidationService()
        validation_result = validation_service.validate_claim(claim_id)
        
        if not validation_result.is_valid:
            update_claim_status(claim_id, "rejected", validation_result.errors)
            return
        
        # Check eligibility
        eligibility_service = EligibilityService()
        eligibility_result = eligibility_service.check_eligibility(claim_id)
        
        if not eligibility_result.is_eligible:
            update_claim_status(claim_id, "rejected", eligibility_result.reason)
            return
        
        # Approve claim
        update_claim_status(claim_id, "approved")
        
        # Trigger payment processing
        process_payment_async.delay(claim_id)
        
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check DATABASE_URL configuration
   - Verify PostgreSQL is running
   - Check network connectivity

2. **Redis Connection Error**
   - Verify Redis is running
   - Check REDIS_URL configuration

3. **Authentication Error**
   - Verify JWT_SECRET matches auth service
   - Check token expiration

## Support

- **Documentation**: [Full documentation](../../docs/)
- **API Spec**: [OpenAPI specification](./docs/openapi.yaml)
- **Issues**: Create ticket in issue tracker
- **Team**: Claims Processing Team

## License

Proprietary - All rights reserved