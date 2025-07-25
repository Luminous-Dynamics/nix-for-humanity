# NixOS GUI Caching Layer

## Overview

The NixOS GUI implements a comprehensive multi-tier caching system to improve performance and reduce load on the system. The caching layer operates at both the backend and frontend levels.

## Architecture

```
┌─────────────────────────────────────────────┐
│              Browser                         │
│  ┌─────────────────────────────────────┐   │
│  │   Memory Cache (Runtime)             │   │
│  │   - Fast access                      │   │
│  │   - Limited size                     │   │
│  │   - Per-session                      │   │
│  └──────────────┬──────────────────────┘   │
│  ┌──────────────▼──────────────────────┐   │
│  │   Browser Storage (Persistent)       │   │
│  │   - LocalStorage/SessionStorage      │   │
│  │   - Survives refreshes               │   │
│  │   - Size limited by browser          │   │
│  └──────────────┬──────────────────────┘   │
└─────────────────┼───────────────────────────┘
                  │ HTTP/WebSocket
┌─────────────────▼───────────────────────────┐
│            Backend Server                    │
│  ┌─────────────────────────────────────┐   │
│  │   Redis Cache (Primary)              │   │
│  │   - Distributed                      │   │
│  │   - Persistent                       │   │
│  │   - Shared across instances          │   │
│  └──────────────┬──────────────────────┘   │
│  ┌──────────────▼──────────────────────┐   │
│  │   Memory Cache (Fallback)            │   │
│  │   - Used when Redis unavailable      │   │
│  │   - Per-instance                     │   │
│  │   - Limited capacity                 │   │
│  └──────────────┬──────────────────────┘   │
└─────────────────┼───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│          System Operations                   │
└─────────────────────────────────────────────┘
```

## Backend Caching

### Cache Service

The main cache service provides a unified interface for caching operations:

```javascript
const { getCache } = require('./services/cache');
const cache = getCache();

// Basic operations
await cache.setCache('namespace', 'key', value, ttl);
const value = await cache.getCache('namespace', 'key');
await cache.invalidate('namespace', 'key');
```

### TTL Configuration

Different data types have different cache durations:

| Data Type | TTL | Reason |
|-----------|-----|--------|
| Packages | 1 hour | Package info changes rarely |
| Search Results | 30 minutes | Balance freshness and performance |
| Services | 1 minute | Service status changes frequently |
| System Info | 1 minute | Metrics need to be current |
| Generations | 10 minutes | List changes occasionally |
| Configuration | 30 seconds | May be actively edited |

### Cache Strategies

#### 1. Get or Set
Standard caching pattern - check cache, fetch if missing:
```javascript
const data = await cache.getOrSet(
  'namespace',
  'key',
  async () => fetchDataFromSource(),
  ttl
);
```

#### 2. Stale While Revalidate
Return cached data immediately, refresh in background:
```javascript
const data = await cache.staleWhileRevalidate(
  'namespace',
  'key',
  async () => fetchFreshData(),
  ttl
);
```

#### 3. Refresh
Always fetch fresh data and update cache:
```javascript
const data = await cache.refresh(
  'namespace',
  'key',
  async () => fetchLatestData(),
  ttl
);
```

### Cache Invalidation

Automatic invalidation based on system events:

```javascript
// Package installed -> invalidate package caches
eventEmitter.on('package.installed', () => {
  cache.invalidate('packages');
  cache.invalidate('searchResults');
});

// System rebuilt -> clear all caches
eventEmitter.on('system.rebuilt', () => {
  cache.invalidatePattern('*');
});
```

### Fallback Cache

When Redis is unavailable, the system falls back to an in-memory cache:
- Limited capacity (100MB default)
- LRU eviction policy
- Shorter TTLs
- Per-instance (not shared)

## Frontend Caching

### Browser Cache

Persistent storage using localStorage:

```javascript
import { BrowserCache } from './utils/cache';

const cache = new BrowserCache({
  prefix: 'nixos-gui:',
  defaultTTL: 300000, // 5 minutes
  maxSize: 50 * 1024 * 1024 // 50MB
});

// Store data
cache.set('packages', 'firefox', packageData);

// Retrieve data
const data = cache.get('packages', 'firefox');

// Invalidate
cache.invalidate('packages', 'firefox');
```

### Memory Cache

Runtime cache for frequently accessed data:

```javascript
import { MemoryCache } from './utils/cache';

const cache = new MemoryCache({
  maxEntries: 1000,
  defaultTTL: 60000 // 1 minute
});
```

### API Client Integration

The API client automatically handles caching:

```javascript
import api from './api';

// Cached request (automatic)
const packages = await api.getInstalledPackages();

// Force refresh
api.clearCache('packages');
const freshPackages = await api.getInstalledPackages();

// View cache statistics
const stats = api.getCacheStats();
console.log(`Cache hit rate: ${stats.browser.hitRate}`);
```

## Cache Warming

Pre-populate caches for better initial performance:

### On Server Start
```javascript
// Automatically warm essential caches
await warmupService.warmupEssentialCaches();
```

### On User Login
```javascript
// Warm user-specific caches
await warmupService.warmupUserCaches(user);
```

### Manual Warming
```bash
# Via API endpoint
curl -X POST /api/cache/warmup \
  -H "Authorization: Bearer $TOKEN"
```

## Performance Optimization

### Batch Operations

Fetch multiple items efficiently:
```javascript
const packages = await cache.getBatch('packages', [
  'firefox',
  'chromium',
  'vscode'
]);
```

### Compression

Large values are automatically compressed:
- Threshold: 1KB
- Algorithm: gzip
- Transparent compression/decompression

### Pipeline Operations

Redis commands are pipelined for efficiency:
- Batch size: 100 commands
- Automatic flushing
- Error handling per command

## Monitoring

### Cache Statistics

Monitor cache performance:

```javascript
const stats = cache.getStats();
// {
//   hits: 1250,
//   misses: 340,
//   errors: 2,
//   hitRate: "78.61%",
//   fallbackHits: 45,
//   connected: true,
//   fallbackSize: 234
// }
```

### Metrics Tracked

- Hit rate
- Error rate
- Memory usage
- Key count
- Eviction count
- Average response time

### Alerts

Automatic alerts for:
- Low hit rate (<50%)
- High error rate (>10%)
- Memory threshold (>90%)
- Redis connection loss

## API Endpoints

### Cache Management

```bash
# Get cache statistics
GET /api/cache/stats

# Clear cache
DELETE /api/cache?namespace=packages

# Get cache configuration
GET /api/cache/config

# Warm up caches
POST /api/cache/warmup
```

## Configuration

### Backend Configuration

```javascript
// backend/config/cache.js
module.exports = {
  redis: {
    host: 'localhost',
    port: 6379,
    keyPrefix: 'nixos-gui:'
  },
  ttl: {
    packages: 3600,
    services: 60,
    // ...
  },
  memory: {
    maxSize: 100 * 1024 * 1024, // 100MB
    maxEntries: 10000
  }
};
```

### Frontend Configuration

```javascript
// When initializing API client
const api = new NixOSAPI({
  cache: {
    browser: {
      maxSize: 50 * 1024 * 1024, // 50MB
      defaultTTL: 300000 // 5 minutes
    },
    memory: {
      maxEntries: 500,
      defaultTTL: 60000 // 1 minute
    }
  }
});
```

## Best Practices

### 1. Choose Appropriate TTLs
- Static data: Longer TTLs (hours)
- Dynamic data: Shorter TTLs (minutes)
- Real-time data: No caching or very short TTL

### 2. Cache Keys
- Use consistent key patterns
- Include relevant parameters
- Avoid overly specific keys

### 3. Cache Invalidation
- Invalidate on data changes
- Use patterns for bulk invalidation
- Consider cascade invalidation

### 4. Error Handling
- Always have fallback behavior
- Return stale data on errors
- Log cache failures

### 5. Memory Management
- Monitor cache size
- Implement eviction policies
- Clean up expired entries

## Troubleshooting

### Cache Not Working

1. **Check Redis connection:**
   ```bash
   redis-cli ping
   ```

2. **Verify cache stats:**
   ```bash
   curl /api/cache/stats
   ```

3. **Check browser storage:**
   ```javascript
   // In browser console
   console.log(localStorage);
   ```

### Low Hit Rate

1. **Review TTL settings** - May be too short
2. **Check key generation** - Keys might be too specific
3. **Monitor invalidation** - Too frequent invalidation

### Memory Issues

1. **Clear old entries:**
   ```bash
   curl -X DELETE /api/cache
   ```

2. **Reduce cache size:**
   ```javascript
   // Adjust configuration
   maxSize: 25 * 1024 * 1024 // 25MB
   ```

3. **Enable compression** for large values

## Security Considerations

### Data Sensitivity
- Don't cache sensitive data in browser
- Use appropriate TTLs for user data
- Clear cache on logout

### Cache Poisoning
- Validate cached data
- Use checksums for critical data
- Monitor for anomalies

### Access Control
- Restrict cache management endpoints
- Audit cache operations
- Encrypt sensitive cached data