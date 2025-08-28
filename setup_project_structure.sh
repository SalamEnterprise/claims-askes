#!/bin/bash

# Production-Grade Project Structure Setup Script
# Claims-Askes Health Insurance Platform

set -e

echo "🏗️ Setting up production project structure for Claims-Askes..."

# Create main directories
mkdir -p .github/workflows
mkdir -p backend/{services,api-gateway,integration,workers}
mkdir -p frontend/{apps,mobile,packages}
mkdir -p packages/{types,validators,constants,errors,models}
mkdir -p infrastructure/{terraform,kubernetes,docker,ansible}
mkdir -p database/{migrations,seeds,backups}
mkdir -p scripts/{setup,deployment,monitoring,maintenance}
mkdir -p tests/{unit,integration,e2e,load,security,fixtures}
mkdir -p docs/{api,architecture,guides,runbooks,compliance}
mkdir -p monitoring/{grafana,prometheus,alerts,logs}
mkdir -p security/{policies,certificates,secrets,scanning}
mkdir -p tools/{cli,generators,analyzers}

# Backend Services
services=(
    "claims-engine"
    "authorization"
    "adjudication"
    "payment"
    "member"
    "provider"
    "benefit"
    "policy"
    "eligibility"
    "accumulator"
    "document"
    "notification"
    "reporting"
    "audit"
    "fraud-detection"
)

for service in "${services[@]}"; do
    mkdir -p "backend/services/${service}"/{cmd/server,internal/{api,domain,infrastructure,application,config},pkg,migrations,docs,tests}
done

# API Gateway
mkdir -p backend/api-gateway/{kong,routes,middleware}

# Integration Services
integrations=(
    "fhir"
    "x12"
    "whatsapp"
    "payment-gateway"
    "sms-gateway"
    "email"
)

for integration in "${integrations[@]}"; do
    mkdir -p "backend/integration/${integration}"/{src,tests,docs}
done

# Workers
workers=(
    "claim-processor"
    "batch-processor"
    "report-generator"
    "data-sync"
)

for worker in "${workers[@]}"; do
    mkdir -p "backend/workers/${worker}"/{src,tests,docs}
done

# Frontend Applications
apps=(
    "member-portal"
    "provider-portal"
    "admin-console"
    "operations-dashboard"
    "broker-portal"
    "employer-portal"
)

for app in "${apps[@]}"; do
    mkdir -p "frontend/apps/${app}"/{public,src/{app,features,shared,layouts,styles},tests}
done

# Mobile Applications
mobile_apps=(
    "member-app"
    "provider-app"
    "field-agent-app"
)

for app in "${mobile_apps[@]}"; do
    mkdir -p "frontend/mobile/${app}"/{ios,android,src/{screens,components,services,navigation,utils}}
done

# Frontend Packages
frontend_packages=(
    "ui-components"
    "design-system"
    "utils"
    "api-client"
)

for package in "${frontend_packages[@]}"; do
    mkdir -p "frontend/packages/${package}"/{src,tests,docs}
done

# Infrastructure
mkdir -p infrastructure/terraform/environments/{dev,staging,production}
mkdir -p infrastructure/terraform/{modules,global}
mkdir -p infrastructure/kubernetes/{base,overlays,charts}
mkdir -p infrastructure/docker/{images,compose}
mkdir -p infrastructure/ansible/{playbooks,roles}

# Database
mkdir -p database/migrations/{postgres,mongodb,redis}

echo "✅ Directory structure created successfully!"
echo ""
echo "📝 Creating configuration files..."

# Create root configuration files
cat > package.json << 'EOF'
{
  "name": "@claims-askes/root",
  "version": "1.0.0",
  "private": true,
  "description": "Health Insurance Claims Processing Platform",
  "workspaces": [
    "backend/services/*",
    "frontend/apps/*",
    "frontend/mobile/*",
    "frontend/packages/*",
    "packages/*"
  ],
  "scripts": {
    "dev": "nx run-many --target=serve --all",
    "build": "nx run-many --target=build --all",
    "test": "nx run-many --target=test --all",
    "lint": "nx run-many --target=lint --all",
    "format": "prettier --write .",
    "prepare": "husky install"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "nx": "^16.0.0",
    "typescript": "^5.0.0",
    "prettier": "^3.0.0",
    "eslint": "^8.0.0",
    "husky": "^8.0.0",
    "lint-staged": "^14.0.0"
  },
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=9.0.0"
  }
}
EOF

# Create nx.json for monorepo management
cat > nx.json << 'EOF'
{
  "$schema": "./node_modules/nx/schemas/nx-schema.json",
  "npmScope": "@claims-askes",
  "affected": {
    "defaultBase": "main"
  },
  "tasksRunnerOptions": {
    "default": {
      "runner": "nx/tasks-runners/default",
      "options": {
        "cacheableOperations": ["build", "lint", "test", "e2e"]
      }
    }
  },
  "targetDefaults": {
    "build": {
      "dependsOn": ["^build"]
    }
  },
  "generators": {
    "@nx/react": {
      "application": {
        "style": "css",
        "linter": "eslint",
        "bundler": "vite",
        "strict": true,
        "unitTestRunner": "jest"
      }
    }
  }
}
EOF

# Create TypeScript config
cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "lib": ["ES2022"],
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "baseUrl": ".",
    "paths": {
      "@claims-askes/*": ["packages/*/src"],
      "@backend/*": ["backend/*/src"],
      "@frontend/*": ["frontend/*/src"]
    }
  },
  "exclude": ["node_modules", "dist", "build", "coverage"]
}
EOF

# Create Docker Compose for local development
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: claims_askes
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # Redis Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  # MongoDB
  mongodb:
    image: mongo:6
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: admin123
    volumes:
      - mongo_data:/data/db

  # Elasticsearch
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elastic_data:/usr/share/elasticsearch/data

  # Kafka
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
    ports:
      - "2181:2181"

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1

volumes:
  postgres_data:
  mongo_data:
  elastic_data:
EOF

# Create Makefile
cat > Makefile << 'EOF'
.PHONY: help install dev build test deploy clean

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make dev        - Start development environment"
	@echo "  make build      - Build all services"
	@echo "  make test       - Run all tests"
	@echo "  make deploy     - Deploy to Kubernetes"
	@echo "  make clean      - Clean build artifacts"

install:
	npm install
	cd backend && go mod download

dev:
	docker-compose up -d
	npm run dev

build:
	npm run build
	docker build -t claims-askes/api-gateway ./backend/api-gateway

test:
	npm run test
	cd backend && go test ./...

deploy:
	kubectl apply -k infrastructure/kubernetes/overlays/production

clean:
	rm -rf node_modules
	rm -rf dist
	rm -rf build
	docker-compose down -v
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
# Dependencies
node_modules/
vendor/

# Build outputs
dist/
build/
out/
*.out
*.exe

# Environment files
.env
.env.*
!.env.example

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# Logs
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Testing
coverage/
.nyc_output/

# Cache
.cache/
.parcel-cache/
.next/
.nuxt/

# Temporary files
tmp/
temp/
*.tmp

# Security
*.pem
*.key
*.crt
secrets/

# Database
*.db
*.sqlite
*.sqlite3

# Docker
.docker/
EOF

# Create GitHub Actions workflow
mkdir -p .github/workflows
cat > .github/workflows/ci.yml << 'EOF'
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm ci
      - run: npm run lint

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - uses: actions/setup-go@v4
        with:
          go-version: 1.21
      - run: npm ci
      - run: npm run test
      - run: cd backend && go test ./...

  build:
    runs-on: ubuntu-latest
    needs: [lint, test]
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm ci
      - run: npm run build

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'repo'
          scan-ref: '.'
EOF

echo "✅ Configuration files created successfully!"
echo ""
echo "🚀 Project structure setup complete!"
echo ""
echo "Next steps:"
echo "1. Run 'chmod +x setup_project_structure.sh' to make this script executable"
echo "2. Run './setup_project_structure.sh' to create the structure"
echo "3. Run 'npm install' to install dependencies"
echo "4. Run 'docker-compose up -d' to start local development environment"
echo "5. Start developing your microservices and applications!"