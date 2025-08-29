# Shared Packages Documentation

## Overview

This directory contains shared libraries, components, and utilities used across the Claims-Askes platform. These packages promote code reuse, maintain consistency, and reduce duplication across microservices and applications.

## Package Structure

```
packages/
├── common/              # Common utilities and helpers
├── auth/                # Authentication & authorization
├── database/            # Database utilities and models
├── messaging/           # Message queue abstractions
├── logging/             # Centralized logging
├── monitoring/          # Monitoring and metrics
├── validation/          # Data validation schemas
├── ui-components/       # Shared React components
├── mobile-components/   # Shared React Native components
└── testing/             # Testing utilities
```

## Core Packages

### 1. Common Package (`@claims-askes/common`)

Shared utilities and helper functions used across all services.

#### Installation
```bash
npm install @claims-askes/common
```

#### Features

```typescript
// packages/common/src/index.ts

// Date utilities
export * from './utils/date';
export * from './utils/currency';
export * from './utils/validation';
export * from './utils/crypto';

// Constants
export * from './constants/status';
export * from './constants/errors';
export * from './constants/regex';

// Types
export * from './types/common';
export * from './types/api';
export * from './types/domain';
```

#### Usage Examples

```typescript
import { formatCurrency, validateNIK, ClaimStatus } from '@claims-askes/common';

// Format Indonesian Rupiah
const amount = formatCurrency(5000000); // "Rp 5.000.000"

// Validate Indonesian National ID
const isValid = validateNIK('3275010101900001'); // true

// Use common enums
const status: ClaimStatus = ClaimStatus.APPROVED;
```

#### Utilities

```typescript
// Date utilities
export const formatDate = (date: Date, format: string): string => {
  // Implementation
};

export const addBusinessDays = (date: Date, days: number): Date => {
  // Skip weekends and holidays
};

export const getQuarter = (date: Date): number => {
  return Math.floor(date.getMonth() / 3) + 1;
};

// Currency utilities
export const formatRupiah = (amount: number): string => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
  }).format(amount);
};

export const parseRupiah = (value: string): number => {
  return parseInt(value.replace(/[^0-9]/g, ''));
};

// Validation utilities
export const validateEmail = (email: string): boolean => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
};

export const validatePhoneNumber = (phone: string): boolean => {
  // Indonesian phone number format
  return /^(\+62|62|0)[0-9]{9,12}$/.test(phone);
};

export const validateNPWP = (npwp: string): boolean => {
  // Indonesian tax number validation
  return /^[0-9]{2}\.[0-9]{3}\.[0-9]{3}\.[0-9]{1}-[0-9]{3}\.[0-9]{3}$/.test(npwp);
};
```

### 2. Authentication Package (`@claims-askes/auth`)

Centralized authentication and authorization utilities.

#### Installation
```bash
npm install @claims-askes/auth
```

#### Features

```typescript
// packages/auth/src/index.ts

// JWT utilities
export * from './jwt/encoder';
export * from './jwt/decoder';
export * from './jwt/validator';

// Middleware
export * from './middleware/authenticate';
export * from './middleware/authorize';

// Services
export * from './services/auth-service';
export * from './services/token-service';

// Types
export * from './types/user';
export * from './types/token';
export * from './types/permissions';
```

#### JWT Service

```typescript
// packages/auth/src/services/jwt-service.ts
import jwt from 'jsonwebtoken';

export interface JWTPayload {
  sub: string;  // User ID
  email: string;
  roles: string[];
  permissions: string[];
  iat?: number;
  exp?: number;
}

export class JWTService {
  private readonly secret: string;
  private readonly expiresIn: string;
  private readonly refreshSecret: string;
  
  constructor(config: JWTConfig) {
    this.secret = config.secret;
    this.expiresIn = config.expiresIn || '1h';
    this.refreshSecret = config.refreshSecret;
  }
  
  generateToken(payload: JWTPayload): string {
    return jwt.sign(payload, this.secret, {
      expiresIn: this.expiresIn,
      issuer: 'claims-askes',
      audience: 'claims-askes-api'
    });
  }
  
  generateRefreshToken(userId: string): string {
    return jwt.sign(
      { sub: userId, type: 'refresh' },
      this.refreshSecret,
      { expiresIn: '7d' }
    );
  }
  
  verifyToken(token: string): JWTPayload {
    return jwt.verify(token, this.secret, {
      issuer: 'claims-askes',
      audience: 'claims-askes-api'
    }) as JWTPayload;
  }
  
  verifyRefreshToken(token: string): { sub: string } {
    return jwt.verify(token, this.refreshSecret) as { sub: string };
  }
  
  decodeToken(token: string): JWTPayload | null {
    return jwt.decode(token) as JWTPayload;
  }
}
```

#### Authentication Middleware

```typescript
// packages/auth/src/middleware/authenticate.ts
import { Request, Response, NextFunction } from 'express';

export interface AuthenticatedRequest extends Request {
  user?: {
    id: string;
    email: string;
    roles: string[];
    permissions: string[];
  };
}

export const authenticate = (jwtService: JWTService) => {
  return async (
    req: AuthenticatedRequest,
    res: Response,
    next: NextFunction
  ) => {
    try {
      const token = extractToken(req);
      
      if (!token) {
        return res.status(401).json({ error: 'No token provided' });
      }
      
      const payload = jwtService.verifyToken(token);
      
      req.user = {
        id: payload.sub,
        email: payload.email,
        roles: payload.roles,
        permissions: payload.permissions
      };
      
      next();
    } catch (error) {
      if (error.name === 'TokenExpiredError') {
        return res.status(401).json({ error: 'Token expired' });
      }
      
      return res.status(401).json({ error: 'Invalid token' });
    }
  };
};

function extractToken(req: Request): string | null {
  const authHeader = req.headers.authorization;
  
  if (authHeader && authHeader.startsWith('Bearer ')) {
    return authHeader.substring(7);
  }
  
  return req.cookies?.token || null;
}
```

#### Authorization Middleware

```typescript
// packages/auth/src/middleware/authorize.ts

export const authorize = (...requiredRoles: string[]) => {
  return (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Not authenticated' });
    }
    
    const hasRole = requiredRoles.some(role => 
      req.user!.roles.includes(role)
    );
    
    if (!hasRole) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }
    
    next();
  };
};

export const requirePermission = (...permissions: string[]) => {
  return (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Not authenticated' });
    }
    
    const hasPermission = permissions.every(permission =>
      req.user!.permissions.includes(permission)
    );
    
    if (!hasPermission) {
      return res.status(403).json({ 
        error: 'Missing required permissions',
        required: permissions
      });
    }
    
    next();
  };
};
```

### 3. Database Package (`@claims-askes/database`)

Shared database utilities, models, and migrations.

#### Installation
```bash
npm install @claims-askes/database
```

#### Features

```typescript
// packages/database/src/index.ts

// Connection management
export * from './connection/postgres';
export * from './connection/redis';
export * from './connection/mongodb';

// Base models
export * from './models/base-entity';
export * from './models/audit-entity';

// Repositories
export * from './repositories/base-repository';
export * from './repositories/cache-repository';

// Utilities
export * from './utils/pagination';
export * from './utils/transaction';
export * from './utils/migration';
```

#### Base Entity

```typescript
// packages/database/src/models/base-entity.ts
import { Entity, PrimaryGeneratedColumn, CreateDateColumn, UpdateDateColumn } from 'typeorm';

@Entity()
export abstract class BaseEntity {
  @PrimaryGeneratedColumn('uuid')
  id: string;
  
  @CreateDateColumn({ type: 'timestamptz' })
  createdAt: Date;
  
  @UpdateDateColumn({ type: 'timestamptz' })
  updatedAt: Date;
}

@Entity()
export abstract class AuditableEntity extends BaseEntity {
  @Column({ nullable: true })
  createdBy: string;
  
  @Column({ nullable: true })
  updatedBy: string;
  
  @Column({ type: 'jsonb', nullable: true })
  metadata: Record<string, any>;
}
```

#### Base Repository

```typescript
// packages/database/src/repositories/base-repository.ts
import { Repository, FindManyOptions, DeepPartial } from 'typeorm';
import { BaseEntity } from '../models/base-entity';

export interface PaginationOptions {
  page: number;
  limit: number;
  sortBy?: string;
  sortOrder?: 'ASC' | 'DESC';
}

export interface PaginatedResult<T> {
  data: T[];
  total: number;
  page: number;
  pages: number;
  limit: number;
}

export abstract class BaseRepository<T extends BaseEntity> {
  constructor(protected repository: Repository<T>) {}
  
  async findById(id: string): Promise<T | null> {
    return this.repository.findOne({ where: { id } as any });
  }
  
  async findAll(options?: FindManyOptions<T>): Promise<T[]> {
    return this.repository.find(options);
  }
  
  async findPaginated(
    options: PaginationOptions,
    where?: FindManyOptions<T>['where']
  ): Promise<PaginatedResult<T>> {
    const { page, limit, sortBy = 'createdAt', sortOrder = 'DESC' } = options;
    
    const [data, total] = await this.repository.findAndCount({
      where,
      skip: (page - 1) * limit,
      take: limit,
      order: { [sortBy]: sortOrder } as any
    });
    
    return {
      data,
      total,
      page,
      pages: Math.ceil(total / limit),
      limit
    };
  }
  
  async create(data: DeepPartial<T>): Promise<T> {
    const entity = this.repository.create(data);
    return this.repository.save(entity);
  }
  
  async update(id: string, data: DeepPartial<T>): Promise<T | null> {
    await this.repository.update(id, data as any);
    return this.findById(id);
  }
  
  async delete(id: string): Promise<boolean> {
    const result = await this.repository.delete(id);
    return result.affected !== 0;
  }
  
  async softDelete(id: string): Promise<boolean> {
    const result = await this.repository.softDelete(id);
    return result.affected !== 0;
  }
}
```

### 4. Messaging Package (`@claims-askes/messaging`)

Message queue abstractions for event-driven architecture.

#### Installation
```bash
npm install @claims-askes/messaging
```

#### Features

```typescript
// packages/messaging/src/index.ts

// Publishers
export * from './publishers/event-publisher';
export * from './publishers/queue-publisher';

// Consumers
export * from './consumers/event-consumer';
export * from './consumers/queue-consumer';

// Events
export * from './events/base-event';
export * from './events/claim-events';
export * from './events/member-events';

// Utilities
export * from './utils/retry';
export * from './utils/dead-letter';
```

#### Event Publisher

```typescript
// packages/messaging/src/publishers/event-publisher.ts
import amqp from 'amqplib';

export interface Event {
  type: string;
  data: any;
  metadata: {
    timestamp: Date;
    correlationId: string;
    userId?: string;
  };
}

export class EventPublisher {
  private connection: amqp.Connection;
  private channel: amqp.Channel;
  
  async connect(url: string): Promise<void> {
    this.connection = await amqp.connect(url);
    this.channel = await this.connection.createChannel();
    
    // Setup exchange
    await this.channel.assertExchange('events', 'topic', {
      durable: true
    });
  }
  
  async publish(event: Event): Promise<void> {
    const routingKey = event.type.replace(/\./g, '_');
    const message = Buffer.from(JSON.stringify(event));
    
    this.channel.publish(
      'events',
      routingKey,
      message,
      {
        persistent: true,
        contentType: 'application/json',
        timestamp: Date.now()
      }
    );
  }
  
  async publishBatch(events: Event[]): Promise<void> {
    for (const event of events) {
      await this.publish(event);
    }
  }
  
  async close(): Promise<void> {
    await this.channel.close();
    await this.connection.close();
  }
}
```

#### Event Consumer

```typescript
// packages/messaging/src/consumers/event-consumer.ts

export interface EventHandler<T = any> {
  handle(event: Event<T>): Promise<void>;
}

export class EventConsumer {
  private handlers: Map<string, EventHandler[]> = new Map();
  
  async connect(url: string): Promise<void> {
    this.connection = await amqp.connect(url);
    this.channel = await this.connection.createChannel();
    
    await this.channel.assertExchange('events', 'topic', {
      durable: true
    });
  }
  
  subscribe(eventType: string, handler: EventHandler): void {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, []);
    }
    
    this.handlers.get(eventType)!.push(handler);
  }
  
  async start(queueName: string): Promise<void> {
    // Create queue
    await this.channel.assertQueue(queueName, {
      durable: true,
      arguments: {
        'x-dead-letter-exchange': 'dlx',
        'x-message-ttl': 3600000 // 1 hour
      }
    });
    
    // Bind queue to events
    for (const eventType of this.handlers.keys()) {
      const routingKey = eventType.replace(/\./g, '_');
      await this.channel.bindQueue(queueName, 'events', routingKey);
    }
    
    // Start consuming
    await this.channel.consume(queueName, async (msg) => {
      if (!msg) return;
      
      try {
        const event = JSON.parse(msg.content.toString());
        const handlers = this.handlers.get(event.type) || [];
        
        for (const handler of handlers) {
          await handler.handle(event);
        }
        
        this.channel.ack(msg);
      } catch (error) {
        console.error('Error processing event:', error);
        
        // Retry logic
        const retryCount = (msg.properties.headers['x-retry-count'] || 0) + 1;
        
        if (retryCount <= 3) {
          // Republish with delay
          setTimeout(() => {
            this.channel.sendToQueue(
              queueName,
              msg.content,
              {
                ...msg.properties,
                headers: {
                  ...msg.properties.headers,
                  'x-retry-count': retryCount
                }
              }
            );
          }, retryCount * 1000);
        } else {
          // Send to dead letter queue
          this.channel.nack(msg, false, false);
        }
      }
    });
  }
}
```

### 5. Logging Package (`@claims-askes/logging`)

Centralized logging with structured logs.

#### Installation
```bash
npm install @claims-askes/logging
```

#### Logger Implementation

```typescript
// packages/logging/src/logger.ts
import winston from 'winston';
import { ElasticsearchTransport } from 'winston-elasticsearch';

export interface LogContext {
  service?: string;
  userId?: string;
  correlationId?: string;
  [key: string]: any;
}

export class Logger {
  private winston: winston.Logger;
  private context: LogContext = {};
  
  constructor(config: LoggerConfig) {
    this.winston = winston.createLogger({
      level: config.level || 'info',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json()
      ),
      defaultMeta: {
        service: config.service,
        environment: config.environment
      },
      transports: this.createTransports(config)
    });
  }
  
  private createTransports(config: LoggerConfig): winston.transport[] {
    const transports: winston.transport[] = [
      new winston.transports.Console({
        format: winston.format.combine(
          winston.format.colorize(),
          winston.format.simple()
        )
      })
    ];
    
    if (config.elasticsearch) {
      transports.push(new ElasticsearchTransport({
        clientOpts: config.elasticsearch,
        index: `logs-${config.service}`,
        level: 'info'
      }));
    }
    
    if (config.file) {
      transports.push(new winston.transports.File({
        filename: config.file,
        level: 'error'
      }));
    }
    
    return transports;
  }
  
  setContext(context: LogContext): void {
    this.context = { ...this.context, ...context };
  }
  
  clearContext(): void {
    this.context = {};
  }
  
  info(message: string, meta?: any): void {
    this.winston.info(message, { ...this.context, ...meta });
  }
  
  error(message: string, error?: Error, meta?: any): void {
    this.winston.error(message, {
      ...this.context,
      ...meta,
      error: {
        message: error?.message,
        stack: error?.stack,
        name: error?.name
      }
    });
  }
  
  warn(message: string, meta?: any): void {
    this.winston.warn(message, { ...this.context, ...meta });
  }
  
  debug(message: string, meta?: any): void {
    this.winston.debug(message, { ...this.context, ...meta });
  }
  
  // Performance logging
  startTimer(): () => void {
    const start = Date.now();
    
    return (message: string, meta?: any) => {
      const duration = Date.now() - start;
      this.info(message, {
        ...meta,
        duration,
        durationMs: duration
      });
    };
  }
}
```

### 6. Validation Package (`@claims-askes/validation`)

Shared validation schemas and utilities.

#### Installation
```bash
npm install @claims-askes/validation
```

#### Schemas

```typescript
// packages/validation/src/schemas/claim.ts
import * as yup from 'yup';

export const claimSchema = yup.object({
  memberId: yup.string().uuid().required(),
  providerId: yup.string().uuid().required(),
  serviceDate: yup.date().max(new Date()).required(),
  claimType: yup.string().oneOf(['cashless', 'reimbursement']).required(),
  serviceType: yup.string().oneOf([
    'inpatient',
    'outpatient',
    'dental',
    'optical',
    'maternity'
  ]).required(),
  items: yup.array().of(
    yup.object({
      benefitCode: yup.string().required(),
      amount: yup.number().positive().required(),
      quantity: yup.number().positive().integer().default(1)
    })
  ).min(1).required()
});

export const memberSchema = yup.object({
  firstName: yup.string().required().min(2).max(100),
  lastName: yup.string().required().min(2).max(100),
  dateOfBirth: yup.date()
    .max(new Date())
    .test('age', 'Must be at least 17 years old', (value) => {
      if (!value) return false;
      const age = new Date().getFullYear() - value.getFullYear();
      return age >= 17;
    })
    .required(),
  nationalId: yup.string()
    .matches(/^[0-9]{16}$/, 'Invalid NIK format')
    .required(),
  email: yup.string().email().required(),
  phone: yup.string()
    .matches(/^(\+62|62|0)[0-9]{9,12}$/, 'Invalid phone number')
    .required()
});
```

### 7. UI Components Package (`@claims-askes/ui-components`)

Shared React components for web applications.

#### Installation
```bash
npm install @claims-askes/ui-components
```

#### Components

```tsx
// packages/ui-components/src/components/Button/Button.tsx
import React from 'react';
import styled from 'styled-components';

export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'small' | 'medium' | 'large';
  loading?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
}

const StyledButton = styled.button<ButtonProps>`
  padding: ${props => {
    switch (props.size) {
      case 'small': return '8px 16px';
      case 'large': return '16px 32px';
      default: return '12px 24px';
    }
  }};
  
  background-color: ${props => {
    switch (props.variant) {
      case 'secondary': return '#6c757d';
      case 'danger': return '#dc3545';
      default: return '#007bff';
    }
  }};
  
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  opacity: ${props => props.disabled ? 0.6 : 1};
  width: ${props => props.fullWidth ? '100%' : 'auto'};
  
  &:hover:not(:disabled) {
    opacity: 0.9;
  }
`;

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'medium',
  loading = false,
  disabled = false,
  fullWidth = false,
  onClick,
  children
}) => {
  return (
    <StyledButton
      variant={variant}
      size={size}
      disabled={disabled || loading}
      fullWidth={fullWidth}
      onClick={onClick}
    >
      {loading ? 'Loading...' : children}
    </StyledButton>
  );
};
```

#### Data Table Component

```tsx
// packages/ui-components/src/components/DataTable/DataTable.tsx
import React, { useState } from 'react';

export interface Column<T> {
  key: keyof T;
  header: string;
  render?: (value: any, row: T) => React.ReactNode;
  sortable?: boolean;
  width?: string;
}

export interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  onRowClick?: (row: T) => void;
  loading?: boolean;
  pagination?: {
    page: number;
    pageSize: number;
    total: number;
    onChange: (page: number, pageSize: number) => void;
  };
}

export function DataTable<T extends { id: string }>({
  columns,
  data,
  onRowClick,
  loading,
  pagination
}: DataTableProps<T>) {
  const [sortBy, setSortBy] = useState<keyof T | null>(null);
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  
  const handleSort = (column: keyof T) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('asc');
    }
  };
  
  const sortedData = [...data].sort((a, b) => {
    if (!sortBy) return 0;
    
    const aVal = a[sortBy];
    const bVal = b[sortBy];
    
    if (aVal < bVal) return sortOrder === 'asc' ? -1 : 1;
    if (aVal > bVal) return sortOrder === 'asc' ? 1 : -1;
    return 0;
  });
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  return (
    <div>
      <table>
        <thead>
          <tr>
            {columns.map(column => (
              <th
                key={String(column.key)}
                style={{ width: column.width }}
                onClick={() => column.sortable && handleSort(column.key)}
              >
                {column.header}
                {sortBy === column.key && (
                  <span>{sortOrder === 'asc' ? ' ▲' : ' ▼'}</span>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sortedData.map(row => (
            <tr
              key={row.id}
              onClick={() => onRowClick?.(row)}
              style={{ cursor: onRowClick ? 'pointer' : 'default' }}
            >
              {columns.map(column => (
                <td key={String(column.key)}>
                  {column.render
                    ? column.render(row[column.key], row)
                    : String(row[column.key])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      
      {pagination && (
        <div>
          <button
            onClick={() => pagination.onChange(pagination.page - 1, pagination.pageSize)}
            disabled={pagination.page === 1}
          >
            Previous
          </button>
          <span>
            Page {pagination.page} of {Math.ceil(pagination.total / pagination.pageSize)}
          </span>
          <button
            onClick={() => pagination.onChange(pagination.page + 1, pagination.pageSize)}
            disabled={pagination.page >= Math.ceil(pagination.total / pagination.pageSize)}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
```

### 8. Mobile Components Package (`@claims-askes/mobile-components`)

Shared React Native components for mobile applications.

#### Installation
```bash
npm install @claims-askes/mobile-components
```

#### Components

```tsx
// packages/mobile-components/src/components/Card/Card.tsx
import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export interface CardProps {
  title?: string;
  subtitle?: string;
  onPress?: () => void;
  children: React.ReactNode;
  elevation?: number;
}

export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  onPress,
  children,
  elevation = 2
}) => {
  const Container = onPress ? TouchableOpacity : View;
  
  return (
    <Container
      style={[styles.card, { elevation }]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      {title && (
        <View style={styles.header}>
          <Text style={styles.title}>{title}</Text>
          {subtitle && <Text style={styles.subtitle}>{subtitle}</Text>}
        </View>
      )}
      <View style={styles.content}>
        {children}
      </View>
    </Container>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 16,
    marginVertical: 8,
    marginHorizontal: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84
  },
  header: {
    marginBottom: 12
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333'
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    marginTop: 4
  },
  content: {
    // Content styles
  }
});
```

### 9. Testing Package (`@claims-askes/testing`)

Shared testing utilities and fixtures.

#### Installation
```bash
npm install -D @claims-askes/testing
```

#### Test Utilities

```typescript
// packages/testing/src/utils/test-helpers.ts

export const createMockUser = (overrides?: Partial<User>): User => {
  return {
    id: 'test-user-id',
    email: 'test@example.com',
    firstName: 'Test',
    lastName: 'User',
    roles: ['member'],
    ...overrides
  };
};

export const createMockClaim = (overrides?: Partial<Claim>): Claim => {
  return {
    id: 'test-claim-id',
    claimNumber: 'CLM-2024-000001',
    memberId: 'test-member-id',
    providerId: 'test-provider-id',
    status: 'submitted',
    serviceDate: new Date('2024-01-15'),
    totalAmount: 500000,
    ...overrides
  };
};

export const setupTestDatabase = async () => {
  // Setup test database
};

export const cleanupTestDatabase = async () => {
  // Cleanup test database
};

export const mockApiResponse = (data: any, status = 200) => {
  return Promise.resolve({
    status,
    data,
    headers: {},
    config: {}
  });
};
```

#### Test Database Setup

```typescript
// packages/testing/src/database/test-db.ts
import { DataSource } from 'typeorm';

export class TestDatabase {
  private dataSource: DataSource;
  
  async initialize(): Promise<void> {
    this.dataSource = new DataSource({
      type: 'sqlite',
      database: ':memory:',
      synchronize: true,
      logging: false,
      entities: ['src/**/*.entity.ts']
    });
    
    await this.dataSource.initialize();
  }
  
  async seed(): Promise<void> {
    // Seed test data
  }
  
  async cleanup(): Promise<void> {
    const entities = this.dataSource.entityMetadatas;
    
    for (const entity of entities) {
      const repository = this.dataSource.getRepository(entity.name);
      await repository.clear();
    }
  }
  
  async destroy(): Promise<void> {
    await this.dataSource.destroy();
  }
  
  getDataSource(): DataSource {
    return this.dataSource;
  }
}
```

## Package Management

### Monorepo Structure with Lerna

```json
// lerna.json
{
  "version": "independent",
  "npmClient": "npm",
  "workspaces": [
    "packages/*",
    "services/*",
    "frontend/apps/*",
    "mobile/apps/*"
  ],
  "command": {
    "publish": {
      "conventionalCommits": true,
      "message": "chore(release): publish",
      "registry": "https://npm.claims-askes.com",
      "allowBranch": ["main", "release/*"]
    },
    "version": {
      "allowBranch": "main",
      "conventionalCommits": true
    }
  }
}
```

### Package.json Configuration

```json
// packages/common/package.json
{
  "name": "@claims-askes/common",
  "version": "1.0.0",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "files": [
    "dist"
  ],
  "scripts": {
    "build": "tsc",
    "test": "jest",
    "lint": "eslint src --ext .ts",
    "prepublishOnly": "npm run build"
  },
  "dependencies": {
    "date-fns": "^2.30.0",
    "lodash": "^4.17.21"
  },
  "devDependencies": {
    "@types/jest": "^29.0.0",
    "@types/node": "^18.0.0",
    "jest": "^29.0.0",
    "typescript": "^5.0.0"
  },
  "publishConfig": {
    "access": "restricted",
    "registry": "https://npm.claims-askes.com"
  }
}
```

## Development Guidelines

### Creating a New Package

```bash
# Create package directory
mkdir packages/new-package
cd packages/new-package

# Initialize package
npm init -y

# Add TypeScript
npm install -D typescript @types/node

# Create tsconfig
cat > tsconfig.json << EOF
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "**/*.test.ts"]
}
EOF

# Create source directory
mkdir src
echo 'export const hello = "world";' > src/index.ts

# Build package
npm run build
```

### Package Versioning

```bash
# Version all packages
lerna version

# Version specific package
lerna version --scope=@claims-askes/common

# Publish packages
lerna publish

# Publish specific package
lerna publish --scope=@claims-askes/common
```

### Testing Packages

```bash
# Test all packages
lerna run test

# Test specific package
lerna run test --scope=@claims-askes/common

# Test affected packages
lerna run test --since main
```

## Best Practices

### 1. Package Design Principles

- **Single Responsibility**: Each package should have one clear purpose
- **Minimal Dependencies**: Keep external dependencies to a minimum
- **Version Independence**: Packages should be independently versioned
- **Backward Compatibility**: Maintain backward compatibility in minor versions
- **Documentation**: Every package must have comprehensive documentation

### 2. Code Quality

- **TypeScript**: All packages must be written in TypeScript
- **Testing**: Minimum 80% code coverage
- **Linting**: Consistent code style across all packages
- **Documentation**: JSDoc comments for all public APIs

### 3. Security

- **Dependency Scanning**: Regular vulnerability scans
- **Access Control**: Restricted npm registry access
- **Code Review**: All changes require peer review
- **Secrets Management**: No hardcoded secrets

## Support

- **Package Team**: packages@claims-askes.com
- **Documentation**: Internal wiki
- **Issues**: GitHub Issues
- **NPM Registry**: npm.claims-askes.com

## License

Proprietary - All rights reserved