-- Claims-Askes Database Initialization
-- Microservices Architecture with Schema Separation
-- Each service owns its schema, no cross-schema direct access

-- ==================== CREATE DATABASE ====================
-- Run this as superuser
-- CREATE DATABASE claims_askes;

-- ==================== CREATE SCHEMAS ====================
-- Each microservice owns its schema
CREATE SCHEMA IF NOT EXISTS claims_service;
CREATE SCHEMA IF NOT EXISTS authorization_service;
CREATE SCHEMA IF NOT EXISTS adjudication_service;
CREATE SCHEMA IF NOT EXISTS payment_service;
CREATE SCHEMA IF NOT EXISTS member_service;
CREATE SCHEMA IF NOT EXISTS provider_service;
CREATE SCHEMA IF NOT EXISTS benefit_service;
CREATE SCHEMA IF NOT EXISTS policy_service;
CREATE SCHEMA IF NOT EXISTS notification_service;
CREATE SCHEMA IF NOT EXISTS document_service;

-- Shared schemas
CREATE SCHEMA IF NOT EXISTS common;  -- Shared reference data
CREATE SCHEMA IF NOT EXISTS audit;   -- Audit logs

-- ==================== CREATE USERS ====================
-- Each service has its own database user
CREATE USER claims_service_user WITH PASSWORD 'claims_pass_dev';
CREATE USER authorization_service_user WITH PASSWORD 'auth_pass_dev';
CREATE USER adjudication_service_user WITH PASSWORD 'adj_pass_dev';
CREATE USER payment_service_user WITH PASSWORD 'payment_pass_dev';
CREATE USER member_service_user WITH PASSWORD 'member_pass_dev';
CREATE USER provider_service_user WITH PASSWORD 'provider_pass_dev';
CREATE USER benefit_service_user WITH PASSWORD 'benefit_pass_dev';
CREATE USER policy_service_user WITH PASSWORD 'policy_pass_dev';
CREATE USER notification_service_user WITH PASSWORD 'notif_pass_dev';
CREATE USER document_service_user WITH PASSWORD 'doc_pass_dev';

-- ==================== GRANT PERMISSIONS ====================
-- Each user can only access their own schema
GRANT ALL ON SCHEMA claims_service TO claims_service_user;
GRANT ALL ON ALL TABLES IN SCHEMA claims_service TO claims_service_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA claims_service TO claims_service_user;

GRANT ALL ON SCHEMA authorization_service TO authorization_service_user;
GRANT ALL ON ALL TABLES IN SCHEMA authorization_service TO authorization_service_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA authorization_service TO authorization_service_user;

GRANT ALL ON SCHEMA adjudication_service TO adjudication_service_user;
GRANT ALL ON ALL TABLES IN SCHEMA adjudication_service TO adjudication_service_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA adjudication_service TO adjudication_service_user;

GRANT ALL ON SCHEMA payment_service TO payment_service_user;
GRANT ALL ON ALL TABLES IN SCHEMA payment_service TO payment_service_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA payment_service TO payment_service_user;

GRANT ALL ON SCHEMA member_service TO member_service_user;
GRANT ALL ON ALL TABLES IN SCHEMA member_service TO member_service_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA member_service TO member_service_user;

GRANT ALL ON SCHEMA provider_service TO provider_service_user;
GRANT ALL ON ALL TABLES IN SCHEMA provider_service TO provider_service_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA provider_service TO provider_service_user;

GRANT ALL ON SCHEMA benefit_service TO benefit_service_user;
GRANT ALL ON ALL TABLES IN SCHEMA benefit_service TO benefit_service_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA benefit_service TO benefit_service_user;

GRANT ALL ON SCHEMA policy_service TO policy_service_user;
GRANT ALL ON ALL TABLES IN SCHEMA policy_service TO policy_service_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA policy_service TO policy_service_user;

GRANT ALL ON SCHEMA notification_service TO notification_service_user;
GRANT ALL ON ALL TABLES IN SCHEMA notification_service TO notification_service_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA notification_service TO notification_service_user;

GRANT ALL ON SCHEMA document_service TO document_service_user;
GRANT ALL ON ALL TABLES IN SCHEMA document_service TO document_service_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA document_service TO document_service_user;

-- Grant read access to common schema for all services
GRANT USAGE ON SCHEMA common TO claims_service_user, authorization_service_user, 
    adjudication_service_user, payment_service_user, member_service_user,
    provider_service_user, benefit_service_user, policy_service_user,
    notification_service_user, document_service_user;

GRANT SELECT ON ALL TABLES IN SCHEMA common TO claims_service_user, authorization_service_user,
    adjudication_service_user, payment_service_user, member_service_user,
    provider_service_user, benefit_service_user, policy_service_user,
    notification_service_user, document_service_user;

-- ==================== COMMON SCHEMA TABLES ====================
-- Reference data shared across services (read-only for services)

CREATE TABLE common.country (
    id SERIAL PRIMARY KEY,
    code VARCHAR(2) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE common.province (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    country_id INTEGER REFERENCES common.country(id),
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE common.city (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    province_id INTEGER REFERENCES common.province(id),
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE common.diagnosis_code (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    category VARCHAR(100),
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE common.procedure_code (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    category VARCHAR(100),
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE common.currency (
    id SERIAL PRIMARY KEY,
    code VARCHAR(3) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL,
    symbol VARCHAR(5),
    is_active BOOLEAN DEFAULT true
);

-- ==================== CLAIMS SERVICE SCHEMA ====================
CREATE TABLE claims_service.claim (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_number VARCHAR(50) UNIQUE NOT NULL,
    member_id UUID NOT NULL,  -- References member-service via API
    provider_id UUID NOT NULL, -- References provider-service via API
    policy_id UUID NOT NULL,   -- References policy-service via API
    
    claim_type VARCHAR(20) NOT NULL,
    service_type VARCHAR(20) NOT NULL,
    admission_date DATE,
    discharge_date DATE,
    service_date DATE NOT NULL,
    
    status VARCHAR(30) NOT NULL DEFAULT 'submitted',
    submission_date TIMESTAMP NOT NULL DEFAULT NOW(),
    
    total_charged_amount DECIMAL(15,2),
    total_approved_amount DECIMAL(15,2),
    total_paid_amount DECIMAL(15,2),
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE claims_service.claim_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id UUID NOT NULL REFERENCES claims_service.claim(id),
    benefit_code VARCHAR(50) NOT NULL,
    service_code VARCHAR(50),
    diagnosis_code VARCHAR(20),
    procedure_code VARCHAR(20),
    quantity INTEGER DEFAULT 1,
    unit_price DECIMAL(15,2),
    charged_amount DECIMAL(15,2) NOT NULL,
    approved_amount DECIMAL(15,2),
    paid_amount DECIMAL(15,2),
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ==================== MEMBER SERVICE SCHEMA ====================
CREATE TABLE member_service.member (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_number VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    gender VARCHAR(10) NOT NULL,
    national_id VARCHAR(50),
    email VARCHAR(255),
    phone VARCHAR(50),
    address_line1 VARCHAR(255),
    city_id INTEGER,  -- References common.city
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    enrollment_date DATE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE member_service.member_coverage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id UUID NOT NULL REFERENCES member_service.member(id),
    policy_id UUID NOT NULL,  -- References policy-service via API
    plan_id UUID NOT NULL,    -- References benefit-service via API
    relationship VARCHAR(20) NOT NULL,
    coverage_start_date DATE NOT NULL,
    coverage_end_date DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ==================== PROVIDER SERVICE SCHEMA ====================
CREATE TABLE provider_service.provider (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_code VARCHAR(50) UNIQUE NOT NULL,
    provider_name VARCHAR(255) NOT NULL,
    provider_type VARCHAR(50) NOT NULL,
    provider_class VARCHAR(20),
    is_network BOOLEAN DEFAULT true,
    address VARCHAR(500),
    city_id INTEGER,  -- References common.city
    phone VARCHAR(50),
    email VARCHAR(255),
    bank_name VARCHAR(100),
    bank_account VARCHAR(50),
    tax_id VARCHAR(50),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ==================== BENEFIT SERVICE SCHEMA ====================
CREATE TABLE benefit_service.plan (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_code VARCHAR(50) UNIQUE NOT NULL,
    plan_name VARCHAR(255) NOT NULL,
    plan_type VARCHAR(50) NOT NULL,
    annual_limit DECIMAL(15,2),
    individual_deductible DECIMAL(15,2) DEFAULT 0,
    family_deductible DECIMAL(15,2) DEFAULT 0,
    effective_date DATE NOT NULL,
    termination_date DATE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE benefit_service.plan_benefit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID NOT NULL REFERENCES benefit_service.plan(id),
    benefit_code VARCHAR(50) NOT NULL,
    benefit_name VARCHAR(255) NOT NULL,
    benefit_category VARCHAR(50) NOT NULL,
    coverage_type VARCHAR(20) DEFAULT 'covered',
    limit_type VARCHAR(20),
    limit_amount DECIMAL(15,2),
    limit_days INTEGER,
    limit_visits INTEGER,
    coinsurance_percentage DECIMAL(5,2) DEFAULT 0,
    copay_amount DECIMAL(15,2) DEFAULT 0,
    requires_authorization BOOLEAN DEFAULT false,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(plan_id, benefit_code)
);

-- ==================== POLICY SERVICE SCHEMA ====================
CREATE TABLE policy_service.policy (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_number VARCHAR(50) UNIQUE NOT NULL,
    company_name VARCHAR(255),
    policy_type VARCHAR(30) NOT NULL,
    plan_id UUID NOT NULL,  -- References benefit-service via API
    effective_date DATE NOT NULL,
    renewal_date DATE NOT NULL,
    total_members INTEGER DEFAULT 0,
    total_premium DECIMAL(15,2),
    funding_type VARCHAR(20),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ==================== AUTHORIZATION SERVICE SCHEMA ====================
CREATE TABLE authorization_service.authorization (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    authorization_number VARCHAR(50) UNIQUE NOT NULL,
    member_id UUID NOT NULL,   -- References member-service via API
    provider_id UUID NOT NULL,  -- References provider-service via API
    service_type VARCHAR(50) NOT NULL,
    procedure_code VARCHAR(20),
    diagnosis_code VARCHAR(20),
    valid_from DATE NOT NULL,
    valid_to DATE NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    approved_amount DECIMAL(15,2),
    approved_days INTEGER,
    decision_date TIMESTAMP,
    decision_by VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ==================== ADJUDICATION SERVICE SCHEMA ====================
CREATE TABLE adjudication_service.adjudication_result (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id UUID NOT NULL,  -- References claims-service via API
    adjudication_date TIMESTAMP NOT NULL DEFAULT NOW(),
    total_charged DECIMAL(15,2),
    total_allowed DECIMAL(15,2),
    total_paid DECIMAL(15,2),
    member_responsibility DECIMAL(15,2),
    deductible_applied DECIMAL(15,2),
    coinsurance_amount DECIMAL(15,2),
    copay_amount DECIMAL(15,2),
    status VARCHAR(30) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ==================== PAYMENT SERVICE SCHEMA ====================
CREATE TABLE payment_service.payment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_number VARCHAR(50) UNIQUE NOT NULL,
    claim_id UUID,  -- References claims-service via API
    payment_type VARCHAR(20) NOT NULL,
    payment_method VARCHAR(20) NOT NULL,
    payment_amount DECIMAL(15,2) NOT NULL,
    payee_type VARCHAR(20) NOT NULL,
    payee_id UUID NOT NULL,
    bank_name VARCHAR(100),
    account_number VARCHAR(50),
    reference_number VARCHAR(50),
    payment_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    payment_date DATE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ==================== NOTIFICATION SERVICE SCHEMA ====================
CREATE TABLE notification_service.notification (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_type VARCHAR(20) NOT NULL,
    recipient_id UUID NOT NULL,
    channel VARCHAR(20) NOT NULL,
    template_id VARCHAR(50),
    subject VARCHAR(255),
    content TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    sent_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ==================== DOCUMENT SERVICE SCHEMA ====================
CREATE TABLE document_service.document (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    checksum VARCHAR(255),
    uploaded_by UUID,
    uploaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ==================== AUDIT SCHEMA ====================
CREATE TABLE audit.audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_name VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL,
    user_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ==================== INDEXES ====================
-- Claims Service
CREATE INDEX idx_claims_member ON claims_service.claim(member_id);
CREATE INDEX idx_claims_provider ON claims_service.claim(provider_id);
CREATE INDEX idx_claims_status ON claims_service.claim(status);
CREATE INDEX idx_claims_service_date ON claims_service.claim(service_date);

-- Member Service
CREATE INDEX idx_member_number ON member_service.member(member_number);
CREATE INDEX idx_member_status ON member_service.member(status);
CREATE INDEX idx_member_coverage_member ON member_service.member_coverage(member_id);

-- Provider Service
CREATE INDEX idx_provider_code ON provider_service.provider(provider_code);
CREATE INDEX idx_provider_type ON provider_service.provider(provider_type);
CREATE INDEX idx_provider_status ON provider_service.provider(status);

-- Authorization Service
CREATE INDEX idx_auth_member ON authorization_service.authorization(member_id);
CREATE INDEX idx_auth_provider ON authorization_service.authorization(provider_id);
CREATE INDEX idx_auth_status ON authorization_service.authorization(status);

-- Payment Service
CREATE INDEX idx_payment_claim ON payment_service.payment(claim_id);
CREATE INDEX idx_payment_status ON payment_service.payment(payment_status);

-- Document Service
CREATE INDEX idx_document_entity ON document_service.document(entity_type, entity_id);

-- Audit
CREATE INDEX idx_audit_service ON audit.audit_log(service_name);
CREATE INDEX idx_audit_entity ON audit.audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_created ON audit.audit_log(created_at);

-- ==================== STORED PROCEDURES ====================
-- Update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update trigger to tables with updated_at
CREATE TRIGGER update_claims_timestamp BEFORE UPDATE ON claims_service.claim
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_member_timestamp BEFORE UPDATE ON member_service.member
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_provider_timestamp BEFORE UPDATE ON provider_service.provider
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_policy_timestamp BEFORE UPDATE ON policy_service.policy
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ==================== SAMPLE DATA ====================
-- Insert reference data
INSERT INTO common.currency (code, name, symbol) VALUES
    ('IDR', 'Indonesian Rupiah', 'Rp'),
    ('USD', 'US Dollar', '$');

INSERT INTO common.country (code, name) VALUES
    ('ID', 'Indonesia'),
    ('SG', 'Singapore');

INSERT INTO common.province (code, name, country_id) VALUES
    ('JKT', 'DKI Jakarta', 1),
    ('JBR', 'Jawa Barat', 1),
    ('JTM', 'Jawa Timur', 1);

INSERT INTO common.city (code, name, province_id) VALUES
    ('JKT01', 'Jakarta Pusat', 1),
    ('JKT02', 'Jakarta Selatan', 1),
    ('BDG01', 'Bandung', 2),
    ('SBY01', 'Surabaya', 3);

-- ==================== PERMISSIONS NOTE ====================
-- Each service should only connect with its own user credentials
-- Service-to-service communication happens via REST APIs, not database
-- Example connection strings:
-- Claims Service: postgresql://claims_service_user:claims_pass_dev@localhost/claims_askes
-- Member Service: postgresql://member_service_user:member_pass_dev@localhost/claims_askes
-- Provider Service: postgresql://provider_service_user:provider_pass_dev@localhost/claims_askes