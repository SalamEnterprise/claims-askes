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

- **Runtime**: Python 3.11+
- **Framework**: FastAPI 0.104+ (for performance)
- **Async Runtime**: uvloop for enhanced async performance
- **API**: REST with optional GraphQL (Strawberry)
- **Protocol**: HTTP/2 with fallback to HTTP/1.1
- **Caching**: Redis with edge caching
- **Queue**: Celery with RabbitMQ
- **Push**: FCM (Firebase) + APNs (Apple) via PyFCM/PyAPNs2
- **WebSocket**: python-socketio for real-time
- **Database**: PostgreSQL with SQLAlchemy 2.0
- **Testing**: pytest + httpx + pytest-asyncio

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

- Python 3.11+
- Redis 7+
- PostgreSQL 15+ (for sync tracking)
- Firebase account (for push)
- Poetry or pip

### Installation

1. **Navigate to project**
```bash
cd bff/mobile-bff
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
# Or using Poetry
poetry install
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**
```bash
alembic upgrade head
```

6. **Start development server**
```bash
uvicorn src.main:app --reload --port 4001
# Or with Hypercorn for HTTP/2 support
hypercorn src.main:app --bind 0.0.0.0:4001 --reload
```

The BFF will be available at:
- REST API: `http://localhost:4001/api/v1`
- WebSocket: `ws://localhost:4001/socket.io`
- Health: `http://localhost:4001/health`
- Metrics: `http://localhost:4001/metrics`
- API Docs: `http://localhost:4001/docs`

### Environment Variables

```bash
# Server Configuration
PORT=4001
ENVIRONMENT=development
LOG_LEVEL=info
WORKERS=4

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
APNS_CERT_PATH=/path/to/cert.pem

# Rate Limiting
RATE_LIMIT_WINDOW=60
RATE_LIMIT_MAX=60

# Compression
COMPRESSION_THRESHOLD=1024
```

## Project Structure

```
mobile-bff/
├── src/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app setup
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── auth.py         # Authentication routes
│   │   │   ├── claims.py       # Claims routes
│   │   │   ├── members.py      # Member routes
│   │   │   ├── providers.py    # Provider routes
│   │   │   ├── sync.py         # Sync endpoints
│   │   │   └── notifications.py # Push notification routes
│   │   └── dependencies.py     # Dependency injection
│   ├── services/
│   │   ├── __init__.py
│   │   ├── aggregator.py       # Data aggregation
│   │   ├── cache.py            # Caching service
│   │   ├── push.py             # Push notifications
│   │   ├── sync.py             # Sync management
│   │   └── compression.py      # Data compression
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py             # JWT validation
│   │   ├── compression.py      # Response compression
│   │   ├── device_detection.py # Device capabilities
│   │   └── rate_limit.py       # Rate limiting
│   ├── models/
│   │   ├── __init__.py
│   │   └── sync_state.py       # Sync tracking models
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── mobile.py           # Pydantic schemas
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── payload_optimizer.py # Payload optimization
│   │   └── image_processor.py  # Image optimization
│   └── websocket/
│       ├── __init__.py
│       └── handlers.py         # WebSocket handlers
├── migrations/                  # Alembic migrations
├── tests/                       # Tests
├── requirements.txt
└── pyproject.toml
```

## API Design

### Mobile-Optimized Endpoints

#### Lightweight Dashboard

```python
# GET /api/v1/member/{member_id}/dashboard-lite
from fastapi import APIRouter, Depends
from typing import Dict, Any

router = APIRouter()

@router.get("/member/{member_id}/dashboard-lite")
async def get_dashboard_lite(
    member_id: str,
    device_type: str = Header(None, alias="X-Device-Type")
) -> Dict[str, Any]:
    """Return compressed dashboard data for mobile"""
    
    # Use shortened keys for mobile
    return {
        "v": 1,  # Version for cache invalidation
        "m": {   # Member data
            "id": member_id,
            "n": "John Doe",  # Shortened keys
            "p": "Premium"    # Plan name
        },
        "c": [  # Recent claims (max 3)
            {
                "id": "456",
                "s": "approved",  # Status
                "a": 500000       # Amount
            }
        ],
        "b": {  # Benefits summary
            "u": 75,  # Usage percentage
            "r": 25000000  # Remaining
        }
    }
```

#### Paginated Claims List

```python
from fastapi import Query
from typing import Optional, List
from pydantic import BaseModel

class ClaimsQuery(BaseModel):
    page: int = 1
    size: int = 10
    fields: Optional[str] = None
    include_total: bool = False

@router.get("/claims")
async def get_claims(
    query: ClaimsQuery = Depends(),
    device_type: str = Header(None, alias="X-Device-Type")
):
    """Get paginated claims with field selection"""
    
    # Optimize page size based on device
    page_size = get_optimal_page_size(device_type)
    query.size = min(query.size or page_size, 20)
    
    claims = await claims_service.get_claims(query)
    
    return {
        "data": compress_claims_data(claims, query.fields),
        "meta": {
            "page": query.page,
            "hasMore": len(claims) == query.size,
            "total": await get_total() if query.include_total else None
        }
    }
```

### Sync Protocol

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional

class EntitySync(BaseModel):
    version: int
    ids: List[str]

class SyncRequest(BaseModel):
    last_sync: datetime
    entities: Dict[str, EntitySync]

class SyncChanges(BaseModel):
    added: List[Dict]
    updated: List[Dict]
    deleted: List[str]

class SyncResponse(BaseModel):
    timestamp: datetime
    changes: Dict[str, SyncChanges]
    next_sync: datetime

@router.post("/sync")
async def sync_data(sync_request: SyncRequest) -> SyncResponse:
    """Sync data changes since last sync"""
    
    changes = await sync_service.get_changes(sync_request)
    
    return SyncResponse(
        timestamp=datetime.utcnow(),
        changes=compress_changes(changes),
        next_sync=calculate_next_sync(changes)
    )
```

### Offline Queue Management

```python
from typing import List
from pydantic import BaseModel

class OfflineData(BaseModel):
    local_id: str
    entity_type: str
    operation: str
    data: Dict[str, Any]
    timestamp: datetime

class QueueResult(BaseModel):
    local_id: str
    server_id: Optional[str] = None
    status: str
    error: Optional[str] = None

@router.post("/offline/queue")
async def queue_offline_data(
    data: List[OfflineData],
    device_id: str = Header(..., alias="X-Device-ID")
) -> Dict[str, List[QueueResult]]:
    """Process offline queue data"""
    
    results = []
    
    for item in data:
        try:
            result = await process_offline_item(item)
            results.append(QueueResult(
                local_id=item.local_id,
                server_id=result.id,
                status="success"
            ))
        except Exception as e:
            results.append(QueueResult(
                local_id=item.local_id,
                status="failed",
                error=str(e)
            ))
    
    return {"results": results}
```

## Mobile Optimizations

### Payload Compression

```python
# src/utils/payload_optimizer.py
from typing import Dict, List, Any

class PayloadOptimizer:
    """Optimize payloads for mobile consumption"""
    
    # Key mapping for compression
    KEY_MAP = {
        'claim_number': 'cn',
        'member_name': 'mn',
        'provider_name': 'pn',
        'total_amount': 'ta',
        'approved_amount': 'aa',
        'status': 's',
        'created_at': 'ca'
    }
    
    def compress_keys(self, data: Any) -> Any:
        """Minimize JSON keys"""
        if isinstance(data, dict):
            return {
                self.KEY_MAP.get(k, k): self.compress_keys(v)
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [self.compress_keys(item) for item in data]
        return data
    
    def remove_empty(self, obj: Dict) -> Dict:
        """Remove null/undefined values"""
        return {
            k: self.remove_empty(v) if isinstance(v, dict) else v
            for k, v in obj.items()
            if v is not None and v != ''
        }
    
    def compress_array(self, items: List[Dict]) -> Dict:
        """Compress arrays of similar objects"""
        if not items:
            return []
        
        keys = list(items[0].keys())
        return {
            '_k': keys,
            '_d': [[item.get(k) for k in keys] for item in items]
        }
```

### Image Optimization

```python
# src/utils/image_processor.py
from enum import Enum
from typing import Optional
from dataclasses import dataclass

class ConnectionType(Enum):
    WIFI = "wifi"
    CELLULAR_4G = "4g"
    CELLULAR_3G = "3g"
    CELLULAR_2G = "2g"

@dataclass
class DeviceProfile:
    device_type: str
    connection_type: ConnectionType
    screen_density: float
    screen_width: int

class ImageOptimizer:
    """Optimize images for mobile devices"""
    
    CDN_URL = "https://cdn.claims-askes.com"
    
    def optimize_for_device(
        self,
        image_url: str,
        device_profile: DeviceProfile
    ) -> str:
        """Generate optimized image URL for device"""
        params = self._get_image_params(device_profile)
        
        return (
            f"{self.CDN_URL}/optimize?"
            f"url={image_url}&"
            f"w={params['width']}&"
            f"q={params['quality']}&"
            f"f={params['format']}"
        )
    
    def _get_image_params(self, profile: DeviceProfile) -> Dict[str, Any]:
        """Calculate optimal image parameters"""
        
        # Adjust based on connection type
        if profile.connection_type == ConnectionType.CELLULAR_2G:
            return {'width': 200, 'quality': 60, 'format': 'webp'}
        
        # Adjust based on device type
        if profile.device_type == 'tablet':
            return {'width': 800, 'quality': 85, 'format': 'webp'}
        
        # Default for phones
        return {'width': 400, 'quality': 75, 'format': 'webp'}
```

### Batch Request Handler

```python
from typing import List, Any
from pydantic import BaseModel

class BatchRequest(BaseModel):
    id: str
    method: str
    path: str
    body: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None

class BatchResponse(BaseModel):
    id: str
    status: int
    data: Optional[Any] = None
    error: Optional[str] = None

@router.post("/batch")
async def handle_batch(
    requests: List[BatchRequest]
) -> List[BatchResponse]:
    """Process multiple requests in a single call"""
    
    import asyncio
    
    tasks = [execute_request(req) for req in requests]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    responses = []
    for req, result in zip(requests, results):
        if isinstance(result, Exception):
            responses.append(BatchResponse(
                id=req.id,
                status=500,
                error=str(result)
            ))
        else:
            responses.append(BatchResponse(
                id=req.id,
                status=200,
                data=result
            ))
    
    return responses
```

## Push Notifications

### Notification Service

```python
# src/services/push.py
from pyfcm import FCMNotification
from apns2.client import APNsClient
from apns2.payload import Payload
from typing import List, Dict, Any
import asyncio

class PushNotificationService:
    """Manage push notifications for mobile devices"""
    
    def __init__(self, fcm_key: str, apns_config: Dict):
        self.fcm = FCMNotification(api_key=fcm_key)
        self.apns = APNsClient(
            credentials=apns_config['cert_path'],
            use_sandbox=apns_config.get('sandbox', False)
        )
    
    async def send_notification(
        self,
        user_id: str,
        title: str,
        body: str,
        data: Optional[Dict] = None
    ):
        """Send notification to user's devices"""
        
        devices = await self.get_user_devices(user_id)
        
        tasks = [
            self.send_to_device(device, title, body, data)
            for device in devices
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Track delivery
        await self.track_delivery(user_id, results)
    
    async def send_to_device(
        self,
        device: Dict,
        title: str,
        body: str,
        data: Optional[Dict] = None
    ):
        """Send notification to specific device"""
        
        if device['platform'] == 'ios':
            return await self.send_apns(
                device['token'],
                title,
                body,
                data
            )
        else:
            return await self.send_fcm(
                device['token'],
                title,
                body,
                data
            )
    
    async def send_fcm(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[Dict] = None
    ):
        """Send FCM notification"""
        
        result = self.fcm.notify_single_device(
            registration_id=token,
            message_title=title,
            message_body=body,
            data_message=data,
            content_available=True,
            priority="high"
        )
        
        return result
    
    async def send_apns(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[Dict] = None
    ):
        """Send APNs notification"""
        
        payload = Payload(
            alert={"title": title, "body": body},
            sound="default",
            badge=1,
            custom=data
        )
        
        response = await asyncio.to_thread(
            self.apns.send_notification,
            token,
            payload
        )
        
        return response
```

### Push Topics Management

```python
@router.post("/notifications/subscribe")
async def subscribe_to_topics(
    token: str = Body(...),
    topics: List[str] = Body(...)
):
    """Subscribe device to notification topics"""
    
    results = []
    for topic in topics:
        result = await push_service.subscribe_to_topic(token, topic)
        results.append({"topic": topic, "success": result})
    
    return {"subscribed": results}

@router.post("/notifications/broadcast")
async def broadcast_notification(
    topic: str = Body(...),
    title: str = Body(...),
    body: str = Body(...),
    data: Optional[Dict] = Body(None)
):
    """Broadcast notification to topic subscribers"""
    
    result = await push_service.send_to_topic(
        topic=topic,
        title=title,
        body=body,
        data=data
    )
    
    return {"sent": result['success'], "failed": result['failure']}
```

## Real-time Updates

### WebSocket Handler

```python
# src/websocket/handlers.py
import socketio
from typing import Dict, Set
import jwt

sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*'
)

# Track connections
connections: Dict[str, Set[str]] = {}

@sio.event
async def connect(sid, environ, auth):
    """Handle WebSocket connection"""
    
    try:
        # Validate token
        token = auth.get('token')
        user = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        
        # Store connection
        if user['id'] not in connections:
            connections[user['id']] = set()
        connections[user['id']].add(sid)
        
        # Join user room
        await sio.enter_room(sid, f"user:{user['id']}")
        
        await sio.emit('connected', {'status': 'ok'}, to=sid)
        
    except Exception as e:
        await sio.disconnect(sid)

@sio.event
async def disconnect(sid):
    """Handle disconnection"""
    
    # Remove from connections
    for user_id, sids in connections.items():
        if sid in sids:
            sids.remove(sid)
            break

@sio.event
async def subscribe(sid, data):
    """Subscribe to channel"""
    channel = data.get('channel')
    await sio.enter_room(sid, channel)
    await sio.emit('subscribed', {'channel': channel}, to=sid)

@sio.event
async def unsubscribe(sid, data):
    """Unsubscribe from channel"""
    channel = data.get('channel')
    await sio.leave_room(sid, channel)
    await sio.emit('unsubscribed', {'channel': channel}, to=sid)

async def notify_user(user_id: str, event: str, data: Any):
    """Send real-time update to user"""
    await sio.emit(event, data, room=f"user:{user_id}")
```

## Caching Strategy

### Multi-Layer Caching

```python
# src/services/cache.py
import redis.asyncio as redis
from cachetools import TTLCache
import json
from typing import Any, Optional
from datetime import datetime, timedelta

class CacheService:
    """Multi-layer caching service"""
    
    def __init__(self, redis_url: str):
        # L1: Memory cache
        self.memory_cache = TTLCache(maxsize=500, ttl=300)
        
        # L2: Redis cache
        self.redis_cache = redis.from_url(redis_url)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get from cache (memory -> redis)"""
        
        # Check memory cache
        if key in self.memory_cache:
            return self.memory_cache[key]
        
        # Check Redis cache
        value = await self.redis_cache.get(key)
        if value:
            data = json.loads(value)
            self.memory_cache[key] = data
            return data
        
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600
    ):
        """Set in both caches"""
        
        # Set in memory
        self.memory_cache[key] = value
        
        # Set in Redis
        await self.redis_cache.setex(
            key,
            ttl,
            json.dumps(value, default=str)
        )
    
    async def get_with_swr(
        self,
        key: str,
        fetcher,
        ttl: int = 3600,
        stale_time: int = 300
    ):
        """Get with stale-while-revalidate pattern"""
        
        cached = await self.get(key)
        
        if cached:
            age = (datetime.utcnow() - datetime.fromisoformat(
                cached.get('_timestamp', '1970-01-01')
            )).total_seconds()
            
            if age < ttl:
                return cached['data']
            
            # Return stale data and refresh in background
            if age < (ttl + stale_time):
                asyncio.create_task(
                    self._refresh_in_background(key, fetcher, ttl)
                )
                return cached['data']
        
        # Fetch fresh data
        data = await fetcher()
        await self.set(
            key,
            {'data': data, '_timestamp': datetime.utcnow().isoformat()},
            ttl
        )
        return data
    
    async def _refresh_in_background(self, key: str, fetcher, ttl: int):
        """Refresh cache in background"""
        try:
            data = await fetcher()
            await self.set(
                key,
                {'data': data, '_timestamp': datetime.utcnow().isoformat()},
                ttl
            )
        except Exception:
            pass  # Silent fail for background refresh
```

## Performance Monitoring

### Request Tracking

```python
# src/middleware/monitoring.py
import time
from fastapi import Request, Response
import logging
from prometheus_client import Counter, Histogram

# Metrics
request_count = Counter(
    'mobile_bff_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'mobile_bff_request_duration_seconds',
    'Request duration',
    ['method', 'endpoint']
)

response_size = Histogram(
    'mobile_bff_response_size_bytes',
    'Response size in bytes',
    ['endpoint', 'device_type']
)

async def monitoring_middleware(request: Request, call_next):
    """Track request metrics"""
    
    start_time = time.time()
    
    # Add request ID
    request_id = generate_request_id()
    request.state.request_id = request_id
    
    # Log request
    logger.info(f"Request started", extra={
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "device": request.headers.get("x-device-type")
    })
    
    # Process request
    response = await call_next(request)
    
    # Calculate metrics
    duration = time.time() - start_time
    
    # Record metrics
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    # Add response headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time"] = f"{duration:.3f}"
    
    # Log response
    logger.info(f"Request completed", extra={
        "request_id": request_id,
        "status": response.status_code,
        "duration": duration
    })
    
    return response
```

## Security

### API Key Authentication

```python
# src/middleware/auth.py
import hashlib
import hmac
from fastapi import HTTPException, Security, Depends
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

class ApiKeyAuth:
    """API key authentication for mobile apps"""
    
    def __init__(self, secret: str):
        self.secret = secret
    
    async def validate_api_key(
        self,
        api_key: str = Security(api_key_header),
        device_id: str = Header(..., alias="X-Device-ID")
    ) -> bool:
        """Validate API key for device"""
        
        # Generate expected hash
        expected = hmac.new(
            self.secret.encode(),
            f"{device_id}:{api_key}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Get stored hash
        stored = await redis_client.get(f"api_key:{device_id}")
        
        if not stored or stored != expected:
            raise HTTPException(
                status_code=403,
                detail="Invalid API key"
            )
        
        return True
    
    async def generate_api_key(self, device_id: str) -> str:
        """Generate new API key for device"""
        
        import secrets
        
        api_key = secrets.token_hex(32)
        
        # Store hash
        key_hash = hmac.new(
            self.secret.encode(),
            f"{device_id}:{api_key}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        await redis_client.set(
            f"api_key:{device_id}",
            key_hash,
            ex=86400 * 30  # 30 days
        )
        
        return api_key
```

## Testing

### Unit Tests

```python
# tests/test_payload_optimizer.py
import pytest
from src.utils.payload_optimizer import PayloadOptimizer

class TestPayloadOptimizer:
    
    @pytest.fixture
    def optimizer(self):
        return PayloadOptimizer()
    
    def test_compress_keys(self, optimizer):
        """Test key compression"""
        input_data = {
            'claim_number': 'CLM-001',
            'member_name': 'John Doe',
            'total_amount': 500000
        }
        
        output = optimizer.compress_keys(input_data)
        
        assert output == {
            'cn': 'CLM-001',
            'mn': 'John Doe',
            'ta': 500000
        }
    
    def test_compress_array(self, optimizer):
        """Test array compression"""
        input_data = [
            {'id': 1, 'name': 'A', 'value': 100},
            {'id': 2, 'name': 'B', 'value': 200}
        ]
        
        output = optimizer.compress_array(input_data)
        
        assert output == {
            '_k': ['id', 'name', 'value'],
            '_d': [[1, 'A', 100], [2, 'B', 200]]
        }
    
    def test_remove_empty(self, optimizer):
        """Test empty value removal"""
        input_data = {
            'id': 1,
            'name': 'Test',
            'empty': None,
            'blank': '',
            'zero': 0
        }
        
        output = optimizer.remove_empty(input_data)
        
        assert output == {
            'id': 1,
            'name': 'Test',
            'zero': 0
        }
```

### Integration Tests

```python
# tests/test_api.py
import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_dashboard_lite():
    """Test lightweight dashboard endpoint"""
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/member/123/dashboard-lite",
            headers={"X-Device-Type": "phone"}
        )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check compressed keys
    assert 'v' in data
    assert 'm' in data
    assert 'c' in data
    assert 'b' in data

@pytest.mark.asyncio
async def test_batch_requests():
    """Test batch request processing"""
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/batch",
            json=[
                {
                    "id": "1",
                    "method": "GET",
                    "path": "/api/v1/claims/123"
                },
                {
                    "id": "2",
                    "method": "GET",
                    "path": "/api/v1/members/456"
                }
            ]
        )
    
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 2
    assert all(r['id'] in ['1', '2'] for r in results)
```

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 4001

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "4001"]
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

```python
# src/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Device metrics
device_type_counter = Counter(
    'mobile_requests_by_device',
    'Requests by device type',
    ['device_type', 'os_version']
)

network_type_counter = Counter(
    'mobile_requests_by_network',
    'Requests by network type',
    ['network_type']
)

# Performance metrics
payload_size_histogram = Histogram(
    'mobile_response_size_bytes',
    'Response payload size in bytes',
    buckets=[100, 500, 1000, 5000, 10000, 50000]
)

sync_duration_histogram = Histogram(
    'mobile_sync_duration_seconds',
    'Sync operation duration',
    ['entity_type']
)

# Push notification metrics
push_sent_counter = Counter(
    'mobile_push_notifications_sent',
    'Push notifications sent',
    ['platform', 'status']
)

# WebSocket metrics
websocket_connections = Gauge(
    'mobile_websocket_connections',
    'Active WebSocket connections'
)
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