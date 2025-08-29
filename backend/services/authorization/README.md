# Authorization Service

## Overview

The Authorization Service manages pre-authorization requirements for medical procedures, inpatient admissions, and high-cost treatments. It ensures that medical services are pre-approved before being rendered, reducing claim rejections and improving cost control.

## Technology Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL 15+ with SQLAlchemy 2.0
- **Cache**: Redis for session and auth data
- **Queue**: Celery with Redis broker
- **API**: REST with optional GraphQL (Strawberry)
- **Testing**: pytest, pytest-asyncio
- **Validation**: Pydantic 2.0+

## Architecture

### Domain Model

```python
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum
import uuid

class AuthorizationStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class AuthorizationType(Enum):
    INPATIENT = "inpatient"
    OUTPATIENT_SURGERY = "outpatient_surgery"
    HIGH_COST_PROCEDURE = "high_cost_procedure"
    SPECIALIST_REFERRAL = "specialist_referral"
    DIAGNOSTIC_IMAGING = "diagnostic_imaging"

@dataclass
class AuthorizationItem:
    """Represents a specific service requiring authorization"""
    id: uuid.UUID
    service_code: str
    procedure_code: str
    quantity: int
    requested_amount: Decimal
    approved_amount: Optional[Decimal]
    notes: Optional[str]

@dataclass
class ClinicalData:
    """Clinical information supporting the authorization"""
    diagnosis_codes: List[str]
    symptoms: List[str]
    clinical_notes: str
    attachments: List[str]

@dataclass
class Authorization:
    """Main authorization entity"""
    id: uuid.UUID
    auth_number: str
    member_id: uuid.UUID
    provider_id: uuid.UUID
    requesting_physician_id: str
    authorization_type: AuthorizationType
    status: AuthorizationStatus
    items: List[AuthorizationItem]
    clinical_data: ClinicalData
    requested_date: datetime
    effective_date: datetime
    expiry_date: datetime
    approved_by: Optional[str]
    approved_date: Optional[datetime]
    denial_reason: Optional[str]
    total_requested: Decimal
    total_approved: Optional[Decimal]
```

### Service Structure

```
authorization/
├── src/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── authorization.py   # Authorization endpoints
│   │   │   ├── validation.py      # Validation endpoints
│   │   │   └── health.py          # Health checks
│   │   └── dependencies.py        # FastAPI dependencies
│   │
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── entities/
│   │   │   ├── __init__.py
│   │   │   └── authorization.py   # Authorization entity
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py    # Business logic
│   │   │   └── rules_engine.py    # Authorization rules
│   │   └── repositories/
│   │       ├── __init__.py
│   │       └── auth_repository.py # Data access
│   │
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── models.py          # SQLAlchemy models
│   │   │   └── postgres.py        # Database connection
│   │   ├── cache/
│   │   │   ├── __init__.py
│   │   │   └── redis_cache.py     # Redis caching
│   │   └── external/
│   │       ├── __init__.py
│   │       ├── member_client.py   # Member service client
│   │       └── benefit_client.py  # Benefit service client
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Configuration
│   │   ├── exceptions.py          # Custom exceptions
│   │   └── security.py            # Security utilities
│   │
│   └── workers/
│       ├── __init__.py
│       ├── celery_app.py          # Celery configuration
│       └── tasks.py               # Background tasks
│
├── migrations/                     # Alembic migrations
├── tests/
├── requirements.txt
└── .env.example
```

## API Documentation

### REST Endpoints

#### Submit Authorization Request

```python
POST /api/v1/authorizations
Content-Type: application/json

{
  "member_id": "uuid",
  "provider_id": "uuid",
  "authorization_type": "inpatient",
  "requesting_physician_id": "DR123",
  "items": [
    {
      "service_code": "99223",
      "procedure_code": "47562",
      "quantity": 1,
      "requested_amount": 5000000
    }
  ],
  "clinical_data": {
    "diagnosis_codes": ["K80.20"],
    "symptoms": ["abdominal pain", "nausea"],
    "clinical_notes": "Patient requires laparoscopic cholecystectomy"
  },
  "effective_date": "2024-01-20",
  "expiry_date": "2024-02-20"
}

Response: 201 Created
{
  "id": "uuid",
  "auth_number": "AUTH-2024-000001",
  "status": "pending",
  "created_at": "2024-01-15T10:00:00Z"
}
```

#### Check Authorization Status

```python
GET /api/v1/authorizations/{auth_id}

Response: 200 OK
{
  "id": "uuid",
  "auth_number": "AUTH-2024-000001",
  "status": "approved",
  "member_id": "uuid",
  "provider_id": "uuid",
  "total_requested": 5000000,
  "total_approved": 4500000,
  "approved_date": "2024-01-15T14:00:00Z",
  "approved_by": "REVIEWER001",
  "items": [...],
  "effective_date": "2024-01-20",
  "expiry_date": "2024-02-20"
}
```

#### Validate Authorization

```python
POST /api/v1/authorizations/validate
Content-Type: application/json

{
  "auth_number": "AUTH-2024-000001",
  "service_date": "2024-01-25",
  "service_codes": ["99223"]
}

Response: 200 OK
{
  "valid": true,
  "auth_number": "AUTH-2024-000001",
  "remaining_amount": 4500000,
  "expiry_date": "2024-02-20"
}
```

## Business Rules Engine

```python
# src/domain/services/rules_engine.py
from typing import Dict, List, Any
from decimal import Decimal
from src.domain.entities.authorization import Authorization, AuthorizationType

class AuthorizationRulesEngine:
    """
    Implements business rules for authorization decisions
    """
    
    def __init__(self, benefit_client, member_client):
        self.benefit_client = benefit_client
        self.member_client = member_client
        self.rules = self._load_rules()
    
    async def evaluate(self, authorization: Authorization) -> Dict[str, Any]:
        """Evaluate authorization request against business rules"""
        
        results = {
            "approved": True,
            "items": [],
            "total_approved": Decimal("0"),
            "messages": []
        }
        
        # Check member eligibility
        member = await self.member_client.get_member(authorization.member_id)
        if not member.is_active:
            results["approved"] = False
            results["messages"].append("Member is not active")
            return results
        
        # Check provider network status
        provider = await self._check_provider_network(authorization.provider_id)
        if not provider["in_network"]:
            results["messages"].append("Out-of-network provider - reduced benefits apply")
        
        # Evaluate each item
        for item in authorization.items:
            item_result = await self._evaluate_item(
                item,
                authorization.authorization_type,
                member,
                provider
            )
            results["items"].append(item_result)
            
            if item_result["approved"]:
                results["total_approved"] += item_result["approved_amount"]
            else:
                results["approved"] = False
        
        # Apply authorization type specific rules
        type_rules = await self._apply_type_rules(
            authorization.authorization_type,
            authorization,
            results
        )
        results.update(type_rules)
        
        return results
    
    async def _evaluate_item(self, item, auth_type, member, provider):
        """Evaluate individual authorization item"""
        
        # Get benefit coverage
        benefit = await self.benefit_client.get_benefit(
            member.plan_id,
            item.service_code
        )
        
        if not benefit:
            return {
                "approved": False,
                "reason": f"Service {item.service_code} not covered"
            }
        
        # Check limits
        if benefit.requires_auth and auth_type in benefit.auth_required_for:
            # Calculate approved amount based on benefit limits
            approved_amount = min(
                item.requested_amount,
                benefit.maximum_amount,
                benefit.allowed_amount
            )
            
            return {
                "approved": True,
                "approved_amount": approved_amount,
                "service_code": item.service_code
            }
        
        return {
            "approved": False,
            "reason": "Authorization not required for this service"
        }
    
    async def _apply_type_rules(self, auth_type, authorization, current_results):
        """Apply authorization type specific rules"""
        
        if auth_type == AuthorizationType.INPATIENT:
            # Inpatient specific rules
            if authorization.clinical_data.diagnosis_codes:
                # Validate diagnosis codes support inpatient admission
                valid_diagnosis = await self._validate_inpatient_diagnosis(
                    authorization.clinical_data.diagnosis_codes
                )
                if not valid_diagnosis:
                    return {
                        "approved": False,
                        "messages": ["Diagnosis does not support inpatient admission"]
                    }
            
            # Check length of stay
            los_limit = await self._get_los_limit(
                authorization.clinical_data.diagnosis_codes[0]
            )
            current_results["max_length_of_stay"] = los_limit
        
        elif auth_type == AuthorizationType.HIGH_COST_PROCEDURE:
            # High cost procedure rules
            if current_results["total_approved"] > Decimal("10000000"):
                # Require additional review
                current_results["requires_medical_director_review"] = True
        
        return current_results
```

## Configuration

```bash
# .env.example

# Service Configuration
SERVICE_NAME=authorization-service
ENVIRONMENT=production
PORT=8081

# Database
DATABASE_URL=postgresql://auth_user:password@postgres:5432/claims_askes
DB_POOL_SIZE=20

# Redis
REDIS_URL=redis://redis:6379/0
CACHE_TTL=3600

# Celery
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# External Services
MEMBER_SERVICE_URL=http://member-service:8082
BENEFIT_SERVICE_URL=http://benefit-service:8083
PROVIDER_SERVICE_URL=http://provider-service:8084

# Security
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256

# Business Rules
AUTO_APPROVAL_THRESHOLD=1000000
REQUIRE_CLINICAL_REVIEW_AMOUNT=5000000
AUTH_EXPIRY_DAYS=30
```

## Testing

```python
# tests/test_authorization_service.py
import pytest
from unittest.mock import AsyncMock
from src.domain.services.auth_service import AuthorizationService
from src.domain.entities.authorization import Authorization, AuthorizationType

@pytest.mark.asyncio
async def test_submit_authorization():
    # Arrange
    mock_repo = AsyncMock()
    mock_rules_engine = AsyncMock()
    mock_rules_engine.evaluate.return_value = {
        "approved": True,
        "total_approved": 4500000
    }
    
    service = AuthorizationService(mock_repo, mock_rules_engine)
    
    auth_request = {
        "member_id": "member-123",
        "provider_id": "provider-456",
        "authorization_type": AuthorizationType.INPATIENT,
        "items": [{"service_code": "99223", "requested_amount": 5000000}]
    }
    
    # Act
    result = await service.submit_authorization(auth_request)
    
    # Assert
    assert result["status"] == "approved"
    assert result["total_approved"] == 4500000
    mock_rules_engine.evaluate.assert_called_once()

@pytest.mark.asyncio
async def test_validate_authorization():
    # Test authorization validation logic
    service = AuthorizationService(AsyncMock(), AsyncMock())
    
    result = await service.validate_authorization(
        auth_number="AUTH-2024-000001",
        service_date="2024-01-25",
        service_codes=["99223"]
    )
    
    assert "valid" in result
```

## Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run as non-root
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8081

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8081"]
```

## Monitoring

### Key Metrics
- `authorization_requests_total` - Total authorization requests
- `authorization_approval_rate` - Percentage of approved authorizations
- `authorization_processing_time` - Time to process authorization
- `auto_approval_rate` - Percentage of auto-approved requests

### Health Checks
- **Liveness**: `/health/live`
- **Readiness**: `/health/ready`

## Support

- **Documentation**: [API Docs](http://localhost:8081/docs)
- **Team**: Authorization Team
- **On-call**: Use PagerDuty

---

*Authorization Service - Part of Claims Processing Platform*