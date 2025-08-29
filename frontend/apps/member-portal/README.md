# Member Portal

## Overview

The Member Portal is a comprehensive web application that provides health insurance members with self-service capabilities to manage their insurance coverage, submit claims, find providers, and access healthcare services.

## Features

### Core Features
- 👤 **Profile Management** - View and update personal information
- 📋 **Claims Management** - Submit and track insurance claims
- 🏥 **Provider Search** - Find in-network healthcare providers
- 💳 **Digital Insurance Card** - Access digital member ID card
- 📊 **Benefits Overview** - View coverage details and limits
- 💰 **Payment History** - Track claim payments and reimbursements
- 📄 **Document Management** - Upload and manage claim documents
- 🔔 **Notifications** - Real-time updates on claim status

### Advanced Features
- 🏥 **Pre-authorization** - Request treatment pre-approvals
- 💊 **Prescription Management** - Track medication coverage
- 📈 **Health Dashboard** - Personalized health insights
- 👨‍👩‍👧‍👦 **Dependent Management** - Manage family member coverage
- 📱 **Telemedicine** - Access virtual consultations
- 🌐 **Multi-language Support** - Indonesian and English

## Technology Stack

- **Framework**: React 18.2+
- **Language**: TypeScript 5.0+
- **State Management**: Redux Toolkit + RTK Query
- **UI Library**: Ant Design 5.0
- **Styling**: CSS Modules + Tailwind CSS
- **Build Tool**: Vite 5.0
- **Testing**: Jest + React Testing Library
- **E2E Testing**: Cypress
- **Code Quality**: ESLint + Prettier

## Getting Started

### Prerequisites

- Node.js 18+ and npm 9+
- Access to backend APIs
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Installation

1. **Navigate to the project**
```bash
cd frontend/apps/member-portal
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

The application will be available at `http://localhost:3000`

### Environment Variables

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:4000
VITE_WS_URL=ws://localhost:4000

# Feature Flags
VITE_ENABLE_TELEMEDICINE=true
VITE_ENABLE_HEALTH_TRACKING=true
VITE_ENABLE_CHAT_SUPPORT=false

# Analytics
VITE_GA_TRACKING_ID=UA-XXXXXXXXX
VITE_SENTRY_DSN=https://xxx@sentry.io/xxx

# Maps
VITE_GOOGLE_MAPS_API_KEY=your-api-key
```

## Project Structure

```
member-portal/
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
│   │   ├── profile/      # Member profile
│   │   ├── providers/    # Provider search
│   │   ├── benefits/     # Benefits overview
│   │   └── documents/    # Document management
│   ├── components/       # Shared components
│   │   ├── common/       # Generic components
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
```

### Code Style Guide

- Use functional components with hooks
- Follow React best practices
- Use TypeScript for type safety
- Maintain consistent naming conventions
- Write comprehensive tests
- Document complex logic

### Component Development

Example component structure:
```typescript
// components/ClaimCard/ClaimCard.tsx
import React from 'react';
import { Card, Tag } from 'antd';
import styles from './ClaimCard.module.css';

interface ClaimCardProps {
  claim: Claim;
  onClick?: (claim: Claim) => void;
}

export const ClaimCard: React.FC<ClaimCardProps> = ({ claim, onClick }) => {
  return (
    <Card 
      className={styles.card}
      onClick={() => onClick?.(claim)}
    >
      <h3>{claim.claimNumber}</h3>
      <Tag color={getStatusColor(claim.status)}>
        {claim.status}
      </Tag>
    </Card>
  );
};
```

## Features Documentation

### Authentication Flow
1. User enters credentials
2. JWT token received from auth service
3. Token stored in secure storage
4. Auto-refresh before expiration
5. Logout clears all session data

### Claims Submission
1. Select claim type (cashless/reimbursement)
2. Choose provider and service date
3. Add claim items with amounts
4. Upload supporting documents
5. Review and submit
6. Track status in real-time

### Provider Search
1. Filter by location, specialty, facility type
2. View provider details and ratings
3. Check real-time availability
4. Get directions via integrated maps
5. Save favorite providers

## State Management

### Redux Store Structure
```typescript
{
  auth: {
    user: User | null,
    token: string | null,
    isAuthenticated: boolean
  },
  claims: {
    list: Claim[],
    selected: Claim | null,
    filters: ClaimFilters,
    loading: boolean
  },
  providers: {
    searchResults: Provider[],
    selected: Provider | null,
    favorites: Provider[]
  },
  ui: {
    theme: 'light' | 'dark',
    language: 'en' | 'id',
    notifications: Notification[]
  }
}
```

## API Integration

### API Service Example
```typescript
// services/api/claims.service.ts
import { apiClient } from '@/services/api/client';

export const claimsService = {
  async submitClaim(data: ClaimSubmission) {
    return apiClient.post('/claims', data);
  },
  
  async getClaims(filters?: ClaimFilters) {
    return apiClient.get('/claims', { params: filters });
  },
  
  async getClaimById(id: string) {
    return apiClient.get(`/claims/${id}`);
  }
};
```

## Testing

### Unit Testing
```typescript
// ClaimCard.test.tsx
import { render, screen } from '@testing-library/react';
import { ClaimCard } from './ClaimCard';

describe('ClaimCard', () => {
  it('displays claim number', () => {
    const claim = { claimNumber: 'CLM-2024-001' };
    render(<ClaimCard claim={claim} />);
    expect(screen.getByText('CLM-2024-001')).toBeInTheDocument();
  });
});
```

### E2E Testing
```typescript
// cypress/e2e/claims.cy.ts
describe('Claims Flow', () => {
  it('submits a new claim', () => {
    cy.login();
    cy.visit('/claims/new');
    cy.fillClaimForm();
    cy.get('[data-testid="submit-button"]').click();
    cy.contains('Claim submitted successfully');
  });
});
```

## Build & Deployment

### Build for Production
```bash
# Build application
npm run build

# Output in dist/ directory
# Ready for deployment to CDN or web server
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

## Performance Optimization

### Code Splitting
- Route-based code splitting
- Lazy loading of features
- Dynamic imports for heavy libraries

### Caching Strategy
- Service Worker for offline support
- API response caching
- Static asset caching

### Bundle Optimization
- Tree shaking
- Minification
- Compression (gzip/brotli)
- Image optimization

## Security

### Security Measures
- Content Security Policy (CSP)
- XSS protection
- HTTPS enforcement
- Secure cookie handling
- Input sanitization
- Rate limiting

### Authentication Security
- JWT token validation
- Token refresh mechanism
- Session timeout
- Multi-factor authentication support

## Accessibility

### WCAG 2.1 Compliance
- Semantic HTML
- ARIA labels
- Keyboard navigation
- Screen reader support
- High contrast mode
- Focus management

## Internationalization

### Supported Languages
- English (en)
- Indonesian (id)

### Translation Management
```typescript
import { useTranslation } from 'react-i18next';

function ClaimsList() {
  const { t } = useTranslation();
  
  return (
    <h1>{t('claims.title')}</h1>
  );
}
```

## Monitoring

### Error Tracking
- Sentry integration for error reporting
- Custom error boundaries
- User feedback collection

### Analytics
- Google Analytics integration
- Custom event tracking
- User behavior analysis

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Troubleshooting

### Common Issues

1. **Build fails**
   - Clear node_modules and reinstall
   - Check Node.js version
   - Verify environment variables

2. **API connection issues**
   - Check API URL configuration
   - Verify CORS settings
   - Check network connectivity

3. **Performance issues**
   - Enable production build
   - Check bundle size
   - Optimize images

## Contributing

### Development Workflow
1. Create feature branch
2. Implement feature with tests
3. Run linting and tests
4. Submit pull request
5. Code review
6. Merge to main

### Commit Guidelines
```
feat: Add claim submission feature
fix: Resolve date picker issue
docs: Update README
style: Format code
refactor: Optimize API calls
test: Add unit tests
chore: Update dependencies
```

## Support

- **Documentation**: [Full docs](../../../docs)
- **Design System**: [UI Components](../../packages/ui-components)
- **Issues**: GitHub Issues
- **Team**: Frontend Team - frontend@claims-askes.com

## License

Proprietary - All rights reserved