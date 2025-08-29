# Database Documentation

## Overview

This directory contains all database-related configurations, schemas, migrations, and management scripts for the Claims-Askes health insurance platform. The system uses PostgreSQL 15+ with schema-based separation following the database-per-service pattern.

## Architecture

### Database Strategy

We implement a **hybrid database-per-service pattern**:

1. **Development/Staging**: Single PostgreSQL instance with schema separation
2. **Production**: Option for separate PostgreSQL instances per service

```
PostgreSQL Instance (claims_askes)
├── Schema: claims_service      # Claims microservice
├── Schema: member_service      # Member management
├── Schema: provider_service    # Provider network
├── Schema: benefit_service     # Benefit configuration
├── Schema: policy_service      # Policy administration
├── Schema: authorization_service # Pre-authorization
├── Schema: payment_service     # Payment processing
├── Schema: notification_service # Notifications
├── Schema: document_service    # Document management
├── Schema: common              # Shared reference data
└── Schema: audit               # Audit logging
```

### Key Principles

1. **Schema Isolation**: Each service owns its schema exclusively
2. **No Cross-Schema Joins**: Services communicate via APIs only
3. **Event-Driven Sync**: Data consistency through events
4. **Audit Everything**: Comprehensive audit trail

## Database Setup

### Prerequisites

- PostgreSQL 15+
- psql client
- pgAdmin 4 (optional)
- TimescaleDB extension (for time-series data)

### Initial Setup

1. **Create database**
```bash
createb claims_askes
```

2. **Initialize schemas**
```bash
psql -U postgres -d claims_askes < init.sql
```

3. **Run migrations**
```bash
# For each service
cd migrations/claims-service
alembic upgrade head
```

4. **Load reference data**
```bash
psql -U postgres -d claims_askes < seed/reference_data.sql
```

### Connection Configuration

#### Service-Specific Users

Each service has its dedicated database user:

| Service | User | Default Password | Schema Access |
|---------|------|-----------------|---------------|
| Claims | claims_service_user | claims_pass_dev | claims_service |
| Member | member_service_user | member_pass_dev | member_service |
| Provider | provider_service_user | provider_pass_dev | provider_service |
| Benefit | benefit_service_user | benefit_pass_dev | benefit_service |
| Policy | policy_service_user | policy_pass_dev | policy_service |

#### Connection Strings

```bash
# Claims Service
DATABASE_URL=postgresql://claims_service_user:password@localhost:5432/claims_askes

# Member Service
DATABASE_URL=postgresql://member_service_user:password@localhost:5432/claims_askes
```

## Schema Documentation

### Claims Service Schema

Core tables for claims processing:

```sql
claims_service.
├── claim                # Main claims table
├── claim_item           # Line items
├── claim_document       # Attached documents
├── claim_status_history # Status audit trail
├── claim_note           # Internal notes
└── claim_payment        # Payment records
```

### Member Service Schema

Member and coverage management:

```sql
member_service.
├── member               # Member demographics
├── member_coverage      # Coverage periods
├── member_dependent     # Dependent relationships
├── member_card          # ID card records
└── member_eligibility   # Eligibility tracking
```

### Provider Service Schema

Provider network management:

```sql
provider_service.
├── provider             # Provider entities
├── provider_facility    # Facility locations
├── provider_specialty   # Specializations
├── provider_contract    # Contract details
└── provider_fee_schedule # Fee schedules
```

### Benefit Service Schema

Benefit plans and rules:

```sql
benefit_service.
├── plan_benefit         # Benefit definitions
├── benefit_limitation   # Coverage limits
├── benefit_exclusion    # Exclusions
├── cost_sharing         # Copay/coinsurance
└── accumulator          # Deductible/OOP tracking
```

## Core Tables

### claim (claims_service)

```sql
CREATE TABLE claims_service.claim (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_number VARCHAR(50) UNIQUE NOT NULL,
    member_id UUID NOT NULL,
    provider_id UUID NOT NULL,
    policy_id UUID NOT NULL,
    
    -- Claim details
    claim_type VARCHAR(20) NOT NULL, -- 'cashless', 'reimbursement'
    service_type VARCHAR(20) NOT NULL, -- 'inpatient', 'outpatient', etc.
    admission_date DATE,
    discharge_date DATE,
    service_date DATE NOT NULL,
    
    -- Financial
    total_charged_amount DECIMAL(15,2),
    total_approved_amount DECIMAL(15,2),
    total_paid_amount DECIMAL(15,2),
    member_responsibility DECIMAL(15,2),
    
    -- Status
    status VARCHAR(30) NOT NULL DEFAULT 'submitted',
    submission_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    
    -- Constraints
    CONSTRAINT chk_dates CHECK (discharge_date >= admission_date),
    CONSTRAINT chk_amounts CHECK (total_charged_amount >= 0)
);

-- Indexes for performance
CREATE INDEX idx_claim_member_id ON claims_service.claim(member_id);
CREATE INDEX idx_claim_provider_id ON claims_service.claim(provider_id);
CREATE INDEX idx_claim_status ON claims_service.claim(status);
CREATE INDEX idx_claim_service_date ON claims_service.claim(service_date);
CREATE INDEX idx_claim_submission_date ON claims_service.claim(submission_date);
```

### member (member_service)

```sql
CREATE TABLE member_service.member (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_number VARCHAR(50) UNIQUE NOT NULL,
    
    -- Personal Information
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    date_of_birth DATE NOT NULL,
    gender VARCHAR(10) NOT NULL,
    
    -- Identification
    national_id VARCHAR(20) UNIQUE,
    passport_number VARCHAR(20),
    
    -- Contact
    email VARCHAR(255),
    phone VARCHAR(20),
    mobile VARCHAR(20),
    
    -- Address
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state_province VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(2) DEFAULT 'ID',
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    enrollment_date DATE NOT NULL,
    termination_date DATE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT chk_age CHECK (date_of_birth < CURRENT_DATE),
    CONSTRAINT chk_gender CHECK (gender IN ('M', 'F', 'O'))
);
```

### plan_benefit (benefit_service)

```sql
CREATE TABLE benefit_service.plan_benefit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID NOT NULL,
    
    -- Benefit identification
    benefit_code VARCHAR(50) NOT NULL,
    benefit_name VARCHAR(255) NOT NULL,
    benefit_category VARCHAR(100),
    
    -- Coverage parameters
    coverage_type VARCHAR(50), -- 'per_incident', 'per_year', 'lifetime'
    limitation_type VARCHAR(50), -- 'days', 'visits', 'amount'
    
    -- Limits
    annual_limit DECIMAL(15,2),
    incident_limit DECIMAL(15,2),
    lifetime_limit DECIMAL(15,2),
    day_limit INTEGER,
    visit_limit INTEGER,
    
    -- Cost sharing
    deductible_amount DECIMAL(15,2) DEFAULT 0,
    coinsurance_percentage DECIMAL(5,2) DEFAULT 0,
    copay_amount DECIMAL(15,2) DEFAULT 0,
    
    -- Rules
    requires_preauth BOOLEAN DEFAULT FALSE,
    waiting_period_days INTEGER DEFAULT 0,
    age_limit_min INTEGER,
    age_limit_max INTEGER,
    
    -- Network
    in_network_coverage DECIMAL(5,2) DEFAULT 100,
    out_network_coverage DECIMAL(5,2) DEFAULT 80,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    effective_date DATE NOT NULL,
    expiration_date DATE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT uk_plan_benefit UNIQUE (plan_id, benefit_code),
    CONSTRAINT chk_percentages CHECK (
        coinsurance_percentage BETWEEN 0 AND 100 AND
        in_network_coverage BETWEEN 0 AND 100 AND
        out_network_coverage BETWEEN 0 AND 100
    )
);
```

## Functions & Procedures

### Claim Number Generation

```sql
CREATE OR REPLACE FUNCTION claims_service.generate_claim_number()
RETURNS VARCHAR AS $$
DECLARE
    v_year VARCHAR(4);
    v_month VARCHAR(2);
    v_sequence INTEGER;
    v_claim_number VARCHAR(50);
BEGIN
    v_year := TO_CHAR(NOW(), 'YYYY');
    v_month := TO_CHAR(NOW(), 'MM');
    
    -- Get next sequence for this month
    SELECT COALESCE(MAX(
        CAST(SUBSTRING(claim_number FROM 12) AS INTEGER)
    ), 0) + 1
    INTO v_sequence
    FROM claims_service.claim
    WHERE claim_number LIKE 'CLM-' || v_year || '-' || v_month || '-%';
    
    v_claim_number := 'CLM-' || v_year || '-' || v_month || '-' || 
                      LPAD(v_sequence::VARCHAR, 6, '0');
    
    RETURN v_claim_number;
END;
$$ LANGUAGE plpgsql;
```

### Eligibility Check

```sql
CREATE OR REPLACE FUNCTION member_service.check_eligibility(
    p_member_id UUID,
    p_service_date DATE,
    p_service_type VARCHAR
)
RETURNS TABLE (
    is_eligible BOOLEAN,
    reason VARCHAR,
    coverage_details JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        CASE 
            WHEN mc.status = 'active' 
                AND p_service_date BETWEEN mc.effective_date AND COALESCE(mc.termination_date, '9999-12-31')
                AND m.status = 'active'
            THEN TRUE
            ELSE FALSE
        END AS is_eligible,
        CASE
            WHEN m.status != 'active' THEN 'Member not active'
            WHEN mc.status != 'active' THEN 'Coverage not active'
            WHEN p_service_date < mc.effective_date THEN 'Service date before coverage start'
            WHEN p_service_date > COALESCE(mc.termination_date, '9999-12-31') THEN 'Coverage terminated'
            ELSE 'Eligible'
        END AS reason,
        jsonb_build_object(
            'plan_id', mc.plan_id,
            'coverage_level', mc.coverage_level,
            'effective_date', mc.effective_date,
            'termination_date', mc.termination_date
        ) AS coverage_details
    FROM member_service.member m
    JOIN member_service.member_coverage mc ON m.id = mc.member_id
    WHERE m.id = p_member_id
    ORDER BY mc.effective_date DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;
```

### Accumulator Update

```sql
CREATE OR REPLACE FUNCTION benefit_service.update_accumulator(
    p_member_id UUID,
    p_benefit_code VARCHAR,
    p_amount DECIMAL,
    p_service_date DATE
)
RETURNS VOID AS $$
DECLARE
    v_year INTEGER;
    v_current_amount DECIMAL;
BEGIN
    v_year := EXTRACT(YEAR FROM p_service_date);
    
    -- Upsert accumulator record
    INSERT INTO benefit_service.accumulator (
        member_id,
        benefit_code,
        year,
        amount_used,
        last_updated
    ) VALUES (
        p_member_id,
        p_benefit_code,
        v_year,
        p_amount,
        NOW()
    )
    ON CONFLICT (member_id, benefit_code, year)
    DO UPDATE SET
        amount_used = accumulator.amount_used + EXCLUDED.amount_used,
        last_updated = NOW();
END;
$$ LANGUAGE plpgsql;
```

## Triggers

### Updated Timestamp Trigger

```sql
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at column
CREATE TRIGGER update_claim_timestamp
BEFORE UPDATE ON claims_service.claim
FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

### Audit Trail Trigger

```sql
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit.audit_log (
        schema_name,
        table_name,
        operation,
        user_name,
        timestamp,
        row_id,
        old_data,
        new_data
    ) VALUES (
        TG_TABLE_SCHEMA,
        TG_TABLE_NAME,
        TG_OP,
        current_user,
        NOW(),
        CASE 
            WHEN TG_OP = 'DELETE' THEN OLD.id
            ELSE NEW.id
        END,
        CASE WHEN TG_OP IN ('UPDATE', 'DELETE') THEN row_to_json(OLD) END,
        CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN row_to_json(NEW) END
    );
    
    RETURN CASE
        WHEN TG_OP = 'DELETE' THEN OLD
        ELSE NEW
    END;
END;
$$ LANGUAGE plpgsql;
```

## Views

### Claims Dashboard View

```sql
CREATE VIEW claims_service.v_claims_dashboard AS
SELECT 
    DATE_TRUNC('day', submission_date) as date,
    COUNT(*) as total_claims,
    COUNT(*) FILTER (WHERE status = 'submitted') as pending_claims,
    COUNT(*) FILTER (WHERE status = 'approved') as approved_claims,
    COUNT(*) FILTER (WHERE status = 'rejected') as rejected_claims,
    SUM(total_charged_amount) as total_charged,
    SUM(total_approved_amount) as total_approved,
    AVG(EXTRACT(EPOCH FROM (updated_at - submission_date))/3600)::DECIMAL(10,2) as avg_processing_hours
FROM claims_service.claim
WHERE submission_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', submission_date)
ORDER BY date DESC;
```

### Member Eligibility View

```sql
CREATE VIEW member_service.v_member_eligibility AS
SELECT 
    m.id,
    m.member_number,
    m.first_name || ' ' || m.last_name as full_name,
    mc.plan_id,
    mc.coverage_level,
    mc.effective_date,
    mc.termination_date,
    CASE 
        WHEN m.status = 'active' 
            AND mc.status = 'active'
            AND CURRENT_DATE BETWEEN mc.effective_date 
            AND COALESCE(mc.termination_date, '9999-12-31')
        THEN 'eligible'
        ELSE 'not_eligible'
    END as eligibility_status
FROM member_service.member m
LEFT JOIN member_service.member_coverage mc ON m.id = mc.member_id
WHERE mc.id = (
    SELECT id FROM member_service.member_coverage
    WHERE member_id = m.id
    ORDER BY effective_date DESC
    LIMIT 1
);
```

## Partitioning Strategy

### Time-based Partitioning for Claims

```sql
-- Create partitioned table
CREATE TABLE claims_service.claim_partitioned (
    LIKE claims_service.claim INCLUDING ALL
) PARTITION BY RANGE (service_date);

-- Create monthly partitions
CREATE TABLE claims_service.claim_2024_01 
PARTITION OF claims_service.claim_partitioned 
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE claims_service.claim_2024_02 
PARTITION OF claims_service.claim_partitioned 
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Automated partition creation
CREATE OR REPLACE FUNCTION create_monthly_partition()
RETURNS VOID AS $$
DECLARE
    start_date DATE;
    end_date DATE;
    partition_name TEXT;
BEGIN
    start_date := DATE_TRUNC('month', CURRENT_DATE + INTERVAL '1 month');
    end_date := start_date + INTERVAL '1 month';
    partition_name := 'claim_' || TO_CHAR(start_date, 'YYYY_MM');
    
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS claims_service.%I PARTITION OF claims_service.claim_partitioned FOR VALUES FROM (%L) TO (%L)',
        partition_name,
        start_date,
        end_date
    );
END;
$$ LANGUAGE plpgsql;
```

## Performance Optimization

### Index Strategy

```sql
-- Covering indexes for common queries
CREATE INDEX idx_claim_member_status_date 
ON claims_service.claim(member_id, status, service_date) 
INCLUDE (total_charged_amount, total_approved_amount);

-- Partial indexes for filtered queries
CREATE INDEX idx_claim_pending 
ON claims_service.claim(submission_date) 
WHERE status = 'submitted';

-- BRIN indexes for time-series data
CREATE INDEX idx_claim_service_date_brin 
ON claims_service.claim 
USING BRIN(service_date);
```

### Query Optimization Tips

1. **Use EXPLAIN ANALYZE**
```sql
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM claims_service.claim 
WHERE member_id = '123' 
AND service_date >= '2024-01-01';
```

2. **Optimize JOIN order**
```sql
-- Good: Filter early
SELECT c.*, m.first_name, m.last_name
FROM claims_service.claim c
JOIN member_service.member m ON c.member_id = m.id
WHERE c.status = 'approved'
AND c.service_date >= CURRENT_DATE - INTERVAL '30 days';
```

3. **Use CTEs for complex queries**
```sql
WITH recent_claims AS (
    SELECT * FROM claims_service.claim
    WHERE service_date >= CURRENT_DATE - INTERVAL '30 days'
),
approved_claims AS (
    SELECT * FROM recent_claims
    WHERE status = 'approved'
)
SELECT 
    member_id,
    COUNT(*) as claim_count,
    SUM(total_approved_amount) as total_approved
FROM approved_claims
GROUP BY member_id;
```

## Maintenance

### Regular Tasks

#### Daily
```sql
-- Update statistics
ANALYZE;

-- Check for long-running queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';
```

#### Weekly
```sql
-- Vacuum tables
VACUUM ANALYZE;

-- Check table bloat
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    n_dead_tup,
    n_live_tup,
    round(n_dead_tup::numeric / NULLIF(n_live_tup + n_dead_tup, 0) * 100, 2) AS dead_percentage
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
```

#### Monthly
```sql
-- Reindex if needed
REINDEX SCHEMA claims_service CONCURRENTLY;

-- Archive old data
INSERT INTO archive.claim
SELECT * FROM claims_service.claim
WHERE service_date < CURRENT_DATE - INTERVAL '2 years';

DELETE FROM claims_service.claim
WHERE service_date < CURRENT_DATE - INTERVAL '2 years';
```

## Backup & Recovery

### Backup Strategy

1. **Full Backup** (Daily)
```bash
pg_dump -h localhost -U postgres -d claims_askes \
  --format=custom \
  --verbose \
  --file="backup_$(date +%Y%m%d).dump"
```

2. **Schema-specific Backup**
```bash
pg_dump -h localhost -U postgres -d claims_askes \
  --schema=claims_service \
  --format=custom \
  --file="claims_service_$(date +%Y%m%d).dump"
```

3. **Point-in-Time Recovery Setup**
```bash
# postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /backup/archive/%f'
```

### Restore Procedures

```bash
# Full restore
pg_restore -h localhost -U postgres -d claims_askes_restore \
  --verbose \
  backup_20240115.dump

# Schema-specific restore
pg_restore -h localhost -U postgres -d claims_askes \
  --schema=claims_service \
  --clean \
  --verbose \
  claims_service_20240115.dump
```

## Monitoring

### Key Metrics

```sql
-- Database size
SELECT 
    pg_database.datname,
    pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database;

-- Table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Connection count
SELECT 
    datname,
    numbackends,
    ROUND(100 * numbackends / max_connections::numeric, 2) AS percentage_used
FROM pg_stat_database, 
    (SELECT setting::int AS max_connections FROM pg_settings WHERE name = 'max_connections') s
WHERE datname = 'claims_askes';

-- Slow queries
SELECT 
    mean_exec_time,
    calls,
    query
FROM pg_stat_statements
WHERE mean_exec_time > 1000 -- queries taking more than 1 second
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### Health Checks

```sql
-- Create health check function
CREATE OR REPLACE FUNCTION health_check()
RETURNS TABLE (
    check_name VARCHAR,
    status VARCHAR,
    details TEXT
) AS $$
BEGIN
    -- Check connection count
    RETURN QUERY
    SELECT 
        'connection_count'::VARCHAR,
        CASE 
            WHEN numbackends < max_connections * 0.8 THEN 'healthy'
            WHEN numbackends < max_connections * 0.9 THEN 'warning'
            ELSE 'critical'
        END::VARCHAR,
        format('Connections: %s/%s', numbackends, max_connections)::TEXT
    FROM pg_stat_database,
        (SELECT setting::int AS max_connections FROM pg_settings WHERE name = 'max_connections') s
    WHERE datname = current_database();
    
    -- Check table bloat
    RETURN QUERY
    SELECT 
        'table_bloat'::VARCHAR,
        CASE 
            WHEN MAX(n_dead_tup::numeric / NULLIF(n_live_tup + n_dead_tup, 0)) < 0.1 THEN 'healthy'
            WHEN MAX(n_dead_tup::numeric / NULLIF(n_live_tup + n_dead_tup, 0)) < 0.2 THEN 'warning'
            ELSE 'critical'
        END::VARCHAR,
        format('Max dead tuple ratio: %s%%', 
            ROUND(MAX(n_dead_tup::numeric / NULLIF(n_live_tup + n_dead_tup, 0)) * 100, 2)
        )::TEXT
    FROM pg_stat_user_tables;
    
    -- Check replication lag (if applicable)
    IF EXISTS (SELECT 1 FROM pg_stat_replication) THEN
        RETURN QUERY
        SELECT 
            'replication_lag'::VARCHAR,
            CASE 
                WHEN MAX(replay_lag) < interval '1 second' THEN 'healthy'
                WHEN MAX(replay_lag) < interval '5 seconds' THEN 'warning'
                ELSE 'critical'
            END::VARCHAR,
            format('Max lag: %s', MAX(replay_lag))::TEXT
        FROM pg_stat_replication;
    END IF;
END;
$$ LANGUAGE plpgsql;
```

## Security

### Access Control

```sql
-- Revoke all default privileges
REVOKE ALL ON SCHEMA public FROM PUBLIC;

-- Grant schema-specific access
GRANT USAGE ON SCHEMA claims_service TO claims_service_user;
GRANT ALL ON ALL TABLES IN SCHEMA claims_service TO claims_service_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA claims_service TO claims_service_user;

-- Read-only user for reporting
CREATE ROLE reporting_user WITH LOGIN PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE claims_askes TO reporting_user;
GRANT USAGE ON SCHEMA claims_service TO reporting_user;
GRANT SELECT ON ALL TABLES IN SCHEMA claims_service TO reporting_user;
```

### Row-Level Security

```sql
-- Enable RLS
ALTER TABLE member_service.member ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY member_isolation ON member_service.member
    FOR ALL
    TO member_service_user
    USING (true); -- Adjust based on requirements

-- Data masking for sensitive fields
CREATE OR REPLACE FUNCTION mask_ssn(ssn TEXT)
RETURNS TEXT AS $$
BEGIN
    IF current_user = 'reporting_user' THEN
        RETURN 'XXX-XX-' || RIGHT(ssn, 4);
    ELSE
        RETURN ssn;
    END IF;
END;
$$ LANGUAGE plpgsql;
```

## Migration Management

### Using Alembic (Python)

```python
# alembic.ini
[alembic]
script_location = migrations
sqlalchemy.url = postgresql://user:pass@localhost/claims_askes

# migrations/env.py
from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config
target_metadata = None

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema='claims_service'
        )
        
        with context.begin_transaction():
            context.run_migrations()
```

### Migration Best Practices

1. **Always test migrations on staging first**
2. **Use transactions for DDL changes**
3. **Create rollback scripts**
4. **Version control all migrations**
5. **Document breaking changes**

## Troubleshooting

### Common Issues

1. **Connection Pool Exhaustion**
```sql
-- Check current connections
SELECT * FROM pg_stat_activity;

-- Kill idle connections
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'claims_askes'
AND pid <> pg_backend_pid()
AND state = 'idle'
AND state_change < CURRENT_TIMESTAMP - INTERVAL '10 minutes';
```

2. **Lock Contention**
```sql
-- Find blocking queries
SELECT 
    blocking.pid AS blocking_pid,
    blocking.query AS blocking_query,
    blocked.pid AS blocked_pid,
    blocked.query AS blocked_query
FROM pg_stat_activity AS blocked
JOIN pg_stat_activity AS blocking 
    ON blocking.pid = ANY(pg_blocking_pids(blocked.pid));
```

3. **Slow Queries**
```sql
-- Enable slow query logging
ALTER SYSTEM SET log_min_duration_statement = '1000'; -- Log queries over 1 second
SELECT pg_reload_conf();
```

## Development Guidelines

### Naming Conventions

- **Tables**: snake_case, singular (e.g., `claim`, `member`)
- **Columns**: snake_case (e.g., `claim_number`, `service_date`)
- **Indexes**: `idx_<table>_<columns>` (e.g., `idx_claim_member_id`)
- **Constraints**: `chk_<table>_<rule>` (e.g., `chk_claim_dates`)
- **Foreign Keys**: `fk_<table>_<referenced_table>` (e.g., `fk_claim_member`)

### SQL Standards

1. **Use explicit JOINs**
2. **Avoid SELECT ***
3. **Use CTEs for readability**
4. **Add comments for complex logic**
5. **Use transactions appropriately**

## Support

- **DBA Team**: dba@claims-askes.com
- **On-call**: PagerDuty for P1 issues
- **Documentation**: Internal wiki
- **Monitoring**: Grafana dashboards

## License

Proprietary - All rights reserved