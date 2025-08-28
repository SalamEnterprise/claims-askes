# API Documentation - Claims-Askes Platform

## Overview

This document provides comprehensive API documentation for all microservices in the Claims-Askes platform. Each service exposes RESTful APIs following OpenAPI 3.0 specification.

## Base URLs

### Development Environment
```
API Gateway:     http://localhost:80
Web BFF:         http://localhost:4000
Mobile BFF:      http://localhost:4001
Direct Services: http://localhost:800X (where X is service number)
```

### Production Environment
```
API Gateway: https://api.claims-askes.com
Web BFF:     https://web-api.claims-askes.com
Mobile BFF:  https://mobile-api.claims-askes.com
```

## Authentication

### JWT Token Authentication
All API requests require JWT authentication token in the Authorization header:

```http
Authorization: Bearer <jwt_token>
```

### Obtaining Token
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "secure_password"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

## Service APIs

### 1. Claims Service API

#### Submit Claim
```http
POST /api/v1/claims
Content-Type: application/json
Authorization: Bearer <token>

{
  "member_id": "550e8400-e29b-41d4-a716-446655440000",
  "provider_id": "660e8400-e29b-41d4-a716-446655440001",
  "policy_id": "770e8400-e29b-41d4-a716-446655440002",
  "claim_type": "cashless",
  "service_type": "outpatient",
  "service_date": "2024-01-15",
  "admission_date": null,
  "discharge_date": null,
  "items": [
    {
      "benefit_code": "CONS-GP",
      "service_code": "99213",
      "diagnosis_code": "J06.9",
      "procedure_code": "99213",
      "quantity": 1,
      "unit_price": 500000,
      "charged_amount": 500000
    }
  ]
}

Response: 201 Created
{
  "id": "880e8400-e29b-41d4-a716-446655440003",
  "claim_number": "CLM-2024-000001",
  "status": "submitted",
  "submission_date": "2024-01-20T10:00:00Z",
  "total_charged_amount": 500000,
  "items": [...],
  "created_at": "2024-01-20T10:00:00Z"
}
```

#### Get Claim Details
```http
GET /api/v1/claims/{claim_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "id": "880e8400-e29b-41d4-a716-446655440003",
  "claim_number": "CLM-2024-000001",
  "member_id": "550e8400-e29b-41d4-a716-446655440000",
  "provider_id": "660e8400-e29b-41d4-a716-446655440001",
  "status": "approved",
  "total_charged_amount": 500000,
  "total_approved_amount": 450000,
  "total_paid_amount": 450000,
  "member_responsibility": 50000,
  "items": [
    {
      "id": "990e8400-e29b-41d4-a716-446655440004",
      "benefit_code": "CONS-GP",
      "charged_amount": 500000,
      "approved_amount": 450000,
      "paid_amount": 450000,
      "status": "approved"
    }
  ]
}
```

#### List Claims
```http
GET /api/v1/claims?member_id={member_id}&status={status}&page=1&size=20
Authorization: Bearer <token>

Query Parameters:
- member_id (optional): Filter by member
- provider_id (optional): Filter by provider
- status (optional): Filter by status (submitted, processing, approved, rejected)
- service_date_from (optional): Start date filter
- service_date_to (optional): End date filter
- page: Page number (default: 1)
- size: Page size (default: 20, max: 100)

Response: 200 OK
{
  "total": 150,
  "page": 1,
  "size": 20,
  "claims": [...]
}
```

#### Update Claim Status
```http
PATCH /api/v1/claims/{claim_id}/status
Content-Type: application/json
Authorization: Bearer <token>

{
  "status": "approved",
  "notes": "Approved after medical review"
}

Response: 200 OK
```

### 2. Member Service API

#### Get Member Details
```http
GET /api/v1/members/{member_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "member_number": "MEM-2024-000001",
  "first_name": "John",
  "last_name": "Doe",
  "birth_date": "1990-01-01",
  "gender": "male",
  "email": "john.doe@example.com",
  "phone": "+62812345678",
  "status": "active",
  "enrollment_date": "2024-01-01"
}
```

#### Check Member Eligibility
```http
GET /api/v1/members/{member_id}/eligibility
Authorization: Bearer <token>

Response: 200 OK
{
  "member_id": "550e8400-e29b-41d4-a716-446655440000",
  "is_eligible": true,
  "coverage": {
    "plan_id": "plan_123",
    "plan_name": "Premium Plan",
    "coverage_start_date": "2024-01-01",
    "coverage_end_date": "2024-12-31",
    "status": "active"
  },
  "restrictions": [],
  "waiting_periods": []
}
```

#### Get Member Coverage
```http
GET /api/v1/members/{member_id}/coverage
Authorization: Bearer <token>

Response: 200 OK
{
  "member_id": "550e8400-e29b-41d4-a716-446655440000",
  "policy_id": "770e8400-e29b-41d4-a716-446655440002",
  "plan_id": "plan_123",
  "relationship": "employee",
  "coverage_start_date": "2024-01-01",
  "coverage_end_date": "2024-12-31",
  "inner_limit_applicable": true,
  "annual_cap_applicable": false,
  "benefits": [
    {
      "benefit_code": "CONS-GP",
      "benefit_name": "GP Consultation",
      "limit_amount": 10000000,
      "used_amount": 500000,
      "remaining_amount": 9500000
    }
  ]
}
```

### 3. Provider Service API

#### Search Providers
```http
GET /api/v1/providers/search?specialty=cardiology&city=jakarta&limit=10
Authorization: Bearer <token>

Query Parameters:
- specialty (optional): Medical specialty
- city (optional): City location
- provider_type (optional): hospital, clinic, pharmacy, lab
- provider_class (optional): A, B, C, D
- is_network (optional): true/false
- limit: Result limit (default: 20)

Response: 200 OK
{
  "total": 45,
  "providers": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "provider_code": "PRV-001",
      "provider_name": "RS Premier Jakarta",
      "provider_type": "hospital",
      "provider_class": "A",
      "is_network": true,
      "address": "Jl. Sudirman No. 1",
      "city": "Jakarta",
      "phone": "+622112345678",
      "specialties": ["cardiology", "internal_medicine"],
      "facilities": ["ICU", "emergency", "pharmacy"]
    }
  ]
}
```

#### Get Provider Details
```http
GET /api/v1/providers/{provider_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "provider_code": "PRV-001",
  "provider_name": "RS Premier Jakarta",
  "provider_type": "hospital",
  "provider_class": "A",
  "is_network": true,
  "contract": {
    "contract_number": "CNT-2024-001",
    "effective_date": "2024-01-01",
    "expiry_date": "2024-12-31",
    "cashless_enabled": true,
    "reimbursement_enabled": true,
    "discount_percentage": 15
  }
}
```

### 4. Authorization Service API

#### Request Pre-Authorization
```http
POST /api/v1/authorizations
Content-Type: application/json
Authorization: Bearer <token>

{
  "member_id": "550e8400-e29b-41d4-a716-446655440000",
  "provider_id": "660e8400-e29b-41d4-a716-446655440001",
  "service_type": "inpatient",
  "procedure_code": "47.0",
  "diagnosis_code": "K35.8",
  "requested_days": 3,
  "requested_amount": 25000000,
  "admission_date": "2024-02-01"
}

Response: 201 Created
{
  "id": "auth_123",
  "authorization_number": "AUTH-2024-000001",
  "status": "pending",
  "created_at": "2024-01-20T10:00:00Z"
}
```

#### Get Authorization Status
```http
GET /api/v1/authorizations/{authorization_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "id": "auth_123",
  "authorization_number": "AUTH-2024-000001",
  "status": "approved",
  "approved_amount": 20000000,
  "approved_days": 3,
  "valid_from": "2024-02-01",
  "valid_to": "2024-02-03",
  "decision_date": "2024-01-21T14:30:00Z",
  "decision_by": "Medical Reviewer",
  "notes": "Approved for appendectomy procedure"
}
```

### 5. Benefit Service API

#### Get Plan Benefits
```http
GET /api/v1/plans/{plan_id}/benefits
Authorization: Bearer <token>

Response: 200 OK
{
  "plan_id": "plan_123",
  "plan_name": "Premium Plan",
  "plan_type": "premium",
  "annual_limit": 500000000,
  "benefits": [
    {
      "benefit_code": "IP-ROOM",
      "benefit_name": "Inpatient Room",
      "benefit_category": "inpatient",
      "coverage_type": "covered",
      "limit_type": "per_day",
      "limit_amount": 2000000,
      "limit_days": 365,
      "coinsurance_percentage": 10,
      "requires_authorization": true
    },
    {
      "benefit_code": "CONS-GP",
      "benefit_name": "GP Consultation",
      "benefit_category": "outpatient",
      "coverage_type": "covered",
      "limit_type": "per_year",
      "limit_amount": 10000000,
      "limit_visits": 50,
      "coinsurance_percentage": 0,
      "requires_authorization": false
    }
  ]
}
```

#### Calculate Benefit Coverage
```http
POST /api/v1/benefits/calculate
Content-Type: application/json
Authorization: Bearer <token>

{
  "member_id": "550e8400-e29b-41d4-a716-446655440000",
  "benefit_code": "IP-ROOM",
  "service_date": "2024-02-01",
  "charged_amount": 2500000,
  "days": 1
}

Response: 200 OK
{
  "benefit_code": "IP-ROOM",
  "charged_amount": 2500000,
  "benefit_limit": 2000000,
  "covered_amount": 1800000,
  "coinsurance_amount": 200000,
  "member_responsibility": 700000,
  "calculation_details": {
    "base_coverage": 2000000,
    "coinsurance_rate": 10,
    "excess_amount": 500000
  }
}
```

## BFF API Endpoints

### Web BFF - Aggregated Endpoints

#### Member Claims Dashboard
```http
GET /api/claims/dashboard/{member_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "member": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "John Doe",
    "member_number": "MEM-2024-000001",
    "status": "active"
  },
  "recent_claims": [
    {
      "claim_number": "CLM-2024-000001",
      "service_date": "2024-01-15",
      "provider": "RS Premier Jakarta",
      "status": "approved",
      "amount": 500000
    }
  ],
  "coverage": {
    "plan_name": "Premium Plan",
    "annual_limit": 500000000,
    "used_amount": 5000000,
    "remaining_amount": 495000000
  },
  "benefit_usage": {
    "outpatient": {
      "used": 2000000,
      "limit": 50000000,
      "percentage": 4
    },
    "inpatient": {
      "used": 3000000,
      "limit": 450000000,
      "percentage": 0.67
    }
  },
  "summary": {
    "total_claims": 5,
    "pending_claims": 1,
    "total_spent": 5000000
  }
}
```

#### Submit Claim with Validation
```http
POST /api/claims/submit-with-validation
Content-Type: application/json
Authorization: Bearer <token>

{
  "member_id": "550e8400-e29b-41d4-a716-446655440000",
  "provider_id": "660e8400-e29b-41d4-a716-446655440001",
  "service_type": "outpatient",
  "service_date": "2024-01-15",
  "items": [
    {
      "benefit_code": "CONS-GP",
      "diagnosis_code": "J06.9",
      "charged_amount": 500000
    }
  ]
}

Response: 200 OK
{
  "success": true,
  "claim": {
    "id": "880e8400-e29b-41d4-a716-446655440003",
    "claim_number": "CLM-2024-000002",
    "status": "submitted"
  },
  "validations": {
    "eligibility": "passed",
    "provider": "passed",
    "authorization": "not_required",
    "benefit_limit": "passed"
  },
  "message": "Claim submitted successfully"
}
```

### Mobile BFF - Optimized Endpoints

#### Mobile Member Summary
```http
GET /api/mobile/member/summary
Authorization: Bearer <token>

Response: 200 OK
{
  "member": {
    "name": "John Doe",
    "card_number": "MEM-2024-000001",
    "plan": "Premium"
  },
  "quick_stats": {
    "available_limit": 495000000,
    "pending_claims": 1,
    "last_claim_date": "2024-01-15"
  },
  "actions": [
    {
      "id": "find_provider",
      "label": "Find Provider",
      "icon": "hospital"
    },
    {
      "id": "submit_claim",
      "label": "Submit Claim",
      "icon": "document"
    }
  ]
}
```

## Error Responses

### Standard Error Format
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional context"
    }
  },
  "timestamp": "2024-01-20T10:00:00Z",
  "path": "/api/v1/claims",
  "request_id": "req_123abc"
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Missing or invalid authentication |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 400 | Input validation failed |
| `DUPLICATE_ENTRY` | 409 | Resource already exists |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

## Rate Limiting

API rate limits per authenticated user:
- Standard endpoints: 1000 requests/hour
- Search endpoints: 100 requests/minute
- Submission endpoints: 50 requests/minute

Rate limit headers:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Pagination

All list endpoints support pagination:

```http
GET /api/v1/claims?page=2&size=50
```

Response includes pagination metadata:
```json
{
  "data": [...],
  "pagination": {
    "total": 500,
    "page": 2,
    "size": 50,
    "total_pages": 10,
    "has_next": true,
    "has_previous": true
  }
}
```

## Webhooks

### Webhook Events

Services can subscribe to events via webhooks:

```json
POST /api/v1/webhooks/subscribe
{
  "url": "https://your-service.com/webhook",
  "events": ["claim.approved", "claim.rejected"],
  "secret": "webhook_secret_key"
}
```

### Event Payload Format
```json
{
  "event": "claim.approved",
  "timestamp": "2024-01-20T10:00:00Z",
  "data": {
    "claim_id": "880e8400-e29b-41d4-a716-446655440003",
    "claim_number": "CLM-2024-000001",
    "status": "approved"
  },
  "signature": "sha256=..."
}
```

## API Versioning

APIs are versioned using URL path:
- Current version: `/api/v1`
- Previous versions maintained for backward compatibility
- Deprecation notices provided 6 months in advance

## SDK Support

Official SDKs available:
- Python: `pip install claims-askes-sdk`
- JavaScript/TypeScript: `npm install @claims-askes/sdk`
- Java: Maven/Gradle support
- Go: `go get github.com/claims-askes/sdk-go`

## Testing

### Test Environment
- Base URL: `https://api-test.claims-askes.com`
- Test credentials available upon request

### Postman Collection
Download our Postman collection for easy API testing:
[Claims-Askes API Collection](https://www.getpostman.com/collections/claims-askes)

## Support

- API Status: https://status.claims-askes.com
- Developer Portal: https://developers.claims-askes.com
- Support Email: api-support@claims-askes.com
- Community Forum: https://forum.claims-askes.com