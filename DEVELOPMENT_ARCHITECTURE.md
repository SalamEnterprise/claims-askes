# Development Architecture - Claims-Askes Platform

## Core Principles
- **Microservices**: Domain-driven, loosely coupled services
- **Event-Driven**: Asynchronous communication between services
- **API-First**: All services expose REST APIs
- **Database-per-Service**: Each service owns its data
- **Python-Native**: Leverage Python ecosystem strengths

## Service Architecture

### 1. Claims Service
**Purpose**: Core claims processing engine

```python
backend/claims/
├── app/
│   ├── api/v1/          # FastAPI routes
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   ├── repositories/     # Data access layer
│   └── utils/           # Utilities
├── migrations/          # Alembic migrations
└── tests/              # Test suites
```

**Key Models**:
- Claim
- ClaimItem
- ClaimDocument
- ClaimStatus
- ClaimWorkflow

**Core APIs**:
- POST /claims - Submit claim
- GET /claims/{id} - Get claim details
- PUT /claims/{id}/status - Update status
- POST /claims/{id}/documents - Upload documents

### 2. Authorization Service
**Purpose**: Pre-authorization and medical necessity

**Key Models**:
- Authorization
- AuthorizationRule
- ClinicalGuideline
- AuthorizationStatus

**Core APIs**:
- POST /authorizations - Request authorization
- GET /authorizations/{id} - Get authorization
- PUT /authorizations/{id}/approve - Approve
- PUT /authorizations/{id}/deny - Deny

### 3. Adjudication Service
**Purpose**: Benefit calculation and rule processing

**Key Models**:
- AdjudicationResult
- BenefitCalculation
- RuleExecution
- Accumulator

**Core APIs**:
- POST /adjudicate - Process claim
- GET /benefits/calculate - Calculate benefits
- GET /accumulators/{member_id} - Get accumulator status

### 4. Payment Service
**Purpose**: Payment processing and EOB generation

**Key Models**:
- Payment
- PaymentBatch
- EOB (Explanation of Benefits)
- RemittanceAdvice

**Core APIs**:
- POST /payments - Process payment
- GET /payments/{id} - Get payment details
- POST /payments/batch - Batch payment
- GET /eob/{claim_id} - Generate EOB

### 5. Member Service
**Purpose**: Member management and eligibility

**Key Models**:
- Member
- MemberCoverage
- Dependent
- EligibilityPeriod

**Core APIs**:
- GET /members/{id} - Get member
- POST /members - Create member
- GET /members/{id}/eligibility - Check eligibility
- GET /members/{id}/coverage - Get coverage

### 6. Provider Service
**Purpose**: Provider network management

**Key Models**:
- Provider
- ProviderContract
- ProviderSpecialty
- NetworkStatus

**Core APIs**:
- GET /providers/{id} - Get provider
- POST /providers - Register provider
- GET /providers/search - Search providers
- PUT /providers/{id}/contract - Update contract

### 7. Benefit Service
**Purpose**: Benefit configuration and management

**Key Models**:
- PlanBenefit
- BenefitLimit
- BenefitCategory
- CoverageRule

**Core APIs**:
- GET /benefits/plans/{id} - Get plan benefits
- POST /benefits/plans - Create plan
- PUT /benefits/plans/{id} - Update plan
- GET /benefits/check - Check benefit coverage

### 8. Policy Service
**Purpose**: Policy administration

**Key Models**:
- Policy
- PolicyHolder
- PolicyPeriod
- Premium

**Core APIs**:
- GET /policies/{id} - Get policy
- POST /policies - Create policy
- PUT /policies/{id} - Update policy
- GET /policies/{id}/members - Get policy members

## Database Schema Organization

```sql
-- Logical schema separation
CREATE SCHEMA claims;      -- Claims domain
CREATE SCHEMA member;      -- Member domain
CREATE SCHEMA provider;    -- Provider domain
CREATE SCHEMA benefit;     -- Benefit configuration
CREATE SCHEMA policy;      -- Policy administration
CREATE SCHEMA billing;     -- Payment & billing
CREATE SCHEMA audit;       -- Audit logs
```

## Service Communication

### Synchronous (REST)
```python
# Example: Claims service calling Authorization
async def check_authorization(claim_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://authorization-service/api/v1/check/{claim_id}"
        )
        return response.json()
```

### Asynchronous (Events)
```python
# Example: Publishing claim submitted event
from celery import Celery

celery = Celery('claims')

@celery.task
def publish_claim_submitted(claim_data):
    # Publish to message queue
    return publish_event('claim.submitted', claim_data)
```

## Shared Code Structure

```python
backend/shared/
├── models/
│   ├── base.py          # Base SQLAlchemy model
│   ├── mixins.py        # Common mixins (timestamps, etc)
│   └── enums.py         # Shared enums
├── schemas/
│   ├── common.py        # Common Pydantic schemas
│   └── responses.py     # Standard API responses
├── database/
│   ├── session.py       # Database session management
│   └── utils.py         # Database utilities
├── auth/
│   ├── jwt.py          # JWT handling
│   └── permissions.py   # Permission checking
└── utils/
    ├── dates.py        # Date utilities
    ├── money.py        # Money/currency handling
    └── validators.py   # Common validators
```

## API Gateway Pattern

```python
# backend/gateway/app/main.py
from fastapi import FastAPI
from .routers import claims, members, providers

app = FastAPI(title="Claims-Askes API Gateway")

# Route to microservices
app.include_router(claims.router, prefix="/api/v1/claims")
app.include_router(members.router, prefix="/api/v1/members")
app.include_router(providers.router, prefix="/api/v1/providers")

@app.middleware("http")
async def add_auth_header(request, call_next):
    # Add authentication/authorization
    response = await call_next(request)
    return response
```

## Service Template

Each service follows this structure:

```python
# app/main.py
from fastapi import FastAPI
from .api.v1 import endpoints
from .core.config import settings
from .database import init_db

app = FastAPI(title=f"{SERVICE_NAME} Service")

@app.on_event("startup")
async def startup():
    await init_db()

app.include_router(endpoints.router, prefix="/api/v1")

# app/models/claim.py
from sqlalchemy import Column, String, DateTime
from shared.models.base import Base

class Claim(Base):
    __tablename__ = "claims"
    
    id = Column(String, primary_key=True)
    claim_number = Column(String, unique=True)
    # ... other fields

# app/schemas/claim.py
from pydantic import BaseModel
from datetime import datetime

class ClaimCreate(BaseModel):
    member_id: str
    provider_id: str
    service_date: datetime
    
class ClaimResponse(BaseModel):
    id: str
    claim_number: str
    status: str

# app/services/claim_service.py
class ClaimService:
    def __init__(self, repository):
        self.repository = repository
    
    async def create_claim(self, claim_data):
        # Business logic here
        return await self.repository.create(claim_data)

# app/repositories/claim_repository.py
class ClaimRepository:
    def __init__(self, session):
        self.session = session
    
    async def create(self, claim_data):
        # Database operations
        pass
```

## Development Workflow

### 1. Local Development
```bash
# Start infrastructure
docker-compose up -d

# Start a service
cd backend/claims
poetry run uvicorn app.main:app --reload --port 8001

# Run tests
poetry run pytest
```

### 2. Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Add claim status"

# Run migrations
alembic upgrade head
```

### 3. API Testing
```bash
# Use httpie or curl
http POST localhost:8001/api/v1/claims \
    member_id=123 \
    provider_id=456 \
    service_date=2024-01-01
```

## Configuration Management

### Environment Variables
```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    jwt_secret: str
    service_name: str = "claims"
    debug: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### Service Discovery
```python
# Simple service registry
SERVICES = {
    "claims": "http://localhost:8001",
    "authorization": "http://localhost:8002",
    "adjudication": "http://localhost:8003",
    "payment": "http://localhost:8004",
    "member": "http://localhost:8005",
    "provider": "http://localhost:8006",
    "benefit": "http://localhost:8007",
    "policy": "http://localhost:8008",
}
```

## Testing Strategy

### Unit Tests
```python
# tests/unit/test_claim_service.py
import pytest
from app.services.claim_service import ClaimService

@pytest.mark.asyncio
async def test_create_claim():
    service = ClaimService(mock_repository)
    result = await service.create_claim(claim_data)
    assert result.id is not None
```

### Integration Tests
```python
# tests/integration/test_api.py
from fastapi.testclient import TestClient

def test_submit_claim(client: TestClient):
    response = client.post("/api/v1/claims", json=claim_data)
    assert response.status_code == 201
```

## Security Considerations

### Authentication
- JWT tokens for API authentication
- Service-to-service authentication
- Role-based access control (RBAC)

### Data Protection
- Encrypt PII fields in database
- Use SSL/TLS for all communications
- Audit logging for all operations

## Performance Optimization

### Database
- Connection pooling
- Query optimization
- Proper indexing
- Read replicas for queries

### Caching
- Redis for session cache
- API response caching
- Database query caching

### Async Operations
- Use async/await throughout
- Background tasks with Celery
- Event-driven processing

## Next Steps

1. **Phase 1**: Core Services (Claims, Member, Provider)
2. **Phase 2**: Processing Services (Authorization, Adjudication, Payment)
3. **Phase 3**: Configuration Services (Benefit, Policy)
4. **Phase 4**: Integration with external systems
5. **Phase 5**: Frontend applications
6. **Phase 6**: Performance optimization
7. **Phase 7**: Security hardening