# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Health Insurance Claims Processing System for the Indonesian market, handling medical claims adjudication, payments, and related workflows. Supports Commercial and Corporate health insurance products with multi-channel intake.

## Development Commands

### Database Setup
```bash
# Set database connection  
export DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/db

# Initialize schema
psql $DATABASE_URL < init_desg/claims_sql_ddl_postgre_sql_v_0.sql
```

### Data Import
```bash
# Import policy benefits from Excel
python init_desg/claims_excel_importer_python_v_0.py \
  --excel /path/to/import-policy-benefit.xlsx \
  --plan-id <UUID> \
  --effective-from 2025-01-01

# Check errors if any (generated as {filename}.errors.csv)
```

### Python Dependencies
```bash
pip install pandas sqlalchemy psycopg2-binary
```

## Architecture

### System Flow
Intake → Pre-check → Adjudication → Payment/EOB → Appeals → Post-pay Integrity

### Core Components
- **Claims Engine**: End-to-end processing with state management
- **Rule Engine**: Eligibility, benefits, cost-sharing, pre-auth, COB/TPL
- **Data Model**: PostgreSQL with claims schema
- **Integration**: FHIR R4, EDI/X12 837/835, CSV batch processing

### Key Database Tables
- `claims.plan_benefit`: Benefit definitions with limits and rules
- `claims.policy_funding`: ASO, buffer, and non-benefit fund tracking
- `claims.accumulator_member_year`: Member annual limits tracking
- `claims.accumulator_family_year`: Family annual limits tracking
- `claims.member_coverage_layer`: IL/AC layer assignments
- `claims.medication_order`: Prescription orders
- `claims.medication_administration`: Medication administration records
- `claims.pharmacy_charge`: Pharmacy billing details
- `claims.non_medical_charge`: Non-medical items routing
- `claims.bed_upgrade_event`: Bed upgrade tracking

## Business Rules

### Benefit Calculation Sequence
1. Eligibility/channel validation
2. Benefit mapping (benefit_code → plan_benefit)
3. Scheduled allowed calculation
4. Deductible application
5. Coinsurance calculation (coins_pct)
6. Buffer/ASO fund draw
7. Accumulator updates
8. COB/TPL processing
9. Final rounding

### Key Normalization (Indonesian → System)
- Limit basis: `per kejadian` → `incident`, `per hari` → `day`, `per tahun` → `year`
- Facility mode: `cashless & reimb` → `both`
- Boolean flags: `ya`/`boleh` → true

### Coverage Layers
- **IL (Inner Limit)**: Basic coverage layer
- **AC (Annual Cap)**: Additional coverage layer
- Precedence determines which layer applies first

### Funding Priority
1. ASO funds (if aso_applicable=true)
2. Buffer fund (if allow_excess_draw=true)
3. Non-benefit fund (fallback)

## File Structure
```
/
├── init_desg/                      # Design documents and implementation
│   # Core Implementation
│   ├── claims_excel_importer_python_v_0.py        # Excel to DB importer
│   ├── claims_sql_ddl_postgre_sql_v_0.sql        # Database schema
│   │
│   # Business Requirements
│   ├── claims_prd_core_journey_v_0.md            # Product requirements
│   ├── claims_group_policy_benefit_rules_v_0.md  # Benefit rules
│   ├── claims_data_model_apis_events_v_0.md      # Data model specs
│   │
│   # Operations Design
│   ├── claims_servicing_um_inpatient_e_gl_v_0.md     # Inpatient UM & GL
│   ├── claims_outpatient_servicing_flow_v_0.md       # Outpatient operations
│   ├── claims_inpatient_discharge_billing_v_0.md     # Discharge & billing
│   ├── claims_reimbursement_operations_v_0.md        # Out-of-network reimbursement
│   │
│   # System Components
│   ├── claims_provider_network_management_v_0.md     # Provider network design
│   ├── claims_realtime_cost_control_auth_v_0.md      # Cost control system
│   ├── claims_gap_analysis_recommendations_v_0.md    # System gap analysis
│   │
│   # Technical Architecture
│   ├── ui_ux_design_specifications_v_0.md            # Complete UI/UX designs
│   ├── process_flow_diagrams_v_0.md                  # Detailed process flows
│   ├── data_model_design_v_0.md                      # Database architecture
│   ├── system_integration_architecture_v_0.md        # Integration design
│   │
│   # Documentation Index
│   ├── claims_executive_summary_v_0.md               # Technical overview
│   └── claims_index_ownership_map_v_0.md             # Document index
│
└── refs/                           # Reference data
    ├── Benefit_Premi.xlsx         # Benefit premium reference
    └── T_C.xlsx                   # Terms & conditions reference
```

## Common Tasks

### Add New Benefits
1. Prepare Excel with columns: benefit_code, benefit_name, limitation_type, maximum_value
2. Optional: Add layer_applicability sheet for IL/AC assignments
3. Run importer with plan-id and effective-from date

### Modify Benefit Rules
Update `claims.plan_benefit` table directly or re-import from Excel with new values

### Check Accumulator Status
Query `claims.accumulator_member_year` with member_id, plan_id, benefit_code, year, layer

## Error Handling
- Import errors saved to `{filename}.errors.csv`
- Includes sheet name, row index, error details
- Processing continues for valid rows

## Performance Targets
- Clean claim adjudication: ≤5 seconds
- Clean claim rate: ≥85%
- Payment TAT: ≤5 business days