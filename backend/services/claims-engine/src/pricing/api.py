"""
Pricing Configuration API Endpoints
FastAPI endpoints for group health insurance pricing and configuration
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Body, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
import pandas as pd
import io

from ..database import get_db
from .pricing_engine import PricingEngine
from .models import (
    PolicyStatus, PricingMethod, BenefitCategory, 
    Gender, MemberType, ApprovalStatus
)

router = APIRouter(prefix="/api/pricing", tags=["pricing"])

# =====================================================
# REQUEST/RESPONSE MODELS
# =====================================================

class CreateConfigRequest(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    industry_type: Optional[str] = None
    participant_count: int = Field(..., gt=0)
    class_count: int = Field(default=1, ge=1)
    coverage_start: date
    coverage_end: date
    pricing_method: str = PricingMethod.FULLY_EXPERIENCED
    distribution_channel: Optional[str] = None
    pricing_officer: Optional[str] = None
    
    @validator('coverage_end')
    def validate_coverage_dates(cls, v, values):
        if 'coverage_start' in values and v <= values['coverage_start']:
            raise ValueError('coverage_end must be after coverage_start')
        return v

class BenefitToggleRequest(BaseModel):
    benefit_category: BenefitCategory
    is_selected: bool

class TCFactorUpdateRequest(BaseModel):
    factor_code: str
    option_value: str

class BenefitLimitOverrideRequest(BaseModel):
    benefit_code: str
    new_limit: Decimal = Field(..., gt=0)
    reason: Optional[str] = None

class AddMemberRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    date_of_birth: date
    gender: Gender
    member_type: MemberType
    relationship: Optional[str] = None
    class_code: str = Field(default='1')
    
    @validator('date_of_birth')
    def validate_dob(cls, v):
        if v >= date.today():
            raise ValueError('date_of_birth must be in the past')
        return v

class ApprovalRequest(BaseModel):
    approver_id: str
    step_name: str
    comments: Optional[str] = None

class ConfigurationResponse(BaseModel):
    config_id: UUID
    policy_number: Optional[str]
    quote_number: str
    company_name: str
    participant_count: int
    coverage_start: date
    coverage_end: date
    status: PolicyStatus
    total_base_premium: Optional[Decimal]
    total_adjusted_premium: Optional[Decimal]
    total_factor_multiplier: Optional[Decimal]
    created_at: datetime
    updated_at: datetime

class PremiumCalculationResponse(BaseModel):
    config_id: UUID
    calculation_date: datetime
    company_name: str
    participant_count: int
    coverage_period: Dict[str, Any]
    premium_breakdown: Dict[str, float]
    monthly_premium: float
    per_member_average: float
    factor_breakdown: Dict[str, Any]
    member_details: List[Dict[str, Any]]

class BenefitSelectionResponse(BaseModel):
    selection_id: UUID
    benefit_category: str
    is_selected: bool
    category_factor: Decimal
    template_name: Optional[str]

class TCFactorResponse(BaseModel):
    factor_code: str
    factor_name: str
    factor_category: str
    selected_option: Optional[str]
    applied_multiplier: Optional[Decimal]
    available_options: List[Dict[str, Any]]

class MemberResponse(BaseModel):
    member_id: UUID
    member_number: int
    full_name: str
    date_of_birth: date
    gender: str
    member_type: str
    age_band: Optional[str]
    base_premium: Optional[Decimal]
    status: str

# =====================================================
# CONFIGURATION ENDPOINTS
# =====================================================

@router.post("/configurations", response_model=ConfigurationResponse)
async def create_configuration(
    request: CreateConfigRequest,
    db: Session = Depends(get_db)
):
    """Create a new policy pricing configuration"""
    try:
        engine = PricingEngine(db)
        config = engine.create_policy_configuration(
            company_name=request.company_name,
            industry_type=request.industry_type,
            participant_count=request.participant_count,
            class_count=request.class_count,
            coverage_start=request.coverage_start,
            coverage_end=request.coverage_end,
            pricing_method=request.pricing_method,
            distribution_channel=request.distribution_channel,
            pricing_officer=request.pricing_officer
        )
        
        return ConfigurationResponse(
            config_id=config.config_id,
            policy_number=config.policy_number,
            quote_number=config.quote_number,
            company_name=config.company_name,
            participant_count=config.participant_count,
            coverage_start=config.coverage_start,
            coverage_end=config.coverage_end,
            status=config.status,
            total_base_premium=config.total_base_premium,
            total_adjusted_premium=config.total_adjusted_premium,
            total_factor_multiplier=config.total_factor_multiplier,
            created_at=config.created_at,
            updated_at=config.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/configurations/{config_id}", response_model=ConfigurationResponse)
async def get_configuration(
    config_id: UUID,
    db: Session = Depends(get_db)
):
    """Get configuration details"""
    from .models import PolicyConfig
    
    config = db.query(PolicyConfig).filter(
        PolicyConfig.config_id == config_id
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    return ConfigurationResponse(
        config_id=config.config_id,
        policy_number=config.policy_number,
        quote_number=config.quote_number,
        company_name=config.company_name,
        participant_count=config.participant_count,
        coverage_start=config.coverage_start,
        coverage_end=config.coverage_end,
        status=config.status,
        total_base_premium=config.total_base_premium,
        total_adjusted_premium=config.total_adjusted_premium,
        total_factor_multiplier=config.total_factor_multiplier,
        created_at=config.created_at,
        updated_at=config.updated_at
    )

@router.get("/configurations", response_model=List[ConfigurationResponse])
async def list_configurations(
    status: Optional[PolicyStatus] = Query(None),
    company_name: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List policy configurations with filtering"""
    from .models import PolicyConfig
    
    query = db.query(PolicyConfig)
    
    if status:
        query = query.filter(PolicyConfig.status == status)
    
    if company_name:
        query = query.filter(PolicyConfig.company_name.ilike(f"%{company_name}%"))
    
    configs = query.order_by(PolicyConfig.created_at.desc()).limit(limit).offset(offset).all()
    
    return [
        ConfigurationResponse(
            config_id=c.config_id,
            policy_number=c.policy_number,
            quote_number=c.quote_number,
            company_name=c.company_name,
            participant_count=c.participant_count,
            coverage_start=c.coverage_start,
            coverage_end=c.coverage_end,
            status=c.status,
            total_base_premium=c.total_base_premium,
            total_adjusted_premium=c.total_adjusted_premium,
            total_factor_multiplier=c.total_factor_multiplier,
            created_at=c.created_at,
            updated_at=c.updated_at
        ) for c in configs
    ]

# =====================================================
# BENEFIT CONFIGURATION ENDPOINTS
# =====================================================

@router.get("/configurations/{config_id}/benefits", response_model=List[BenefitSelectionResponse])
async def get_benefit_selections(
    config_id: UUID,
    db: Session = Depends(get_db)
):
    """Get benefit selections for a configuration"""
    from .models import BenefitSelection
    
    selections = db.query(BenefitSelection).filter(
        BenefitSelection.config_id == config_id
    ).all()
    
    return [
        BenefitSelectionResponse(
            selection_id=s.selection_id,
            benefit_category=s.benefit_category,
            is_selected=s.is_selected,
            category_factor=s.category_factor,
            template_name=s.template.template_name if s.template else None
        ) for s in selections
    ]

@router.post("/configurations/{config_id}/benefits/toggle")
async def toggle_benefit(
    config_id: UUID,
    request: BenefitToggleRequest,
    db: Session = Depends(get_db)
):
    """Toggle a benefit category on/off"""
    try:
        engine = PricingEngine(db)
        selection = engine.toggle_benefit_category(
            config_id=config_id,
            category=request.benefit_category,
            is_selected=request.is_selected
        )
        
        # Recalculate premium
        premium_result = engine.calculate_premium(config_id)
        
        return {
            "selection": {
                "benefit_category": selection.benefit_category,
                "is_selected": selection.is_selected,
                "category_factor": float(selection.category_factor)
            },
            "premium_update": premium_result["premium_breakdown"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/configurations/{config_id}/benefits/override")
async def override_benefit_limit(
    config_id: UUID,
    request: BenefitLimitOverrideRequest,
    db: Session = Depends(get_db)
):
    """Override a specific benefit limit"""
    try:
        engine = PricingEngine(db)
        override = engine.update_benefit_limit(
            config_id=config_id,
            benefit_code=request.benefit_code,
            new_limit=request.new_limit,
            reason=request.reason
        )
        
        return {
            "override_id": str(override.override_id),
            "benefit_code": override.benefit_code,
            "original_limit": float(override.original_limit) if override.original_limit else None,
            "override_limit": float(override.override_limit),
            "reason": override.override_reason
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =====================================================
# TC FACTOR ENDPOINTS
# =====================================================

@router.get("/configurations/{config_id}/factors", response_model=List[TCFactorResponse])
async def get_tc_factors(
    config_id: UUID,
    db: Session = Depends(get_db)
):
    """Get TC factors for a configuration"""
    from .models import TCFactorConfig, PolicyTCSelection
    
    # Get all active factors
    factors = db.query(TCFactorConfig).filter(
        TCFactorConfig.is_active == True
    ).order_by(TCFactorConfig.display_order).all()
    
    # Get current selections
    selections = db.query(PolicyTCSelection).filter(
        PolicyTCSelection.config_id == config_id
    ).all()
    
    selection_map = {s.factor_id: s for s in selections}
    engine = PricingEngine(db)
    
    response = []
    for factor in factors:
        selection = selection_map.get(factor.factor_id)
        options = engine.get_applicable_tc_options(config_id, factor.factor_code)
        
        response.append(TCFactorResponse(
            factor_code=factor.factor_code,
            factor_name=factor.factor_name,
            factor_category=factor.factor_category,
            selected_option=selection.option.option_label if selection and selection.option else None,
            applied_multiplier=selection.applied_multiplier if selection else None,
            available_options=[
                {
                    "option_id": str(opt.option_id),
                    "option_value": opt.option_value,
                    "option_label": opt.option_label,
                    "multiplier": float(opt.multiplier),
                    "is_default": opt.is_default
                } for opt in options
            ]
        ))
    
    return response

@router.post("/configurations/{config_id}/factors/update")
async def update_tc_factor(
    config_id: UUID,
    request: TCFactorUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update a TC factor selection"""
    try:
        engine = PricingEngine(db)
        selection = engine.update_tc_factor(
            config_id=config_id,
            factor_code=request.factor_code,
            option_value=request.option_value
        )
        
        # Recalculate premium
        premium_result = engine.calculate_premium(config_id)
        
        return {
            "factor": {
                "factor_code": selection.factor.factor_code,
                "selected_option": selection.option.option_label,
                "multiplier": float(selection.applied_multiplier)
            },
            "premium_update": premium_result["premium_breakdown"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =====================================================
# MEMBER MANAGEMENT ENDPOINTS
# =====================================================

@router.get("/configurations/{config_id}/members", response_model=List[MemberResponse])
async def get_members(
    config_id: UUID,
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get members for a configuration"""
    from .models import PolicyMember
    
    query = db.query(PolicyMember).filter(
        PolicyMember.config_id == config_id
    )
    
    if status:
        query = query.filter(PolicyMember.status == status)
    
    members = query.order_by(PolicyMember.member_number).all()
    
    return [
        MemberResponse(
            member_id=m.member_id,
            member_number=m.member_number,
            full_name=m.full_name,
            date_of_birth=m.date_of_birth,
            gender=m.gender,
            member_type=m.member_type,
            age_band=m.age_band,
            base_premium=m.base_premium,
            status=m.status
        ) for m in members
    ]

@router.post("/configurations/{config_id}/members")
async def add_member(
    config_id: UUID,
    request: AddMemberRequest,
    db: Session = Depends(get_db)
):
    """Add a member to the configuration"""
    try:
        engine = PricingEngine(db)
        member = engine.add_member(
            config_id=config_id,
            full_name=request.full_name,
            date_of_birth=request.date_of_birth,
            gender=request.gender.value,
            member_type=request.member_type.value,
            relationship=request.relationship,
            class_code=request.class_code
        )
        
        # Recalculate premium
        premium_result = engine.calculate_premium(config_id)
        
        return {
            "member": {
                "member_id": str(member.member_id),
                "member_number": member.member_number,
                "full_name": member.full_name,
                "base_premium": float(member.base_premium) if member.base_premium else 0
            },
            "premium_update": premium_result["premium_breakdown"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/configurations/{config_id}/members/import")
async def import_members(
    config_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import members from Excel file"""
    try:
        # Read Excel file
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # Validate required columns
        required_columns = ['full_name', 'date_of_birth', 'gender', 'member_type']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Convert to dict format
        excel_data = df.to_dict('records')
        
        # Import members
        engine = PricingEngine(db)
        members, errors = engine.import_members_from_excel(config_id, excel_data)
        
        # Recalculate premium if members added
        premium_update = None
        if members:
            premium_result = engine.calculate_premium(config_id)
            premium_update = premium_result["premium_breakdown"]
        
        return {
            "imported_count": len(members),
            "error_count": len(errors),
            "errors": errors[:10],  # Return first 10 errors
            "premium_update": premium_update
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =====================================================
# PREMIUM CALCULATION ENDPOINTS
# =====================================================

@router.post("/configurations/{config_id}/calculate", response_model=PremiumCalculationResponse)
async def calculate_premium(
    config_id: UUID,
    save: bool = Query(True, description="Save calculation to history"),
    db: Session = Depends(get_db)
):
    """Calculate premium for a configuration"""
    try:
        engine = PricingEngine(db)
        result = engine.calculate_premium(config_id, save_calculation=save)
        
        return PremiumCalculationResponse(
            config_id=UUID(result['config_id']),
            calculation_date=datetime.fromisoformat(result['calculation_date']),
            company_name=result['company_name'],
            participant_count=result['participant_count'],
            coverage_period=result['coverage_period'],
            premium_breakdown=result['premium_breakdown'],
            monthly_premium=result['monthly_premium'],
            per_member_average=result['per_member_average'],
            factor_breakdown=result['factor_breakdown'],
            member_details=result['member_details']
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/configurations/{config_id}/calculations/history")
async def get_calculation_history(
    config_id: UUID,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get calculation history for a configuration"""
    try:
        engine = PricingEngine(db)
        calculations = engine.get_calculation_history(config_id, limit)
        
        return [
            {
                "calc_id": str(calc.calc_id),
                "timestamp": calc.calculation_timestamp.isoformat(),
                "participant_count": calc.participant_count,
                "base_premium": float(calc.base_premium_total) if calc.base_premium_total else 0,
                "total_multiplier": float(calc.total_multiplier) if calc.total_multiplier else 1,
                "total_premium": float(calc.total_premium) if calc.total_premium else 0
            } for calc in calculations
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =====================================================
# APPROVAL WORKFLOW ENDPOINTS
# =====================================================

@router.post("/configurations/{config_id}/submit")
async def submit_for_approval(
    config_id: UUID,
    submitted_by: str = Body(...),
    db: Session = Depends(get_db)
):
    """Submit configuration for approval"""
    try:
        engine = PricingEngine(db)
        config = engine.submit_for_approval(config_id, submitted_by)
        
        return {
            "config_id": str(config.config_id),
            "quote_number": config.quote_number,
            "status": config.status,
            "message": "Configuration submitted for approval successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/configurations/{config_id}/approve")
async def approve_configuration(
    config_id: UUID,
    request: ApprovalRequest,
    db: Session = Depends(get_db)
):
    """Approve a configuration step"""
    try:
        engine = PricingEngine(db)
        config = engine.approve_configuration(
            config_id=config_id,
            approver_id=request.approver_id,
            step_name=request.step_name,
            comments=request.comments
        )
        
        return {
            "config_id": str(config.config_id),
            "status": config.status,
            "policy_number": config.policy_number,
            "message": f"Step {request.step_name} approved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/configurations/{config_id}/approvals")
async def get_approval_status(
    config_id: UUID,
    db: Session = Depends(get_db)
):
    """Get approval workflow status"""
    from .models import ApprovalWorkflow
    
    workflows = db.query(ApprovalWorkflow).filter(
        ApprovalWorkflow.config_id == config_id
    ).order_by(ApprovalWorkflow.step_order).all()
    
    return [
        {
            "step_name": w.step_name,
            "step_order": w.step_order,
            "status": w.approval_status,
            "approver": w.approver_id,
            "approval_date": w.approval_date.isoformat() if w.approval_date else None,
            "comments": w.comments
        } for w in workflows
    ]

# =====================================================
# QUOTE GENERATION ENDPOINTS
# =====================================================

@router.get("/configurations/{config_id}/quote")
async def generate_quote(
    config_id: UUID,
    db: Session = Depends(get_db)
):
    """Generate quote document"""
    try:
        engine = PricingEngine(db)
        quote = engine.generate_quote_document(config_id)
        return quote
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/configurations/{config_id}/quote/pdf")
async def download_quote_pdf(
    config_id: UUID,
    db: Session = Depends(get_db)
):
    """Download quote as PDF (placeholder - implement PDF generation)"""
    # This would integrate with a PDF generation service
    # For now, return JSON as placeholder
    
    try:
        engine = PricingEngine(db)
        quote = engine.generate_quote_document(config_id)
        
        # TODO: Implement actual PDF generation
        # pdf_bytes = generate_pdf_from_quote(quote)
        
        # For now, return JSON
        import json
        json_bytes = json.dumps(quote, indent=2, default=str).encode()
        
        return StreamingResponse(
            io.BytesIO(json_bytes),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=quote_{config_id}.json"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =====================================================
# WEBSOCKET FOR REAL-TIME UPDATES
# =====================================================

from fastapi import WebSocket, WebSocketDisconnect
from typing import Set
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[UUID, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, config_id: UUID):
        await websocket.accept()
        if config_id not in self.active_connections:
            self.active_connections[config_id] = set()
        self.active_connections[config_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, config_id: UUID):
        if config_id in self.active_connections:
            self.active_connections[config_id].discard(websocket)
            if not self.active_connections[config_id]:
                del self.active_connections[config_id]
    
    async def send_update(self, config_id: UUID, message: dict):
        if config_id in self.active_connections:
            for connection in self.active_connections[config_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass

manager = ConnectionManager()

@router.websocket("/configurations/{config_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    config_id: UUID,
    db: Session = Depends(get_db)
):
    """WebSocket for real-time configuration updates"""
    await manager.connect(websocket, config_id)
    
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "calculate":
                # Perform real-time calculation
                engine = PricingEngine(db)
                result = engine.calculate_premium(config_id, save_calculation=False)
                
                # Send update to all connected clients
                await manager.send_update(config_id, {
                    "type": "premium_update",
                    "data": result["premium_breakdown"]
                })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, config_id)