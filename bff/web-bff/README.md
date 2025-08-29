# Web BFF (Backend for Frontend)

## Overview

The Web BFF is a specialized backend service that aggregates and optimizes API calls for web applications (Member Portal, Provider Portal, Admin Console). It acts as an intermediary layer between the web frontends and microservices, reducing the number of API calls and tailoring responses for web-specific needs.

## Purpose

### Why BFF?
- **API Aggregation**: Combines multiple microservice calls into single endpoints
- **Response Optimization**: Tailors data format for web consumption
- **Reduced Latency**: Minimizes round trips between client and server
- **Business Logic**: Implements presentation-layer business logic
- **Security**: Additional security layer between frontend and microservices
- **Caching**: Intelligent caching for frequently accessed data

## Technology Stack

- **Runtime**: Node.js 18+
- **Framework**: NestJS 10+
- **Language**: TypeScript 5.0+
- **API**: GraphQL with Apollo Server
- **REST**: For legacy endpoints
- **Caching**: Redis
- **Authentication**: JWT with refresh tokens
- **API Gateway**: Express Gateway
- **Testing**: Jest + Supertest
- **Documentation**: GraphQL Playground + Swagger

## Architecture

```
Web Clients
    ↓
[Web BFF]
    ↓
┌───────────────────────────────────────────────────────────┐
│ Claims  │ Member  │ Provider │ Benefit │ Policy  │
│ Service │ Service │ Service  │ Service │ Service │
└───────────────────────────────────────────────────────────┘
```

## Getting Started

### Prerequisites

- Node.js 18+
- Redis 7+
- Access to microservices

### Installation

1. **Navigate to project**
```bash
cd bff/web-bff
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
npm run start:dev
```

The BFF will be available at:
- GraphQL: `http://localhost:4000/graphql`
- REST: `http://localhost:4000/api/v1`
- GraphQL Playground: `http://localhost:4000/graphql`
- Swagger: `http://localhost:4000/api-docs`

### Environment Variables

```bash
# Server Configuration
PORT=4000
NODE_ENV=development

# Microservices URLs
CLAIMS_SERVICE_URL=http://localhost:8001
MEMBER_SERVICE_URL=http://localhost:8002
PROVIDER_SERVICE_URL=http://localhost:8003
BENEFIT_SERVICE_URL=http://localhost:8004
POLICY_SERVICE_URL=http://localhost:8005

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Security
JWT_SECRET=your-secret-key
JWT_EXPIRATION=1h
REFRESH_TOKEN_SECRET=your-refresh-secret
REFRESH_TOKEN_EXPIRATION=7d

# Rate Limiting
RATE_LIMIT_WINDOW=15m
RATE_LIMIT_MAX=100

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
```

## Project Structure

```
web-bff/
├── src/
│   ├── app.module.ts           # Root module
│   ├── main.ts                 # Application entry
│   ├── modules/
│   │   ├── auth/               # Authentication
│   │   ├── claims/             # Claims aggregation
│   │   ├── members/            # Member aggregation
│   │   ├── providers/          # Provider aggregation
│   │   ├── dashboard/          # Dashboard aggregation
│   │   └── reports/            # Reports aggregation
│   ├── graphql/
│   │   ├── schema.gql          # GraphQL schema
│   │   ├── resolvers/          # GraphQL resolvers
│   │   └── scalars/            # Custom scalars
│   ├── common/
│   │   ├── interceptors/       # HTTP interceptors
│   │   ├── guards/             # Auth guards
│   │   ├── filters/            # Exception filters
│   │   └── decorators/         # Custom decorators
│   ├── services/
│   │   ├── cache.service.ts    # Redis caching
│   │   ├── aggregator.service.ts # Data aggregation
│   │   └── circuit-breaker.ts  # Circuit breaker
│   └── config/
│       └── configuration.ts    # Config module
├── test/                       # E2E tests
├── nest-cli.json
└── package.json
```

## API Patterns

### GraphQL Schema

```graphql
type Query {
  # Member Portal
  memberDashboard(memberId: ID!): MemberDashboard!
  memberClaims(memberId: ID!, filter: ClaimFilter): ClaimConnection!
  memberBenefits(memberId: ID!): [Benefit!]!
  nearbyProviders(location: LocationInput!, radius: Float): [Provider!]!
  
  # Provider Portal
  providerDashboard(providerId: ID!): ProviderDashboard!
  eligibilityCheck(request: EligibilityRequest!): EligibilityResponse!
  providerClaims(providerId: ID!, filter: ClaimFilter): ClaimConnection!
  
  # Admin Console
  systemMetrics: SystemMetrics!
  claimsAnalytics(dateRange: DateRangeInput!): ClaimsAnalytics!
  memberAnalytics(dateRange: DateRangeInput!): MemberAnalytics!
}

type Mutation {
  # Claims
  submitClaim(input: ClaimInput!): ClaimResponse!
  updateClaimStatus(claimId: ID!, status: ClaimStatus!): Claim!
  
  # Authentication
  login(credentials: LoginInput!): AuthResponse!
  refreshToken(token: String!): AuthResponse!
  logout: Boolean!
}

type Subscription {
  claimStatusUpdated(claimId: ID!): ClaimStatusUpdate!
  notificationReceived(userId: ID!): Notification!
}
```

### Aggregation Examples

#### Member Dashboard Aggregation

```typescript
@Resolver('MemberDashboard')
export class MemberDashboardResolver {
  constructor(
    private claimsService: ClaimsService,
    private memberService: MemberService,
    private benefitService: BenefitService,
    private cacheService: CacheService
  ) {}
  
  @Query()
  async memberDashboard(@Args('memberId') memberId: string) {
    const cacheKey = `dashboard:${memberId}`;
    const cached = await this.cacheService.get(cacheKey);
    
    if (cached) return cached;
    
    // Parallel service calls
    const [member, claims, benefits, coverage] = await Promise.all([
      this.memberService.getMember(memberId),
      this.claimsService.getRecentClaims(memberId, 5),
      this.benefitService.getMemberBenefits(memberId),
      this.memberService.getCoverageStatus(memberId)
    ]);
    
    const dashboard = {
      member: {
        id: member.id,
        name: member.name,
        planName: member.plan.name,
        memberSince: member.enrollmentDate
      },
      recentClaims: claims.map(this.transformClaim),
      benefitsSummary: this.summarizeBenefits(benefits),
      coverageStatus: coverage,
      notifications: await this.getNotifications(memberId)
    };
    
    await this.cacheService.set(cacheKey, dashboard, 300); // 5 min cache
    
    return dashboard;
  }
}
```

#### Claims Submission Aggregation

```typescript
@Injectable()
export class ClaimsAggregatorService {
  async submitClaim(claimData: ClaimInput, userId: string) {
    // Step 1: Validate member eligibility
    const eligibility = await this.memberService.checkEligibility({
      memberId: claimData.memberId,
      serviceDate: claimData.serviceDate,
      providerId: claimData.providerId
    });
    
    if (!eligibility.isEligible) {
      throw new BadRequestException(eligibility.reason);
    }
    
    // Step 2: Validate provider
    const provider = await this.providerService.validateProvider(
      claimData.providerId
    );
    
    if (!provider.isActive) {
      throw new BadRequestException('Provider not active');
    }
    
    // Step 3: Check benefits
    const benefitCheck = await this.benefitService.validateBenefits(
      claimData.items
    );
    
    // Step 4: Submit claim
    const claim = await this.claimsService.submitClaim({
      ...claimData,
      eligibility,
      benefitValidation: benefitCheck
    });
    
    // Step 5: Send notifications
    await this.notificationService.notifyClaimSubmission(claim);
    
    return claim;
  }
}
```

### REST Endpoints (Legacy Support)

```typescript
@Controller('api/v1')
export class LegacyController {
  @Get('claims/:memberId')
  @UseGuards(JwtAuthGuard)
  async getMemberClaims(
    @Param('memberId') memberId: string,
    @Query() query: ClaimQueryDto
  ) {
    return this.claimsAggregator.getMemberClaims(memberId, query);
  }
  
  @Post('claims')
  @UseGuards(JwtAuthGuard)
  async submitClaim(@Body() claimDto: CreateClaimDto) {
    return this.claimsAggregator.submitClaim(claimDto);
  }
}
```

## Data Transformation

### Response Optimization

```typescript
class DataTransformer {
  // Transform for web consumption
  transformClaimForWeb(claim: RawClaim): WebClaim {
    return {
      id: claim.id,
      displayNumber: `CLM-${claim.claim_number}`,
      status: this.mapStatus(claim.status),
      statusColor: this.getStatusColor(claim.status),
      amount: this.formatCurrency(claim.total_amount),
      provider: {
        name: claim.provider_name,
        location: claim.provider_location
      },
      timeline: this.buildTimeline(claim.history),
      actions: this.getAvailableActions(claim)
    };
  }
  
  // Aggregate multiple sources
  aggregateMemberData(sources: DataSources): MemberProfile {
    return {
      personal: sources.memberService,
      claims: this.summarizeClaims(sources.claimsService),
      benefits: this.organizeBenefits(sources.benefitService),
      payments: sources.paymentService,
      documents: sources.documentService
    };
  }
}
```

## Caching Strategy

### Redis Caching Implementation

```typescript
@Injectable()
export class CacheService {
  private redis: Redis;
  
  constructor() {
    this.redis = new Redis({
      host: process.env.REDIS_HOST,
      port: process.env.REDIS_PORT
    });
  }
  
  async get<T>(key: string): Promise<T | null> {
    const data = await this.redis.get(key);
    return data ? JSON.parse(data) : null;
  }
  
  async set(key: string, value: any, ttl: number = 3600) {
    await this.redis.setex(key, ttl, JSON.stringify(value));
  }
  
  async invalidate(pattern: string) {
    const keys = await this.redis.keys(pattern);
    if (keys.length) {
      await this.redis.del(...keys);
    }
  }
  
  // Cache aside pattern
  async getOrSet<T>(
    key: string,
    factory: () => Promise<T>,
    ttl: number = 3600
  ): Promise<T> {
    let data = await this.get<T>(key);
    
    if (!data) {
      data = await factory();
      await this.set(key, data, ttl);
    }
    
    return data;
  }
}
```

### Cache Invalidation

```typescript
@Injectable()
export class CacheInvalidator {
  constructor(
    private cacheService: CacheService,
    private eventEmitter: EventEmitter2
  ) {
    this.setupEventListeners();
  }
  
  private setupEventListeners() {
    // Invalidate on claim status change
    this.eventEmitter.on('claim.status.changed', async (event) => {
      await this.cacheService.invalidate(`claim:${event.claimId}:*`);
      await this.cacheService.invalidate(`dashboard:${event.memberId}:*`);
    });
    
    // Invalidate on member update
    this.eventEmitter.on('member.updated', async (event) => {
      await this.cacheService.invalidate(`member:${event.memberId}:*`);
    });
  }
}
```

## Error Handling

### Circuit Breaker Pattern

```typescript
@Injectable()
export class CircuitBreakerService {
  private breakers = new Map<string, CircuitBreaker>();
  
  getBreaker(serviceName: string): CircuitBreaker {
    if (!this.breakers.has(serviceName)) {
      this.breakers.set(serviceName, new CircuitBreaker({
        timeout: 5000,
        errorThreshold: 50,
        resetTimeout: 30000
      }));
    }
    
    return this.breakers.get(serviceName);
  }
  
  async callService<T>(
    serviceName: string,
    operation: () => Promise<T>,
    fallback?: () => T
  ): Promise<T> {
    const breaker = this.getBreaker(serviceName);
    
    try {
      return await breaker.fire(operation);
    } catch (error) {
      if (fallback) {
        return fallback();
      }
      throw new ServiceUnavailableException(
        `${serviceName} is currently unavailable`
      );
    }
  }
}
```

## Security

### Authentication & Authorization

```typescript
@Injectable()
export class AuthService {
  async validateToken(token: string): Promise<TokenPayload> {
    try {
      const payload = jwt.verify(token, process.env.JWT_SECRET);
      
      // Additional validation
      const user = await this.userService.findById(payload.userId);
      if (!user || !user.isActive) {
        throw new UnauthorizedException('Invalid user');
      }
      
      return payload;
    } catch (error) {
      throw new UnauthorizedException('Invalid token');
    }
  }
  
  async refreshToken(refreshToken: string): Promise<AuthTokens> {
    const payload = jwt.verify(
      refreshToken,
      process.env.REFRESH_TOKEN_SECRET
    );
    
    const newAccessToken = this.generateAccessToken(payload.userId);
    const newRefreshToken = this.generateRefreshToken(payload.userId);
    
    return {
      accessToken: newAccessToken,
      refreshToken: newRefreshToken
    };
  }
}
```

### Rate Limiting

```typescript
@Injectable()
export class RateLimitGuard implements CanActivate {
  constructor(private rateLimiter: RateLimiterRedis) {}
  
  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest();
    const key = `${request.ip}:${request.user?.id || 'anonymous'}`;
    
    try {
      await this.rateLimiter.consume(key);
      return true;
    } catch (rejRes) {
      throw new TooManyRequestsException(
        'Too many requests, please try again later'
      );
    }
  }
}
```

## Testing

### Unit Testing

```typescript
describe('ClaimsAggregatorService', () => {
  let service: ClaimsAggregatorService;
  let claimsService: MockClaimsService;
  let memberService: MockMemberService;
  
  beforeEach(() => {
    const module = Test.createTestingModule({
      providers: [
        ClaimsAggregatorService,
        { provide: ClaimsService, useClass: MockClaimsService },
        { provide: MemberService, useClass: MockMemberService }
      ]
    }).compile();
    
    service = module.get(ClaimsAggregatorService);
  });
  
  describe('submitClaim', () => {
    it('should aggregate data from multiple services', async () => {
      const claimData = { /* test data */ };
      
      const result = await service.submitClaim(claimData, 'user123');
      
      expect(result).toHaveProperty('claimNumber');
      expect(memberService.checkEligibility).toHaveBeenCalled();
      expect(claimsService.submitClaim).toHaveBeenCalled();
    });
    
    it('should handle service failures gracefully', async () => {
      memberService.checkEligibility.mockRejectedValue(
        new Error('Service unavailable')
      );
      
      await expect(service.submitClaim({}, 'user123'))
        .rejects.toThrow(ServiceUnavailableException);
    });
  });
});
```

### E2E Testing

```typescript
describe('Web BFF E2E', () => {
  let app: INestApplication;
  
  beforeAll(async () => {
    const moduleFixture = await Test.createTestingModule({
      imports: [AppModule]
    }).compile();
    
    app = moduleFixture.createNestApplication();
    await app.init();
  });
  
  describe('GraphQL', () => {
    it('should return member dashboard', () => {
      return request(app.getHttpServer())
        .post('/graphql')
        .send({
          query: `
            query {
              memberDashboard(memberId: "123") {
                member { name }
                recentClaims { id status }
              }
            }
          `
        })
        .expect(200)
        .expect(res => {
          expect(res.body.data.memberDashboard).toBeDefined();
        });
    });
  });
});
```

## Performance Optimization

### Request Batching

```typescript
@Injectable()
export class BatchingService {
  private batch: Map<string, Promise<any>> = new Map();
  
  async batchRequest<T>(
    key: string,
    factory: () => Promise<T>
  ): Promise<T> {
    if (!this.batch.has(key)) {
      const promise = factory().finally(() => {
        this.batch.delete(key);
      });
      
      this.batch.set(key, promise);
    }
    
    return this.batch.get(key);
  }
}
```

### Response Compression

```typescript
app.use(compression({
  filter: (req, res) => {
    if (req.headers['x-no-compression']) {
      return false;
    }
    return compression.filter(req, res);
  },
  level: 6
}));
```

## Monitoring

### Metrics Collection

```typescript
@Injectable()
export class MetricsService {
  private register: Registry;
  private httpDuration: Histogram;
  private serviceCallDuration: Histogram;
  
  constructor() {
    this.register = new Registry();
    
    this.httpDuration = new Histogram({
      name: 'http_request_duration_seconds',
      help: 'Duration of HTTP requests in seconds',
      labelNames: ['method', 'route', 'status'],
      registers: [this.register]
    });
    
    this.serviceCallDuration = new Histogram({
      name: 'service_call_duration_seconds',
      help: 'Duration of service calls in seconds',
      labelNames: ['service', 'method'],
      registers: [this.register]
    });
  }
  
  recordHttpRequest(method: string, route: string, status: number, duration: number) {
    this.httpDuration.observe({ method, route, status }, duration);
  }
  
  recordServiceCall(service: string, method: string, duration: number) {
    this.serviceCallDuration.observe({ service, method }, duration);
  }
}
```

### Health Checks

```typescript
@Controller('health')
export class HealthController {
  constructor(
    private health: HealthCheckService,
    private http: HttpHealthIndicator,
    private redis: RedisHealthIndicator
  ) {}
  
  @Get()
  @HealthCheck()
  check() {
    return this.health.check([
      () => this.http.pingCheck('claims-service', process.env.CLAIMS_SERVICE_URL),
      () => this.http.pingCheck('member-service', process.env.MEMBER_SERVICE_URL),
      () => this.redis.isHealthy('redis')
    ]);
  }
}
```

## Deployment

### Docker

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./
EXPOSE 4000
CMD ["node", "dist/main"]
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-bff
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-bff
  template:
    metadata:
      labels:
        app: web-bff
    spec:
      containers:
      - name: web-bff
        image: web-bff:latest
        ports:
        - containerPort: 4000
        env:
        - name: NODE_ENV
          value: production
        livenessProbe:
          httpGet:
            path: /health
            port: 4000
        readinessProbe:
          httpGet:
            path: /health
            port: 4000
```

## Troubleshooting

### Common Issues

1. **Service timeout errors**
   - Increase timeout in circuit breaker
   - Check service health endpoints
   - Review network connectivity

2. **High memory usage**
   - Review cache TTL settings
   - Implement cache eviction policies
   - Monitor for memory leaks

3. **GraphQL N+1 queries**
   - Implement DataLoader pattern
   - Use field-level caching
   - Optimize resolver queries

## Support

- **Documentation**: [Full docs](../../docs)
- **Service Catalog**: [Microservices](../../services)
- **Team**: Platform Team - platform@claims-askes.com

## License

Proprietary - All rights reserved