"""
Pricing Configuration Models
SQLAlchemy models for group health insurance pricing and configuration
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import (
    Column, String, Integer, Decimal as SQLDecimal, Boolean, Date, DateTime,
    ForeignKey, UniqueConstraint, CheckConstraint, JSON, text, Index
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, INET, JSONB
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, validates, Session
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# =====================================================
# ENUMS
# =====================================================

class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    CHILD = "CHILD"

class MemberType(str, Enum):
    EMPLOYEE = "EMPLOYEE"
    SPOUSE = "SPOUSE"
    CHILD = "CHILD"
    
class PolicyStatus(str, Enum):
    DRAFT = "DRAFT"
    QUOTED = "QUOTED"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"

class PricingMethod(str, Enum):
    FULLY_EXPERIENCED = "FULLY_EXPERIENCED"
    MANUAL_RATE = "MANUAL_RATE"
    COMMUNITY_RATED = "COMMUNITY_RATED"
    ASO = "ASO"

class BenefitCategory(str, Enum):
    INPATIENT = "INPATIENT"
    OUTPATIENT = "OUTPATIENT"
    DENTAL = "DENTAL"
    MATERNITY = "MATERNITY"
    OPTICAL = "OPTICAL"
    ASO = "ASO"

class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REVISION = "REVISION"

# =====================================================
# CORE PRICING MODELS
# =====================================================

class ProductTemplate(Base):
    """Base product templates (IP-1000, OP-500, etc)"""
    __tablename__ = 'product_template'
    __table_args__ = {'schema': 'pricing'}
    
    template_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    template_code = Column(String(20), unique=True, nullable=False)
    template_name = Column(String(100), nullable=False)
    product_category = Column(String(50), nullable=False)
    
    # Base premiums by demographic
    base_premium_adult_male = Column(SQLDecimal(12, 2))
    base_premium_adult_female = Column(SQLDecimal(12, 2))
    base_premium_child = Column(SQLDecimal(12, 2))
    
    version = Column(String(10), default='v4.3')
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    age_bands = relationship("AgeBandMultiplier", back_populates="template")
    benefit_selections = relationship("BenefitSelection", back_populates="template")
    
    def get_base_premium(self, gender: str, age: int) -> Decimal:
        """Get base premium for given demographics"""
        if age < 18:
            return self.base_premium_child or Decimal('0')
        elif gender == Gender.MALE:
            return self.base_premium_adult_male or Decimal('0')
        else:
            return self.base_premium_adult_female or Decimal('0')


class AgeBandMultiplier(Base):
    """Age-based premium multipliers"""
    __tablename__ = 'age_band_multiplier'
    __table_args__ = (
        UniqueConstraint('template_id', 'age_from', 'age_to', 'gender'),
        {'schema': 'pricing'}
    )
    
    band_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    template_id = Column(PGUUID(as_uuid=True), ForeignKey('pricing.product_template.template_id'))
    age_from = Column(Integer, nullable=False)
    age_to = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)
    multiplier = Column(SQLDecimal(5, 3), nullable=False, default=Decimal('1.000'))
    
    # Relationships
    template = relationship("ProductTemplate", back_populates="age_bands")
    
    @validates('age_from', 'age_to')
    def validate_age_range(self, key, value):
        if key == 'age_to' and hasattr(self, 'age_from'):
            if value < self.age_from:
                raise ValueError("age_to must be greater than age_from")
        return value


class TCFactorConfig(Base):
    """Terms & Conditions factor configuration"""
    __tablename__ = 'tc_factor_config'
    __table_args__ = {'schema': 'pricing'}
    
    factor_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    factor_code = Column(String(20), unique=True, nullable=False)
    factor_category = Column(String(50), nullable=False)
    factor_name = Column(String(100), nullable=False)
    factor_description = Column(String)
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer)
    
    # Relationships
    options = relationship("TCFactorOption", back_populates="factor", cascade="all, delete-orphan")
    policy_selections = relationship("PolicyTCSelection", back_populates="factor")


class TCFactorOption(Base):
    """Options for each TC factor"""
    __tablename__ = 'tc_factor_option'
    __table_args__ = {'schema': 'pricing'}
    
    option_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    factor_id = Column(PGUUID(as_uuid=True), ForeignKey('pricing.tc_factor_config.factor_id'))
    option_value = Column(String(200), nullable=False)
    option_label = Column(String(200), nullable=False)
    multiplier = Column(SQLDecimal(5, 3), nullable=False, default=Decimal('1.000'))
    is_default = Column(Boolean, default=False)
    min_participants = Column(Integer)
    max_participants = Column(Integer)
    display_order = Column(Integer)
    
    # Relationships
    factor = relationship("TCFactorConfig", back_populates="options")
    policy_selections = relationship("PolicyTCSelection", back_populates="option")

# =====================================================
# POLICY CONFIGURATION MODELS
# =====================================================

class PolicyConfig(Base):
    """Main policy configuration and pricing setup"""
    __tablename__ = 'policy_config'
    __table_args__ = {'schema': 'pricing'}
    
    config_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    policy_number = Column(String(50), unique=True)
    quote_number = Column(String(50), unique=True)
    
    # Company Information
    company_name = Column(String(255), nullable=False)
    industry_type = Column(String(100))
    participant_count = Column(Integer, nullable=False)
    class_count = Column(Integer, default=1)
    
    # Coverage Period
    coverage_start = Column(Date, nullable=False)
    coverage_end = Column(Date, nullable=False)
    
    # Pricing Method
    pricing_method = Column(String(50), nullable=False)
    distribution_channel = Column(String(100))
    pricing_officer = Column(String(100))
    
    # Status
    status = Column(String(20), default=PolicyStatus.DRAFT)
    
    # Calculated Values
    total_base_premium = Column(SQLDecimal(15, 2))
    total_adjusted_premium = Column(SQLDecimal(15, 2))
    total_factor_multiplier = Column(SQLDecimal(10, 6))
    
    # Metadata
    created_by = Column(String(100))
    approved_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = Column(DateTime)
    
    # Relationships
    benefit_selections = relationship("BenefitSelection", back_populates="config", cascade="all, delete-orphan")
    tc_selections = relationship("PolicyTCSelection", back_populates="config", cascade="all, delete-orphan")
    benefit_overrides = relationship("PolicyBenefitOverride", back_populates="config", cascade="all, delete-orphan")
    members = relationship("PolicyMember", back_populates="config", cascade="all, delete-orphan")
    calculations = relationship("PremiumCalculationLog", back_populates="config")
    approvals = relationship("ApprovalWorkflow", back_populates="config")
    
    @hybrid_property
    def coverage_days(self) -> int:
        """Calculate coverage period in days"""
        if self.coverage_start and self.coverage_end:
            return (self.coverage_end - self.coverage_start).days
        return 0
    
    def calculate_total_factor(self) -> Decimal:
        """Calculate total multiplier from all selected factors"""
        total = Decimal('1.000')
        
        # Benefit category factors
        for selection in self.benefit_selections:
            if selection.is_selected:
                total *= selection.category_factor or Decimal('1.000')
        
        # TC factors
        for tc_selection in self.tc_selections:
            total *= tc_selection.applied_multiplier or Decimal('1.000')
        
        return total
    
    def calculate_premium(self, session: Session) -> Dict[str, Any]:
        """Calculate total premium for the policy"""
        base_total = Decimal('0')
        
        # Calculate base premium for all members
        for member in self.members:
            if member.status == 'ACTIVE':
                base_total += member.calculate_base_premium(session)
        
        # Apply total factor
        total_factor = self.calculate_total_factor()
        adjusted_total = base_total * total_factor
        
        # Update stored values
        self.total_base_premium = base_total
        self.total_factor_multiplier = total_factor
        self.total_adjusted_premium = adjusted_total
        
        return {
            'base_premium': float(base_total),
            'total_factor': float(total_factor),
            'adjusted_premium': float(adjusted_total),
            'monthly_premium': float(adjusted_total / 12),
            'per_member_average': float(adjusted_total / self.participant_count) if self.participant_count > 0 else 0
        }


class BenefitSelection(Base):
    """Selected benefits for a policy configuration"""
    __tablename__ = 'benefit_selection'
    __table_args__ = (
        UniqueConstraint('config_id', 'benefit_category'),
        {'schema': 'pricing'}
    )
    
    selection_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    config_id = Column(PGUUID(as_uuid=True), ForeignKey('pricing.policy_config.config_id', ondelete='CASCADE'))
    benefit_category = Column(String(50), nullable=False)
    template_id = Column(PGUUID(as_uuid=True), ForeignKey('pricing.product_template.template_id'))
    is_selected = Column(Boolean, default=False)
    category_factor = Column(SQLDecimal(5, 3), default=Decimal('1.000'))
    
    # Relationships
    config = relationship("PolicyConfig", back_populates="benefit_selections")
    template = relationship("ProductTemplate", back_populates="benefit_selections")


class PolicyTCSelection(Base):
    """Selected TC factors for a policy"""
    __tablename__ = 'policy_tc_selection'
    __table_args__ = (
        UniqueConstraint('config_id', 'factor_id'),
        {'schema': 'pricing'}
    )
    
    selection_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    config_id = Column(PGUUID(as_uuid=True), ForeignKey('pricing.policy_config.config_id', ondelete='CASCADE'))
    factor_id = Column(PGUUID(as_uuid=True), ForeignKey('pricing.tc_factor_config.factor_id'))
    option_id = Column(PGUUID(as_uuid=True), ForeignKey('pricing.tc_factor_option.option_id'))
    applied_multiplier = Column(SQLDecimal(5, 3), nullable=False)
    
    # Relationships
    config = relationship("PolicyConfig", back_populates="tc_selections")
    factor = relationship("TCFactorConfig", back_populates="policy_selections")
    option = relationship("TCFactorOption", back_populates="policy_selections")


class PolicyBenefitOverride(Base):
    """Customized benefit limits for a policy"""
    __tablename__ = 'policy_benefit_override'
    __table_args__ = (
        UniqueConstraint('config_id', 'benefit_code'),
        {'schema': 'pricing'}
    )
    
    override_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    config_id = Column(PGUUID(as_uuid=True), ForeignKey('pricing.policy_config.config_id', ondelete='CASCADE'))
    benefit_code = Column(String(20), nullable=False)
    benefit_name = Column(String(200))
    original_limit = Column(SQLDecimal(15, 2))
    override_limit = Column(SQLDecimal(15, 2))
    limit_type = Column(String(50))
    override_reason = Column(String)
    
    # Relationships
    config = relationship("PolicyConfig", back_populates="benefit_overrides")

# =====================================================
# MEMBER ENROLLMENT MODELS
# =====================================================

class PolicyMember(Base):
    """Enrolled members for each policy configuration"""
    __tablename__ = 'policy_member'
    __table_args__ = (
        UniqueConstraint('config_id', 'member_number'),
        {'schema': 'pricing'}
    )
    
    member_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    config_id = Column(PGUUID(as_uuid=True), ForeignKey('pricing.policy_config.config_id', ondelete='CASCADE'))
    member_number = Column(Integer, nullable=False)
    
    # Member Information
    full_name = Column(String(255), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(10), nullable=False)
    member_type = Column(String(20), nullable=False)
    relationship = Column(String(50))
    
    # Classification
    class_code = Column(String(10), default='1')
    age_band = Column(String(20))
    
    # Premium Calculation
    base_premium = Column(SQLDecimal(12, 2))
    adjusted_premium = Column(SQLDecimal(12, 2))
    
    # Status
    enrollment_date = Column(Date)
    termination_date = Column(Date)
    status = Column(String(20), default='ACTIVE')
    
    # Relationships
    config = relationship("PolicyConfig", back_populates="members")
    
    @hybrid_property
    def age(self) -> int:
        """Calculate current age"""
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return 0
    
    def get_age_band(self) -> str:
        """Determine age band for premium calculation"""
        age = self.age
        if age < 18:
            return "CHILD"
        elif age <= 55:
            return "0-55"
        elif age <= 60:
            return "56-60"
        elif age <= 65:
            return "61-65"
        elif age <= 70:
            return "66-70"
        elif age <= 75:
            return "71-75"
        else:
            return "76+"
    
    def calculate_base_premium(self, session: Session) -> Decimal:
        """Calculate base premium for this member"""
        # Get selected benefits for the policy
        benefit_selections = session.query(BenefitSelection).filter(
            BenefitSelection.config_id == self.config_id,
            BenefitSelection.is_selected == True
        ).all()
        
        total_premium = Decimal('0')
        age_band = self.get_age_band()
        
        for selection in benefit_selections:
            if selection.template:
                # Get base premium from template
                base = selection.template.get_base_premium(self.gender, self.age)
                
                # Apply age band multiplier
                age_multiplier = session.query(AgeBandMultiplier).filter(
                    AgeBandMultiplier.template_id == selection.template_id,
                    AgeBandMultiplier.age_from <= self.age,
                    AgeBandMultiplier.age_to >= self.age,
                    AgeBandMultiplier.gender == self.gender if self.age >= 18 else 'CHILD'
                ).first()
                
                if age_multiplier:
                    base *= age_multiplier.multiplier
                
                total_premium += base
        
        self.base_premium = total_premium
        self.age_band = age_band
        
        return total_premium

# =====================================================
# CALCULATION & AUDIT MODELS
# =====================================================

class PremiumCalculationLog(Base):
    """Audit trail of all premium calculations"""
    __tablename__ = 'premium_calculation_log'
    __table_args__ = {'schema': 'pricing'}
    
    calc_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    config_id = Column(PGUUID(as_uuid=True), ForeignKey('pricing.policy_config.config_id'))
    calculation_timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Input Parameters
    participant_count = Column(Integer)
    selected_benefits = Column(JSONB)
    selected_factors = Column(JSONB)
    
    # Calculation Steps
    base_premium_total = Column(SQLDecimal(15, 2))
    factor_details = Column(JSONB)
    total_multiplier = Column(SQLDecimal(10, 6))
    
    # Results
    monthly_premium = Column(SQLDecimal(15, 2))
    annual_premium = Column(SQLDecimal(15, 2))
    admin_fee = Column(SQLDecimal(12, 2))
    tpa_fee = Column(SQLDecimal(12, 2))
    total_premium = Column(SQLDecimal(15, 2))
    
    # User Info
    calculated_by = Column(String(100))
    ip_address = Column(INET)
    user_agent = Column(String)
    
    # Relationships
    config = relationship("PolicyConfig", back_populates="calculations")


class ApprovalWorkflow(Base):
    """Pricing approval workflow tracking"""
    __tablename__ = 'approval_workflow'
    __table_args__ = (
        UniqueConstraint('config_id', 'step_order'),
        {'schema': 'pricing'}
    )
    
    workflow_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    config_id = Column(PGUUID(as_uuid=True), ForeignKey('pricing.policy_config.config_id'))
    
    # Workflow Steps
    step_name = Column(String(50), nullable=False)
    step_order = Column(Integer, nullable=False)
    
    # Approval Details
    approver_id = Column(String(100))
    approval_status = Column(String(20))
    approval_date = Column(DateTime)
    comments = Column(String)
    
    # Conditions
    min_premium_threshold = Column(SQLDecimal(15, 2))
    max_discount_allowed = Column(SQLDecimal(5, 2))
    
    # Relationships
    config = relationship("PolicyConfig", back_populates="approvals")

# =====================================================
# RATE TABLES
# =====================================================

class RateTable(Base):
    """Master rate table for premium calculations"""
    __tablename__ = 'rate_table'
    __table_args__ = (
        UniqueConstraint('rate_code', 'benefit_code', 'effective_date'),
        {'schema': 'pricing'}
    )
    
    rate_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    rate_code = Column(String(20), nullable=False)
    benefit_code = Column(String(20), nullable=False)
    benefit_description = Column(String)
    
    # Age Band Rates
    age_0_55_male = Column(SQLDecimal(12, 2))
    age_0_55_female = Column(SQLDecimal(12, 2))
    age_0_55_child = Column(SQLDecimal(12, 2))
    age_56_60_male = Column(SQLDecimal(12, 2))
    age_56_60_female = Column(SQLDecimal(12, 2))
    age_61_65_male = Column(SQLDecimal(12, 2))
    age_61_65_female = Column(SQLDecimal(12, 2))
    age_66_70_male = Column(SQLDecimal(12, 2))
    age_66_70_female = Column(SQLDecimal(12, 2))
    age_71_75_male = Column(SQLDecimal(12, 2))
    age_71_75_female = Column(SQLDecimal(12, 2))
    
    effective_date = Column(Date, nullable=False)
    expiry_date = Column(Date)
    
    def get_rate(self, age: int, gender: str) -> Decimal:
        """Get rate for specific age and gender"""
        if age < 18:
            return self.age_0_55_child or Decimal('0')
        
        if age <= 55:
            return self.age_0_55_male if gender == 'MALE' else self.age_0_55_female
        elif age <= 60:
            return self.age_56_60_male if gender == 'MALE' else self.age_56_60_female
        elif age <= 65:
            return self.age_61_65_male if gender == 'MALE' else self.age_61_65_female
        elif age <= 70:
            return self.age_66_70_male if gender == 'MALE' else self.age_66_70_female
        elif age <= 75:
            return self.age_71_75_male if gender == 'MALE' else self.age_71_75_female
        
        return Decimal('0')  # Over 75 not covered

# =====================================================
# INTEGRATION MODELS
# =====================================================

class PolicyPricingLink(Base):
    """Link pricing config to actual policies in claims schema"""
    __tablename__ = 'policy_pricing_link'
    __table_args__ = (
        UniqueConstraint('config_id'),
        UniqueConstraint('policy_id'),
        {'schema': 'pricing'}
    )
    
    link_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    config_id = Column(PGUUID(as_uuid=True), ForeignKey('pricing.policy_config.config_id'))
    policy_id = Column(PGUUID(as_uuid=True))  # References claims.policy
    plan_id = Column(PGUUID(as_uuid=True))    # References claims.plan
    
    # Conversion metadata
    converted_at = Column(DateTime)
    converted_by = Column(String(100))
    
    # Relationships (config only, policy/plan are in different schema)
    config = relationship("PolicyConfig")

# Create indexes
Index('idx_policy_config_status', PolicyConfig.status)
Index('idx_policy_config_dates', PolicyConfig.coverage_start, PolicyConfig.coverage_end)
Index('idx_policy_member_config', PolicyMember.config_id)
Index('idx_benefit_selection_config', BenefitSelection.config_id)
Index('idx_tc_selection_config', PolicyTCSelection.config_id)
Index('idx_calc_log_config', PremiumCalculationLog.config_id)
Index('idx_calc_log_timestamp', PremiumCalculationLog.calculation_timestamp.desc())