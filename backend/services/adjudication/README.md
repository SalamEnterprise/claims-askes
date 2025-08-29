# Adjudication Service

## Overview

The Adjudication Service is responsible for evaluating claims against benefit plans, calculating allowed amounts, applying deductibles, copayments, coinsurance, and determining the final payment amounts. It implements complex benefit rules and ensures accurate claim processing according to policy terms.

## Technology Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL 15+ with SQLAlchemy 2.0
- **Cache**: Redis for benefit plan caching
- **Queue**: Celery with Redis broker
- **Rules Engine**: Python-based rules engine with Pydantic validation
- **Testing**: pytest, pytest-asyncio, hypothesis

## Architecture

### Domain Model

```python
from dataclasses import dataclass
from typing import List, Optional, Dict
from datetime import datetime
from decimal import Decimal
from enum import Enum
import uuid

class AdjudicationStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_REVIEW = "requires_review"

class BenefitType(Enum):
    INPATIENT = "inpatient"
    OUTPATIENT = "outpatient"
    DENTAL = "dental"
    OPTICAL = "optical"
    PHARMACY = "pharmacy"
    MATERNITY = "maternity"

@dataclass
class BenefitLimit:
    """Represents benefit limits and accumulations"""
    limit_type: str  # annual, per_incident, per_day
    limit_amount: Decimal
    used_amount: Decimal
    remaining_amount: Decimal
    reset_date: datetime

@dataclass
class CostSharing:
    """Cost sharing components"""
    deductible: Decimal
    deductible_met: Decimal
    copayment: Decimal
    coinsurance_percentage: Decimal
    out_of_pocket_max: Decimal
    out_of_pocket_met: Decimal

@dataclass
class AdjudicationLineItem:
    """Individual claim line adjudication result"""
    line_number: int
    service_code: str
    benefit_code: str
    charged_amount: Decimal
    allowed_amount: Decimal
    deductible_amount: Decimal
    copay_amount: Decimal
    coinsurance_amount: Decimal
    paid_amount: Decimal
    member_responsibility: Decimal
    denial_reason: Optional[str]
    remark_codes: List[str]

@dataclass
class AdjudicationResult:
    """Complete adjudication result for a claim"""
    id: uuid.UUID
    claim_id: uuid.UUID
    adjudication_date: datetime
    status: AdjudicationStatus
    total_charged: Decimal
    total_allowed: Decimal
    total_deductible: Decimal
    total_copay: Decimal
    total_coinsurance: Decimal
    total_paid: Decimal
    total_member_responsibility: Decimal
    line_items: List[AdjudicationLineItem]
    cost_sharing: CostSharing
    benefit_limits: List[BenefitLimit]
    coordination_of_benefits: Optional[Dict]
    notes: List[str]
```

### Service Structure

```
adjudication/
├── src/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── adjudication.py    # Adjudication endpoints
│   │   │   ├── benefits.py        # Benefit inquiry endpoints
│   │   │   └── health.py          # Health checks
│   │   └── dependencies.py        # FastAPI dependencies
│   │
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── entities/
│   │   │   ├── __init__.py
│   │   │   ├── adjudication.py    # Adjudication entities
│   │   │   └── benefit_plan.py    # Benefit plan entities
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── adjudication_service.py
│   │   │   ├── benefit_calculator.py
│   │   │   └── accumulator_service.py
│   │   └── rules/
│   │       ├── __init__.py
│   │       ├── rule_engine.py     # Main rules engine
│   │       ├── benefit_rules.py   # Benefit-specific rules
│   │       └── cob_rules.py       # COB/TPL rules
│   │
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── models.py          # SQLAlchemy models
│   │   │   └── postgres.py        # Database connection
│   │   ├── cache/
│   │   │   ├── __init__.py
│   │   │   └── redis_cache.py     # Benefit plan caching
│   │   └── external/
│   │       ├── __init__.py
│   │       ├── member_client.py   # Member service client
│   │       ├── provider_client.py # Provider service client
│   │       └── policy_client.py   # Policy service client
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Configuration
│   │   ├── exceptions.py          # Custom exceptions
│   │   └── constants.py           # Business constants
│   │
│   └── workers/
│       ├── __init__.py
│       ├── celery_app.py          # Celery configuration
│       └── tasks.py               # Async adjudication tasks
│
├── migrations/                     # Alembic migrations
├── tests/
├── requirements.txt
└── .env.example
```

## Core Features

### Benefit Calculation Engine

```python
# src/domain/services/benefit_calculator.py
from decimal import Decimal
from typing import Dict, List
from src.domain.entities.adjudication import AdjudicationLineItem, CostSharing

class BenefitCalculator:
    """
    Calculates benefit payments according to plan rules
    """
    
    def __init__(self, benefit_plan, accumulator_service):
        self.benefit_plan = benefit_plan
        self.accumulator_service = accumulator_service
    
    async def calculate_allowed_amount(
        self,
        service_code: str,
        charged_amount: Decimal,
        provider_type: str
    ) -> Decimal:
        """Calculate allowed amount based on fee schedule"""
        
        # Get fee schedule for service
        fee_schedule = await self._get_fee_schedule(
            service_code,
            provider_type
        )
        
        if fee_schedule:
            # Use the lesser of charged or scheduled amount
            return min(charged_amount, fee_schedule.allowed_amount)
        
        # Default to percentage of charged if no schedule
        return charged_amount * Decimal("0.8")
    
    async def apply_cost_sharing(
        self,
        member_id: str,
        allowed_amount: Decimal,
        benefit_code: str,
        service_date: datetime
    ) -> Dict:
        """Apply deductibles, copays, and coinsurance"""
        
        # Get current accumulations
        accumulators = await self.accumulator_service.get_accumulators(
            member_id,
            service_date.year
        )
        
        result = {
            "allowed_amount": allowed_amount,
            "deductible_amount": Decimal("0"),
            "copay_amount": Decimal("0"),
            "coinsurance_amount": Decimal("0"),
            "paid_amount": Decimal("0"),
            "member_responsibility": Decimal("0")
        }
        
        # Step 1: Apply deductible
        if accumulators.deductible_remaining > 0:
            deductible_applied = min(
                allowed_amount,
                accumulators.deductible_remaining
            )
            result["deductible_amount"] = deductible_applied
            allowed_amount -= deductible_applied
            
            # Update accumulator
            await self.accumulator_service.update_deductible(
                member_id,
                deductible_applied
            )
        
        # Step 2: Apply copayment
        benefit = self.benefit_plan.get_benefit(benefit_code)
        if benefit.copay_amount:
            result["copay_amount"] = benefit.copay_amount
            allowed_amount -= benefit.copay_amount
        
        # Step 3: Apply coinsurance
        if benefit.coinsurance_percentage:
            coinsurance = allowed_amount * (
                benefit.coinsurance_percentage / Decimal("100")
            )
            result["coinsurance_amount"] = coinsurance
            result["paid_amount"] = allowed_amount - coinsurance
        else:
            result["paid_amount"] = allowed_amount
        
        # Calculate member responsibility
        result["member_responsibility"] = (
            result["deductible_amount"] +
            result["copay_amount"] +
            result["coinsurance_amount"]
        )
        
        # Check out-of-pocket maximum
        if accumulators.oop_met + result["member_responsibility"] > accumulators.oop_max:
            # Adjust member responsibility to not exceed OOP max
            max_responsibility = accumulators.oop_max - accumulators.oop_met
            reduction = result["member_responsibility"] - max_responsibility
            result["member_responsibility"] = max_responsibility
            result["paid_amount"] += reduction
        
        return result
```

### Adjudication Rules Engine

```python
# src/domain/rules/rule_engine.py
from typing import List, Dict, Any
from abc import ABC, abstractmethod
from src.domain.entities.adjudication import AdjudicationResult

class Rule(ABC):
    """Base class for adjudication rules"""
    
    @abstractmethod
    async def evaluate(self, context: Dict[str, Any]) -> bool:
        pass
    
    @abstractmethod
    async def apply(self, context: Dict[str, Any]) -> Dict[str, Any]:
        pass

class MedicalNecessityRule(Rule):
    """Check medical necessity for services"""
    
    async def evaluate(self, context: Dict[str, Any]) -> bool:
        diagnosis_codes = context.get("diagnosis_codes", [])
        service_code = context.get("service_code")
        
        # Check if diagnosis supports the service
        return await self._is_medically_necessary(
            diagnosis_codes,
            service_code
        )
    
    async def apply(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if not await self.evaluate(context):
            context["denial_reason"] = "Not medically necessary"
            context["paid_amount"] = Decimal("0")
        return context

class DuplicateClaimRule(Rule):
    """Check for duplicate claims"""
    
    async def evaluate(self, context: Dict[str, Any]) -> bool:
        # Check if similar claim was already processed
        existing_claims = await self._find_similar_claims(
            context["member_id"],
            context["service_date"],
            context["service_code"]
        )
        return len(existing_claims) == 0
    
    async def apply(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if not await self.evaluate(context):
            context["denial_reason"] = "Duplicate claim"
            context["paid_amount"] = Decimal("0")
        return context

class RuleEngine:
    """Main rules engine for adjudication"""
    
    def __init__(self):
        self.rules = [
            MedicalNecessityRule(),
            DuplicateClaimRule(),
            # Add more rules as needed
        ]
    
    async def process(self, claim_data: Dict[str, Any]) -> AdjudicationResult:
        """Process claim through all rules"""
        
        context = {
            "claim_id": claim_data["claim_id"],
            "member_id": claim_data["member_id"],
            "service_date": claim_data["service_date"],
            "line_items": []
        }
        
        # Process each line item
        for item in claim_data["items"]:
            item_context = {
                **context,
                "service_code": item["service_code"],
                "charged_amount": item["charged_amount"],
                "diagnosis_codes": claim_data.get("diagnosis_codes", [])
            }
            
            # Apply all rules
            for rule in self.rules:
                item_context = await rule.apply(item_context)
            
            context["line_items"].append(item_context)
        
        return self._build_result(context)
```

## API Documentation

### Adjudicate Claim

```python
POST /api/v1/adjudicate
Content-Type: application/json

{
  "claim_id": "uuid",
  "member_id": "uuid",
  "provider_id": "uuid",
  "service_date": "2024-01-15",
  "diagnosis_codes": ["J06.9", "R50.9"],
  "items": [
    {
      "line_number": 1,
      "service_code": "99213",
      "charged_amount": 150000,
      "units": 1
    }
  ]
}

Response: 200 OK
{
  "adjudication_id": "uuid",
  "claim_id": "uuid",
  "status": "completed",
  "total_charged": 150000,
  "total_allowed": 120000,
  "total_deductible": 0,
  "total_copay": 25000,
  "total_coinsurance": 19000,
  "total_paid": 76000,
  "total_member_responsibility": 44000,
  "line_items": [
    {
      "line_number": 1,
      "service_code": "99213",
      "charged_amount": 150000,
      "allowed_amount": 120000,
      "paid_amount": 76000,
      "member_responsibility": 44000
    }
  ]
}
```

### Check Benefit Eligibility

```python
GET /api/v1/benefits/eligibility?member_id={uuid}&service_code={code}&service_date={date}

Response: 200 OK
{
  "eligible": true,
  "benefit_details": {
    "benefit_code": "CONS-GP",
    "covered": true,
    "requires_authorization": false,
    "copay": 25000,
    "coinsurance": 20,
    "annual_limit": 10000000,
    "annual_used": 2500000,
    "annual_remaining": 7500000
  }
}
```

## Configuration

```bash
# .env.example

# Service Configuration
SERVICE_NAME=adjudication-service
ENVIRONMENT=production
PORT=8082

# Database
DATABASE_URL=postgresql://adjudication_user:password@postgres:5432/claims_askes
DB_POOL_SIZE=20

# Redis
REDIS_URL=redis://redis:6379/0
CACHE_TTL=3600

# Celery
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# External Services
MEMBER_SERVICE_URL=http://member-service:8083
PROVIDER_SERVICE_URL=http://provider-service:8084
POLICY_SERVICE_URL=http://policy-service:8085
ACCUMULATOR_SERVICE_URL=http://accumulator-service:8086

# Business Rules
DEFAULT_COINSURANCE=20
DEFAULT_COPAY=25000
ANNUAL_DEDUCTIBLE=500000
ANNUAL_OOP_MAX=10000000

# Fee Schedule
USE_FEE_SCHEDULE=true
FEE_SCHEDULE_VERSION=2024.1
```

## Testing

```python
# tests/test_benefit_calculator.py
import pytest
from decimal import Decimal
from src.domain.services.benefit_calculator import BenefitCalculator

@pytest.mark.asyncio
async def test_calculate_allowed_amount():
    # Arrange
    calculator = BenefitCalculator(mock_benefit_plan, mock_accumulator)
    
    # Act
    allowed = await calculator.calculate_allowed_amount(
        service_code="99213",
        charged_amount=Decimal("150000"),
        provider_type="in_network"
    )
    
    # Assert
    assert allowed == Decimal("120000")

@pytest.mark.asyncio
async def test_apply_cost_sharing():
    # Test cost sharing calculation
    calculator = BenefitCalculator(mock_benefit_plan, mock_accumulator)
    
    result = await calculator.apply_cost_sharing(
        member_id="member-123",
        allowed_amount=Decimal("120000"),
        benefit_code="CONS-GP",
        service_date=datetime(2024, 1, 15)
    )
    
    assert result["copay_amount"] == Decimal("25000")
    assert result["coinsurance_amount"] == Decimal("19000")
    assert result["paid_amount"] == Decimal("76000")
    assert result["member_responsibility"] == Decimal("44000")
```

## Performance Optimization

### Caching Strategy

```python
# src/infrastructure/cache/redis_cache.py
import redis.asyncio as redis
import json
from typing import Optional, Any

class BenefitPlanCache:
    """Cache benefit plans for fast lookup"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.ttl = 3600  # 1 hour
    
    async def get_benefit_plan(self, plan_id: str) -> Optional[Dict]:
        """Get cached benefit plan"""
        key = f"benefit_plan:{plan_id}"
        cached = await self.redis.get(key)
        
        if cached:
            return json.loads(cached)
        return None
    
    async def set_benefit_plan(self, plan_id: str, plan_data: Dict):
        """Cache benefit plan"""
        key = f"benefit_plan:{plan_id}"
        await self.redis.setex(
            key,
            self.ttl,
            json.dumps(plan_data)
        )
    
    async def get_fee_schedule(
        self,
        service_code: str,
        provider_type: str
    ) -> Optional[Decimal]:
        """Get cached fee schedule amount"""
        key = f"fee_schedule:{provider_type}:{service_code}"
        cached = await self.redis.get(key)
        
        if cached:
            return Decimal(cached)
        return None
```

## Monitoring

### Key Metrics
- `adjudication_requests_total` - Total adjudication requests
- `adjudication_processing_time` - Processing time histogram
- `adjudication_approval_rate` - Percentage of approved items
- `average_payment_percentage` - Average paid vs charged percentage
- `cost_sharing_amounts` - Distribution of member responsibility

### Health Checks
- **Liveness**: `/health/live`
- **Readiness**: `/health/ready`
- **Dependencies**: `/health/dependencies`

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

EXPOSE 8082

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8082"]
```

## Support

- **Documentation**: [API Docs](http://localhost:8082/docs)
- **Team**: Adjudication Team
- **On-call**: Use PagerDuty for critical issues

---

*Adjudication Service - Core component of Claims Processing Platform*