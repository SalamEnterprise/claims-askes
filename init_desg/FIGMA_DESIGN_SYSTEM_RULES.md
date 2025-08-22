# Figma Design System Rules - Claims Askes Health Insurance Platform

## Design System Structure

### 1. Token Definitions

#### Color Tokens
```javascript
// Primary Colors
const colors = {
  primary: {
    100: '#E6F2FF',
    500: '#0066CC',
    600: '#0066CC',
    900: '#001A33'
  },
  secondary: {
    500: '#00A851'  // Success, approved
  },
  semantic: {
    success: '#4CAF50',
    warning: '#FFC107', 
    error: '#E91E63',
    info: '#17A2B8'
  },
  neutral: {
    gray100: '#FAFAFA',
    gray200: '#F5F5F5',
    gray300: '#E0E0E0',
    gray400: '#CCCCCC',
    gray500: '#9E9E9E',
    gray600: '#666666',
    gray700: '#616161',
    gray800: '#424242',
    gray900: '#212121',
    black: '#1A1A1A',
    white: '#FFFFFF'
  }
}
```

#### Typography Tokens
```javascript
const typography = {
  fontFamily: {
    primary: 'Inter',
    secondary: 'SF Pro Display',
    mono: 'SF Mono'
  },
  fontSize: {
    display: '48px',
    h1: '36px',
    h2: '28px',
    h3: '24px',
    body: '16px',
    caption: '14px',
    small: '12px'
  },
  lineHeight: {
    display: '56px',
    h1: '44px',
    h2: '36px',
    h3: '32px',
    body: '24px',
    caption: '20px',
    small: '16px'
  },
  fontWeight: {
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700
  }
}
```

#### Spacing Tokens
```javascript
const spacing = {
  base: 8,
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
  xxxl: 64
}
```

#### Border & Shadow Tokens
```javascript
const borderRadius = {
  none: 0,
  sm: 8,
  md: 12,
  lg: 16,
  full: 9999
}

const shadows = {
  sm: '0 2px 4px rgba(0,0,0,0.08)',
  md: '0 4px 8px rgba(0,0,0,0.12)',
  lg: '0 8px 16px rgba(0,0,0,0.16)'
}
```

### 2. Component Library Structure

#### Atomic Design Pattern
```
Components/
├── Atoms/
│   ├── Button
│   ├── Input
│   ├── Icon
│   ├── Text
│   └── Badge
├── Molecules/
│   ├── Card
│   ├── FormField
│   ├── ClaimCard
│   ├── InsuranceCard
│   └── BottomNavigation
├── Organisms/
│   ├── Header
│   ├── ClaimForm
│   ├── CameraViewfinder
│   ├── ProviderList
│   └── Dashboard
└── Templates/
    ├── MemberPortal
    ├── ProviderPortal
    ├── MobileApp
    └── AdminDashboard
```

### 3. Frameworks & Libraries

#### Web Portal Stack
- **Framework**: React 18+ with TypeScript
- **Styling**: CSS Modules + PostCSS
- **State Management**: Context API for design system
- **Build System**: Webpack/Vite
- **Component Documentation**: Storybook

#### Mobile App Stack
- **Framework**: React Native 0.70+
- **Styling**: StyleSheet API
- **Navigation**: React Navigation 6
- **Platform**: iOS 13+ / Android 6+

### 4. Asset Management

#### Image Assets
```
assets/
├── images/
│   ├── logos/
│   ├── illustrations/
│   └── backgrounds/
├── icons/
│   ├── system/     # UI icons
│   ├── medical/    # Healthcare specific
│   └── status/     # Status indicators
└── animations/
    └── lottie/     # JSON animations
```

#### Asset Optimization
- WebP format for web images
- Multiple resolutions (@1x, @2x, @3x) for mobile
- SVG for icons and logos
- Lazy loading for images

### 5. Icon System

#### Icon Naming Convention
```
icon-[category]-[name]-[variant]
Examples:
- icon-system-home-outline
- icon-medical-hospital-filled
- icon-status-success-circle
```

#### Icon Implementation
```jsx
// Web
import { Icon } from '@/components/atoms/Icon'
<Icon name="home" size={24} color="#0066CC" />

// Mobile
import Icon from 'react-native-vector-icons/MaterialIcons'
<Icon name="home" size={24} color="#0066CC" />
```

### 6. Styling Approach

#### CSS Architecture
```css
/* Base styles */
:root {
  --color-primary: #0066CC;
  --spacing-unit: 8px;
  --font-primary: 'Inter', sans-serif;
}

/* Component styles */
.component {
  /* Layout */
  display: flex;
  
  /* Spacing */
  padding: var(--spacing-md);
  
  /* Typography */
  font-family: var(--font-primary);
  
  /* Colors */
  background: var(--color-surface);
  
  /* Responsive */
  @media (max-width: 768px) {
    padding: var(--spacing-sm);
  }
}
```

#### Responsive Breakpoints
```javascript
const breakpoints = {
  mobile: 320,    // Small phones
  mobileL: 375,   // Standard phones  
  tablet: 768,    // Tablets
  desktop: 1024,  // Desktop
  desktopL: 1440, // Large screens
  desktopXL: 1920 // Ultra-wide
}
```

### 7. Figma-to-Code Mapping

#### Component Naming
```
Figma Layer → Code Component
Button/Primary → <Button variant="primary" />
Card/Claim → <ClaimCard />
Form/Input → <FormField type="text" />
```

#### Variable Mapping
```javascript
// Figma Variables → Code Tokens
{
  'color/primary/500': colors.primary[500],
  'spacing/md': spacing.md,
  'typography/body': typography.fontSize.body,
  'radius/md': borderRadius.md
}
```

## Component Implementation Patterns

### Button Component
```jsx
// Figma: Button/Primary/Default
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'danger' | 'ghost'
  size: 'small' | 'medium' | 'large'
  icon?: string
  loading?: boolean
  disabled?: boolean
  fullWidth?: boolean
}

// Usage
<Button 
  variant="primary"
  size="medium"
  icon="arrow-right"
>
  Submit Claim
</Button>
```

### Card Component  
```jsx
// Figma: Card/Elevated
interface CardProps {
  elevated?: boolean
  interactive?: boolean
  padding?: 'none' | 'small' | 'medium' | 'large'
  status?: 'default' | 'success' | 'warning' | 'error'
}

// Usage
<Card elevated interactive status="success">
  <CardHeader title="Claim Approved" />
  <CardBody>...</CardBody>
</Card>
```

### Form Field Component
```jsx
// Figma: Form/Input/Currency
interface FormFieldProps {
  type: 'text' | 'number' | 'currency' | 'date'
  label: string
  helper?: string
  error?: string
  prefix?: ReactNode
  suffix?: ReactNode
}

// Usage
<FormField
  type="currency"
  label="Claim Amount"
  prefix="Rp"
  helper="Enter the total amount"
/>
```

## Screen-Specific Guidelines

### Member Portal
- Grid: 12 columns on desktop, 4 on mobile
- Max width: 1200px
- Side navigation: 240px width
- Content padding: 32px desktop, 16px mobile

### Provider Portal  
- Dashboard layout: 3-column grid
- Data tables: Sticky headers
- Modal overlays: 600px max width
- Real-time updates: WebSocket integration

### Mobile App
- Bottom navigation: 56px height
- Safe area insets: Platform-specific
- Touch targets: Minimum 44x44px
- Gesture zones: 20px from edges

### Admin Dashboard
- Sidebar: Collapsible to 64px
- Chart containers: Responsive aspect ratios
- Data grids: Virtual scrolling for performance
- Multi-panel layouts: Resizable splitters

## Accessibility Standards

### WCAG 2.1 AA Compliance
```css
/* Color Contrast */
.text-primary {
  color: #1A1A1A; /* 12.6:1 on white */
}

.text-secondary {
  color: #666666; /* 5.7:1 on white */
}

/* Focus Indicators */
:focus-visible {
  outline: 2px solid #0066CC;
  outline-offset: 2px;
}

/* Touch Targets */
.touchable {
  min-width: 44px;
  min-height: 44px;
}
```

### Semantic HTML
```jsx
// Use semantic elements
<nav aria-label="Main navigation">
<main role="main">
<section aria-labelledby="claims-heading">
<button aria-label="Submit claim" aria-busy={loading}>
```

## Performance Guidelines

### Bundle Size Targets
- JavaScript: <200KB gzipped
- CSS: <50KB gzipped  
- Initial load: <3s on 3G
- Time to interactive: <5s

### Optimization Techniques
- Code splitting by route
- Lazy loading components
- Image optimization (WebP, progressive)
- Font subsetting
- CSS purging

## Integration with Figma

### Using Figma Dev Mode
1. Select component in Figma
2. Use MCP tools to get code
3. Map to existing component structure
4. Apply local token overrides

### Code Connect Mapping
```javascript
// Map Figma components to code
const figmaMapping = {
  '1:234': 'components/Button',
  '2:456': 'components/Card',
  '3:789': 'components/ClaimForm'
}
```

### Variable Sync
```javascript
// Sync Figma variables to code
const syncVariables = async (nodeId) => {
  const variables = await getFigmaVariables(nodeId)
  return mapToDesignTokens(variables)
}
```

## Quality Checklist

### Before Handoff
- [ ] All components have proper variants
- [ ] Design tokens are consistent
- [ ] Responsive behavior defined
- [ ] Interactions documented
- [ ] Accessibility annotations added
- [ ] Export settings configured

### Code Review
- [ ] Components match Figma specs
- [ ] Tokens used consistently
- [ ] Responsive breakpoints work
- [ ] Accessibility standards met
- [ ] Performance targets achieved
- [ ] Cross-browser tested

---

*Last Updated: August 15, 2025*
*Version: 1.0.0*