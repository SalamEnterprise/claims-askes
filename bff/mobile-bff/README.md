# Mobile BFF (Backend for Frontend)

## Overview

The Mobile BFF is a specialized backend service optimized for mobile applications (Member App, Provider App, Field Agent App). It provides mobile-specific optimizations including reduced payload sizes, efficient data synchronization, offline support, and push notification management.

## Purpose

### Mobile-Specific Optimizations
- **Bandwidth Optimization**: Minimized payload sizes for cellular networks
- **Battery Efficiency**: Batched requests to reduce radio usage
- **Offline Support**: Sync protocols for offline-first mobile apps
- **Push Notifications**: Centralized push notification management
- **Device-Specific**: Tailored responses based on device capabilities
- **Progressive Data Loading**: Pagination and lazy loading support

## Technology Stack

- **Runtime**: Node.js 18+
- **Framework**: Fastify 4+ (for performance)
- **Language**: TypeScript 5.0+
- **API**: REST with optional GraphQL
- **Protocol**: HTTP/2 with fallback to HTTP/1.1
- **Caching**: Redis with edge caching
- **Queue**: Bull for job processing
- **Push**: FCM (Firebase) + APNs (Apple)
- **WebSocket**: Socket.io for real-time
- **Testing**: Jest + Supertest

## Architecture

```
Mobile Apps
    ↓
[Mobile BFF]
    ↓
[CDN/Edge Cache]
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
- PostgreSQL (for sync tracking)
- Firebase account (for push)

### Installation

1. **Navigate to project**
```bash
cd bff/mobile-bff
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

4. **Initialize database**
```bash
npm run db:migrate
```

5. **Start development server**
```bash
npm run dev
```

The BFF will be available at:
- REST API: `http://localhost:4001/api/v1`
- WebSocket: `ws://localhost:4001`
- Health: `http://localhost:4001/health`
- Metrics: `http://localhost:4001/metrics`

### Environment Variables

```bash
# Server Configuration
PORT=4001
NODE_ENV=development
LOG_LEVEL=info

# Microservices
CLAIMS_SERVICE_URL=http://localhost:8001
MEMBER_SERVICE_URL=http://localhost:8002
PROVIDER_SERVICE_URL=http://localhost:8003
BENEFIT_SERVICE_URL=http://localhost:8004

# Redis
REDIS_URL=redis://localhost:6379
CACHE_TTL=300

# Database (for sync tracking)
DATABASE_URL=postgresql://user:pass@localhost:5432/mobile_bff

# Security
JWT_SECRET=your-secret-key
API_KEY_SECRET=your-api-key-secret

# Push Notifications
FCM_SERVER_KEY=your-fcm-key
APNS_KEY_ID=your-apns-key-id
APNS_TEAM_ID=your-team-id

# Rate Limiting
RATE_LIMIT_WINDOW=60000
RATE_LIMIT_MAX=60

# Compression
COMPRESSION_THRESHOLD=1024
```

## Project Structure

```
mobile-bff/
├── src/
│   ├── app.ts                  # Fastify app setup
│   ├── server.ts               # Server entry point
│   ├── routes/
│   │   ├── auth/               # Authentication routes
│   │   ├── claims/             # Claims routes
│   │   ├── members/            # Member routes
│   │   ├── providers/          # Provider routes
│   │   ├── sync/               # Sync endpoints
│   │   └── notifications/      # Push notification routes
│   ├── services/
│   │   ├── aggregator/         # Data aggregation
│   │   ├── cache/              # Caching service
│   │   ├── push/               # Push notifications
│   │   ├── sync/               # Sync management
│   │   └── compression/        # Data compression
│   ├── middleware/
│   │   ├── auth.ts             # JWT validation
│   │   ├── compression.ts      # Response compression
│   │   ├── device-detection.ts # Device capabilities
│   │   └── rate-limit.ts       # Rate limiting
│   ├── models/
│   │   └── sync-state.ts       # Sync tracking
│   ├── utils/
│   │   ├── payload-optimizer.ts # Payload optimization
│   │   └── image-processor.ts  # Image optimization
│   └── websocket/
│       └── handlers.ts         # WebSocket handlers
├── migrations/                 # Database migrations
├── test/                       # Tests
└── package.json
```

## API Design

### Mobile-Optimized Endpoints

#### Lightweight Dashboard
```typescript
// GET /api/v1/member/:id/dashboard-lite
{
  "v": 1, // Version for cache invalidation
  "m": {  // Member data
    "id": "123",
    "n": "John Doe", // Shortened keys
    "p": "Premium"   // Plan name
  },
  "c": [ // Recent claims (max 3)
    {
      "id": "456",
      "s": "approved", // Status
      "a": 500000      // Amount
    }
  ],
  "b": { // Benefits summary
    "u": 75, // Usage percentage
    "r": 25000000 // Remaining
  }
}
```

#### Paginated Claims List
```typescript
// GET /api/v1/claims?page=1&size=10&fields=id,status,amount
@Get('/claims')
async getClaims(
  @Query() query: ClaimsQuery,
  @Headers('x-device-type') deviceType: string
) {
  const pageSize = this.getOptimalPageSize(deviceType);
  
  const claims = await this.claimsService.getClaims({
    ...query,
    size: Math.min(query.size || pageSize, 20)
  });
  
  return {
    data: this.compressClaimsData(claims, query.fields),
    meta: {
      page: query.page,
      hasMore: claims.length === pageSize,
      total: query.includeTotal ? await this.getTotal() : undefined
    }
  };
}
```

### Sync Protocol

```typescript
interface SyncRequest {
  lastSync: string; // ISO timestamp
  entities: {
    claims?: { version: number; ids: string[] };
    members?: { version: number; ids: string[] };
    benefits?: { version: number; ids: string[] };
  };
}

interface SyncResponse {
  timestamp: string;
  changes: {
    claims?: { added: Claim[]; updated: Claim[]; deleted: string[] };
    members?: { added: Member[]; updated: Member[]; deleted: string[] };
    benefits?: { added: Benefit[]; updated: Benefit[]; deleted: string[] };
  };
  nextSync: string; // Suggested next sync time
}

@Post('/sync')
async syncData(@Body() syncRequest: SyncRequest): Promise<SyncResponse> {
  const changes = await this.syncService.getChanges(syncRequest);
  
  return {
    timestamp: new Date().toISOString(),
    changes: this.compressChanges(changes),
    nextSync: this.calculateNextSync(changes)
  };
}
```

### Offline Queue Management

```typescript
@Post('/offline/queue')
async queueOfflineData(
  @Body() data: OfflineData[],
  @Headers('x-device-id') deviceId: string
) {
  const results = [];
  
  for (const item of data) {
    try {
      const result = await this.processOfflineItem(item);
      results.push({ 
        localId: item.localId,
        serverId: result.id,
        status: 'success'
      });
    } catch (error) {
      results.push({
        localId: item.localId,
        status: 'failed',
        error: error.message
      });
    }
  }
  
  return { results };
}
```

## Mobile Optimizations

### Payload Compression

```typescript
class PayloadOptimizer {
  // Minimize JSON keys
  compressKeys(data: any): any {
    const keyMap = {
      'claimNumber': 'cn',
      'memberName': 'mn',
      'providerName': 'pn',
      'totalAmount': 'ta',
      'approvedAmount': 'aa',
      'status': 's',
      'createdAt': 'ca'
    };
    
    return this.transformKeys(data, keyMap);
  }
  
  // Remove null/undefined values
  removeEmpty(obj: any): any {
    return Object.entries(obj).reduce((acc, [key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        acc[key] = typeof value === 'object' 
          ? this.removeEmpty(value) 
          : value;
      }
      return acc;
    }, {});
  }
  
  // Compress arrays of similar objects
  compressArray(items: any[]): any {
    if (items.length === 0) return [];
    
    const keys = Object.keys(items[0]);
    return {
      _k: keys,
      _d: items.map(item => keys.map(k => item[k]))
    };
  }
}
```

### Image Optimization

```typescript
class ImageOptimizer {
  async optimizeForDevice(
    imageUrl: string,
    deviceProfile: DeviceProfile
  ): Promise<string> {
    const params = this.getImageParams(deviceProfile);
    
    // Use image CDN with on-the-fly optimization
    return `${CDN_URL}/optimize?url=${imageUrl}&w=${params.width}&q=${params.quality}&f=${params.format}`;
  }
  
  getImageParams(profile: DeviceProfile) {
    // Adjust based on device capabilities
    if (profile.connectionType === '2g') {
      return { width: 200, quality: 60, format: 'webp' };
    }
    
    if (profile.deviceType === 'tablet') {
      return { width: 800, quality: 85, format: 'webp' };
    }
    
    return { width: 400, quality: 75, format: 'webp' };
  }
}
```

### Batch Request Handler

```typescript
@Post('/batch')
async handleBatch(@Body() requests: BatchRequest[]): Promise<BatchResponse[]> {
  const results = await Promise.allSettled(
    requests.map(req => this.executeRequest(req))
  );
  
  return results.map((result, index) => ({
    id: requests[index].id,
    status: result.status === 'fulfilled' ? 200 : 500,
    data: result.status === 'fulfilled' ? result.value : null,
    error: result.status === 'rejected' ? result.reason : null
  }));
}

private async executeRequest(request: BatchRequest) {
  const handler = this.getHandler(request.method, request.path);
  return handler(request.body, request.headers);
}
```

## Push Notifications

### Notification Service

```typescript
@Injectable()
export class PushNotificationService {
  private fcm: admin.messaging.Messaging;
  private apns: APNsClient;
  
  async sendNotification(notification: Notification) {
    const devices = await this.getDevices(notification.userId);
    
    const results = await Promise.allSettled(
      devices.map(device => this.sendToDevice(device, notification))
    );
    
    // Track delivery
    await this.trackDelivery(notification, results);
  }
  
  private async sendToDevice(device: Device, notification: Notification) {
    if (device.platform === 'ios') {
      return this.sendAPNs(device.token, notification);
    } else {
      return this.sendFCM(device.token, notification);
    }
  }
  
  private async sendFCM(token: string, notification: Notification) {
    const message = {
      token,
      notification: {
        title: notification.title,
        body: notification.body
      },
      data: notification.data,
      android: {
        priority: 'high' as const,
        ttl: 3600 * 1000
      }
    };
    
    return this.fcm.send(message);
  }
}
```

### Push Topics Management

```typescript
@Post('/notifications/subscribe')
async subscribeToTopic(
  @Body() body: { token: string; topics: string[] }
) {
  const results = await Promise.all(
    body.topics.map(topic => 
      admin.messaging().subscribeToTopic(body.token, topic)
    )
  );
  
  return { subscribed: body.topics };
}

@Post('/notifications/broadcast')
async broadcastNotification(
  @Body() notification: BroadcastNotification
) {
  const message = {
    topic: notification.topic,
    notification: {
      title: notification.title,
      body: notification.body
    },
    data: notification.data
  };
  
  return admin.messaging().send(message);
}
```

## Real-time Updates

### WebSocket Handler

```typescript
export class WebSocketHandler {
  private io: Server;
  private connections: Map<string, Socket> = new Map();
  
  initialize(server: http.Server) {
    this.io = new Server(server, {
      cors: { origin: '*' },
      transports: ['websocket', 'polling']
    });
    
    this.io.on('connection', this.handleConnection.bind(this));
  }
  
  private async handleConnection(socket: Socket) {
    const token = socket.handshake.auth.token;
    const user = await this.validateToken(token);
    
    if (!user) {
      socket.disconnect();
      return;
    }
    
    this.connections.set(user.id, socket);
    
    // Join user-specific room
    socket.join(`user:${user.id}`);
    
    // Handle events
    socket.on('subscribe', (channel) => this.subscribe(socket, channel));
    socket.on('unsubscribe', (channel) => this.unsubscribe(socket, channel));
    
    socket.on('disconnect', () => {
      this.connections.delete(user.id);
    });
  }
  
  // Send real-time updates
  async notifyUser(userId: string, event: string, data: any) {
    this.io.to(`user:${userId}`).emit(event, data);
  }
}
```

## Caching Strategy

### Multi-Layer Caching

```typescript
@Injectable()
export class CacheService {
  private memoryCache: LRUCache<string, any>;
  private redisCache: Redis;
  
  constructor() {
    this.memoryCache = new LRUCache({
      max: 500,
      ttl: 1000 * 60 * 5 // 5 minutes
    });
    
    this.redisCache = new Redis(process.env.REDIS_URL);
  }
  
  async get(key: string): Promise<any> {
    // L1: Memory cache
    const memCached = this.memoryCache.get(key);
    if (memCached) return memCached;
    
    // L2: Redis cache
    const redisCached = await this.redisCache.get(key);
    if (redisCached) {
      const data = JSON.parse(redisCached);
      this.memoryCache.set(key, data);
      return data;
    }
    
    return null;
  }
  
  async set(key: string, value: any, ttl: number = 3600) {
    // Set in both caches
    this.memoryCache.set(key, value);
    await this.redisCache.setex(key, ttl, JSON.stringify(value));
  }
  
  // Cache with stale-while-revalidate
  async getWithSWR(
    key: string,
    fetcher: () => Promise<any>,
    ttl: number = 3600,
    staleTime: number = 300
  ) {
    const cached = await this.get(key);
    
    if (cached) {
      const age = Date.now() - cached._timestamp;
      
      if (age < ttl * 1000) {
        return cached.data;
      }
      
      // Return stale data and refresh in background
      if (age < (ttl + staleTime) * 1000) {
        this.refreshInBackground(key, fetcher, ttl);
        return cached.data;
      }
    }
    
    // Fetch fresh data
    const data = await fetcher();
    await this.set(key, { data, _timestamp: Date.now() }, ttl);
    return data;
  }
}
```

## Performance Monitoring

### Request Tracking

```typescript
class PerformanceMonitor {
  trackRequest(req: FastifyRequest, reply: FastifyReply) {
    const start = Date.now();
    
    reply.header('X-Request-ID', generateRequestId());
    
    req.log.info({
      method: req.method,
      url: req.url,
      device: req.headers['x-device-type'],
      version: req.headers['x-app-version']
    });
    
    reply.addHook('onSend', (request, reply, payload, done) => {
      const duration = Date.now() - start;
      
      metrics.recordHttpDuration(
        req.method,
        req.routerPath,
        reply.statusCode,
        duration
      );
      
      req.log.info({
        duration,
        statusCode: reply.statusCode,
        responseSize: Buffer.byteLength(payload)
      });
      
      done();
    });
  }
}
```

## Security

### API Key Authentication

```typescript
class ApiKeyAuth {
  async validateApiKey(apiKey: string, deviceId: string): Promise<boolean> {
    const hash = crypto
      .createHmac('sha256', process.env.API_KEY_SECRET)
      .update(`${deviceId}:${apiKey}`)
      .digest('hex');
    
    const stored = await this.redis.get(`api_key:${deviceId}`);
    
    return stored === hash;
  }
  
  async generateApiKey(deviceId: string): Promise<string> {
    const apiKey = crypto.randomBytes(32).toString('hex');
    const hash = crypto
      .createHmac('sha256', process.env.API_KEY_SECRET)
      .update(`${deviceId}:${apiKey}`)
      .digest('hex');
    
    await this.redis.set(`api_key:${deviceId}`, hash);
    
    return apiKey;
  }
}
```

### Certificate Pinning Support

```typescript
app.addHook('onRequest', async (request, reply) => {
  const pin = request.headers['x-certificate-pin'];
  
  if (pin && pin !== process.env.EXPECTED_CERT_PIN) {
    reply.code(403).send({ error: 'Certificate pin mismatch' });
  }
});
```

## Testing

### Unit Tests

```typescript
describe('PayloadOptimizer', () => {
  let optimizer: PayloadOptimizer;
  
  beforeEach(() => {
    optimizer = new PayloadOptimizer();
  });
  
  describe('compressKeys', () => {
    it('should compress object keys', () => {
      const input = {
        claimNumber: 'CLM-001',
        memberName: 'John Doe',
        totalAmount: 500000
      };
      
      const output = optimizer.compressKeys(input);
      
      expect(output).toEqual({
        cn: 'CLM-001',
        mn: 'John Doe',
        ta: 500000
      });
    });
  });
  
  describe('compressArray', () => {
    it('should compress array of objects', () => {
      const input = [
        { id: 1, name: 'A', value: 100 },
        { id: 2, name: 'B', value: 200 }
      ];
      
      const output = optimizer.compressArray(input);
      
      expect(output).toEqual({
        _k: ['id', 'name', 'value'],
        _d: [[1, 'A', 100], [2, 'B', 200]]
      });
    });
  });
});
```

### Load Testing

```javascript
// k6 load test
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 200 },
    { duration: '5m', target: 200 },
    { duration: '2m', target: 0 }
  ],
  thresholds: {
    http_req_duration: ['p(95)<500']
  }
};

export default function() {
  const response = http.get('http://localhost:4001/api/v1/claims?page=1&size=10');
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500
  });
}
```

## Deployment

### Docker

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
EXPOSE 4001
CMD ["node", "dist/server.js"]
```

### Kubernetes with HPA

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: mobile-bff-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: mobile-bff
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
```

## Monitoring

### Mobile-Specific Metrics

```typescript
class MobileMetrics {
  private prometheus = new PrometheusClient();
  
  constructor() {
    // Device type distribution
    this.deviceTypeCounter = new Counter({
      name: 'mobile_requests_by_device',
      help: 'Requests by device type',
      labelNames: ['device_type', 'os_version']
    });
    
    // Network type distribution
    this.networkTypeCounter = new Counter({
      name: 'mobile_requests_by_network',
      help: 'Requests by network type',
      labelNames: ['network_type']
    });
    
    // Payload size histogram
    this.payloadSizeHistogram = new Histogram({
      name: 'mobile_response_size_bytes',
      help: 'Response payload size in bytes',
      buckets: [100, 500, 1000, 5000, 10000, 50000]
    });
    
    // Sync operations
    this.syncDurationHistogram = new Histogram({
      name: 'mobile_sync_duration_seconds',
      help: 'Sync operation duration',
      labelNames: ['entity_type']
    });
  }
}
```

## Troubleshooting

### Common Issues

1. **High payload sizes**
   - Review compression settings
   - Check field selection in queries
   - Enable pagination for large datasets

2. **Sync conflicts**
   - Review conflict resolution strategy
   - Check timestamp synchronization
   - Validate offline queue processing

3. **Push notification failures**
   - Verify FCM/APNs credentials
   - Check device token validity
   - Review notification payload size

4. **WebSocket disconnections**
   - Check keepalive settings
   - Review proxy timeouts
   - Monitor connection stability

## Support

- **Documentation**: [Full docs](../../docs)
- **Mobile Team**: mobile-backend@claims-askes.com
- **On-call**: Use PagerDuty for urgent issues

## License

Proprietary - All rights reserved