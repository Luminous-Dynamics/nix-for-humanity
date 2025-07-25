const LRU = require('lru-cache');
const crypto = require('crypto');
const { promisify } = require('util');
const fs = require('fs').promises;
const path = require('path');

/**
 * Multi-tier cache manager for NixOS GUI
 * Implements L1 (memory), L2 (SQLite), and L3 (Redis) caching
 */
class CacheManager {
  constructor(options = {}) {
    this.options = {
      ttl: 300000, // 5 minutes default
      maxSize: 100 * 1024 * 1024, // 100MB memory limit
      maxAge: 86400000, // 24 hours max age
      ...options
    };

    // L1: In-memory LRU cache
    this.memoryCache = new LRU({
      max: this.options.maxSize,
      ttl: this.options.ttl,
      updateAgeOnGet: true,
      sizeCalculation: (value) => {
        return Buffer.byteLength(JSON.stringify(value));
      }
    });

    // L2: SQLite cache (initialized in init())
    this.sqliteCache = null;

    // L3: Redis cache (optional)
    this.redisCache = null;

    // Statistics
    this.stats = {
      hits: { memory: 0, sqlite: 0, redis: 0 },
      misses: 0,
      sets: 0,
      deletes: 0,
      errors: 0
    };
  }

  async init(db, redis = null) {
    // Initialize SQLite cache
    this.sqliteCache = new SQLiteCache(db);
    await this.sqliteCache.init();

    // Initialize Redis if provided
    if (redis) {
      this.redisCache = new RedisCache(redis);
    }

    // Start cleanup interval
    this.startCleanup();
  }

  /**
   * Get value from cache
   * @param {string} key - Cache key
   * @returns {Promise<any>} Cached value or null
   */
  async get(key) {
    const hashedKey = this.hashKey(key);

    // L1: Check memory cache
    const memoryValue = this.memoryCache.get(hashedKey);
    if (memoryValue !== undefined) {
      this.stats.hits.memory++;
      return memoryValue;
    }

    // L2: Check SQLite cache
    try {
      const sqliteValue = await this.sqliteCache.get(hashedKey);
      if (sqliteValue !== null) {
        this.stats.hits.sqlite++;
        // Promote to memory cache
        this.memoryCache.set(hashedKey, sqliteValue);
        return sqliteValue;
      }
    } catch (error) {
      this.stats.errors++;
      console.error('SQLite cache error:', error);
    }

    // L3: Check Redis cache
    if (this.redisCache) {
      try {
        const redisValue = await this.redisCache.get(hashedKey);
        if (redisValue !== null) {
          this.stats.hits.redis++;
          // Promote to memory and SQLite
          this.memoryCache.set(hashedKey, redisValue);
          await this.sqliteCache.set(hashedKey, redisValue, this.options.ttl);
          return redisValue;
        }
      } catch (error) {
        this.stats.errors++;
        console.error('Redis cache error:', error);
      }
    }

    this.stats.misses++;
    return null;
  }

  /**
   * Set value in cache
   * @param {string} key - Cache key
   * @param {any} value - Value to cache
   * @param {number} ttl - Time to live in ms (optional)
   */
  async set(key, value, ttl = this.options.ttl) {
    const hashedKey = this.hashKey(key);
    this.stats.sets++;

    // L1: Set in memory cache
    this.memoryCache.set(hashedKey, value, { ttl });

    // L2: Set in SQLite cache
    try {
      await this.sqliteCache.set(hashedKey, value, ttl);
    } catch (error) {
      this.stats.errors++;
      console.error('SQLite cache set error:', error);
    }

    // L3: Set in Redis cache
    if (this.redisCache) {
      try {
        await this.redisCache.set(hashedKey, value, ttl);
      } catch (error) {
        this.stats.errors++;
        console.error('Redis cache set error:', error);
      }
    }
  }

  /**
   * Delete value from cache
   * @param {string} key - Cache key
   */
  async delete(key) {
    const hashedKey = this.hashKey(key);
    this.stats.deletes++;

    // Delete from all tiers
    this.memoryCache.delete(hashedKey);
    
    try {
      await this.sqliteCache.delete(hashedKey);
    } catch (error) {
      this.stats.errors++;
    }

    if (this.redisCache) {
      try {
        await this.redisCache.delete(hashedKey);
      } catch (error) {
        this.stats.errors++;
      }
    }
  }

  /**
   * Clear cache by pattern
   * @param {string} pattern - Pattern to match (e.g., 'packages:*')
   */
  async clearPattern(pattern) {
    // Clear from memory cache
    const regex = new RegExp(pattern.replace('*', '.*'));
    for (const key of this.memoryCache.keys()) {
      if (regex.test(key)) {
        this.memoryCache.delete(key);
      }
    }

    // Clear from other tiers
    await this.sqliteCache.clearPattern(pattern);
    if (this.redisCache) {
      await this.redisCache.clearPattern(pattern);
    }
  }

  /**
   * Clear all cache
   */
  async clear() {
    this.memoryCache.clear();
    await this.sqliteCache.clear();
    if (this.redisCache) {
      await this.redisCache.clear();
    }
  }

  /**
   * Get cache statistics
   */
  getStats() {
    const memorySize = this.memoryCache.size;
    const memoryCount = this.memoryCache.size;
    
    return {
      ...this.stats,
      memory: {
        size: memorySize,
        count: memoryCount,
        maxSize: this.options.maxSize
      },
      hitRate: this.calculateHitRate()
    };
  }

  /**
   * Hash key for consistent storage
   */
  hashKey(key) {
    return crypto.createHash('md5').update(key).digest('hex');
  }

  /**
   * Calculate cache hit rate
   */
  calculateHitRate() {
    const totalHits = Object.values(this.stats.hits).reduce((a, b) => a + b, 0);
    const totalRequests = totalHits + this.stats.misses;
    return totalRequests > 0 ? (totalHits / totalRequests) * 100 : 0;
  }

  /**
   * Start periodic cleanup
   */
  startCleanup() {
    // Cleanup expired entries every hour
    this.cleanupInterval = setInterval(async () => {
      try {
        await this.sqliteCache.cleanup();
        if (this.redisCache) {
          await this.redisCache.cleanup();
        }
      } catch (error) {
        console.error('Cache cleanup error:', error);
      }
    }, 3600000); // 1 hour
  }

  /**
   * Stop cache manager
   */
  async stop() {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
    this.memoryCache.clear();
  }
}

/**
 * SQLite cache implementation
 */
class SQLiteCache {
  constructor(db) {
    this.db = db;
  }

  async init() {
    await this.db.run(`
      CREATE TABLE IF NOT EXISTS cache (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        expires_at INTEGER NOT NULL,
        created_at INTEGER NOT NULL,
        accessed_at INTEGER NOT NULL,
        access_count INTEGER DEFAULT 1
      )
    `);

    // Create index for cleanup
    await this.db.run(`
      CREATE INDEX IF NOT EXISTS idx_cache_expires 
      ON cache(expires_at)
    `);
  }

  async get(key) {
    const now = Date.now();
    const row = await this.db.get(
      'SELECT value FROM cache WHERE key = ? AND expires_at > ?',
      [key, now]
    );

    if (row) {
      // Update access statistics
      await this.db.run(
        'UPDATE cache SET accessed_at = ?, access_count = access_count + 1 WHERE key = ?',
        [now, key]
      );
      return JSON.parse(row.value);
    }

    return null;
  }

  async set(key, value, ttl) {
    const now = Date.now();
    const expiresAt = now + ttl;
    const serialized = JSON.stringify(value);

    await this.db.run(`
      INSERT OR REPLACE INTO cache 
      (key, value, expires_at, created_at, accessed_at, access_count)
      VALUES (?, ?, ?, ?, ?, 1)
    `, [key, serialized, expiresAt, now, now]);
  }

  async delete(key) {
    await this.db.run('DELETE FROM cache WHERE key = ?', [key]);
  }

  async clearPattern(pattern) {
    const sqlPattern = pattern.replace('*', '%');
    await this.db.run('DELETE FROM cache WHERE key LIKE ?', [sqlPattern]);
  }

  async clear() {
    await this.db.run('DELETE FROM cache');
  }

  async cleanup() {
    const now = Date.now();
    const result = await this.db.run(
      'DELETE FROM cache WHERE expires_at <= ?',
      [now]
    );
    return result.changes;
  }

  async getSize() {
    const result = await this.db.get(
      'SELECT COUNT(*) as count, SUM(LENGTH(value)) as size FROM cache'
    );
    return result;
  }
}

/**
 * Redis cache implementation
 */
class RedisCache {
  constructor(redis) {
    this.redis = redis;
    this.prefix = 'nixos-gui:cache:';
  }

  async get(key) {
    const value = await this.redis.get(this.prefix + key);
    return value ? JSON.parse(value) : null;
  }

  async set(key, value, ttl) {
    const serialized = JSON.stringify(value);
    await this.redis.setex(
      this.prefix + key,
      Math.floor(ttl / 1000),
      serialized
    );
  }

  async delete(key) {
    await this.redis.del(this.prefix + key);
  }

  async clearPattern(pattern) {
    const keys = await this.redis.keys(this.prefix + pattern);
    if (keys.length > 0) {
      await this.redis.del(...keys);
    }
  }

  async clear() {
    const keys = await this.redis.keys(this.prefix + '*');
    if (keys.length > 0) {
      await this.redis.del(...keys);
    }
  }

  async cleanup() {
    // Redis handles expiration automatically
    return 0;
  }
}

module.exports = CacheManager;