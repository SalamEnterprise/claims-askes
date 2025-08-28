# Claims-Askes Production Project Structure

## Overview
Production-grade monorepo structure for enterprise health insurance platform with microservices backend, multiple frontend applications, and comprehensive DevOps infrastructure.

```
claims-askes/
├── .github/                          # GitHub configuration
│   ├── workflows/                    # CI/CD pipelines
│   ├── CODEOWNERS                   # Code ownership
│   └── SECURITY.md                  # Security policies
│
├── backend/                          # Backend services (microservices)
│   ├── services/                     # Core microservices
│   │   ├── claims-engine/           # Claims processing service
│   │   ├── authorization/           # Pre-authorization service
│   │   ├── adjudication/           # Claims adjudication service
│   │   ├── payment/                # Payment processing service
│   │   ├── member/                 # Member management service
│   │   ├── provider/               # Provider network service
│   │   ├── benefit/                # Benefit configuration service
│   │   ├── policy/                 # Policy management service
│   │   ├── eligibility/            # Eligibility verification service
│   │   ├── accumulator/            # Accumulator tracking service
│   │   ├── document/               # Document management service
│   │   ├── notification/           # Notification service
│   │   ├── reporting/              # Reporting & analytics service
│   │   ├── audit/                  # Audit logging service
│   │   └── fraud-detection/        # AI/ML fraud detection service
│   │
│   ├── api-gateway/                 # API Gateway
│   │   ├── kong/                    # Kong configuration
│   │   ├── routes/                  # API routes
│   │   └── middleware/              # Custom middleware
│   │
│   ├── integration/                 # External integrations
│   │   ├── fhir/                   # FHIR R4 adapter
│   │   ├── x12/                    # EDI X12 adapter
│   │   ├── whatsapp/               # WhatsApp Business API
│   │   ├── payment-gateway/        # Payment gateway integrations
│   │   ├── sms-gateway/            # SMS gateway
│   │   └── email/                  # Email service integration
│   │
│   └── workers/                     # Background job workers
│       ├── claim-processor/        # Async claim processing
│       ├── batch-processor/        # Batch job processing
│       ├── report-generator/       # Scheduled reports
│       └── data-sync/              # Data synchronization
│
├── frontend/                         # Frontend applications
│   ├── apps/                        # Main applications
│   │   ├── member-portal/          # Member web portal
│   │   ├── provider-portal/        # Provider web portal
│   │   ├── admin-console/          # Insurance admin console
│   │   ├── operations-dashboard/   # Claims operations dashboard
│   │   ├── broker-portal/          # Broker/agent portal
│   │   └── employer-portal/        # Employer/HR portal
│   │
│   ├── mobile/                      # Mobile applications
│   │   ├── member-app/             # Member mobile app
│   │   │   ├── ios/               # iOS native code
│   │   │   ├── android/           # Android native code
│   │   │   └── src/               # React Native code
│   │   │
│   │   ├── provider-app/           # Provider mobile app
│   │   │   ├── ios/
│   │   │   ├── android/
│   │   │   └── src/
│   │   │
│   │   └── field-agent-app/        # Field agent mobile app
│   │       ├── ios/
│   │       ├── android/
│   │       └── src/
│   │
│   └── packages/                    # Shared frontend packages
│       ├── ui-components/          # Shared UI component library
│       ├── design-system/          # Design tokens and theme
│       ├── utils/                  # Shared utilities
│       └── api-client/             # API client library
│
├── packages/                         # Shared packages (backend & frontend)
│   ├── types/                       # TypeScript type definitions
│   ├── validators/                  # Shared validation logic
│   ├── constants/                   # Shared constants
│   ├── errors/                      # Error definitions
│   └── models/                      # Shared data models
│
├── infrastructure/                   # Infrastructure as Code
│   ├── terraform/                   # Terraform configurations
│   │   ├── environments/           # Environment-specific configs
│   │   │   ├── dev/
│   │   │   ├── staging/
│   │   │   └── production/
│   │   ├── modules/                # Reusable Terraform modules
│   │   └── global/                 # Global resources
│   │
│   ├── kubernetes/                  # Kubernetes manifests
│   │   ├── base/                   # Base configurations
│   │   ├── overlays/               # Environment overlays
│   │   └── charts/                 # Helm charts
│   │
│   ├── docker/                      # Docker configurations
│   │   ├── images/                 # Dockerfile definitions
│   │   └── compose/                # Docker compose files
│   │
│   └── ansible/                     # Ansible playbooks
│       ├── playbooks/
│       └── roles/
│
├── database/                         # Database management
│   ├── migrations/                  # Database migrations
│   │   ├── postgres/               # PostgreSQL migrations
│   │   ├── mongodb/                # MongoDB migrations
│   │   └── redis/                  # Redis configurations
│   │
│   ├── seeds/                       # Seed data
│   └── backups/                     # Backup scripts
│
├── scripts/                          # Utility scripts
│   ├── setup/                       # Setup scripts
│   ├── deployment/                  # Deployment scripts
│   ├── monitoring/                  # Monitoring scripts
│   └── maintenance/                 # Maintenance scripts
│
├── tests/                           # Test suites
│   ├── unit/                       # Unit tests
│   ├── integration/                # Integration tests
│   ├── e2e/                        # End-to-end tests
│   ├── load/                       # Load testing
│   ├── security/                   # Security testing
│   └── fixtures/                   # Test fixtures
│
├── docs/                            # Documentation
│   ├── api/                        # API documentation
│   ├── architecture/               # Architecture decisions
│   ├── guides/                     # User guides
│   ├── runbooks/                   # Operational runbooks
│   └── compliance/                 # Compliance documentation
│
├── monitoring/                      # Monitoring & Observability
│   ├── grafana/                    # Grafana dashboards
│   ├── prometheus/                 # Prometheus configs
│   ├── alerts/                     # Alert rules
│   └── logs/                       # Log aggregation configs
│
├── security/                        # Security configurations
│   ├── policies/                   # Security policies
│   ├── certificates/               # SSL certificates
│   ├── secrets/                    # Secret management
│   └── scanning/                   # Security scanning configs
│
├── tools/                           # Development tools
│   ├── cli/                        # CLI tools
│   ├── generators/                 # Code generators
│   └── analyzers/                  # Code analyzers
│
├── .devcontainer/                   # Dev container configuration
├── .vscode/                         # VS Code workspace settings
├── .idea/                          # IntelliJ IDEA settings
│
├── docker-compose.yml               # Local development
├── Makefile                        # Build automation
├── nx.json                         # Nx monorepo configuration
├── package.json                    # Root package.json
├── tsconfig.json                   # TypeScript configuration
├── .eslintrc.js                   # ESLint configuration
├── .prettierrc                    # Prettier configuration
├── .gitignore                     # Git ignore rules
├── .env.example                   # Environment variables example
├── LICENSE                        # License file
└── README.md                      # Project documentation
```

## Detailed Service Structure

### Backend Service Template
Each microservice follows this structure:

```
services/claims-engine/
├── cmd/                           # Application entrypoints
│   └── server/
│       └── main.go               # Main application
│
├── internal/                      # Private application code
│   ├── api/                      # API layer
│   │   ├── grpc/                # gRPC handlers
│   │   ├── rest/                # REST handlers
│   │   └── graphql/             # GraphQL resolvers
│   │
│   ├── domain/                   # Domain logic
│   │   ├── entities/            # Domain entities
│   │   ├── repositories/        # Repository interfaces
│   │   ├── services/            # Domain services
│   │   └── events/              # Domain events
│   │
│   ├── infrastructure/           # Infrastructure layer
│   │   ├── database/            # Database implementation
│   │   ├── messaging/           # Message queue implementation
│   │   ├── cache/               # Cache implementation
│   │   └── external/            # External service clients
│   │
│   ├── application/              # Application services
│   │   ├── commands/            # Command handlers
│   │   ├── queries/             # Query handlers
│   │   └── events/              # Event handlers
│   │
│   └── config/                   # Configuration
│       └── config.go            # Configuration struct
│
├── pkg/                          # Public packages
│   ├── errors/                  # Error types
│   └── models/                  # Data models
│
├── migrations/                   # Service-specific migrations
├── docs/                        # Service documentation
├── tests/                       # Service tests
├── Dockerfile                   # Docker image
├── Makefile                     # Service-specific commands
├── go.mod                       # Go modules
└── README.md                    # Service documentation
```

### Frontend Application Template
Each frontend application follows this structure:

```
apps/member-portal/
├── public/                       # Static assets
│   ├── images/
│   ├── fonts/
│   └── locales/                # i18n translations
│
├── src/
│   ├── app/                    # Application setup
│   │   ├── App.tsx
│   │   ├── routes.tsx
│   │   └── store.ts
│   │
│   ├── features/                # Feature modules
│   │   ├── claims/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── services/
│   │   │   ├── store/
│   │   │   └── types/
│   │   │
│   │   ├── coverage/
│   │   ├── providers/
│   │   └── profile/
│   │
│   ├── shared/                  # Shared resources
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── utils/
│   │   └── types/
│   │
│   ├── layouts/                 # Layout components
│   │   ├── MainLayout.tsx
│   │   └── AuthLayout.tsx
│   │
│   ├── styles/                  # Global styles
│   │   ├── global.css
│   │   └── variables.css
│   │
│   └── index.tsx               # Application entry
│
├── tests/                       # Application tests
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── .env.example                # Environment variables
├── Dockerfile                  # Docker image
├── nginx.conf                  # Nginx configuration
├── package.json               # Dependencies
├── tsconfig.json              # TypeScript config
├── vite.config.ts             # Vite configuration
└── README.md                  # Application documentation
```

## Technology Stack

### Backend
- **Languages**: Go (primary), Python (ML/AI), Node.js (specific services)
- **Frameworks**: Gin/Echo (Go), FastAPI (Python), NestJS (Node.js)
- **Databases**: PostgreSQL (primary), MongoDB (documents), Redis (cache)
- **Message Queue**: Apache Kafka, RabbitMQ
- **API**: REST, GraphQL, gRPC
- **Search**: Elasticsearch

### Frontend
- **Web Framework**: React 18 with TypeScript
- **Mobile**: React Native
- **State Management**: Redux Toolkit, Zustand
- **UI Libraries**: Ant Design, Material-UI
- **Build Tools**: Vite, Webpack
- **Testing**: Jest, React Testing Library, Cypress

### Infrastructure
- **Container**: Docker, Kubernetes
- **CI/CD**: GitHub Actions, ArgoCD
- **Cloud**: AWS/GCP/Azure
- **Monitoring**: Prometheus, Grafana, ELK Stack
- **Service Mesh**: Istio
- **API Gateway**: Kong

## Development Workflow

### Branch Strategy
```
main (production)
├── develop
│   ├── feature/JIRA-123-feature-name
│   ├── bugfix/JIRA-456-bug-description
│   └── hotfix/JIRA-789-critical-fix
└── release/v1.2.0
```

### Commit Convention
```
type(scope): subject

feat(claims): add bulk claim processing
fix(auth): resolve token expiration issue
docs(api): update API documentation
chore(deps): upgrade dependencies
```

### Environment Strategy
- **Local**: Docker Compose
- **Development**: Kubernetes (dev cluster)
- **Staging**: Production-like environment
- **Production**: Multi-region deployment

## Security Considerations

### Authentication & Authorization
- OAuth 2.0 / OIDC
- JWT tokens
- Role-Based Access Control (RBAC)
- Multi-Factor Authentication (MFA)

### Data Protection
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- PII data masking
- Audit logging

### Compliance
- HIPAA compliance
- PCI-DSS for payments
- GDPR/CCPA for privacy
- OJK regulations (Indonesia)