const crypto = require('crypto');

/**
 * Express middleware for HTTP response caching
 */
class CacheMiddleware {
  constructor(cacheManager, options = {}) {
    this.cache = cacheManager;
    this.options = {
      defaultTTL: 300000, // 5 minutes
      varyHeaders: ['accept', 'accept-encoding'],
      excludePaths: ['/api/auth', '/api/ws'],
      excludeMethods: ['POST', 'PUT', 'DELETE', 'PATCH'],
      includeQuery: true,
      includeAuth: false,
      ...options
    };
  }

  /**
   * Create cache middleware
   */
  middleware() {
    return async (req, res, next) => {
      // Skip caching for excluded methods
      if (this.options.excludeMethods.includes(req.method)) {
        return next();
      }

      // Skip caching for excluded paths
      if (this.shouldExcludePath(req.path)) {
        return next();
      }

      // Generate cache key
      const cacheKey = this.generateCacheKey(req);

      // Try to get from cache
      const cached = await this.cache.get(cacheKey);
      if (cached) {
        // Send cached response
        res.set(cached.headers);
        res.set('X-Cache', 'HIT');
        res.set('X-Cache-Key', cacheKey);
        return res.status(cached.status).send(cached.body);
      }

      // Cache miss - capture response
      res.set('X-Cache', 'MISS');
      res.set('X-Cache-Key', cacheKey);

      // Store original methods
      const originalSend = res.send;
      const originalJson = res.json;
      const originalEnd = res.end;

      // Response capture
      let responseData;
      let responseHeaders = {};

      // Override send method
      res.send = function(data) {
        responseData = data;
        return originalSend.call(this, data);
      };

      // Override json method
      res.json = function(data) {
        responseData = JSON.stringify(data);
        res.set('Content-Type', 'application/json');
        return originalJson.call(this, data);
      };

      // Override end method
      res.end = async function(...args) {
        // Only cache successful responses
        if (res.statusCode >= 200 && res.statusCode < 300) {
          // Determine TTL
          const ttl = determineTTL(req, res, this.options.defaultTTL);

          if (ttl > 0) {
            // Capture headers
            const headersToCache = [
              'content-type',
              'content-encoding',
              'content-language',
              'cache-control',
              'etag',
              'last-modified'
            ];

            headersToCache.forEach(header => {
              const value = res.get(header);
              if (value) {
                responseHeaders[header] = value;
              }
            });

            // Store in cache
            await this.cache.set(cacheKey, {
              status: res.statusCode,
              headers: responseHeaders,
              body: responseData || args[0],
              timestamp: Date.now()
            }, ttl);
          }
        }

        return originalEnd.apply(this, args);
      }.bind(this);

      next();
    };
  }

  /**
   * Cache invalidation middleware
   */
  invalidation() {
    return async (req, res, next) => {
      // Invalidate cache on state-changing methods
      if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(req.method)) {
        const patterns = this.getInvalidationPatterns(req);
        
        for (const pattern of patterns) {
          await this.cache.clearPattern(pattern);
        }
      }

      next();
    };
  }

  /**
   * Generate cache key from request
   */
  generateCacheKey(req) {
    const parts = [
      req.method,
      req.path
    ];

    // Include query parameters
    if (this.options.includeQuery && Object.keys(req.query).length > 0) {
      const sortedQuery = Object.keys(req.query)
        .sort()
        .map(key => `${key}=${req.query[key]}`)
        .join('&');
      parts.push(sortedQuery);
    }

    // Include auth info
    if (this.options.includeAuth && req.user) {
      parts.push(`user:${req.user.id}`);
    }

    // Include vary headers
    this.options.varyHeaders.forEach(header => {
      const value = req.get(header);
      if (value) {
        parts.push(`${header}:${value}`);
      }
    });

    const key = parts.join(':');
    return `http:${crypto.createHash('md5').update(key).digest('hex')}`;
  }

  /**
   * Check if path should be excluded from caching
   */
  shouldExcludePath(path) {
    return this.options.excludePaths.some(excludePath => {
      if (typeof excludePath === 'string') {
        return path.startsWith(excludePath);
      } else if (excludePath instanceof RegExp) {
        return excludePath.test(path);
      }
      return false;
    });
  }

  /**
   * Get invalidation patterns based on request
   */
  getInvalidationPatterns(req) {
    const patterns = [];

    // Invalidate related endpoints
    switch (req.path) {
      case '/api/packages/install':
        patterns.push('http:*packages*');
        patterns.push('api:packages:*');
        break;
      
      case '/api/config':
        patterns.push('http:*config*');
        patterns.push('api:config:*');
        patterns.push('api:generations:*');
        break;
      
      case '/api/services':
        const serviceName = req.params.name || req.body.name;
        if (serviceName) {
          patterns.push(`http:*services/${serviceName}*`);
          patterns.push(`api:services:${serviceName}:*`);
        }
        patterns.push('http:*services*');
        patterns.push('api:services:*');
        break;
      
      default:
        // Generic invalidation
        const resource = req.path.split('/')[2]; // /api/resource/...
        if (resource) {
          patterns.push(`http:*${resource}*`);
          patterns.push(`api:${resource}:*`);
        }
    }

    return patterns;
  }
}

/**
 * Determine TTL from request/response
 */
function determineTTL(req, res, defaultTTL) {
  // Check Cache-Control header
  const cacheControl = res.get('Cache-Control');
  if (cacheControl) {
    const maxAge = cacheControl.match(/max-age=(\d+)/);
    if (maxAge) {
      return parseInt(maxAge[1]) * 1000;
    }
    if (cacheControl.includes('no-cache') || cacheControl.includes('no-store')) {
      return 0;
    }
  }

  // Resource-specific TTLs
  if (req.path.includes('/api/packages/search')) {
    return 600000; // 10 minutes for package search
  }
  if (req.path.includes('/api/system/info')) {
    return 10000; // 10 seconds for system info
  }
  if (req.path.includes('/api/services')) {
    return 5000; // 5 seconds for service status
  }
  if (req.path.includes('/api/generations')) {
    return 300000; // 5 minutes for generations
  }

  return defaultTTL;
}

module.exports = CacheMiddleware;