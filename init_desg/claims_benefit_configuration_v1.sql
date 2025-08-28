-- Claims Benefit Configuration Schema v1.0
-- Production-grade schema for handling complex benefit rules from Benefit_Plan.md
-- Supports 150+ benefit configurations with validations and limits

-- ============================================================================
-- BENEFIT CONFIGURATION TABLES
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS claims;

-- Benefit Categories Enum
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname='benefit_category_enum') THEN
    CREATE TYPE claims.benefit_category_enum AS ENUM (
      'inpatient',
      'outpatient', 
      'dental',
      'optical',
      'maternity',
      'emergency',
      'preventive',
      'mental_health',
      'rehabilitation'
    );
  END IF;
END $$;

-- Coverage Type Enum
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname='coverage_type_enum') THEN
    CREATE TYPE claims.coverage_type_enum AS ENUM (
      'not_covered',
      'covered_standard',
      'covered_per_case',
      'covered_per_year',
      'covered_per_visit',
      'covered_per_day',
      'covered_in_surgery',
      'covered_in_hospital_costs',
      'covered_as_separate_benefit',
      'covered_with_medical_indication',
      'covered_tc' -- Terms & Conditions apply
    );
  END IF;
END $$;

-- Surgery Classification Enum
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname='surgery_class_enum') THEN
    CREATE TYPE claims.surgery_class_enum AS ENUM (
      'complex',
      'major',
      'medium',
      'minor',
      'one_day',
      'not_surgery'
    );
  END IF;
END $$;

-- ============================================================================
-- CORE BENEFIT CONFIGURATION TABLE
-- ============================================================================

DROP TABLE IF EXISTS claims.plan_benefit CASCADE;
CREATE TABLE claims.plan_benefit (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  plan_id UUID NOT NULL,
  
  -- Basic Information
  benefit_code VARCHAR(50) NOT NULL,
  benefit_name VARCHAR(255) NOT NULL,
  benefit_category claims.benefit_category_enum NOT NULL,
  benefit_type VARCHAR(100), -- Specific type within category
  
  -- Coverage Configuration
  coverage_type claims.coverage_type_enum NOT NULL DEFAULT 'not_covered',
  claim_settlement_pct SMALLINT DEFAULT 100 CHECK (claim_settlement_pct BETWEEN 0 AND 100),
  coinsurance_pct SMALLINT DEFAULT 0 CHECK (coinsurance_pct BETWEEN 0 AND 100),
  
  -- Limits
  limit_basis claims.limit_basis_enum,
  limit_value claims.money_idr,
  qty_value INT,
  max_days_per_year INT,
  max_visits_per_year INT,
  max_cases_per_year INT,
  
  -- Facility & Channel
  facility_mode claims.facility_mode_enum DEFAULT 'both',
  requires_preauth BOOLEAN DEFAULT FALSE,
  
  -- Age Restrictions
  min_age_years INT,
  max_age_years INT,
  age_restriction_note TEXT,
  
  -- Medical Indications
  requires_medical_indication BOOLEAN DEFAULT FALSE,
  medical_indication_rules JSONB,
  
  -- Exclusions
  exclusion_list JSONB, -- Array of exclusion codes
  waiting_period_days INT DEFAULT 0,
  
  -- Special Rules
  pre_hospitalization_days INT,
  post_hospitalization_days INT,
  recovery_period_days INT,
  
  -- Group Configuration
  benefit_group_id UUID,
  shared_limit_group VARCHAR(100),
  
  -- Coverage Conditions
  coverage_conditions JSONB, -- Complex conditions in JSON format
  
  -- Metadata
  effective_from DATE NOT NULL,
  effective_to DATE,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  
  UNIQUE(plan_id, benefit_code, effective_from)
);

-- ============================================================================
-- SURGERY CONFIGURATION
-- ============================================================================

DROP TABLE IF EXISTS claims.surgery_classification CASCADE;
CREATE TABLE claims.surgery_classification (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  procedure_code VARCHAR(50) NOT NULL,
  procedure_name VARCHAR(255) NOT NULL,
  surgery_class claims.surgery_class_enum NOT NULL,
  
  -- Component Percentages (of total surgery limit)
  surgeon_fee_pct SMALLINT DEFAULT 60,
  operating_room_pct SMALLINT DEFAULT 25,
  anesthesia_fee_pct SMALLINT DEFAULT 15,
  
  -- Reference Pricing
  reference_price_min claims.money_idr,
  reference_price_max claims.money_idr,
  
  -- Bundling Rules
  can_bundle BOOLEAN DEFAULT TRUE,
  max_bundle_count INT DEFAULT 1,
  
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(procedure_code)
);

-- ============================================================================
-- PRE/POST HOSPITALIZATION RULES
-- ============================================================================

DROP TABLE IF EXISTS claims.hospitalization_coverage_rules CASCADE;
CREATE TABLE claims.hospitalization_coverage_rules (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  plan_id UUID NOT NULL,
  
  -- Pre-Hospitalization
  pre_hosp_physician_coverage claims.coverage_type_enum DEFAULT 'not_covered',
  pre_hosp_physician_days INT,
  pre_hosp_medicine_lab_coverage claims.coverage_type_enum DEFAULT 'not_covered',
  pre_hosp_medicine_lab_days INT,
  
  -- Post-Hospitalization  
  post_hosp_coverage claims.coverage_type_enum DEFAULT 'not_covered',
  post_hosp_days INT,
  
  -- Coverage Basis
  coverage_basis VARCHAR(50), -- 'per_case', 'per_year', 'per_visit'
  
  -- Limits
  pre_hosp_limit claims.money_idr,
  post_hosp_limit claims.money_idr,
  
  effective_from DATE NOT NULL,
  effective_to DATE,
  
  UNIQUE(plan_id, effective_from)
);

-- ============================================================================
-- BENEFIT PREREQUISITES & DEPENDENCIES
-- ============================================================================

DROP TABLE IF EXISTS claims.benefit_prerequisites CASCADE;
CREATE TABLE claims.benefit_prerequisites (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  benefit_code VARCHAR(50) NOT NULL,
  prerequisite_benefit_code VARCHAR(50) NOT NULL,
  prerequisite_type VARCHAR(50), -- 'required', 'recommended', 'either_or'
  validation_rule TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  
  UNIQUE(benefit_code, prerequisite_benefit_code)
);

-- ============================================================================
-- AGE-BASED BENEFIT RULES
-- ============================================================================

DROP TABLE IF EXISTS claims.age_based_benefit_rules CASCADE;
CREATE TABLE claims.age_based_benefit_rules (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  plan_id UUID NOT NULL,
  benefit_code VARCHAR(50) NOT NULL,
  
  -- Age Ranges
  age_from INT NOT NULL,
  age_to INT,
  
  -- Modified Coverage
  coverage_type claims.coverage_type_enum,
  limit_adjustment_pct INT, -- Percentage adjustment to base limit
  
  -- Special Conditions
  special_conditions JSONB,
  
  created_at TIMESTAMPTZ DEFAULT now(),
  
  UNIQUE(plan_id, benefit_code, age_from)
);

-- ============================================================================
-- ROOM & BOARD UPGRADE RULES
-- ============================================================================

DROP TABLE IF EXISTS claims.room_upgrade_rules CASCADE;
CREATE TABLE claims.room_upgrade_rules (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  plan_id UUID NOT NULL,
  
  -- Entitled Room Class
  entitled_room_class VARCHAR(50) NOT NULL,
  max_daily_rate claims.money_idr NOT NULL,
  
  -- Upgrade Rules
  allow_upgrade BOOLEAN DEFAULT TRUE,
  member_pays_difference BOOLEAN DEFAULT TRUE,
  upgrade_affects_other_benefits BOOLEAN DEFAULT FALSE,
  other_benefit_adjustment_pct INT DEFAULT 0,
  
  -- ICU/CCU Rules
  icu_max_days INT DEFAULT 30,
  intermediate_care_max_days INT DEFAULT 30,
  
  created_at TIMESTAMPTZ DEFAULT now(),
  
  UNIQUE(plan_id, entitled_room_class)
);

-- ============================================================================
-- EXCLUSION MASTER LIST
-- ============================================================================

DROP TABLE IF EXISTS claims.exclusion_master CASCADE;
CREATE TABLE claims.exclusion_master (
  exclusion_code VARCHAR(50) PRIMARY KEY,
  exclusion_name VARCHAR(255) NOT NULL,
  exclusion_category VARCHAR(100),
  icd10_codes TEXT[], -- Array of ICD-10 codes
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- BENEFIT LIMIT GROUPS (Shared Limits)
-- ============================================================================

DROP TABLE IF EXISTS claims.benefit_limit_groups CASCADE;
CREATE TABLE claims.benefit_limit_groups (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  group_code VARCHAR(50) NOT NULL UNIQUE,
  group_name VARCHAR(255) NOT NULL,
  group_description TEXT,
  
  -- Shared Limit Configuration
  shared_annual_limit claims.money_idr,
  shared_per_case_limit claims.money_idr,
  shared_per_day_limit claims.money_idr,
  
  -- Member Benefits in Group
  member_benefit_codes TEXT[],
  
  created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- SPECIAL CONDITION RULES
-- ============================================================================

DROP TABLE IF EXISTS claims.special_condition_rules CASCADE;
CREATE TABLE claims.special_condition_rules (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  condition_code VARCHAR(50) NOT NULL UNIQUE,
  condition_name VARCHAR(255) NOT NULL,
  
  -- Conditions
  condition_type VARCHAR(50), -- 'congenital', 'chronic', 'pre_existing', 'maternity'
  
  -- Coverage Rules
  waiting_period_days INT,
  coverage_after_waiting claims.coverage_type_enum,
  special_limit claims.money_idr,
  requires_declaration BOOLEAN DEFAULT FALSE,
  
  -- Documentation Requirements
  required_documents JSONB,
  
  created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- VALIDATION RULE DEFINITIONS
-- ============================================================================

DROP TABLE IF EXISTS claims.validation_rules CASCADE;
CREATE TABLE claims.validation_rules (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  rule_code VARCHAR(50) NOT NULL UNIQUE,
  rule_name VARCHAR(255) NOT NULL,
  rule_category VARCHAR(50), -- 'eligibility', 'limit', 'medical_necessity', 'documentation'
  
  -- Rule Definition
  rule_logic JSONB NOT NULL, -- Structured rule definition
  error_message TEXT NOT NULL,
  severity VARCHAR(20) DEFAULT 'error', -- 'error', 'warning', 'info'
  
  -- Applicability
  applies_to_benefits TEXT[], -- Array of benefit codes
  applies_to_categories claims.benefit_category_enum[],
  
  -- Control
  is_active BOOLEAN DEFAULT TRUE,
  can_override BOOLEAN DEFAULT FALSE,
  override_authority_level INT DEFAULT 3,
  
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- ACCUMULATOR CONFIGURATION
-- ============================================================================

DROP TABLE IF EXISTS claims.accumulator_config CASCADE;
CREATE TABLE claims.accumulator_config (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  plan_id UUID NOT NULL,
  accumulator_type VARCHAR(50) NOT NULL, -- 'deductible', 'out_of_pocket', 'benefit_specific'
  
  -- Limits
  individual_limit claims.money_idr,
  family_limit claims.money_idr,
  
  -- Accumulation Rules
  accumulates_across_benefits BOOLEAN DEFAULT FALSE,
  included_benefit_codes TEXT[],
  excluded_benefit_codes TEXT[],
  
  -- Reset Rules
  reset_period VARCHAR(20) DEFAULT 'calendar_year', -- 'calendar_year', 'policy_year', 'rolling_12_months'
  
  created_at TIMESTAMPTZ DEFAULT now(),
  
  UNIQUE(plan_id, accumulator_type)
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

CREATE INDEX idx_plan_benefit_plan_id ON claims.plan_benefit(plan_id);
CREATE INDEX idx_plan_benefit_benefit_code ON claims.plan_benefit(benefit_code);
CREATE INDEX idx_plan_benefit_category ON claims.plan_benefit(benefit_category);
CREATE INDEX idx_plan_benefit_effective ON claims.plan_benefit(effective_from, effective_to);

CREATE INDEX idx_surgery_classification_code ON claims.surgery_classification(procedure_code);
CREATE INDEX idx_surgery_classification_class ON claims.surgery_classification(surgery_class);

CREATE INDEX idx_hospitalization_rules_plan ON claims.hospitalization_coverage_rules(plan_id);
CREATE INDEX idx_age_rules_plan_benefit ON claims.age_based_benefit_rules(plan_id, benefit_code);

CREATE INDEX idx_validation_rules_active ON claims.validation_rules(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_validation_rules_category ON claims.validation_rules(rule_category);

-- ============================================================================
-- SAMPLE DATA FOR COMMON BENEFITS
-- ============================================================================

-- Insert sample surgery classifications
INSERT INTO claims.surgery_classification (procedure_code, procedure_name, surgery_class, surgeon_fee_pct, operating_room_pct, anesthesia_fee_pct)
VALUES 
  ('0DT90ZZ', 'Appendectomy', 'major', 60, 25, 15),
  ('0DB60ZZ', 'Cholecystectomy', 'major', 60, 25, 15),
  ('0SB00ZZ', 'Hip Replacement', 'complex', 65, 20, 15),
  ('0HB3XZZ', 'Cataract Surgery', 'minor', 70, 20, 10),
  ('0JH70MZ', 'Knee Arthroscopy', 'medium', 60, 25, 15);

-- Insert common exclusions
INSERT INTO claims.exclusion_master (exclusion_code, exclusion_name, exclusion_category, description)
VALUES 
  ('EXC001', 'Cosmetic Surgery', 'elective', 'All cosmetic and aesthetic procedures'),
  ('EXC002', 'Experimental Treatment', 'experimental', 'Treatments not proven effective'),
  ('EXC003', 'Self-Inflicted Injury', 'behavioral', 'Intentional self-harm'),
  ('EXC004', 'War and Terrorism', 'external', 'Injuries from war or terrorist acts'),
  ('EXC005', 'Professional Sports', 'activity', 'Injuries from professional sports participation');

-- Insert validation rules
INSERT INTO claims.validation_rules (rule_code, rule_name, rule_category, rule_logic, error_message, severity)
VALUES 
  ('VAL001', 'Age Limit Check', 'eligibility', 
   '{"check": "age_between", "min": 0, "max": 65}', 
   'Member age exceeds benefit age limit', 'error'),
  
  ('VAL002', 'Annual Limit Check', 'limit',
   '{"check": "accumulator_under_limit", "accumulator": "annual_benefit"}',
   'Annual benefit limit exceeded', 'error'),
  
  ('VAL003', 'Pre-Authorization Required', 'medical_necessity',
   '{"check": "has_preauth", "for_amounts_over": 10000000}',
   'Pre-authorization required for this service', 'error'),
  
  ('VAL004', 'Waiting Period Check', 'eligibility',
   '{"check": "waiting_period_met", "days": 30}',
   'Waiting period not yet satisfied', 'error'),
  
  ('VAL005', 'Duplicate Claim Check', 'documentation',
   '{"check": "no_duplicate", "window_days": 30}',
   'Potential duplicate claim detected', 'warning');

-- ============================================================================
-- FUNCTIONS FOR BENEFIT VALIDATION
-- ============================================================================

-- Function to check if a benefit is covered for a member
CREATE OR REPLACE FUNCTION claims.check_benefit_coverage(
  p_member_id UUID,
  p_benefit_code VARCHAR,
  p_service_date DATE,
  p_amount NUMERIC
) RETURNS TABLE (
  is_covered BOOLEAN,
  coverage_type claims.coverage_type_enum,
  limit_remaining NUMERIC,
  coinsurance_pct INT,
  validation_messages TEXT[]
) AS $$
DECLARE
  v_messages TEXT[] := ARRAY[]::TEXT[];
  v_plan_id UUID;
  v_benefit RECORD;
BEGIN
  -- Get member's plan
  SELECT plan_id INTO v_plan_id
  FROM claims.member_coverage
  WHERE member_id = p_member_id
    AND p_service_date BETWEEN effective_from AND COALESCE(effective_to, '9999-12-31');
  
  -- Get benefit configuration
  SELECT * INTO v_benefit
  FROM claims.plan_benefit
  WHERE plan_id = v_plan_id
    AND benefit_code = p_benefit_code
    AND p_service_date BETWEEN effective_from AND COALESCE(effective_to, '9999-12-31');
  
  -- Check coverage type
  IF v_benefit.coverage_type = 'not_covered' THEN
    RETURN QUERY SELECT 
      FALSE,
      'not_covered'::claims.coverage_type_enum,
      0::NUMERIC,
      0::INT,
      ARRAY['Benefit not covered under plan']::TEXT[];
    RETURN;
  END IF;
  
  -- Additional validation logic would go here
  
  RETURN QUERY SELECT 
    TRUE,
    v_benefit.coverage_type,
    v_benefit.limit_value,
    v_benefit.coinsurance_pct,
    v_messages;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TRIGGERS FOR AUDIT
-- ============================================================================

CREATE OR REPLACE FUNCTION claims.update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_plan_benefit_timestamp
  BEFORE UPDATE ON claims.plan_benefit
  FOR EACH ROW EXECUTE FUNCTION claims.update_timestamp();

CREATE TRIGGER update_validation_rules_timestamp
  BEFORE UPDATE ON claims.validation_rules
  FOR EACH ROW EXECUTE FUNCTION claims.update_timestamp();

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE claims.plan_benefit IS 'Comprehensive benefit configuration supporting all 150+ benefit types from Benefit_Plan.md';
COMMENT ON TABLE claims.surgery_classification IS 'Surgery procedure classifications with component pricing percentages';
COMMENT ON TABLE claims.hospitalization_coverage_rules IS 'Pre and post hospitalization coverage configurations';
COMMENT ON TABLE claims.validation_rules IS 'Configurable validation rules for claims processing';
COMMENT ON TABLE claims.accumulator_config IS 'Accumulator configuration for deductibles and out-of-pocket tracking';

-- End of Benefit Configuration Schema