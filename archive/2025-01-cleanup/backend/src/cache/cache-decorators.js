/**
 * Decorators for method-level caching
 */

const cacheManager = require('./index');

/**
 * Cache method results
 * @param {Object} options - Cache options
 * @param {number} options.ttl - Time to live
 * @param {Function} options.key - Key generator function
 * @param {string} options.prefix - Cache key prefix
 */
function Cacheable(options = {}) {
  return function(target, propertyName, descriptor) {
    const originalMethod = descriptor.value;

    descriptor.value = async function(...args) {
      // Generate cache key
      const keyPrefix = options.prefix || `${target.constructor.name}:${propertyName}`;
      const key = options.key 
        ? options.key.apply(this, args)
        : `${keyPrefix}:${JSON.stringify(args)}`;

      // Try to get from cache
      const cached = await cacheManager.get(key);
      if (cached !== null) {
        return cached;
      }

      // Execute method
      const result = await originalMethod.apply(this, args);

      // Cache result
      if (result !== undefined) {
        await cacheManager.set(key, result, options.ttl);
      }

      return result;
    };

    return descriptor;
  };
}

/**
 * Invalidate cache on method execution
 * @param {Object} options - Invalidation options
 * @param {string|Function} options.pattern - Pattern or function to generate pattern
 */
function CacheEvict(options = {}) {
  return function(target, propertyName, descriptor) {
    const originalMethod = descriptor.value;

    descriptor.value = async function(...args) {
      // Execute method first
      const result = await originalMethod.apply(this, args);

      // Determine invalidation pattern
      let pattern;
      if (typeof options.pattern === 'function') {
        pattern = options.pattern.apply(this, args);
      } else if (typeof options.pattern === 'string') {
        pattern = options.pattern;
      } else {
        // Default pattern based on class and method
        pattern = `${target.constructor.name}:*`;
      }

      // Invalidate cache
      await cacheManager.clearPattern(pattern);

      return result;
    };

    return descriptor;
  };
}

/**
 * Update cache after method execution
 * @param {Object} options - Update options
 * @param {Function} options.key - Key generator function
 * @param {number} options.ttl - Time to live
 */
function CachePut(options = {}) {
  return function(target, propertyName, descriptor) {
    const originalMethod = descriptor.value;

    descriptor.value = async function(...args) {
      // Execute method
      const result = await originalMethod.apply(this, args);

      // Generate cache key
      const key = options.key
        ? options.key.apply(this, args)
        : `${target.constructor.name}:${propertyName}:${JSON.stringify(args)}`;

      // Update cache
      if (result !== undefined) {
        await cacheManager.set(key, result, options.ttl);
      }

      return result;
    };

    return descriptor;
  };
}

/**
 * Conditional caching based on result
 * @param {Object} options - Conditional options
 * @param {Function} options.condition - Condition function
 * @param {number} options.ttl - Time to live
 */
function CacheConditional(options = {}) {
  return function(target, propertyName, descriptor) {
    const originalMethod = descriptor.value;

    descriptor.value = async function(...args) {
      const keyPrefix = `${target.constructor.name}:${propertyName}`;
      const key = `${keyPrefix}:${JSON.stringify(args)}`;

      // Try cache first
      const cached = await cacheManager.get(key);
      if (cached !== null) {
        return cached;
      }

      // Execute method
      const result = await originalMethod.apply(this, args);

      // Check condition
      const shouldCache = options.condition
        ? options.condition(result)
        : result !== null && result !== undefined;

      // Cache if condition met
      if (shouldCache) {
        await cacheManager.set(key, result, options.ttl);
      }

      return result;
    };

    return descriptor;
  };
}

/**
 * Example usage:
 * 
 * class PackageService {
 *   @Cacheable({ ttl: 600000, prefix: 'packages' })
 *   async search(query) {
 *     // Expensive search operation
 *   }
 * 
 *   @CacheEvict({ pattern: 'packages:*' })
 *   async install(packageName) {
 *     // Install package
 *   }
 * 
 *   @CachePut({ 
 *     key: (name) => `packages:details:${name}`,
 *     ttl: 300000 
 *   })
 *   async getDetails(packageName) {
 *     // Get package details
 *   }
 * 
 *   @CacheConditional({
 *     condition: (result) => result.success,
 *     ttl: 60000
 *   })
 *   async checkAvailability(packageName) {
 *     // Check if package is available
 *   }
 * }
 */

module.exports = {
  Cacheable,
  CacheEvict,
  CachePut,
  CacheConditional
};