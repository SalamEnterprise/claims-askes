# Claims — Outpatient Servicing Flow & Operations (v0.1)

**Purpose**: Complete outpatient journey from registration through treatment, auxiliary services, pharmacy, and payment
**Date**: 2025-08-14
**Owner**: Medical Affairs & Operations
**Status**: Initial Design

---

## 1. EXECUTIVE SUMMARY

Outpatient services represent 60-70% of claim volume and require seamless coordination between members, providers, and payers. This document defines the complete outpatient servicing flow with real-time eligibility, authorization, and payment processes.

---

## 2. OUTPATIENT SERVICE CATEGORIES

### 2.1 Service Types
```yaml
Outpatient_Services:
  Consultations:
    - Primary care visits
    - Specialist consultations
    - Follow-up visits
    - Preventive care
    - Telemedicine consultations
    
  Diagnostics:
    - Laboratory tests
    - Radiology/Imaging
    - Pathology
    - Cardiac diagnostics
    - Neurological tests
    
  Procedures:
    - Minor surgery
    - Endoscopy
    - Wound care
    - Injections
    - Physiotherapy
    
  Emergency:
    - Emergency room (non-admission)
    - Urgent care
    - After-hours clinic
    
  Wellness:
    - Health screening
    - Vaccination
    - Health education
    - Nutrition counseling
```

---

## 3. PRE-VISIT PHASE

### 3.1 Appointment Scheduling
```yaml
Scheduling_Flow:
  Member_Initiated:
    1. Search providers (specialty, location, availability)
    2. Check provider network status
    3. View quality ratings and reviews
    4. Select appointment slot
    5. Receive confirmation with pre-visit instructions
    
  Provider_Initiated:
    1. Verify member eligibility
    2. Check benefit coverage
    3. Schedule appointment
    4. Send reminder to member
```

### 3.2 Pre-Registration & Eligibility
```sql
-- Real-time eligibility check
CREATE TABLE outpatient.eligibility_check (
    check_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id UUID NOT NULL,
    provider_id UUID NOT NULL,
    service_date DATE NOT NULL,
    service_types TEXT[],
    eligibility_status VARCHAR(50),
    benefits_summary JSONB,
    copay_amount DECIMAL(12,2),
    deductible_remaining DECIMAL(12,2),
    out_of_pocket_remaining DECIMAL(12,2),
    preauth_required BOOLEAN,
    referral_required BOOLEAN,
    checked_at TIMESTAMPTZ DEFAULT NOW(),
    valid_until TIMESTAMPTZ
);

-- Pre-visit requirements
CREATE TABLE outpatient.previsit_requirement (
    requirement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    appointment_id UUID NOT NULL,
    requirement_type VARCHAR(50), -- lab_fasting, documents, referral
    description TEXT,
    completed BOOLEAN DEFAULT false,
    completed_at TIMESTAMPTZ
);
```

### 3.3 Pre-Authorization for Outpatient
```python
def check_outpatient_preauth_requirement(service_codes, diagnosis_codes, member_plan):
    """
    Determine if pre-authorization required for outpatient services
    """
    preauth_rules = get_plan_preauth_rules(member_plan)
    
    requires_auth = []
    auto_approved = []
    
    for service in service_codes:
        if service in preauth_rules.always_required:
            requires_auth.append(service)
        elif meets_auto_approval_criteria(service, diagnosis_codes):
            auto_approved.append(service)
        else:
            requires_auth.append(service)
    
    return {
        'requires_auth': requires_auth,
        'auto_approved': auto_approved,
        'auth_timeline': get_auth_timeline(requires_auth)
    }
```

---

## 4. REGISTRATION & CHECK-IN

### 4.1 Member Verification
```yaml
Verification_Process:
  Identity_Verification:
    - Biometric (fingerprint/face)
    - OTP verification
    - Physical card + ID
    - QR code from mobile app
    
  Coverage_Verification:
    - Active membership status
    - Benefit plan details
    - Remaining limits
    - Exclusions/waiting periods
    
  Financial_Verification:
    - Outstanding balances
    - Payment history
    - Copay collection
    - Deposit requirements
```

### 4.2 Digital Check-In Process
```sql
CREATE TABLE outpatient.visit_registration (
    registration_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    appointment_id UUID,
    member_id UUID NOT NULL,
    provider_id UUID NOT NULL,
    location_id UUID NOT NULL,
    check_in_time TIMESTAMPTZ DEFAULT NOW(),
    check_in_method VARCHAR(50), -- kiosk, mobile, desk
    verification_method VARCHAR(50),
    eligibility_verified BOOLEAN,
    copay_collected DECIMAL(12,2),
    consent_signed BOOLEAN,
    forms_completed JSONB,
    queue_number VARCHAR(20),
    estimated_wait_minutes INTEGER,
    triage_level VARCHAR(20)
);
```

---

## 5. CONSULTATION PHASE

### 5.1 Provider Workflow
```yaml
Consultation_Process:
  Pre_Consultation:
    - Review member history
    - Check allergies/medications
    - Review referral/preauth
    - Access clinical guidelines
    
  During_Consultation:
    - Document chief complaint
    - Perform examination
    - Order diagnostics
    - Prescribe medications
    - Plan follow-up
    
  Service_Documentation:
    - Diagnosis codes (ICD-10)
    - Procedure codes
    - Time spent
    - Clinical notes
```

### 5.2 Real-Time Service Authorization
```sql
CREATE TABLE outpatient.service_authorization (
    auth_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    visit_id UUID NOT NULL,
    service_code VARCHAR(50),
    service_description TEXT,
    quantity INTEGER,
    diagnosis_codes TEXT[],
    clinical_justification TEXT,
    auth_status VARCHAR(50), -- approved, denied, pending_review
    auth_response_time_ms INTEGER,
    approved_amount DECIMAL(12,2),
    member_liability DECIMAL(12,2),
    auth_number VARCHAR(50),
    valid_through DATE,
    limitations TEXT
);
```

### 5.3 Point-of-Care Decision Support
```python
def provide_clinical_decision_support(diagnosis, member_history):
    """
    Real-time clinical guidelines and cost-effective alternatives
    """
    guidelines = get_clinical_guidelines(diagnosis)
    formulary = get_formulary_preferences(member.plan_id)
    
    recommendations = {
        'preferred_medications': formulary.get_preferred_drugs(diagnosis),
        'diagnostic_guidelines': guidelines.recommended_tests,
        'preventive_care_gaps': identify_care_gaps(member_history),
        'cost_effective_alternatives': suggest_alternatives(planned_services),
        'quality_measures': applicable_quality_metrics(diagnosis)
    }
    
    return recommendations
```

---

## 6. DIAGNOSTIC SERVICES

### 6.1 Laboratory Services
```yaml
Lab_Service_Flow:
  Order_Creation:
    - Provider places lab order
    - Check medical necessity
    - Verify coverage
    - Generate lab requisition
    
  Sample_Collection:
    - Patient registration at lab
    - Verify fasting/prep requirements
    - Collect samples
    - Chain of custody tracking
    
  Processing:
    - Sample processing
    - Quality control
    - Result generation
    - Abnormal value flagging
    
  Result_Distribution:
    - Provider notification
    - Member portal access
    - Auto-interpretation where applicable
    - Follow-up action triggers
```

### 6.2 Radiology & Imaging
```sql
CREATE TABLE outpatient.imaging_order (
    order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    visit_id UUID,
    member_id UUID NOT NULL,
    ordering_provider_id UUID NOT NULL,
    imaging_type VARCHAR(100),
    body_part VARCHAR(100),
    clinical_indication TEXT,
    urgency VARCHAR(20), -- routine, urgent, stat
    contrast_required BOOLEAN,
    authorization_status VARCHAR(50),
    scheduled_datetime TIMESTAMPTZ,
    performed_datetime TIMESTAMPTZ,
    technician_id UUID,
    radiologist_id UUID,
    report_status VARCHAR(50),
    critical_findings BOOLEAN DEFAULT false
);

CREATE TABLE outpatient.imaging_result (
    result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES outpatient.imaging_order,
    images_count INTEGER,
    pacs_reference VARCHAR(200),
    findings TEXT,
    impression TEXT,
    recommendations TEXT,
    reported_by UUID,
    reported_at TIMESTAMPTZ,
    addendum TEXT,
    peer_review_required BOOLEAN
);
```

### 6.3 Laboratory Integration
```python
def process_lab_order(order_details, member_id, provider_id):
    """
    Process laboratory order with automatic authorization
    """
    # Check if tests require pre-authorization
    auth_required = check_lab_preauth(order_details.test_codes)
    
    if auth_required:
        auth_result = request_lab_authorization(
            test_codes=order_details.test_codes,
            diagnosis=order_details.diagnosis,
            clinical_notes=order_details.justification
        )
    else:
        auth_result = auto_approve_routine_labs(order_details)
    
    # Create lab order
    lab_order = create_lab_requisition(
        member_id=member_id,
        provider_id=provider_id,
        tests=order_details.test_codes,
        authorization=auth_result.auth_number
    )
    
    # Send to preferred lab
    route_to_network_lab(lab_order, member.preferred_lab)
    
    return lab_order
```

---

## 7. PHARMACY SERVICES

### 7.1 E-Prescribing Integration
```yaml
E_Prescribing_Flow:
  Prescription_Creation:
    - Drug selection with formulary check
    - Dosage calculation
    - Drug-drug interaction check
    - Allergy verification
    - Generic substitution prompt
    
  Prescription_Routing:
    - Member's preferred pharmacy
    - Network pharmacy selection
    - Mail order option
    - Specialty pharmacy routing
    
  Prior_Authorization:
    - Automatic PA check
    - Clinical criteria validation
    - Alternative suggestions
    - Appeal process
```

### 7.2 Pharmacy Point-of-Sale
```sql
CREATE TABLE outpatient.pharmacy_transaction (
    transaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prescription_id UUID NOT NULL,
    member_id UUID NOT NULL,
    pharmacy_id UUID NOT NULL,
    drug_code VARCHAR(50),
    drug_name TEXT,
    quantity DECIMAL(10,2),
    days_supply INTEGER,
    unit_price DECIMAL(12,2),
    total_price DECIMAL(12,2),
    formulary_status VARCHAR(50),
    copay_amount DECIMAL(12,2),
    plan_paid DECIMAL(12,2),
    member_paid DECIMAL(12,2),
    deductible_applied DECIMAL(12,2),
    dispensed_at TIMESTAMPTZ,
    pharmacist_id UUID,
    counseling_provided BOOLEAN,
    generic_substituted BOOLEAN
);
```

### 7.3 Medication Therapy Management
```python
def medication_therapy_management(member_id):
    """
    Comprehensive medication review and optimization
    """
    medications = get_active_medications(member_id)
    medical_conditions = get_member_conditions(member_id)
    
    mtm_review = {
        'drug_interactions': check_interactions(medications),
        'duplicate_therapy': identify_duplicates(medications),
        'gaps_in_therapy': identify_missing_medications(medical_conditions),
        'adherence_issues': calculate_adherence_rates(member_id),
        'cost_optimization': suggest_generic_alternatives(medications),
        'side_effect_monitoring': flag_potential_side_effects(medications)
    }
    
    if mtm_review.has_critical_issues():
        alert_provider(member.pcp_id, mtm_review)
        alert_member(member_id, mtm_review)
    
    return mtm_review
```

---

## 8. PAYMENT & BILLING

### 8.1 Real-Time Adjudication
```yaml
Adjudication_Components:
  Benefit_Check:
    - Service coverage verification
    - Limit validation
    - Exclusion check
    - Network status
    
  Cost_Calculation:
    - Contracted rate application
    - Copay determination
    - Deductible application
    - Coinsurance calculation
    - Out-of-pocket tracking
    
  Payment_Determination:
    - Plan payment amount
    - Member responsibility
    - Provider write-off
    - COB if applicable
```

### 8.2 Payment Processing
```sql
CREATE TABLE outpatient.visit_payment (
    payment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    visit_id UUID NOT NULL,
    total_charges DECIMAL(12,2),
    allowed_amount DECIMAL(12,2),
    copay DECIMAL(12,2),
    deductible DECIMAL(12,2),
    coinsurance DECIMAL(12,2),
    plan_paid DECIMAL(12,2),
    member_responsibility DECIMAL(12,2),
    provider_adjustment DECIMAL(12,2),
    payment_status VARCHAR(50),
    payment_method VARCHAR(50),
    payment_date DATE,
    receipt_number VARCHAR(50),
    bundled_services JSONB
);
```

### 8.3 Member Cost Estimation
```python
def estimate_outpatient_costs(services, member_id, provider_id):
    """
    Pre-visit cost estimation for transparency
    """
    member_plan = get_member_plan(member_id)
    provider_contract = get_provider_rates(provider_id)
    accumulations = get_member_accumulators(member_id)
    
    estimated_costs = {}
    for service in services:
        contracted_rate = provider_contract.get_rate(service.code)
        
        cost_breakdown = {
            'service': service.description,
            'provider_charge': service.standard_charge,
            'allowed_amount': contracted_rate,
            'deductible': calculate_deductible(accumulations, contracted_rate),
            'copay': member_plan.get_copay(service.type),
            'coinsurance': calculate_coinsurance(member_plan, contracted_rate),
            'estimated_member_cost': 0,  # Sum of above
            'estimated_plan_payment': 0,
            'savings': service.standard_charge - contracted_rate
        }
        
        cost_breakdown['estimated_member_cost'] = (
            cost_breakdown['deductible'] + 
            cost_breakdown['copay'] + 
            cost_breakdown['coinsurance']
        )
        
        estimated_costs[service.code] = cost_breakdown
    
    return estimated_costs
```

---

## 9. POST-VISIT OPERATIONS

### 9.1 Follow-Up Management
```yaml
Follow_Up_Activities:
  Clinical:
    - Test result notification
    - Abnormal value alerts
    - Referral coordination
    - Next appointment scheduling
    
  Administrative:
    - Visit summary generation
    - Claim submission
    - EOB generation
    - Payment processing
    
  Care_Management:
    - Care gap closure
    - Chronic care management
    - Preventive care reminders
    - Medication adherence
```

### 9.2 Claims Processing
```sql
CREATE TABLE outpatient.claim_submission (
    claim_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    visit_id UUID NOT NULL,
    submission_method VARCHAR(50), -- real_time, batch, manual
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    claim_status VARCHAR(50),
    total_charges DECIMAL(12,2),
    diagnosis_codes TEXT[],
    procedure_codes TEXT[],
    modifiers TEXT[],
    place_of_service VARCHAR(10),
    rendering_provider_id UUID,
    referring_provider_id UUID,
    adjudicated_at TIMESTAMPTZ,
    paid_amount DECIMAL(12,2),
    denial_reasons TEXT[]
);
```

---

## 10. EMERGENCY OUTPATIENT SERVICES

### 10.1 Emergency Room (Non-Admission)
```yaml
ER_Process:
  Triage:
    - Severity assessment
    - Priority assignment
    - Initial stabilization
    
  Registration:
    - Emergency eligibility override
    - Retrospective authorization
    - Guardian consent if needed
    
  Treatment:
    - Emergency services
    - Diagnostic tests
    - Medications
    - Observation
    
  Disposition:
    - Discharge home
    - Transfer to inpatient
    - Transfer to another facility
    - Leave AMA
```

### 10.2 Urgent Care Services
```sql
CREATE TABLE outpatient.urgent_care_visit (
    visit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id UUID NOT NULL,
    facility_id UUID NOT NULL,
    arrival_time TIMESTAMPTZ,
    triage_time TIMESTAMPTZ,
    seen_by_provider_time TIMESTAMPTZ,
    discharge_time TIMESTAMPTZ,
    chief_complaint TEXT,
    triage_level INTEGER,
    diagnosis_codes TEXT[],
    procedures_performed TEXT[],
    disposition VARCHAR(50),
    follow_up_required BOOLEAN,
    total_charges DECIMAL(12,2),
    authorization_status VARCHAR(50)
);
```

---

## 11. TELEMEDICINE INTEGRATION

### 11.1 Virtual Visit Flow
```yaml
Telemedicine_Process:
  Scheduling:
    - Platform selection
    - Technology check
    - Consent collection
    
  Pre_Visit:
    - Link generation
    - Waiting room
    - Identity verification
    
  Consultation:
    - Video/audio connection
    - Screen sharing
    - Document sharing
    - E-prescribing
    
  Post_Visit:
    - Visit notes
    - Recording storage
    - Follow-up scheduling
    - Billing
```

### 11.2 Telemedicine Authorization
```python
def authorize_telemedicine_visit(member_id, provider_id, service_type):
    """
    Validate and authorize telemedicine services
    """
    # Check if service appropriate for telemedicine
    if not is_telemedicine_appropriate(service_type):
        return deny_authorization("Service requires in-person visit")
    
    # Verify provider licensed for member's location
    if not verify_interstate_license(provider_id, member.state):
        return deny_authorization("Provider not licensed in member state")
    
    # Check plan coverage for telemedicine
    coverage = check_telemedicine_coverage(member.plan_id, service_type)
    
    if coverage.covered:
        return approve_authorization(
            auth_number=generate_auth_number(),
            copay=coverage.telemedicine_copay,
            valid_for_days=1
        )
    
    return deny_authorization("Telemedicine not covered")
```

---

## 12. QUALITY & COMPLIANCE

### 12.1 Outpatient Quality Metrics
```yaml
Quality_Measures:
  Access:
    - Appointment availability
    - Wait times
    - After-hours access
    
  Care_Delivery:
    - Preventive care rates
    - Chronic care management
    - Care coordination
    
  Outcomes:
    - ER avoidance
    - Hospital admission prevention
    - Patient satisfaction
    
  Efficiency:
    - Generic prescribing rates
    - Appropriate testing
    - Network utilization
```

### 12.2 Regulatory Compliance
```sql
CREATE TABLE outpatient.compliance_tracking (
    tracking_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    visit_id UUID NOT NULL,
    compliance_type VARCHAR(100),
    requirement VARCHAR(200),
    met BOOLEAN,
    evidence TEXT,
    reviewed_by UUID,
    reviewed_at TIMESTAMPTZ
);
```

---

## 13. ANALYTICS & REPORTING

### 13.1 Outpatient KPIs
```yaml
Operational_KPIs:
  Volume:
    - Daily visit count
    - Service mix
    - Provider utilization
    
  Financial:
    - Revenue per visit
    - Collection rate
    - Denial rate
    
  Clinical:
    - Care gap closure rate
    - Readmission prevention
    - Medication adherence
    
  Member_Experience:
    - Wait times
    - Satisfaction scores
    - Portal adoption
```

### 13.2 Predictive Analytics
```python
def predict_outpatient_utilization(member_id):
    """
    Predict future outpatient service needs
    """
    features = {
        'demographics': get_member_demographics(member_id),
        'medical_history': get_medical_history(member_id),
        'current_conditions': get_active_conditions(member_id),
        'medication_adherence': calculate_adherence(member_id),
        'past_utilization': get_utilization_pattern(member_id),
        'social_determinants': get_social_factors(member_id)
    }
    
    predictions = {
        'er_risk_score': predict_er_visit(features),
        'specialist_needs': predict_specialist_referrals(features),
        'preventive_care_due': identify_preventive_gaps(features),
        'chronic_care_needs': predict_chronic_care_visits(features),
        'cost_projection': estimate_annual_costs(features)
    }
    
    return create_outreach_plan(predictions)
```

---

## 14. IMPLEMENTATION ROADMAP

### Phase 1 (Weeks 1-4): Foundation
- Database schema setup
- Basic eligibility checking
- Provider integration APIs

### Phase 2 (Weeks 5-8): Core Services  
- Consultation workflow
- Real-time authorization
- Basic pharmacy integration

### Phase 3 (Weeks 9-12): Diagnostics
- Lab order management
- Imaging workflow
- Result distribution

### Phase 4 (Weeks 13-16): Advanced Features
- Telemedicine platform
- Cost estimation tools
- Quality metrics tracking

---

**Related Documents**:
- Claims — Servicing & UM (Inpatient)
- Claims — Provider Network Management
- Claims — Data Model, APIs & Events