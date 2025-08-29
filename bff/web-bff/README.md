# Web BFF (Backend for Frontend)

## Overview

The Web BFF is a specialized backend service that aggregates and optimizes API calls for web applications (Member Portal, Provider Portal, Admin Console). It acts as an intermediary layer between the web frontends and microservices, reducing the number of API calls and tailoring responses for web-specific needs.

## Purpose

### Why BFF?
- **API Aggregation**: Combines multiple microservice calls into single endpoints
- **Response Optimization**: Tailors data format for web consumption
- **Reduced Latency**: Minimizes round trips between client and server
- **Business Logic**: Implements presentation-layer business logic
- **Security**: Additional security layer between frontend and microservices
- **Caching**: Intelligent caching for frequently accessed data

## Technology Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI 0.104+ with Strawberry GraphQL
- **GraphQL**: Strawberry (Python GraphQL library)
- **REST**: FastAPI for RESTful endpoints
- **Async HTTP**: httpx for service-to-service calls
- **Caching**: Redis with redis-py
- **Authentication**: python-jose for JWT
- **Task Queue**: Celery for background tasks
- **Testing**: pytest + pytest-asyncio
- **Documentation**: GraphQL Playground + OpenAPI/Swagger

## Architecture

```
Web Clients
    ↓
[Web BFF]
    ↓
┌───────────────────────────────────────────────────────────┐
│ Claims  │ Member  │ Provider │ Benefit │ Policy  │
│ Service │ Service │ Service  │ Service │ Service │
└───────────────────────────────────────────────────────────┘
```

## Getting Started

### Prerequisites

- Node.js 18+
- Redis 7+
- Access to microservices

### Installation

1. **Navigate to project**
```bash
cd bff/web-bff
```

2. **Create virtual environment**
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

5. **Start development server**
```bash
# Development
uvicorn src.main:app --reload --port 4000

# Production
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:4000
```

The BFF will be available at:
- GraphQL: `http://localhost:4000/graphql`
- REST: `http://localhost:4000/api/v1`
- GraphQL Playground: `http://localhost:4000/graphql`
- Swagger: `http://localhost:4000/api-docs`

### Environment Variables

```bash
# Server Configuration
PORT=4000
NODE_ENV=development

# Microservices URLs
CLAIMS_SERVICE_URL=http://localhost:8001
MEMBER_SERVICE_URL=http://localhost:8002
PROVIDER_SERVICE_URL=http://localhost:8003
BENEFIT_SERVICE_URL=http://localhost:8004
POLICY_SERVICE_URL=http://localhost:8005

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Security
JWT_SECRET=your-secret-key
JWT_EXPIRATION=1h
REFRESH_TOKEN_SECRET=your-refresh-secret
REFRESH_TOKEN_EXPIRATION=7d

# Rate Limiting
RATE_LIMIT_WINDOW=15m
RATE_LIMIT_MAX=100

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
```

## Project Structure

```
web-bff/
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── api/
│   │   ├── __init__.py
│   │   ├── rest/               # REST endpoints
│   │   │   ├── claims.py
│   │   │   ├── members.py
│   │   │   └── dashboard.py
│   │   └── graphql/            # GraphQL endpoints
│   │       ├── schema.py       # GraphQL schema
│   │       ├── queries.py      # Query resolvers
│   │       └── mutations.py    # Mutation resolvers
│   ├── services/
│   │   ├── __init__.py
│   │   ├── aggregator.py       # Data aggregation
│   │   ├── cache_service.py    # Redis caching
│   │   ├── circuit_breaker.py  # Circuit breaker
│   │   └── service_client.py   # HTTP client for microservices
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration
│   │   ├── security.py         # JWT handling
│   │   └── exceptions.py       # Custom exceptions
│   ├── models/
│   │   ├── __init__.py
│   │   └── responses.py        # Response models
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py             # Authentication
│   │   ├── cors.py             # CORS handling
│   │   └── rate_limit.py       # Rate limiting
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── tests/                      # Test files
├── requirements.txt
├── pyproject.toml
└── Dockerfile
```

## API Patterns

### GraphQL Schema (using Strawberry)

```python
# src/api/graphql/schema.py
import strawberry
from typing import List, Optional
from datetime import datetime

@strawberry.type
class MemberDashboard:
    member_id: str
    name: str
    plan_name: str
    recent_claims: List["Claim"]
    benefits_summary: "BenefitsSummary"
    notifications: List["Notification"]

@strawberry.type
class Claim:
    id: str
    claim_number: str
    status: str
    service_date: datetime
    total_amount: float
    provider_name: str

@strawberry.type
class Query:
    @strawberry.field
    async def member_dashboard(self, member_id: str) -> MemberDashboard:
        """Get aggregated member dashboard data"""
        # Implementation here
        pass
    
    @strawberry.field
    async def member_claims(
        self, 
        member_id: str, 
        status: Optional[str] = None,
        limit: int = 10
    ) -> List[Claim]:
        """Get member claims with filtering"""
        # Implementation here
        pass
    
    @strawberry.field
    async def eligibility_check(
        self,
        member_id: str,
        provider_id: str,
        service_date: datetime
    ) -> "EligibilityResponse":
        """Check member eligibility"""
        # Implementation here
        pass

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def submit_claim(self, claim_input: "ClaimInput") -> "ClaimResponse":
        """Submit a new claim"""
        # Implementation here
        pass
    
    @strawberry.mutation
    async def login(self, email: str, password: str) -> "AuthResponse":
        """User login"""
        # Implementation here
        pass

schema = strawberry.Schema(query=Query, mutation=Mutation)
```

### Aggregation Examples

#### Member Dashboard Aggregation

```python
# src/api/graphql/queries.py
from typing import Dict, Any
import asyncio
import httpx
from src.services.cache_service import CacheService
from src.services.service_client import ServiceClient
from src.core.config import settings

class MemberDashboardResolver:
    def __init__(self):
        self.cache = CacheService()
        self.service_client = ServiceClient()
    
    async def resolve_member_dashboard(self, member_id: str) -> Dict[str, Any]:
        """Aggregate member dashboard data from multiple services"""
        
        # Check cache first
        cache_key = f"dashboard:{member_id}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        # Parallel service calls using asyncio.gather
        async with httpx.AsyncClient() as client:
            member_task = self.service_client.get_member(client, member_id)
            claims_task = self.service_client.get_recent_claims(client, member_id, limit=5)
            benefits_task = self.service_client.get_member_benefits(client, member_id)
            coverage_task = self.service_client.get_coverage_status(client, member_id)
            
            # Execute all tasks concurrently
            member, claims, benefits, coverage = await asyncio.gather(
                member_task,
                claims_task,
                benefits_task,
                coverage_task,
                return_exceptions=True
            )
        
        # Handle any failed requests
        if isinstance(member, Exception):
            member = self._get_fallback_member_data(member_id)
        
        # Transform and aggregate data
        dashboard = {
            "member": {
                "id": member.get("id"),
                "name": f"{member.get('first_name')} {member.get('last_name')}",
                "plan_name": member.get("plan", {}).get("name"),
                "member_since": member.get("enrollment_date")
            },
            "recent_claims": self._transform_claims(claims),
            "benefits_summary": self._summarize_benefits(benefits),
            "coverage_status": coverage,
            "notifications": await self._get_notifications(member_id)
        }
        
        # Cache the result
        await self.cache.set(cache_key, dashboard, ttl=300)  # 5 minutes
        
        return dashboard
    
    def _transform_claims(self, claims: list) -> list:
        """Transform claim data for frontend consumption"""
        return [
            {
                "id": claim["id"],
                "claim_number": claim["claim_number"],
                "status": claim["status"],
                "status_color": self._get_status_color(claim["status"]),
                "amount": claim["total_amount"],
                "formatted_amount": f"Rp {claim['total_amount']:,.0f}",
                "service_date": claim["service_date"],
                "provider_name": claim.get("provider", {}).get("name")
            }
            for claim in claims[:5]
        ]
    
    def _get_status_color(self, status: str) -> str:
        """Map status to UI color"""
        status_colors = {
            "submitted": "blue",
            "processing": "orange",
            "approved": "green",
            "rejected": "red",
            "paid": "green"
        }
        return status_colors.get(status, "gray")
```

#### Claims Submission Aggregation

```python
# src/services/aggregator.py
from typing import Dict, Any
import asyncio
from fastapi import HTTPException
from src.services.service_client import ServiceClient
from src.services.cache_service import CacheService

class ClaimsAggregatorService:
    def __init__(self):
        self.service_client = ServiceClient()
        self.cache = CacheService()
    
    async def submit_claim(self, claim_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Aggregate claim submission across multiple services"""
        
        async with httpx.AsyncClient() as client:
            # Step 1: Validate member eligibility
            eligibility = await self.service_client.check_eligibility(
                client,
                member_id=claim_data["member_id"],
                service_date=claim_data["service_date"],
                provider_id=claim_data["provider_id"]
            )
            
            if not eligibility["is_eligible"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Member not eligible: {eligibility['reason']}"
                )
            
            # Step 2: Validate provider
            provider = await self.service_client.validate_provider(
                client,
                provider_id=claim_data["provider_id"]
            )
            
            if not provider["is_active"]:
                raise HTTPException(
                    status_code=400,
                    detail="Provider is not active"
                )
            
            # Step 3: Check benefits in parallel
            benefit_tasks = [
                self.service_client.validate_benefit(client, item)
                for item in claim_data["items"]
            ]
            benefit_validations = await asyncio.gather(*benefit_tasks)
            
            # Step 4: Submit claim to claims service
            claim = await self.service_client.submit_claim(
                client,
                {
                    **claim_data,
                    "eligibility": eligibility,
                    "benefit_validations": benefit_validations,
                    "submitted_by": user_id
                }
            )
            
            # Step 5: Send notifications (async, don't wait)
            asyncio.create_task(
                self._send_claim_notification(claim["id"], user_id)
            )
            
            # Invalidate relevant caches
            await self.cache.delete(f"dashboard:{claim_data['member_id']}")
            await self.cache.delete(f"claims:member:{claim_data['member_id']}")
            
            return claim
    
    async def _send_claim_notification(self, claim_id: str, user_id: str):
        """Send claim submission notification"""
        try:
            async with httpx.AsyncClient() as client:
                await self.service_client.send_notification(
                    client,
                    {
                        "type": "claim_submitted",
                        "claim_id": claim_id,
                        "user_id": user_id,
                        "channel": ["email", "push"]
                    }
                )
        except Exception as e:
            # Log error but don't fail the claim submission
            print(f"Failed to send notification: {e}")
```

### REST Endpoints

```python
# src/api/rest/claims.py
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from datetime import datetime
from src.services.aggregator import ClaimsAggregatorService
from src.middleware.auth import get_current_user
from src.models.responses import ClaimResponse, ClaimListResponse

router = APIRouter(prefix="/api/v1")
aggregator = ClaimsAggregatorService()

@router.get("/claims/{member_id}", response_model=ClaimListResponse)
async def get_member_claims(
    member_id: str,
    status: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
    current_user = Depends(get_current_user)
):
    """Get member claims with pagination and filtering"""
    
    # Verify user has access to this member's data
    if current_user["id"] != member_id and "admin" not in current_user["roles"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    claims = await aggregator.get_member_claims(
        member_id=member_id,
        status=status,
        limit=limit,
        offset=offset
    )
    
    return claims

@router.post("/claims", response_model=ClaimResponse)
async def submit_claim(
    claim_data: dict,
    current_user = Depends(get_current_user)
):
    """Submit a new claim"""
    
    result = await aggregator.submit_claim(
        claim_data=claim_data,
        user_id=current_user["id"]
    )
    
    return result

@router.get("/dashboard/{member_id}")
async def get_member_dashboard(
    member_id: str,
    current_user = Depends(get_current_user)
):
    """Get aggregated dashboard data"""
    
    # Verify access
    if current_user["id"] != member_id and "admin" not in current_user["roles"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    dashboard = await aggregator.get_dashboard_data(member_id)
    return dashboard
```

## Data Transformation

### Response Optimization

```typescript
class DataTransformer {
  // Transform for web consumption
  transformClaimForWeb(claim: RawClaim): WebClaim {
    return {
      id: claim.id,
      displayNumber: `CLM-${claim.claim_number}`,
      status: this.mapStatus(claim.status),
      statusColor: this.getStatusColor(claim.status),
      amount: this.formatCurrency(claim.total_amount),
      provider: {
        name: claim.provider_name,
        location: claim.provider_location
      },
      timeline: this.buildTimeline(claim.history),
      actions: this.getAvailableActions(claim)
    };
  }
  
  // Aggregate multiple sources
  aggregateMemberData(sources: DataSources): MemberProfile {
    return {
      personal: sources.memberService,
      claims: this.summarizeClaims(sources.claimsService),
      benefits: this.organizeBenefits(sources.benefitService),
      payments: sources.paymentService,
      documents: sources.documentService
    };
  }
}
```

## Caching Strategy

### Redis Caching Implementation

```python
# src/services/cache_service.py
import json
import redis.asyncio as redis
from typing import Optional, Any, Callable
from src.core.config import settings

class CacheService:
    def __init__(self):
        self.redis = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        data = await self.redis.get(key)
        return json.loads(data) if data else None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set value in cache with TTL"""
        await self.redis.setex(
            key,
            ttl,
            json.dumps(value, default=str)
        )
    
    async def delete(self, key: str) -> None:
        """Delete key from cache"""
        await self.redis.delete(key)
    
    async def invalidate_pattern(self, pattern: str) -> None:
        """Invalidate all keys matching pattern"""
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(
                cursor,
                match=pattern,
                count=100
            )
            if keys:
                await self.redis.delete(*keys)
            if cursor == 0:
                break
    
    async def get_or_set(
        self,
        key: str,
        factory: Callable,
        ttl: int = 3600
    ) -> Any:
        """Cache-aside pattern implementation"""
        # Try to get from cache
        data = await self.get(key)
        
        if data is None:
            # Not in cache, call factory function
            data = await factory()
            # Store in cache
            await self.set(key, data, ttl)
        
        return data
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter in cache"""
        return await self.redis.incrby(key, amount)
    
    async def expire(self, key: str, ttl: int) -> None:
        """Set expiration on existing key"""
        await self.redis.expire(key, ttl)
```

### Cache Invalidation

```typescript
@Injectable()
export class CacheInvalidator {
  constructor(
    private cacheService: CacheService,
    private eventEmitter: EventEmitter2
  ) {
    this.setupEventListeners();
  }
  
  private setupEventListeners() {
    // Invalidate on claim status change
    this.eventEmitter.on('claim.status.changed', async (event) => {
      await this.cacheService.invalidate(`claim:${event.claimId}:*`);
      await this.cacheService.invalidate(`dashboard:${event.memberId}:*`);
    });
    
    // Invalidate on member update
    this.eventEmitter.on('member.updated', async (event) => {
      await this.cacheService.invalidate(`member:${event.memberId}:*`);
    });
  }
}
```

## Error Handling

### Circuit Breaker Pattern

```python
# src/services/circuit_breaker.py
import asyncio
from typing import Optional, Callable, Any, Dict
from datetime import datetime, timedelta
from enum import Enum
from fastapi import HTTPException

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED
    
    async def call(
        self,
        func: Callable,
        *args,
        fallback: Optional[Callable] = None,
        **kwargs
    ) -> Any:
        """Execute function with circuit breaker protection"""
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                if fallback:
                    return await fallback()
                raise HTTPException(
                    status_code=503,
                    detail="Service temporarily unavailable"
                )
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            if fallback:
                return await fallback()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        return (
            self.last_failure_time and
            datetime.now() >= self.last_failure_time + timedelta(seconds=self.recovery_timeout)
        )
    
    def _on_success(self):
        """Reset failure count on successful call"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Increment failure count and possibly open circuit"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

class CircuitBreakerManager:
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
    
    def get_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for service"""
        if service_name not in self.breakers:
            self.breakers[service_name] = CircuitBreaker()
        return self.breakers[service_name]
    
    async def call_service(
        self,
        service_name: str,
        operation: Callable,
        fallback: Optional[Callable] = None
    ) -> Any:
        """Call service with circuit breaker protection"""
        breaker = self.get_breaker(service_name)
        return await breaker.call(operation, fallback=fallback)

# Global circuit breaker manager
circuit_breaker_manager = CircuitBreakerManager()
```

## Security

### Authentication & Authorization

```typescript
@Injectable()
export class AuthService {
  async validateToken(token: string): Promise<TokenPayload> {
    try {
      const payload = jwt.verify(token, process.env.JWT_SECRET);
      
      // Additional validation
      const user = await this.userService.findById(payload.userId);
      if (!user || !user.isActive) {
        throw new UnauthorizedException('Invalid user');
      }
      
      return payload;
    } catch (error) {
      throw new UnauthorizedException('Invalid token');
    }
  }
  
  async refreshToken(refreshToken: string): Promise<AuthTokens> {
    const payload = jwt.verify(
      refreshToken,
      process.env.REFRESH_TOKEN_SECRET
    );
    
    const newAccessToken = this.generateAccessToken(payload.userId);
    const newRefreshToken = this.generateRefreshToken(payload.userId);
    
    return {
      accessToken: newAccessToken,
      refreshToken: newRefreshToken
    };
  }
}
```

### Rate Limiting

```typescript
@Injectable()
export class RateLimitGuard implements CanActivate {
  constructor(private rateLimiter: RateLimiterRedis) {}
  
  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest();
    const key = `${request.ip}:${request.user?.id || 'anonymous'}`;
    
    try {
      await this.rateLimiter.consume(key);
      return true;
    } catch (rejRes) {
      throw new TooManyRequestsException(
        'Too many requests, please try again later'
      );
    }
  }
}
```

## Testing

### Unit Testing

```python
# tests/test_aggregator.py
import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.services.aggregator import ClaimsAggregatorService
from fastapi import HTTPException

@pytest.fixture
def aggregator_service():
    return ClaimsAggregatorService()

@pytest.fixture
def mock_service_client():
    with patch('src.services.aggregator.ServiceClient') as mock:
        client = mock.return_value
        client.check_eligibility = AsyncMock()
        client.validate_provider = AsyncMock()
        client.validate_benefit = AsyncMock()
        client.submit_claim = AsyncMock()
        yield client

@pytest.mark.asyncio
class TestClaimsAggregator:
    async def test_submit_claim_success(
        self, 
        aggregator_service, 
        mock_service_client
    ):
        # Arrange
        mock_service_client.check_eligibility.return_value = {
            "is_eligible": True,
            "coverage": "full"
        }
        mock_service_client.validate_provider.return_value = {
            "is_active": True,
            "name": "Test Hospital"
        }
        mock_service_client.validate_benefit.return_value = {
            "is_covered": True,
            "coverage_amount": 1000000
        }
        mock_service_client.submit_claim.return_value = {
            "id": "claim-123",
            "status": "submitted"
        }
        
        claim_data = {
            "member_id": "member-123",
            "provider_id": "provider-456",
            "service_date": "2024-01-15",
            "items": [{"benefit_code": "CONS-GP", "amount": 500000}]
        }
        
        # Act
        result = await aggregator_service.submit_claim(
            claim_data, 
            "user-123"
        )
        
        # Assert
        assert result["id"] == "claim-123"
        assert result["status"] == "submitted"
        mock_service_client.check_eligibility.assert_called_once()
        mock_service_client.submit_claim.assert_called_once()
    
    async def test_submit_claim_ineligible_member(
        self,
        aggregator_service,
        mock_service_client
    ):
        # Arrange
        mock_service_client.check_eligibility.return_value = {
            "is_eligible": False,
            "reason": "Coverage expired"
        }
        
        claim_data = {
            "member_id": "member-123",
            "provider_id": "provider-456",
            "service_date": "2024-01-15",
            "items": []
        }
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await aggregator_service.submit_claim(claim_data, "user-123")
        
        assert exc_info.value.status_code == 400
        assert "not eligible" in str(exc_info.value.detail)
    
    async def test_cache_invalidation_on_claim_submission(
        self,
        aggregator_service,
        mock_service_client
    ):
        # Arrange
        mock_cache = AsyncMock()
        aggregator_service.cache = mock_cache
        
        mock_service_client.check_eligibility.return_value = {
            "is_eligible": True
        }
        mock_service_client.validate_provider.return_value = {
            "is_active": True
        }
        mock_service_client.submit_claim.return_value = {
            "id": "claim-123"
        }
        
        # Act
        await aggregator_service.submit_claim(
            {"member_id": "member-123", "items": []},
            "user-123"
        )
        
        # Assert
        mock_cache.delete.assert_any_call("dashboard:member-123")
        mock_cache.delete.assert_any_call("claims:member:member-123")
```

### Integration Testing

```python
# tests/test_integration.py
import pytest
from fastapi.testclient import TestClient
from src.main import app
import json

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers():
    # Mock JWT token for testing
    return {"Authorization": "Bearer test-token"}

class TestWebBFFIntegration:
    def test_graphql_member_dashboard(self, client, auth_headers):
        query = """
        query {
            memberDashboard(memberId: "123") {
                memberId
                name
                planName
                recentClaims {
                    id
                    status
                }
            }
        }
        """
        
        response = client.post(
            "/graphql",
            json={"query": query},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "memberDashboard" in data["data"]
    
    def test_rest_get_claims(self, client, auth_headers):
        response = client.get(
            "/api/v1/claims/member-123?limit=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "claims" in data
        assert "total" in data
    
    def test_rest_submit_claim(self, client, auth_headers):
        claim_data = {
            "member_id": "member-123",
            "provider_id": "provider-456",
            "service_date": "2024-01-15",
            "items": [
                {
                    "benefit_code": "CONS-GP",
                    "amount": 500000,
                    "quantity": 1
                }
            ]
        }
        
        response = client.post(
            "/api/v1/claims",
            json=claim_data,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert "id" in data
        assert "claim_number" in data
    
    @pytest.mark.asyncio
    async def test_circuit_breaker(self, client, auth_headers):
        # Simulate multiple failures to trigger circuit breaker
        for _ in range(6):
            response = client.get(
                "/api/v1/claims/invalid-member",
                headers=auth_headers
            )
            # First 5 should fail normally, 6th should trigger circuit
        
        # Circuit should be open now
        response = client.get(
            "/api/v1/claims/valid-member",
            headers=auth_headers
        )
        
        assert response.status_code == 503
        assert "temporarily unavailable" in response.json()["detail"].lower()
```

## Performance Optimization

### Request Batching

```typescript
@Injectable()
export class BatchingService {
  private batch: Map<string, Promise<any>> = new Map();
  
  async batchRequest<T>(
    key: string,
    factory: () => Promise<T>
  ): Promise<T> {
    if (!this.batch.has(key)) {
      const promise = factory().finally(() => {
        this.batch.delete(key);
      });
      
      this.batch.set(key, promise);
    }
    
    return this.batch.get(key);
  }
}
```

### Response Compression

```typescript
app.use(compression({
  filter: (req, res) => {
    if (req.headers['x-no-compression']) {
      return false;
    }
    return compression.filter(req, res);
  },
  level: 6
}));
```

## Monitoring

### Metrics Collection

```typescript
@Injectable()
export class MetricsService {
  private register: Registry;
  private httpDuration: Histogram;
  private serviceCallDuration: Histogram;
  
  constructor() {
    this.register = new Registry();
    
    this.httpDuration = new Histogram({
      name: 'http_request_duration_seconds',
      help: 'Duration of HTTP requests in seconds',
      labelNames: ['method', 'route', 'status'],
      registers: [this.register]
    });
    
    this.serviceCallDuration = new Histogram({
      name: 'service_call_duration_seconds',
      help: 'Duration of service calls in seconds',
      labelNames: ['service', 'method'],
      registers: [this.register]
    });
  }
  
  recordHttpRequest(method: string, route: string, status: number, duration: number) {
    this.httpDuration.observe({ method, route, status }, duration);
  }
  
  recordServiceCall(service: string, method: string, duration: number) {
    this.serviceCallDuration.observe({ service, method }, duration);
  }
}
```

### Health Checks

```typescript
@Controller('health')
export class HealthController {
  constructor(
    private health: HealthCheckService,
    private http: HttpHealthIndicator,
    private redis: RedisHealthIndicator
  ) {}
  
  @Get()
  @HealthCheck()
  check() {
    return this.health.check([
      () => this.http.pingCheck('claims-service', process.env.CLAIMS_SERVICE_URL),
      () => this.http.pingCheck('member-service', process.env.MEMBER_SERVICE_URL),
      () => this.redis.isHealthy('redis')
    ]);
  }
}
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
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production image
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 4000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import httpx; httpx.get('http://localhost:4000/health')"

# Run with uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "4000"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  web-bff:
    build: .
    ports:
      - "4000:4000"
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://user:pass@postgres:5432/db
      - CLAIMS_SERVICE_URL=http://claims-service:8001
      - MEMBER_SERVICE_URL=http://member-service:8002
    depends_on:
      - redis
      - postgres
    networks:
      - claims-network
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - claims-network
  
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=claims_askes
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    networks:
      - claims-network

networks:
  claims-network:
    driver: bridge
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-bff
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-bff
  template:
    metadata:
      labels:
        app: web-bff
    spec:
      containers:
      - name: web-bff
        image: web-bff:latest
        ports:
        - containerPort: 4000
        env:
        - name: NODE_ENV
          value: production
        livenessProbe:
          httpGet:
            path: /health
            port: 4000
        readinessProbe:
          httpGet:
            path: /health
            port: 4000
```

## Troubleshooting

### Common Issues

1. **Service timeout errors**
   - Increase timeout in circuit breaker
   - Check service health endpoints
   - Review network connectivity

2. **High memory usage**
   - Review cache TTL settings
   - Implement cache eviction policies
   - Monitor for memory leaks

3. **GraphQL N+1 queries**
   - Implement DataLoader pattern
   - Use field-level caching
   - Optimize resolver queries

## Application Setup

### Main Application

```python
# src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import strawberry
from strawberry.fastapi import GraphQLRouter

from src.api.rest import claims, members, dashboard
from src.api.graphql.schema import schema
from src.core.config import settings
from src.middleware.auth import AuthMiddleware
from src.services.cache_service import CacheService

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    cache = CacheService()
    await cache.redis.ping()
    print("Connected to Redis")
    yield
    # Shutdown
    await cache.redis.close()
    print("Disconnected from Redis")

app = FastAPI(
    title="Web BFF Service",
    description="Backend for Frontend aggregation layer",
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

app.add_middleware(AuthMiddleware)

# GraphQL endpoint
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

# REST endpoints
app.include_router(claims.router, tags=["claims"])
app.include_router(members.router, tags=["members"])
app.include_router(dashboard.router, tags=["dashboard"])

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=4000,
        reload=settings.DEBUG
    )
```

### Requirements

```txt
# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
strawberry-graphql[fastapi]==0.211.1
httpx==0.25.1
redis[hiredis]==5.0.1
python-jose[cryptography]==3.3.0
python-multipart==0.0.6
pydantic==2.4.2
pydantic-settings==2.0.3
celery==5.3.4
prometheus-client==0.18.0
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
```

## Support

- **Documentation**: [Full docs](../../docs)
- **Service Catalog**: [Microservices](../../services)
- **Team**: Platform Team - platform@claims-askes.com

## License

Proprietary - All rights reserved