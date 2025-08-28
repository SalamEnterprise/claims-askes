# Claims Engine Service

## Overview
The Claims Engine Service is the core service responsible for managing the entire claims lifecycle from submission to payment. It orchestrates the claims workflow, manages state transitions, and coordinates with other services.

## Architecture

### Domain Model
```go
// Core domain entities
type Claim struct {
    ID              uuid.UUID
    ClaimNumber     string
    MemberID        uuid.UUID
    ProviderID      uuid.UUID
    ServiceDate     time.Time
    SubmissionDate  time.Time
    ClaimType       ClaimType
    Status          ClaimStatus
    Items           []ClaimItem
    Documents       []Document
    Authorization   *Authorization
    Adjudication    *Adjudication
    Payment         *Payment
    AuditTrail      []AuditEntry
}

type ClaimItem struct {
    ID              uuid.UUID
    ClaimID         uuid.UUID
    ServiceCode     string
    DiagnosisCode   string
    ProcedureCode   string
    Quantity        decimal.Decimal
    ChargedAmount   decimal.Decimal
    AllowedAmount   decimal.Decimal
    PaidAmount      decimal.Decimal
}
```

### Service Structure
```
claims-engine/
├── cmd/
│   └── server/
│       └── main.go                 # Application entry point
│
├── internal/
│   ├── api/
│   │   ├── grpc/
│   │   │   └── claims_server.go   # gRPC server implementation
│   │   ├── rest/
│   │   │   ├── handlers.go        # REST handlers
│   │   │   ├── routes.go          # Route definitions
│   │   │   └── middleware.go      # HTTP middleware
│   │   └── graphql/
│   │       └── resolvers.go       # GraphQL resolvers
│   │
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── claim.go          # Claim entity
│   │   │   └── claim_item.go     # Claim item entity
│   │   ├── repositories/
│   │   │   └── claim_repository.go # Repository interface
│   │   ├── services/
│   │   │   ├── claim_service.go   # Domain service
│   │   │   └── workflow_service.go # Workflow orchestration
│   │   └── events/
│   │       └── claim_events.go    # Domain events
│   │
│   ├── infrastructure/
│   │   ├── database/
│   │   │   ├── postgres.go        # PostgreSQL implementation
│   │   │   └── migrations/        # Database migrations
│   │   ├── messaging/
│   │   │   ├── kafka.go           # Kafka producer/consumer
│   │   │   └── events.go          # Event publishing
│   │   ├── cache/
│   │   │   └── redis.go           # Redis cache
│   │   └── external/
│   │       ├── authorization_client.go
│   │       └── adjudication_client.go
│   │
│   ├── application/
│   │   ├── commands/
│   │   │   ├── submit_claim.go    # Submit claim command
│   │   │   └── approve_claim.go   # Approve claim command
│   │   ├── queries/
│   │   │   ├── get_claim.go       # Get claim query
│   │   │   └── list_claims.go     # List claims query
│   │   └── events/
│   │       └── handlers.go        # Event handlers
│   │
│   └── config/
│       └── config.go              # Configuration
│
├── pkg/
│   ├── errors/
│   │   └── errors.go              # Custom error types
│   └── models/
│       └── dto.go                 # Data transfer objects
│
├── migrations/
│   └── *.sql                      # Database migrations
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
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── docs/
│   ├── api.md
│   └── workflow.md
│
├── Makefile
├── go.mod
├── go.sum
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

### gRPC API

```protobuf
service ClaimsService {
  rpc SubmitClaim(SubmitClaimRequest) returns (SubmitClaimResponse);
  rpc GetClaim(GetClaimRequest) returns (Claim);
  rpc ListClaims(ListClaimsRequest) returns (ListClaimsResponse);
  rpc UpdateClaimStatus(UpdateClaimStatusRequest) returns (Claim);
  rpc ProcessClaim(ProcessClaimRequest) returns (ProcessClaimResponse);
}

message Claim {
  string id = 1;
  string claim_number = 2;
  string member_id = 3;
  string provider_id = 4;
  google.protobuf.Timestamp service_date = 5;
  ClaimStatus status = 6;
  repeated ClaimItem items = 7;
}
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
```go
// ClaimSubmittedEvent
type ClaimSubmittedEvent struct {
    EventID     string    `json:"eventId"`
    ClaimID     string    `json:"claimId"`
    MemberID    string    `json:"memberId"`
    ProviderID  string    `json:"providerId"`
    ServiceDate time.Time `json:"serviceDate"`
    Timestamp   time.Time `json:"timestamp"`
}

// ClaimApprovedEvent
type ClaimApprovedEvent struct {
    EventID       string          `json:"eventId"`
    ClaimID       string          `json:"claimId"`
    ApprovedAmount decimal.Decimal `json:"approvedAmount"`
    Timestamp     time.Time       `json:"timestamp"`
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
GRPC_PORT=9090

# Database Configuration
DB_HOST=postgres
DB_PORT=5432
DB_NAME=claims
DB_USER=claims_user
DB_PASSWORD=secure_password
DB_SSL_MODE=require

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# Kafka Configuration
KAFKA_BROKERS=kafka:9092
KAFKA_CONSUMER_GROUP=claims-engine
KAFKA_TOPICS=claims.events,authorization.events,adjudication.events

# Service Discovery
AUTHORIZATION_SERVICE_URL=http://authorization:8081
ADJUDICATION_SERVICE_URL=http://adjudication:8082
PAYMENT_SERVICE_URL=http://payment:8083

# Observability
JAEGER_ENDPOINT=http://jaeger:14268/api/traces
METRICS_PORT=9091

# Security
JWT_SECRET=your-secret-key
ENCRYPTION_KEY=your-encryption-key
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
- Go 1.21+
- PostgreSQL 15+
- Redis 7+
- Kafka 3.0+
- Docker & Docker Compose

### Local Development
```bash
# Install dependencies
go mod download

# Run database migrations
make migrate

# Run tests
make test

# Run service locally
make run

# Build Docker image
make docker-build

# Run with Docker Compose
docker-compose up
```

### Testing
```bash
# Unit tests
go test ./internal/domain/...

# Integration tests
go test ./internal/infrastructure/...

# E2E tests
go test ./tests/e2e/...

# Coverage report
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out
```

## Deployment

### Kubernetes
```bash
# Deploy to development
kubectl apply -f deployments/kubernetes/ -n claims-dev

# Deploy with Helm
helm install claims-engine ./deployments/helm/claims-engine -n claims-prod
```

### Health Checks
- **Liveness**: `/health/live`
- **Readiness**: `/health/ready`
- **Metrics**: `/metrics`

## Monitoring

### Metrics
- `claims_submitted_total` - Total claims submitted
- `claims_processed_total` - Total claims processed
- `claims_processing_duration` - Processing duration histogram
- `claims_status_count` - Claims by status

### Logging
Structured logging with correlation IDs for request tracing.

### Alerts
- High error rate (>1%)
- Processing delays (>5s)
- Database connection issues
- Kafka lag

## SLA
- **Availability**: 99.99%
- **Response Time**: <500ms (p99)
- **Throughput**: 1000 claims/second

---

*For more information, see the [main documentation](../../../docs/README.md)*