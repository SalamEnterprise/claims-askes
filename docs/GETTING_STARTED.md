# 🚀 Getting Started Guide

## Overview

This guide will help you understand and navigate the Claims-Askes health insurance system documentation and begin implementation.

## Prerequisites

### Knowledge Requirements
- Basic understanding of health insurance concepts
- Familiarity with claims processing workflows
- Knowledge of Indonesian healthcare regulations (OJK, BPJS)

### Technical Requirements
- PostgreSQL 15+ database knowledge
- Python 3.9+ programming
- REST API concepts
- Basic understanding of microservices

## System Overview

The Claims-Askes system is a comprehensive health insurance platform with:

### Core Capabilities
1. **Claims Processing**: Both network (cashless) and reimbursement
2. **Provider Management**: Complete provider lifecycle
3. **Member Services**: Self-service portals and mobile apps
4. **Real-time Authorization**: Sub-second decision making
5. **Fraud Detection**: AI/ML-powered fraud prevention

## Quick Start Path

### Step 1: Understand the Business Context
Start with these documents to understand the business requirements:

1. **[Executive Summary](../init_desg/claims_executive_summary_v_0.md)**
   - Read time: 10 minutes
   - Provides high-level system overview

2. **[Product Requirements](../init_desg/claims_prd_core_journey_v_0.md)**
   - Read time: 30 minutes
   - Understand core features and user journeys

3. **[Gap Analysis](../init_desg/claims_gap_analysis_recommendations_v_0.md)**
   - Read time: 20 minutes
   - Identify what was missing and how it's addressed

### Step 2: Explore Key Workflows

#### For Inpatient Services:
- **[Inpatient UM & e-GL](../init_desg/claims_servicing_um_inpatient_e_gl_v_0.md)** - Admission and guarantee letters
- **[Discharge & Billing](../init_desg/claims_inpatient_discharge_billing_v_0.md)** - Discharge and payment

#### For Outpatient Services:
- **[Outpatient Flow](../init_desg/claims_outpatient_servicing_flow_v_0.md)** - Consultation to payment
- **[Reimbursement](../init_desg/claims_reimbursement_operations_v_0.md)** - Out-of-network claims

### Step 3: Review Technical Architecture

1. **[Data Model](../init_desg/data_model_design_v_0.md)**
   - Database schemas and relationships
   - Start with Section 2 (Member Domain) and Section 4 (Claims Domain)

2. **[Process Flows](../init_desg/process_flow_diagrams_v_0.md)**
   - Visual workflow diagrams
   - Focus on Section 1 (Member Journey Flows)

3. **[UI/UX Design](../init_desg/ui_ux_design_specifications_v_0.md)**
   - User interface specifications
   - Review Section 2 (Member Portal) first

### Step 4: Set Up Development Environment

#### Database Setup
```bash
# 1. Install PostgreSQL 15+
# 2. Create database
createdb claims_askes

# 3. Set environment variable
export DATABASE_URL=postgresql://user:pass@localhost:5432/claims_askes

# 4. Run schema creation
psql $DATABASE_URL < init_desg/claims_sql_ddl_postgre_sql_v_0.sql
```

#### Python Environment
```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install pandas sqlalchemy psycopg2-binary

# 3. Test Excel importer
python init_desg/claims_excel_importer_python_v_0.py --help
```

## Key Concepts to Understand

### 1. Network vs Out-of-Network
- **Network (Cashless)**: Provider bills insurance directly
- **Out-of-Network (Reimbursement)**: Member pays, then claims reimbursement

### 2. Coverage Layers
- **IL (Inner Limit)**: Basic coverage layer
- **AC (Annual Cap)**: Additional coverage layer

### 3. Key Processes
- **Eligibility**: Checking if member is covered
- **Authorization**: Pre-approval for services
- **Adjudication**: Processing and payment decision
- **EOB**: Explanation of Benefits sent to member

### 4. Indonesian Specifics
- **INA-CBG**: Indonesian Case-Based Groups (like DRG)
- **BPJS**: Government health insurance coordination
- **OJK**: Financial services authority compliance

## Implementation Phases

### Phase 1: Foundation (Months 1-3)
Focus areas:
- Database setup
- Provider management system
- Basic claim submission

Key documents:
- [Provider Network Management](../init_desg/claims_provider_network_management_v_0.md)
- [Data Model Design](../init_desg/data_model_design_v_0.md)

### Phase 2: Core Features (Months 4-6)
Focus areas:
- Claims adjudication engine
- Member and provider portals
- Authorization system

Key documents:
- [Real-Time Cost Control](../init_desg/claims_realtime_cost_control_auth_v_0.md)
- [UI/UX Specifications](../init_desg/ui_ux_design_specifications_v_0.md)

### Phase 3: Advanced Features (Months 7-9)
Focus areas:
- Mobile applications
- Fraud detection
- Analytics dashboard

Key documents:
- [System Integration Architecture](../init_desg/system_integration_architecture_v_0.md)

## Common Tasks

### Adding a New Benefit Plan
1. Prepare Excel file with benefit details
2. Use the Excel importer script
3. Verify in database

### Processing a Claim
1. Member submits claim (portal/mobile)
2. System validates eligibility
3. Authorization check (if required)
4. Adjudication process
5. Payment determination
6. EOB generation

### Setting Up Provider
1. Provider application submission
2. Credentialing verification
3. Contract negotiation
4. System onboarding
5. Portal access provisioning

## Troubleshooting Guide

### Common Issues

#### Database Connection Error
```bash
# Check PostgreSQL is running
pg_isready

# Verify connection string
psql $DATABASE_URL -c "SELECT version();"
```

#### Import Errors
- Check Excel format matches requirements
- Verify all required columns present
- Review error file: `{filename}.errors.csv`

## Next Steps

1. **Join the Team**
   - Review team structure in [Document Index](../init_desg/claims_index_ownership_map_v_0.md)
   
2. **Deep Dive into Your Area**
   - Frontend: Start with [UI/UX Design](../init_desg/ui_ux_design_specifications_v_0.md)
   - Backend: Focus on [Integration Architecture](../init_desg/system_integration_architecture_v_0.md)
   - Database: Study [Data Model](../init_desg/data_model_design_v_0.md)
   - Business: Review all operations documents

3. **Contribute**
   - Follow coding standards in CLAUDE.md
   - Create feature branches
   - Write tests for new features
   - Update documentation

## Resources

### Internal Documentation
- [Full Navigation Guide](./NAVIGATION.md)
- [CLAUDE.md](../CLAUDE.md) - Development quick reference

### External Resources
- [FHIR R4 Specification](https://www.hl7.org/fhir/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Indonesian Healthcare Regulations](https://www.ojk.go.id)

## Support

For questions or clarifications:
1. Check existing documentation
2. Review [Gap Analysis](../init_desg/claims_gap_analysis_recommendations_v_0.md) for known issues
3. Create an issue in GitHub

---

*Welcome to the Claims-Askes team! 🎉*

*Last Updated: August 14, 2025*