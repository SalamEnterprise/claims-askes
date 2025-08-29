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
- **ORM**: SQLAlchemy 2.0
- **Cache**: Redis
- **Message Queue**: RabbitMQ
- **Testing**: pytest, pytest-asyncio

### Domain Model
```
Claim (Aggregate Root)
├── ClaimItem (Entity)
├── ClaimDocument (Entity)
└── ClaimStatus (Value Object)
```

## Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- RabbitMQ 3.12+

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

6. **Start the service**
```bash
# Development
uvicorn src.main:app --reload --port 8001

# Production
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
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

# RabbitMQ
RABBITMQ_URL=amqp://admin:admin@localhost:5672/

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
pytest tests/unit --cov=src --cov-report=html
```

### Integration Tests
```bash
# Run integration tests
pytest tests/integration -v

# Specific test file
pytest tests/integration/test_claim_api.py -v
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
│   └── test_utils.py
├── integration/
│   ├── test_api.py
│   ├── test_database.py
│   └── test_events.py
└── fixtures/
    └── claim_fixtures.py
```

## Deployment

### Docker

Build image:
```bash
docker build -t claims-service:latest .
```

Run container:
```bash
docker run -d \
  --name claims-service \
  -p 8001:8000 \
  -e DATABASE_URL=postgresql://user:pass@db:5432/claims \
  claims-service:latest
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

## API Client Examples

### Python
```python
import httpx

async def submit_claim(claim_data):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/api/v1/claims",
            json=claim_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
```

### JavaScript
```javascript
const submitClaim = async (claimData) => {
  const response = await fetch('http://localhost:8001/api/v1/claims', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(claimData)
  });
  return response.json();
};
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