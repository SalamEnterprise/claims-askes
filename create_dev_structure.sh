#!/bin/bash

# Development-Focused Project Structure
# Claims-Askes Health Insurance Platform
# Focus: Core application development without DevOps complexity

set -e

echo "🏗️ Creating Development Project Structure..."
echo "Focus: Core application architecture"
echo ""

# ================== BACKEND MICROSERVICES ==================
echo "📦 Creating Backend Services..."

# Core business services
services=(
    "claims"
    "authorization"
    "adjudication"
    "payment"
    "member"
    "provider"
    "benefit"
    "policy"
)

for service in "${services[@]}"; do
    # Service structure following DDD principles
    mkdir -p "backend/${service}/app/api/v1"
    mkdir -p "backend/${service}/app/core"
    mkdir -p "backend/${service}/app/models"
    mkdir -p "backend/${service}/app/schemas"
    mkdir -p "backend/${service}/app/services"
    mkdir -p "backend/${service}/app/repositories"
    mkdir -p "backend/${service}/app/utils"
    
    # Database migrations
    mkdir -p "backend/${service}/migrations/versions"
    
    # Tests
    mkdir -p "backend/${service}/tests/unit"
    mkdir -p "backend/${service}/tests/integration"
    
    # Configuration
    mkdir -p "backend/${service}/config"
    
    # Documentation
    mkdir -p "backend/${service}/docs"
done

# API Gateway (Simple)
echo "🌐 Creating API Gateway..."
mkdir -p backend/gateway/app/routers
mkdir -p backend/gateway/app/middleware
mkdir -p backend/gateway/app/auth
mkdir -p backend/gateway/config

# Shared Backend Code
echo "📚 Creating Shared Libraries..."
mkdir -p backend/shared/models
mkdir -p backend/shared/schemas
mkdir -p backend/shared/database
mkdir -p backend/shared/utils
mkdir -p backend/shared/auth
mkdir -p backend/shared/validators
mkdir -p backend/shared/exceptions

# Background Jobs
echo "⚙️ Creating Background Jobs..."
mkdir -p backend/workers/tasks
mkdir -p backend/workers/schedulers
mkdir -p backend/workers/handlers

# External Integrations
echo "🔌 Creating Integration Adapters..."
mkdir -p backend/integrations/fhir
mkdir -p backend/integrations/x12
mkdir -p backend/integrations/whatsapp
mkdir -p backend/integrations/email

# ================== DATABASE ==================
echo "💾 Creating Database Structure..."

# PostgreSQL Schema Organization
mkdir -p database/schemas
mkdir -p database/migrations
mkdir -p database/seeds
mkdir -p database/functions
mkdir -p database/procedures
mkdir -p database/triggers
mkdir -p database/views
mkdir -p database/indexes

# Database Documentation
mkdir -p database/docs

# ================== FRONTEND APPLICATIONS ==================
echo "🎨 Creating Frontend Applications..."

# Web Applications
web_apps=(
    "member-portal"
    "provider-portal"
    "admin-dashboard"
    "operations-center"
)

for app in "${web_apps[@]}"; do
    mkdir -p "frontend/web/${app}/public"
    mkdir -p "frontend/web/${app}/src/components"
    mkdir -p "frontend/web/${app}/src/pages"
    mkdir -p "frontend/web/${app}/src/features"
    mkdir -p "frontend/web/${app}/src/hooks"
    mkdir -p "frontend/web/${app}/src/services"
    mkdir -p "frontend/web/${app}/src/store"
    mkdir -p "frontend/web/${app}/src/utils"
    mkdir -p "frontend/web/${app}/src/styles"
    mkdir -p "frontend/web/${app}/src/types"
    mkdir -p "frontend/web/${app}/tests"
done

# Mobile Applications
mobile_apps=(
    "member-app"
    "provider-app"
)

for app in "${mobile_apps[@]}"; do
    mkdir -p "frontend/mobile/${app}/src/screens"
    mkdir -p "frontend/mobile/${app}/src/components"
    mkdir -p "frontend/mobile/${app}/src/navigation"
    mkdir -p "frontend/mobile/${app}/src/services"
    mkdir -p "frontend/mobile/${app}/src/store"
    mkdir -p "frontend/mobile/${app}/src/utils"
    mkdir -p "frontend/mobile/${app}/ios"
    mkdir -p "frontend/mobile/${app}/android"
done

# Shared Frontend Components
mkdir -p frontend/shared/components
mkdir -p frontend/shared/hooks
mkdir -p frontend/shared/utils
mkdir -p frontend/shared/api

# ================== CONFIGURATION ==================
echo "⚙️ Creating Configuration..."

mkdir -p config/development
mkdir -p config/testing
mkdir -p config/production

# ================== DOCUMENTATION ==================
echo "📚 Creating Documentation..."

mkdir -p docs/api
mkdir -p docs/architecture
mkdir -p docs/business-rules
mkdir -p docs/database
mkdir -p docs/setup
mkdir -p docs/user-guides

# ================== TESTING ==================
echo "🧪 Creating Testing Structure..."

mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p tests/e2e
mkdir -p tests/fixtures
mkdir -p tests/mocks

# ================== SCRIPTS ==================
echo "📜 Creating Development Scripts..."

mkdir -p scripts/setup
mkdir -p scripts/database
mkdir -p scripts/data-import
mkdir -p scripts/development

# ================== ROOT FILES ==================
echo "📄 Creating root configuration files..."

# Python project configuration
cat > pyproject.toml << 'EOF'
[tool.poetry]
name = "claims-askes"
version = "1.0.0"
description = "Health Insurance Claims Processing System"
authors = ["Your Team"]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"
sqlalchemy = "^2.0.23"
alembic = "^1.12.0"
pydantic = "^2.5.0"
asyncpg = "^0.29.0"
redis = "^5.0.0"
celery = "^5.3.0"
httpx = "^0.25.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
black = "^23.0.0"
ruff = "^0.1.0"
mypy = "^1.7.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
EOF

# Docker Compose for local development
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: claims_dev
      POSTGRES_USER: claims_user
      POSTGRES_PASSWORD: claims_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  mailhog:
    image: mailhog/mailhog
    ports:
      - "1025:1025"
      - "8025:8025"

volumes:
  postgres_data:
EOF

# Environment template
cat > .env.example << 'EOF'
# Database
DATABASE_URL=postgresql+asyncpg://claims_user:claims_pass@localhost:5432/claims_dev

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

# Application
DEBUG=True
ENVIRONMENT=development
LOG_LEVEL=INFO

# External Services
FHIR_SERVER_URL=
X12_GATEWAY_URL=
SMS_API_KEY=
EMAIL_SMTP_HOST=localhost
EMAIL_SMTP_PORT=1025
EOF

# Makefile for common tasks
cat > Makefile << 'EOF'
.PHONY: help install dev test clean

help:
	@echo "Available commands:"
	@echo "  install    - Install dependencies"
	@echo "  dev        - Start development environment"
	@echo "  test       - Run tests"
	@echo "  migrate    - Run database migrations"
	@echo "  clean      - Clean up generated files"

install:
	poetry install

dev:
	docker-compose up -d
	poetry run uvicorn backend.gateway.app.main:app --reload

test:
	poetry run pytest

migrate:
	poetry run alembic upgrade head

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
EOF

# README
cat > README.md << 'EOF'
# Claims-Askes Health Insurance Platform

## Overview
Production-grade health insurance claims processing system for the Indonesian market.

## Technology Stack
- **Backend**: Python 3.11, FastAPI, SQLAlchemy
- **Database**: PostgreSQL, Redis
- **Frontend**: React, React Native
- **Message Queue**: Celery, Redis

## Project Structure
```
.
├── backend/           # Microservices
│   ├── claims/       # Claims processing service
│   ├── authorization/# Pre-authorization service
│   ├── adjudication/ # Claims adjudication
│   ├── payment/      # Payment processing
│   ├── member/       # Member management
│   ├── provider/     # Provider network
│   ├── benefit/      # Benefit configuration
│   └── policy/       # Policy administration
├── frontend/         # Client applications
│   ├── web/         # Web portals
│   └── mobile/      # Mobile apps
├── database/        # Database schemas and migrations
├── docs/           # Documentation
└── tests/          # Test suites
```

## Quick Start
1. Install dependencies: `make install`
2. Start services: `make dev`
3. Run migrations: `make migrate`
4. Run tests: `make test`

## Development
See `docs/setup/` for detailed setup instructions.
EOF

echo ""
echo "✅ Development structure created successfully!"
echo ""
echo "📋 Structure Summary:"
echo "  - 8 Python microservices with DDD architecture"
echo "  - 4 web applications + 2 mobile apps"
echo "  - PostgreSQL database with proper schema organization"
echo "  - Shared libraries and utilities"
echo "  - Development-focused configuration"
echo ""
echo "🚀 Next Steps:"
echo "  1. Run: chmod +x create_dev_structure.sh"
echo "  2. Run: ./create_dev_structure.sh"
echo "  3. Copy .env.example to .env and configure"
echo "  4. Run: make install"
echo "  5. Run: make dev"
echo ""
echo "Focus on building core business logic first!"