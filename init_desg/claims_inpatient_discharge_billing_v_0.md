# Claims — Inpatient Discharge & Billing Reconciliation (v0.1)

**Purpose**: Complete design for inpatient discharge planning, final billing, reconciliation, and payment processes
**Date**: 2025-08-14
**Owner**: Medical Affairs, Finance & Operations
**Status**: Initial Design

---

## 1. EXECUTIVE SUMMARY

Inpatient discharge and billing reconciliation is a critical junction where clinical care transitions to financial settlement. This document defines comprehensive processes for discharge planning, bill review, reconciliation, excess handling, and payment finalization while ensuring member satisfaction and cost control.

---

## 2. DISCHARGE PLANNING FRAMEWORK

### 2.1 Early Discharge Planning
```yaml
Discharge_Planning_Timeline:
  Day_0_Admission:
    - Estimated length of stay (LOS) calculation
    - Discharge needs assessment
    - Social support evaluation
    - Home environment assessment
    
  Day_1_to_N:
    - Daily discharge readiness assessment
    - Barrier identification
    - Care coordination initiation
    - Equipment/medication planning
    
  Day_Before_Discharge:
    - Final medication reconciliation
    - Follow-up appointments scheduled
    - Home health arranged if needed
    - Transportation confirmed
    
  Discharge_Day:
    - Final clinical review
    - Discharge instructions
    - Medication dispensing
    - Bill generation
```

### 2.2 Discharge Readiness Criteria
```sql
CREATE TABLE inpatient.discharge_readiness (
    assessment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL,
    assessment_date DATE NOT NULL,
    clinical_stable BOOLEAN,
    medication_plan_ready BOOLEAN,
    follow_up_scheduled BOOLEAN,
    home_support_adequate BOOLEAN,
    dme_arranged BOOLEAN,
    education_completed BOOLEAN,
    barriers_resolved BOOLEAN,
    estimated_discharge_date DATE,
    actual_discharge_date DATE,
    delay_reasons TEXT[],
    assessed_by UUID,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE inpatient.discharge_barrier (
    barrier_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL,
    barrier_type VARCHAR(100), -- clinical, social, financial, administrative
    description TEXT,
    identified_date DATE,
    responsible_party UUID,
    action_plan TEXT,
    resolved BOOLEAN DEFAULT false,
    resolved_date DATE,
    resolution_notes TEXT
);
```

### 2.3 Transition of Care
```python
def prepare_discharge_transition(case_id):
    """
    Comprehensive discharge transition preparation
    """
    discharge_plan = {
        'clinical_summary': generate_clinical_summary(case_id),
        'medication_reconciliation': reconcile_medications(case_id),
        'follow_up_appointments': schedule_follow_ups(case_id),
        'home_health_needs': assess_home_health(case_id),
        'dme_requirements': identify_dme_needs(case_id),
        'caregiver_training': document_training_completed(case_id),
        'warning_signs': list_red_flags(case_id),
        'emergency_contacts': compile_emergency_info(case_id)
    }
    
    # Check for high-risk discharge
    risk_score = calculate_readmission_risk(case_id)
    if risk_score > THRESHOLD:
        discharge_plan['case_management'] = assign_case_manager(case_id)
        discharge_plan['follow_up_calls'] = schedule_post_discharge_calls(case_id)
    
    return discharge_plan
```

---

## 3. BILLING GENERATION & REVIEW

### 3.1 Bill Compilation Process
```yaml
Bill_Components:
  Room_and_Board:
    - Daily room charges
    - Nursing services
    - Meals
    - Housekeeping
    
  Medical_Services:
    - Physician fees
    - Consultation fees
    - Procedure charges
    - Anesthesia
    
  Diagnostics:
    - Laboratory tests
    - Imaging studies
    - Pathology
    - Special procedures
    
  Medications:
    - Drug charges
    - IV fluids
    - Medical gases
    - Blood products
    
  Supplies_Equipment:
    - Medical supplies
    - Surgical supplies
    - DME usage
    - Prosthetics/orthotics
    
  Other_Services:
    - Physical therapy
    - Respiratory therapy
    - Dietary services
    - Social services
```

### 3.2 Detailed Bill Generation
```sql
CREATE TABLE inpatient.discharge_bill (
    bill_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL,
    admission_date DATE NOT NULL,
    discharge_date DATE NOT NULL,
    total_days INTEGER,
    bill_number VARCHAR(50) UNIQUE,
    bill_date DATE DEFAULT CURRENT_DATE,
    total_charges DECIMAL(15,2),
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE inpatient.bill_line_item (
    line_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bill_id UUID REFERENCES inpatient.discharge_bill,
    service_date DATE NOT NULL,
    category VARCHAR(100),
    service_code VARCHAR(50),
    service_description TEXT,
    quantity DECIMAL(10,2),
    unit_price DECIMAL(12,2),
    total_price DECIMAL(12,2),
    department VARCHAR(100),
    provider_id UUID,
    gl_verified BOOLEAN DEFAULT false,
    gl_verification_notes TEXT
);

CREATE TABLE inpatient.bill_adjustment (
    adjustment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bill_id UUID REFERENCES inpatient.discharge_bill,
    adjustment_type VARCHAR(50), -- discount, write_off, correction
    adjustment_reason TEXT,
    original_amount DECIMAL(12,2),
    adjustment_amount DECIMAL(12,2),
    new_amount DECIMAL(12,2),
    approved_by UUID,
    approved_at TIMESTAMPTZ,
    gl_reversal_entry VARCHAR(100)
);
```

### 3.3 Clinical Coding & DRG Assignment
```python
def assign_drg_coding(case_id):
    """
    Assign DRG/INA-CBG coding for billing
    """
    clinical_data = get_clinical_data(case_id)
    
    # Primary and secondary diagnoses
    diagnoses = extract_diagnoses(clinical_data)
    procedures = extract_procedures(clinical_data)
    
    # Calculate INA-CBG for Indonesia
    ina_cbg = calculate_ina_cbg(
        primary_diagnosis=diagnoses.primary,
        secondary_diagnoses=diagnoses.secondary,
        procedures=procedures,
        los=clinical_data.length_of_stay,
        discharge_status=clinical_data.discharge_status,
        severity_level=calculate_severity(clinical_data)
    )
    
    # Determine payment rate
    payment_rate = get_ina_cbg_rate(
        cbg_code=ina_cbg.code,
        hospital_class=clinical_data.hospital_class,
        regional_adjustment=clinical_data.region
    )
    
    return {
        'ina_cbg_code': ina_cbg.code,
        'ina_cbg_description': ina_cbg.description,
        'severity_level': ina_cbg.severity,
        'base_rate': payment_rate.base,
        'adjusted_rate': payment_rate.adjusted,
        'outlier_threshold': payment_rate.outlier_days
    }
```

---

## 4. GL RECONCILIATION PROCESS

### 4.1 GL vs Bill Reconciliation
```yaml
Reconciliation_Steps:
  1_GL_Retrieval:
    - Fetch approved GL amount
    - Get approved services list
    - Check GL validity period
    - Verify GL conditions
    
  2_Bill_Comparison:
    - Match services to GL
    - Identify non-GL services
    - Calculate variances
    - Flag exceeded limits
    
  3_Variance_Analysis:
    - Service additions
    - Quantity overages
    - Rate differences
    - Unauthorized services
    
  4_Resolution:
    - Clinical justification
    - Prior auth retroactive
    - Member liability
    - Provider write-off
```

### 4.2 Reconciliation Engine
```sql
CREATE TABLE inpatient.gl_reconciliation (
    reconciliation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL,
    gl_id UUID NOT NULL,
    bill_id UUID NOT NULL,
    gl_amount DECIMAL(15,2),
    bill_amount DECIMAL(15,2),
    variance_amount DECIMAL(15,2),
    reconciliation_status VARCHAR(50),
    reconciled_at TIMESTAMPTZ,
    reconciled_by UUID
);

CREATE TABLE inpatient.reconciliation_variance (
    variance_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reconciliation_id UUID REFERENCES inpatient.gl_reconciliation,
    variance_type VARCHAR(100), -- service_addition, quantity_excess, rate_difference
    service_code VARCHAR(50),
    gl_quantity DECIMAL(10,2),
    bill_quantity DECIMAL(10,2),
    gl_amount DECIMAL(12,2),
    bill_amount DECIMAL(12,2),
    variance_amount DECIMAL(12,2),
    justification TEXT,
    resolution VARCHAR(100), -- approved, denied, member_liability
    resolution_notes TEXT
);
```

### 4.3 Automated Reconciliation Logic
```python
def automated_gl_reconciliation(case_id, bill_id, gl_id):
    """
    Automated reconciliation with variance handling
    """
    gl_details = get_gl_details(gl_id)
    bill_details = get_bill_details(bill_id)
    
    reconciliation = {
        'matched_services': [],
        'unmatched_bill_items': [],
        'unutilized_gl_items': [],
        'variances': []
    }
    
    # Match bill items to GL
    for bill_item in bill_details.line_items:
        gl_match = find_gl_match(bill_item, gl_details.approved_services)
        
        if gl_match:
            variance = calculate_variance(bill_item, gl_match)
            if variance.amount > 0:
                reconciliation['variances'].append({
                    'service': bill_item.service_code,
                    'type': determine_variance_type(variance),
                    'amount': variance.amount,
                    'auto_resolution': apply_auto_resolution_rules(variance)
                })
            reconciliation['matched_services'].append(bill_item)
        else:
            reconciliation['unmatched_bill_items'].append(bill_item)
    
    # Check for unutilized GL services
    reconciliation['unutilized_gl_items'] = find_unutilized_gl_services(
        gl_details.approved_services, 
        reconciliation['matched_services']
    )
    
    # Calculate financial summary
    reconciliation['financial_summary'] = {
        'gl_approved': gl_details.total_amount,
        'bill_total': bill_details.total_amount,
        'covered_amount': sum_matched_services(reconciliation['matched_services']),
        'variance_amount': sum_variances(reconciliation['variances']),
        'uncovered_amount': sum_unmatched_items(reconciliation['unmatched_bill_items'])
    }
    
    return reconciliation
```

---

## 5. EXCESS & COPAYMENT MANAGEMENT

### 5.1 Excess Calculation
```yaml
Excess_Components:
  Over_Limit_Services:
    - Services exceeding GL approval
    - Quantity beyond authorized
    - Non-covered services
    
  Upgrade_Charges:
    - Room upgrade costs
    - Comfort items
    - Personal preferences
    
  Exclusions:
    - Policy exclusions
    - Waiting period items
    - Experimental treatments
    
  Copayment_Coinsurance:
    - Fixed copayments
    - Percentage coinsurance
    - Deductible amounts
```

### 5.2 Member Liability Determination
```sql
CREATE TABLE inpatient.member_liability (
    liability_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL,
    bill_id UUID NOT NULL,
    total_charges DECIMAL(15,2),
    covered_amount DECIMAL(15,2),
    copayment DECIMAL(12,2),
    coinsurance DECIMAL(12,2),
    deductible DECIMAL(12,2),
    non_covered_services DECIMAL(12,2),
    room_upgrade DECIMAL(12,2),
    excess_over_limit DECIMAL(12,2),
    total_member_liability DECIMAL(15,2),
    payment_due_date DATE,
    payment_plan_available BOOLEAN DEFAULT false
);

CREATE TABLE inpatient.liability_breakdown (
    breakdown_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    liability_id UUID REFERENCES inpatient.member_liability,
    category VARCHAR(100),
    service_description TEXT,
    charge_amount DECIMAL(12,2),
    covered_amount DECIMAL(12,2),
    member_amount DECIMAL(12,2),
    reason VARCHAR(200),
    dispute_eligible BOOLEAN DEFAULT true
);
```

### 5.3 Excess Collection Strategy
```python
def determine_collection_strategy(member_id, liability_amount):
    """
    Determine optimal collection approach for member liability
    """
    member_profile = get_member_profile(member_id)
    payment_history = get_payment_history(member_id)
    
    collection_options = {
        'immediate_payment': liability_amount <= member_profile.immediate_payment_limit,
        'payment_plan': offer_payment_plan(liability_amount, member_profile.credit_score),
        'guarantor_option': member_profile.has_guarantor,
        'financial_assistance': check_financial_assistance_eligibility(member_profile),
        'deposit_application': apply_existing_deposit(member_id)
    }
    
    # Automated payment if card on file
    if member_profile.has_payment_method and collection_options['immediate_payment']:
        return process_automatic_payment(member_id, liability_amount)
    
    # Generate collection plan
    return create_collection_plan(
        member_id=member_id,
        amount=liability_amount,
        options=collection_options,
        due_date=calculate_due_date()
    )
```

---

## 6. FINAL ADJUDICATION & PAYMENT

### 6.1 Claims Adjudication Process
```yaml
Adjudication_Workflow:
  Initial_Review:
    - Completeness check
    - Eligibility verification
    - Coverage determination
    - Medical necessity review
    
  Pricing_Application:
    - Contract rate application
    - DRG/INA-CBG pricing
    - Outlier calculation
    - Discount application
    
  Benefit_Application:
    - Deductible processing
    - Copay/coinsurance calculation
    - Annual limit checking
    - COB processing
    
  Final_Determination:
    - Allowed amount
    - Plan payment
    - Member responsibility
    - Provider adjustment
```

### 6.2 Payment Processing
```sql
CREATE TABLE inpatient.payment_determination (
    determination_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL,
    claim_id UUID NOT NULL,
    total_billed DECIMAL(15,2),
    allowed_amount DECIMAL(15,2),
    deductible_applied DECIMAL(12,2),
    copay_amount DECIMAL(12,2),
    coinsurance_amount DECIMAL(12,2),
    plan_payment DECIMAL(15,2),
    member_payment DECIMAL(12,2),
    provider_writeoff DECIMAL(12,2),
    other_insurance_payment DECIMAL(12,2),
    adjudicated_at TIMESTAMPTZ DEFAULT NOW(),
    adjudicated_by UUID
);

CREATE TABLE inpatient.payment_transaction (
    transaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    determination_id UUID REFERENCES inpatient.payment_determination,
    payee_type VARCHAR(50), -- provider, member_reimbursement
    payee_id UUID,
    payment_method VARCHAR(50), -- eft, check, wire
    payment_amount DECIMAL(15,2),
    payment_date DATE,
    reference_number VARCHAR(100),
    cleared_date DATE,
    status VARCHAR(50),
    remittance_sent BOOLEAN DEFAULT false
);
```

### 6.3 Provider Payment & Remittance
```python
def process_provider_payment(case_id, determination_id):
    """
    Process provider payment with remittance advice
    """
    determination = get_payment_determination(determination_id)
    provider = get_provider_details(case_id)
    
    # Calculate payment components
    payment = {
        'gross_amount': determination.plan_payment,
        'withholding_tax': calculate_withholding(determination.plan_payment),
        'previous_overpayment': get_overpayment_recovery(provider.id),
        'net_payment': 0
    }
    
    payment['net_payment'] = (
        payment['gross_amount'] - 
        payment['withholding_tax'] - 
        payment['previous_overpayment']
    )
    
    # Process payment
    if payment['net_payment'] > 0:
        transaction = initiate_payment(
            provider_id=provider.id,
            amount=payment['net_payment'],
            method=provider.preferred_payment_method
        )
        
        # Generate remittance advice
        remittance = generate_remittance(
            provider_id=provider.id,
            case_id=case_id,
            payment_details=payment,
            transaction_ref=transaction.reference
        )
        
        # Send notifications
        notify_provider(provider.id, remittance)
        update_gl_entries(transaction)
        
    return transaction
```

---

## 7. DISPUTE & APPEAL MANAGEMENT

### 7.1 Billing Dispute Process
```yaml
Dispute_Categories:
  Clinical_Disputes:
    - Medical necessity
    - Level of care
    - Length of stay
    - Service appropriateness
    
  Administrative_Disputes:
    - Authorization issues
    - Timely filing
    - Coding errors
    - Documentation gaps
    
  Financial_Disputes:
    - Pricing disagreements
    - Contract interpretation
    - Excess calculations
    - Payment amounts
```

### 7.2 Dispute Resolution Workflow
```sql
CREATE TABLE inpatient.billing_dispute (
    dispute_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL,
    bill_id UUID NOT NULL,
    dispute_type VARCHAR(100),
    disputed_amount DECIMAL(15,2),
    dispute_reason TEXT,
    supporting_documents JSONB,
    submitted_by UUID,
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'open',
    assigned_to UUID,
    priority VARCHAR(20),
    resolution TEXT,
    resolution_amount DECIMAL(15,2),
    resolved_at TIMESTAMPTZ,
    resolved_by UUID
);

CREATE TABLE inpatient.dispute_communication (
    communication_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dispute_id UUID REFERENCES inpatient.billing_dispute,
    sender_type VARCHAR(50), -- provider, payer, member
    sender_id UUID,
    message TEXT,
    attachments JSONB,
    sent_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 8. POST-DISCHARGE MONITORING

### 8.1 Post-Discharge Follow-Up
```yaml
Follow_Up_Timeline:
  24_Hours:
    - Discharge phone call
    - Medication verification
    - Question resolution
    
  48-72_Hours:
    - Symptom check
    - Appointment confirmation
    - Home health verification
    
  7_Days:
    - Clinical status
    - Medication adherence
    - Care plan compliance
    
  30_Days:
    - Readmission prevention
    - Outcome assessment
    - Satisfaction survey
```

### 8.2 Readmission Prevention
```python
def monitor_readmission_risk(case_id):
    """
    Monitor and prevent potential readmissions
    """
    discharge_data = get_discharge_data(case_id)
    risk_factors = assess_readmission_risk(discharge_data)
    
    interventions = []
    
    if risk_factors['medication_complexity'] > HIGH:
        interventions.append(schedule_pharmacy_consultation(case_id))
    
    if risk_factors['social_support'] < ADEQUATE:
        interventions.append(assign_social_worker(case_id))
    
    if risk_factors['chronic_conditions'] > 2:
        interventions.append(enroll_disease_management(case_id))
    
    if risk_factors['previous_readmissions'] > 0:
        interventions.append(assign_case_manager(case_id))
    
    # Schedule follow-up calls
    follow_up_schedule = create_follow_up_schedule(
        risk_level=risk_factors['overall_risk'],
        interventions=interventions
    )
    
    return {
        'risk_score': risk_factors['overall_risk'],
        'interventions': interventions,
        'follow_up_schedule': follow_up_schedule
    }
```

---

## 9. FINANCIAL RECONCILIATION & REPORTING

### 9.1 Monthly Reconciliation
```yaml
Reconciliation_Process:
  Provider_Reconciliation:
    - Outstanding claims
    - Payment status
    - Disputed amounts
    - Contract compliance
    
  Member_Reconciliation:
    - Outstanding balances
    - Payment plans
    - Refunds due
    - Collection status
    
  Financial_Reconciliation:
    - GL posting verification
    - Reserve adequacy
    - Cash position
    - Accrual adjustments
```

### 9.2 Management Reporting
```sql
CREATE TABLE inpatient.discharge_metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reporting_period DATE,
    total_discharges INTEGER,
    avg_los DECIMAL(5,2),
    avg_bill_amount DECIMAL(15,2),
    avg_payment_amount DECIMAL(15,2),
    payment_variance_pct DECIMAL(5,2),
    denial_rate DECIMAL(5,2),
    dispute_rate DECIMAL(5,2),
    member_satisfaction_score DECIMAL(5,2),
    readmission_rate DECIMAL(5,2),
    payment_tat_days DECIMAL(5,2)
);
```

---

## 10. SYSTEM INTEGRATION POINTS

### 10.1 Integration Architecture
```yaml
System_Integrations:
  Clinical_Systems:
    - EMR/HIS for clinical data
    - PACS for imaging
    - LIS for lab results
    - Pharmacy systems
    
  Financial_Systems:
    - General ledger
    - Accounts payable
    - Revenue cycle
    - Banking systems
    
  Administrative_Systems:
    - Member portal
    - Provider portal
    - Case management
    - Customer service
```

### 10.2 Data Exchange Standards
```python
def generate_discharge_hl7_message(case_id):
    """
    Generate HL7 ADT^A03 discharge message
    """
    discharge_data = get_discharge_summary(case_id)
    
    hl7_message = {
        'MSH': create_message_header('ADT', 'A03'),
        'EVN': create_event_segment(discharge_data.discharge_datetime),
        'PID': create_patient_segment(discharge_data.patient),
        'PV1': create_visit_segment(discharge_data.visit),
        'DG1': create_diagnosis_segments(discharge_data.diagnoses),
        'PR1': create_procedure_segments(discharge_data.procedures),
        'IN1': create_insurance_segments(discharge_data.insurance),
        'ZBL': create_custom_billing_segment(discharge_data.billing)
    }
    
    return format_hl7_message(hl7_message)
```

---

## 11. QUALITY METRICS & KPIs

### 11.1 Discharge & Billing KPIs
```yaml
Key_Performance_Indicators:
  Clinical:
    - Discharge planning started within 24h: >95%
    - Medication reconciliation completion: 100%
    - Follow-up scheduled before discharge: >90%
    
  Operational:
    - Bill generation within 24h: >95%
    - Clean claim rate: >90%
    - Bill accuracy rate: >95%
    
  Financial:
    - Payment within 30 days: >85%
    - Dispute rate: <5%
    - Collection rate: >95%
    
  Member_Experience:
    - Discharge satisfaction: >4.5/5
    - Bill clarity rating: >4.0/5
    - Complaint rate: <2%
```

---

## 12. IMPLEMENTATION ROADMAP

### Phase 1 (Weeks 1-4): Foundation
- Database schema implementation
- Basic discharge workflow
- Bill generation system

### Phase 2 (Weeks 5-8): Reconciliation
- GL reconciliation engine
- Variance management
- Excess calculation

### Phase 3 (Weeks 9-12): Payment
- Adjudication integration
- Payment processing
- Remittance generation

### Phase 4 (Weeks 13-16): Advanced
- Dispute management
- Analytics dashboard
- Post-discharge monitoring

---

**Related Documents**:
- Claims — Servicing & UM (Inpatient e-GL)
- Claims — Data Model, APIs & Events
- Claims — Gap Analysis & Recommendations