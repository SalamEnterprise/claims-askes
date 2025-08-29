# Claims Service Database Documentation

## Overview

The Claims Service uses PostgreSQL with its own dedicated schema `claims_service`. It follows the database-per-service pattern where this service exclusively owns and manages its schema.

## Database Configuration

### Connection Details
```
Host: PostgreSQL instance
Port: 5432
Database: claims_askes
Schema: claims_service
User: claims_service_user
```

### Connection String
```
postgresql://claims_service_user:password@localhost:5432/claims_askes
```

## Schema Design

### Schema: `claims_service`

This schema contains all tables, indexes, and database objects owned by the Claims Service.

## Tables

### 1. claim

Main table storing claim information.

```sql
CREATE TABLE claims_service.claim (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_number VARCHAR(50) UNIQUE NOT NULL,
    member_id UUID NOT NULL,
    provider_id UUID NOT NULL,
    policy_id UUID NOT NULL,
    
    -- Claim details
    claim_type VARCHAR(20) NOT NULL,
    service_type VARCHAR(20) NOT NULL,
    admission_date DATE,
    discharge_date DATE,
    service_date DATE NOT NULL,
    
    -- Status tracking
    status VARCHAR(30) NOT NULL DEFAULT 'submitted',
    submission_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Financial summary
    total_charged_amount DECIMAL(15,2),
    total_approved_amount DECIMAL(15,2),
    total_paid_amount DECIMAL(15,2),
    member_responsibility DECIMAL(15,2),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    
    -- Constraints
    CONSTRAINT chk_claim_type CHECK (claim_type IN ('cashless', 'reimbursement')),
    CONSTRAINT chk_service_type CHECK (service_type IN ('inpatient', 'outpatient', 'dental', 'optical', 'maternity')),
    CONSTRAINT chk_status CHECK (status IN ('submitted', 'processing', 'pending_info', 'approved', 'rejected', 'payment_processing', 'paid', 'cancelled'))
);
```

**Indexes:**
```sql
CREATE INDEX idx_claim_member_id ON claims_service.claim(member_id);
CREATE INDEX idx_claim_provider_id ON claims_service.claim(provider_id);
CREATE INDEX idx_claim_policy_id ON claims_service.claim(policy_id);
CREATE INDEX idx_claim_status ON claims_service.claim(status);
CREATE INDEX idx_claim_service_date ON claims_service.claim(service_date);
CREATE INDEX idx_claim_submission_date ON claims_service.claim(submission_date);
CREATE INDEX idx_claim_claim_type ON claims_service.claim(claim_type);
CREATE INDEX idx_claim_service_type ON claims_service.claim(service_type);
```

### 2. claim_item

Line items for each claim.

```sql
CREATE TABLE claims_service.claim_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id UUID NOT NULL REFERENCES claims_service.claim(id) ON DELETE CASCADE,
    
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
    
    -- Adjudication details
    deductible_amount DECIMAL(15,2) DEFAULT 0,
    coinsurance_amount DECIMAL(15,2) DEFAULT 0,
    copay_amount DECIMAL(15,2) DEFAULT 0,
    
    -- Status
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    denial_reason VARCHAR(500),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT chk_quantity CHECK (quantity > 0),
    CONSTRAINT chk_amounts CHECK (charged_amount >= 0)
);
```

**Indexes:**
```sql
CREATE INDEX idx_claim_item_claim_id ON claims_service.claim_item(claim_id);
CREATE INDEX idx_claim_item_benefit_code ON claims_service.claim_item(benefit_code);
CREATE INDEX idx_claim_item_status ON claims_service.claim_item(status);
```

### 3. claim_document

Documents attached to claims.

```sql
CREATE TABLE claims_service.claim_document (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id UUID NOT NULL REFERENCES claims_service.claim(id) ON DELETE CASCADE,
    
    -- Document details
    document_type VARCHAR(50) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    checksum VARCHAR(255),
    
    -- Metadata
    uploaded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    uploaded_by VARCHAR(100),
    
    -- Constraints
    CONSTRAINT chk_document_type CHECK (document_type IN ('invoice', 'prescription', 'medical_report', 'lab_result', 'referral', 'authorization', 'other'))
);
```

**Indexes:**
```sql
CREATE INDEX idx_claim_document_claim_id ON claims_service.claim_document(claim_id);
CREATE INDEX idx_claim_document_type ON claims_service.claim_document(document_type);
CREATE INDEX idx_claim_document_uploaded_at ON claims_service.claim_document(uploaded_at);
```

### 4. claim_status_history

Audit trail of claim status changes.

```sql
CREATE TABLE claims_service.claim_status_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id UUID NOT NULL REFERENCES claims_service.claim(id) ON DELETE CASCADE,
    
    -- Status change details
    old_status VARCHAR(30),
    new_status VARCHAR(30) NOT NULL,
    changed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    changed_by VARCHAR(100),
    notes TEXT,
    
    -- Additional context
    ip_address VARCHAR(45),
    user_agent TEXT
);
```

**Indexes:**
```sql
CREATE INDEX idx_claim_status_history_claim_id ON claims_service.claim_status_history(claim_id);
CREATE INDEX idx_claim_status_history_changed_at ON claims_service.claim_status_history(changed_at);
```

### 5. claim_note

Internal notes and comments on claims.

```sql
CREATE TABLE claims_service.claim_note (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id UUID NOT NULL REFERENCES claims_service.claim(id) ON DELETE CASCADE,
    
    -- Note details
    note_type VARCHAR(50) NOT NULL,
    note_text TEXT NOT NULL,
    is_internal BOOLEAN DEFAULT true,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_by VARCHAR(100) NOT NULL
);
```

**Indexes:**
```sql
CREATE INDEX idx_claim_note_claim_id ON claims_service.claim_note(claim_id);
CREATE INDEX idx_claim_note_created_at ON claims_service.claim_note(created_at);
```

## Views

### 1. claim_summary_view

Aggregated view for reporting and dashboards.

```sql
CREATE VIEW claims_service.claim_summary_view AS
SELECT 
    c.id,
    c.claim_number,
    c.member_id,
    c.provider_id,
    c.claim_type,
    c.service_type,
    c.service_date,
    c.status,
    c.submission_date,
    c.total_charged_amount,
    c.total_approved_amount,
    c.total_paid_amount,
    c.member_responsibility,
    COUNT(ci.id) as item_count,
    COUNT(cd.id) as document_count
FROM claims_service.claim c
LEFT JOIN claims_service.claim_item ci ON c.id = ci.claim_id
LEFT JOIN claims_service.claim_document cd ON c.id = cd.claim_id
GROUP BY c.id;
```

### 2. pending_claims_view

View of claims requiring action.

```sql
CREATE VIEW claims_service.pending_claims_view AS
SELECT 
    c.*,
    EXTRACT(EPOCH FROM (NOW() - c.submission_date))/3600 as hours_pending
FROM claims_service.claim c
WHERE c.status IN ('submitted', 'processing', 'pending_info')
ORDER BY c.submission_date ASC;
```

## Functions & Procedures

### 1. update_claim_totals()

Trigger function to update claim totals when items change.

```sql
CREATE OR REPLACE FUNCTION claims_service.update_claim_totals()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE claims_service.claim
    SET 
        total_charged_amount = (
            SELECT COALESCE(SUM(charged_amount), 0)
            FROM claims_service.claim_item
            WHERE claim_id = NEW.claim_id
        ),
        total_approved_amount = (
            SELECT COALESCE(SUM(approved_amount), 0)
            FROM claims_service.claim_item
            WHERE claim_id = NEW.claim_id
        ),
        total_paid_amount = (
            SELECT COALESCE(SUM(paid_amount), 0)
            FROM claims_service.claim_item
            WHERE claim_id = NEW.claim_id
        ),
        updated_at = NOW()
    WHERE id = NEW.claim_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### 2. generate_claim_number()

Generate unique claim number.

```sql
CREATE OR REPLACE FUNCTION claims_service.generate_claim_number()
RETURNS VARCHAR AS $$
DECLARE
    v_year VARCHAR(4);
    v_sequence INTEGER;
    v_claim_number VARCHAR(50);
BEGIN
    v_year := TO_CHAR(NOW(), 'YYYY');
    
    SELECT COALESCE(MAX(CAST(SUBSTRING(claim_number FROM 10) AS INTEGER)), 0) + 1
    INTO v_sequence
    FROM claims_service.claim
    WHERE claim_number LIKE 'CLM-' || v_year || '-%';
    
    v_claim_number := 'CLM-' || v_year || '-' || LPAD(v_sequence::VARCHAR, 6, '0');
    
    RETURN v_claim_number;
END;
$$ LANGUAGE plpgsql;
```

## Triggers

### 1. Update timestamp trigger

```sql
CREATE TRIGGER update_claim_timestamp
BEFORE UPDATE ON claims_service.claim
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_claim_item_timestamp
BEFORE UPDATE ON claims_service.claim_item
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();
```

### 2. Update claim totals trigger

```sql
CREATE TRIGGER update_claim_totals_trigger
AFTER INSERT OR UPDATE OR DELETE ON claims_service.claim_item
FOR EACH ROW
EXECUTE FUNCTION claims_service.update_claim_totals();
```

### 3. Generate claim number trigger

```sql
CREATE TRIGGER generate_claim_number_trigger
BEFORE INSERT ON claims_service.claim
FOR EACH ROW
WHEN (NEW.claim_number IS NULL)
EXECUTE FUNCTION claims_service.generate_claim_number();
```

### 4. Log status changes trigger

```sql
CREATE TRIGGER log_claim_status_change
AFTER UPDATE ON claims_service.claim
FOR EACH ROW
WHEN (OLD.status IS DISTINCT FROM NEW.status)
EXECUTE FUNCTION claims_service.log_status_change();
```

## Data Types & Enums

### Status Enum
```sql
CREATE TYPE claims_service.claim_status AS ENUM (
    'submitted',
    'processing',
    'pending_info',
    'approved',
    'rejected',
    'payment_processing',
    'paid',
    'cancelled'
);
```

### Claim Type Enum
```sql
CREATE TYPE claims_service.claim_type AS ENUM (
    'cashless',
    'reimbursement'
);
```

### Service Type Enum
```sql
CREATE TYPE claims_service.service_type AS ENUM (
    'inpatient',
    'outpatient',
    'dental',
    'optical',
    'maternity'
);
```

## Partitioning Strategy

For high-volume production environments, partition claims table by service_date:

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
```

## Performance Optimization

### Query Optimization Tips

1. **Use indexes effectively**
   - Always filter by indexed columns when possible
   - Use compound indexes for common query patterns

2. **Optimize pagination**
   ```sql
   -- Good: Use cursor-based pagination
   SELECT * FROM claims_service.claim
   WHERE id > $last_id
   ORDER BY id
   LIMIT 20;
   
   -- Avoid: OFFSET for large datasets
   SELECT * FROM claims_service.claim
   OFFSET 10000 LIMIT 20;
   ```

3. **Use appropriate data types**
   - Use UUID for IDs (better for distributed systems)
   - Use DECIMAL for monetary values
   - Use appropriate VARCHAR lengths

### Maintenance Tasks

1. **Regular VACUUM**
   ```sql
   VACUUM ANALYZE claims_service.claim;
   ```

2. **Update statistics**
   ```sql
   ANALYZE claims_service.claim;
   ```

3. **Reindex periodically**
   ```sql
   REINDEX TABLE claims_service.claim;
   ```

## Backup & Recovery

### Backup Strategy
- Daily full backups
- Hourly incremental backups
- Transaction log archiving

### Backup Commands
```bash
# Backup schema only
pg_dump -h localhost -U postgres -d claims_askes \
  --schema=claims_service \
  -f claims_service_backup.sql

# Backup with data
pg_dump -h localhost -U postgres -d claims_askes \
  --schema=claims_service \
  --data-only \
  -f claims_service_data.sql
```

### Restore Commands
```bash
# Restore schema and data
psql -h localhost -U postgres -d claims_askes < claims_service_backup.sql
```

## Monitoring Queries

### Check table sizes
```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'claims_service'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Check slow queries
```sql
SELECT 
    query,
    calls,
    mean_exec_time,
    total_exec_time
FROM pg_stat_statements
WHERE query LIKE '%claims_service%'
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### Check index usage
```sql
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'claims_service'
ORDER BY idx_scan DESC;
```

## Security

### Row-Level Security (RLS)
```sql
-- Enable RLS
ALTER TABLE claims_service.claim ENABLE ROW LEVEL SECURITY;

-- Create policy for service user
CREATE POLICY claims_service_policy ON claims_service.claim
FOR ALL
TO claims_service_user
USING (true);
```

### Audit Logging
All sensitive operations are logged to the audit schema:
- Claim status changes
- Document uploads
- Data modifications

## Migration Management

Using Alembic for database migrations:

```bash
# Create new migration
alembic revision --autogenerate -m "Add new column to claim table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Contact

For database-related issues:
- DBA Team: dba@claims-askes.com
- On-call: Use PagerDuty