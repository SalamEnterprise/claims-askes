# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Health Insurance Claims Processing System focused on the Indonesian market, handling medical claims adjudication, payments, and related workflows. The system supports both Commercial and Corporate health insurance products with multi-channel intake (portal, EDI/X12, FHIR, CSV, email+OCR).

## Architecture

### Core Components
- **Claims Engine**: End-to-end claims processing (intake → adjudication → payment → EOB → appeals)
- **Rule Engine**: Codified rules for eligibility, benefits, cost-sharing, pre-authorization, COB/TPL
- **Validation Engine (v1)**: Async Python engine with 25+ parallel validation rules
- **Data Model**: PostgreSQL-based with schemas for claims, policies, benefits, accumulators, and funding
- **Enhanced Schema (v1)**: 15+ new tables for parametric benefit configuration
- **Integration Layer**: FHIR R4 compliant, EDI/X12 support, batch CSV processing
- **Coverage Layers**: Supports IL (Inner Limit) and AC (Annual Cap) benefit structures

### Key Technologies
- **Database**: PostgreSQL with claims schema
- **Data Import**: Python-based Excel importer using pandas and SQLAlchemy
- **Standards**: ICD-10, ICD-9-CM (for INA-CBG), FHIR Claim/ClaimResponse/Coverage/EOB, X12 837/835
- **Indonesian Specifics**: INA-CBG support, Indonesian language normalization for benefit labels

## Development Commands

### Database Setup
```bash
# Set database connection
export DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/db

# Run DDL to create schema (execute claims_sql_ddl_postgre_sql_v_0.sql)
psql $DATABASE_URL < claims_sql_ddl_postgre_sql_v_0.sql

# Run enhanced schema for v1 features
psql $DATABASE_URL < claims_benefit_configuration_v1.sql
```

### Data Import
```bash
# Import policy benefits from Excel
python claims_excel_importer_python_v_0.py \
  --excel /path/to/import-policy-benefit.xlsx \
  --plan-id <UUID> \
  --effective-from 2025-01-01
```

### Python Dependencies
The Excel importer requires:
- pandas
- sqlalchemy
- psycopg2

The validation engine requires:
- asyncio (built-in)
- dataclasses (built-in)
- concurrent.futures (built-in)

## Key Business Rules

### Benefit Calculation Order
1. Eligibility/channel validation
2. Benefit mapping
3. Scheduled allowed calculation
4. Deductible application
5. Coinsurance calculation
6. Buffer/ASO fund draw
7. Accumulator updates
8. COB/TPL processing
9. Final rounding

### Facility Modes
- **cashless**: Direct billing to insurer
- **reimburse**: Member pays, then claims reimbursement
- **both**: Supports either channel

### Limit Basis Types
- **incident**: Per medical incident/case
- **day**: Per day limit
- **year**: Annual limit

### Funding Sources
- **ASO (Administrative Services Only)**: Employer-funded claims
- **Buffer Fund**: Insurer risk pool
- **Non-benefit Fund**: Additional coverage pool

## Data Model Highlights

### Core Tables (v0)
- `claims.plan_benefit`: Benefit definitions with limits, coinsurance, facility modes
- `claims.policy_funding`: ASO, buffer, and non-benefit fund balances
- `claims.accumulator_member_year`: Member-level annual accumulator tracking
- `claims.accumulator_family_year`: Family-level annual accumulator tracking
- `claims.member_coverage_layer`: IL/AC layer assignments per member
- `claims.medication_order/administration`: Medication tracking
- `claims.pharmacy_charge`: Pharmacy billing details

### Enhanced Tables (v1)
- `claims.plan_benefit_enhanced`: 150+ parametric benefit configurations
- `claims.surgery_classification`: 4-tier surgery classification system
- `claims.validation_rules`: Configurable validation rules without code changes
- `claims.hospitalization_coverage_rules`: Pre/post hospitalization windows
- `claims.age_based_benefit_rules`: Age-specific benefit variations
- `claims.room_upgrade_rules`: Room class upgrade management
- `claims.exclusion_master`: Centralized exclusion management
- `claims.benefit_limit_groups`: Shared limit configurations
- `claims.special_condition_rules`: Condition-specific coverage rules
- `claims.accumulator_config`: Advanced accumulator management

### Key Fields in plan_benefit
- `benefit_code`: Unique benefit identifier
- `limit_basis`: incident/day/year
- `limit_value`: Maximum monetary limit
- `qty_value`: Quantity limit
- `coins_pct`: Coinsurance percentage (0-100)
- `allow_excess_draw`: Whether to allow drawing from buffer when limit exceeded
- `layer_applicability`: IL/AC/BOTH layer assignment

## Error Handling

The Excel importer generates error reports:
- Errors saved to `{filename}.errors.csv`
- Includes sheet name, row index, and error details
- Continues processing valid rows even if some fail

## Validation Rules

Key validations enforced:
- Age and relationship coherence
- Facility vs channel compatibility
- Active benefit verification
- Monetary and quantity bounds
- Group cap integrity
- Late claim detection
- ASO funds availability check

## Performance Targets
- Clean claim adjudication: ≤5 seconds
- Clean claim rate: ≥85%
- Pend rate: ≤15%
- Payment TAT: ≤5 business days
- System availability: 99.9%