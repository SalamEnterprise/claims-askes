# Shared Packages Documentation

## Overview

This directory contains shared Python packages, libraries, and utilities used across the Claims-Askes platform. These packages promote code reuse, maintain consistency, and reduce duplication across microservices and applications.

## Package Structure

```
packages/
├── claims_common/       # Common utilities and helpers
├── claims_auth/         # Authentication & authorization
├── claims_database/     # Database utilities and models
├── claims_messaging/    # Message queue abstractions
├── claims_logging/      # Centralized logging
├── claims_monitoring/   # Monitoring and metrics
├── claims_validation/   # Data validation schemas
├── claims_cache/        # Caching utilities
├── claims_events/       # Event-driven architecture utilities
└── claims_testing/      # Testing utilities
```

## Core Packages

### 1. Common Package (`claims-common`)

Shared utilities and helper functions used across all services.

#### Installation
```bash
pip install claims-common
# Or from local development
pip install -e ./packages/claims_common
```

#### Features

```python
# packages/claims_common/__init__.py

# Date utilities
from .utils.date import (
    format_date,
    add_business_days,
    get_quarter,
    parse_iso_date
)

# Currency utilities
from .utils.currency import (
    format_rupiah,
    parse_rupiah,
    convert_currency
)

# Validation utilities
from .utils.validation import (
    validate_nik,
    validate_npwp,
    validate_phone_number,
    validate_email
)

# Crypto utilities
from .utils.crypto import (
    hash_password,
    verify_password,
    generate_token
)

# Constants
from .constants import (
    ClaimStatus,
    ServiceType,
    ErrorCodes,
    DEFAULT_PAGE_SIZE
)

# Types
from .types import (
    PaginationParams,
    ApiResponse,
    ErrorResponse
)
```

#### Usage Examples

```python
from claims_common import format_rupiah, validate_nik, ClaimStatus

# Format Indonesian Rupiah
amount = format_rupiah(5000000)  # "Rp 5.000.000"

# Validate Indonesian National ID
is_valid = validate_nik('3275010101900001')  # True

# Use common enums
status = ClaimStatus.APPROVED
```

#### Utilities

```python
# packages/claims_common/utils/date.py
from datetime import datetime, timedelta
from typing import List
import holidays

# Indonesian holidays
ID_HOLIDAYS = holidays.Indonesia()

def format_date(date: datetime, format_str: str = "%Y-%m-%d") -> str:
    """Format date to string"""
    return date.strftime(format_str)

def add_business_days(date: datetime, days: int) -> datetime:
    """Add business days, skipping weekends and holidays"""
    current = date
    days_added = 0
    
    while days_added < days:
        current += timedelta(days=1)
        if current.weekday() < 5 and current not in ID_HOLIDAYS:
            days_added += 1
    
    return current

def get_quarter(date: datetime) -> int:
    """Get quarter from date"""
    return (date.month - 1) // 3 + 1

# packages/claims_common/utils/currency.py
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
import locale

# Set Indonesian locale
try:
    locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
except:
    locale.setlocale(locale.LC_ALL, '')

def format_rupiah(amount: Decimal) -> str:
    """Format amount to Indonesian Rupiah"""
    # Format with thousands separator
    formatted = f"Rp {amount:,.0f}".replace(',', '.')
    return formatted

def parse_rupiah(value: str) -> Decimal:
    """Parse Rupiah string to Decimal"""
    # Remove non-numeric characters
    cleaned = ''.join(c for c in value if c.isdigit() or c == '.')
    return Decimal(cleaned.replace('.', ''))

def round_rupiah(amount: Decimal) -> Decimal:
    """Round to nearest Rupiah (no decimal places)"""
    return amount.quantize(Decimal('1'), rounding=ROUND_HALF_UP)

# packages/claims_common/utils/validation.py
import re
from typing import Optional

def validate_email(email: str) -> bool:
    """Validate email address format"""
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return bool(re.match(pattern, email))

def validate_phone_number(phone: str) -> bool:
    """Validate Indonesian phone number format"""
    pattern = r'^(\+62|62|0)[0-9]{9,12}$'
    return bool(re.match(pattern, phone))

def validate_npwp(npwp: str) -> bool:
    """Validate Indonesian tax number (NPWP)"""
    pattern = r'^[0-9]{2}\.[0-9]{3}\.[0-9]{3}\.[0-9]{1}-[0-9]{3}\.[0-9]{3}$'
    return bool(re.match(pattern, npwp))

def validate_nik(nik: str) -> bool:
    """Validate Indonesian National ID (NIK)"""
    if not nik or len(nik) != 16:
        return False
    
    if not nik.isdigit():
        return False
    
    # Additional validation logic
    # Province code (2 digits): 11-94
    province = int(nik[:2])
    if province < 11 or province > 94:
        return False
    
    # Date validation (DDMMYY)
    day = int(nik[6:8])
    month = int(nik[8:10])
    
    # For females, day is increased by 40
    if day > 40:
        day -= 40
    
    if day < 1 or day > 31:
        return False
    
    if month < 1 or month > 12:
        return False
    
    return True
```

### 2. Authentication Package (`claims-auth`)

Centralized authentication and authorization utilities.

#### Installation
```bash
pip install claims-auth
# Or from local development
pip install -e ./packages/claims_auth
```

#### Features

```python
# packages/claims_auth/__init__.py

# JWT utilities
from .jwt import (
    encode_token,
    decode_token,
    validate_token,
    refresh_token
)

# Middleware
from .middleware import (
    authenticate,
    authorize,
    require_roles,
    require_permissions
)

# Services
from .services import (
    AuthService,
    TokenService,
    PermissionService
)

# Types
from .types import (
    User,
    Token,
    Permission,
    Role
)

# Password utilities
from .password import (
    hash_password,
    verify_password,
    generate_password
)
```

#### JWT Service

```python
# packages/claims_auth/jwt.py
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
import jwt
from pydantic import BaseModel

class JWTPayload(BaseModel):
    """JWT payload structure"""
    sub: str  # User ID
    email: str
    roles: List[str]
    permissions: List[str]
    iat: Optional[int] = None
    exp: Optional[int] = None

class JWTConfig(BaseModel):
    """JWT configuration"""
    secret: str
    algorithm: str = "HS256"
    expires_in: int = 3600  # 1 hour in seconds
    refresh_secret: str
    refresh_expires_in: int = 604800  # 7 days in seconds
    issuer: str = "claims-askes"
    audience: str = "claims-askes-api"

class JWTService:
    """JWT token management service"""
    
    def __init__(self, config: JWTConfig):
        self.config = config
    
    def generate_token(self, payload: JWTPayload) -> str:
        """Generate access token"""
        now = datetime.now(timezone.utc)
        exp = now + timedelta(seconds=self.config.expires_in)
        
        token_data = {
            **payload.dict(exclude_none=True),
            'iat': now.timestamp(),
            'exp': exp.timestamp(),
            'iss': self.config.issuer,
            'aud': self.config.audience
        }
        
        return jwt.encode(
            token_data,
            self.config.secret,
            algorithm=self.config.algorithm
        )
    
    def generate_refresh_token(self, user_id: str) -> str:
        """Generate refresh token"""
        now = datetime.now(timezone.utc)
        exp = now + timedelta(seconds=self.config.refresh_expires_in)
        
        token_data = {
            'sub': user_id,
            'type': 'refresh',
            'iat': now.timestamp(),
            'exp': exp.timestamp(),
            'iss': self.config.issuer
        }
        
        return jwt.encode(
            token_data,
            self.config.refresh_secret,
            algorithm=self.config.algorithm
        )
    
    def verify_token(self, token: str) -> JWTPayload:
        """Verify and decode access token"""
        try:
            decoded = jwt.decode(
                token,
                self.config.secret,
                algorithms=[self.config.algorithm],
                issuer=self.config.issuer,
                audience=self.config.audience
            )
            return JWTPayload(**decoded)
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {str(e)}")
    
    def verify_refresh_token(self, token: str) -> Dict[str, str]:
        """Verify refresh token"""
        try:
            decoded = jwt.decode(
                token,
                self.config.refresh_secret,
                algorithms=[self.config.algorithm],
                issuer=self.config.issuer
            )
            return {'sub': decoded['sub']}
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid refresh token: {str(e)}")
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode token without verification"""
        try:
            return jwt.decode(token, options={"verify_signature": False})
        except Exception:
            return None
```

#### Authentication Middleware

```python
# packages/claims_auth/middleware.py
from functools import wraps
from typing import Optional, List, Callable, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .jwt import JWTService, JWTPayload
from .types import User

security = HTTPBearer()

class AuthenticationMiddleware:
    """FastAPI authentication middleware"""
    
    def __init__(self, jwt_service: JWTService):
        self.jwt_service = jwt_service
    
    async def __call__(
        self,
        request: Request,
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> User:
        """Authenticate user from JWT token"""
        token = credentials.credentials
        
        try:
            payload = self.jwt_service.verify_token(token)
            
            # Create user object from JWT payload
            user = User(
                id=payload.sub,
                email=payload.email,
                roles=payload.roles,
                permissions=payload.permissions
            )
            
            # Store user in request state
            request.state.user = user
            return user
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )

def authenticate(jwt_service: JWTService) -> Callable:
    """Create authentication dependency"""
    return AuthenticationMiddleware(jwt_service)

def require_roles(*required_roles: str) -> Callable:
    """Decorator to require specific roles"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(
            *args,
            current_user: User = Depends(authenticate),
            **kwargs
        ) -> Any:
            if not any(role in current_user.roles for role in required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

def require_permissions(*required_permissions: str) -> Callable:
    """Decorator to require specific permissions"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(
            *args,
            current_user: User = Depends(authenticate),
            **kwargs
        ) -> Any:
            if not all(perm in current_user.permissions for perm in required_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permissions: {required_permissions}"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# Alternative for standard Python frameworks
def extract_token(authorization: Optional[str], cookies: dict = None) -> Optional[str]:
    """Extract token from authorization header or cookies"""
    if authorization and authorization.startswith('Bearer '):
        return authorization[7:]
    
    if cookies and 'token' in cookies:
        return cookies['token']
    
    return None
```

#### Authorization Service

```python
# packages/claims_auth/authorization.py
from typing import List, Set, Optional
from enum import Enum
from pydantic import BaseModel

class Permission(str, Enum):
    """System permissions"""
    # Claims
    CLAIM_CREATE = "claim:create"
    CLAIM_READ = "claim:read"
    CLAIM_UPDATE = "claim:update"
    CLAIM_DELETE = "claim:delete"
    CLAIM_APPROVE = "claim:approve"
    CLAIM_REJECT = "claim:reject"
    
    # Members
    MEMBER_CREATE = "member:create"
    MEMBER_READ = "member:read"
    MEMBER_UPDATE = "member:update"
    MEMBER_DELETE = "member:delete"
    
    # Providers
    PROVIDER_CREATE = "provider:create"
    PROVIDER_READ = "provider:read"
    PROVIDER_UPDATE = "provider:update"
    PROVIDER_DELETE = "provider:delete"
    
    # Admin
    ADMIN_ACCESS = "admin:access"
    ADMIN_REPORTS = "admin:reports"
    ADMIN_SETTINGS = "admin:settings"

class Role(str, Enum):
    """System roles"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    CLAIM_PROCESSOR = "claim_processor"
    PROVIDER = "provider"
    MEMBER = "member"
    AUDITOR = "auditor"

class RolePermissions:
    """Role to permissions mapping"""
    
    ROLE_PERMISSIONS = {
        Role.SUPER_ADMIN: set(Permission),  # All permissions
        
        Role.ADMIN: {
            Permission.CLAIM_CREATE, Permission.CLAIM_READ,
            Permission.CLAIM_UPDATE, Permission.CLAIM_APPROVE,
            Permission.CLAIM_REJECT,
            Permission.MEMBER_CREATE, Permission.MEMBER_READ,
            Permission.MEMBER_UPDATE,
            Permission.PROVIDER_CREATE, Permission.PROVIDER_READ,
            Permission.PROVIDER_UPDATE,
            Permission.ADMIN_ACCESS, Permission.ADMIN_REPORTS
        },
        
        Role.CLAIM_PROCESSOR: {
            Permission.CLAIM_READ, Permission.CLAIM_UPDATE,
            Permission.CLAIM_APPROVE, Permission.CLAIM_REJECT,
            Permission.MEMBER_READ, Permission.PROVIDER_READ
        },
        
        Role.PROVIDER: {
            Permission.CLAIM_CREATE, Permission.CLAIM_READ,
            Permission.MEMBER_READ
        },
        
        Role.MEMBER: {
            Permission.CLAIM_CREATE, Permission.CLAIM_READ,
            Permission.MEMBER_READ, Permission.MEMBER_UPDATE
        },
        
        Role.AUDITOR: {
            Permission.CLAIM_READ, Permission.MEMBER_READ,
            Permission.PROVIDER_READ, Permission.ADMIN_REPORTS
        }
    }
    
    @classmethod
    def get_permissions(cls, roles: List[Role]) -> Set[Permission]:
        """Get all permissions for given roles"""
        permissions = set()
        for role in roles:
            if role in cls.ROLE_PERMISSIONS:
                permissions.update(cls.ROLE_PERMISSIONS[role])
        return permissions

class AuthorizationService:
    """Authorization service for permission checking"""
    
    def __init__(self):
        self.role_permissions = RolePermissions()
    
    def has_permission(
        self,
        user_roles: List[str],
        required_permission: Permission
    ) -> bool:
        """Check if user roles have required permission"""
        roles = [Role(r) for r in user_roles if r in Role.__members__.values()]
        permissions = self.role_permissions.get_permissions(roles)
        return required_permission in permissions
    
    def has_any_permission(
        self,
        user_roles: List[str],
        required_permissions: List[Permission]
    ) -> bool:
        """Check if user has any of the required permissions"""
        roles = [Role(r) for r in user_roles if r in Role.__members__.values()]
        permissions = self.role_permissions.get_permissions(roles)
        return any(perm in permissions for perm in required_permissions)
    
    def has_all_permissions(
        self,
        user_roles: List[str],
        required_permissions: List[Permission]
    ) -> bool:
        """Check if user has all required permissions"""
        roles = [Role(r) for r in user_roles if r in Role.__members__.values()]
        permissions = self.role_permissions.get_permissions(roles)
        return all(perm in permissions for perm in required_permissions)
```

### 3. Database Package (`claims-database`)

Shared database utilities, models, and migrations.

#### Installation
```bash
pip install claims-database
# Or from local development
pip install -e ./packages/claims_database
```

#### Features

```python
# packages/claims_database/__init__.py

# Connection management
from .connection import (
    DatabaseConnection,
    create_engine,
    get_session,
    async_session_maker
)

# Base models
from .models import (
    BaseModel,
    AuditableModel,
    TimestampMixin,
    SoftDeleteMixin
)

# Repositories
from .repositories import (
    BaseRepository,
    CacheRepository,
    AsyncRepository
)

# Utilities
from .utils import (
    Pagination,
    Transaction,
    bulk_insert,
    bulk_update
)

# Query builders
from .query import (
    QueryBuilder,
    FilterOperator,
    SortOrder
)
```

#### Base Models

```python
# packages/claims_database/models.py
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, JSON, Boolean, text
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class TimestampMixin:
    """Mixin for timestamp fields"""
    
    @declared_attr
    def created_at(cls):
        return Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text('CURRENT_TIMESTAMP')
        )
    
    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text('CURRENT_TIMESTAMP'),
            onupdate=datetime.utcnow
        )

class SoftDeleteMixin:
    """Mixin for soft delete functionality"""
    
    @declared_attr
    def deleted_at(cls):
        return Column(DateTime(timezone=True), nullable=True)
    
    @declared_attr
    def is_deleted(cls):
        return Column(Boolean, default=False, nullable=False)
    
    def soft_delete(self):
        """Mark record as deleted"""
        self.deleted_at = datetime.utcnow()
        self.is_deleted = True
    
    def restore(self):
        """Restore soft deleted record"""
        self.deleted_at = None
        self.is_deleted = False

class BaseModel(Base, TimestampMixin):
    """Base model with common fields"""
    __abstract__ = True
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )

class AuditableModel(BaseModel, SoftDeleteMixin):
    """Auditable model with user tracking"""
    __abstract__ = True
    
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    def update_audit(
        self,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Update audit fields"""
        self.updated_by = user_id
        self.updated_at = datetime.utcnow()
        if metadata:
            self.metadata = {**(self.metadata or {}), **metadata}
```

#### Base Repository

```python
# packages/claims_database/repositories.py
from typing import TypeVar, Generic, Optional, List, Dict, Any, Type
from datetime import datetime
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from pydantic import BaseModel as PydanticModel

from .models import BaseModel, AuditableModel
from .utils import Pagination, PaginatedResult

T = TypeVar('T', bound=BaseModel)

class FilterOperator:
    """Filter operators for queries"""
    EQ = "eq"  # Equal
    NEQ = "neq"  # Not equal
    GT = "gt"  # Greater than
    GTE = "gte"  # Greater than or equal
    LT = "lt"  # Less than
    LTE = "lte"  # Less than or equal
    IN = "in"  # In list
    NOT_IN = "not_in"  # Not in list
    LIKE = "like"  # Like pattern
    ILIKE = "ilike"  # Case-insensitive like
    IS_NULL = "is_null"  # Is null
    IS_NOT_NULL = "is_not_null"  # Is not null

class BaseRepository(Generic[T]):
    """Base repository for database operations"""
    
    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model
    
    def find_by_id(self, id: str) -> Optional[T]:
        """Find entity by ID"""
        return self.session.query(self.model).filter(
            self.model.id == id
        ).first()
    
    def find_all(
        self,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> List[T]:
        """Find all entities with optional filters"""
        query = self.session.query(self.model)
        
        if filters:
            query = self._apply_filters(query, filters)
        
        if order_by:
            column = getattr(self.model, order_by)
            query = query.order_by(column.desc() if order_desc else column)
        
        return query.all()
    
    def find_paginated(
        self,
        pagination: Pagination,
        filters: Optional[Dict[str, Any]] = None
    ) -> PaginatedResult[T]:
        """Find entities with pagination"""
        query = self.session.query(self.model)
        
        if filters:
            query = self._apply_filters(query, filters)
        
        # Get total count
        total = query.count()
        
        # Apply ordering
        if pagination.sort_by:
            column = getattr(self.model, pagination.sort_by)
            query = query.order_by(
                column.desc() if pagination.sort_desc else column
            )
        
        # Apply pagination
        query = query.offset((pagination.page - 1) * pagination.limit)
        query = query.limit(pagination.limit)
        
        items = query.all()
        
        return PaginatedResult(
            items=items,
            total=total,
            page=pagination.page,
            pages=(total + pagination.limit - 1) // pagination.limit,
            limit=pagination.limit
        )
    
    def create(self, data: Dict[str, Any]) -> T:
        """Create new entity"""
        entity = self.model(**data)
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity
    
    def update(self, id: str, data: Dict[str, Any]) -> Optional[T]:
        """Update entity by ID"""
        entity = self.find_by_id(id)
        if not entity:
            return None
        
        for key, value in data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        
        if isinstance(entity, AuditableModel):
            entity.updated_at = datetime.utcnow()
        
        self.session.commit()
        self.session.refresh(entity)
        return entity
    
    def delete(self, id: str) -> bool:
        """Delete entity by ID"""
        entity = self.find_by_id(id)
        if not entity:
            return False
        
        self.session.delete(entity)
        self.session.commit()
        return True
    
    def soft_delete(self, id: str) -> bool:
        """Soft delete entity by ID"""
        entity = self.find_by_id(id)
        if not entity or not hasattr(entity, 'soft_delete'):
            return False
        
        entity.soft_delete()
        self.session.commit()
        return True
    
    def _apply_filters(self, query, filters: Dict[str, Any]):
        """Apply filters to query"""
        for field, value in filters.items():
            if isinstance(value, dict) and 'operator' in value:
                query = self._apply_operator_filter(
                    query, field, value['operator'], value.get('value')
                )
            else:
                # Default to equality
                query = query.filter(getattr(self.model, field) == value)
        
        return query
    
    def _apply_operator_filter(self, query, field, operator, value):
        """Apply operator-based filter"""
        column = getattr(self.model, field)
        
        if operator == FilterOperator.EQ:
            return query.filter(column == value)
        elif operator == FilterOperator.NEQ:
            return query.filter(column != value)
        elif operator == FilterOperator.GT:
            return query.filter(column > value)
        elif operator == FilterOperator.GTE:
            return query.filter(column >= value)
        elif operator == FilterOperator.LT:
            return query.filter(column < value)
        elif operator == FilterOperator.LTE:
            return query.filter(column <= value)
        elif operator == FilterOperator.IN:
            return query.filter(column.in_(value))
        elif operator == FilterOperator.NOT_IN:
            return query.filter(~column.in_(value))
        elif operator == FilterOperator.LIKE:
            return query.filter(column.like(f'%{value}%'))
        elif operator == FilterOperator.ILIKE:
            return query.filter(column.ilike(f'%{value}%'))
        elif operator == FilterOperator.IS_NULL:
            return query.filter(column.is_(None))
        elif operator == FilterOperator.IS_NOT_NULL:
            return query.filter(column.isnot(None))
        else:
            return query

class AsyncRepository(Generic[T]):
    """Async repository for database operations"""
    
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model
    
    async def find_by_id(self, id: str) -> Optional[T]:
        """Find entity by ID"""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def find_all(
        self,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> List[T]:
        """Find all entities with optional filters"""
        stmt = select(self.model)
        
        if filters:
            stmt = self._apply_filters(stmt, filters)
        
        if order_by:
            column = getattr(self.model, order_by)
            stmt = stmt.order_by(column.desc() if order_desc else column)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def create(self, data: Dict[str, Any]) -> T:
        """Create new entity"""
        entity = self.model(**data)
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity
    
    async def update(self, id: str, data: Dict[str, Any]) -> Optional[T]:
        """Update entity by ID"""
        entity = await self.find_by_id(id)
        if not entity:
            return None
        
        for key, value in data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        
        await self.session.commit()
        await self.session.refresh(entity)
        return entity
    
    async def delete(self, id: str) -> bool:
        """Delete entity by ID"""
        entity = await self.find_by_id(id)
        if not entity:
            return False
        
        await self.session.delete(entity)
        await self.session.commit()
        return True
```

### 4. Messaging Package (`claims-messaging`)

Message queue abstractions for event-driven architecture.

#### Installation
```bash
pip install claims-messaging
# Or from local development
pip install -e ./packages/claims_messaging
```

#### Features

```python
# packages/claims_messaging/__init__.py

# Publishers
from .publishers import (
    EventPublisher,
    QueuePublisher,
    TopicPublisher
)

# Consumers
from .consumers import (
    EventConsumer,
    QueueConsumer,
    TopicConsumer
)

# Events
from .events import (
    BaseEvent,
    ClaimEvent,
    MemberEvent,
    ProviderEvent,
    EventType
)

# Message brokers
from .brokers import (
    RabbitMQBroker,
    RedisBroker,
    KafkaBroker
)

# Utilities
from .utils import (
    RetryPolicy,
    DeadLetterQueue,
    MessageSerializer
)
```

#### Event Publisher

```python
# packages/claims_messaging/publishers.py
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import uuid
import aio_pika
from aio_pika import Message, ExchangeType
import redis.asyncio as redis
from aiokafka import AIOKafkaProducer

@dataclass
class EventMetadata:
    """Event metadata"""
    timestamp: datetime
    correlation_id: str
    user_id: Optional[str] = None
    source: Optional[str] = None
    version: str = "1.0"

@dataclass
class Event:
    """Base event structure"""
    type: str
    data: Dict[str, Any]
    metadata: EventMetadata
    
    def to_json(self) -> str:
        """Convert event to JSON"""
        return json.dumps({
            'type': self.type,
            'data': self.data,
            'metadata': {
                'timestamp': self.metadata.timestamp.isoformat(),
                'correlation_id': self.metadata.correlation_id,
                'user_id': self.metadata.user_id,
                'source': self.metadata.source,
                'version': self.metadata.version
            }
        })

class EventPublisher:
    """RabbitMQ event publisher"""
    
    def __init__(self, url: str, exchange_name: str = 'events'):
        self.url = url
        self.exchange_name = exchange_name
        self.connection = None
        self.channel = None
        self.exchange = None
    
    async def connect(self):
        """Connect to RabbitMQ"""
        self.connection = await aio_pika.connect_robust(self.url)
        self.channel = await self.connection.channel()
        
        # Declare exchange
        self.exchange = await self.channel.declare_exchange(
            self.exchange_name,
            ExchangeType.TOPIC,
            durable=True
        )
    
    async def publish(self, event: Event):
        """Publish single event"""
        if not self.channel:
            await self.connect()
        
        routing_key = event.type.replace('.', '_')
        message = Message(
            event.to_json().encode(),
            content_type='application/json',
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            timestamp=datetime.utcnow(),
            message_id=str(uuid.uuid4()),
            correlation_id=event.metadata.correlation_id
        )
        
        await self.exchange.publish(message, routing_key=routing_key)
    
    async def publish_batch(self, events: List[Event]):
        """Publish multiple events"""
        tasks = [self.publish(event) for event in events]
        await asyncio.gather(*tasks)
    
    async def close(self):
        """Close connection"""
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()

class RedisEventPublisher:
    """Redis Pub/Sub event publisher"""
    
    def __init__(self, url: str):
        self.url = url
        self.client = None
    
    async def connect(self):
        """Connect to Redis"""
        self.client = await redis.from_url(self.url)
    
    async def publish(self, channel: str, event: Event):
        """Publish event to channel"""
        if not self.client:
            await self.connect()
        
        await self.client.publish(channel, event.to_json())
    
    async def close(self):
        """Close connection"""
        if self.client:
            await self.client.close()

class KafkaEventPublisher:
    """Kafka event publisher"""
    
    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
    
    async def connect(self):
        """Connect to Kafka"""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode()
        )
        await self.producer.start()
    
    async def publish(self, topic: str, event: Event):
        """Publish event to topic"""
        if not self.producer:
            await self.connect()
        
        await self.producer.send(
            topic,
            value={
                'type': event.type,
                'data': event.data,
                'metadata': asdict(event.metadata)
            },
            key=event.metadata.correlation_id.encode()
        )
    
    async def close(self):
        """Close connection"""
        if self.producer:
            await self.producer.stop()
```

#### Event Consumer

```python
# packages/claims_messaging/consumers.py
import json
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Callable, Any, Optional
from datetime import datetime
import aio_pika
from aio_pika import IncomingMessage
import redis.asyncio as redis
from aiokafka import AIOKafkaConsumer
import logging

logger = logging.getLogger(__name__)

class EventHandler(ABC):
    """Abstract event handler"""
    
    @abstractmethod
    async def handle(self, event: Event) -> None:
        """Handle event"""
        pass

class EventConsumer:
    """RabbitMQ event consumer"""
    
    def __init__(self, url: str, queue_name: str):
        self.url = url
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
        self.queue = None
        self.handlers: Dict[str, List[EventHandler]] = {}
    
    async def connect(self):
        """Connect to RabbitMQ"""
        self.connection = await aio_pika.connect_robust(self.url)
        self.channel = await self.connection.channel()
        
        # Set prefetch count for load balancing
        await self.channel.set_qos(prefetch_count=10)
        
        # Declare exchange
        exchange = await self.channel.declare_exchange(
            'events',
            aio_pika.ExchangeType.TOPIC,
            durable=True
        )
        
        # Declare dead letter exchange
        dlx = await self.channel.declare_exchange(
            'dlx',
            aio_pika.ExchangeType.DIRECT,
            durable=True
        )
        
        # Declare queue with dead letter configuration
        self.queue = await self.channel.declare_queue(
            self.queue_name,
            durable=True,
            arguments={
                'x-dead-letter-exchange': 'dlx',
                'x-message-ttl': 3600000,  # 1 hour
                'x-max-retries': 3
            }
        )
    
    def subscribe(self, event_type: str, handler: EventHandler):
        """Subscribe to event type"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    async def start(self):
        """Start consuming messages"""
        if not self.channel:
            await self.connect()
        
        # Bind queue to event types
        exchange = await self.channel.get_exchange('events')
        for event_type in self.handlers.keys():
            routing_key = event_type.replace('.', '_')
            await self.queue.bind(exchange, routing_key=routing_key)
        
        # Start consuming
        async with self.queue.iterator() as queue_iter:
            async for message in queue_iter:
                await self._process_message(message)
    
    async def _process_message(self, message: IncomingMessage):
        """Process incoming message"""
        async with message.process():
            try:
                # Parse message
                body = json.loads(message.body.decode())
                event = Event(
                    type=body['type'],
                    data=body['data'],
                    metadata=EventMetadata(
                        timestamp=datetime.fromisoformat(body['metadata']['timestamp']),
                        correlation_id=body['metadata']['correlation_id'],
                        user_id=body['metadata'].get('user_id'),
                        source=body['metadata'].get('source'),
                        version=body['metadata'].get('version', '1.0')
                    )
                )
                
                # Get handlers for event type
                handlers = self.handlers.get(event.type, [])
                
                # Process with all handlers
                for handler in handlers:
                    await handler.handle(event)
                
                logger.info(f"Successfully processed event: {event.type}")
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                
                # Get retry count
                headers = message.headers or {}
                retry_count = headers.get('x-retry-count', 0)
                
                if retry_count < 3:
                    # Requeue with incremented retry count
                    await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                    
                    await self.channel.default_exchange.publish(
                        aio_pika.Message(
                            message.body,
                            headers={'x-retry-count': retry_count + 1}
                        ),
                        routing_key=self.queue_name
                    )
                    logger.info(f"Requeued message, retry count: {retry_count + 1}")
                else:
                    # Max retries exceeded, reject to dead letter queue
                    await message.reject(requeue=False)
                    logger.error(f"Message sent to dead letter queue after {retry_count} retries")
    
    async def stop(self):
        """Stop consumer"""
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()

class RedisEventConsumer:
    """Redis Pub/Sub consumer"""
    
    def __init__(self, url: str):
        self.url = url
        self.client = None
        self.pubsub = None
        self.handlers: Dict[str, List[Callable]] = {}
    
    async def connect(self):
        """Connect to Redis"""
        self.client = await redis.from_url(self.url)
        self.pubsub = self.client.pubsub()
    
    async def subscribe(self, channel: str, handler: Callable):
        """Subscribe to channel"""
        if not self.pubsub:
            await self.connect()
        
        await self.pubsub.subscribe(channel)
        
        if channel not in self.handlers:
            self.handlers[channel] = []
        self.handlers[channel].append(handler)
    
    async def start(self):
        """Start consuming messages"""
        async for message in self.pubsub.listen():
            if message['type'] == 'message':
                channel = message['channel'].decode()
                data = json.loads(message['data'])
                
                # Process with all handlers for this channel
                for handler in self.handlers.get(channel, []):
                    await handler(data)
    
    async def stop(self):
        """Stop consumer"""
        if self.pubsub:
            await self.pubsub.unsubscribe()
            await self.pubsub.close()
        if self.client:
            await self.client.close()
```

### 5. Logging Package (`claims-logging`)

Centralized logging with structured logs.

#### Installation
```bash
pip install claims-logging
# Or from local development
pip install -e ./packages/claims_logging
```

#### Logger Implementation

```python
# packages/claims_logging/logger.py
import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from contextvars import ContextVar
from pythonjsonlogger import jsonlogger
from elasticsearch import Elasticsearch
import structlog

# Context variables for request-scoped data
log_context: ContextVar[Dict[str, Any]] = ContextVar('log_context', default={})

class LoggerConfig:
    """Logger configuration"""
    def __init__(
        self,
        service: str,
        environment: str,
        level: str = 'INFO',
        elasticsearch_url: Optional[str] = None,
        file_path: Optional[str] = None
    ):
        self.service = service
        self.environment = environment
        self.level = level
        self.elasticsearch_url = elasticsearch_url
        self.file_path = file_path

class StructuredLogger:
    """Structured logger with multiple outputs"""
    
    def __init__(self, config: LoggerConfig):
        self.config = config
        self.logger = self._setup_logger()
        self.es_client = None
        
        if config.elasticsearch_url:
            self.es_client = Elasticsearch([config.elasticsearch_url])
    
    def _setup_logger(self) -> structlog.BoundLogger:
        """Setup structured logger"""
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                self._add_context,
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
        
        # Configure standard logging
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=getattr(logging, self.config.level)
        )
        
        # Add file handler if configured
        if self.config.file_path:
            file_handler = logging.FileHandler(self.config.file_path)
            file_handler.setLevel(logging.ERROR)
            formatter = jsonlogger.JsonFormatter()
            file_handler.setFormatter(formatter)
            logging.getLogger().addHandler(file_handler)
        
        return structlog.get_logger(
            service=self.config.service,
            environment=self.config.environment
        )
    
    def _add_context(self, logger, method_name, event_dict):
        """Add context to log entries"""
        context = log_context.get()
        event_dict.update(context)
        return event_dict
    
    def set_context(self, **kwargs):
        """Set logging context"""
        current = log_context.get()
        updated = {**current, **kwargs}
        log_context.set(updated)
    
    def clear_context(self):
        """Clear logging context"""
        log_context.set({})
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, **kwargs)
        self._send_to_elasticsearch('info', message, kwargs)
    
    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log error message"""
        if error:
            kwargs['error'] = {
                'type': type(error).__name__,
                'message': str(error),
                'traceback': None  # Will be added by format_exc_info processor
            }
        self.logger.error(message, exc_info=error, **kwargs)
        self._send_to_elasticsearch('error', message, kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, **kwargs)
        self._send_to_elasticsearch('warning', message, kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, **kwargs)
    
    def start_timer(self) -> 'Timer':
        """Start a performance timer"""
        return Timer(self)
    
    def _send_to_elasticsearch(self, level: str, message: str, data: Dict[str, Any]):
        """Send log to Elasticsearch"""
        if not self.es_client:
            return
        
        try:
            doc = {
                '@timestamp': datetime.utcnow().isoformat(),
                'level': level,
                'message': message,
                'service': self.config.service,
                'environment': self.config.environment,
                **data,
                **log_context.get()
            }
            
            index_name = f"logs-{self.config.service}-{datetime.utcnow().strftime('%Y.%m.%d')}"
            self.es_client.index(index=index_name, body=doc)
        except Exception as e:
            # Don't fail if ES is down
            print(f"Failed to send log to Elasticsearch: {e}")

class Timer:
    """Performance timer for logging"""
    
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
        self.start_time = datetime.utcnow()
    
    def stop(self, message: str, **kwargs):
        """Stop timer and log duration"""
        duration = (datetime.utcnow() - self.start_time).total_seconds() * 1000
        self.logger.info(
            message,
            duration_ms=duration,
            **kwargs
        )

# Singleton logger instance
_logger: Optional[StructuredLogger] = None

def get_logger(config: Optional[LoggerConfig] = None) -> StructuredLogger:
    """Get or create logger instance"""
    global _logger
    
    if _logger is None:
        if config is None:
            config = LoggerConfig(
                service='claims-askes',
                environment='development'
            )
        _logger = StructuredLogger(config)
    
    return _logger

# Convenience functions
def info(message: str, **kwargs):
    """Log info message"""
    get_logger().info(message, **kwargs)

def error(message: str, error: Optional[Exception] = None, **kwargs):
    """Log error message"""
    get_logger().error(message, error, **kwargs)

def warning(message: str, **kwargs):
    """Log warning message"""
    get_logger().warning(message, **kwargs)

def debug(message: str, **kwargs):
    """Log debug message"""
    get_logger().debug(message, **kwargs)
```

### 6. Validation Package (`claims-validation`)

Shared validation schemas and utilities.

#### Installation
```bash
pip install claims-validation
# Or from local development
pip install -e ./packages/claims_validation
```

#### Schemas

```python
# packages/claims_validation/schemas.py
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field, validator, UUID4, EmailStr
import re

class ClaimType(str, Enum):
    """Claim type enumeration"""
    CASHLESS = "cashless"
    REIMBURSEMENT = "reimbursement"

class ServiceType(str, Enum):
    """Service type enumeration"""
    INPATIENT = "inpatient"
    OUTPATIENT = "outpatient"
    DENTAL = "dental"
    OPTICAL = "optical"
    MATERNITY = "maternity"
    EMERGENCY = "emergency"

class ClaimItemSchema(BaseModel):
    """Claim item validation schema"""
    benefit_code: str = Field(..., min_length=1, max_length=50)
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    quantity: int = Field(default=1, gt=0)
    description: Optional[str] = Field(None, max_length=500)
    
    @validator('amount')
    def validate_amount(cls, v):
        """Ensure amount is positive"""
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

class ClaimSchema(BaseModel):
    """Claim validation schema"""
    member_id: UUID4
    provider_id: UUID4
    service_date: date
    claim_type: ClaimType
    service_type: ServiceType
    items: List[ClaimItemSchema] = Field(..., min_items=1)
    diagnosis_codes: Optional[List[str]] = Field(default_factory=list)
    notes: Optional[str] = Field(None, max_length=1000)
    
    @validator('service_date')
    def validate_service_date(cls, v):
        """Service date cannot be in the future"""
        if v > date.today():
            raise ValueError('Service date cannot be in the future')
        return v
    
    @validator('items')
    def validate_items(cls, v):
        """At least one item required"""
        if not v:
            raise ValueError('At least one claim item is required')
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: str(v)
        }

class MemberSchema(BaseModel):
    """Member validation schema"""
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    date_of_birth: date
    national_id: str = Field(..., regex='^[0-9]{16}$')
    email: EmailStr
    phone: str = Field(..., regex='^(\+62|62|0)[0-9]{9,12}$')
    address: Optional[str] = Field(None, max_length=500)
    
    @validator('date_of_birth')
    def validate_age(cls, v):
        """Must be at least 17 years old"""
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 17:
            raise ValueError('Must be at least 17 years old')
        return v
    
    @validator('national_id')
    def validate_nik(cls, v):
        """Validate Indonesian NIK format"""
        if not re.match(r'^[0-9]{16}$', v):
            raise ValueError('Invalid NIK format')
        
        # Additional NIK validation
        province = int(v[:2])
        if province < 11 or province > 94:
            raise ValueError('Invalid province code in NIK')
        
        return v

class ProviderSchema(BaseModel):
    """Provider validation schema"""
    name: str = Field(..., min_length=3, max_length=200)
    provider_type: str = Field(..., min_length=1, max_length=50)
    tax_id: str = Field(..., regex='^[0-9]{2}\.[0-9]{3}\.[0-9]{3}\.[0-9]{1}-[0-9]{3}\.[0-9]{3}$')
    email: EmailStr
    phone: str = Field(..., regex='^(\+62|62|0)[0-9]{9,12}$')
    address: str = Field(..., min_length=10, max_length=500)
    city: str = Field(..., min_length=2, max_length=100)
    province: str = Field(..., min_length=2, max_length=100)
    postal_code: str = Field(..., regex='^[0-9]{5}$')
    
    @validator('tax_id')
    def validate_npwp(cls, v):
        """Validate Indonesian NPWP format"""
        pattern = r'^[0-9]{2}\.[0-9]{3}\.[0-9]{3}\.[0-9]{1}-[0-9]{3}\.[0-9]{3}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid NPWP format')
        return v

class PaymentSchema(BaseModel):
    """Payment validation schema"""
    claim_id: UUID4
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    payment_method: str = Field(..., min_length=1, max_length=50)
    payment_date: date
    reference_number: str = Field(..., min_length=1, max_length=100)
    bank_name: Optional[str] = Field(None, max_length=100)
    account_number: Optional[str] = Field(None, max_length=50)
    
    @validator('payment_date')
    def validate_payment_date(cls, v):
        """Payment date cannot be in the future"""
        if v > date.today():
            raise ValueError('Payment date cannot be in the future')
        return v
```

### 7. Testing Package (`claims-testing`)

Shared testing utilities and fixtures.

#### Installation
```bash
pip install claims-testing
# Or from local development
pip install -e ./packages/claims_testing
```

#### Test Utilities

```python
# packages/claims_testing/fixtures.py
import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, Any, Optional
import factory
from faker import Faker

fake = Faker('id_ID')  # Indonesian locale

class UserFactory:
    """Factory for creating mock users"""
    
    @staticmethod
    def create(**overrides) -> Dict[str, Any]:
        """Create mock user"""
        return {
            'id': str(uuid.uuid4()),
            'email': fake.email(),
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'roles': ['member'],
            'created_at': datetime.utcnow(),
            **overrides
        }

class ClaimFactory:
    """Factory for creating mock claims"""
    
    @staticmethod
    def create(**overrides) -> Dict[str, Any]:
        """Create mock claim"""
        return {
            'id': str(uuid.uuid4()),
            'claim_number': f'CLM-{datetime.now().strftime("%Y%m%d")}-{fake.random_number(6)}',
            'member_id': str(uuid.uuid4()),
            'provider_id': str(uuid.uuid4()),
            'status': 'submitted',
            'service_date': date.today(),
            'total_amount': Decimal(fake.random_number(digits=6)),
            'created_at': datetime.utcnow(),
            **overrides
        }

class MemberFactory:
    """Factory for creating mock members"""
    
    @staticmethod
    def create(**overrides) -> Dict[str, Any]:
        """Create mock member"""
        return {
            'id': str(uuid.uuid4()),
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'date_of_birth': fake.date_of_birth(minimum_age=17, maximum_age=80),
            'national_id': fake.nik(),  # Indonesian NIK
            'email': fake.email(),
            'phone': fake.phone_number(),
            'address': fake.address(),
            'created_at': datetime.utcnow(),
            **overrides
        }

# packages/claims_testing/database.py
import asyncio
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import Session, sessionmaker
from alembic import command
from alembic.config import Config

class TestDatabase:
    """Test database management"""
    
    def __init__(self, database_url: str = "sqlite:///:memory:"):
        self.database_url = database_url
        self.engine = None
        self.session_factory = None
    
    def initialize(self):
        """Initialize test database"""
        self.engine = create_engine(
            self.database_url,
            echo=False,
            pool_pre_ping=True
        )
        
        # Create all tables
        from claims_database.models import Base
        Base.metadata.create_all(self.engine)
        
        # Create session factory
        self.session_factory = sessionmaker(
            bind=self.engine,
            expire_on_commit=False
        )
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.session_factory()
    
    def seed(self, data: Optional[Dict[str, List[Dict[str, Any]]]] = None):
        """Seed test data"""
        if not data:
            return
        
        with self.get_session() as session:
            for table_name, records in data.items():
                for record in records:
                    session.execute(
                        text(f"INSERT INTO {table_name} VALUES :values"),
                        {"values": record}
                    )
            session.commit()
    
    def cleanup(self):
        """Clean up test data"""
        from claims_database.models import Base
        
        with self.get_session() as session:
            # Delete all data from tables
            for table in reversed(Base.metadata.sorted_tables):
                session.execute(table.delete())
            session.commit()
    
    def destroy(self):
        """Destroy test database"""
        if self.engine:
            self.engine.dispose()

class AsyncTestDatabase:
    """Async test database management"""
    
    def __init__(self, database_url: str = "sqlite+aiosqlite:///:memory:"):
        self.database_url = database_url
        self.engine = None
        self.session_factory = None
    
    async def initialize(self):
        """Initialize async test database"""
        self.engine = create_async_engine(
            self.database_url,
            echo=False,
            pool_pre_ping=True
        )
        
        # Create all tables
        from claims_database.models import Base
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Create session factory
        self.session_factory = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def get_session(self) -> AsyncSession:
        """Get async database session"""
        async with self.session_factory() as session:
            yield session
    
    async def cleanup(self):
        """Clean up test data"""
        from claims_database.models import Base
        
        async with self.session_factory() as session:
            # Delete all data from tables
            for table in reversed(Base.metadata.sorted_tables):
                await session.execute(table.delete())
            await session.commit()
    
    async def destroy(self):
        """Destroy async test database"""
        if self.engine:
            await self.engine.dispose()

# packages/claims_testing/helpers.py
import json
from typing import Dict, Any, Optional
from unittest.mock import Mock, AsyncMock
import httpx
import pytest

def mock_api_response(
    data: Any,
    status_code: int = 200,
    headers: Optional[Dict[str, str]] = None
) -> httpx.Response:
    """Create mock API response"""
    return httpx.Response(
        status_code=status_code,
        json=data if isinstance(data, dict) else json.loads(data),
        headers=headers or {}
    )

def create_mock_service(methods: Dict[str, Any]) -> Mock:
    """Create mock service with specified methods"""
    mock = Mock()
    for method_name, return_value in methods.items():
        setattr(mock, method_name, Mock(return_value=return_value))
    return mock

def create_async_mock_service(methods: Dict[str, Any]) -> Mock:
    """Create async mock service with specified methods"""
    mock = Mock()
    for method_name, return_value in methods.items():
        setattr(mock, method_name, AsyncMock(return_value=return_value))
    return mock

@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    from unittest.mock import MagicMock
    redis_mock = MagicMock()
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.set = AsyncMock(return_value=True)
    redis_mock.delete = AsyncMock(return_value=1)
    redis_mock.expire = AsyncMock(return_value=True)
    return redis_mock
```

## Package Management

### Python Package Structure

```toml
# pyproject.toml (root level)
[tool.poetry]
name = "claims-askes-packages"
version = "1.0.0"
description = "Shared packages for Claims-Askes platform"
authors = ["Claims-Askes Team"]

[tool.poetry.dependencies]
python = "^3.11"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
pytest-cov = "^4.1.0"
black = "^23.7.0"
ruff = "^0.0.280"
mypy = "^1.4.1"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry.extras]
all = [
    "claims-common",
    "claims-auth",
    "claims-database",
    "claims-messaging",
    "claims-logging",
    "claims-validation",
    "claims-testing"
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short --strict-markers"

[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'

[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]
target-version = "py311"
```

### Individual Package Configuration

```toml
# packages/claims_common/pyproject.toml
[tool.poetry]
name = "claims-common"
version = "1.0.0"
description = "Common utilities for Claims-Askes platform"
authors = ["Claims-Askes Team"]
readme = "README.md"
packages = [{include = "claims_common"}]

[tool.poetry.dependencies]
python = "^3.11"
python-dateutil = "^2.8.2"
holidays = "^0.34"
pydantic = "^2.0.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-cov = "^4.1.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### setup.py (Alternative for pip)

```python
# packages/claims_common/setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="claims-common",
    version="1.0.0",
    author="Claims-Askes Team",
    author_email="dev@claims-askes.com",
    description="Common utilities for Claims-Askes platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/claims-askes/packages",
    packages=find_packages(exclude=["tests*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.11",
    install_requires=[
        "python-dateutil>=2.8.2",
        "holidays>=0.34",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "ruff>=0.0.280",
        ],
    },
)
```

## Development Guidelines

### Creating a New Package

```bash
# Create package directory
mkdir packages/claims_newpackage
cd packages/claims_newpackage

# Initialize with Poetry
poetry new claims-newpackage
cd claims-newpackage

# Or manually create structure
mkdir -p claims_newpackage tests
touch claims_newpackage/__init__.py
touch pyproject.toml README.md

# Create pyproject.toml
cat > pyproject.toml << EOF
[tool.poetry]
name = "claims-newpackage"
version = "0.1.0"
description = "New package for Claims-Askes"
authors = ["Your Name <email@example.com>"]
readme = "README.md"
packages = [{include = "claims_newpackage"}]

[tool.poetry.dependencies]
python = "^3.11"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
EOF

# Install dependencies
poetry install

# Create initial module
echo '__version__ = "0.1.0"' > claims_newpackage/__init__.py
```

### Package Versioning

```bash
# Update version with Poetry
poetry version patch  # 0.1.0 -> 0.1.1
poetry version minor  # 0.1.0 -> 0.2.0
poetry version major  # 0.1.0 -> 1.0.0

# Build package
poetry build

# Publish to PyPI (or private registry)
poetry publish --repository private-pypi

# Or use twine
python -m build
twine upload --repository private-pypi dist/*
```

### Installing Packages Locally

```bash
# Install in development mode
pip install -e ./packages/claims_common

# Or with Poetry (from service directory)
poetry add --editable ../../packages/claims_common

# Install from private PyPI
pip install claims-common --index-url https://pypi.claims-askes.com/simple/
```

### Testing Packages

```bash
# Test individual package
cd packages/claims_common
pytest tests/ -v --cov=claims_common

# Test all packages with tox
tox -e py311

# Run tests with coverage
pytest --cov=claims_common --cov-report=html --cov-report=term

# Run type checking
mypy claims_common

# Run linting
ruff check claims_common
black --check claims_common

# Format code
black claims_common
ruff check --fix claims_common
```

### Monorepo Management

```bash
# Use a Makefile for common operations
cat > Makefile << 'EOF'
.PHONY: install test lint format build publish

PACKAGES := claims_common claims_auth claims_database claims_messaging claims_logging claims_validation claims_testing

install:
	@for pkg in $(PACKAGES); do \
		echo "Installing $$pkg..."; \
		cd packages/$$pkg && poetry install && cd ../..; \
	done

test:
	@for pkg in $(PACKAGES); do \
		echo "Testing $$pkg..."; \
		cd packages/$$pkg && pytest tests/ && cd ../..; \
	done

lint:
	@for pkg in $(PACKAGES); do \
		echo "Linting $$pkg..."; \
		cd packages/$$pkg && ruff check . && cd ../..; \
	done

format:
	@for pkg in $(PACKAGES); do \
		echo "Formatting $$pkg..."; \
		cd packages/$$pkg && black . && cd ../..; \
	done

build:
	@for pkg in $(PACKAGES); do \
		echo "Building $$pkg..."; \
		cd packages/$$pkg && poetry build && cd ../..; \
	done

publish:
	@for pkg in $(PACKAGES); do \
		echo "Publishing $$pkg..."; \
		cd packages/$$pkg && poetry publish --repository private && cd ../..; \
	done
EOF

# Run all tests
make test

# Build all packages
make build
```

## Best Practices

### 1. Package Design Principles

- **Single Responsibility**: Each package should have one clear purpose
- **Minimal Dependencies**: Keep external dependencies to a minimum
- **Version Independence**: Packages should be independently versioned
- **Backward Compatibility**: Maintain backward compatibility in minor versions
- **Documentation**: Every package must have comprehensive documentation

### 2. Code Quality

- **Type Hints**: All packages must use Python type hints
- **Testing**: Minimum 80% code coverage
- **Linting**: Consistent code style using Black and Ruff
- **Documentation**: Docstrings for all public APIs (Google style)
- **Type Checking**: Use mypy for static type checking

### 3. Security

- **Dependency Scanning**: Regular vulnerability scans with pip-audit
- **Access Control**: Restricted PyPI registry access
- **Code Review**: All changes require peer review
- **Secrets Management**: No hardcoded secrets, use environment variables

### 4. Documentation Standards

```python
# Example of proper documentation
def process_claim(claim_id: str, user_id: str) -> Dict[str, Any]:
    """Process a claim for adjudication.
    
    Args:
        claim_id: Unique identifier of the claim
        user_id: ID of the user processing the claim
    
    Returns:
        Dictionary containing processing results with keys:
            - status: Processing status ('approved', 'rejected', 'pending')
            - amount: Approved amount if applicable
            - reasons: List of rejection reasons if applicable
    
    Raises:
        ClaimNotFoundError: If claim_id doesn't exist
        PermissionError: If user lacks permission to process claims
    
    Example:
        >>> result = process_claim('CLM-123', 'USR-456')
        >>> print(result['status'])
        'approved'
    """
    # Implementation
    pass
```

## Support

- **Package Team**: packages@claims-askes.com
- **Documentation**: Internal wiki
- **Issues**: GitHub Issues
- **PyPI Registry**: pypi.claims-askes.com
- **Package Repository**: https://github.com/claims-askes/packages

## License

Proprietary - All rights reserved