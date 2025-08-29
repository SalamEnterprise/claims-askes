# Provider Portal

## Overview

The Provider Portal is a comprehensive web application designed for healthcare providers to manage insurance claims, verify member eligibility, request pre-authorizations, and handle administrative tasks related to health insurance services.

## Features

### Core Features
- 🏥 **Provider Dashboard** - Overview of claims, authorizations, and payments
- 📋 **Claims Submission** - Submit and manage insurance claims
- ✅ **Eligibility Verification** - Real-time member eligibility checks
- 🔐 **Pre-Authorization** - Request and track treatment authorizations
- 💰 **Payment Tracking** - Monitor claim payments and remittances
- 👥 **Patient Management** - Manage patient records and coverage
- 📊 **Analytics & Reports** - Provider performance and claims analytics
- 📄 **Document Management** - Upload and manage medical documents

### Advanced Features
- 🏛️ **Facility Management** - Manage multiple facility locations
- 👨‍⚕️ **Staff Management** - Manage provider staff and permissions
- 💊 **Prescription Management** - E-prescribing and medication tracking
- 🛏️ **Bed Management** - Inpatient bed tracking and utilization
- 📱 **Mobile Responsive** - Full functionality on mobile devices
- 🌐 **Multi-language** - Indonesian and English support
- 🔄 **Batch Processing** - Bulk claim submission and processing

## Technology Stack

- **Framework**: React 18.2+
- **Language**: TypeScript 5.0+
- **State Management**: Redux Toolkit + RTK Query
- **UI Library**: Material-UI (MUI) v5
- **Styling**: Styled Components + CSS-in-JS
- **Build Tool**: Vite 5.0
- **Testing**: Jest + React Testing Library
- **E2E Testing**: Playwright
- **Code Quality**: ESLint + Prettier
- **Charts**: Recharts
- **Forms**: React Hook Form + Yup

## Getting Started

### Prerequisites

- Node.js 18+ and npm 9+
- Access to backend APIs
- Provider credentials
- Modern web browser

### Installation

1. **Navigate to the project**
```bash
cd frontend/apps/provider-portal
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

The application will be available at `http://localhost:3001`

### Environment Variables

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:4000
VITE_WS_URL=ws://localhost:4000

# Feature Flags
VITE_ENABLE_BATCH_CLAIMS=true
VITE_ENABLE_E_PRESCRIBING=true
VITE_ENABLE_BED_MANAGEMENT=true
VITE_ENABLE_ANALYTICS=true

# External Services
VITE_ELIGIBILITY_API_URL=https://api.eligibility.com
VITE_PRESCRIPTION_API_URL=https://api.prescriptions.com

# Analytics
VITE_GA_TRACKING_ID=UA-XXXXXXXXX
VITE_SENTRY_DSN=https://xxx@sentry.io/xxx

# Maps
VITE_GOOGLE_MAPS_API_KEY=your-api-key
```

## Project Structure

```
provider-portal/
├── public/
│   ├── assets/           # Static assets
│   └── locales/          # Translation files
├── src/
│   ├── app/              # App configuration
│   │   ├── App.tsx       # Root component
│   │   ├── store.ts      # Redux store
│   │   └── routes.tsx    # Route definitions
│   ├── features/         # Feature modules
│   │   ├── auth/         # Authentication
│   │   ├── claims/       # Claims management
│   │   ├── eligibility/  # Eligibility verification
│   │   ├── authorization/ # Pre-authorization
│   │   ├── payments/     # Payment tracking
│   │   ├── patients/     # Patient management
│   │   ├── analytics/    # Analytics & reports
│   │   ├── facility/     # Facility management
│   │   └── prescriptions/ # E-prescribing
│   ├── components/       # Shared components
│   │   ├── common/       # Generic components
│   │   ├── forms/        # Form components
│   │   ├── tables/       # Table components
│   │   └── layout/       # Layout components
│   ├── hooks/           # Custom hooks
│   ├── services/        # API services
│   ├── utils/           # Utility functions
│   ├── styles/          # Global styles
│   └── types/           # TypeScript types
├── tests/               # Test files
├── playwright/          # E2E tests
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
npm run e2e:debug    # Debug E2E tests

# Code Quality
npm run lint         # Run ESLint
npm run lint:fix     # Fix ESLint issues
npm run format       # Format with Prettier
npm run type-check   # TypeScript type checking
```

### Code Style Guide

- Use functional components with hooks
- Follow React best practices
- Use TypeScript for type safety
- Implement proper error boundaries
- Use React.memo for performance optimization
- Document complex business logic

## Features Documentation

### Claims Management

#### Cashless Claims
1. Search member by card/ID
2. Verify eligibility in real-time
3. Select services and diagnoses
4. Auto-calculate coverage
5. Submit for instant approval
6. Print guarantee letter

#### Reimbursement Claims
1. Enter member details
2. Add service items and costs
3. Upload supporting documents
4. Submit for processing
5. Track claim status
6. Receive payment notification

### Eligibility Verification

```typescript
// Real-time eligibility check
const checkEligibility = async (memberId: string) => {
  const response = await eligibilityService.verify({
    memberId,
    providerId,
    serviceDate: new Date(),
    serviceType: 'outpatient'
  });
  
  return {
    isEligible: response.eligible,
    coverage: response.coverage,
    benefits: response.benefits,
    limitations: response.limitations
  };
};
```

### Pre-Authorization

1. **Request Authorization**
   - Select member and service
   - Provide medical justification
   - Upload supporting documents
   - Submit for review

2. **Track Authorization**
   - View pending requests
   - Receive approval notifications
   - Download authorization letters

### Payment Management

```typescript
interface PaymentSummary {
  totalClaims: number;
  totalAmount: number;
  paidAmount: number;
  pendingAmount: number;
  payments: Payment[];
}

// Payment tracking component
const PaymentTracker = () => {
  const { data: payments } = useGetPaymentsQuery({
    providerId,
    dateRange: last30Days
  });
  
  return <PaymentDashboard data={payments} />;
};
```

## State Management

### Redux Store Structure

```typescript
{
  auth: {
    provider: Provider | null,
    facility: Facility | null,
    token: string | null,
    permissions: string[]
  },
  claims: {
    drafts: ClaimDraft[],
    submitted: Claim[],
    filters: ClaimFilters,
    selectedClaim: Claim | null
  },
  eligibility: {
    verifications: EligibilityCheck[],
    cache: Map<string, Eligibility>
  },
  authorizations: {
    pending: Authorization[],
    approved: Authorization[],
    rejected: Authorization[]
  },
  payments: {
    summary: PaymentSummary,
    transactions: Transaction[],
    remittances: Remittance[]
  },
  ui: {
    theme: 'light' | 'dark',
    language: 'en' | 'id',
    notifications: Notification[],
    sidebar: boolean
  }
}
```

## API Integration

### Service Layer Architecture

```typescript
// services/api/provider.service.ts
import { createApi } from '@reduxjs/toolkit/query/react';

export const providerApi = createApi({
  reducerPath: 'providerApi',
  baseQuery: fetchBaseQuery({
    baseUrl: VITE_API_BASE_URL,
    prepareHeaders: (headers) => {
      headers.set('authorization', `Bearer ${token}`);
      return headers;
    }
  }),
  endpoints: (builder) => ({
    submitClaim: builder.mutation<Claim, ClaimSubmission>({
      query: (claim) => ({
        url: '/claims',
        method: 'POST',
        body: claim
      })
    }),
    verifyEligibility: builder.query<Eligibility, EligibilityRequest>({
      query: (params) => `/eligibility/verify?${params}`
    })
  })
});
```

## Testing

### Unit Testing Strategy

```typescript
// ClaimForm.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ClaimForm } from './ClaimForm';

describe('ClaimForm', () => {
  it('validates required fields', async () => {
    render(<ClaimForm />);
    
    const submitButton = screen.getByRole('button', { name: /submit/i });
    await userEvent.click(submitButton);
    
    expect(screen.getByText('Member ID is required')).toBeInTheDocument();
    expect(screen.getByText('Service date is required')).toBeInTheDocument();
  });
  
  it('calculates coverage automatically', async () => {
    render(<ClaimForm />);
    
    await userEvent.type(screen.getByLabelText('Charged Amount'), '1000000');
    
    await waitFor(() => {
      expect(screen.getByLabelText('Covered Amount')).toHaveValue('900000');
      expect(screen.getByLabelText('Member Responsibility')).toHaveValue('100000');
    });
  });
});
```

### E2E Testing

```typescript
// playwright/specs/claim-submission.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Claim Submission Flow', () => {
  test('submits cashless claim successfully', async ({ page }) => {
    await page.goto('/claims/new');
    
    // Search member
    await page.fill('[data-testid="member-search"]', '1234567890');
    await page.click('[data-testid="search-button"]');
    
    // Verify eligibility
    await expect(page.locator('.eligibility-status')).toContainText('Eligible');
    
    // Add services
    await page.click('[data-testid="add-service"]');
    await page.selectOption('[data-testid="service-type"]', 'consultation');
    await page.fill('[data-testid="service-amount"]', '500000');
    
    // Submit claim
    await page.click('[data-testid="submit-claim"]');
    await expect(page.locator('.success-message')).toBeVisible();
  });
});
```

## Performance Optimization

### Code Splitting
```typescript
// Lazy load heavy features
const Analytics = lazy(() => import('./features/analytics'));
const Reports = lazy(() => import('./features/reports'));
```

### Data Caching
```typescript
// RTK Query caching
providerApi.endpoints.getProviderData.initiate(providerId, {
  subscriptionOptions: { pollingInterval: 60000 },
  forceRefetch: false
});
```

### Virtual Scrolling
```typescript
// For large claim lists
import { VirtualList } from '@tanstack/react-virtual';

const ClaimsList = ({ claims }) => (
  <VirtualList
    height={600}
    itemCount={claims.length}
    itemSize={80}
    renderItem={({ index }) => <ClaimRow claim={claims[index]} />}
  />
);
```

## Security

### Security Measures
- JWT token authentication
- Role-based access control (RBAC)
- Input sanitization
- XSS protection
- CSRF protection
- Secure session management
- Data encryption in transit

### Provider Permissions
```typescript
type Permission = 
  | 'claims.submit'
  | 'claims.view'
  | 'authorization.request'
  | 'patients.manage'
  | 'facility.admin'
  | 'reports.view';

const hasPermission = (permission: Permission): boolean => {
  return currentUser.permissions.includes(permission);
};
```

## Deployment

### Build for Production
```bash
# Build with optimizations
npm run build

# Analyze bundle
npm run build:analyze
```

### Docker Deployment
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

### Environment-Specific Builds
```bash
# Development
npm run build:dev

# Staging
npm run build:staging

# Production
npm run build:prod
```

## Monitoring

### Error Tracking
- Sentry integration for error reporting
- Custom error boundaries
- Detailed error logs

### Performance Monitoring
- Core Web Vitals tracking
- API response time monitoring
- User interaction tracking

### Analytics
- Page view tracking
- Feature usage analytics
- Conversion funnel analysis

## Troubleshooting

### Common Issues

1. **API Connection Issues**
   - Check API URL configuration
   - Verify CORS settings
   - Check authentication token

2. **Performance Issues**
   - Enable production build
   - Check bundle size
   - Optimize API calls
   - Implement pagination

3. **Authentication Issues**
   - Clear local storage
   - Check token expiration
   - Verify provider credentials

## Support

- **Documentation**: [Full docs](../../../docs)
- **API Documentation**: [API Reference](../../../services/*/docs/API.md)
- **Design System**: [UI Components](../../packages/ui-components)
- **Issues**: GitHub Issues
- **Team**: Provider Portal Team - provider-portal@claims-askes.com

## License

Proprietary - All rights reserved