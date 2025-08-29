# Claims Engine Service

## Overview
The Claims Engine Service is the core service responsible for managing the entire claims lifecycle from submission to payment. It orchestrates the claims workflow, manages state transitions, and coordinates with other services.

## Architecture

### Domain Model
```python
# Core domain entities
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum
import uuid

class ClaimType(Enum):
    PROFESSIONAL = "professional"
    INSTITUTIONAL = "institutional"
    DENTAL = "dental"
    PHARMACY = "pharmacy"

class ClaimStatus(Enum):
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"
    APPEALED = "appealed"

@dataclass
class ClaimItem:
    """Represents a line item in a claim"""
    id: uuid.UUID
    claim_id: uuid.UUID
    service_code: str
    diagnosis_code: str
    procedure_code: str
    quantity: Decimal
    charged_amount: Decimal
    allowed_amount: Decimal
    paid_amount: Decimal

@dataclass
class Document:
    """Represents a document attached to a claim"""
    id: uuid.UUID
    document_type: str
    file_path: str
    uploaded_at: datetime

@dataclass
class Authorization:
    """Represents pre-authorization data"""
    auth_number: str
    approved_date: datetime
    approved_amount: Decimal
    valid_until: datetime

@dataclass
class Adjudication:
    """Represents adjudication results"""
    adjudicated_date: datetime
    allowed_amount: Decimal
    copay_amount: Decimal
    deductible_amount: Decimal
    coinsurance_amount: Decimal

@dataclass
class Payment:
    """Represents payment information"""
    payment_number: str
    payment_date: datetime
    payment_amount: Decimal
    payment_method: str

@dataclass
class AuditEntry:
    """Represents an audit trail entry"""
    timestamp: datetime
    user_id: str
    action: str
    details: dict

@dataclass
class Claim:
    """Aggregate root for claims domain"""
    id: uuid.UUID
    claim_number: str
    member_id: uuid.UUID
    provider_id: uuid.UUID
    service_date: datetime
    submission_date: datetime
    claim_type: ClaimType
    status: ClaimStatus
    items: List[ClaimItem]
    documents: List[Document]
    authorization: Optional[Authorization]
    adjudication: Optional[Adjudication]
    payment: Optional[Payment]
    audit_trail: List[AuditEntry]
```

### Service Structure
```
claims-engine/
├── src/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application entry point
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── claims.py          # Claims REST endpoints
│   │   │   ├── workflow.py        # Workflow endpoints
│   │   │   └── health.py          # Health checks
│   │   ├── graphql/
│   │   │   ├── __init__.py
│   │   │   ├── schema.py          # GraphQL schema
│   │   │   └── resolvers.py       # GraphQL resolvers
│   │   └── dependencies.py        # FastAPI dependencies
│   │
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── entities/
│   │   │   ├── __init__.py
│   │   │   ├── claim.py           # Claim entity
│   │   │   └── claim_item.py      # Claim item entity
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   └── claim_repository.py # Repository interface
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── claim_service.py   # Domain service
│   │   │   └── workflow_service.py # Workflow orchestration
│   │   └── events/
│   │       ├── __init__.py
│   │       └── claim_events.py    # Domain events
│   │
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── postgres.py        # SQLAlchemy setup
│   │   │   └── models.py          # SQLAlchemy models
│   │   ├── messaging/
│   │   │   ├── __init__.py
│   │   │   ├── kafka_client.py    # Kafka producer/consumer
│   │   │   └── events.py          # Event publishing
│   │   ├── cache/
│   │   │   ├── __init__.py
│   │   │   └── redis_cache.py     # Redis cache
│   │   └── external/
│   │       ├── __init__.py
│   │       ├── authorization_client.py
│   │       └── adjudication_client.py
│   │
│   ├── application/
│   │   ├── __init__.py
│   │   ├── commands/
│   │   │   ├── __init__.py
│   │   │   ├── submit_claim.py    # Submit claim command
│   │   │   └── approve_claim.py   # Approve claim command
│   │   ├── queries/
│   │   │   ├── __init__.py
│   │   │   ├── get_claim.py       # Get claim query
│   │   │   └── list_claims.py     # List claims query
│   │   └── handlers/
│   │       ├── __init__.py
│   │       └── event_handlers.py  # Event handlers
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Configuration settings
│   │   ├── exceptions.py          # Custom exceptions
│   │   └── security.py            # Security utilities
│   │
│   └── workers/
│       ├── __init__.py
│       ├── celery_app.py          # Celery configuration
│       └── tasks.py               # Async tasks
│
├── migrations/                     # Alembic migrations
│   ├── alembic.ini
│   ├── env.py
│   └── versions/
│
├── tests/
│   ├── __init__.py
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── deployments/
│   ├── Dockerfile
│   ├── kubernetes/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── configmap.yaml
│   └── helm/
│       └── claims-engine/
│
├── docs/
│   ├── api.md
│   └── workflow.md
│
├── requirements.txt               # Python dependencies
├── pyproject.toml                # Poetry configuration
├── setup.py                      # Package setup
├── .env.example                  # Environment variables example
└── README.md
```

## API Documentation

### REST API

#### Submit Claim
```http
POST /api/v1/claims
Content-Type: application/json

{
  "memberId": "550e8400-e29b-41d4-a716-446655440000",
  "providerId": "660e8400-e29b-41d4-a716-446655440001",
  "serviceDate": "2024-01-15",
  "claimType": "professional",
  "items": [
    {
      "serviceCode": "99213",
      "diagnosisCode": "J06.9",
      "quantity": 1,
      "chargedAmount": 150.00
    }
  ]
}

Response: 201 Created
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "claimNumber": "CLM-2024-000001",
  "status": "submitted",
  "createdAt": "2024-01-20T10:00:00Z"
}
```

#### Get Claim Status
```http
GET /api/v1/claims/{claimId}

Response: 200 OK
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "claimNumber": "CLM-2024-000001",
  "status": "processing",
  "memberId": "550e8400-e29b-41d4-a716-446655440000",
  "providerId": "660e8400-e29b-41d4-a716-446655440001",
  "serviceDate": "2024-01-15",
  "submissionDate": "2024-01-20",
  "items": [...],
  "adjudication": {
    "allowedAmount": 120.00,
    "paidAmount": 96.00,
    "memberResponsibility": 24.00
  }
}
```

### gRPC API (Optional)

If gRPC support is needed, use grpcio-tools:

```python
# src/api/grpc/claims_service.py
import grpc
from concurrent import futures
from src.api.grpc import claims_pb2, claims_pb2_grpc

class ClaimsServicer(claims_pb2_grpc.ClaimsServiceServicer):
    def __init__(self, claim_service):
        self.claim_service = claim_service
    
    async def SubmitClaim(self, request, context):
        """Submit a new claim via gRPC"""
        claim = await self.claim_service.submit_claim(
            member_id=request.member_id,
            provider_id=request.provider_id,
            service_date=request.service_date,
            items=request.items
        )
        return claims_pb2.SubmitClaimResponse(
            claim_id=claim.id,
            claim_number=claim.claim_number,
            status=claim.status
        )
    
    async def GetClaim(self, request, context):
        """Get claim details via gRPC"""
        claim = await self.claim_service.get_claim(request.claim_id)
        if not claim:
            context.abort(grpc.StatusCode.NOT_FOUND, "Claim not found")
        return self._claim_to_proto(claim)
    
    async def ListClaims(self, request, context):
        """List claims with pagination"""
        claims = await self.claim_service.list_claims(
            member_id=request.member_id,
            status=request.status,
            page=request.page,
            size=request.size
        )
        return claims_pb2.ListClaimsResponse(
            claims=[self._claim_to_proto(c) for c in claims],
            total=len(claims)
        )
```

### GraphQL API

```graphql
type Query {
  claim(id: ID!): Claim
  claims(
    memberId: ID
    status: ClaimStatus
    dateFrom: Date
    dateTo: Date
    first: Int
    after: String
  ): ClaimConnection!
}

type Mutation {
  submitClaim(input: SubmitClaimInput!): Claim!
  approveClaim(id: ID!): Claim!
  denyClaim(id: ID!, reason: String!): Claim!
}

type Claim {
  id: ID!
  claimNumber: String!
  member: Member!
  provider: Provider!
  serviceDate: Date!
  status: ClaimStatus!
  items: [ClaimItem!]!
  adjudication: Adjudication
  payment: Payment
}
```

## Events

### Published Events
```python
# src/domain/events/claim_events.py
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
import uuid

@dataclass
class ClaimSubmittedEvent:
    """Event published when a claim is submitted"""
    event_id: str
    claim_id: str
    member_id: str
    provider_id: str
    service_date: datetime
    timestamp: datetime
    
    def to_dict(self):
        return {
            "event_id": self.event_id,
            "event_type": "claim.submitted",
            "claim_id": self.claim_id,
            "member_id": self.member_id,
            "provider_id": self.provider_id,
            "service_date": self.service_date.isoformat(),
            "timestamp": self.timestamp.isoformat()
        }

@dataclass
class ClaimApprovedEvent:
    """Event published when a claim is approved"""
    event_id: str
    claim_id: str
    approved_amount: Decimal
    timestamp: datetime
    
    def to_dict(self):
        return {
            "event_id": self.event_id,
            "event_type": "claim.approved",
            "claim_id": self.claim_id,
            "approved_amount": str(self.approved_amount),
            "timestamp": self.timestamp.isoformat()
        }

@dataclass
class ClaimRejectedEvent:
    """Event published when a claim is rejected"""
    event_id: str
    claim_id: str
    rejection_reason: str
    timestamp: datetime
    
    def to_dict(self):
        return {
            "event_id": self.event_id,
            "event_type": "claim.rejected",
            "claim_id": self.claim_id,
            "rejection_reason": self.rejection_reason,
            "timestamp": self.timestamp.isoformat()
        }
```

### Consumed Events
- `AuthorizationApprovedEvent`
- `AdjudicationCompletedEvent`
- `PaymentProcessedEvent`

## Configuration

### Environment Variables
```bash
# Server Configuration
SERVER_PORT=8080
SERVER_HOST=0.0.0.0
WORKERS=4
ENVIRONMENT=production

# Database Configuration
DATABASE_URL=postgresql://claims_user:secure_password@postgres:5432/claims
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
DB_POOL_TIMEOUT=30

# Redis Configuration (Cache and Message Broker)
REDIS_URL=redis://redis:6379/0
CACHE_TTL=3600

# Celery Configuration
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2
CELERY_TASK_SERIALIZER=json
CELERY_RESULT_SERIALIZER=json

# Kafka Configuration (if needed for events)
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_CONSUMER_GROUP=claims-engine
KAFKA_TOPICS=claims.events,authorization.events,adjudication.events

# Service Discovery
AUTHORIZATION_SERVICE_URL=http://authorization:8081
ADJUDICATION_SERVICE_URL=http://adjudication:8082
PAYMENT_SERVICE_URL=http://payment:8083

# Observability
JAEGER_AGENT_HOST=jaeger
JAEGER_AGENT_PORT=6831
METRICS_PORT=9091

# Security
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30
ENCRYPTION_KEY=your-encryption-key

# API Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

## Database Schema

```sql
-- Claims table
CREATE TABLE claims (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_number VARCHAR(50) UNIQUE NOT NULL,
    member_id UUID NOT NULL,
    provider_id UUID NOT NULL,
    service_date DATE NOT NULL,
    submission_date TIMESTAMP NOT NULL DEFAULT NOW(),
    claim_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    total_charged DECIMAL(10,2),
    total_allowed DECIMAL(10,2),
    total_paid DECIMAL(10,2),
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Claim items table
CREATE TABLE claim_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id UUID NOT NULL REFERENCES claims(id),
    service_code VARCHAR(50) NOT NULL,
    diagnosis_code VARCHAR(50),
    procedure_code VARCHAR(50),
    quantity DECIMAL(10,2) NOT NULL DEFAULT 1,
    charged_amount DECIMAL(10,2) NOT NULL,
    allowed_amount DECIMAL(10,2),
    paid_amount DECIMAL(10,2),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_claims_member_id ON claims(member_id);
CREATE INDEX idx_claims_provider_id ON claims(provider_id);
CREATE INDEX idx_claims_status ON claims(status);
CREATE INDEX idx_claims_service_date ON claims(service_date);
```

## Development

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Kafka 3.0+ (optional for event streaming)
- Docker & Docker Compose

### Local Development
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
# Or using Poetry
poetry install

# Run database migrations
alembic upgrade head

# Start Celery worker (in separate terminal)
celery -A src.workers.celery_app worker --loglevel=info

# Start Celery beat scheduler (for periodic tasks)
celery -A src.workers.celery_app beat --loglevel=info

# Run service locally
uvicorn src.main:app --reload --port 8080

# Or with multiple workers
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080

# Build Docker image
docker build -t claims-engine:latest .

# Run with Docker Compose
docker-compose up
```

### Testing
```bash
# Run all tests
pytest

# Run unit tests
pytest tests/unit -v

# Run integration tests
pytest tests/integration -v

# Run E2E tests
pytest tests/e2e -v

# Run with coverage
pytest --cov=src --cov-report=html --cov-report=term

# Run specific test file
pytest tests/unit/test_claim_service.py -v

# Run tests with markers
pytest -m "not slow" -v  # Skip slow tests
pytest -m database -v    # Only database tests

# Type checking
mypy src/

# Linting
ruff check src/
black src/ --check

# Format code
black src/
ruff format src/
```

## Deployment

### Docker
```dockerfile
# Dockerfile
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Kubernetes
```yaml
# deployments/kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: claims-engine
spec:
  replicas: 3
  selector:
    matchLabels:
      app: claims-engine
  template:
    metadata:
      labels:
        app: claims-engine
    spec:
      containers:
      - name: claims-engine
        image: claims-engine:latest
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: claims-engine-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: claims-engine-secrets
              key: redis-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

```bash
# Deploy to Kubernetes
kubectl apply -f deployments/kubernetes/ -n claims-dev

# Deploy with Helm
helm install claims-engine ./deployments/helm/claims-engine -n claims-prod
```

### Health Checks
```python
# src/api/v1/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.dependencies import get_db
from src.utils.cache import redis_client

router = APIRouter()

@router.get("/live")
async def liveness():
    """Liveness probe for Kubernetes"""
    return {"status": "alive"}

@router.get("/ready")
async def readiness(db: AsyncSession = Depends(get_db)):
    """Readiness probe checking dependencies"""
    try:
        # Check database
        await db.execute("SELECT 1")
        # Check Redis
        await redis_client.ping()
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not_ready", "error": str(e)}, 503

@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from fastapi.responses import Response
    
    metrics_data = generate_latest()
    return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)
```

- **Liveness**: `/health/live`
- **Readiness**: `/health/ready`
- **Metrics**: `/metrics`

## Monitoring

### Metrics
```python
# src/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
claims_submitted_total = Counter(
    'claims_submitted_total',
    'Total number of claims submitted',
    ['claim_type', 'status']
)

claims_processed_total = Counter(
    'claims_processed_total',
    'Total number of claims processed',
    ['status', 'processor']
)

claims_processing_duration = Histogram(
    'claims_processing_duration_seconds',
    'Time spent processing claims',
    ['claim_type', 'status'],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
)

claims_status_count = Gauge(
    'claims_status_count',
    'Current count of claims by status',
    ['status']
)

celery_tasks_pending = Gauge(
    'celery_tasks_pending',
    'Number of pending Celery tasks',
    ['queue']
)
```

- `claims_submitted_total` - Total claims submitted
- `claims_processed_total` - Total claims processed
- `claims_processing_duration_seconds` - Processing duration histogram
- `claims_status_count` - Claims by status
- `celery_tasks_pending` - Pending async tasks

### Logging
```python
# src/core/logging.py
import logging
import json
from pythonjsonlogger import jsonlogger

# Configure structured logging
logger = logging.getLogger("claims_engine")
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    "%(timestamp)s %(level)s %(name)s %(message)s",
    timestamp=True
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Usage with correlation ID
def log_with_context(correlation_id: str, message: str, **kwargs):
    logger.info(
        message,
        extra={
            "correlation_id": correlation_id,
            **kwargs
        }
    )
```

### Alerts
- High error rate (>1%)
- Processing delays (>5s)
- Database connection issues
- Redis connection issues
- Celery queue lag

## Code Examples

### FastAPI Application
```python
# src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from strawberry.fastapi import GraphQLRouter

from src.api.v1 import claims, workflow, health
from src.api.graphql.schema import schema
from src.core.config import settings
from src.infrastructure.database.postgres import engine, Base
from src.infrastructure.cache.redis_cache import redis_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await redis_client.ping()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await redis_client.close()
    await engine.dispose()

app = FastAPI(
    title="Claims Engine Service",
    description="Core claims processing and workflow orchestration",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST API routes
app.include_router(claims.router, prefix="/api/v1/claims", tags=["claims"])
app.include_router(workflow.router, prefix="/api/v1/workflow", tags=["workflow"])
app.include_router(health.router, prefix="/health", tags=["health"])

# GraphQL endpoint
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=settings.ENVIRONMENT == "development"
    )
```

### Claim Service Implementation
```python
# src/domain/services/claim_service.py
from typing import List, Optional
from datetime import datetime
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.claim import Claim, ClaimStatus
from src.domain.repositories.claim_repository import ClaimRepository
from src.domain.events.claim_events import ClaimSubmittedEvent
from src.infrastructure.messaging.events import EventPublisher
from src.workers.tasks import process_claim_async

class ClaimService:
    def __init__(self, db: AsyncSession):
        self.repository = ClaimRepository(db)
        self.event_publisher = EventPublisher()
    
    async def submit_claim(self, claim_data: dict) -> Claim:
        """Submit a new claim for processing"""
        
        # Create claim entity
        claim = Claim(
            id=uuid.uuid4(),
            claim_number=self._generate_claim_number(),
            member_id=claim_data['member_id'],
            provider_id=claim_data['provider_id'],
            service_date=claim_data['service_date'],
            submission_date=datetime.utcnow(),
            claim_type=claim_data['claim_type'],
            status=ClaimStatus.SUBMITTED,
            items=claim_data['items'],
            documents=[],
            authorization=None,
            adjudication=None,
            payment=None,
            audit_trail=[]
        )
        
        # Save to database
        saved_claim = await self.repository.save(claim)
        
        # Publish event
        event = ClaimSubmittedEvent(
            event_id=str(uuid.uuid4()),
            claim_id=str(claim.id),
            member_id=str(claim.member_id),
            provider_id=str(claim.provider_id),
            service_date=claim.service_date,
            timestamp=datetime.utcnow()
        )
        await self.event_publisher.publish(event)
        
        # Trigger async processing
        process_claim_async.delay(str(claim.id))
        
        return saved_claim
    
    async def get_claim(self, claim_id: str) -> Optional[Claim]:
        """Get claim by ID"""
        return await self.repository.get_by_id(claim_id)
    
    async def update_status(self, claim_id: str, status: ClaimStatus) -> Claim:
        """Update claim status"""
        claim = await self.repository.get_by_id(claim_id)
        if not claim:
            raise ValueError(f"Claim {claim_id} not found")
        
        claim.status = status
        return await self.repository.save(claim)
    
    def _generate_claim_number(self) -> str:
        """Generate unique claim number"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = str(uuid.uuid4())[:6].upper()
        return f"CLM-{timestamp}-{random_suffix}"
```

### Workflow Orchestration
```python
# src/domain/services/workflow_service.py
from typing import Dict, Any
import asyncio
from src.domain.services.claim_service import ClaimService
from src.infrastructure.external.authorization_client import AuthorizationClient
from src.infrastructure.external.adjudication_client import AdjudicationClient

class WorkflowService:
    def __init__(self):
        self.claim_service = ClaimService()
        self.auth_client = AuthorizationClient()
        self.adjudication_client = AdjudicationClient()
    
    async def process_claim_workflow(self, claim_id: str) -> Dict[str, Any]:
        """Orchestrate the complete claim processing workflow"""
        
        # Step 1: Get claim
        claim = await self.claim_service.get_claim(claim_id)
        if not claim:
            raise ValueError(f"Claim {claim_id} not found")
        
        # Step 2: Check authorization (if required)
        if claim.claim_type in ['institutional', 'inpatient']:
            auth_result = await self.auth_client.check_authorization(
                member_id=claim.member_id,
                provider_id=claim.provider_id,
                service_codes=[item.service_code for item in claim.items]
            )
            if not auth_result['approved']:
                await self.claim_service.update_status(claim_id, 'rejected')
                return {"status": "rejected", "reason": "Authorization denied"}
        
        # Step 3: Adjudicate claim
        adjudication_result = await self.adjudication_client.adjudicate(
            claim_id=claim_id,
            items=claim.items
        )
        
        # Step 4: Update claim with results
        if adjudication_result['approved']:
            await self.claim_service.update_status(claim_id, 'approved')
            # Trigger payment processing
            await self._trigger_payment(claim_id, adjudication_result)
        else:
            await self.claim_service.update_status(claim_id, 'rejected')
        
        return {
            "status": adjudication_result['status'],
            "approved_amount": adjudication_result.get('approved_amount'),
            "member_responsibility": adjudication_result.get('member_responsibility')
        }
    
    async def _trigger_payment(self, claim_id: str, adjudication_result: Dict):
        """Trigger payment processing for approved claim"""
        from src.workers.tasks import process_payment_async
        process_payment_async.delay(claim_id, adjudication_result)
```

### Celery Tasks
```python
# src/workers/tasks.py
from celery import Celery
from src.core.config import settings

# Configure Celery with Redis
celery_app = Celery(
    'claims_engine',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)

@celery_app.task(bind=True, max_retries=3)
def process_claim_async(self, claim_id: str):
    """Process claim asynchronously"""
    try:
        from src.domain.services.workflow_service import WorkflowService
        workflow_service = WorkflowService()
        
        # Run async workflow
        import asyncio
        result = asyncio.run(
            workflow_service.process_claim_workflow(claim_id)
        )
        
        return result
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)

@celery_app.task
def process_payment_async(claim_id: str, adjudication_result: dict):
    """Process payment for approved claim"""
    # Payment processing logic
    pass
```

## SLA
- **Availability**: 99.99%
- **Response Time**: <500ms (p99)
- **Throughput**: 1000 claims/second
- **Processing Time**: <5s for clean claims

---

*For more information, see the [main documentation](../../../docs/README.md)*