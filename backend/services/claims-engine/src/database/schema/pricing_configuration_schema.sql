-- =====================================================
-- PRICING CONFIGURATION SCHEMA
-- Group Health Insurance Product Setup & Premium Calculation
-- =====================================================

-- Drop existing tables if they exist (for clean setup)
DROP SCHEMA IF EXISTS pricing CASCADE;
CREATE SCHEMA pricing;

-- =====================================================
-- CORE PRICING TABLES
-- =====================================================

-- Product Templates (Base products like IP-1000)
CREATE TABLE pricing.product_template (
    template_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_code VARCHAR(20) UNIQUE NOT NULL, -- IP-1000, OP-500, etc
    template_name VARCHAR(100) NOT NULL,
    product_category VARCHAR(50) NOT NULL, -- INPATIENT, OUTPATIENT, DENTAL, MATERNITY
    base_premium_adult_male DECIMAL(12,2),
    base_premium_adult_female DECIMAL(12,2),
    base_premium_child DECIMAL(12,2),
    version VARCHAR(10) DEFAULT 'v4.3',
    effective_from DATE NOT NULL,
    effective_to DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Age Band Premium Multipliers
CREATE TABLE pricing.age_band_multiplier (
    band_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID REFERENCES pricing.product_template(template_id),
    age_from INTEGER NOT NULL,
    age_to INTEGER NOT NULL,
    gender VARCHAR(10) NOT NULL CHECK (gender IN ('MALE', 'FEMALE', 'CHILD')),
    multiplier DECIMAL(5,3) NOT NULL DEFAULT 1.000,
    UNIQUE(template_id, age_from, age_to, gender)
);

-- Terms & Conditions Factor Configuration
CREATE TABLE pricing.tc_factor_config (
    factor_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    factor_code VARCHAR(20) UNIQUE NOT NULL, -- TCGC-01, TCNBIP-01, etc
    factor_category VARCHAR(50) NOT NULL, -- GENERAL, INPATIENT, OUTPATIENT
    factor_name VARCHAR(100) NOT NULL,
    factor_description TEXT,
    is_active BOOLEAN DEFAULT true,
    display_order INTEGER
);

-- TC Factor Options (dropdown values)
CREATE TABLE pricing.tc_factor_option (
    option_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    factor_id UUID REFERENCES pricing.tc_factor_config(factor_id),
    option_value VARCHAR(200) NOT NULL,
    option_label VARCHAR(200) NOT NULL,
    multiplier DECIMAL(5,3) NOT NULL DEFAULT 1.000,
    is_default BOOLEAN DEFAULT false,
    min_participants INTEGER, -- For participant-based factors
    max_participants INTEGER,
    display_order INTEGER
);

-- =====================================================
-- POLICY CONFIGURATION TABLES
-- =====================================================

-- Policy Pricing Configuration (Main configuration record)
CREATE TABLE pricing.policy_config (
    config_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_number VARCHAR(50) UNIQUE,
    quote_number VARCHAR(50) UNIQUE,
    
    -- Company Information
    company_name VARCHAR(255) NOT NULL,
    industry_type VARCHAR(100),
    participant_count INTEGER NOT NULL,
    class_count INTEGER DEFAULT 1,
    
    -- Coverage Period
    coverage_start DATE NOT NULL,
    coverage_end DATE NOT NULL,
    
    -- Pricing Method
    pricing_method VARCHAR(50) NOT NULL, -- FULLY_EXPERIENCED, MANUAL_RATE, COMMUNITY_RATED
    distribution_channel VARCHAR(100),
    pricing_officer VARCHAR(100),
    
    -- Status
    status VARCHAR(20) DEFAULT 'DRAFT', -- DRAFT, QUOTED, APPROVED, ACTIVE, EXPIRED
    
    -- Calculated Values
    total_base_premium DECIMAL(15,2),
    total_adjusted_premium DECIMAL(15,2),
    total_factor_multiplier DECIMAL(10,6),
    
    -- Metadata
    created_by VARCHAR(100),
    approved_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP,
    
    CONSTRAINT chk_coverage_dates CHECK (coverage_end > coverage_start)
);

-- Benefit Category Selection
CREATE TABLE pricing.benefit_selection (
    selection_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_id UUID REFERENCES pricing.policy_config(config_id) ON DELETE CASCADE,
    benefit_category VARCHAR(50) NOT NULL, -- INPATIENT, OUTPATIENT, DENTAL, MATERNITY, OPTICAL, ASO
    template_id UUID REFERENCES pricing.product_template(template_id),
    is_selected BOOLEAN DEFAULT false,
    category_factor DECIMAL(5,3) DEFAULT 1.000,
    UNIQUE(config_id, benefit_category)
);

-- Selected TC Factors for Policy
CREATE TABLE pricing.policy_tc_selection (
    selection_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_id UUID REFERENCES pricing.policy_config(config_id) ON DELETE CASCADE,
    factor_id UUID REFERENCES pricing.tc_factor_config(factor_id),
    option_id UUID REFERENCES pricing.tc_factor_option(option_id),
    applied_multiplier DECIMAL(5,3) NOT NULL,
    UNIQUE(config_id, factor_id)
);

-- Benefit Limit Overrides (customization per policy)
CREATE TABLE pricing.policy_benefit_override (
    override_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_id UUID REFERENCES pricing.policy_config(config_id) ON DELETE CASCADE,
    benefit_code VARCHAR(20) NOT NULL, -- IPBC-01, OPBC-01, etc
    benefit_name VARCHAR(200),
    original_limit DECIMAL(15,2),
    override_limit DECIMAL(15,2),
    limit_type VARCHAR(50), -- PER_DAY, PER_INCIDENT, PER_YEAR
    override_reason TEXT,
    UNIQUE(config_id, benefit_code)
);

-- =====================================================
-- MEMBER ENROLLMENT TABLES
-- =====================================================

-- Policy Members (Daftar Peserta)
CREATE TABLE pricing.policy_member (
    member_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_id UUID REFERENCES pricing.policy_config(config_id) ON DELETE CASCADE,
    member_number INTEGER NOT NULL,
    
    -- Member Information
    full_name VARCHAR(255) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(10) NOT NULL CHECK (gender IN ('MALE', 'FEMALE')),
    member_type VARCHAR(20) NOT NULL, -- EMPLOYEE, SPOUSE, CHILD
    relationship VARCHAR(50),
    
    -- Classification
    class_code VARCHAR(10) DEFAULT '1',
    age_at_entry INTEGER GENERATED ALWAYS AS (DATE_PART('year', AGE(CURRENT_DATE, date_of_birth))) STORED,
    age_band VARCHAR(20),
    
    -- Premium Calculation
    base_premium DECIMAL(12,2),
    adjusted_premium DECIMAL(12,2),
    
    -- Status
    enrollment_date DATE,
    termination_date DATE,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    
    UNIQUE(config_id, member_number)
);

-- =====================================================
-- RATE TABLES (From Excel sheets Rate_RI, Rate_RJ, etc)
-- =====================================================

-- Master Rate Table
CREATE TABLE pricing.rate_table (
    rate_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rate_code VARCHAR(20) NOT NULL,
    benefit_code VARCHAR(20) NOT NULL, -- IPBC-01, OPBC-01
    benefit_description TEXT,
    
    -- Age Band Rates
    age_0_55_male DECIMAL(12,2),
    age_0_55_female DECIMAL(12,2),
    age_0_55_child DECIMAL(12,2),
    age_56_60_male DECIMAL(12,2),
    age_56_60_female DECIMAL(12,2),
    age_61_65_male DECIMAL(12,2),
    age_61_65_female DECIMAL(12,2),
    age_66_70_male DECIMAL(12,2),
    age_66_70_female DECIMAL(12,2),
    age_71_75_male DECIMAL(12,2),
    age_71_75_female DECIMAL(12,2),
    
    effective_date DATE NOT NULL,
    expiry_date DATE,
    
    UNIQUE(rate_code, benefit_code, effective_date)
);

-- =====================================================
-- CALCULATION & AUDIT TABLES
-- =====================================================

-- Premium Calculation Log
CREATE TABLE pricing.premium_calculation_log (
    calc_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_id UUID REFERENCES pricing.policy_config(config_id),
    calculation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Input Parameters
    participant_count INTEGER,
    selected_benefits JSONB,
    selected_factors JSONB,
    
    -- Calculation Steps
    base_premium_total DECIMAL(15,2),
    factor_details JSONB, -- Detailed factor breakdown
    total_multiplier DECIMAL(10,6),
    
    -- Results
    monthly_premium DECIMAL(15,2),
    annual_premium DECIMAL(15,2),
    admin_fee DECIMAL(12,2),
    tpa_fee DECIMAL(12,2),
    total_premium DECIMAL(15,2),
    
    -- User Info
    calculated_by VARCHAR(100),
    ip_address INET,
    user_agent TEXT
);

-- Pricing Approval Workflow
CREATE TABLE pricing.approval_workflow (
    workflow_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_id UUID REFERENCES pricing.policy_config(config_id),
    
    -- Workflow Steps
    step_name VARCHAR(50) NOT NULL, -- UNDERWRITING, ACTUARIAL, MANAGEMENT
    step_order INTEGER NOT NULL,
    
    -- Approval Details
    approver_id VARCHAR(100),
    approval_status VARCHAR(20), -- PENDING, APPROVED, REJECTED, REVISION
    approval_date TIMESTAMP,
    comments TEXT,
    
    -- Conditions
    min_premium_threshold DECIMAL(15,2),
    max_discount_allowed DECIMAL(5,2),
    
    UNIQUE(config_id, step_order)
);

-- =====================================================
-- INTEGRATION WITH CLAIMS SCHEMA
-- =====================================================

-- Link pricing config to actual policies
CREATE TABLE pricing.policy_pricing_link (
    link_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_id UUID REFERENCES pricing.policy_config(config_id),
    policy_id UUID, -- References claims.policy when created
    plan_id UUID,   -- References claims.plan when created
    
    -- Conversion metadata
    converted_at TIMESTAMP,
    converted_by VARCHAR(100),
    
    UNIQUE(config_id),
    UNIQUE(policy_id)
);

-- =====================================================
-- VIEWS FOR EASIER ACCESS
-- =====================================================

-- Active Policy Configurations View
CREATE VIEW pricing.v_active_configs AS
SELECT 
    pc.*,
    COUNT(DISTINCT pm.member_id) as enrolled_members,
    SUM(pm.adjusted_premium) as total_member_premium,
    STRING_AGG(DISTINCT bs.benefit_category, ', ') as selected_benefits
FROM pricing.policy_config pc
LEFT JOIN pricing.policy_member pm ON pc.config_id = pm.config_id
LEFT JOIN pricing.benefit_selection bs ON pc.config_id = bs.config_id AND bs.is_selected = true
WHERE pc.status IN ('QUOTED', 'APPROVED', 'ACTIVE')
GROUP BY pc.config_id;

-- Premium Calculation Summary View
CREATE VIEW pricing.v_premium_summary AS
SELECT 
    pc.config_id,
    pc.company_name,
    pc.participant_count,
    pc.total_base_premium,
    pc.total_factor_multiplier,
    pc.total_adjusted_premium,
    pcl.admin_fee,
    pcl.tpa_fee,
    pcl.total_premium as final_premium
FROM pricing.policy_config pc
JOIN pricing.premium_calculation_log pcl ON pc.config_id = pcl.config_id
WHERE pcl.calc_id = (
    SELECT calc_id FROM pricing.premium_calculation_log 
    WHERE config_id = pc.config_id 
    ORDER BY calculation_timestamp DESC 
    LIMIT 1
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

CREATE INDEX idx_policy_config_status ON pricing.policy_config(status);
CREATE INDEX idx_policy_config_dates ON pricing.policy_config(coverage_start, coverage_end);
CREATE INDEX idx_policy_member_config ON pricing.policy_member(config_id);
CREATE INDEX idx_benefit_selection_config ON pricing.benefit_selection(config_id);
CREATE INDEX idx_tc_selection_config ON pricing.policy_tc_selection(config_id);
CREATE INDEX idx_calc_log_config ON pricing.premium_calculation_log(config_id);
CREATE INDEX idx_calc_log_timestamp ON pricing.premium_calculation_log(calculation_timestamp DESC);

-- =====================================================
-- SAMPLE DATA FOR TC FACTORS
-- =====================================================

-- General TC Factors
INSERT INTO pricing.tc_factor_config (factor_code, factor_category, factor_name, display_order) VALUES
('TCGC-01', 'GENERAL', 'Cara Bayar Premi', 1),
('TCGC-02', 'GENERAL', 'Provider', 2),
('TCGC-03', 'GENERAL', 'Usia Anak', 3),
('TCGC-04', 'GENERAL', 'Dash Board System', 4);

-- Inpatient TC Factors
INSERT INTO pricing.tc_factor_config (factor_code, factor_category, factor_name, display_order) VALUES
('TCNBIP-01', 'INPATIENT', 'Penggantian Klaim', 1),
('TCNBIP-02', 'INPATIENT', 'Ekses Klaim', 2),
('TCNBIP-03', 'INPATIENT', 'Recovery Penyakit', 3),
('TCNBIP-04', 'INPATIENT', 'Toleransi', 4),
('TCNBIP-05', 'INPATIENT', 'Jumlah Peserta Minimum', 5);

-- Add some TC Factor Options
INSERT INTO pricing.tc_factor_option (factor_id, option_value, option_label, multiplier, is_default) VALUES
((SELECT factor_id FROM pricing.tc_factor_config WHERE factor_code = 'TCGC-01'), 'SEKALIGUS', 'Sekaligus', 1.000, true),
((SELECT factor_id FROM pricing.tc_factor_config WHERE factor_code = 'TCGC-01'), 'CICILAN_3', 'Cicilan 3 Bulan', 1.015, false),
((SELECT factor_id FROM pricing.tc_factor_config WHERE factor_code = 'TCGC-01'), 'CICILAN_6', 'Cicilan 6 Bulan', 1.025, false),
((SELECT factor_id FROM pricing.tc_factor_config WHERE factor_code = 'TCGC-01'), 'CICILAN_12', 'Cicilan 12 Bulan', 1.035, false);

COMMENT ON SCHEMA pricing IS 'Group health insurance pricing and configuration management';
COMMENT ON TABLE pricing.policy_config IS 'Main policy configuration and pricing setup';
COMMENT ON TABLE pricing.policy_member IS 'Enrolled members for each policy configuration';
COMMENT ON TABLE pricing.tc_factor_config IS 'Terms and conditions factors that affect pricing';
COMMENT ON TABLE pricing.premium_calculation_log IS 'Audit trail of all premium calculations';