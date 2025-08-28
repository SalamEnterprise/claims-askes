# Microservices Architecture Documentation

## Overview
The Claims-Askes platform follows a microservices architecture pattern with complete separation of concerns. Each service owns its data and communicates via REST APIs or asynchronous events.

## Architecture Principles

### 1. Database Per Service with Schema Separation
We use a **hybrid approach** combining logical and physical separation:

```sql
PostgreSQL Instance (Shared in Dev/Staging, Separate in Production)
├── claims_service schema       (owned by claims-service)
├── member_service schema       (owned by member-service)
├── provider_service schema     (owned by provider-service)
├── benefit_service schema      (owned by benefit-service)
├── policy_service schema       (owned by policy-service)
├── common schema              (read-only reference data)
└── audit schema               (audit logs)
```

**Key Rules:**
- Each service can ONLY access its own schema
- No cross-schema joins or direct database access
- Inter-service data access MUST go through APIs
- Common schema contains shared reference data (read-only)

### 2. Service Communication Patterns

#### Synchronous Communication (REST)
```python
# Example: Claims service getting member data
async def get_member_details(member_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{MEMBER_SERVICE_URL}/api/v1/members/{member_id}"
        )
        return response.json()
```

#### Asynchronous Communication (Events)
```python
# Example: Publishing claim submitted event
async def publish_claim_submitted(claim_data):
    event = {
        "event_type": "claim.submitted",
        "claim_id": claim_data.id,
        "timestamp": datetime.utcnow()
    }
    await message_queue.publish(event)
```

### 3. BFF (Backend for Frontend) Pattern

The BFF layer optimizes API calls for different client types:

**Web BFF:**
- Aggregates multiple service calls
- Optimizes for desktop bandwidth
- Provides rich data sets

**Mobile BFF:**
- Minimizes payload size
- Reduces number of API calls
- Optimizes for mobile bandwidth

## Service Catalog

### Core Business Services

| Service | Port | Schema | Responsibility |
|---------|------|--------|---------------|
| claims-service | 8001 | claims_service | Claims processing and management |
| member-service | 8002 | member_service | Member management and eligibility |
| provider-service | 8003 | provider_service | Provider network management |
| benefit-service | 8004 | benefit_service | Benefit configuration and rules |
| policy-service | 8005 | policy_service | Policy administration |
| authorization-service | 8006 | authorization_service | Pre-authorization and approvals |
| adjudication-service | 8007 | adjudication_service | Claims adjudication and rules engine |
| payment-service | 8008 | payment_service | Payment processing and EOB |
| notification-service | 8009 | notification_service | Notifications and alerts |
| document-service | 8010 | document_service | Document storage and management |

### BFF Services

| Service | Port | Purpose |
|---------|------|---------|
| web-bff | 4000 | Aggregates APIs for web applications |
| mobile-bff | 4001 | Optimizes APIs for mobile applications |

## Service Structure

Each microservice follows this standard structure:

```
service-name/
├── src/
│   ├── api/v1/           # API endpoints
│   │   ├── endpoints/    # Route handlers
│   │   └── middlewares/  # API middleware
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   ├── repositories/     # Data access layer
│   ├── events/           # Event handling
│   │   ├── publishers/   # Event publishers
│   │   └── consumers/    # Event consumers
│   ├── utils/           # Utilities
│   └── config/          # Configuration
├── tests/               # Test suites
├── migrations/          # Database migrations
├── requirements.txt     # Dependencies
├── Dockerfile          # Container definition
└── README.md           # Service documentation
```

## API Design Standards

### REST API Conventions

```
GET    /api/v1/resources          # List resources
GET    /api/v1/resources/{id}     # Get single resource
POST   /api/v1/resources          # Create resource
PUT    /api/v1/resources/{id}     # Update resource
PATCH  /api/v1/resources/{id}     # Partial update
DELETE /api/v1/resources/{id}     # Delete resource
```

### Standard Response Format

```json
{
  "success": true,
  "data": {},
  "message": "Operation successful",
  "errors": [],
  "metadata": {
    "timestamp": "2024-01-15T10:00:00Z",
    "version": "1.0.0"
  }
}
```

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  },
  "metadata": {
    "timestamp": "2024-01-15T10:00:00Z",
    "request_id": "abc-123"
  }
}
```

## Event-Driven Architecture

### Event Naming Convention
```
<domain>.<entity>.<action>
```

Examples:
- `claim.submitted`
- `claim.approved`
- `member.enrolled`
- `payment.processed`

### Event Structure

```json
{
  "event_id": "uuid",
  "event_type": "claim.submitted",
  "timestamp": "2024-01-15T10:00:00Z",
  "service": "claims-service",
  "data": {
    "claim_id": "uuid",
    "member_id": "uuid"
  },
  "metadata": {
    "correlation_id": "uuid",
    "user_id": "uuid"
  }
}
```

## Development Workflow

### 1. Start Infrastructure
```bash
docker-compose -f docker-compose.dev.yml up -d
```

### 2. Initialize Database
```bash
docker exec -i claims-postgres psql -U postgres claims_askes < database/init.sql
```

### 3. Run a Service
```bash
cd services/claims-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8001
```

### 4. Run BFF
```bash
cd bff/web-bff
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 4000
```

## Service Discovery

### Development Environment
Services discover each other using environment variables:

```python
# .env file for each service
MEMBER_SERVICE_URL=http://localhost:8002
PROVIDER_SERVICE_URL=http://localhost:8003
BENEFIT_SERVICE_URL=http://localhost:8004
```

### Production Environment
Use service mesh (Istio) or service discovery (Consul):

```python
# Dynamic service discovery
service_url = service_discovery.get_url("member-service")
```

## Security

### Service-to-Service Authentication
```python
# JWT token for service authentication
headers = {
    "Authorization": f"Bearer {service_token}",
    "X-Service-Name": "claims-service"
}
```

### API Gateway Authentication
- OAuth 2.0 for external clients
- JWT tokens for authenticated requests
- Rate limiting per client

## Monitoring & Observability

### Health Checks
Each service exposes:
- `/health` - Basic health status
- `/ready` - Readiness probe (checks dependencies)

### Metrics
Each service exposes Prometheus metrics:
- Request count
- Request duration
- Error rate
- Business metrics

### Distributed Tracing
Use correlation IDs for request tracing:

```python
# Pass correlation ID through service calls
headers = {
    "X-Correlation-ID": correlation_id
}
```

## Deployment Strategy

### Development
- All services run locally
- Single PostgreSQL with schema separation
- Docker Compose for infrastructure

### Staging
- Kubernetes deployment
- Single PostgreSQL with schema separation
- Horizontal scaling for services

### Production
- Kubernetes with auto-scaling
- Separate PostgreSQL instances per service
- Multi-region deployment
- Blue-green deployments

## Migration Path

### Phase 1: Current State
- Single PostgreSQL with schema separation
- Services communicate via REST
- Basic event publishing

### Phase 2: Enhanced Integration
- Add service mesh (Istio)
- Implement saga patterns for distributed transactions
- Add circuit breakers

### Phase 3: Full Separation
- Separate databases per service
- CQRS for read/write separation
- Event sourcing for audit trail

## Best Practices

### 1. API Versioning
Always version APIs:
```
/api/v1/claims
/api/v2/claims  # New version
```

### 2. Backward Compatibility
- Never break existing APIs
- Deprecate gracefully
- Support multiple versions

### 3. Idempotency
Make operations idempotent:
```python
# Use idempotency keys
@app.post("/api/v1/claims")
async def create_claim(
    claim: ClaimCreate,
    idempotency_key: str = Header(None)
):
    # Check if already processed
    if await is_already_processed(idempotency_key):
        return existing_response
```

### 4. Graceful Degradation
Handle service failures gracefully:
```python
try:
    member_data = await get_member_details(member_id)
except ServiceUnavailable:
    # Use cached data or default
    member_data = get_cached_member(member_id)
```

### 5. Data Consistency
Use eventual consistency patterns:
- Saga pattern for distributed transactions
- Event-driven updates
- Compensation transactions

## Common Patterns

### 1. Aggregation Pattern (BFF)
```python
# Aggregate data from multiple services
async def get_claim_details(claim_id):
    claim, member, provider = await asyncio.gather(
        get_claim(claim_id),
        get_member(member_id),
        get_provider(provider_id)
    )
    return aggregate_response(claim, member, provider)
```

### 2. Circuit Breaker Pattern
```python
from circuit_breaker import CircuitBreaker

@CircuitBreaker(failure_threshold=5, recovery_timeout=30)
async def call_external_service():
    # Service call with automatic circuit breaking
    pass
```

### 3. Retry Pattern
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def resilient_service_call():
    # Automatic retry with exponential backoff
    pass
```

## Troubleshooting

### Service Can't Connect to Database
```bash
# Check database user permissions
docker exec -it claims-postgres psql -U postgres -d claims_askes
\du  # List users
\dn+ # List schemas with permissions
```

### Service Discovery Issues
```bash
# Test service connectivity
curl http://localhost:8001/health
curl http://localhost:8002/health
```

### Event Publishing Issues
```bash
# Check RabbitMQ management UI
open http://localhost:15672
# Login: admin/admin
```

## Next Steps

1. **Implement remaining services** following the claims-service template
2. **Add authentication** using JWT tokens
3. **Implement event consumers** for asynchronous processing
4. **Add caching layer** using Redis
5. **Create integration tests** for service interactions
6. **Add monitoring** with Prometheus and Grafana
7. **Implement API documentation** using OpenAPI/Swagger