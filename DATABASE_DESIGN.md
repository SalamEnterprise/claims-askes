# Database Design - Claims-Askes Platform

## Overview
Core database design for health insurance claims processing system with focus on Indonesian market requirements.

## Schema Organization

```sql
-- Logical separation by domain
CREATE SCHEMA claims;      -- Claims processing
CREATE SCHEMA member;      -- Member management  
CREATE SCHEMA provider;    -- Provider network
CREATE SCHEMA benefit;     -- Benefit configuration
CREATE SCHEMA policy;      -- Policy administration
CREATE SCHEMA billing;     -- Payment and billing
CREATE SCHEMA audit;       -- Audit and compliance
```

## Core Tables

### Claims Domain

```sql
-- Main claims table
CREATE TABLE claims.claim (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_number VARCHAR(50) UNIQUE NOT NULL,
    member_id UUID NOT NULL,
    provider_id UUID NOT NULL,
    policy_id UUID NOT NULL,
    
    -- Claim details
    claim_type VARCHAR(20) NOT NULL, -- 'cashless', 'reimbursement'
    service_type VARCHAR(20) NOT NULL, -- 'inpatient', 'outpatient', 'dental', 'optical'
    admission_date DATE,
    discharge_date DATE,
    service_date DATE NOT NULL,
    
    -- Status tracking
    status VARCHAR(30) NOT NULL DEFAULT 'submitted',
    submission_date TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Financial
    total_charged_amount DECIMAL(15,2),
    total_approved_amount DECIMAL(15,2),
    total_paid_amount DECIMAL(15,2),
    member_responsibility DECIMAL(15,2),
    
    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(100),
    updated_by VARCHAR(100)
);

-- Claim line items
CREATE TABLE claims.claim_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id UUID NOT NULL REFERENCES claims.claim(id),
    
    -- Service details
    benefit_code VARCHAR(50) NOT NULL,
    service_code VARCHAR(50),
    diagnosis_code VARCHAR(20),
    procedure_code VARCHAR(20),
    
    -- Quantities and amounts
    quantity INTEGER DEFAULT 1,
    unit_price DECIMAL(15,2),
    charged_amount DECIMAL(15,2) NOT NULL,
    approved_amount DECIMAL(15,2),
    paid_amount DECIMAL(15,2),
    
    -- Adjudication results
    deductible_amount DECIMAL(15,2) DEFAULT 0,
    coinsurance_amount DECIMAL(15,2) DEFAULT 0,
    copay_amount DECIMAL(15,2) DEFAULT 0,
    
    -- Status
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    denial_reason VARCHAR(500),
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Claim documents
CREATE TABLE claims.claim_document (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id UUID NOT NULL REFERENCES claims.claim(id),
    document_type VARCHAR(50) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    uploaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    uploaded_by VARCHAR(100)
);

-- Authorization tracking
CREATE TABLE claims.authorization (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    authorization_number VARCHAR(50) UNIQUE NOT NULL,
    claim_id UUID REFERENCES claims.claim(id),
    member_id UUID NOT NULL,
    provider_id UUID NOT NULL,
    
    -- Authorization details
    service_type VARCHAR(50) NOT NULL,
    procedure_code VARCHAR(20),
    diagnosis_code VARCHAR(20),
    
    -- Validity period
    valid_from DATE NOT NULL,
    valid_to DATE NOT NULL,
    
    -- Status
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    approved_amount DECIMAL(15,2),
    approved_days INTEGER,
    
    -- Decision tracking
    decision_date TIMESTAMP,
    decision_by VARCHAR(100),
    decision_notes TEXT,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### Member Domain

```sql
-- Member master table
CREATE TABLE member.member (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_number VARCHAR(50) UNIQUE NOT NULL,
    
    -- Personal information
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    gender VARCHAR(10) NOT NULL,
    
    -- Identification
    national_id VARCHAR(50),
    passport_number VARCHAR(50),
    
    -- Contact
    email VARCHAR(255),
    phone VARCHAR(50),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    province VARCHAR(100),
    postal_code VARCHAR(20),
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    enrollment_date DATE NOT NULL,
    termination_date DATE,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Member coverage
CREATE TABLE member.member_coverage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id UUID NOT NULL REFERENCES member.member(id),
    policy_id UUID NOT NULL,
    plan_id UUID NOT NULL,
    
    -- Coverage details
    relationship VARCHAR(20) NOT NULL, -- 'employee', 'spouse', 'child'
    coverage_start_date DATE NOT NULL,
    coverage_end_date DATE,
    
    -- Coverage layers (Indonesian specific)
    inner_limit_applicable BOOLEAN DEFAULT true,
    annual_cap_applicable BOOLEAN DEFAULT false,
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Member accumulators
CREATE TABLE member.accumulator (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id UUID NOT NULL REFERENCES member.member(id),
    plan_id UUID NOT NULL,
    benefit_code VARCHAR(50),
    
    -- Period
    year INTEGER NOT NULL,
    
    -- Accumulator values
    limit_amount DECIMAL(15,2),
    used_amount DECIMAL(15,2) DEFAULT 0,
    remaining_amount DECIMAL(15,2),
    
    -- Counts
    visit_limit INTEGER,
    visit_count INTEGER DEFAULT 0,
    remaining_visits INTEGER,
    
    -- Deductibles
    deductible_limit DECIMAL(15,2),
    deductible_met DECIMAL(15,2) DEFAULT 0,
    
    last_updated TIMESTAMP NOT NULL DEFAULT NOW(),
    
    UNIQUE(member_id, plan_id, benefit_code, year)
);
```

### Provider Domain

```sql
-- Provider master table  
CREATE TABLE provider.provider (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_code VARCHAR(50) UNIQUE NOT NULL,
    
    -- Provider information
    provider_name VARCHAR(255) NOT NULL,
    provider_type VARCHAR(50) NOT NULL, -- 'hospital', 'clinic', 'pharmacy', 'lab'
    
    -- Classification
    provider_class VARCHAR(20), -- 'A', 'B', 'C', 'D'
    is_network BOOLEAN DEFAULT true,
    
    -- Contact
    address VARCHAR(500),
    city VARCHAR(100),
    province VARCHAR(100),
    phone VARCHAR(50),
    email VARCHAR(255),
    
    -- Banking
    bank_name VARCHAR(100),
    bank_account VARCHAR(50),
    tax_id VARCHAR(50),
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    contract_start_date DATE,
    contract_end_date DATE,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Provider contracts
CREATE TABLE provider.provider_contract (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id UUID NOT NULL REFERENCES provider.provider(id),
    contract_number VARCHAR(50) UNIQUE NOT NULL,
    
    -- Contract terms
    effective_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    
    -- Payment terms
    payment_method VARCHAR(20), -- 'fee_for_service', 'capitation'
    discount_percentage DECIMAL(5,2),
    
    -- Service agreements
    cashless_enabled BOOLEAN DEFAULT true,
    reimbursement_enabled BOOLEAN DEFAULT true,
    
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### Benefit Domain

```sql
-- Benefit plans
CREATE TABLE benefit.plan (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_code VARCHAR(50) UNIQUE NOT NULL,
    plan_name VARCHAR(255) NOT NULL,
    plan_type VARCHAR(50) NOT NULL, -- 'basic', 'standard', 'premium'
    
    -- Plan limits
    annual_limit DECIMAL(15,2),
    lifetime_limit DECIMAL(15,2),
    
    -- Deductibles
    individual_deductible DECIMAL(15,2) DEFAULT 0,
    family_deductible DECIMAL(15,2) DEFAULT 0,
    
    -- Out of pocket max
    individual_oop_max DECIMAL(15,2),
    family_oop_max DECIMAL(15,2),
    
    effective_date DATE NOT NULL,
    termination_date DATE,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Plan benefits configuration
CREATE TABLE benefit.plan_benefit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID NOT NULL REFERENCES benefit.plan(id),
    
    -- Benefit identification
    benefit_code VARCHAR(50) NOT NULL,
    benefit_name VARCHAR(255) NOT NULL,
    benefit_category VARCHAR(50) NOT NULL,
    
    -- Coverage configuration
    coverage_type VARCHAR(20) DEFAULT 'covered', -- 'covered', 'not_covered', 'limited'
    
    -- Limits
    limit_type VARCHAR(20), -- 'per_incident', 'per_day', 'per_year'
    limit_amount DECIMAL(15,2),
    limit_days INTEGER,
    limit_visits INTEGER,
    
    -- Cost sharing
    coinsurance_percentage DECIMAL(5,2) DEFAULT 0,
    copay_amount DECIMAL(15,2) DEFAULT 0,
    
    -- Special conditions
    requires_authorization BOOLEAN DEFAULT false,
    waiting_period_days INTEGER DEFAULT 0,
    
    -- Network applicability
    in_network_covered BOOLEAN DEFAULT true,
    out_network_covered BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    UNIQUE(plan_id, benefit_code)
);

-- Exclusions
CREATE TABLE benefit.exclusion (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID REFERENCES benefit.plan(id),
    
    exclusion_code VARCHAR(50) NOT NULL,
    exclusion_description TEXT NOT NULL,
    
    -- Categorization
    exclusion_type VARCHAR(50), -- 'diagnosis', 'procedure', 'condition'
    icd_code VARCHAR(20),
    
    effective_date DATE,
    termination_date DATE,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### Policy Domain

```sql
-- Policy master
CREATE TABLE policy.policy (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_number VARCHAR(50) UNIQUE NOT NULL,
    
    -- Policy holder
    company_name VARCHAR(255),
    company_id VARCHAR(50),
    
    -- Policy details
    policy_type VARCHAR(30) NOT NULL, -- 'group', 'individual'
    plan_id UUID NOT NULL,
    
    -- Period
    effective_date DATE NOT NULL,
    renewal_date DATE NOT NULL,
    termination_date DATE,
    
    -- Enrollment
    total_members INTEGER DEFAULT 0,
    total_premium DECIMAL(15,2),
    
    -- Funding (Indonesian specific)
    funding_type VARCHAR(20), -- 'aso', 'full_insured'
    aso_fund_balance DECIMAL(15,2) DEFAULT 0,
    buffer_fund_balance DECIMAL(15,2) DEFAULT 0,
    
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### Billing Domain

```sql
-- Payment transactions
CREATE TABLE billing.payment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_number VARCHAR(50) UNIQUE NOT NULL,
    claim_id UUID REFERENCES claims.claim(id),
    
    -- Payment details
    payment_type VARCHAR(20) NOT NULL, -- 'claim', 'reimbursement'
    payment_method VARCHAR(20) NOT NULL, -- 'bank_transfer', 'check'
    
    -- Amounts
    payment_amount DECIMAL(15,2) NOT NULL,
    
    -- Recipient
    payee_type VARCHAR(20) NOT NULL, -- 'provider', 'member'
    payee_id UUID NOT NULL,
    
    -- Banking details
    bank_name VARCHAR(100),
    account_number VARCHAR(50),
    reference_number VARCHAR(50),
    
    -- Status
    payment_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    payment_date DATE,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- EOB (Explanation of Benefits)
CREATE TABLE billing.eob (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    eob_number VARCHAR(50) UNIQUE NOT NULL,
    claim_id UUID NOT NULL REFERENCES claims.claim(id),
    member_id UUID NOT NULL,
    
    -- EOB details
    service_date DATE NOT NULL,
    provider_name VARCHAR(255),
    
    -- Financial summary
    total_charged DECIMAL(15,2),
    total_approved DECIMAL(15,2),
    total_paid DECIMAL(15,2),
    member_responsibility DECIMAL(15,2),
    
    -- Breakdown
    deductible_applied DECIMAL(15,2) DEFAULT 0,
    coinsurance_amount DECIMAL(15,2) DEFAULT 0,
    copay_amount DECIMAL(15,2) DEFAULT 0,
    
    generated_date TIMESTAMP NOT NULL DEFAULT NOW(),
    sent_date TIMESTAMP
);
```

## Indexes

```sql
-- Claims indexes
CREATE INDEX idx_claim_member ON claims.claim(member_id);
CREATE INDEX idx_claim_provider ON claims.claim(provider_id);
CREATE INDEX idx_claim_status ON claims.claim(status);
CREATE INDEX idx_claim_service_date ON claims.claim(service_date);
CREATE INDEX idx_claim_submission_date ON claims.claim(submission_date);

-- Member indexes
CREATE INDEX idx_member_status ON member.member(status);
CREATE INDEX idx_member_coverage_member ON member.member_coverage(member_id);
CREATE INDEX idx_accumulator_member ON member.accumulator(member_id, year);

-- Provider indexes
CREATE INDEX idx_provider_status ON provider.provider(status);
CREATE INDEX idx_provider_type ON provider.provider(provider_type);

-- Benefit indexes
CREATE INDEX idx_plan_benefit_plan ON benefit.plan_benefit(plan_id);
CREATE INDEX idx_plan_benefit_code ON benefit.plan_benefit(benefit_code);
```

## Views

```sql
-- Active members with coverage
CREATE VIEW member.active_members_view AS
SELECT 
    m.id,
    m.member_number,
    m.first_name || ' ' || m.last_name as full_name,
    mc.policy_id,
    mc.plan_id,
    mc.coverage_start_date,
    mc.coverage_end_date
FROM member.member m
JOIN member.member_coverage mc ON m.id = mc.member_id
WHERE m.status = 'active' 
  AND mc.status = 'active'
  AND CURRENT_DATE BETWEEN mc.coverage_start_date 
      AND COALESCE(mc.coverage_end_date, '9999-12-31');

-- Claim summary view
CREATE VIEW claims.claim_summary_view AS
SELECT 
    c.id,
    c.claim_number,
    m.member_number,
    m.first_name || ' ' || m.last_name as member_name,
    p.provider_name,
    c.service_date,
    c.status,
    c.total_charged_amount,
    c.total_approved_amount,
    c.total_paid_amount
FROM claims.claim c
JOIN member.member m ON c.member_id = m.id
JOIN provider.provider p ON c.provider_id = p.id;
```

## Functions and Procedures

```sql
-- Function to calculate remaining benefit
CREATE OR REPLACE FUNCTION benefit.calculate_remaining_benefit(
    p_member_id UUID,
    p_benefit_code VARCHAR,
    p_year INTEGER
) RETURNS DECIMAL AS $$
DECLARE
    v_limit DECIMAL;
    v_used DECIMAL;
BEGIN
    SELECT limit_amount, used_amount
    INTO v_limit, v_used
    FROM member.accumulator
    WHERE member_id = p_member_id
      AND benefit_code = p_benefit_code
      AND year = p_year;
    
    RETURN COALESCE(v_limit - v_used, 0);
END;
$$ LANGUAGE plpgsql;

-- Procedure to update accumulator
CREATE OR REPLACE PROCEDURE member.update_accumulator(
    p_member_id UUID,
    p_benefit_code VARCHAR,
    p_amount DECIMAL,
    p_year INTEGER
) AS $$
BEGIN
    UPDATE member.accumulator
    SET used_amount = used_amount + p_amount,
        remaining_amount = limit_amount - (used_amount + p_amount),
        last_updated = NOW()
    WHERE member_id = p_member_id
      AND benefit_code = p_benefit_code
      AND year = p_year;
END;
$$ LANGUAGE plpgsql;
```

## Triggers

```sql
-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to tables
CREATE TRIGGER update_claim_timestamp
BEFORE UPDATE ON claims.claim
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_member_timestamp
BEFORE UPDATE ON member.member
FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

## Partitioning Strategy

```sql
-- Partition claims table by year
CREATE TABLE claims.claim_2024 PARTITION OF claims.claim
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE claims.claim_2025 PARTITION OF claims.claim
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- Partition audit logs by month
CREATE TABLE audit.log_2024_01 PARTITION OF audit.audit_log
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

## Security Considerations

### Row-Level Security
```sql
-- Enable RLS
ALTER TABLE claims.claim ENABLE ROW LEVEL SECURITY;

-- Policy for members to see only their claims
CREATE POLICY member_claim_policy ON claims.claim
FOR SELECT
TO member_role
USING (member_id = current_setting('app.current_member_id')::UUID);
```

### Column Encryption
```sql
-- Encrypt sensitive columns
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Example: Encrypt national ID
ALTER TABLE member.member 
ADD COLUMN national_id_encrypted BYTEA;

UPDATE member.member 
SET national_id_encrypted = pgp_sym_encrypt(national_id, 'encryption_key');
```

## Performance Optimization

### Connection Pooling
```python
# SQLAlchemy configuration
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/claims"
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_MAX_OVERFLOW = 40
SQLALCHEMY_POOL_TIMEOUT = 30
```

### Query Optimization
- Use prepared statements
- Implement query result caching
- Use database views for complex queries
- Implement read replicas for reporting

## Backup and Recovery

### Backup Strategy
```bash
# Daily full backup
pg_dump -h localhost -U postgres -d claims_askes > backup_$(date +%Y%m%d).sql

# Continuous archiving with WAL
archive_mode = on
archive_command = 'cp %p /backup/wal/%f'
```

### Point-in-Time Recovery
```bash
# Restore to specific time
pg_restore -h localhost -U postgres -d claims_askes \
  --recovery-target-time="2024-01-15 14:30:00" backup.sql
```