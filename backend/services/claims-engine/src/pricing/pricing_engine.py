"""
Pricing Engine Service
Core business logic for group health insurance pricing and premium calculations
"""

import logging
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID

from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session, joinedload

from .models import (
    PolicyConfig, ProductTemplate, BenefitSelection, PolicyTCSelection,
    TCFactorConfig, TCFactorOption, PolicyMember, PolicyBenefitOverride,
    PremiumCalculationLog, ApprovalWorkflow, RateTable, AgeBandMultiplier,
    PolicyStatus, PricingMethod, BenefitCategory, Gender, MemberType
)

logger = logging.getLogger(__name__)

class PricingEngine:
    """
    Main pricing engine for group health insurance
    Handles premium calculations, factor applications, and configuration management
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.calculation_cache = {}
        
    # =====================================================
    # CONFIGURATION CREATION & MANAGEMENT
    # =====================================================
    
    def create_policy_configuration(
        self,
        company_name: str,
        participant_count: int,
        coverage_start: date,
        coverage_end: date,
        pricing_method: str = PricingMethod.FULLY_EXPERIENCED,
        **kwargs
    ) -> PolicyConfig:
        """Create a new policy configuration"""
        
        # Generate quote number
        quote_number = self._generate_quote_number()
        
        config = PolicyConfig(
            quote_number=quote_number,
            company_name=company_name,
            participant_count=participant_count,
            coverage_start=coverage_start,
            coverage_end=coverage_end,
            pricing_method=pricing_method,
            status=PolicyStatus.DRAFT,
            **kwargs
        )
        
        self.session.add(config)
        
        # Initialize default benefit categories
        self._initialize_default_benefits(config)
        
        # Initialize default TC factors
        self._initialize_default_tc_factors(config)
        
        self.session.commit()
        
        logger.info(f"Created policy configuration {quote_number} for {company_name}")
        return config
    
    def _generate_quote_number(self) -> str:
        """Generate unique quote number"""
        today = datetime.now()
        prefix = f"Q{today.strftime('%Y%m%d')}"
        
        # Get count of quotes today
        count = self.session.query(PolicyConfig).filter(
            PolicyConfig.quote_number.like(f"{prefix}%")
        ).count()
        
        return f"{prefix}{count + 1:04d}"
    
    def _initialize_default_benefits(self, config: PolicyConfig):
        """Initialize benefit categories with defaults"""
        templates = self.session.query(ProductTemplate).filter(
            ProductTemplate.effective_from <= config.coverage_start,
            or_(
                ProductTemplate.effective_to.is_(None),
                ProductTemplate.effective_to >= config.coverage_start
            )
        ).all()
        
        # Group templates by category
        template_map = {t.product_category: t for t in templates}
        
        # Create benefit selections
        for category in BenefitCategory:
            template = template_map.get(category.value)
            
            selection = BenefitSelection(
                config_id=config.config_id,
                benefit_category=category.value,
                template_id=template.template_id if template else None,
                is_selected=category in [BenefitCategory.INPATIENT, BenefitCategory.OUTPATIENT],
                category_factor=Decimal('1.000')
            )
            self.session.add(selection)
    
    def _initialize_default_tc_factors(self, config: PolicyConfig):
        """Initialize TC factors with default selections"""
        factors = self.session.query(TCFactorConfig).filter(
            TCFactorConfig.is_active == True
        ).options(joinedload(TCFactorConfig.options)).all()
        
        for factor in factors:
            # Find default option
            default_option = next(
                (opt for opt in factor.options if opt.is_default), 
                factor.options[0] if factor.options else None
            )
            
            if default_option:
                selection = PolicyTCSelection(
                    config_id=config.config_id,
                    factor_id=factor.factor_id,
                    option_id=default_option.option_id,
                    applied_multiplier=default_option.multiplier
                )
                self.session.add(selection)
    
    # =====================================================
    # BENEFIT CONFIGURATION
    # =====================================================
    
    def toggle_benefit_category(
        self, 
        config_id: UUID, 
        category: BenefitCategory, 
        is_selected: bool
    ) -> BenefitSelection:
        """Toggle a benefit category on/off"""
        selection = self.session.query(BenefitSelection).filter(
            BenefitSelection.config_id == config_id,
            BenefitSelection.benefit_category == category.value
        ).first()
        
        if selection:
            selection.is_selected = is_selected
            
            # Update category factor based on selection
            if is_selected:
                selection.category_factor = self._calculate_category_factor(
                    config_id, category
                )
            else:
                selection.category_factor = Decimal('1.000')
        
        self.session.commit()
        return selection
    
    def update_benefit_limit(
        self,
        config_id: UUID,
        benefit_code: str,
        new_limit: Decimal,
        reason: str = None
    ) -> PolicyBenefitOverride:
        """Override a specific benefit limit"""
        
        # Get original limit from template/rate table
        original = self._get_original_benefit_limit(benefit_code)
        
        override = self.session.query(PolicyBenefitOverride).filter(
            PolicyBenefitOverride.config_id == config_id,
            PolicyBenefitOverride.benefit_code == benefit_code
        ).first()
        
        if not override:
            override = PolicyBenefitOverride(
                config_id=config_id,
                benefit_code=benefit_code,
                original_limit=original
            )
            self.session.add(override)
        
        override.override_limit = new_limit
        override.override_reason = reason
        
        self.session.commit()
        return override
    
    def _calculate_category_factor(
        self, 
        config_id: UUID, 
        category: BenefitCategory
    ) -> Decimal:
        """Calculate factor for a benefit category based on configuration"""
        
        config = self.session.query(PolicyConfig).get(config_id)
        base_factor = Decimal('1.000')
        
        # Apply participant count factor
        if config.participant_count < 15:
            base_factor *= Decimal('1.500')  # Small group loading
        elif config.participant_count < 25:
            base_factor *= Decimal('1.250')
        elif config.participant_count < 50:
            base_factor *= Decimal('1.100')
        
        # Category-specific adjustments
        if category == BenefitCategory.MATERNITY:
            # Check demographic mix
            female_count = self.session.query(PolicyMember).filter(
                PolicyMember.config_id == config_id,
                PolicyMember.gender == Gender.FEMALE,
                PolicyMember.age >= 18,
                PolicyMember.age <= 45
            ).count()
            
            if female_count > config.participant_count * 0.4:
                base_factor *= Decimal('1.150')  # Higher maternity risk
        
        return base_factor
    
    def _get_original_benefit_limit(self, benefit_code: str) -> Decimal:
        """Get original benefit limit from rate table"""
        rate = self.session.query(RateTable).filter(
            RateTable.benefit_code == benefit_code,
            RateTable.effective_date <= date.today()
        ).order_by(RateTable.effective_date.desc()).first()
        
        # This would need mapping based on benefit type
        # For now, return a default
        return Decimal('0')
    
    # =====================================================
    # TC FACTOR MANAGEMENT
    # =====================================================
    
    def update_tc_factor(
        self,
        config_id: UUID,
        factor_code: str,
        option_value: str
    ) -> PolicyTCSelection:
        """Update a TC factor selection"""
        
        # Get factor and option
        factor = self.session.query(TCFactorConfig).filter(
            TCFactorConfig.factor_code == factor_code
        ).first()
        
        if not factor:
            raise ValueError(f"Invalid factor code: {factor_code}")
        
        option = self.session.query(TCFactorOption).filter(
            TCFactorOption.factor_id == factor.factor_id,
            TCFactorOption.option_value == option_value
        ).first()
        
        if not option:
            raise ValueError(f"Invalid option value: {option_value}")
        
        # Check participant-based constraints
        config = self.session.query(PolicyConfig).get(config_id)
        
        if option.min_participants and config.participant_count < option.min_participants:
            raise ValueError(f"Minimum {option.min_participants} participants required")
        
        if option.max_participants and config.participant_count > option.max_participants:
            raise ValueError(f"Maximum {option.max_participants} participants allowed")
        
        # Update or create selection
        selection = self.session.query(PolicyTCSelection).filter(
            PolicyTCSelection.config_id == config_id,
            PolicyTCSelection.factor_id == factor.factor_id
        ).first()
        
        if not selection:
            selection = PolicyTCSelection(
                config_id=config_id,
                factor_id=factor.factor_id
            )
            self.session.add(selection)
        
        selection.option_id = option.option_id
        selection.applied_multiplier = option.multiplier
        
        self.session.commit()
        return selection
    
    def get_applicable_tc_options(
        self, 
        config_id: UUID, 
        factor_code: str
    ) -> List[TCFactorOption]:
        """Get applicable TC options based on configuration"""
        
        config = self.session.query(PolicyConfig).get(config_id)
        factor = self.session.query(TCFactorConfig).filter(
            TCFactorConfig.factor_code == factor_code
        ).first()
        
        if not factor:
            return []
        
        # Filter options based on participant count
        options = self.session.query(TCFactorOption).filter(
            TCFactorOption.factor_id == factor.factor_id,
            or_(
                TCFactorOption.min_participants.is_(None),
                TCFactorOption.min_participants <= config.participant_count
            ),
            or_(
                TCFactorOption.max_participants.is_(None),
                TCFactorOption.max_participants >= config.participant_count
            )
        ).order_by(TCFactorOption.display_order).all()
        
        return options
    
    # =====================================================
    # MEMBER MANAGEMENT
    # =====================================================
    
    def add_member(
        self,
        config_id: UUID,
        full_name: str,
        date_of_birth: date,
        gender: str,
        member_type: str,
        **kwargs
    ) -> PolicyMember:
        """Add a member to the policy configuration"""
        
        # Get next member number
        max_number = self.session.query(func.max(PolicyMember.member_number)).filter(
            PolicyMember.config_id == config_id
        ).scalar() or 0
        
        member = PolicyMember(
            config_id=config_id,
            member_number=max_number + 1,
            full_name=full_name,
            date_of_birth=date_of_birth,
            gender=gender,
            member_type=member_type,
            status='ACTIVE',
            enrollment_date=date.today(),
            **kwargs
        )
        
        # Calculate age band
        member.age_band = member.get_age_band()
        
        # Calculate initial premium
        member.base_premium = member.calculate_base_premium(self.session)
        
        self.session.add(member)
        
        # Update participant count
        config = self.session.query(PolicyConfig).get(config_id)
        config.participant_count = self.session.query(PolicyMember).filter(
            PolicyMember.config_id == config_id,
            PolicyMember.status == 'ACTIVE'
        ).count()
        
        self.session.commit()
        return member
    
    def import_members_from_excel(
        self, 
        config_id: UUID, 
        excel_data: List[Dict[str, Any]]
    ) -> Tuple[List[PolicyMember], List[Dict[str, str]]]:
        """Import members from Excel data"""
        
        members = []
        errors = []
        
        for idx, row in enumerate(excel_data, start=1):
            try:
                member = self.add_member(
                    config_id=config_id,
                    full_name=row['full_name'],
                    date_of_birth=row['date_of_birth'],
                    gender=row['gender'].upper(),
                    member_type=row['member_type'].upper(),
                    relationship=row.get('relationship'),
                    class_code=row.get('class_code', '1')
                )
                members.append(member)
                
            except Exception as e:
                errors.append({
                    'row': idx,
                    'error': str(e),
                    'data': row
                })
                logger.error(f"Error importing member row {idx}: {e}")
        
        self.session.commit()
        return members, errors
    
    # =====================================================
    # PREMIUM CALCULATION
    # =====================================================
    
    def calculate_premium(
        self, 
        config_id: UUID,
        save_calculation: bool = True
    ) -> Dict[str, Any]:
        """
        Main premium calculation method
        Calculates total premium based on members, benefits, and factors
        """
        
        config = self.session.query(PolicyConfig).options(
            joinedload(PolicyConfig.members),
            joinedload(PolicyConfig.benefit_selections),
            joinedload(PolicyConfig.tc_selections)
        ).get(config_id)
        
        if not config:
            raise ValueError(f"Configuration {config_id} not found")
        
        # Step 1: Calculate base premium for all members
        base_premium_total = Decimal('0')
        member_details = []
        
        for member in config.members:
            if member.status != 'ACTIVE':
                continue
                
            member_base = self._calculate_member_premium(member, config)
            base_premium_total += member_base
            
            member_details.append({
                'member_id': str(member.member_id),
                'name': member.full_name,
                'age': member.age,
                'gender': member.gender,
                'base_premium': float(member_base)
            })
        
        # Step 2: Calculate total factor multiplier
        factor_breakdown = self._calculate_factor_breakdown(config)
        total_multiplier = factor_breakdown['total_multiplier']
        
        # Step 3: Calculate adjusted premium
        adjusted_premium = base_premium_total * total_multiplier
        
        # Step 4: Add administrative fees
        admin_fee = self._calculate_admin_fee(config, adjusted_premium)
        tpa_fee = self._calculate_tpa_fee(config, adjusted_premium)
        
        # Step 5: Calculate final premium
        total_premium = adjusted_premium + admin_fee + tpa_fee
        
        # Round to 2 decimal places
        total_premium = total_premium.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Step 6: Update configuration
        config.total_base_premium = base_premium_total
        config.total_factor_multiplier = total_multiplier
        config.total_adjusted_premium = adjusted_premium
        
        # Step 7: Create calculation result
        result = {
            'config_id': str(config_id),
            'calculation_date': datetime.now().isoformat(),
            'company_name': config.company_name,
            'participant_count': config.participant_count,
            'coverage_period': {
                'start': config.coverage_start.isoformat(),
                'end': config.coverage_end.isoformat(),
                'days': config.coverage_days
            },
            'premium_breakdown': {
                'base_premium': float(base_premium_total),
                'total_multiplier': float(total_multiplier),
                'adjusted_premium': float(adjusted_premium),
                'admin_fee': float(admin_fee),
                'tpa_fee': float(tpa_fee),
                'total_premium': float(total_premium)
            },
            'monthly_premium': float(total_premium / 12),
            'per_member_average': float(total_premium / config.participant_count) if config.participant_count > 0 else 0,
            'factor_breakdown': factor_breakdown,
            'member_details': member_details
        }
        
        # Step 8: Save calculation log
        if save_calculation:
            self._save_calculation_log(config, result)
        
        self.session.commit()
        return result
    
    def _calculate_member_premium(
        self, 
        member: PolicyMember, 
        config: PolicyConfig
    ) -> Decimal:
        """Calculate premium for a single member"""
        
        premium = Decimal('0')
        
        # Get selected benefits
        for selection in config.benefit_selections:
            if not selection.is_selected or not selection.template:
                continue
            
            # Get base rate from template
            if member.age < 18:
                base_rate = selection.template.base_premium_child or Decimal('0')
            elif member.gender == Gender.MALE:
                base_rate = selection.template.base_premium_adult_male or Decimal('0')
            else:
                base_rate = selection.template.base_premium_adult_female or Decimal('0')
            
            # Apply age band multiplier
            age_multiplier = self._get_age_band_multiplier(
                selection.template_id, 
                member.age, 
                member.gender
            )
            
            premium += base_rate * age_multiplier
        
        # Store in member record
        member.base_premium = premium
        
        return premium
    
    def _get_age_band_multiplier(
        self, 
        template_id: UUID, 
        age: int, 
        gender: str
    ) -> Decimal:
        """Get age band multiplier for premium calculation"""
        
        multiplier = self.session.query(AgeBandMultiplier).filter(
            AgeBandMultiplier.template_id == template_id,
            AgeBandMultiplier.age_from <= age,
            AgeBandMultiplier.age_to >= age,
            AgeBandMultiplier.gender == (gender if age >= 18 else 'CHILD')
        ).first()
        
        return multiplier.multiplier if multiplier else Decimal('1.000')
    
    def _calculate_factor_breakdown(self, config: PolicyConfig) -> Dict[str, Any]:
        """Calculate detailed factor breakdown"""
        
        factors = {
            'benefit_factors': {},
            'tc_factors': {},
            'total_multiplier': Decimal('1.000')
        }
        
        # Benefit category factors
        for selection in config.benefit_selections:
            if selection.is_selected:
                factors['benefit_factors'][selection.benefit_category] = float(selection.category_factor)
                factors['total_multiplier'] *= selection.category_factor
        
        # TC factors
        for tc_selection in config.tc_selections:
            if tc_selection.factor and tc_selection.option:
                factors['tc_factors'][tc_selection.factor.factor_code] = {
                    'name': tc_selection.factor.factor_name,
                    'option': tc_selection.option.option_label,
                    'multiplier': float(tc_selection.applied_multiplier)
                }
                factors['total_multiplier'] *= tc_selection.applied_multiplier
        
        return factors
    
    def _calculate_admin_fee(
        self, 
        config: PolicyConfig, 
        premium: Decimal
    ) -> Decimal:
        """Calculate administrative fee"""
        
        # Base admin fee
        base_fee = Decimal('100000')  # Rp 100,000 base
        
        # Percentage of premium (e.g., 5%)
        percentage_fee = premium * Decimal('0.05')
        
        # Use higher of the two
        return max(base_fee, percentage_fee)
    
    def _calculate_tpa_fee(
        self, 
        config: PolicyConfig, 
        premium: Decimal
    ) -> Decimal:
        """Calculate TPA (Third Party Administrator) fee"""
        
        # Per member fee
        per_member_fee = Decimal('10000') * config.participant_count
        
        # Minimum fee
        min_fee = Decimal('100000')
        
        return max(per_member_fee, min_fee)
    
    def _save_calculation_log(
        self, 
        config: PolicyConfig, 
        result: Dict[str, Any]
    ):
        """Save calculation to audit log"""
        
        log = PremiumCalculationLog(
            config_id=config.config_id,
            participant_count=config.participant_count,
            selected_benefits={
                s.benefit_category: s.is_selected 
                for s in config.benefit_selections
            },
            selected_factors={
                tc.factor.factor_code: tc.option.option_value 
                for tc in config.tc_selections 
                if tc.factor and tc.option
            },
            base_premium_total=Decimal(str(result['premium_breakdown']['base_premium'])),
            factor_details=result['factor_breakdown'],
            total_multiplier=Decimal(str(result['premium_breakdown']['total_multiplier'])),
            monthly_premium=Decimal(str(result['monthly_premium'])),
            annual_premium=Decimal(str(result['premium_breakdown']['total_premium'])),
            admin_fee=Decimal(str(result['premium_breakdown']['admin_fee'])),
            tpa_fee=Decimal(str(result['premium_breakdown']['tpa_fee'])),
            total_premium=Decimal(str(result['premium_breakdown']['total_premium']))
        )
        
        self.session.add(log)
    
    # =====================================================
    # APPROVAL WORKFLOW
    # =====================================================
    
    def submit_for_approval(
        self, 
        config_id: UUID, 
        submitted_by: str
    ) -> PolicyConfig:
        """Submit configuration for approval"""
        
        config = self.session.query(PolicyConfig).get(config_id)
        
        if config.status != PolicyStatus.DRAFT:
            raise ValueError(f"Only draft configurations can be submitted for approval")
        
        # Validate configuration
        self._validate_configuration(config)
        
        # Calculate premium
        self.calculate_premium(config_id)
        
        # Update status
        config.status = PolicyStatus.QUOTED
        
        # Create approval workflow steps
        self._create_approval_workflow(config)
        
        self.session.commit()
        
        logger.info(f"Configuration {config.quote_number} submitted for approval by {submitted_by}")
        return config
    
    def _validate_configuration(self, config: PolicyConfig):
        """Validate configuration before submission"""
        
        # Check minimum requirements
        if config.participant_count < 5:
            raise ValueError("Minimum 5 participants required")
        
        # Check at least one benefit selected
        has_benefits = any(
            s.is_selected for s in config.benefit_selections
        )
        if not has_benefits:
            raise ValueError("At least one benefit must be selected")
        
        # Check members enrolled
        member_count = self.session.query(PolicyMember).filter(
            PolicyMember.config_id == config.config_id,
            PolicyMember.status == 'ACTIVE'
        ).count()
        
        if member_count == 0:
            raise ValueError("No members enrolled")
    
    def _create_approval_workflow(self, config: PolicyConfig):
        """Create approval workflow steps"""
        
        steps = [
            ('UNDERWRITING', 1, Decimal('1000000')),
            ('ACTUARIAL', 2, Decimal('5000000')),
            ('MANAGEMENT', 3, Decimal('10000000'))
        ]
        
        for step_name, step_order, threshold in steps:
            if config.total_adjusted_premium and config.total_adjusted_premium >= threshold:
                workflow = ApprovalWorkflow(
                    config_id=config.config_id,
                    step_name=step_name,
                    step_order=step_order,
                    approval_status='PENDING',
                    min_premium_threshold=threshold
                )
                self.session.add(workflow)
    
    def approve_configuration(
        self,
        config_id: UUID,
        approver_id: str,
        step_name: str,
        comments: str = None
    ) -> PolicyConfig:
        """Approve a configuration step"""
        
        workflow = self.session.query(ApprovalWorkflow).filter(
            ApprovalWorkflow.config_id == config_id,
            ApprovalWorkflow.step_name == step_name
        ).first()
        
        if not workflow:
            raise ValueError(f"No approval workflow found for step {step_name}")
        
        if workflow.approval_status != 'PENDING':
            raise ValueError(f"Step {step_name} already processed")
        
        # Update workflow
        workflow.approver_id = approver_id
        workflow.approval_status = 'APPROVED'
        workflow.approval_date = datetime.now()
        workflow.comments = comments
        
        # Check if all steps approved
        pending_count = self.session.query(ApprovalWorkflow).filter(
            ApprovalWorkflow.config_id == config_id,
            ApprovalWorkflow.approval_status == 'PENDING'
        ).count()
        
        config = self.session.query(PolicyConfig).get(config_id)
        
        if pending_count == 0:
            # All approved - update config status
            config.status = PolicyStatus.APPROVED
            config.approved_by = approver_id
            config.approved_at = datetime.now()
            
            # Generate policy number
            config.policy_number = self._generate_policy_number()
        
        self.session.commit()
        return config
    
    def _generate_policy_number(self) -> str:
        """Generate unique policy number"""
        today = datetime.now()
        prefix = f"PGH{today.strftime('%Y%m')}"
        
        count = self.session.query(PolicyConfig).filter(
            PolicyConfig.policy_number.like(f"{prefix}%")
        ).count()
        
        return f"{prefix}{count + 1:05d}"
    
    # =====================================================
    # REPORTING & ANALYTICS
    # =====================================================
    
    def get_calculation_history(
        self, 
        config_id: UUID, 
        limit: int = 10
    ) -> List[PremiumCalculationLog]:
        """Get calculation history for a configuration"""
        
        calculations = self.session.query(PremiumCalculationLog).filter(
            PremiumCalculationLog.config_id == config_id
        ).order_by(
            PremiumCalculationLog.calculation_timestamp.desc()
        ).limit(limit).all()
        
        return calculations
    
    def generate_quote_document(self, config_id: UUID) -> Dict[str, Any]:
        """Generate quote document data"""
        
        config = self.session.query(PolicyConfig).options(
            joinedload(PolicyConfig.members),
            joinedload(PolicyConfig.benefit_selections),
            joinedload(PolicyConfig.tc_selections),
            joinedload(PolicyConfig.benefit_overrides)
        ).get(config_id)
        
        if not config:
            raise ValueError(f"Configuration {config_id} not found")
        
        # Calculate current premium
        premium_data = self.calculate_premium(config_id, save_calculation=False)
        
        # Build quote document structure
        quote = {
            'quote_number': config.quote_number,
            'quote_date': datetime.now().isoformat(),
            'valid_until': (datetime.now() + timedelta(days=30)).isoformat(),
            'company_details': {
                'name': config.company_name,
                'industry': config.industry_type,
                'participant_count': config.participant_count
            },
            'coverage_period': {
                'start': config.coverage_start.isoformat(),
                'end': config.coverage_end.isoformat()
            },
            'benefits': self._format_benefits_for_quote(config),
            'premium': premium_data['premium_breakdown'],
            'terms_conditions': self._format_tc_for_quote(config),
            'member_summary': self._generate_member_summary(config)
        }
        
        return quote
    
    def _format_benefits_for_quote(self, config: PolicyConfig) -> List[Dict[str, Any]]:
        """Format benefits for quote document"""
        benefits = []
        
        for selection in config.benefit_selections:
            if selection.is_selected:
                benefit_data = {
                    'category': selection.benefit_category,
                    'included': True,
                    'limits': []
                }
                
                # Add benefit-specific limits
                overrides = [
                    o for o in config.benefit_overrides 
                    if o.benefit_code.startswith(selection.benefit_category[:2])
                ]
                
                for override in overrides:
                    benefit_data['limits'].append({
                        'code': override.benefit_code,
                        'name': override.benefit_name,
                        'limit': float(override.override_limit or override.original_limit),
                        'type': override.limit_type
                    })
                
                benefits.append(benefit_data)
        
        return benefits
    
    def _format_tc_for_quote(self, config: PolicyConfig) -> List[Dict[str, Any]]:
        """Format terms & conditions for quote"""
        tc_items = []
        
        for tc_selection in config.tc_selections:
            if tc_selection.factor and tc_selection.option:
                tc_items.append({
                    'category': tc_selection.factor.factor_category,
                    'name': tc_selection.factor.factor_name,
                    'selected_option': tc_selection.option.option_label,
                    'impact': f"{((tc_selection.applied_multiplier - 1) * 100):.1f}%" 
                              if tc_selection.applied_multiplier != Decimal('1.000') else "No impact"
                })
        
        return tc_items
    
    def _generate_member_summary(self, config: PolicyConfig) -> Dict[str, Any]:
        """Generate member demographic summary"""
        
        members = config.members
        active_members = [m for m in members if m.status == 'ACTIVE']
        
        summary = {
            'total_count': len(active_members),
            'by_type': {},
            'by_gender': {},
            'by_age_band': {},
            'average_age': 0
        }
        
        # Count by type
        for member_type in MemberType:
            count = len([m for m in active_members if m.member_type == member_type.value])
            if count > 0:
                summary['by_type'][member_type.value] = count
        
        # Count by gender
        for gender in [Gender.MALE, Gender.FEMALE]:
            count = len([m for m in active_members if m.gender == gender.value])
            if count > 0:
                summary['by_gender'][gender.value] = count
        
        # Count by age band
        age_bands = {}
        total_age = 0
        for member in active_members:
            band = member.get_age_band()
            age_bands[band] = age_bands.get(band, 0) + 1
            total_age += member.age
        
        summary['by_age_band'] = age_bands
        summary['average_age'] = round(total_age / len(active_members)) if active_members else 0
        
        return summary

from datetime import timedelta  # Add this import at the top