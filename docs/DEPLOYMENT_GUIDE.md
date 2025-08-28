# Deployment Guide - Claims-Askes Platform

## Overview

This guide provides comprehensive instructions for deploying the Claims-Askes platform across different environments: Development, Staging, and Production.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Deployment](#database-deployment)
4. [Microservices Deployment](#microservices-deployment)
5. [Docker Deployment](#docker-deployment)
6. [Kubernetes Deployment](#kubernetes-deployment)
7. [Configuration Management](#configuration-management)
8. [Health Checks & Monitoring](#health-checks--monitoring)
9. [Backup & Recovery](#backup--recovery)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

#### Minimum Requirements (Development)
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Storage**: 50 GB SSD
- **OS**: Ubuntu 20.04+ / CentOS 8+ / macOS 12+

#### Recommended Requirements (Production)
- **CPU**: 16+ cores
- **RAM**: 32+ GB
- **Storage**: 500+ GB SSD (RAID configuration)
- **OS**: Ubuntu 22.04 LTS / RHEL 8+
- **Network**: Redundant network connections

### Software Dependencies
```bash
# Core Requirements
Python 3.11+
Node.js 18+
Docker 24+
Docker Compose 2.20+
PostgreSQL 15+
Redis 7+
nginx 1.24+

# Optional (Production)
Kubernetes 1.28+
Helm 3.12+
Terraform 1.5+
Ansible 2.15+
```

## Environment Setup

### 1. Development Environment

```bash
# Clone repository
git clone https://github.com/your-org/claims-askes.git
cd claims-askes

# Create project structure
chmod +x create_microservices_structure.sh
./create_microservices_structure.sh

# Start infrastructure
docker-compose -f docker-compose.dev.yml up -d

# Initialize database
docker exec -i claims-postgres psql -U postgres -d claims_askes < database/init.sql

# Setup Python environment for each service
cd services/claims-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run service
uvicorn src.main:app --reload --port 8001
```

### 2. Staging Environment

```bash
# Use Docker Compose with staging configuration
docker-compose -f docker-compose.staging.yml up -d

# Apply staging configurations
export ENVIRONMENT=staging
export DATABASE_URL=postgresql://user:pass@staging-db:5432/claims_askes

# Deploy all services
./scripts/deploy-staging.sh
```

### 3. Production Environment

Production deployment uses Kubernetes for orchestration.

## Database Deployment

### PostgreSQL Setup

#### 1. Single Instance with Schema Separation (Dev/Staging)
```sql
-- Create database
CREATE DATABASE claims_askes;

-- Run initialization script
psql -U postgres -d claims_askes < database/init.sql

-- Verify schemas
\dn+
```

#### 2. High Availability Setup (Production)
```bash
# Primary-Replica Configuration
# Primary server
postgresql.conf:
wal_level = replica
max_wal_senders = 3
wal_keep_segments = 64
synchronous_commit = on

# Replica server
recovery.conf:
standby_mode = 'on'
primary_conninfo = 'host=primary port=5432 user=replicator'
```

### Database Migrations
```bash
# Run migrations for each service
cd services/claims-service
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### Backup Strategy
```bash
# Automated daily backups
0 2 * * * pg_dump -U postgres claims_askes > /backup/claims_askes_$(date +\%Y\%m\%d).sql

# Point-in-time recovery setup
archive_mode = on
archive_command = 'cp %p /archive/%f'
```

## Microservices Deployment

### Service Configuration

Each service requires environment-specific configuration:

```bash
# services/claims-service/.env.production
DATABASE_URL=postgresql://claims_service_user:prod_pass@prod-db:5432/claims_askes
REDIS_URL=redis://prod-redis:6379/0
RABBITMQ_URL=amqp://admin:admin@prod-rabbitmq:5672/
JWT_SECRET=production-secret-key
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
```

### Service Startup Order

Deploy services in this order to respect dependencies:

1. **Infrastructure Services**
   ```bash
   # Start in order
   docker-compose up -d postgres redis rabbitmq minio
   
   # Wait for readiness
   ./scripts/wait-for-it.sh postgres:5432
   ./scripts/wait-for-it.sh redis:6379
   ```

2. **Core Services**
   ```bash
   # Deploy core services
   docker-compose up -d \
     member-service \
     provider-service \
     benefit-service \
     policy-service
   ```

3. **Processing Services**
   ```bash
   # Deploy processing services
   docker-compose up -d \
     claims-service \
     authorization-service \
     adjudication-service \
     payment-service
   ```

4. **Support Services**
   ```bash
   # Deploy support services
   docker-compose up -d \
     notification-service \
     document-service
   ```

5. **BFF & Gateway**
   ```bash
   # Deploy BFF and API Gateway
   docker-compose up -d web-bff mobile-bff nginx
   ```

## Docker Deployment

### Building Docker Images

```dockerfile
# services/claims-service/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/
COPY migrations/ ./migrations/

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Building Images
```bash
# Build all service images
docker-compose build

# Build specific service
docker build -t claims-askes/claims-service:latest ./services/claims-service

# Push to registry
docker push claims-askes/claims-service:latest
```

### Docker Compose Production
```yaml
# docker-compose.production.yml
version: '3.8'

services:
  claims-service:
    image: claims-askes/claims-service:latest
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    environment:
      - ENVIRONMENT=production
    networks:
      - claims-network
```

## Kubernetes Deployment

### Kubernetes Manifests

```yaml
# k8s/claims-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: claims-service
  namespace: claims-askes
spec:
  replicas: 3
  selector:
    matchLabels:
      app: claims-service
  template:
    metadata:
      labels:
        app: claims-service
    spec:
      containers:
      - name: claims-service
        image: claims-askes/claims-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: claims-secrets
              key: database-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: claims-service
  namespace: claims-askes
spec:
  selector:
    app: claims-service
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
```

### Helm Deployment
```bash
# Create namespace
kubectl create namespace claims-askes

# Install with Helm
helm install claims-platform ./helm-charts/claims-platform \
  --namespace claims-askes \
  --values helm-charts/claims-platform/values.production.yaml

# Upgrade deployment
helm upgrade claims-platform ./helm-charts/claims-platform \
  --namespace claims-askes \
  --values helm-charts/claims-platform/values.production.yaml

# Check status
kubectl get pods -n claims-askes
```

### Auto-scaling Configuration
```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: claims-service-hpa
  namespace: claims-askes
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: claims-service
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## Configuration Management

### Environment Variables Management

```bash
# Create ConfigMap for non-sensitive config
kubectl create configmap app-config \
  --from-env-file=config/production.env \
  -n claims-askes

# Create Secrets for sensitive data
kubectl create secret generic claims-secrets \
  --from-literal=database-url='postgresql://user:pass@db/claims' \
  --from-literal=jwt-secret='production-secret' \
  -n claims-askes
```

### Service Discovery

```yaml
# k8s/service-discovery.yaml
apiVersion: v1
kind: Service
metadata:
  name: service-discovery
  namespace: claims-askes
spec:
  clusterIP: None
  selector:
    app: microservice
  ports:
  - port: 80
```

### API Gateway Configuration

```nginx
# gateway/nginx/nginx.conf
upstream claims-service {
    server claims-service:8000 max_fails=3 fail_timeout=30s;
}

upstream member-service {
    server member-service:8000 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name api.claims-askes.com;

    location /api/v1/claims {
        proxy_pass http://claims-service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/v1/members {
        proxy_pass http://member-service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Health Checks & Monitoring

### Service Health Checks

```python
# src/health.py
from fastapi import APIRouter, status
from sqlalchemy import text

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.get("/ready")
async def readiness_check(db: Session):
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        # Check Redis connection
        redis_client.ping()
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not ready", "error": str(e)}, status.HTTP_503_SERVICE_UNAVAILABLE
```

### Monitoring Stack

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"
      - "14268:14268"
```

### Logging Configuration

```python
# src/utils/logging.py
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "service": "claims-service",
            "message": record.getMessage(),
            "correlation_id": getattr(record, 'correlation_id', None)
        }
        return json.dumps(log_obj)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
```

## Backup & Recovery

### Database Backup

```bash
#!/bin/bash
# scripts/backup-database.sh

# Configuration
BACKUP_DIR="/backup/postgres"
DB_NAME="claims_askes"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup
pg_dump -U postgres -d $DB_NAME > $BACKUP_DIR/backup_$TIMESTAMP.sql

# Compress backup
gzip $BACKUP_DIR/backup_$TIMESTAMP.sql

# Upload to S3
aws s3 cp $BACKUP_DIR/backup_$TIMESTAMP.sql.gz \
  s3://claims-askes-backups/postgres/

# Clean old backups (keep last 30 days)
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

### Disaster Recovery Plan

1. **RTO (Recovery Time Objective)**: 1 hour
2. **RPO (Recovery Point Objective)**: 15 minutes

```bash
# Restore from backup
gunzip < backup_20240120_020000.sql.gz | psql -U postgres -d claims_askes

# Verify restoration
psql -U postgres -d claims_askes -c "SELECT COUNT(*) FROM claims_service.claim;"
```

## Troubleshooting

### Common Issues

#### 1. Service Cannot Connect to Database
```bash
# Check database connectivity
nc -zv postgres-host 5432

# Check credentials
psql -h postgres-host -U claims_service_user -d claims_askes

# Check user permissions
\du claims_service_user
```

#### 2. Service Discovery Issues
```bash
# Check service endpoints
kubectl get endpoints -n claims-askes

# Check service DNS
nslookup claims-service.claims-askes.svc.cluster.local

# Check pod status
kubectl describe pod claims-service-xxx -n claims-askes
```

#### 3. High Memory Usage
```bash
# Check memory usage
kubectl top pods -n claims-askes

# Restart pod
kubectl delete pod claims-service-xxx -n claims-askes

# Scale deployment
kubectl scale deployment claims-service --replicas=5 -n claims-askes
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
export DEBUG=True

# View logs
kubectl logs -f deployment/claims-service -n claims-askes

# Execute into pod
kubectl exec -it claims-service-xxx -n claims-askes -- /bin/bash
```

### Performance Tuning

```python
# Optimize database connections
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_POOL_RECYCLE = 3600
SQLALCHEMY_MAX_OVERFLOW = 40

# Optimize Redis connections
REDIS_POOL_SIZE = 50
REDIS_POOL_TIMEOUT = 20

# Optimize async operations
import uvloop
uvloop.install()
```

## Security Hardening

### Production Security Checklist

- [ ] Use secrets management (Vault, K8s Secrets)
- [ ] Enable TLS/SSL for all communications
- [ ] Implement network policies
- [ ] Regular security updates
- [ ] Vulnerability scanning
- [ ] Access logging and monitoring
- [ ] Rate limiting
- [ ] Input validation
- [ ] SQL injection prevention
- [ ] CORS configuration

### Network Policies
```yaml
# k8s/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: claims-service-policy
  namespace: claims-askes
spec:
  podSelector:
    matchLabels:
      app: claims-service
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: api-gateway
    ports:
    - protocol: TCP
      port: 8000
```

## Deployment Checklist

### Pre-deployment
- [ ] Code review completed
- [ ] Unit tests passing (>80% coverage)
- [ ] Integration tests passing
- [ ] Security scan completed
- [ ] Documentation updated
- [ ] Database migrations prepared
- [ ] Configuration verified

### Deployment
- [ ] Backup current database
- [ ] Deploy to staging first
- [ ] Run smoke tests
- [ ] Deploy to production (blue-green)
- [ ] Verify health checks
- [ ] Monitor metrics

### Post-deployment
- [ ] Verify all services healthy
- [ ] Check error rates
- [ ] Monitor performance metrics
- [ ] Update documentation
- [ ] Notify stakeholders

## Support

For deployment support:
- Documentation: [Full Docs](../README.md)
- Issues: Create ticket in issue tracker
- Emergency: Contact DevOps team
- Slack: #claims-askes-deployment