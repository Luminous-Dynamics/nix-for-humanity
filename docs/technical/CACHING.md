# Caching Documentation

## Overview

NixOS GUI implements a comprehensive multi-tier caching strategy to improve performance and reduce load on system resources. The caching system is designed to be transparent, efficient, and easy to manage.

## Architecture

### Cache Tiers

```
┌─────────────────┐
│   Browser       │
│  (Frontend)     │
├─────────────────┤
│ L1: Memory      │ ← In-browser memory cache
│ L2: LocalStorage│ ← Persistent browser storage
└─────────────────┘
        ↓
┌─────────────────┐
│   Server        │
│  (Backend)      │
├─────────────────┤
│ L1: Memory (LRU)│ ← Fast in-memory cache
│ L2: SQLite      │ ← Persistent local cache
│ L3: Redis       │ ← Distributed cache (optional)
└─────────────────┘
```

### Cache Flow

1. **Request arrives** → Check L1 (Memory)
2. **L1 Miss** → Check L2 (SQLite/LocalStorage)
3. **L2 Miss** → Check L3 (Redis) if available
4. **L3 Miss** → Fetch from source
5. **Populate** → Write to all cache tiers

## Backend Caching

### Configuration

```javascript
// In server configuration
{
  cacheEnabled: true,
  cache: {
    ttl: 300000,        // 5 minutes default TTL
    maxSize: 104857600, // 100MB memory limit
    maxAge: 86400000    // 24 hours max age
  }
}
```

### Environment Variables

```bash
# Enable/disable caching
CACHE_ENABLED=true

# Redis configuration (optional)
REDIS_URL=redis://localhost:6379

# Cache settings
CACHE_TTL=300000
CACHE_MAX_SIZE=104857600
```

### Service-Level Caching

Using decorators for method caching:

```javascript
class PackageService {
  @Cacheable({ 
    ttl: 600000, 
    key: (query) => `search:${query}` 
  })
  async search(query) {
    // Expensive search operation
  }

  @CacheEvict({ pattern: 'packages:*' })
  async install(package) {
    // Invalidates cache after install
  }
}
```

### HTTP Response Caching

Automatic caching of GET requests:

```javascript
// Applied via middleware
app.use(createCacheMiddleware({
  defaultTTL: 300000,
  excludePaths: ['/api/auth', '/api/ws'],
  varyHeaders: ['accept', 'accept-encoding']
}));
```

### Cache Invalidation

Automatic invalidation on state changes:

```javascript
// POST /api/packages/install
// Automatically invalidates:
// - packages:*
// - http:*packages*
```

## Frontend Caching

### Basic Usage

```javascript
import { FrontendCache } from '/js/lib/cache.js';

const cache = new FrontendCache({
  prefix: 'nixos-gui:',
  defaultTTL: 300000,
  storage: 'localStorage'
});

// Set value
await cache.set('user:preferences', preferences, 3600000);

// Get value
const preferences = await cache.get('user:preferences');

// Clear pattern
await cache.clearPattern('packages:*');
```

### API Request Caching

```javascript
import { CachedAPI } from '/js/lib/cache.js';

const api = new CachedAPI('/api');

// Cached GET request (5 minute TTL)
const packages = await api.get('/packages/search?q=firefox', {
  ttl: 300000
});

// Force refresh
const fresh = await api.get('/packages/installed', {
  forceRefresh: true
});

// Non-cached POST
const result = await api.post('/packages/install', {
  package: 'firefox'
});
```

### Component-Level Caching

```javascript
class PackageList {
  @cacheable({ 
    ttl: 60000,
    key: () => 'package-list' 
  })
  async loadPackages() {
    return fetch('/api/packages/installed');
  }
}
```

## Cache Management

### Viewing Cache Statistics

```bash
# API endpoint
GET /api/cache/stats

# Response
{
  "hits": {
    "memory": 1523,
    "sqlite": 342,
    "redis": 89
  },
  "misses": 234,
  "hitRate": "89.34%",
  "memory": {
    "size": 52428800,
    "count": 145,
    "maxSize": 104857600
  }
}
```

### Clearing Cache

```bash
# Clear all cache
DELETE /api/cache/clear

# Clear specific pattern
DELETE /api/cache/clear?pattern=packages:*
```

### Frontend Cache Management

```javascript
// Get cache stats
const stats = cache.getStats();
console.log(`Hit rate: ${stats.hitRate}`);

// Clear all cache
await cache.clear();

// Clear by pattern
await cache.clearPattern('api:*');
```

## Cache Keys

### Naming Convention

```
service:operation:parameters
```

Examples:
- `packages:search:firefox`
- `packages:details:nginx`
- `services:list:running`
- `config:current`
- `generations:list`

### HTTP Cache Keys

```
http:method:path:query:headers
```

Hashed to MD5 for consistency.

## TTL Strategy

| Resource | TTL | Rationale |
|----------|-----|-----------|
| Package search | 10 minutes | Results change infrequently |
| Package details | 5 minutes | May change with updates |
| Installed packages | 1 minute | User may install/remove |
| Service status | 5 seconds | Real-time monitoring |
| System info | 10 seconds | Performance metrics |
| Configuration | 5 minutes | Rarely changes |
| Generations | 5 minutes | Historical data |

## Performance Optimization

### Cache Warming

On startup, pre-cache common queries:

```javascript
async warmCache() {
  const common = ['firefox', 'git', 'vim', 'vscode'];
  await Promise.all(common.map(q => this.search(q)));
}
```

### Batch Operations

Cache bulk requests efficiently:

```javascript
const results = await cache.memoize(
  () => Promise.all(queries.map(q => search(q))),
  { ttl: 600000, key: () => `bulk:${queries.join(',')}` }
);
```

### Size Management

- **Memory**: LRU eviction when size exceeded
- **SQLite**: Periodic cleanup of expired entries
- **LocalStorage**: Remove oldest when 80% full

## Monitoring

### Metrics to Track

1. **Hit Rate**: Should be >80% for effective caching
2. **Response Time**: Compare cached vs uncached
3. **Cache Size**: Monitor growth over time
4. **Eviction Rate**: High rate indicates size issues

### Debug Mode

Enable cache debugging:

```javascript
// Backend
DEBUG=cache:* npm start

// Frontend
localStorage.setItem('debug:cache', 'true');
```

## Best Practices

### Do Cache

- ✅ GET requests
- ✅ Expensive computations
- ✅ External API calls
- ✅ Database queries
- ✅ Search results

### Don't Cache

- ❌ User authentication
- ❌ Real-time data (WebSocket)
- ❌ Sensitive information
- ❌ POST/PUT/DELETE responses
- ❌ Error responses

### Cache Invalidation

1. **Time-based**: Use appropriate TTLs
2. **Event-based**: Invalidate on state changes
3. **Manual**: Provide clear cache controls
4. **Pattern-based**: Clear related entries

## Troubleshooting

### Cache Not Working

1. Check if caching is enabled:
   ```bash
   echo $CACHE_ENABLED
   ```

2. Verify cache statistics:
   ```bash
   curl http://localhost:8080/api/cache/stats
   ```

3. Check browser storage:
   ```javascript
   console.log(localStorage.length);
   ```

### High Memory Usage

1. Reduce cache size limit
2. Decrease TTLs
3. Implement more aggressive eviction

### Stale Data

1. Verify invalidation patterns
2. Check TTL values
3. Use force refresh when needed

## Advanced Configuration

### Redis Clustering

```javascript
// For high availability
{
  redis: {
    cluster: true,
    nodes: [
      { host: 'redis1', port: 6379 },
      { host: 'redis2', port: 6379 }
    ]
  }
}
```

### Custom Cache Stores

```javascript
class CustomStore {
  async get(key) { /* implementation */ }
  async set(key, value, ttl) { /* implementation */ }
  async delete(key) { /* implementation */ }
}

cache.addStore('custom', new CustomStore());
```

### Cache Policies

```javascript
// LRU (Least Recently Used) - Default
new CacheManager({ eviction: 'lru' });

// LFU (Least Frequently Used)
new CacheManager({ eviction: 'lfu' });

// TTL (Time To Live only)
new CacheManager({ eviction: 'ttl' });
```