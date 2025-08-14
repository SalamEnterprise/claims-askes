# Data Model Design — Complete Database Architecture (v0.1)

**Purpose**: Comprehensive database design for the health insurance system
**Date**: 2025-08-14
**Owner**: Data Architecture, Engineering, Database Administration
**Status**: Technical Specification

---

## 1. DATABASE ARCHITECTURE OVERVIEW

### 1.1 Database Strategy
```yaml
Database_Tiers:
  Operational:
    Technology: PostgreSQL 15+
    Purpose: Transactional processing
    Schemas: [claims, provider, member, auth, payment]
    Size: 5-10 TB
    Backup: Real-time replication
    
  Cache:
    Technology: Redis Cluster
    Purpose: Session, frequent queries
    Data: [eligibility, auth_tokens, rate_limits]
    Size: 50-100 GB
    TTL: Variable (5min - 24hr)
    
  Document:
    Technology: MongoDB
    Purpose: Unstructured documents
    Collections: [receipts, medical_reports, eobs]
    Size: 10-20 TB
    Sharding: By date
    
  Analytics:
    Technology: ClickHouse
    Purpose: OLAP, reporting
    Tables: [fact_claims, dim_member, dim_provider]
    Size: 20+ TB
    Partitioning: Monthly
    
  Search:
    Technology: Elasticsearch
    Purpose: Full-text search
    Indices: [providers, benefits, documents]
    Size: 1-2 TB
    Shards: 5 primary, 1 replica
```

### 1.2 Schema Organization
```sql
-- Core Business Schemas
CREATE SCHEMA IF NOT EXISTS member;     -- Member management
CREATE SCHEMA IF NOT EXISTS provider;   -- Provider network
CREATE SCHEMA IF NOT EXISTS claims;     -- Claims processing
CREATE SCHEMA IF NOT EXISTS auth;       -- Authorization
CREATE SCHEMA IF NOT EXISTS payment;    -- Financial transactions
CREATE SCHEMA IF NOT EXISTS benefit;    -- Benefit configuration

-- Supporting Schemas
CREATE SCHEMA IF NOT EXISTS audit;      -- Audit trails
CREATE SCHEMA IF NOT EXISTS lookup;     -- Reference data
CREATE SCHEMA IF NOT EXISTS workflow;   -- Process management
CREATE SCHEMA IF NOT EXISTS fraud;      -- Fraud detection
CREATE SCHEMA IF NOT EXISTS analytics;  -- Materialized views
```

---

## 2. MEMBER DOMAIN MODEL

### 2.1 Core Member Tables
```sql
-- Member Master Data
CREATE TABLE member.member (
    member_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_number VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(10) CHECK (gender IN ('M', 'F', 'O')),
    marital_status VARCHAR(20),
    
    -- Identification
    national_id VARCHAR(50) UNIQUE,
    passport_number VARCHAR(50),
    tax_id VARCHAR(50),
    
    -- Contact
    email VARCHAR(255),
    phone_primary VARCHAR(20),
    phone_secondary VARCHAR(20),
    preferred_language VARCHAR(10) DEFAULT 'id',
    
    -- Security
    password_hash VARCHAR(255),
    mfa_enabled BOOLEAN DEFAULT false,
    mfa_secret VARCHAR(255),
    biometric_enrolled BOOLEAN DEFAULT false,
    biometric_data BYTEA,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',
    activation_date DATE,
    termination_date DATE,
    termination_reason VARCHAR(100),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID,
    updated_by UUID,
    version INTEGER DEFAULT 1,
    
    -- Indexes
    INDEX idx_member_name (last_name, first_name),
    INDEX idx_member_dob (date_of_birth),
    INDEX idx_member_status (status),
    INDEX idx_member_email (email)
);

-- Member Address
CREATE TABLE member.member_address (
    address_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id UUID REFERENCES member.member(member_id),
    address_type VARCHAR(20), -- home, work, mailing
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state_province VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(2) DEFAULT 'ID',
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    is_primary BOOLEAN DEFAULT false,
    effective_from DATE NOT NULL,
    effective_to DATE,
    
    INDEX idx_address_member (member_id),
    INDEX idx_address_type (address_type),
    INDEX idx_address_postal (postal_code)
);

-- Member Coverage
CREATE TABLE member.member_coverage (
    coverage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id UUID REFERENCES member.member(member_id),
    policy_id UUID NOT NULL,
    plan_id UUID NOT NULL,
    
    -- Coverage Details
    coverage_tier VARCHAR(20), -- employee, spouse, child, family
    relationship VARCHAR(20), -- self, spouse, child, parent
    subscriber_id UUID REFERENCES member.member(member_id),
    
    -- Dates
    effective_date DATE NOT NULL,
    termination_date DATE,
    waiting_period_end DATE,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',
    enrollment_type VARCHAR(20), -- new, renewal, change
    
    -- Group Information
    group_id UUID,
    group_name VARCHAR(255),
    employer_id UUID,
    employer_name VARCHAR(255),
    department VARCHAR(100),
    employee_id VARCHAR(50),
    
    INDEX idx_coverage_member (member_id),
    INDEX idx_coverage_policy (policy_id),
    INDEX idx_coverage_dates (effective_date, termination_date),
    INDEX idx_coverage_group (group_id),
    
    CONSTRAINT check_dates CHECK (termination_date > effective_date)
);

-- Member Dependents
CREATE TABLE member.member_dependent (
    dependent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    primary_member_id UUID REFERENCES member.member(member_id),
    dependent_member_id UUID REFERENCES member.member(member_id),
    relationship VARCHAR(20) NOT NULL,
    is_disabled BOOLEAN DEFAULT false,
    is_student BOOLEAN DEFAULT false,
    dependency_proof_doc JSONB,
    verified_date DATE,
    verified_by UUID,
    
    UNIQUE(primary_member_id, dependent_member_id),
    INDEX idx_dependent_primary (primary_member_id),
    INDEX idx_dependent_member (dependent_member_id)
);
```

### 2.2 Member Preferences & Settings
```sql
-- Communication Preferences
CREATE TABLE member.member_preference (
    preference_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id UUID REFERENCES member.member(member_id) UNIQUE,
    
    -- Communication
    comm_email BOOLEAN DEFAULT true,
    comm_sms BOOLEAN DEFAULT true,
    comm_whatsapp BOOLEAN DEFAULT false,
    comm_push BOOLEAN DEFAULT true,
    comm_mail BOOLEAN DEFAULT false,
    
    -- Notifications
    notify_claim_status BOOLEAN DEFAULT true,
    notify_auth_status BOOLEAN DEFAULT true,
    notify_payment BOOLEAN DEFAULT true,
    notify_eob BOOLEAN DEFAULT true,
    notify_benefits BOOLEAN DEFAULT true,
    notify_preventive BOOLEAN DEFAULT true,
    
    -- Payment
    paperless_eob BOOLEAN DEFAULT true,
    auto_pay BOOLEAN DEFAULT false,
    payment_method VARCHAR(20), -- bank, wallet, check
    payment_details JSONB, -- encrypted
    
    -- Portal
    portal_theme VARCHAR(20) DEFAULT 'light',
    portal_language VARCHAR(10) DEFAULT 'id',
    dashboard_layout JSONB,
    
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Member Payment Methods
CREATE TABLE member.member_payment_method (
    payment_method_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id UUID REFERENCES member.member(member_id),
    
    method_type VARCHAR(20), -- bank, card, wallet
    is_primary BOOLEAN DEFAULT false,
    
    -- Bank Account
    bank_name VARCHAR(100),
    account_number VARCHAR(50), -- encrypted
    account_name VARCHAR(255),
    swift_code VARCHAR(20),
    
    -- Digital Wallet
    wallet_provider VARCHAR(50), -- gopay, ovo, dana
    wallet_id VARCHAR(100), -- encrypted
    
    -- Card
    card_token VARCHAR(255), -- tokenized
    card_last4 VARCHAR(4),
    card_brand VARCHAR(20),
    card_exp_month INTEGER,
    card_exp_year INTEGER,
    
    -- Verification
    verified BOOLEAN DEFAULT false,
    verified_date TIMESTAMPTZ,
    verification_method VARCHAR(50),
    
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    INDEX idx_payment_member (member_id),
    INDEX idx_payment_primary (member_id, is_primary)
);
```

---

## 3. PROVIDER DOMAIN MODEL

### 3.1 Provider Master Tables
```sql
-- Provider Organization
CREATE TABLE provider.provider_organization (
    provider_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_code VARCHAR(50) UNIQUE NOT NULL,
    npi VARCHAR(20),
    tax_id VARCHAR(30) UNIQUE,
    
    -- Basic Info
    legal_name VARCHAR(255) NOT NULL,
    dba_name VARCHAR(255),
    provider_type VARCHAR(50), -- hospital, clinic, pharmacy, lab
    provider_subtype VARCHAR(50), -- general, specialty, urgent_care
    ownership_type VARCHAR(50), -- private, public, non_profit
    
    -- Classification
    facility_type VARCHAR(50),
    bed_capacity INTEGER,
    accreditation VARCHAR(100),
    accreditation_date DATE,
    specialties TEXT[],
    
    -- Contact
    website VARCHAR(255),
    email VARCHAR(255),
    phone_main VARCHAR(20),
    phone_emergency VARCHAR(20),
    fax VARCHAR(20),
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',
    network_status VARCHAR(20), -- in_network, out_of_network
    network_tier VARCHAR(20), -- tier1, tier2, tier3
    
    -- Dates
    established_date DATE,
    contracted_date DATE,
    termination_date DATE,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    INDEX idx_provider_type (provider_type),
    INDEX idx_provider_status (status, network_status),
    INDEX idx_provider_tax (tax_id)
);

-- Provider Locations
CREATE TABLE provider.provider_location (
    location_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id UUID REFERENCES provider.provider_organization(provider_id),
    location_code VARCHAR(50) UNIQUE,
    
    -- Address
    location_name VARCHAR(255),
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state_province VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(2) DEFAULT 'ID',
    
    -- Geolocation
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    service_area_radius_km INTEGER,
    
    -- Contact
    phone VARCHAR(20),
    fax VARCHAR(20),
    email VARCHAR(255),
    
    -- Operations
    operating_hours JSONB,
    emergency_services BOOLEAN DEFAULT false,
    appointment_required BOOLEAN DEFAULT true,
    walk_in_accepted BOOLEAN DEFAULT false,
    telemedicine_available BOOLEAN DEFAULT false,
    
    -- Accessibility
    wheelchair_accessible BOOLEAN,
    parking_available BOOLEAN,
    public_transport_nearby BOOLEAN,
    
    -- Status
    active BOOLEAN DEFAULT true,
    temporary_closed BOOLEAN DEFAULT false,
    
    INDEX idx_location_provider (provider_id),
    INDEX idx_location_geo (latitude, longitude),
    INDEX idx_location_city (city),
    INDEX idx_location_postal (postal_code)
);

-- Provider Practitioners
CREATE TABLE provider.provider_practitioner (
    practitioner_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id UUID REFERENCES provider.provider_organization(provider_id),
    
    -- Identification
    npi VARCHAR(20),
    license_number VARCHAR(50) NOT NULL,
    license_state VARCHAR(50),
    str_number VARCHAR(50), -- Indonesia specific
    sip_number VARCHAR(50), -- Indonesia specific
    
    -- Personal Info
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    last_name VARCHAR(100) NOT NULL,
    title VARCHAR(20), -- Dr, Prof, etc
    gender VARCHAR(10),
    
    -- Professional
    specialty_primary VARCHAR(100),
    specialty_secondary VARCHAR(100),
    subspecialties TEXT[],
    board_certifications JSONB,
    
    -- Education
    medical_school VARCHAR(255),
    graduation_year INTEGER,
    residency_info JSONB,
    fellowship_info JSONB,
    
    -- Schedule
    locations UUID[], -- array of location_ids
    schedule JSONB, -- weekly schedule per location
    consultation_fee DECIMAL(12,2),
    
    -- Status
    active BOOLEAN DEFAULT true,
    accepting_patients BOOLEAN DEFAULT true,
    
    -- Languages
    languages_spoken TEXT[],
    
    INDEX idx_practitioner_provider (provider_id),
    INDEX idx_practitioner_name (last_name, first_name),
    INDEX idx_practitioner_specialty (specialty_primary),
    INDEX idx_practitioner_npi (npi)
);

-- Provider Contracts
CREATE TABLE provider.provider_contract (
    contract_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id UUID REFERENCES provider.provider_organization(provider_id),
    contract_number VARCHAR(50) UNIQUE NOT NULL,
    
    -- Contract Details
    contract_type VARCHAR(50), -- fee_for_service, capitation, bundled
    payment_terms VARCHAR(50), -- net30, net45, net60
    
    -- Dates
    effective_date DATE NOT NULL,
    expiration_date DATE,
    auto_renewal BOOLEAN DEFAULT false,
    renewal_notice_days INTEGER DEFAULT 90,
    
    -- Financial
    withholding_tax_rate DECIMAL(5,2),
    admin_fee_rate DECIMAL(5,2),
    
    -- Performance
    quality_metrics_required BOOLEAN DEFAULT true,
    minimum_quality_score DECIMAL(5,2),
    volume_commitments JSONB,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',
    signed_date DATE,
    signed_by VARCHAR(255),
    
    -- Documents
    contract_document_url TEXT,
    amendments JSONB,
    
    INDEX idx_contract_provider (provider_id),
    INDEX idx_contract_dates (effective_date, expiration_date),
    INDEX idx_contract_status (status)
);

-- Provider Service Rates
CREATE TABLE provider.provider_rate (
    rate_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id UUID REFERENCES provider.provider_contract(contract_id),
    
    -- Service Identification
    service_code VARCHAR(50) NOT NULL,
    service_description TEXT,
    service_category VARCHAR(100),
    
    -- Rates
    rate_type VARCHAR(20), -- fixed, percentage, per_diem
    base_rate DECIMAL(15,2),
    rate_multiplier DECIMAL(5,3) DEFAULT 1.0,
    min_rate DECIMAL(15,2),
    max_rate DECIMAL(15,2),
    
    -- Modifiers
    modifiers JSONB,
    place_of_service_adjustments JSONB,
    
    -- Validity
    effective_date DATE NOT NULL,
    end_date DATE,
    
    INDEX idx_rate_contract (contract_id),
    INDEX idx_rate_service (service_code),
    INDEX idx_rate_dates (effective_date, end_date),
    
    UNIQUE(contract_id, service_code, effective_date)
);
```

### 3.2 Provider Performance & Quality
```sql
-- Provider Performance Metrics
CREATE TABLE provider.provider_performance (
    performance_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id UUID REFERENCES provider.provider_organization(provider_id),
    measurement_period DATE NOT NULL,
    
    -- Volume Metrics
    total_claims INTEGER,
    total_members_served INTEGER,
    total_billed_amount DECIMAL(15,2),
    total_paid_amount DECIMAL(15,2),
    
    -- Quality Metrics
    quality_score DECIMAL(5,2),
    patient_satisfaction_score DECIMAL(5,2),
    clinical_outcome_score DECIMAL(5,2),
    
    -- Efficiency Metrics
    avg_length_of_stay DECIMAL(5,2),
    readmission_rate DECIMAL(5,2),
    er_utilization_rate DECIMAL(5,2),
    generic_prescribing_rate DECIMAL(5,2),
    
    -- Financial Metrics
    cost_per_member DECIMAL(12,2),
    cost_efficiency_index DECIMAL(5,2),
    claim_denial_rate DECIMAL(5,2),
    appeal_overturn_rate DECIMAL(5,2),
    
    -- Compliance Metrics
    documentation_accuracy DECIMAL(5,2),
    coding_accuracy DECIMAL(5,2),
    timely_filing_rate DECIMAL(5,2),
    
    -- Comparative
    peer_percentile INTEGER,
    regional_rank INTEGER,
    
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    
    INDEX idx_performance_provider (provider_id),
    INDEX idx_performance_period (measurement_period),
    UNIQUE(provider_id, measurement_period)
);

-- Provider Credentialing
CREATE TABLE provider.provider_credential (
    credential_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id UUID REFERENCES provider.provider_organization(provider_id),
    practitioner_id UUID REFERENCES provider.provider_practitioner(practitioner_id),
    
    credential_type VARCHAR(50), -- license, certification, insurance
    credential_name VARCHAR(255),
    issuing_authority VARCHAR(255),
    credential_number VARCHAR(100),
    
    issue_date DATE,
    expiration_date DATE,
    
    -- Verification
    verification_status VARCHAR(20), -- pending, verified, expired
    verification_date DATE,
    verification_method VARCHAR(50),
    verified_by UUID,
    
    -- Documents
    document_url TEXT,
    
    -- Alerts
    renewal_alert_days INTEGER DEFAULT 90,
    alert_sent BOOLEAN DEFAULT false,
    
    INDEX idx_credential_provider (provider_id),
    INDEX idx_credential_practitioner (practitioner_id),
    INDEX idx_credential_expiration (expiration_date),
    INDEX idx_credential_status (verification_status)
);
```

---

## 4. CLAIMS DOMAIN MODEL

### 4.1 Core Claims Tables
```sql
-- Claim Master
CREATE TABLE claims.claim (
    claim_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_number VARCHAR(50) UNIQUE NOT NULL,
    
    -- Parties
    member_id UUID NOT NULL,
    subscriber_id UUID,
    provider_id UUID,
    rendering_provider_id UUID,
    referring_provider_id UUID,
    
    -- Policy/Coverage
    policy_id UUID NOT NULL,
    plan_id UUID NOT NULL,
    coverage_id UUID,
    
    -- Claim Type
    claim_type VARCHAR(20), -- medical, pharmacy, dental, vision
    claim_subtype VARCHAR(50), -- professional, institutional, dme
    service_type VARCHAR(50), -- inpatient, outpatient, emergency
    
    -- Dates
    service_date_from DATE NOT NULL,
    service_date_to DATE NOT NULL,
    admission_date TIMESTAMPTZ,
    discharge_date TIMESTAMPTZ,
    received_date DATE DEFAULT CURRENT_DATE,
    
    -- Status
    status VARCHAR(50) DEFAULT 'received',
    status_reason VARCHAR(255),
    adjudication_status VARCHAR(50),
    payment_status VARCHAR(50),
    
    -- Financial
    billed_amount DECIMAL(15,2) NOT NULL,
    allowed_amount DECIMAL(15,2),
    paid_amount DECIMAL(15,2),
    member_responsibility DECIMAL(15,2),
    
    -- Clinical
    primary_diagnosis VARCHAR(20),
    diagnosis_codes TEXT[],
    procedure_codes TEXT[],
    drg_code VARCHAR(20),
    
    -- Authorization
    auth_number VARCHAR(50),
    auth_required BOOLEAN DEFAULT false,
    
    -- Source
    submission_method VARCHAR(20), -- portal, edi, api, manual
    submission_source VARCHAR(50),
    
    -- Reimbursement
    is_reimbursement BOOLEAN DEFAULT false,
    member_paid_amount DECIMAL(15,2),
    reimbursement_amount DECIMAL(15,2),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    adjudicated_at TIMESTAMPTZ,
    paid_at TIMESTAMPTZ,
    
    INDEX idx_claim_member (member_id),
    INDEX idx_claim_provider (provider_id),
    INDEX idx_claim_dates (service_date_from, service_date_to),
    INDEX idx_claim_status (status, adjudication_status, payment_status),
    INDEX idx_claim_number (claim_number),
    INDEX idx_claim_auth (auth_number)
);

-- Claim Lines
CREATE TABLE claims.claim_line (
    line_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id UUID REFERENCES claims.claim(claim_id),
    line_number INTEGER NOT NULL,
    
    -- Service
    service_date DATE NOT NULL,
    service_code VARCHAR(20),
    service_description TEXT,
    modifier_codes TEXT[],
    
    -- Diagnosis
    diagnosis_codes TEXT[],
    diagnosis_pointers TEXT[],
    
    -- Quantities
    quantity DECIMAL(10,2) DEFAULT 1,
    unit_of_measure VARCHAR(20),
    
    -- Financial
    billed_amount DECIMAL(15,2) NOT NULL,
    allowed_amount DECIMAL(15,2),
    copay_amount DECIMAL(12,2),
    coinsurance_amount DECIMAL(12,2),
    deductible_amount DECIMAL(12,2),
    paid_amount DECIMAL(15,2),
    
    -- Provider
    rendering_provider_id UUID,
    place_of_service VARCHAR(5),
    
    -- Status
    status VARCHAR(50),
    denial_reasons TEXT[],
    
    -- Adjudication
    benefit_code VARCHAR(50),
    adjudication_details JSONB,
    
    INDEX idx_line_claim (claim_id),
    INDEX idx_line_service (service_code),
    INDEX idx_line_date (service_date),
    
    UNIQUE(claim_id, line_number)
);

-- Claim Documents
CREATE TABLE claims.claim_document (
    document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id UUID REFERENCES claims.claim(claim_id),
    
    document_type VARCHAR(50), -- receipt, medical_report, prescription
    document_name VARCHAR(255),
    file_path TEXT,
    file_size INTEGER,
    mime_type VARCHAR(100),
    
    -- OCR Results
    ocr_processed BOOLEAN DEFAULT false,
    ocr_confidence DECIMAL(5,2),
    extracted_data JSONB,
    
    -- Validation
    validated BOOLEAN DEFAULT false,
    validation_score DECIMAL(5,2),
    validation_flags TEXT[],
    
    -- Metadata
    uploaded_at TIMESTAMPTZ DEFAULT NOW(),
    uploaded_by UUID,
    
    INDEX idx_document_claim (claim_id),
    INDEX idx_document_type (document_type)
);

-- Claim History
CREATE TABLE claims.claim_history (
    history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id UUID REFERENCES claims.claim(claim_id),
    
    action VARCHAR(100) NOT NULL,
    previous_status VARCHAR(50),
    new_status VARCHAR(50),
    
    changes JSONB,
    reason TEXT,
    
    performed_by UUID,
    performed_at TIMESTAMPTZ DEFAULT NOW(),
    
    INDEX idx_history_claim (claim_id),
    INDEX idx_history_date (performed_at)
);
```

### 4.2 Adjudication & Payment Tables
```sql
-- Adjudication Results
CREATE TABLE claims.adjudication_result (
    adjudication_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id UUID REFERENCES claims.claim(claim_id),
    
    -- Decision
    decision VARCHAR(20), -- approve, deny, partial, pend
    decision_date TIMESTAMPTZ DEFAULT NOW(),
    decision_by UUID,
    decision_method VARCHAR(20), -- auto, manual, ml
    
    -- Financial Breakdown
    billed_amount DECIMAL(15,2),
    allowed_amount DECIMAL(15,2),
    
    -- Member Cost Share
    deductible_applied DECIMAL(12,2),
    copay_amount DECIMAL(12,2),
    coinsurance_amount DECIMAL(12,2),
    member_responsibility DECIMAL(15,2),
    
    -- Plan Payment
    plan_payment DECIMAL(15,2),
    
    -- Other Insurance
    cob_amount DECIMAL(15,2),
    cob_savings DECIMAL(15,2),
    
    -- Adjustments
    provider_discount DECIMAL(15,2),
    contractual_adjustment DECIMAL(15,2),
    
    -- Accumulators Impact
    deductible_ytd_before DECIMAL(12,2),
    deductible_ytd_after DECIMAL(12,2),
    oop_ytd_before DECIMAL(12,2),
    oop_ytd_after DECIMAL(12,2),
    
    -- Rules Applied
    rules_applied JSONB,
    denial_reasons TEXT[],
    
    INDEX idx_adjudication_claim (claim_id),
    INDEX idx_adjudication_date (decision_date)
);

-- Payment Transactions
CREATE TABLE payment.payment_transaction (
    transaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_number VARCHAR(50) UNIQUE NOT NULL,
    
    -- Reference
    claim_id UUID,
    auth_id UUID,
    
    -- Payee
    payee_type VARCHAR(20), -- provider, member
    payee_id UUID NOT NULL,
    
    -- Amount
    payment_amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'IDR',
    
    -- Method
    payment_method VARCHAR(20), -- eft, check, card, wallet
    payment_details JSONB, -- encrypted
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending',
    
    -- Dates
    initiated_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    failed_at TIMESTAMPTZ,
    
    -- Reference Numbers
    internal_reference VARCHAR(100),
    external_reference VARCHAR(100),
    
    -- Error Handling
    failure_reason TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    
    INDEX idx_payment_claim (claim_id),
    INDEX idx_payment_payee (payee_type, payee_id),
    INDEX idx_payment_status (status),
    INDEX idx_payment_date (initiated_at)
);

-- Remittance Advice
CREATE TABLE payment.remittance_advice (
    remittance_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id UUID NOT NULL,
    
    remittance_date DATE DEFAULT CURRENT_DATE,
    payment_date DATE,
    
    -- Summary
    total_billed DECIMAL(15,2),
    total_allowed DECIMAL(15,2),
    total_paid DECIMAL(15,2),
    total_adjustment DECIMAL(15,2),
    
    -- Payment Info
    payment_method VARCHAR(20),
    check_number VARCHAR(50),
    eft_reference VARCHAR(100),
    
    -- Details
    claim_details JSONB,
    
    -- Delivery
    delivery_method VARCHAR(20), -- email, portal, mail
    delivered_at TIMESTAMPTZ,
    
    INDEX idx_remittance_provider (provider_id),
    INDEX idx_remittance_date (remittance_date)
);
```

---

## 5. AUTHORIZATION DOMAIN MODEL

### 5.1 Authorization Tables
```sql
-- Authorization Requests
CREATE TABLE auth.authorization_request (
    auth_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_number VARCHAR(50) UNIQUE NOT NULL,
    
    -- Parties
    member_id UUID NOT NULL,
    provider_id UUID,
    requesting_provider_id UUID,
    
    -- Coverage
    policy_id UUID NOT NULL,
    plan_id UUID NOT NULL,
    
    -- Service Details
    service_type VARCHAR(50),
    service_codes TEXT[],
    procedure_codes TEXT[],
    
    -- Clinical
    primary_diagnosis VARCHAR(20),
    diagnosis_codes TEXT[],
    clinical_notes TEXT,
    
    -- Dates
    request_date TIMESTAMPTZ DEFAULT NOW(),
    service_date_from DATE,
    service_date_to DATE,
    
    -- Urgency
    urgency VARCHAR(20), -- routine, urgent, emergency
    
    -- Quantities
    requested_units INTEGER,
    requested_days INTEGER,
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending',
    decision VARCHAR(20), -- approved, denied, partial, pended
    decision_date TIMESTAMPTZ,
    decision_by UUID,
    
    -- Approved Details
    approved_units INTEGER,
    approved_days INTEGER,
    approved_amount DECIMAL(15,2),
    
    -- Validity
    valid_from DATE,
    valid_through DATE,
    
    -- Denial
    denial_reasons TEXT[],
    appeal_rights TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    INDEX idx_auth_member (member_id),
    INDEX idx_auth_provider (provider_id),
    INDEX idx_auth_status (status),
    INDEX idx_auth_dates (valid_from, valid_through),
    INDEX idx_auth_number (auth_number)
);

-- Authorization Clinical Review
CREATE TABLE auth.clinical_review (
    review_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_id UUID REFERENCES auth.authorization_request(auth_id),
    
    -- Reviewer
    reviewer_id UUID NOT NULL,
    reviewer_type VARCHAR(20), -- nurse, physician, medical_director
    
    -- Review Details
    review_date TIMESTAMPTZ DEFAULT NOW(),
    review_notes TEXT,
    
    -- Clinical Criteria
    criteria_met JSONB,
    guidelines_referenced TEXT[],
    
    -- Decision
    recommendation VARCHAR(20), -- approve, deny, modify
    recommended_units INTEGER,
    recommended_days INTEGER,
    
    -- Peer to Peer
    p2p_requested BOOLEAN DEFAULT false,
    p2p_date TIMESTAMPTZ,
    p2p_notes TEXT,
    
    INDEX idx_review_auth (auth_id),
    INDEX idx_review_date (review_date)
);

-- Authorization Appeals
CREATE TABLE auth.authorization_appeal (
    appeal_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_id UUID REFERENCES auth.authorization_request(auth_id),
    
    -- Appeal Details
    appeal_date TIMESTAMPTZ DEFAULT NOW(),
    appellant_type VARCHAR(20), -- member, provider
    appellant_id UUID,
    
    -- Reason
    appeal_reason TEXT,
    supporting_documents JSONB,
    
    -- Review
    review_level VARCHAR(20), -- first, second, external
    reviewer_id UUID,
    review_date TIMESTAMPTZ,
    
    -- Decision
    decision VARCHAR(20), -- upheld, overturned, partial
    decision_notes TEXT,
    
    -- Outcome
    new_approved_units INTEGER,
    new_approved_days INTEGER,
    
    INDEX idx_appeal_auth (auth_id),
    INDEX idx_appeal_date (appeal_date)
);
```

---

## 6. BENEFIT CONFIGURATION MODEL

### 6.1 Benefit Structure Tables
```sql
-- Benefit Plans
CREATE TABLE benefit.plan (
    plan_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_code VARCHAR(50) UNIQUE NOT NULL,
    plan_name VARCHAR(255) NOT NULL,
    plan_type VARCHAR(50), -- PPO, HMO, EPO, POS
    
    -- Tiers
    network_tiers INTEGER DEFAULT 1,
    
    -- Cost Sharing
    annual_deductible_individual DECIMAL(12,2),
    annual_deductible_family DECIMAL(12,2),
    annual_oop_max_individual DECIMAL(12,2),
    annual_oop_max_family DECIMAL(12,2),
    
    -- Lifetime Limits
    lifetime_maximum DECIMAL(15,2),
    
    -- Status
    active BOOLEAN DEFAULT true,
    effective_date DATE NOT NULL,
    termination_date DATE,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    INDEX idx_plan_code (plan_code),
    INDEX idx_plan_dates (effective_date, termination_date)
);

-- Benefit Categories
CREATE TABLE benefit.benefit_category (
    category_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_code VARCHAR(50) UNIQUE NOT NULL,
    category_name VARCHAR(255) NOT NULL,
    parent_category_id UUID REFERENCES benefit.benefit_category(category_id),
    
    description TEXT,
    display_order INTEGER,
    
    INDEX idx_category_parent (parent_category_id)
);

-- Plan Benefits (Already exists in claims schema, showing enhanced version)
CREATE TABLE benefit.plan_benefit (
    benefit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID REFERENCES benefit.plan(plan_id),
    benefit_code VARCHAR(50) NOT NULL,
    
    -- Benefit Details
    benefit_name VARCHAR(255) NOT NULL,
    category_id UUID REFERENCES benefit.benefit_category(category_id),
    
    -- Coverage
    covered BOOLEAN DEFAULT true,
    requires_auth BOOLEAN DEFAULT false,
    requires_referral BOOLEAN DEFAULT false,
    
    -- Limits
    limit_basis VARCHAR(20), -- incident, day, year
    limit_value DECIMAL(15,2),
    limit_quantity INTEGER,
    
    -- Cost Sharing
    copay_amount DECIMAL(12,2),
    coinsurance_percent DECIMAL(5,2),
    
    -- Network Differentials
    in_network_coinsurance DECIMAL(5,2),
    out_network_coinsurance DECIMAL(5,2),
    
    -- Special Rules
    age_limits JSONB,
    gender_restrictions VARCHAR(10),
    waiting_period_days INTEGER,
    
    -- Effective Dates
    effective_date DATE NOT NULL,
    end_date DATE,
    
    INDEX idx_benefit_plan (plan_id),
    INDEX idx_benefit_code (benefit_code),
    INDEX idx_benefit_category (category_id),
    
    UNIQUE(plan_id, benefit_code, effective_date)
);

-- Benefit Exclusions
CREATE TABLE benefit.exclusion (
    exclusion_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID REFERENCES benefit.plan(plan_id),
    
    exclusion_code VARCHAR(50),
    exclusion_description TEXT,
    
    -- Conditions
    diagnosis_codes TEXT[],
    procedure_codes TEXT[],
    
    -- Exceptions
    exception_criteria JSONB,
    
    INDEX idx_exclusion_plan (plan_id)
);
```

---

## 7. FRAUD DETECTION MODEL

### 7.1 Fraud Detection Tables
```sql
-- Fraud Cases
CREATE TABLE fraud.fraud_case (
    case_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_number VARCHAR(50) UNIQUE NOT NULL,
    
    -- Subject
    subject_type VARCHAR(20), -- member, provider, both
    member_id UUID,
    provider_id UUID,
    
    -- Detection
    detection_date TIMESTAMPTZ DEFAULT NOW(),
    detection_method VARCHAR(50), -- rule, ml, tip, audit
    
    -- Risk Assessment
    risk_score DECIMAL(5,2),
    fraud_type VARCHAR(100),
    estimated_loss DECIMAL(15,2),
    
    -- Investigation
    status VARCHAR(50) DEFAULT 'open',
    priority VARCHAR(20),
    assigned_to UUID,
    
    -- Evidence
    evidence JSONB,
    related_claims UUID[],
    
    -- Outcome
    investigation_outcome VARCHAR(50),
    confirmed_fraud BOOLEAN,
    recovered_amount DECIMAL(15,2),
    
    -- Actions
    actions_taken JSONB,
    law_enforcement_referred BOOLEAN DEFAULT false,
    
    -- Dates
    opened_at TIMESTAMPTZ DEFAULT NOW(),
    closed_at TIMESTAMPTZ,
    
    INDEX idx_fraud_subject (subject_type, member_id, provider_id),
    INDEX idx_fraud_status (status),
    INDEX idx_fraud_date (detection_date)
);

-- Fraud Indicators
CREATE TABLE fraud.fraud_indicator (
    indicator_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Reference
    claim_id UUID,
    auth_id UUID,
    member_id UUID,
    provider_id UUID,
    
    -- Indicator Details
    indicator_type VARCHAR(100),
    indicator_value JSONB,
    confidence_score DECIMAL(5,2),
    
    -- Detection
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    detection_rule VARCHAR(100),
    
    -- Status
    reviewed BOOLEAN DEFAULT false,
    false_positive BOOLEAN,
    
    INDEX idx_indicator_claim (claim_id),
    INDEX idx_indicator_member (member_id),
    INDEX idx_indicator_provider (provider_id),
    INDEX idx_indicator_type (indicator_type)
);

-- Fraud Rules
CREATE TABLE fraud.fraud_rule (
    rule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_code VARCHAR(50) UNIQUE NOT NULL,
    rule_name VARCHAR(255) NOT NULL,
    
    -- Rule Definition
    rule_type VARCHAR(50), -- threshold, pattern, velocity
    rule_logic JSONB,
    
    -- Scoring
    base_score DECIMAL(5,2),
    weight DECIMAL(5,2) DEFAULT 1.0,
    
    -- Status
    active BOOLEAN DEFAULT true,
    
    -- Performance
    true_positive_rate DECIMAL(5,2),
    false_positive_rate DECIMAL(5,2),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    INDEX idx_fraud_rule_active (active),
    INDEX idx_fraud_rule_type (rule_type)
);
```

---

## 8. LOOKUP & REFERENCE TABLES

### 8.1 Medical Codes
```sql
-- ICD-10 Diagnosis Codes
CREATE TABLE lookup.icd10_diagnosis (
    code VARCHAR(20) PRIMARY KEY,
    short_description VARCHAR(255),
    long_description TEXT,
    category VARCHAR(20),
    
    -- Hierarchy
    parent_code VARCHAR(20),
    level INTEGER,
    
    -- Status
    active BOOLEAN DEFAULT true,
    effective_date DATE,
    end_date DATE,
    
    INDEX idx_icd10_category (category),
    INDEX idx_icd10_parent (parent_code)
);

-- Procedure Codes
CREATE TABLE lookup.procedure_code (
    code VARCHAR(20) PRIMARY KEY,
    code_system VARCHAR(20), -- CPT, HCPCS, ICD-9-CM
    
    description TEXT,
    category VARCHAR(100),
    
    -- RVU Values
    work_rvu DECIMAL(8,4),
    practice_rvu DECIMAL(8,4),
    malpractice_rvu DECIMAL(8,4),
    total_rvu DECIMAL(8,4),
    
    -- Status
    active BOOLEAN DEFAULT true,
    
    INDEX idx_procedure_system (code_system),
    INDEX idx_procedure_category (category)
);

-- Drug Codes
CREATE TABLE lookup.drug_code (
    ndc VARCHAR(20) PRIMARY KEY,
    
    -- Drug Info
    drug_name VARCHAR(255),
    generic_name VARCHAR(255),
    brand_name VARCHAR(255),
    
    -- Classification
    therapeutic_class VARCHAR(100),
    pharmacologic_class VARCHAR(100),
    
    -- Dosage
    strength VARCHAR(100),
    dosage_form VARCHAR(100),
    route VARCHAR(50),
    
    -- Package
    package_size INTEGER,
    package_unit VARCHAR(50),
    
    -- Status
    generic_available BOOLEAN,
    controlled_substance VARCHAR(10),
    
    INDEX idx_drug_name (drug_name),
    INDEX idx_drug_generic (generic_name),
    INDEX idx_drug_class (therapeutic_class)
);
```

### 8.2 Geographic & Administrative
```sql
-- Geographic Regions
CREATE TABLE lookup.geographic_region (
    region_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    region_code VARCHAR(20) UNIQUE NOT NULL,
    region_name VARCHAR(255) NOT NULL,
    
    -- Hierarchy
    country VARCHAR(2) DEFAULT 'ID',
    province VARCHAR(100),
    city VARCHAR(100),
    district VARCHAR(100),
    postal_code VARCHAR(20),
    
    -- Geographic Data
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    timezone VARCHAR(50),
    
    -- Network Planning
    urban_rural VARCHAR(20),
    population INTEGER,
    
    INDEX idx_region_province (province),
    INDEX idx_region_city (city),
    INDEX idx_region_postal (postal_code)
);

-- Reason Codes
CREATE TABLE lookup.reason_code (
    code VARCHAR(50) PRIMARY KEY,
    category VARCHAR(50),
    
    description TEXT,
    user_message TEXT,
    
    -- Actions
    appealable BOOLEAN DEFAULT true,
    correctable BOOLEAN DEFAULT true,
    
    INDEX idx_reason_category (category)
);
```

---

## 9. AUDIT & COMPLIANCE TABLES

### 9.1 Audit Trail
```sql
-- Audit Log
CREATE TABLE audit.audit_log (
    audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Entity
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID NOT NULL,
    
    -- Action
    action VARCHAR(100) NOT NULL,
    action_timestamp TIMESTAMPTZ DEFAULT NOW(),
    
    -- User
    user_id UUID,
    user_role VARCHAR(50),
    ip_address INET,
    user_agent TEXT,
    
    -- Changes
    old_values JSONB,
    new_values JSONB,
    
    -- Context
    session_id VARCHAR(100),
    request_id VARCHAR(100),
    
    INDEX idx_audit_entity (entity_type, entity_id),
    INDEX idx_audit_user (user_id),
    INDEX idx_audit_timestamp (action_timestamp),
    INDEX idx_audit_action (action)
);

-- Compliance Tracking
CREATE TABLE audit.compliance_tracking (
    tracking_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Requirement
    regulation VARCHAR(100), -- OJK, BPJS, HIPAA
    requirement VARCHAR(255),
    
    -- Assessment
    assessment_date DATE,
    compliant BOOLEAN,
    findings TEXT,
    
    -- Evidence
    evidence_documents JSONB,
    
    -- Remediation
    action_required BOOLEAN,
    action_plan TEXT,
    due_date DATE,
    
    INDEX idx_compliance_regulation (regulation),
    INDEX idx_compliance_date (assessment_date)
);
```

---

## 10. INDEXES & OPTIMIZATION

### 10.1 Performance Indexes
```sql
-- Composite Indexes for Common Queries
CREATE INDEX idx_claim_member_date ON claims.claim(member_id, service_date_from DESC);
CREATE INDEX idx_claim_provider_status ON claims.claim(provider_id, status);
CREATE INDEX idx_auth_member_valid ON auth.authorization_request(member_id, valid_from, valid_through);

-- Partial Indexes
CREATE INDEX idx_claim_pending ON claims.claim(status) WHERE status IN ('pending', 'pended');
CREATE INDEX idx_payment_failed ON payment.payment_transaction(status) WHERE status = 'failed';

-- Expression Indexes
CREATE INDEX idx_member_fullname ON member.member(lower(last_name || ', ' || first_name));
CREATE INDEX idx_claim_month ON claims.claim(date_trunc('month', service_date_from));

-- BRIN Indexes for Time Series
CREATE INDEX idx_audit_timestamp_brin ON audit.audit_log USING BRIN(action_timestamp);
CREATE INDEX idx_claim_created_brin ON claims.claim USING BRIN(created_at);
```

### 10.2 Materialized Views
```sql
-- Member Summary View
CREATE MATERIALIZED VIEW analytics.member_summary AS
SELECT 
    m.member_id,
    m.member_number,
    m.first_name || ' ' || m.last_name as full_name,
    mc.policy_id,
    mc.plan_id,
    COUNT(DISTINCT c.claim_id) as total_claims,
    SUM(c.paid_amount) as total_paid,
    MAX(c.service_date_to) as last_service_date
FROM member.member m
LEFT JOIN member.member_coverage mc ON m.member_id = mc.member_id
LEFT JOIN claims.claim c ON m.member_id = c.member_id
GROUP BY m.member_id, m.member_number, m.first_name, m.last_name, mc.policy_id, mc.plan_id;

CREATE UNIQUE INDEX ON analytics.member_summary(member_id);

-- Provider Performance View
CREATE MATERIALIZED VIEW analytics.provider_performance_summary AS
SELECT 
    p.provider_id,
    p.provider_code,
    p.legal_name,
    COUNT(DISTINCT c.claim_id) as claim_count,
    AVG(c.paid_amount) as avg_claim_amount,
    SUM(c.paid_amount) as total_paid,
    AVG(EXTRACT(epoch FROM c.adjudicated_at - c.created_at)/86400) as avg_processing_days
FROM provider.provider_organization p
LEFT JOIN claims.claim c ON p.provider_id = c.provider_id
WHERE c.created_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY p.provider_id, p.provider_code, p.legal_name;

CREATE UNIQUE INDEX ON analytics.provider_performance_summary(provider_id);
```

---

## 11. DATA GOVERNANCE

### 11.1 Data Quality Rules
```yaml
Quality_Rules:
  Completeness:
    - Member email or phone required
    - Provider NPI or tax_id required
    - Claim diagnosis required
    
  Consistency:
    - Service dates <= current date
    - Birth date < coverage start date
    - Termination date > effective date
    
  Accuracy:
    - Valid ICD-10 codes
    - Valid provider license
    - Valid member ID format
    
  Uniqueness:
    - No duplicate member IDs
    - No duplicate claim numbers
    - No duplicate provider tax IDs
```

### 11.2 Data Retention Policy
```yaml
Retention_Periods:
  Claims: 7 years
  Authorizations: 7 years
  Member_Data: 7 years after termination
  Provider_Data: 10 years
  Audit_Logs: 10 years
  Payment_Records: 10 years
  
Archival_Strategy:
  Hot_Storage: Current year + 1
  Warm_Storage: 2-5 years
  Cold_Storage: 6+ years
  
Purge_Policy:
  Soft_Delete: Mark as deleted
  Hard_Delete: After retention period
  Anonymization: For analytics after purge
```

---

## 12. SECURITY & ENCRYPTION

### 12.1 Sensitive Data Encryption
```sql
-- Encryption Functions
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypted Columns (using application-level encryption)
-- member.member: national_id, passport_number, tax_id
-- member.member_payment_method: account_number, wallet_id
-- payment.payment_transaction: payment_details

-- Row-Level Security
ALTER TABLE member.member ENABLE ROW LEVEL SECURITY;

CREATE POLICY member_access ON member.member
    FOR ALL
    USING (
        member_id = current_setting('app.current_member_id')::UUID
        OR 
        EXISTS (
            SELECT 1 FROM auth.user_permission
            WHERE user_id = current_setting('app.current_user_id')::UUID
            AND permission IN ('member.read', 'member.admin')
        )
    );
```

### 12.2 Audit Requirements
```sql
-- Trigger for automatic audit logging
CREATE OR REPLACE FUNCTION audit.log_changes()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit.audit_log (
        entity_type,
        entity_id,
        action,
        user_id,
        old_values,
        new_values
    ) VALUES (
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        TG_OP,
        current_setting('app.current_user_id')::UUID,
        to_jsonb(OLD),
        to_jsonb(NEW)
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to sensitive tables
CREATE TRIGGER audit_member_changes
    AFTER INSERT OR UPDATE OR DELETE ON member.member
    FOR EACH ROW EXECUTE FUNCTION audit.log_changes();
```

---

**Related Documents**:
- UI/UX Design Specifications
- Process Flow Diagrams
- API Specifications
- System Architecture