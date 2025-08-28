"""
Claim Domain Models
SQLAlchemy models for claims service
"""

from sqlalchemy import Column, String, UUID, Date, DateTime, Numeric, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from src.models.base import Base


class Claim(Base):
    """Claim entity model"""
    __tablename__ = "claim"
    __table_args__ = {"schema": "claims_service"}
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Business identifiers
    claim_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Foreign references (to other services via API)
    member_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    provider_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    policy_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Claim details
    claim_type = Column(String(20), nullable=False)  # 'cashless', 'reimbursement'
    service_type = Column(String(20), nullable=False)  # 'inpatient', 'outpatient', etc
    admission_date = Column(Date)
    discharge_date = Column(Date)
    service_date = Column(Date, nullable=False, index=True)
    
    # Status
    status = Column(String(30), nullable=False, default='submitted', index=True)
    submission_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Financial summary
    total_charged_amount = Column(Numeric(15, 2))
    total_approved_amount = Column(Numeric(15, 2))
    total_paid_amount = Column(Numeric(15, 2))
    member_responsibility = Column(Numeric(15, 2))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    items = relationship("ClaimItem", back_populates="claim", cascade="all, delete-orphan")
    documents = relationship("ClaimDocument", back_populates="claim", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Claim {self.claim_number}>"


class ClaimItem(Base):
    """Claim line item model"""
    __tablename__ = "claim_item"
    __table_args__ = {"schema": "claims_service"}
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key
    claim_id = Column(UUID(as_uuid=True), ForeignKey("claims_service.claim.id"), nullable=False)
    
    # Service details
    benefit_code = Column(String(50), nullable=False)
    service_code = Column(String(50))
    diagnosis_code = Column(String(20))
    procedure_code = Column(String(20))
    
    # Quantities and amounts
    quantity = Column(Integer, default=1)
    unit_price = Column(Numeric(15, 2))
    charged_amount = Column(Numeric(15, 2), nullable=False)
    approved_amount = Column(Numeric(15, 2))
    paid_amount = Column(Numeric(15, 2))
    
    # Adjudication details
    deductible_amount = Column(Numeric(15, 2), default=0)
    coinsurance_amount = Column(Numeric(15, 2), default=0)
    copay_amount = Column(Numeric(15, 2), default=0)
    
    # Status
    status = Column(String(30), nullable=False, default='pending')
    denial_reason = Column(String(500))
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relationship
    claim = relationship("Claim", back_populates="items")
    
    def __repr__(self):
        return f"<ClaimItem {self.id} for {self.benefit_code}>"


class ClaimDocument(Base):
    """Claim document model"""
    __tablename__ = "claim_document"
    __table_args__ = {"schema": "claims_service"}
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key
    claim_id = Column(UUID(as_uuid=True), ForeignKey("claims_service.claim.id"), nullable=False)
    
    # Document details
    document_type = Column(String(50), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    
    # Metadata
    uploaded_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    uploaded_by = Column(String(100))
    
    # Relationship
    claim = relationship("Claim", back_populates="documents")
    
    def __repr__(self):
        return f"<ClaimDocument {self.document_type} for claim {self.claim_id}>"