#!/bin/bash

# Microservices Architecture Setup
# Claims-Askes Health Insurance Platform
# Pattern: Database per Service with Schema Separation

set -e

echo "🏗️ Creating Microservices Architecture..."
echo "Pattern: Database per Service with Schema Separation"
echo ""

# ================== BACKEND MICROSERVICES ==================
echo "📦 Creating Backend Microservices..."

# Core microservices
services=(
    "claims-service"
    "authorization-service"
    "adjudication-service"
    "payment-service"
    "member-service"
    "provider-service"
    "benefit-service"
    "policy-service"
    "notification-service"
    "document-service"
)

for service in "${services[@]}"; do
    echo "  Creating ${service}..."
    
    # Source code structure
    mkdir -p "services/${service}/src/api/v1/endpoints"
    mkdir -p "services/${service}/src/api/v1/middlewares"
    mkdir -p "services/${service}/src/models"
    mkdir -p "services/${service}/src/schemas"
    mkdir -p "services/${service}/src/services"
    mkdir -p "services/${service}/src/repositories"
    mkdir -p "services/${service}/src/events/publishers"
    mkdir -p "services/${service}/src/events/consumers"
    mkdir -p "services/${service}/src/utils"
    mkdir -p "services/${service}/src/config"
    
    # Tests
    mkdir -p "services/${service}/tests/unit"
    mkdir -p "services/${service}/tests/integration"
    mkdir -p "services/${service}/tests/fixtures"
    
    # Database migrations (Alembic)
    mkdir -p "services/${service}/migrations/versions"
    
    # Configuration
    mkdir -p "services/${service}/config"
    
    # Documentation
    mkdir -p "services/${service}/docs"
done

# ================== BFF LAYER ==================
echo "🌐 Creating BFF (Backend for Frontend) Layer..."

# Web BFF
mkdir -p bff/web-bff/src/api
mkdir -p bff/web-bff/src/aggregators
mkdir -p bff/web-bff/src/transformers
mkdir -p bff/web-bff/src/cache
mkdir -p bff/web-bff/src/config
mkdir -p bff/web-bff/tests

# Mobile BFF
mkdir -p bff/mobile-bff/src/api
mkdir -p bff/mobile-bff/src/aggregators
mkdir -p bff/mobile-bff/src/transformers
mkdir -p bff/mobile-bff/src/cache
mkdir -p bff/mobile-bff/src/config
mkdir -p bff/mobile-bff/tests

# ================== WEB APPLICATIONS ==================
echo "🎨 Creating Web Applications..."

web_apps=(
    "member-portal"
    "provider-portal"
    "admin-console"
    "operations-dashboard"
    "broker-portal"
)

for app in "${web_apps[@]}"; do
    echo "  Creating ${app}..."
    
    mkdir -p "web/${app}/public/assets"
    mkdir -p "web/${app}/src/components/common"
    mkdir -p "web/${app}/src/components/features"
    mkdir -p "web/${app}/src/pages"
    mkdir -p "web/${app}/src/hooks"
    mkdir -p "web/${app}/src/services"
    mkdir -p "web/${app}/src/store/slices"
    mkdir -p "web/${app}/src/utils"
    mkdir -p "web/${app}/src/styles"
    mkdir -p "web/${app}/src/types"
    mkdir -p "web/${app}/src/config"
    mkdir -p "web/${app}/tests"
done

# ================== MOBILE APPLICATIONS ==================
echo "📱 Creating Mobile Applications..."

mobile_apps=(
    "member-mobile"
    "provider-mobile"
    "field-agent-mobile"
)

for app in "${mobile_apps[@]}"; do
    echo "  Creating ${app}..."
    
    mkdir -p "mobile/${app}/src/screens"
    mkdir -p "mobile/${app}/src/components"
    mkdir -p "mobile/${app}/src/navigation"
    mkdir -p "mobile/${app}/src/services"
    mkdir -p "mobile/${app}/src/store"
    mkdir -p "mobile/${app}/src/utils"
    mkdir -p "mobile/${app}/src/assets"
    mkdir -p "mobile/${app}/src/types"
    mkdir -p "mobile/${app}/ios"
    mkdir -p "mobile/${app}/android"
    mkdir -p "mobile/${app}/tests"
done

# ================== API GATEWAY ==================
echo "🚪 Creating API Gateway..."

mkdir -p gateway/src/routes
mkdir -p gateway/src/middleware
mkdir -p gateway/src/config
mkdir -p gateway/nginx
mkdir -p gateway/kong

# ================== SHARED LIBRARIES ==================
echo "📚 Creating Shared Libraries..."

# Python libraries
mkdir -p libraries/python/claims-common/src
mkdir -p libraries/python/claims-common/tests
mkdir -p libraries/python/claims-auth/src
mkdir -p libraries/python/claims-auth/tests
mkdir -p libraries/python/claims-events/src
mkdir -p libraries/python/claims-events/tests

# JavaScript libraries
mkdir -p libraries/javascript/ui-components/src
mkdir -p libraries/javascript/ui-components/tests
mkdir -p libraries/javascript/api-client/src
mkdir -p libraries/javascript/api-client/tests
mkdir -p libraries/javascript/mobile-components/src
mkdir -p libraries/javascript/mobile-components/tests

# ================== DATABASE ==================
echo "💾 Creating Database Structure..."

mkdir -p database/schemas
mkdir -p database/migrations/common
mkdir -p database/seeds
mkdir -p database/functions
mkdir -p database/views
mkdir -p database/scripts

# ================== INFRASTRUCTURE ==================
echo "🔧 Creating Infrastructure..."

mkdir -p infrastructure/docker
mkdir -p infrastructure/docker-compose
mkdir -p infrastructure/kubernetes
mkdir -p infrastructure/scripts

# ================== DOCUMENTATION ==================
echo "📚 Creating Documentation..."

mkdir -p docs/architecture
mkdir -p docs/api
mkdir -p docs/guides
mkdir -p docs/services

# ================== ROOT CONFIGURATION FILES ==================
echo "📄 Creating root configuration files..."

# Root .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv
*.egg-info/
dist/
build/

# JavaScript
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# Environment
.env
.env.*
!.env.example

# Database
*.db
*.sqlite3

# Logs
logs/
*.log

# Testing
.coverage
htmlcov/
.pytest_cache/
coverage/

# Docker
.docker/
EOF

# Root README
cat > README.md << 'EOF'
# Claims-Askes Microservices Platform

## Architecture Overview
Production-grade health insurance claims processing system using microservices architecture.

## Project Structure
```
.
├── services/           # Backend microservices
├── bff/               # Backend for Frontend layers
├── web/               # Web applications
├── mobile/            # Mobile applications
├── gateway/           # API Gateway
├── libraries/         # Shared libraries
├── database/          # Database schemas and migrations
├── infrastructure/    # Docker and deployment configs
└── docs/             # Documentation
```

## Services

### Core Services
- **claims-service**: Claims processing and management
- **authorization-service**: Pre-authorization and approvals
- **adjudication-service**: Claims adjudication and rule engine
- **payment-service**: Payment processing and EOB
- **member-service**: Member management and eligibility
- **provider-service**: Provider network management
- **benefit-service**: Benefit configuration
- **policy-service**: Policy administration
- **notification-service**: Notifications and alerts
- **document-service**: Document management

### BFF Layer
- **web-bff**: Aggregates APIs for web applications
- **mobile-bff**: Optimizes APIs for mobile applications

### Applications
- **Web**: Member Portal, Provider Portal, Admin Console
- **Mobile**: Member App, Provider App, Field Agent App

## Database Architecture
Single PostgreSQL instance with schema separation:
- Each service owns its schema
- No cross-schema direct access
- Service communication via APIs only

## Quick Start
1. Run `./create_microservices_structure.sh`
2. Run `docker-compose up -d`
3. Initialize database: `./database/scripts/init.sh`
4. Start services: `./infrastructure/scripts/start-all.sh`

## Development
See `/docs/guides/development.md` for detailed setup instructions.
EOF

echo ""
echo "✅ Microservices structure created successfully!"
echo ""
echo "📋 Structure Summary:"
echo "  - 10 independent microservices"
echo "  - 2 BFF layers (web and mobile)"
echo "  - 5 web applications"
echo "  - 3 mobile applications"
echo "  - Shared libraries for Python and JavaScript"
echo "  - Database with schema separation"
echo ""
echo "🚀 Next Steps:"
echo "  1. Run: chmod +x create_microservices_structure.sh"
echo "  2. Run: ./create_microservices_structure.sh"
echo "  3. Initialize database schemas"
echo "  4. Set up Docker environment"
echo "  5. Start developing services independently"