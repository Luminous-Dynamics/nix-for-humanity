/**
 * Frontend caching utilities
 */

class FrontendCache {
  constructor(options = {}) {
    this.options = {
      prefix: 'nixos-gui:',
      defaultTTL: 300000, // 5 minutes
      maxSize: 50 * 1024 * 1024, // 50MB
      storage: 'localStorage', // or 'sessionStorage', 'indexedDB'
      ...options
    };

    this.stats = {
      hits: 0,
      misses: 0,
      sets: 0,
      deletes: 0
    };

    // Initialize storage adapter
    this.initStorage();
  }

  initStorage() {
    switch (this.options.storage) {
      case 'localStorage':
        this.storage = new LocalStorageAdapter(this.options.prefix);
        break;
      case 'sessionStorage':
        this.storage = new SessionStorageAdapter(this.options.prefix);
        break;
      case 'indexedDB':
        this.storage = new IndexedDBAdapter(this.options.prefix);
        break;
      default:
        this.storage = new MemoryAdapter();
    }
  }

  /**
   * Get value from cache
   */
  async get(key) {
    try {
      const entry = await this.storage.get(key);
      
      if (!entry) {
        this.stats.misses++;
        return null;
      }

      // Check expiration
      if (entry.expiresAt && entry.expiresAt < Date.now()) {
        await this.delete(key);
        this.stats.misses++;
        return null;
      }

      this.stats.hits++;
      return entry.value;
    } catch (error) {
      console.error('Cache get error:', error);
      this.stats.misses++;
      return null;
    }
  }

  /**
   * Set value in cache
   */
  async set(key, value, ttl = this.options.defaultTTL) {
    try {
      const entry = {
        value,
        createdAt: Date.now(),
        expiresAt: ttl > 0 ? Date.now() + ttl : null
      };

      await this.storage.set(key, entry);
      this.stats.sets++;

      // Check size limits
      await this.enforceSize();
    } catch (error) {
      console.error('Cache set error:', error);
    }
  }

  /**
   * Delete value from cache
   */
  async delete(key) {
    try {
      await this.storage.delete(key);
      this.stats.deletes++;
    } catch (error) {
      console.error('Cache delete error:', error);
    }
  }

  /**
   * Clear cache by pattern
   */
  async clearPattern(pattern) {
    const regex = new RegExp(pattern.replace('*', '.*'));
    const keys = await this.storage.keys();
    
    for (const key of keys) {
      if (regex.test(key)) {
        await this.delete(key);
      }
    }
  }

  /**
   * Clear all cache
   */
  async clear() {
    await this.storage.clear();
  }

  /**
   * Get cache statistics
   */
  getStats() {
    const hitRate = this.stats.hits + this.stats.misses > 0
      ? (this.stats.hits / (this.stats.hits + this.stats.misses)) * 100
      : 0;

    return {
      ...this.stats,
      hitRate: hitRate.toFixed(2) + '%'
    };
  }

  /**
   * Enforce size limits
   */
  async enforceSize() {
    const size = await this.storage.getSize();
    
    if (size > this.options.maxSize) {
      // Remove oldest entries
      const entries = await this.storage.getAllEntries();
      entries.sort((a, b) => a.createdAt - b.createdAt);
      
      let currentSize = size;
      for (const entry of entries) {
        if (currentSize <= this.options.maxSize * 0.8) break;
        
        await this.storage.delete(entry.key);
        currentSize -= entry.size;
      }
    }
  }
}

/**
 * Storage Adapters
 */

class LocalStorageAdapter {
  constructor(prefix) {
    this.prefix = prefix;
  }

  async get(key) {
    const item = localStorage.getItem(this.prefix + key);
    return item ? JSON.parse(item) : null;
  }

  async set(key, value) {
    localStorage.setItem(this.prefix + key, JSON.stringify(value));
  }

  async delete(key) {
    localStorage.removeItem(this.prefix + key);
  }

  async keys() {
    const keys = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key.startsWith(this.prefix)) {
        keys.push(key.substring(this.prefix.length));
      }
    }
    return keys;
  }

  async clear() {
    const keys = await this.keys();
    keys.forEach(key => this.delete(key));
  }

  async getSize() {
    let size = 0;
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key.startsWith(this.prefix)) {
        size += key.length + localStorage.getItem(key).length;
      }
    }
    return size;
  }

  async getAllEntries() {
    const entries = [];
    const keys = await this.keys();
    
    for (const key of keys) {
      const value = await this.get(key);
      entries.push({
        key,
        ...value,
        size: JSON.stringify(value).length
      });
    }
    
    return entries;
  }
}

class SessionStorageAdapter extends LocalStorageAdapter {
  async get(key) {
    const item = sessionStorage.getItem(this.prefix + key);
    return item ? JSON.parse(item) : null;
  }

  async set(key, value) {
    sessionStorage.setItem(this.prefix + key, JSON.stringify(value));
  }

  async delete(key) {
    sessionStorage.removeItem(this.prefix + key);
  }

  async keys() {
    const keys = [];
    for (let i = 0; i < sessionStorage.length; i++) {
      const key = sessionStorage.key(i);
      if (key.startsWith(this.prefix)) {
        keys.push(key.substring(this.prefix.length));
      }
    }
    return keys;
  }

  async getSize() {
    let size = 0;
    for (let i = 0; i < sessionStorage.length; i++) {
      const key = sessionStorage.key(i);
      if (key.startsWith(this.prefix)) {
        size += key.length + sessionStorage.getItem(key).length;
      }
    }
    return size;
  }
}

class MemoryAdapter {
  constructor() {
    this.store = new Map();
  }

  async get(key) {
    return this.store.get(key) || null;
  }

  async set(key, value) {
    this.store.set(key, value);
  }

  async delete(key) {
    this.store.delete(key);
  }

  async keys() {
    return Array.from(this.store.keys());
  }

  async clear() {
    this.store.clear();
  }

  async getSize() {
    let size = 0;
    for (const [key, value] of this.store) {
      size += key.length + JSON.stringify(value).length;
    }
    return size;
  }

  async getAllEntries() {
    const entries = [];
    for (const [key, value] of this.store) {
      entries.push({
        key,
        ...value,
        size: JSON.stringify(value).length
      });
    }
    return entries;
  }
}

/**
 * Cache decorators for methods
 */
function cacheable(options = {}) {
  return function(target, propertyKey, descriptor) {
    const originalMethod = descriptor.value;
    const cache = new FrontendCache(options.cacheOptions);

    descriptor.value = async function(...args) {
      const key = options.key 
        ? options.key(...args)
        : `${propertyKey}:${JSON.stringify(args)}`;

      // Try cache first
      const cached = await cache.get(key);
      if (cached !== null) {
        console.log(`Cache hit: ${key}`);
        return cached;
      }

      // Call original method
      const result = await originalMethod.apply(this, args);

      // Cache result
      if (result !== undefined) {
        await cache.set(key, result, options.ttl);
      }

      return result;
    };

    return descriptor;
  };
}

/**
 * API request caching
 */
class CachedAPI {
  constructor(baseURL, cache = new FrontendCache()) {
    this.baseURL = baseURL;
    this.cache = cache;
  }

  async request(url, options = {}) {
    const {
      method = 'GET',
      ttl = 300000,
      forceRefresh = false,
      ...fetchOptions
    } = options;

    // Only cache GET requests
    if (method !== 'GET' || forceRefresh) {
      return this.fetch(url, { method, ...fetchOptions });
    }

    // Generate cache key
    const cacheKey = `api:${method}:${url}`;

    // Try cache
    const cached = await this.cache.get(cacheKey);
    if (cached !== null) {
      return cached;
    }

    // Make request
    const response = await this.fetch(url, { method, ...fetchOptions });
    
    // Cache successful responses
    if (response.ok) {
      const data = await response.json();
      await this.cache.set(cacheKey, data, ttl);
      return data;
    }

    throw new Error(`API request failed: ${response.statusText}`);
  }

  async fetch(url, options) {
    const fullURL = url.startsWith('http') ? url : `${this.baseURL}${url}`;
    return fetch(fullURL, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      credentials: 'include'
    });
  }

  // Convenience methods
  async get(url, options) {
    return this.request(url, { ...options, method: 'GET' });
  }

  async post(url, data, options) {
    return this.request(url, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async put(url, data, options) {
    return this.request(url, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  async delete(url, options) {
    return this.request(url, {
      ...options,
      method: 'DELETE'
    });
  }

  // Clear cache for specific patterns
  async invalidate(pattern) {
    await this.cache.clearPattern(`api:*${pattern}*`);
  }
}

// Export for use
export { FrontendCache, CachedAPI, cacheable };