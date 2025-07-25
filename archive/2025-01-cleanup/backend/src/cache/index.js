const CacheManager = require('./cache-manager');
const CacheMiddleware = require('./cache-middleware');

// Singleton cache manager instance
let cacheManager = null;

/**
 * Initialize cache manager
 * @param {Object} db - SQLite database instance
 * @param {Object} redis - Redis client (optional)
 * @param {Object} options - Cache options
 */
async function initCache(db, redis = null, options = {}) {
  if (cacheManager) {
    console.warn('Cache manager already initialized');
    return cacheManager;
  }

  cacheManager = new CacheManager(options);
  await cacheManager.init(db, redis);

  console.log('Cache manager initialized');
  return cacheManager;
}

/**
 * Get cache manager instance
 */
function getCache() {
  if (!cacheManager) {
    throw new Error('Cache manager not initialized. Call initCache() first.');
  }
  return cacheManager;
}

/**
 * Create cache middleware
 * @param {Object} options - Middleware options
 */
function createCacheMiddleware(options = {}) {
  const cache = getCache();
  const middleware = new CacheMiddleware(cache, options);
  return middleware.middleware();
}

/**
 * Create cache invalidation middleware
 * @param {Object} options - Middleware options
 */
function createInvalidationMiddleware(options = {}) {
  const cache = getCache();
  const middleware = new CacheMiddleware(cache, options);
  return middleware.invalidation();
}

/**
 * Cache utilities
 */
const utils = {
  /**
   * Generate cache key
   * @param {string} prefix - Key prefix
   * @param {...any} parts - Key parts
   */
  key(prefix, ...parts) {
    return `${prefix}:${parts.join(':')}`;
  },

  /**
   * Cache wrapper function
   * @param {string} key - Cache key
   * @param {Function} fn - Function to cache
   * @param {number} ttl - Time to live
   */
  async cached(key, fn, ttl = 300000) {
    const cache = getCache();
    
    // Try cache first
    const cached = await cache.get(key);
    if (cached !== null) {
      return cached;
    }

    // Execute function
    const result = await fn();

    // Cache result
    if (result !== undefined) {
      await cache.set(key, result, ttl);
    }

    return result;
  },

  /**
   * Remember function - cache with lazy evaluation
   * @param {string} key - Cache key
   * @param {Function} fn - Function to cache
   * @param {number} ttl - Time to live
   */
  remember(key, fn, ttl = 300000) {
    return utils.cached(key, fn, ttl);
  },

  /**
   * Memoize function
   * @param {Function} fn - Function to memoize
   * @param {Object} options - Memoization options
   */
  memoize(fn, options = {}) {
    const {
      ttl = 300000,
      keyGenerator = (...args) => JSON.stringify(args),
      prefix = fn.name || 'memoized'
    } = options;

    return async function(...args) {
      const key = `${prefix}:${keyGenerator(...args)}`;
      return utils.cached(key, () => fn(...args), ttl);
    };
  }
};

module.exports = {
  initCache,
  getCache,
  createCacheMiddleware,
  createInvalidationMiddleware,
  utils,
  CacheManager,
  CacheMiddleware
};