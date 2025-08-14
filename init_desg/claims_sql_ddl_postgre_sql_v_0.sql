-- Claims — SQL DDL (PostgreSQL) — v0.3
-- Delta from v0.2: adds medication tables, non-medical, bed upgrades, member coverage layers; adds layer column to accumulators.

CREATE SCHEMA IF NOT EXISTS claims;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Enums (reuse if exist)
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname='facility_mode_enum') THEN
    CREATE TYPE claims.facility_mode_enum AS ENUM ('cashless','reimburse','both');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname='limit_basis_enum') THEN
    CREATE TYPE claims.limit_basis_enum AS ENUM ('incident','day','year');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname='channel_enum') THEN
    CREATE TYPE claims.channel_enum AS ENUM ('cashless','reimburse');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname='coverage_layer_enum') THEN
    CREATE TYPE claims.coverage_layer_enum AS ENUM ('IL','AC');
  END IF;
END $$;

-- Domains
CREATE DOMAIN IF NOT EXISTS claims.money_idr AS NUMERIC(18,2) CHECK (VALUE >= 0);

-- NEW: Member coverage layers
CREATE TABLE IF NOT EXISTS claims.member_coverage_layer (
  member_id UUID NOT NULL,
  layer claims.coverage_layer_enum NOT NULL,
  plan_id UUID NOT NULL,
  precedence SMALLINT NOT NULL DEFAULT 1,
  effective_from DATE NOT NULL,
  effective_to   DATE,
  PRIMARY KEY (member_id, layer, effective_from)
);

-- ALTER: accumulators add layer
DO $$ BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_schema='claims' AND table_name='accumulator_member_year' AND column_name='layer') THEN
    ALTER TABLE claims.accumulator_member_year
      ADD COLUMN layer claims.coverage_layer_enum;
    -- Extend PK
    ALTER TABLE claims.accumulator_member_year DROP CONSTRAINT IF EXISTS accumulator_member_year_pkey;
    ALTER TABLE claims.accumulator_member_year ADD PRIMARY KEY (member_id, plan_id, benefit_code, year, layer);
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_schema='claims' AND table_name='accumulator_family_year' AND column_name='layer') THEN
    ALTER TABLE claims.accumulator_family_year
      ADD COLUMN layer claims.coverage_layer_enum;
    ALTER TABLE claims.accumulator_family_year DROP CONSTRAINT IF EXISTS accumulator_family_year_pkey;
    ALTER TABLE claims.accumulator_family_year ADD PRIMARY KEY (family_id, plan_id, benefit_code, year, layer);
  END IF;
END $$;

-- Medication tables
CREATE TABLE IF NOT EXISTS claims.medication_order (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  case_id UUID,
  claim_id UUID,
  ordering_practitioner_id UUID,
  drug_code TEXT NOT NULL,
  atc_code TEXT,
  local_code TEXT,
  strength TEXT,
  dose NUMERIC(12,4),
  dose_unit TEXT,
  route TEXT,
  frequency TEXT,
  duration_days INT,
  quantity NUMERIC(12,4),
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS claims.medication_administration (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  case_id UUID NOT NULL,
  medication_order_id UUID,
  administered_by_practitioner_id UUID,
  start_ts TIMESTAMPTZ NOT NULL,
  end_ts TIMESTAMPTZ,
  dose_given NUMERIC(12,4),
  dose_unit TEXT,
  route TEXT,
  frequency TEXT,
  ddd_calculated NUMERIC(12,4),
  lot_no TEXT,
  remarks TEXT
);

CREATE TABLE IF NOT EXISTS claims.pharmacy_charge (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  claim_id UUID NOT NULL,
  line_no INT NOT NULL,
  drug_code TEXT NOT NULL,
  qty NUMERIC(12,4) NOT NULL,
  unit_price claims.money_idr NOT NULL,
  amount claims.money_idr NOT NULL,
  formulary_tier TEXT,
  non_formulary_reason TEXT,
  pa_id UUID,
  reasons JSONB NOT NULL DEFAULT '[]'::jsonb
);
CREATE INDEX IF NOT EXISTS pharmacy_charge_claim_idx ON claims.pharmacy_charge(claim_id);

-- Non-medical charges
CREATE TABLE IF NOT EXISTS claims.non_medical_charge (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  claim_id UUID NOT NULL,
  code TEXT NOT NULL,
  description TEXT,
  qty NUMERIC(12,2) NOT NULL DEFAULT 1,
  unit_price claims.money_idr NOT NULL,
  amount claims.money_idr NOT NULL,
  route TEXT NOT NULL CHECK (route IN ('deny','non_benefit','member'))
);

-- Bed upgrades
CREATE TABLE IF NOT EXISTS claims.bed_upgrade_event (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  case_id UUID NOT NULL,
  from_class TEXT,
  to_class TEXT NOT NULL,
  reason TEXT NOT NULL CHECK (reason IN ('unavailability','member_request')),
  evidence_doc_id UUID,
  approved_by UUID,
  approved_ts TIMESTAMPTZ,
  upgrade_fee_policy TEXT NOT NULL CHECK (upgrade_fee_policy IN ('member','coins_pct','as_charged')),
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Helpful indexes
CREATE INDEX IF NOT EXISTS med_order_case_idx ON claims.medication_order(case_id);
CREATE INDEX IF NOT EXISTS med_admin_case_idx ON claims.medication_administration(case_id);
CREATE INDEX IF NOT EXISTS bed_upgrade_case_idx ON claims.bed_upgrade_event(case_id);

-- END OF v0.3 delta DDL
