# Admin Console

## Overview

The Admin Console is a comprehensive administrative web application for managing the health insurance platform. It provides system administrators, insurance administrators, and operations teams with tools to configure benefits, manage policies, monitor claims, and oversee the entire insurance ecosystem.

## Features

### Core Administrative Features
- 🔐 **User Management** - Manage system users, roles, and permissions
- 📊 **System Dashboard** - Real-time system metrics and KPIs
- 📋 **Policy Administration** - Create and manage insurance policies
- 💰 **Benefit Configuration** - Define and manage benefit plans
- 🏥 **Provider Management** - Onboard and manage healthcare providers
- 👥 **Member Management** - Manage member enrollments and coverage
- 📄 **Claims Administration** - Review and adjudicate claims
- 💸 **Financial Management** - Payment processing and reconciliation

### Advanced Features
- 📊 **Analytics & Reporting** - Comprehensive business intelligence
- 🔧 **System Configuration** - Platform settings and parameters
- 📧 **Communication Center** - Mass notifications and alerts
- 📅 **Audit Trail** - Complete system audit logging
- 🤖 **Rule Engine** - Configure business rules and workflows
- 📤 **Data Import/Export** - Bulk data operations
- 🌐 **Multi-tenant Support** - Manage multiple organizations
- 🔄 **Batch Processing** - Scheduled jobs and automation

## Technology Stack

- **Framework**: React 18.2+
- **Language**: TypeScript 5.0+
- **State Management**: Redux Toolkit + RTK Query
- **UI Library**: Ant Design Pro 5.0
- **Styling**: Less + CSS Modules
- **Build Tool**: Vite 5.0
- **Testing**: Jest + React Testing Library
- **E2E Testing**: Cypress
- **Code Quality**: ESLint + Prettier
- **Charts**: Apache ECharts
- **Forms**: Ant Design Form + Formik
- **Tables**: Ant Design Table with virtual scrolling

## Getting Started

### Prerequisites

- Node.js 18+ and npm 9+
- Admin credentials
- Access to backend APIs
- Modern web browser

### Installation

1. **Navigate to the project**
```bash
cd frontend/apps/admin-console
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Start development server**
```bash
npm run dev
```

The application will be available at `http://localhost:3002`

### Environment Variables

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:4000
VITE_WS_URL=ws://localhost:4000

# Feature Flags
VITE_ENABLE_MULTI_TENANT=true
VITE_ENABLE_RULE_ENGINE=true
VITE_ENABLE_BATCH_PROCESSING=true
VITE_ENABLE_ADVANCED_ANALYTICS=true

# External Services
VITE_AUDIT_SERVICE_URL=https://audit.claims-askes.com
VITE_NOTIFICATION_SERVICE_URL=https://notify.claims-askes.com

# Security
VITE_SESSION_TIMEOUT=1800000
VITE_MFA_ENABLED=true

# Analytics
VITE_GA_TRACKING_ID=UA-XXXXXXXXX
VITE_SENTRY_DSN=https://xxx@sentry.io/xxx
```

## Project Structure

```
admin-console/
├── public/
│   ├── assets/           # Static assets
│   └── locales/          # Translation files
├── src/
│   ├── app/              # App configuration
│   │   ├── App.tsx       # Root component
│   │   ├── store.ts      # Redux store
│   │   └── routes.tsx    # Route definitions
│   ├── features/         # Feature modules
│   │   ├── dashboard/    # System dashboard
│   │   ├── users/        # User management
│   │   ├── policies/     # Policy administration
│   │   ├── benefits/     # Benefit configuration
│   │   ├── providers/    # Provider management
│   │   ├── members/      # Member management
│   │   ├── claims/       # Claims administration
│   │   ├── finance/      # Financial management
│   │   ├── analytics/    # Analytics & reporting
│   │   ├── settings/     # System configuration
│   │   ├── audit/        # Audit trail
│   │   └── rules/        # Rule engine
│   ├── components/       # Shared components
│   │   ├── common/       # Generic components
│   │   ├── charts/       # Chart components
│   │   ├── tables/       # Advanced tables
│   │   └── layout/       # Layout components
│   ├── hooks/           # Custom hooks
│   ├── services/        # API services
│   ├── utils/           # Utility functions
│   ├── styles/          # Global styles
│   └── types/           # TypeScript types
├── tests/               # Test files
├── cypress/             # E2E tests
└── package.json
```

## Development

### Available Scripts

```bash
# Development
npm run dev           # Start dev server
npm run build        # Build for production
npm run preview      # Preview production build

# Testing
npm run test         # Run unit tests
npm run test:watch   # Run tests in watch mode
npm run test:coverage # Generate coverage report
npm run e2e          # Run E2E tests
npm run e2e:headless # Run E2E tests headless

# Code Quality
npm run lint         # Run ESLint
npm run lint:fix     # Fix ESLint issues
npm run format       # Format with Prettier
npm run type-check   # TypeScript type checking

# Analysis
npm run analyze      # Analyze bundle size
```

## Features Documentation

### User Management

```typescript
interface User {
  id: string;
  username: string;
  email: string;
  roles: Role[];
  permissions: Permission[];
  status: 'active' | 'inactive' | 'suspended';
  lastLogin: Date;
  mfaEnabled: boolean;
}

// Role-based access control
const rolePermissions = {
  SUPER_ADMIN: ['*'],
  ADMIN: ['users.*', 'policies.*', 'benefits.*'],
  OPERATOR: ['claims.view', 'claims.process', 'members.view'],
  ANALYST: ['analytics.*', 'reports.*'],
  AUDITOR: ['audit.*', 'reports.view']
};
```

### Policy Administration

1. **Create Policy**
   - Define policy details
   - Set coverage periods
   - Configure benefit plans
   - Assign pricing tiers

2. **Manage Enrollments**
   - Add/remove members
   - Update coverage levels
   - Handle life events
   - Process terminations

### Benefit Configuration

```typescript
interface BenefitPlan {
  id: string;
  name: string;
  code: string;
  benefits: Benefit[];
  coverageLimits: CoverageLimit[];
  costSharing: CostSharing;
  exclusions: string[];
  effectiveDate: Date;
  expirationDate: Date;
}

// Benefit configuration example
const configureBenefit = {
  benefitCode: 'CONS-SP',
  benefitName: 'Specialist Consultation',
  coverageType: 'per_incident',
  annualLimit: 10000000,
  incidentLimit: 1000000,
  coinsurance: 10,
  deductible: 0,
  requiresPreAuth: false,
  waitingPeriod: 0
};
```

### Claims Administration

#### Claims Dashboard
```typescript
const ClaimsDashboard = () => {
  const metrics = useClaimsMetrics();
  
  return (
    <Dashboard>
      <MetricCard title="Pending Claims" value={metrics.pending} />
      <MetricCard title="Processing Time" value={metrics.avgTime} />
      <MetricCard title="Approval Rate" value={metrics.approvalRate} />
      <MetricCard title="Total Value" value={metrics.totalValue} />
    </Dashboard>
  );
};
```

#### Manual Adjudication
```typescript
const adjudicateClaim = async (claimId: string, decision: Decision) => {
  await claimsService.adjudicate({
    claimId,
    decision: decision.status,
    approvedAmount: decision.amount,
    denialReason: decision.reason,
    notes: decision.notes,
    adjudicatorId: currentUser.id
  });
};
```

### Rule Engine

```typescript
interface BusinessRule {
  id: string;
  name: string;
  category: 'eligibility' | 'benefit' | 'authorization' | 'payment';
  condition: RuleCondition;
  action: RuleAction;
  priority: number;
  active: boolean;
}

// Rule configuration UI
const RuleBuilder = () => {
  return (
    <RuleEditor
      conditions={[
        { field: 'diagnosis', operator: 'equals', value: 'J06.9' },
        { field: 'amount', operator: 'greater_than', value: 1000000 }
      ]}
      actions={[
        { type: 'require_authorization' },
        { type: 'flag_for_review' }
      ]}
    />
  );
};
```

### Analytics & Reporting

```typescript
// Real-time analytics dashboard
const AnalyticsDashboard = () => {
  const { data: metrics } = useRealTimeMetrics();
  
  return (
    <Grid>
      <ClaimsVolumeChart data={metrics.claimsVolume} />
      <ProviderPerformance data={metrics.providerMetrics} />
      <MemberUtilization data={metrics.utilization} />
      <FinancialSummary data={metrics.financial} />
    </Grid>
  );
};

// Report generation
const generateReport = async (params: ReportParams) => {
  const report = await reportService.generate({
    type: params.type,
    dateRange: params.dateRange,
    filters: params.filters,
    format: 'xlsx' // pdf, csv, xlsx
  });
  
  downloadFile(report.url);
};
```

## State Management

### Redux Store Structure

```typescript
{
  auth: {
    user: AdminUser | null,
    permissions: string[],
    token: string | null,
    mfaVerified: boolean
  },
  system: {
    metrics: SystemMetrics,
    health: HealthStatus,
    notifications: SystemNotification[],
    jobs: BackgroundJob[]
  },
  policies: {
    list: Policy[],
    selected: Policy | null,
    filters: PolicyFilters
  },
  benefits: {
    plans: BenefitPlan[],
    rules: BenefitRule[],
    templates: BenefitTemplate[]
  },
  claims: {
    queue: Claim[],
    processing: Claim[],
    statistics: ClaimStatistics
  },
  audit: {
    logs: AuditLog[],
    filters: AuditFilters,
    retention: RetentionPolicy
  },
  ui: {
    theme: 'light' | 'dark',
    language: 'en' | 'id',
    sidebar: boolean,
    notifications: UINotification[]
  }
}
```

## API Integration

### Admin API Service

```typescript
// services/api/admin.service.ts
import { createApi } from '@reduxjs/toolkit/query/react';

export const adminApi = createApi({
  reducerPath: 'adminApi',
  baseQuery: fetchBaseQuery({
    baseUrl: VITE_API_BASE_URL,
    prepareHeaders: (headers) => {
      headers.set('authorization', `Bearer ${token}`);
      headers.set('x-admin-key', adminKey);
      return headers;
    }
  }),
  tagTypes: ['User', 'Policy', 'Benefit', 'Claim'],
  endpoints: (builder) => ({
    getSystemMetrics: builder.query<SystemMetrics, void>({
      query: () => '/admin/metrics',
      providesTags: ['System']
    }),
    updateBenefitPlan: builder.mutation<BenefitPlan, UpdateBenefitPlanDto>({
      query: (plan) => ({
        url: `/admin/benefits/${plan.id}`,
        method: 'PUT',
        body: plan
      }),
      invalidatesTags: ['Benefit']
    })
  })
});
```

## Security

### Authentication & Authorization

```typescript
// Multi-factor authentication
const authenticateAdmin = async (credentials: AdminCredentials) => {
  // Step 1: Username/password
  const { token, requiresMFA } = await authService.login(credentials);
  
  if (requiresMFA) {
    // Step 2: MFA verification
    const mfaCode = await promptMFACode();
    const { accessToken } = await authService.verifyMFA(token, mfaCode);
    return accessToken;
  }
  
  return token;
};

// Permission checking
const ProtectedRoute = ({ permission, children }) => {
  const hasPermission = usePermission(permission);
  
  if (!hasPermission) {
    return <AccessDenied />;
  }
  
  return children;
};
```

### Audit Logging

```typescript
// Automatic audit logging
const auditMiddleware = (action: any) => {
  if (AUDITABLE_ACTIONS.includes(action.type)) {
    auditService.log({
      action: action.type,
      user: currentUser.id,
      timestamp: new Date(),
      data: action.payload,
      ip: clientIP,
      userAgent: navigator.userAgent
    });
  }
};
```

## Testing

### Unit Testing

```typescript
// BenefitConfiguration.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { BenefitConfiguration } from './BenefitConfiguration';

describe('BenefitConfiguration', () => {
  it('validates benefit limits', () => {
    render(<BenefitConfiguration />);
    
    const annualLimitInput = screen.getByLabelText('Annual Limit');
    fireEvent.change(annualLimitInput, { target: { value: '-1000' } });
    
    expect(screen.getByText('Annual limit must be positive')).toBeInTheDocument();
  });
  
  it('calculates total coverage correctly', () => {
    const { getByTestId } = render(<BenefitConfiguration />);
    
    fireEvent.change(getByTestId('base-coverage'), { target: { value: '1000000' } });
    fireEvent.change(getByTestId('additional-coverage'), { target: { value: '500000' } });
    
    expect(getByTestId('total-coverage')).toHaveTextContent('1,500,000');
  });
});
```

### E2E Testing

```typescript
// cypress/e2e/admin-workflow.cy.ts
describe('Admin Workflow', () => {
  beforeEach(() => {
    cy.loginAsAdmin();
  });
  
  it('configures new benefit plan', () => {
    cy.visit('/benefits');
    cy.contains('Create Benefit Plan').click();
    
    cy.fillBenefitForm({
      name: 'Premium Plan 2024',
      code: 'PREM-2024',
      effectiveDate: '2024-01-01'
    });
    
    cy.addBenefitItems([
      { code: 'CONS-GP', limit: 'unlimited' },
      { code: 'CONS-SP', limit: '10000000' }
    ]);
    
    cy.contains('Save').click();
    cy.contains('Benefit plan created successfully').should('be.visible');
  });
});
```

## Performance Optimization

### Large Dataset Handling

```typescript
// Virtual scrolling for large tables
import { VirtualTable } from '@ant-design/pro-table';

const ClaimsTable = ({ claims }) => (
  <VirtualTable
    columns={columns}
    dataSource={claims}
    scroll={{ y: 600 }}
    pagination={{
      pageSize: 50,
      showSizeChanger: true
    }}
  />
);
```

### Dashboard Optimization

```typescript
// WebSocket for real-time updates
const useRealTimeMetrics = () => {
  useEffect(() => {
    const ws = new WebSocket(VITE_WS_URL);
    
    ws.on('metrics:update', (data) => {
      dispatch(updateMetrics(data));
    });
    
    return () => ws.close();
  }, []);
};
```

## Deployment

### Production Build

```bash
# Build with optimizations
npm run build:prod

# Analyze bundle
npm run analyze
```

### Docker Deployment

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY security-headers.conf /etc/nginx/conf.d/security-headers.conf
EXPOSE 80
```

## Monitoring

### System Health Dashboard

```typescript
const SystemHealth = () => {
  const health = useSystemHealth();
  
  return (
    <HealthDashboard>
      <ServiceStatus services={health.services} />
      <DatabaseMetrics metrics={health.database} />
      <QueueStatus queues={health.queues} />
      <ErrorRate rate={health.errorRate} />
    </HealthDashboard>
  );
};
```

### Performance Metrics

- Page load time < 2s
- API response time < 500ms
- Dashboard refresh rate: 5s
- Real-time updates latency < 100ms

## Troubleshooting

### Common Issues

1. **Session Timeout**
   - Configure VITE_SESSION_TIMEOUT
   - Implement session refresh
   - Add warning notifications

2. **Large Dataset Performance**
   - Enable pagination
   - Implement virtual scrolling
   - Use server-side filtering

3. **Real-time Updates Not Working**
   - Check WebSocket connection
   - Verify firewall settings
   - Check browser console for errors

## Support

- **Documentation**: [Full docs](../../../docs)
- **API Documentation**: [Admin API Reference](../../../services/admin-service/docs/API.md)
- **System Architecture**: [Architecture Guide](../../../MICROSERVICES_ARCHITECTURE.md)
- **Issues**: GitHub Issues
- **Team**: Platform Team - admin@claims-askes.com

## License

Proprietary - All rights reserved