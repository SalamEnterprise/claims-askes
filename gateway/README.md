# API Gateway Documentation

## Overview

The API Gateway serves as the single entry point for all client requests to the Claims-Askes platform. It provides essential cross-cutting concerns including authentication, rate limiting, request routing, protocol translation, and API versioning.

## Architecture

```
                 Internet
                     │
              ┌─────────────┐
              │ Load Balancer│
              └─────────────┘
                     │
          ┌─────────────────────┐
          │    API Gateway       │
          │   (Kong/NGINX)       │
          └─────────────────────┘
                     │
     ┌─────────────────────────────────┐
     │                                   │
┌──────────┐  ┌────────────┐  ┌────────────┐
│ Web BFF  │  │ Mobile BFF │  │ Admin API  │
└──────────┘  └────────────┘  └────────────┘
```

## Technology Stack

### Primary Gateway: Kong

- **Version**: Kong 3.4+
- **Database**: PostgreSQL (for configuration)
- **Deployment**: Kubernetes Ingress Controller
- **Plugins**: Custom and community plugins

### Alternative: NGINX Plus

- **Version**: NGINX Plus R30+
- **Module**: njs for custom logic
- **Configuration**: Dynamic upstream configuration
- **Monitoring**: NGINX Amplify

## Core Features

### 1. Authentication & Authorization

- **JWT Validation**: Verify and decode JWT tokens
- **OAuth 2.0**: Support for authorization code flow
- **API Key Management**: For service-to-service communication
- **RBAC**: Role-based access control
- **Session Management**: Sticky sessions for stateful services

### 2. Rate Limiting

- **Global Rate Limiting**: Platform-wide limits
- **Per-User Rate Limiting**: Based on JWT claims
- **Per-API Rate Limiting**: Different limits per endpoint
- **Distributed Rate Limiting**: Using Redis
- **Adaptive Rate Limiting**: Based on system load

### 3. Request Routing

- **Path-based Routing**: Route by URL path
- **Header-based Routing**: Route by custom headers
- **Host-based Routing**: Multiple domains support
- **Version Routing**: API versioning support
- **Canary Deployments**: Percentage-based routing

### 4. Security

- **TLS Termination**: SSL/TLS handling
- **WAF Integration**: Web Application Firewall
- **DDoS Protection**: Rate limiting and blacklisting
- **CORS Handling**: Cross-origin resource sharing
- **Input Validation**: Request schema validation

### 5. Observability

- **Request Logging**: Comprehensive access logs
- **Metrics Collection**: Prometheus metrics
- **Distributed Tracing**: OpenTelemetry integration
- **Health Checks**: Upstream service monitoring
- **Alerting**: Integration with monitoring systems

## Configuration

### Kong Configuration

```yaml
# gateway/kong/kong.yml
_format_version: "3.0"
_transform: true

services:
  # Web BFF Service
  - name: web-bff
    url: http://web-bff.claims-askes.svc.cluster.local:4000
    retries: 3
    connect_timeout: 5000
    write_timeout: 60000
    read_timeout: 60000
    routes:
      - name: web-bff-route
        paths:
          - /api/web
        strip_path: true
        preserve_host: true
    plugins:
      - name: jwt
        config:
          key_claim_name: iss
          claims_to_verify:
            - exp
      - name: rate-limiting
        config:
          minute: 100
          hour: 1000
          policy: redis
          redis_host: redis.cache.svc.cluster.local
      - name: cors
        config:
          origins:
            - https://claims-askes.com
            - https://app.claims-askes.com
          methods:
            - GET
            - POST
            - PUT
            - DELETE
            - OPTIONS
          headers:
            - Accept
            - Accept-Version
            - Content-Length
            - Content-Type
            - Authorization
          exposed_headers:
            - X-Auth-Token
          credentials: true
          max_age: 3600

  # Mobile BFF Service
  - name: mobile-bff
    url: http://mobile-bff.claims-askes.svc.cluster.local:4001
    routes:
      - name: mobile-bff-route
        paths:
          - /api/mobile
        strip_path: true
    plugins:
      - name: jwt
      - name: rate-limiting
        config:
          second: 10
          minute: 60
          policy: redis
      - name: request-transformer
        config:
          add:
            headers:
              - X-Mobile-Request:true
      - name: response-transformer
        config:
          add:
            headers:
              - Cache-Control:private, max-age=300

  # Admin API Service
  - name: admin-api
    url: http://admin-gateway.claims-askes.svc.cluster.local:5000
    routes:
      - name: admin-api-route
        paths:
          - /api/admin
        strip_path: true
    plugins:
      - name: jwt
        config:
          roles_claim: roles
          roles:
            - admin
            - super_admin
      - name: ip-restriction
        config:
          allow:
            - 10.0.0.0/8
            - 192.168.0.0/16
      - name: request-size-limiting
        config:
          allowed_payload_size: 10
          size_unit: megabytes

# Global Plugins
plugins:
  - name: prometheus
    config:
      status_code_metrics: true
      latency_metrics: true
      bandwidth_metrics: true
      upstream_health_metrics: true
  
  - name: zipkin
    config:
      http_endpoint: http://zipkin.monitoring.svc.cluster.local:9411/api/v2/spans
      sample_ratio: 0.01
  
  - name: syslog
    config:
      log_level: info
      server_errors_as_warnings: true
      client_errors_as_warnings: false

# Upstreams Configuration
upstreams:
  - name: web-bff-upstream
    algorithm: round-robin
    targets:
      - target: web-bff-1.claims-askes.svc.cluster.local:4000
        weight: 100
      - target: web-bff-2.claims-askes.svc.cluster.local:4000
        weight: 100
    healthchecks:
      active:
        healthy:
          interval: 5
          successes: 2
        unhealthy:
          interval: 5
          tcp_failures: 2
          http_failures: 2
```

### NGINX Configuration

```nginx
# gateway/nginx/nginx.conf
upstream web_bff {
    least_conn;
    server web-bff-1.claims-askes.local:4000 max_fails=3 fail_timeout=30s;
    server web-bff-2.claims-askes.local:4000 max_fails=3 fail_timeout=30s;
    
    # Health check
    check interval=5000 rise=2 fall=3 timeout=4000 type=http;
    check_http_send "GET /health HTTP/1.0\r\n\r\n";
    check_http_expect_alive http_2xx http_3xx;
}

upstream mobile_bff {
    least_conn;
    server mobile-bff-1.claims-askes.local:4001;
    server mobile-bff-2.claims-askes.local:4001;
}

# Rate limiting zones
limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
limit_req_zone $jwt_claim_sub zone=per_user:10m rate=100r/m;
limit_req_zone $uri zone=per_endpoint:10m rate=1000r/m;

# Cache configuration
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g inactive=60m use_temp_path=off;

server {
    listen 443 ssl http2;
    server_name api.claims-askes.com;
    
    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # CORS Configuration
    set $cors_origin "";
    if ($http_origin ~* ^https?://(.*\.)?(claims-askes\.com|localhost:3000)$) {
        set $cors_origin $http_origin;
    }
    
    add_header Access-Control-Allow-Origin $cors_origin always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Authorization, Content-Type, X-Requested-With" always;
    add_header Access-Control-Allow-Credentials "true" always;
    
    # Handle preflight requests
    if ($request_method = OPTIONS) {
        return 204;
    }
    
    # Rate limiting
    limit_req zone=general burst=20 nodelay;
    limit_req zone=per_user burst=50;
    
    # Request size limit
    client_max_body_size 10M;
    
    # Timeouts
    proxy_connect_timeout 10s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
    
    # Web BFF Routes
    location /api/web/ {
        # JWT Validation
        auth_jwt "Protected API";
        auth_jwt_key_file /etc/nginx/jwt/public.pem;
        
        # Rate limiting for specific endpoints
        location /api/web/claims/submit {
            limit_req zone=per_endpoint burst=5;
            proxy_pass http://web_bff/claims/submit;
        }
        
        proxy_pass http://web_bff/;
        
        # Caching for GET requests
        proxy_cache api_cache;
        proxy_cache_methods GET HEAD;
        proxy_cache_valid 200 5m;
        proxy_cache_valid 404 1m;
        proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;
        proxy_cache_bypass $http_cache_control;
        add_header X-Cache-Status $upstream_cache_status;
        
        # Proxy headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Request-ID $request_id;
    }
    
    # Mobile BFF Routes
    location /api/mobile/ {
        auth_jwt "Protected API";
        auth_jwt_key_file /etc/nginx/jwt/public.pem;
        
        # Mobile-specific optimizations
        gzip on;
        gzip_types application/json;
        gzip_min_length 1000;
        
        proxy_pass http://mobile_bff/;
        
        # Aggressive caching for mobile
        proxy_cache api_cache;
        proxy_cache_valid 200 10m;
        proxy_cache_lock on;
        
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Device-Type $http_x_device_type;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    # Metrics endpoint (internal only)
    location /metrics {
        allow 10.0.0.0/8;
        deny all;
        
        # Prometheus metrics
        content_by_lua_block {
            local prometheus = require("prometheus")
            prometheus:collect()
        }
    }
    
    # Status page (internal only)
    location /nginx_status {
        stub_status;
        allow 10.0.0.0/8;
        deny all;
    }
}
```

## Custom Plugins

### JWT Claims Enrichment Plugin

```lua
-- gateway/plugins/jwt-enrichment.lua
local jwt_decoder = require "kong.plugins.jwt.jwt_parser"
local http = require "resty.http"

local JwtEnrichmentHandler = {
    PRIORITY = 900,
    VERSION = "1.0.0",
}

function JwtEnrichmentHandler:access(conf)
    local token = kong.request.get_header("Authorization")
    if not token then
        return
    end
    
    token = token:gsub("Bearer ", "")
    local jwt, err = jwt_decoder:new(token)
    
    if err then
        return kong.response.exit(401, { message = "Invalid token" })
    end
    
    local claims = jwt.claims
    
    -- Enrich with additional user data
    local httpc = http.new()
    local res, err = httpc:request_uri(
        conf.user_service_url .. "/users/" .. claims.sub,
        {
            method = "GET",
            headers = {
                ["X-Internal-Request"] = "true"
            }
        }
    )
    
    if res and res.status == 200 then
        local user_data = cjson.decode(res.body)
        
        -- Add enriched headers
        kong.service.request.set_header("X-User-Id", claims.sub)
        kong.service.request.set_header("X-User-Role", user_data.role)
        kong.service.request.set_header("X-User-Plan", user_data.plan_id)
        kong.service.request.set_header("X-User-Tenant", user_data.tenant_id)
    end
end

return JwtEnrichmentHandler
```

### Request Validation Plugin

```python
# gateway/plugins/request-validator.py
import json
import jsonschema
from jsonschema import validate

class RequestValidator:
    def __init__(self, config):
        self.schemas = self.load_schemas(config['schema_path'])
    
    def load_schemas(self, path):
        schemas = {}
        # Load JSON schemas from file system
        with open(f"{path}/claims-submit.json") as f:
            schemas['claims-submit'] = json.load(f)
        return schemas
    
    def validate_request(self, route, body):
        schema_name = self.get_schema_name(route)
        if schema_name not in self.schemas:
            return True, None
        
        try:
            validate(instance=body, schema=self.schemas[schema_name])
            return True, None
        except jsonschema.exceptions.ValidationError as e:
            return False, str(e)
    
    def get_schema_name(self, route):
        # Map routes to schema names
        route_schema_map = {
            '/api/web/claims/submit': 'claims-submit',
            '/api/web/members/register': 'member-register'
        }
        return route_schema_map.get(route)

# Example schema
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["member_id", "provider_id", "service_date", "items"],
    "properties": {
        "member_id": {
            "type": "string",
            "format": "uuid"
        },
        "provider_id": {
            "type": "string",
            "format": "uuid"
        },
        "service_date": {
            "type": "string",
            "format": "date"
        },
        "items": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["benefit_code", "amount"],
                "properties": {
                    "benefit_code": {"type": "string"},
                    "amount": {"type": "number", "minimum": 0}
                }
            }
        }
    }
}
```

## Rate Limiting Strategies

### Tiered Rate Limiting

```yaml
# gateway/rate-limiting/tiers.yml
rate_limit_tiers:
  free:
    requests_per_second: 1
    requests_per_minute: 30
    requests_per_hour: 500
    requests_per_day: 5000
  
  basic:
    requests_per_second: 10
    requests_per_minute: 100
    requests_per_hour: 2000
    requests_per_day: 20000
  
  premium:
    requests_per_second: 50
    requests_per_minute: 500
    requests_per_hour: 10000
    requests_per_day: 100000
  
  enterprise:
    requests_per_second: 100
    requests_per_minute: 1000
    requests_per_hour: 50000
    requests_per_day: 500000

# Endpoint-specific limits
endpoint_limits:
  /api/web/claims/submit:
    burst: 5
    sustained: 2
    window: 60
  
  /api/web/eligibility/check:
    burst: 20
    sustained: 10
    window: 60
  
  /api/mobile/sync:
    burst: 3
    sustained: 1
    window: 300
```

### Dynamic Rate Limiting

```javascript
// gateway/middleware/dynamic-rate-limit.js
class DynamicRateLimiter {
    constructor(redis) {
        this.redis = redis;
        this.limits = new Map();
    }
    
    async shouldAllowRequest(userId, endpoint) {
        // Get user tier
        const userTier = await this.getUserTier(userId);
        
        // Get current system load
        const systemLoad = await this.getSystemLoad();
        
        // Adjust limits based on system load
        const adjustedLimit = this.calculateAdjustedLimit(
            userTier,
            systemLoad
        );
        
        // Check current usage
        const key = `rate_limit:${userId}:${endpoint}`;
        const current = await this.redis.incr(key);
        
        if (current === 1) {
            await this.redis.expire(key, 60);
        }
        
        if (current > adjustedLimit) {
            return {
                allowed: false,
                limit: adjustedLimit,
                remaining: 0,
                resetAt: await this.redis.ttl(key)
            };
        }
        
        return {
            allowed: true,
            limit: adjustedLimit,
            remaining: adjustedLimit - current,
            resetAt: await this.redis.ttl(key)
        };
    }
    
    calculateAdjustedLimit(baseTier, systemLoad) {
        const baseLimit = this.getTierLimit(baseTier);
        
        // Reduce limits when system is under load
        if (systemLoad > 0.8) {
            return Math.floor(baseLimit * 0.5);
        } else if (systemLoad > 0.6) {
            return Math.floor(baseLimit * 0.75);
        }
        
        return baseLimit;
    }
    
    async getSystemLoad() {
        // Get average response time from last 5 minutes
        const avgResponseTime = await this.redis.get('metrics:avg_response_time');
        
        // Calculate load factor (0-1)
        const targetResponseTime = 500; // 500ms target
        return Math.min(avgResponseTime / targetResponseTime, 1);
    }
}
```

## API Versioning

### Version Routing Strategy

```nginx
# Version detection and routing
location ~ ^/api/v(\d+)/(.*)$ {
    set $api_version $1;
    set $api_path $2;
    
    # Route to version-specific upstream
    if ($api_version = "1") {
        proxy_pass http://api_v1/$api_path;
    }
    
    if ($api_version = "2") {
        proxy_pass http://api_v2/$api_path;
    }
    
    # Default to latest version
    if ($api_version = "") {
        proxy_pass http://api_v2/$api_path;
    }
    
    # Add version header
    add_header X-API-Version $api_version always;
}
```

### Version Deprecation

```lua
-- gateway/plugins/version-deprecation.lua
local VersionDeprecation = {}

local deprecated_versions = {
    ["v1"] = {
        deprecated_date = "2024-01-01",
        sunset_date = "2024-07-01",
        message = "API v1 is deprecated. Please migrate to v2."
    }
}

function VersionDeprecation:header_filter(conf)
    local path = kong.request.get_path()
    local version = path:match("/api/(v%d+)/")
    
    if version and deprecated_versions[version] then
        local deprecation = deprecated_versions[version]
        
        kong.response.set_header("Deprecation", "true")
        kong.response.set_header("Sunset", deprecation.sunset_date)
        kong.response.set_header("Link", 
            '</api/v2/>; rel="successor-version"')
        
        -- Log deprecation usage
        kong.log.warn("Deprecated API version used: ", version, 
                     " by ", kong.request.get_header("X-User-Id"))
    end
end

return VersionDeprecation
```

## Circuit Breaker

```lua
-- gateway/plugins/circuit-breaker.lua
local CircuitBreaker = {
    PRIORITY = 850,
    VERSION = "1.0.0"
}

local states = {
    CLOSED = "closed",
    OPEN = "open",
    HALF_OPEN = "half_open"
}

function CircuitBreaker:access(conf)
    local service_name = kong.router.get_service().name
    local cache_key = "circuit:" .. service_name
    
    local circuit_state = kong.cache:get(cache_key, nil, function()
        return {
            state = states.CLOSED,
            failures = 0,
            last_failure_time = 0,
            success_count = 0
        }
    end)
    
    -- Check if circuit is open
    if circuit_state.state == states.OPEN then
        local time_since_failure = ngx.now() - circuit_state.last_failure_time
        
        if time_since_failure > conf.timeout then
            -- Try half-open state
            circuit_state.state = states.HALF_OPEN
            circuit_state.success_count = 0
            kong.cache:set(cache_key, circuit_state, conf.ttl)
        else
            -- Circuit still open
            return kong.response.exit(503, {
                message = "Service temporarily unavailable",
                retry_after = conf.timeout - time_since_failure
            })
        end
    end
    
    -- Store state for response phase
    ngx.ctx.circuit_state = circuit_state
    ngx.ctx.cache_key = cache_key
end

function CircuitBreaker:header_filter(conf)
    local circuit_state = ngx.ctx.circuit_state
    local cache_key = ngx.ctx.cache_key
    
    if not circuit_state then
        return
    end
    
    local status = kong.response.get_status()
    
    if status >= 500 then
        -- Failure
        circuit_state.failures = circuit_state.failures + 1
        circuit_state.last_failure_time = ngx.now()
        
        if circuit_state.failures >= conf.failure_threshold then
            circuit_state.state = states.OPEN
            kong.log.err("Circuit breaker opened for ", cache_key)
        end
    else
        -- Success
        if circuit_state.state == states.HALF_OPEN then
            circuit_state.success_count = circuit_state.success_count + 1
            
            if circuit_state.success_count >= conf.success_threshold then
                circuit_state.state = states.CLOSED
                circuit_state.failures = 0
                kong.log.info("Circuit breaker closed for ", cache_key)
            end
        elseif circuit_state.state == states.CLOSED then
            circuit_state.failures = 0
        end
    end
    
    kong.cache:set(cache_key, circuit_state, conf.ttl)
end

return CircuitBreaker
```

## Monitoring & Observability

### Prometheus Metrics

```lua
-- gateway/monitoring/prometheus.lua
local prometheus = require("prometheus")

-- Define metrics
local request_count = prometheus:counter(
    "gateway_requests_total",
    "Total number of requests",
    {"method", "endpoint", "status"}
)

local request_duration = prometheus:histogram(
    "gateway_request_duration_seconds",
    "Request duration in seconds",
    {"method", "endpoint"}
)

local upstream_latency = prometheus:histogram(
    "gateway_upstream_latency_seconds",
    "Upstream service latency",
    {"service"}
)

local rate_limit_hits = prometheus:counter(
    "gateway_rate_limit_hits_total",
    "Number of rate limited requests",
    {"tier", "endpoint"}
)

-- Collect metrics
function collect_metrics()
    local start_time = ngx.now()
    
    -- Process request
    local res = ngx.location.capture(ngx.var.request_uri)
    
    -- Record metrics
    local duration = ngx.now() - start_time
    local endpoint = ngx.var.uri
    local method = ngx.var.request_method
    local status = res.status
    
    request_count:inc(1, {method, endpoint, status})
    request_duration:observe(duration, {method, endpoint})
    
    -- Export metrics
    ngx.say(prometheus:collect())
end
```

### Access Logging

```json
// gateway/logging/access-log-format.json
{
    "timestamp": "$time_iso8601",
    "client_ip": "$remote_addr",
    "method": "$request_method",
    "uri": "$request_uri",
    "status": $status,
    "bytes_sent": $bytes_sent,
    "request_time": $request_time,
    "upstream_time": "$upstream_response_time",
    "user_agent": "$http_user_agent",
    "request_id": "$request_id",
    "user_id": "$http_x_user_id",
    "api_version": "$api_version",
    "cache_status": "$upstream_cache_status"
}
```

## Security Policies

### WAF Rules

```lua
-- gateway/security/waf-rules.lua
local waf_rules = {
    -- SQL Injection
    {
        pattern = [[(%27)|(\')|(--)|(%23)|(#)]],
        score = 5,
        description = "SQL Injection attempt"
    },
    -- XSS
    {
        pattern = [[(<script[^>]*>.*?</script>)]],
        score = 10,
        description = "XSS attempt"
    },
    -- Path Traversal
    {
        pattern = [[(\.\./)|(\.\.\\)]],
        score = 5,
        description = "Path traversal attempt"
    },
    -- Command Injection
    {
        pattern = [[;\s*(ls|cat|wget|curl|bash|sh)]],
        score = 10,
        description = "Command injection attempt"
    }
}

function check_waf_rules(request_body)
    local total_score = 0
    local triggered_rules = {}
    
    for _, rule in ipairs(waf_rules) do
        if string.match(request_body, rule.pattern) then
            total_score = total_score + rule.score
            table.insert(triggered_rules, rule.description)
        end
    end
    
    if total_score >= 10 then
        return false, triggered_rules
    end
    
    return true, nil
end
```

## Disaster Recovery

### Failover Configuration

```yaml
# gateway/failover/config.yml
failover:
  primary_datacenter: us-east-1
  secondary_datacenter: us-west-2
  
  health_check:
    interval: 5s
    timeout: 3s
    unhealthy_threshold: 3
    healthy_threshold: 2
  
  dns_failover:
    ttl: 60
    provider: route53
    health_check_id: ${health_check_id}
  
  traffic_split:
    normal:
      primary: 100
      secondary: 0
    degraded:
      primary: 80
      secondary: 20
    failover:
      primary: 0
      secondary: 100
```

## Performance Tuning

### NGINX Optimization

```nginx
# gateway/nginx/performance.conf

# Worker processes
worker_processes auto;
worker_cpu_affinity auto;
worker_rlimit_nofile 65535;

events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}

http {
    # TCP optimizations
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    
    # Keepalive
    keepalive_timeout 65;
    keepalive_requests 100;
    
    # Buffers
    client_body_buffer_size 16K;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 16k;
    client_max_body_size 10m;
    
    # Timeouts
    client_body_timeout 12;
    client_header_timeout 12;
    send_timeout 10;
    
    # Gzip
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss 
               application/rss+xml application/atom+xml image/svg+xml 
               text/javascript application/vnd.ms-fontobject 
               application/x-font-ttf font/opentype;
    
    # Cache
    open_file_cache max=1000 inactive=20s;
    open_file_cache_valid 30s;
    open_file_cache_min_uses 2;
    open_file_cache_errors on;
    
    # Rate limiting
    limit_req_status 429;
    limit_conn_status 429;
}
```

## Troubleshooting

### Common Issues

1. **High Latency**
   - Check upstream service health
   - Review circuit breaker status
   - Analyze slow query logs
   - Check connection pool settings

2. **Rate Limiting Issues**
   - Verify Redis connectivity
   - Check rate limit configurations
   - Review user tier assignments
   - Monitor rate limit metrics

3. **Authentication Failures**
   - Validate JWT signing keys
   - Check token expiration
   - Verify JWKS endpoint
   - Review authentication logs

### Debug Mode

```lua
-- Enable debug headers
if kong.request.get_header("X-Debug-Mode") == "true" then
    kong.response.set_header("X-Kong-Upstream-Latency", 
                            ngx.ctx.KONG_WAITING_TIME)
    kong.response.set_header("X-Kong-Proxy-Latency", 
                            ngx.ctx.KONG_PROXY_LATENCY)
    kong.response.set_header("X-Kong-Request-ID", 
                            kong.request.get_header("X-Request-ID"))
end
```

## Support

- **Gateway Team**: gateway@claims-askes.com
- **On-call**: PagerDuty rotation
- **Documentation**: Internal wiki
- **Monitoring**: Gateway dashboard at grafana.claims-askes.com

## License

Proprietary - All rights reserved