# Infrastructure Documentation

## Overview

This directory contains infrastructure-as-code (IaC) configurations, deployment scripts, and operational guides for the Claims-Askes health insurance platform. We use a cloud-native, containerized architecture with support for multiple deployment environments.

## Infrastructure Stack

### Core Technologies
- **Container Orchestration**: Kubernetes 1.28+
- **Container Runtime**: Docker 24+
- **Infrastructure as Code**: Terraform 1.5+
- **Configuration Management**: Helm 3.12+
- **Service Mesh**: Istio 1.19+
- **CI/CD**: GitLab CI / GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Tracing**: Jaeger

## Architecture Overview

```
┌────────────────────────────────────────────────────┐
│                   Load Balancer                    │
└────────────────────────────────────────────────────┘
                           │
┌────────────────────────────────────────────────────┐
│                   API Gateway                      │
│                  (Kong/Nginx)                      │
└────────────────────────────────────────────────────┘
                           │
┌────────────────────────────────────────────────────┐
│                  Service Mesh                      │
│                    (Istio)                         │
├────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │   BFF    │  │   BFF    │  │ Gateway  │        │
│  │   Web    │  │  Mobile  │  │  Admin   │        │
│  └──────────┘  └──────────┘  └──────────┘        │
├────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  Claims  │  │  Member  │  │ Provider │  ...   │
│  │  Service │  │  Service │  │ Service  │        │
│  └──────────┘  └──────────┘  └──────────┘        │
└────────────────────────────────────────────────────┘
                           │
┌────────────────────────────────────────────────────┐
│              Data Layer                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │PostgreSQL│  │  Redis   │  │ RabbitMQ │        │
│  └──────────┘  └──────────┘  └──────────┘        │
└────────────────────────────────────────────────────┘
```

## Directory Structure

```
infrastructure/
├── terraform/           # Infrastructure as Code
│   ├── environments/    # Environment-specific configs
│   │   ├── dev/
│   │   ├── staging/
│   │   └── production/
│   ├── modules/         # Reusable Terraform modules
│   │   ├── eks/         # AWS EKS cluster
│   │   ├── rds/         # RDS PostgreSQL
│   │   ├── elasticache/ # Redis cluster
│   │   ├── vpc/         # Network configuration
│   │   └── s3/          # Object storage
│   └── backend.tf       # Terraform state configuration
├── kubernetes/          # Kubernetes manifests
│   ├── base/            # Base configurations
│   ├── overlays/        # Environment overlays
│   └── helm/            # Helm charts
├── docker/              # Docker configurations
│   ├── base/            # Base images
│   └── services/        # Service-specific Dockerfiles
├── scripts/             # Deployment and utility scripts
│   ├── deploy.sh
│   ├── rollback.sh
│   └── health-check.sh
└── monitoring/          # Monitoring configurations
    ├── prometheus/
    ├── grafana/
    └── alerts/
```

## Environment Configuration

### Development Environment

```yaml
# infrastructure/kubernetes/overlays/dev/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

bases:
  - ../../base

replicas:
  - name: claims-service
    count: 1
  - name: member-service
    count: 1

resources:
  - namespace.yaml
  - ingress.yaml

configMapGenerator:
  - name: env-config
    literals:
      - ENVIRONMENT=development
      - LOG_LEVEL=debug
      - DATABASE_HOST=postgres-dev.local
```

### Staging Environment

```yaml
# infrastructure/kubernetes/overlays/staging/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

bases:
  - ../../base

replicas:
  - name: claims-service
    count: 2
  - name: member-service
    count: 2

resources:
  - namespace.yaml
  - ingress.yaml
  - network-policy.yaml

configMapGenerator:
  - name: env-config
    literals:
      - ENVIRONMENT=staging
      - LOG_LEVEL=info
      - DATABASE_HOST=postgres-staging.aws.com
```

### Production Environment

```yaml
# infrastructure/kubernetes/overlays/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

bases:
  - ../../base

replicas:
  - name: claims-service
    count: 5
  - name: member-service
    count: 5

resources:
  - namespace.yaml
  - ingress.yaml
  - network-policy.yaml
  - pod-disruption-budget.yaml

configMapGenerator:
  - name: env-config
    literals:
      - ENVIRONMENT=production
      - LOG_LEVEL=warn
      - DATABASE_HOST=postgres-prod.aws.com
```

## Terraform Configuration

### AWS EKS Cluster

```hcl
# infrastructure/terraform/modules/eks/main.tf
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "claims-askes-${var.environment}"
  cluster_version = "1.28"

  vpc_id     = var.vpc_id
  subnet_ids = var.private_subnets

  # Node groups configuration
  eks_managed_node_groups = {
    general = {
      desired_size = var.environment == "production" ? 5 : 2
      min_size     = var.environment == "production" ? 3 : 1
      max_size     = var.environment == "production" ? 10 : 4

      instance_types = ["t3.medium"]
      
      k8s_labels = {
        Environment = var.environment
        NodeType    = "general"
      }
    }
    
    spot = {
      desired_size = var.environment == "production" ? 3 : 1
      min_size     = 0
      max_size     = var.environment == "production" ? 6 : 2

      instance_types = ["t3.medium", "t3a.medium"]
      capacity_type  = "SPOT"
      
      k8s_labels = {
        Environment = var.environment
        NodeType    = "spot"
      }
      
      taints = [{
        key    = "spot"
        value  = "true"
        effect = "NoSchedule"
      }]
    }
  }

  # OIDC Provider for IRSA
  enable_irsa = true

  # Addons
  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    aws-ebs-csi-driver = {
      most_recent = true
    }
  }
}
```

### RDS PostgreSQL

```hcl
# infrastructure/terraform/modules/rds/main.tf
module "rds" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 6.0"

  identifier = "claims-askes-${var.environment}"

  engine            = "postgres"
  engine_version    = "15.4"
  instance_class    = var.environment == "production" ? "db.r6g.xlarge" : "db.t3.medium"
  allocated_storage = var.environment == "production" ? 100 : 20
  storage_encrypted = true

  db_name  = "claims_askes"
  username = "postgres"
  port     = "5432"

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.database.name

  # Backups
  backup_retention_period = var.environment == "production" ? 30 : 7
  backup_window          = "03:00-06:00"
  maintenance_window     = "Mon:00:00-Mon:03:00"

  # High Availability
  multi_az = var.environment == "production" ? true : false

  # Performance Insights
  performance_insights_enabled = var.environment == "production" ? true : false
  performance_insights_retention_period = 7

  # Monitoring
  enabled_cloudwatch_logs_exports = ["postgresql"]
  monitoring_interval             = "30"
  monitoring_role_arn            = aws_iam_role.rds_enhanced_monitoring.arn

  tags = {
    Environment = var.environment
    Application = "claims-askes"
  }
}
```

## Kubernetes Deployments

### Service Deployment

```yaml
# infrastructure/kubernetes/base/claims-service/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: claims-service
  labels:
    app: claims-service
    version: v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: claims-service
  template:
    metadata:
      labels:
        app: claims-service
        version: v1
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: claims-service
      containers:
      - name: claims-service
        image: claims-askes/claims-service:latest
        ports:
        - containerPort: 8001
          name: http
        - containerPort: 9090
          name: metrics
        env:
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: env-config
              key: ENVIRONMENT
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: url
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8001
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: config
          mountPath: /app/config
          readOnly: true
      volumes:
      - name: config
        configMap:
          name: claims-service-config
```

### Horizontal Pod Autoscaler

```yaml
# infrastructure/kubernetes/base/claims-service/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: claims-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: claims-service
  minReplicas: 2
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
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
```

## Service Mesh (Istio)

### Virtual Service

```yaml
# infrastructure/kubernetes/istio/virtual-service.yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: claims-service
spec:
  hosts:
  - claims-service
  http:
  - match:
    - headers:
        x-version:
          exact: v2
    route:
    - destination:
        host: claims-service
        subset: v2
      weight: 100
  - route:
    - destination:
        host: claims-service
        subset: v1
      weight: 90
    - destination:
        host: claims-service
        subset: v2
      weight: 10
    timeout: 30s
    retries:
      attempts: 3
      perTryTimeout: 10s
      retryOn: 5xx,reset,connect-failure,refused-stream
```

### Destination Rule

```yaml
# infrastructure/kubernetes/istio/destination-rule.yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: claims-service
spec:
  host: claims-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 50
        http2MaxRequests: 100
        maxRequestsPerConnection: 2
    loadBalancer:
      simple: LEAST_REQUEST
    outlierDetection:
      consecutiveErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
      minHealthPercent: 30
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy to Kubernetes

on:
  push:
    branches:
      - main
      - staging
      - develop

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to ECR
      uses: aws-actions/amazon-ecr-login@v1
    
    - name: Build and push Docker images
      run: |
        for service in claims-service member-service provider-service; do
          docker buildx build \
            --platform linux/amd64,linux/arm64 \
            --push \
            -t ${{ secrets.ECR_REGISTRY }}/$service:${{ github.sha }} \
            -t ${{ secrets.ECR_REGISTRY }}/$service:latest \
            ./services/$service
        done
    
    - name: Update Kubernetes manifests
      run: |
        sed -i "s|image: .*|image: ${{ secrets.ECR_REGISTRY }}/claims-service:${{ github.sha }}|" \
          infrastructure/kubernetes/base/claims-service/deployment.yaml
    
    - name: Deploy to Kubernetes
      run: |
        if [ "${{ github.ref }}" == "refs/heads/main" ]; then
          ENV="production"
        elif [ "${{ github.ref }}" == "refs/heads/staging" ]; then
          ENV="staging"
        else
          ENV="dev"
        fi
        
        kubectl apply -k infrastructure/kubernetes/overlays/$ENV
```

## Monitoring Stack

### Prometheus Configuration

```yaml
# infrastructure/monitoring/prometheus/values.yaml
prometheus:
  prometheusSpec:
    storageSpec:
      volumeClaimTemplate:
        spec:
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 50Gi
    
    retention: 30d
    
    serviceMonitorSelector:
      matchLabels:
        prometheus: kube-prometheus
    
    resources:
      requests:
        memory: 2Gi
        cpu: 1
      limits:
        memory: 4Gi
        cpu: 2
    
    additionalScrapeConfigs:
    - job_name: 'kubernetes-pods'
      kubernetes_sd_configs:
      - role: pod
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
```

### Grafana Dashboards

```json
// infrastructure/monitoring/grafana/dashboards/claims-service.json
{
  "dashboard": {
    "title": "Claims Service Dashboard",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{service=\"claims-service\"}[5m])"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{service=\"claims-service\",status=~\"5..\"}[5m])"
          }
        ]
      },
      {
        "title": "P95 Latency",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{service=\"claims-service\"}[5m]))"
          }
        ]
      }
    ]
  }
}
```

## Logging Configuration

### Fluentd DaemonSet

```yaml
# infrastructure/monitoring/logging/fluentd-daemonset.yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
  namespace: kube-system
spec:
  selector:
    matchLabels:
      name: fluentd
  template:
    metadata:
      labels:
        name: fluentd
    spec:
      serviceAccountName: fluentd
      containers:
      - name: fluentd
        image: fluent/fluentd-kubernetes-daemonset:v1-debian-elasticsearch
        env:
        - name: FLUENT_ELASTICSEARCH_HOST
          value: "elasticsearch.elastic-system"
        - name: FLUENT_ELASTICSEARCH_PORT
          value: "9200"
        - name: FLUENT_ELASTICSEARCH_SCHEME
          value: "https"
        - name: FLUENT_ELASTICSEARCH_USER
          valueFrom:
            secretKeyRef:
              name: elasticsearch-credentials
              key: username
        - name: FLUENT_ELASTICSEARCH_PASSWORD
          valueFrom:
            secretKeyRef:
              name: elasticsearch-credentials
              key: password
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: dockercontainerlogdirectory
          mountPath: /var/lib/docker/containers
          readOnly: true
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: dockercontainerlogdirectory
        hostPath:
          path: /var/lib/docker/containers
```

## Disaster Recovery

### Backup Strategy

```bash
#!/bin/bash
# infrastructure/scripts/backup.sh

# Database backup
KUBECTL="kubectl"
NAMESPACE="claims-askes"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup PostgreSQL
$KUBECTL exec -n $NAMESPACE postgres-0 -- pg_dumpall -U postgres | \
  gzip > backup_postgres_${TIMESTAMP}.sql.gz

# Upload to S3
aws s3 cp backup_postgres_${TIMESTAMP}.sql.gz \
  s3://claims-askes-backups/postgres/${TIMESTAMP}/

# Backup persistent volumes
for pvc in $($KUBECTL get pvc -n $NAMESPACE -o jsonpath='{.items[*].metadata.name}'); do
  $KUBECTL exec -n $NAMESPACE backup-job -- tar czf - /data | \
    aws s3 cp - s3://claims-askes-backups/pvcs/${pvc}_${TIMESTAMP}.tar.gz
done

# Backup Kubernetes resources
$KUBECTL get all,cm,secret,ing -n $NAMESPACE -o yaml > \
  k8s_resources_${TIMESTAMP}.yaml

aws s3 cp k8s_resources_${TIMESTAMP}.yaml \
  s3://claims-askes-backups/k8s/${TIMESTAMP}/
```

### Recovery Procedures

```bash
#!/bin/bash
# infrastructure/scripts/restore.sh

TIMESTAMP=$1
NAMESPACE="claims-askes"

# Restore PostgreSQL
aws s3 cp s3://claims-askes-backups/postgres/${TIMESTAMP}/backup_postgres_${TIMESTAMP}.sql.gz - | \
  gunzip | \
  kubectl exec -i -n $NAMESPACE postgres-0 -- psql -U postgres

# Restore Kubernetes resources
aws s3 cp s3://claims-askes-backups/k8s/${TIMESTAMP}/k8s_resources_${TIMESTAMP}.yaml - | \
  kubectl apply -f -

# Verify restoration
kubectl get all -n $NAMESPACE
kubectl exec -n $NAMESPACE postgres-0 -- psql -U postgres -c "\\dt"
```

## Security

### Network Policies

```yaml
# infrastructure/kubernetes/base/network-policies/deny-all.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
---
# Allow specific traffic
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-claims-service
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
          app: web-bff
    - podSelector:
        matchLabels:
          app: mobile-bff
    ports:
    - protocol: TCP
      port: 8001
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
```

### Secret Management

```yaml
# Using Sealed Secrets
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: database-credentials
  namespace: claims-askes
spec:
  encryptedData:
    username: AgBvK8kN1...
    password: AgCdL9mP2...
  template:
    metadata:
      name: database-credentials
      namespace: claims-askes
    type: Opaque
```

## Cost Optimization

### Spot Instance Configuration

```yaml
# infrastructure/kubernetes/base/spot-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: spot-interrupt-handler
data:
  config.yaml: |
    nodeSelector:
      node.kubernetes.io/lifecycle: spot
    tolerations:
    - key: spot
      operator: Equal
      value: "true"
      effect: NoSchedule
    spotInstancePools: 4
    onDemandBaseCapacity: 2
    onDemandPercentageAboveBaseCapacity: 25
```

### Resource Quotas

```yaml
# infrastructure/kubernetes/base/resource-quota.yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
spec:
  hard:
    requests.cpu: "100"
    requests.memory: 200Gi
    limits.cpu: "200"
    limits.memory: 400Gi
    persistentvolumeclaims: "10"
    services.loadbalancers: "2"
```

## Operational Runbooks

### Service Deployment

```bash
# Deploy new version
./scripts/deploy.sh claims-service v2.0.0 production

# Rollback if needed
./scripts/rollback.sh claims-service production

# Check deployment status
kubectl rollout status deployment/claims-service -n claims-askes
```

### Scaling Operations

```bash
# Manual scaling
kubectl scale deployment claims-service --replicas=10 -n claims-askes

# Update HPA limits
kubectl patch hpa claims-service-hpa -n claims-askes \
  --patch '{"spec":{"maxReplicas":20}}'

# Scale node group
eksctl scale nodegroup --cluster=claims-askes-prod \
  --name=general --nodes-min=5 --nodes-max=15
```

## Troubleshooting

### Common Issues

1. **Pod CrashLoopBackOff**
```bash
# Check logs
kubectl logs -n claims-askes claims-service-xxx --previous

# Describe pod
kubectl describe pod -n claims-askes claims-service-xxx

# Check events
kubectl get events -n claims-askes --sort-by='.lastTimestamp'
```

2. **High Memory Usage**
```bash
# Check resource usage
kubectl top pods -n claims-askes

# Get memory limits
kubectl get pods -n claims-askes -o json | \
  jq '.items[] | {name: .metadata.name, memory: .spec.containers[].resources}'
```

3. **Network Issues**
```bash
# Test connectivity
kubectl exec -n claims-askes claims-service-xxx -- \
  curl -v http://member-service:8002/health

# Check network policies
kubectl get networkpolicy -n claims-askes
```

## Support

- **DevOps Team**: devops@claims-askes.com
- **On-call**: PagerDuty escalation
- **Documentation**: Internal wiki
- **Monitoring**: Grafana dashboards at grafana.claims-askes.com

## License

Proprietary - All rights reserved