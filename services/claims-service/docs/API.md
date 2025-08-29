# Claims Service API Documentation

## API Version
Current Version: v1

## Base URLs
- Development: `http://localhost:8001/api/v1`
- Staging: `https://staging-api.claims-askes.com/claims/api/v1`
- Production: `https://api.claims-askes.com/claims/api/v1`

## Authentication
All API endpoints require JWT authentication token in the Authorization header:
```http
Authorization: Bearer <jwt_token>
```

## Content Types
- Request: `application/json`
- Response: `application/json`
- File Upload: `multipart/form-data`

## API Endpoints

### 1. Submit Claim

Create a new insurance claim.

**Endpoint:** `POST /claims`

**Request Body:**
```json
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
```

**Response:** `201 Created`
```json
{
  "id": "880e8400-e29b-41d4-a716-446655440003",
  "claim_number": "CLM-2024-000001",
  "status": "submitted",
  "submission_date": "2024-01-20T10:00:00Z",
  "total_charged_amount": 500000,
  "created_at": "2024-01-20T10:00:00Z"
}
```

**Validation Rules:**
- `member_id`: Required, must be valid UUID
- `provider_id`: Required, must be valid UUID
- `claim_type`: Required, enum: ["cashless", "reimbursement"]
- `service_type`: Required, enum: ["inpatient", "outpatient", "dental", "optical", "maternity"]
- `service_date`: Required, ISO 8601 date format
- `items`: Required, minimum 1 item

### 2. Get Claim Details

Retrieve details of a specific claim.

**Endpoint:** `GET /claims/{claim_id}`

**Path Parameters:**
- `claim_id` (UUID): The claim identifier

**Response:** `200 OK`
```json
{
  "id": "880e8400-e29b-41d4-a716-446655440003",
  "claim_number": "CLM-2024-000001",
  "member_id": "550e8400-e29b-41d4-a716-446655440000",
  "provider_id": "660e8400-e29b-41d4-a716-446655440001",
  "policy_id": "770e8400-e29b-41d4-a716-446655440002",
  "claim_type": "cashless",
  "service_type": "outpatient",
  "service_date": "2024-01-15",
  "status": "approved",
  "submission_date": "2024-01-20T10:00:00Z",
  "total_charged_amount": 500000,
  "total_approved_amount": 450000,
  "total_paid_amount": 450000,
  "member_responsibility": 50000,
  "items": [
    {
      "id": "990e8400-e29b-41d4-a716-446655440004",
      "benefit_code": "CONS-GP",
      "service_code": "99213",
      "diagnosis_code": "J06.9",
      "charged_amount": 500000,
      "approved_amount": 450000,
      "paid_amount": 450000,
      "deductible_amount": 0,
      "coinsurance_amount": 50000,
      "copay_amount": 0,
      "status": "approved"
    }
  ],
  "documents": [
    {
      "id": "aa0e8400-e29b-41d4-a716-446655440005",
      "document_type": "invoice",
      "file_name": "invoice_001.pdf",
      "uploaded_at": "2024-01-20T10:05:00Z"
    }
  ],
  "created_at": "2024-01-20T10:00:00Z",
  "updated_at": "2024-01-20T14:30:00Z"
}
```

### 3. List Claims

Retrieve a paginated list of claims with optional filters.

**Endpoint:** `GET /claims`

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| member_id | UUID | No | Filter by member |
| provider_id | UUID | No | Filter by provider |
| status | string | No | Filter by status |
| service_type | string | No | Filter by service type |
| claim_type | string | No | Filter by claim type |
| service_date_from | date | No | Start date filter |
| service_date_to | date | No | End date filter |
| submission_date_from | datetime | No | Submission start filter |
| submission_date_to | datetime | No | Submission end filter |
| page | integer | No | Page number (default: 1) |
| size | integer | No | Page size (default: 20, max: 100) |
| sort | string | No | Sort field (default: submission_date) |
| order | string | No | Sort order: asc/desc (default: desc) |

**Response:** `200 OK`
```json
{
  "total": 150,
  "page": 1,
  "size": 20,
  "total_pages": 8,
  "claims": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "claim_number": "CLM-2024-000001",
      "member_id": "550e8400-e29b-41d4-a716-446655440000",
      "provider_id": "660e8400-e29b-41d4-a716-446655440001",
      "service_date": "2024-01-15",
      "status": "approved",
      "total_charged_amount": 500000
    }
  ]
}
```

### 4. Update Claim Status

Update the status of a claim (restricted to authorized users).

**Endpoint:** `PATCH /claims/{claim_id}/status`

**Request Body:**
```json
{
  "status": "approved",
  "notes": "Approved after medical review",
  "approved_amount": 450000
}
```

**Valid Status Transitions:**
- `submitted` → `processing`, `rejected`
- `processing` → `approved`, `rejected`, `pending_info`
- `pending_info` → `processing`, `rejected`
- `approved` → `payment_processing`
- `payment_processing` → `paid`

**Response:** `200 OK`
```json
{
  "id": "880e8400-e29b-41d4-a716-446655440003",
  "claim_number": "CLM-2024-000001",
  "status": "approved",
  "updated_at": "2024-01-20T14:30:00Z"
}
```

### 5. Upload Claim Document

Upload supporting documents for a claim.

**Endpoint:** `POST /claims/{claim_id}/documents`

**Content-Type:** `multipart/form-data`

**Form Fields:**
- `file`: The document file (max 10MB)
- `document_type`: Type of document (invoice, prescription, medical_report, etc.)

**Response:** `201 Created`
```json
{
  "id": "aa0e8400-e29b-41d4-a716-446655440005",
  "claim_id": "880e8400-e29b-41d4-a716-446655440003",
  "document_type": "invoice",
  "file_name": "invoice_001.pdf",
  "file_size": 245632,
  "mime_type": "application/pdf",
  "uploaded_at": "2024-01-20T10:05:00Z"
}
```

### 6. Get Claim Documents

Retrieve all documents for a claim.

**Endpoint:** `GET /claims/{claim_id}/documents`

**Response:** `200 OK`
```json
{
  "documents": [
    {
      "id": "aa0e8400-e29b-41d4-a716-446655440005",
      "document_type": "invoice",
      "file_name": "invoice_001.pdf",
      "file_size": 245632,
      "uploaded_at": "2024-01-20T10:05:00Z",
      "download_url": "/claims/880e8400/documents/aa0e8400/download"
    }
  ]
}
```

### 7. Download Document

Download a specific document.

**Endpoint:** `GET /claims/{claim_id}/documents/{document_id}/download`

**Response:** Binary file stream with appropriate Content-Type header

### 8. Delete Claim

Delete a claim (only if status is 'submitted').

**Endpoint:** `DELETE /claims/{claim_id}`

**Response:** `204 No Content`

### 9. Resubmit Claim

Resubmit a rejected claim with corrections.

**Endpoint:** `POST /claims/{claim_id}/resubmit`

**Request Body:**
```json
{
  "items": [...],
  "notes": "Corrected diagnosis code"
}
```

**Response:** `200 OK`

### 10. Get Claim History

Get the status change history of a claim.

**Endpoint:** `GET /claims/{claim_id}/history`

**Response:** `200 OK`
```json
{
  "history": [
    {
      "status": "submitted",
      "timestamp": "2024-01-20T10:00:00Z",
      "user": "system"
    },
    {
      "status": "processing",
      "timestamp": "2024-01-20T10:30:00Z",
      "user": "processor_01"
    },
    {
      "status": "approved",
      "timestamp": "2024-01-20T14:30:00Z",
      "user": "medical_reviewer_01",
      "notes": "Approved after medical review"
    }
  ]
}
```

## Error Responses

### Error Format
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
| `VALIDATION_ERROR` | 400 | Request validation failed |
| `UNAUTHORIZED` | 401 | Missing or invalid authentication |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Claim not found |
| `CONFLICT` | 409 | Duplicate claim or invalid state transition |
| `UNPROCESSABLE_ENTITY` | 422 | Business rule violation |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

## Rate Limiting

API rate limits per authenticated user:
- Submit claim: 10 requests/minute
- Get claim: 100 requests/minute
- List claims: 50 requests/minute
- Upload document: 20 requests/minute

Rate limit headers:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1640995200
```

## Webhooks

Claims service can send webhooks for claim events:

### Webhook Events
- `claim.submitted`
- `claim.approved`
- `claim.rejected`
- `claim.paid`

### Webhook Payload
```json
{
  "event": "claim.approved",
  "timestamp": "2024-01-20T14:30:00Z",
  "data": {
    "claim_id": "880e8400-e29b-41d4-a716-446655440003",
    "claim_number": "CLM-2024-000001",
    "status": "approved",
    "approved_amount": 450000
  },
  "signature": "sha256=..."
}
```

## API Versioning

- Current version: v1
- Version in URL path: `/api/v1/claims`
- Deprecation notice: 6 months advance notice
- Sunset period: 3 months after deprecation

## Testing

### Test Environment
- Base URL: `https://test-api.claims-askes.com/claims/api/v1`
- Test credentials available from DevOps team

### Postman Collection
Available at: `/docs/postman/claims-service.json`

### Example cURL Commands

Submit claim:
```bash
curl -X POST http://localhost:8001/api/v1/claims \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "member_id": "550e8400-e29b-41d4-a716-446655440000",
    "provider_id": "660e8400-e29b-41d4-a716-446655440001",
    "claim_type": "cashless",
    "service_type": "outpatient",
    "service_date": "2024-01-15",
    "items": [...]
  }'
```

Get claim:
```bash
curl -X GET http://localhost:8001/api/v1/claims/880e8400-e29b-41d4-a716-446655440003 \
  -H "Authorization: Bearer $TOKEN"
```