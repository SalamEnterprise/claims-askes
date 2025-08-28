"""
Claim Pydantic Schemas
Data validation and serialization schemas
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID


# ==================== Base Schemas ====================
class ClaimItemBase(BaseModel):
    """Base schema for claim items"""
    benefit_code: str = Field(..., max_length=50)
    service_code: Optional[str] = Field(None, max_length=50)
    diagnosis_code: Optional[str] = Field(None, max_length=20)
    procedure_code: Optional[str] = Field(None, max_length=20)
    quantity: int = Field(1, ge=1)
    unit_price: Optional[Decimal] = Field(None, decimal_places=2)
    charged_amount: Decimal = Field(..., decimal_places=2)


class ClaimBase(BaseModel):
    """Base schema for claims"""
    member_id: UUID
    provider_id: UUID
    policy_id: UUID
    claim_type: str = Field(..., pattern="^(cashless|reimbursement)$")
    service_type: str = Field(..., pattern="^(inpatient|outpatient|dental|optical|maternity)$")
    service_date: date
    admission_date: Optional[date] = None
    discharge_date: Optional[date] = None


# ==================== Create Schemas ====================
class ClaimItemCreate(ClaimItemBase):
    """Schema for creating claim items"""
    pass


class ClaimCreate(ClaimBase):
    """Schema for creating a claim"""
    items: List[ClaimItemCreate] = Field(..., min_length=1)
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "member_id": "550e8400-e29b-41d4-a716-446655440000",
            "provider_id": "660e8400-e29b-41d4-a716-446655440001",
            "policy_id": "770e8400-e29b-41d4-a716-446655440002",
            "claim_type": "cashless",
            "service_type": "outpatient",
            "service_date": "2024-01-15",
            "items": [
                {
                    "benefit_code": "CONS-GP",
                    "diagnosis_code": "J06.9",
                    "quantity": 1,
                    "charged_amount": "500000"
                }
            ]
        }
    })


# ==================== Update Schemas ====================
class ClaimUpdate(BaseModel):
    """Schema for updating a claim"""
    status: Optional[str] = None
    admission_date: Optional[date] = None
    discharge_date: Optional[date] = None


# ==================== Response Schemas ====================
class ClaimItemResponse(BaseModel):
    """Response schema for claim items"""
    id: UUID
    claim_id: UUID
    benefit_code: str
    service_code: Optional[str]
    diagnosis_code: Optional[str]
    procedure_code: Optional[str]
    quantity: int
    unit_price: Optional[Decimal]
    charged_amount: Decimal
    approved_amount: Optional[Decimal]
    paid_amount: Optional[Decimal]
    deductible_amount: Decimal
    coinsurance_amount: Decimal
    copay_amount: Decimal
    status: str
    denial_reason: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ClaimDocumentResponse(BaseModel):
    """Response schema for claim documents"""
    id: UUID
    document_type: str
    file_name: str
    file_size: Optional[int]
    mime_type: Optional[str]
    uploaded_at: datetime
    uploaded_by: Optional[str]
    
    model_config = ConfigDict(from_attributes=True)


class ClaimResponse(BaseModel):
    """Response schema for claims"""
    id: UUID
    claim_number: str
    member_id: UUID
    provider_id: UUID
    policy_id: UUID
    claim_type: str
    service_type: str
    admission_date: Optional[date]
    discharge_date: Optional[date]
    service_date: date
    status: str
    submission_date: datetime
    total_charged_amount: Optional[Decimal]
    total_approved_amount: Optional[Decimal]
    total_paid_amount: Optional[Decimal]
    member_responsibility: Optional[Decimal]
    created_at: datetime
    updated_at: datetime
    items: List[ClaimItemResponse] = []
    documents: List[ClaimDocumentResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


class ClaimListResponse(BaseModel):
    """Response schema for claim list"""
    total: int
    page: int
    size: int
    claims: List[ClaimResponse]


# ==================== Search/Filter Schemas ====================
class ClaimFilter(BaseModel):
    """Schema for filtering claims"""
    member_id: Optional[UUID] = None
    provider_id: Optional[UUID] = None
    status: Optional[str] = None
    service_date_from: Optional[date] = None
    service_date_to: Optional[date] = None
    submission_date_from: Optional[datetime] = None
    submission_date_to: Optional[datetime] = None


# ==================== Event Schemas ====================
class ClaimSubmittedEvent(BaseModel):
    """Event schema for claim submission"""
    claim_id: UUID
    claim_number: str
    member_id: UUID
    provider_id: UUID
    service_date: date
    total_charged_amount: Decimal
    submitted_at: datetime


class ClaimStatusChangedEvent(BaseModel):
    """Event schema for claim status change"""
    claim_id: UUID
    claim_number: str
    old_status: str
    new_status: str
    changed_at: datetime
    changed_by: Optional[str] = None