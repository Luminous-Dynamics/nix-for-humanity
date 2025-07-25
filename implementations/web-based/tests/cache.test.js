const { CacheService } = require('../backend/services/cache');
const { BrowserCache, MemoryCache, CachedAPI } = require('../js/utils/cache');

// Mock Redis client
jest.mock('redis', () => ({
  createClient: jest.fn(() => ({
    on: jest.fn(),
    get: jest.fn((key, cb) => cb(null, null)),
    set: jest.fn((key, value, mode, ttl, cb) => cb(null, 'OK')),
    del: jest.fn((key, cb) => cb(null, 1)),
    keys: jest.fn((pattern, cb) => cb(null, [])),
    ttl: jest.fn((key, cb) => cb(null, -1)),
    expire: jest.fn((key, ttl, cb) => cb(null, 1)),
    mget: jest.fn((keys, cb) => cb(null, [])),
    mset: jest.fn((...args) => {
      const cb = args[args.length - 1];
      cb(null, 'OK');
    }),
    quit: jest.fn()
  }))
}));

describe('Backend Cache Service', () => {
  let cache;

  beforeEach(() => {
    cache = new CacheService({
      ttl: {
        test: 60
      }
    });
  });

  afterEach(() => {
    cache.disconnect();
  });

  describe('Basic Operations', () => {
    test('should generate consistent keys', () => {
      const key1 = cache.generateKey('namespace', 'identifier');
      const key2 = cache.generateKey('namespace', 'identifier');
      expect(key1).toBe(key2);
      expect(key1).toBe('nixos-gui:namespace:identifier');
    });

    test('should generate consistent keys for objects', () => {
      const obj1 = { b: 2, a: 1 };
      const obj2 = { a: 1, b: 2 };
      const key1 = cache.generateKey('namespace', obj1);
      const key2 = cache.generateKey('namespace', obj2);
      expect(key1).toBe(key2);
    });

    test('should handle cache miss', async () => {
      const result = await cache.getCache('test', 'missing');
      expect(result).toBeNull();
      expect(cache.stats.misses).toBe(1);
    });

    test('should set and get from fallback cache', async () => {
      cache.connected = false; // Force fallback
      
      await cache.setCache('test', 'key', { value: 'data' });
      const result = await cache.getCache('test', 'key');
      
      expect(result).toEqual({ value: 'data' });
      expect(cache.stats.fallbackHits).toBe(1);
    });

    test('should respect TTL in fallback cache', async () => {
      cache.connected = false;
      
      await cache.setCache('test', 'key', { value: 'data' }, 0.1); // 100ms TTL
      
      // Should get value immediately
      let result = await cache.getCache('test', 'key');
      expect(result).toEqual({ value: 'data' });
      
      // Wait for expiration
      await new Promise(resolve => setTimeout(resolve, 150));
      
      result = await cache.getCache('test', 'key');
      expect(result).toBeNull();
    });
  });

  describe('Batch Operations', () => {
    test('should get multiple values in batch', async () => {
      cache.connected = false; // Use fallback
      
      await cache.setCache('test', 'key1', 'value1');
      await cache.setCache('test', 'key2', 'value2');
      
      const results = await cache.getBatch('test', ['key1', 'key2', 'key3']);
      
      expect(results.get('key1')).toBe('value1');
      expect(results.get('key2')).toBe('value2');
      expect(results.has('key3')).toBe(false);
    });

    test('should set multiple values in batch', async () => {
      cache.connected = false;
      
      await cache.setBatch('test', [
        { identifier: 'key1', value: 'value1' },
        { identifier: 'key2', value: 'value2' }
      ]);
      
      const result1 = await cache.getCache('test', 'key1');
      const result2 = await cache.getCache('test', 'key2');
      
      expect(result1).toBe('value1');
      expect(result2).toBe('value2');
    });
  });

  describe('Cache Strategies', () => {
    test('should use getOrSet strategy', async () => {
      let fetchCount = 0;
      const fetcher = jest.fn(async () => {
        fetchCount++;
        return { data: 'fetched' };
      });
      
      // First call should fetch
      const result1 = await cache.getOrSet('test', 'key', fetcher);
      expect(result1).toEqual({ data: 'fetched' });
      expect(fetchCount).toBe(1);
      
      // Second call should use cache
      const result2 = await cache.getOrSet('test', 'key', fetcher);
      expect(result2).toEqual({ data: 'fetched' });
      expect(fetchCount).toBe(1); // Not incremented
    });

    test('should use staleWhileRevalidate strategy', async () => {
      let fetchCount = 0;
      const fetcher = jest.fn(async () => {
        fetchCount++;
        await new Promise(resolve => setTimeout(resolve, 50));
        return { data: `fetched-${fetchCount}` };
      });
      
      // First call should fetch synchronously
      const result1 = await cache.staleWhileRevalidate('test', 'key', fetcher);
      expect(result1).toEqual({ data: 'fetched-1' });
      expect(fetchCount).toBe(1);
      
      // Second call should return stale immediately and refresh in background
      const result2 = await cache.staleWhileRevalidate('test', 'key', fetcher);
      expect(result2).toEqual({ data: 'fetched-1' }); // Stale data
      
      // Wait for background refresh
      await new Promise(resolve => setTimeout(resolve, 100));
      expect(fetchCount).toBe(2); // Background fetch completed
      
      // Third call should get refreshed data
      const result3 = await cache.staleWhileRevalidate('test', 'key', fetcher);
      expect(result3).toEqual({ data: 'fetched-2' });
    });
  });

  describe('Invalidation', () => {
    test('should invalidate specific key', async () => {
      cache.connected = false;
      
      await cache.setCache('test', 'key1', 'value1');
      await cache.setCache('test', 'key2', 'value2');
      
      await cache.invalidate('test', 'key1');
      
      expect(await cache.getCache('test', 'key1')).toBeNull();
      expect(await cache.getCache('test', 'key2')).toBe('value2');
    });

    test('should invalidate namespace', async () => {
      cache.connected = false;
      
      await cache.setCache('test', 'key1', 'value1');
      await cache.setCache('test', 'key2', 'value2');
      await cache.setCache('other', 'key3', 'value3');
      
      await cache.invalidate('test');
      
      expect(await cache.getCache('test', 'key1')).toBeNull();
      expect(await cache.getCache('test', 'key2')).toBeNull();
      expect(await cache.getCache('other', 'key3')).toBe('value3');
    });

    test('should invalidate by pattern', async () => {
      cache.connected = false;
      
      await cache.setCache('test', 'user:1', 'data1');
      await cache.setCache('test', 'user:2', 'data2');
      await cache.setCache('test', 'post:1', 'data3');
      
      await cache.invalidatePattern('test:user:*');
      
      expect(await cache.getCache('test', 'user:1')).toBeNull();
      expect(await cache.getCache('test', 'user:2')).toBeNull();
      expect(await cache.getCache('test', 'post:1')).toBe('data3');
    });
  });

  describe('Stats and Monitoring', () => {
    test('should track cache statistics', async () => {
      cache.connected = false;
      
      // Generate some activity
      await cache.setCache('test', 'key', 'value');
      await cache.getCache('test', 'key'); // Hit
      await cache.getCache('test', 'missing'); // Miss
      
      const stats = cache.getStats();
      
      expect(stats.hits).toBe(0); // Fallback hits tracked separately
      expect(stats.fallbackHits).toBe(1);
      expect(stats.misses).toBe(1);
      expect(stats.total).toBe(2);
      expect(parseFloat(stats.hitRate)).toBeCloseTo(50, 0);
    });

    test('should clean up expired entries', async () => {
      cache.connected = false;
      
      // Add entries with short TTL
      await cache.setCache('test', 'key1', 'value1', 0.1);
      await cache.setCache('test', 'key2', 'value2', 10);
      
      // Wait for first to expire
      await new Promise(resolve => setTimeout(resolve, 150));
      
      const cleaned = await cache.cleanup();
      
      expect(cleaned).toBe(1);
      expect(cache.fallbackCache.has(cache.generateKey('test', 'key1'))).toBe(false);
      expect(cache.fallbackCache.has(cache.generateKey('test', 'key2'))).toBe(true);
    });
  });
});

describe('Frontend Cache', () => {
  // Mock localStorage
  const localStorageMock = (() => {
    let store = {};
    return {
      getItem: jest.fn(key => store[key] || null),
      setItem: jest.fn((key, value) => { store[key] = value; }),
      removeItem: jest.fn(key => { delete store[key]; }),
      clear: jest.fn(() => { store = {}; }),
      key: jest.fn(index => Object.keys(store)[index] || null),
      get length() { return Object.keys(store).length; }
    };
  })();

  Object.defineProperty(window, 'localStorage', {
    value: localStorageMock
  });

  describe('BrowserCache', () => {
    let cache;

    beforeEach(() => {
      localStorageMock.clear();
      cache = new BrowserCache({
        prefix: 'test:',
        defaultTTL: 1000
      });
    });

    test('should store and retrieve values', () => {
      cache.set('test', 'key', { data: 'value' });
      const result = cache.get('test', 'key');
      
      expect(result).toEqual({ data: 'value' });
      expect(cache.stats.hits).toBe(1);
    });

    test('should respect TTL', async () => {
      cache.set('test', 'key', { data: 'value' }, 100);
      
      // Should get value immediately
      expect(cache.get('test', 'key')).toEqual({ data: 'value' });
      
      // Wait for expiration
      await new Promise(resolve => setTimeout(resolve, 150));
      
      expect(cache.get('test', 'key')).toBeNull();
    });

    test('should handle storage quota errors', () => {
      // Mock quota exceeded error
      localStorageMock.setItem.mockImplementationOnce(() => {
        const error = new Error('QuotaExceededError');
        error.name = 'QuotaExceededError';
        throw error;
      });
      
      const spy = jest.spyOn(cache, 'evictOldest');
      
      cache.set('test', 'key', { data: 'value' });
      
      expect(spy).toHaveBeenCalled();
    });

    test('should calculate storage size', () => {
      cache.set('test', 'key1', 'short');
      cache.set('test', 'key2', 'a'.repeat(1000));
      
      const size = cache.getCurrentSize();
      expect(size).toBeGreaterThan(1000);
    });
  });

  describe('MemoryCache', () => {
    let cache;

    beforeEach(() => {
      cache = new MemoryCache({
        maxEntries: 3,
        defaultTTL: 1000
      });
    });

    test('should enforce max entries with LRU eviction', () => {
      cache.set('test', 'key1', 'value1');
      cache.set('test', 'key2', 'value2');
      cache.set('test', 'key3', 'value3');
      
      // Access key1 to make it recently used
      cache.get('test', 'key1');
      
      // Add new entry, should evict key2 (least recently used)
      cache.set('test', 'key4', 'value4');
      
      expect(cache.get('test', 'key1')).toBe('value1');
      expect(cache.get('test', 'key2')).toBeNull();
      expect(cache.get('test', 'key3')).toBe('value3');
      expect(cache.get('test', 'key4')).toBe('value4');
      expect(cache.stats.evictions).toBe(1);
    });
  });

  describe('CachedAPI', () => {
    let api, cachedAPI;

    beforeEach(() => {
      localStorageMock.clear();
      
      api = {
        fetchData: jest.fn(async (id) => ({ id, data: `data-${id}` }))
      };
      
      cachedAPI = new CachedAPI(api, {
        browserCache: { defaultTTL: 1000 },
        memoryCache: { maxEntries: 10 },
        ttls: { test: 500 }
      });
    });

    test('should cache API responses', async () => {
      const fetcher = () => api.fetchData('123');
      
      // First call - fetches from API
      const result1 = await cachedAPI.cachedRequest('test', '123', fetcher);
      expect(result1).toEqual({ id: '123', data: 'data-123' });
      expect(api.fetchData).toHaveBeenCalledTimes(1);
      
      // Second call - from cache
      const result2 = await cachedAPI.cachedRequest('test', '123', fetcher);
      expect(result2).toEqual({ id: '123', data: 'data-123' });
      expect(api.fetchData).toHaveBeenCalledTimes(1); // Not called again
    });

    test('should return stale data on error', async () => {
      const fetcher = () => api.fetchData('123');
      
      // First call succeeds
      await cachedAPI.cachedRequest('test', '123', fetcher);
      
      // Make API fail
      api.fetchData.mockRejectedValueOnce(new Error('Network error'));
      
      // Should return cached data
      const result = await cachedAPI.cachedRequest('test', '123', fetcher);
      expect(result).toEqual({ id: '123', data: 'data-123' });
    });

    test('should respect cache options', async () => {
      const fetcher = () => api.fetchData('123');
      
      // Cache in memory only
      await cachedAPI.cachedRequest('test', 'mem-only', fetcher, {
        memory: true,
        browser: false
      });
      
      expect(cachedAPI.memoryCache.get('test', 'mem-only')).toBeTruthy();
      expect(cachedAPI.cache.get('test', 'mem-only')).toBeNull();
      
      // Cache in browser only
      await cachedAPI.cachedRequest('test', 'browser-only', fetcher, {
        memory: false,
        browser: true
      });
      
      expect(cachedAPI.memoryCache.get('test', 'browser-only')).toBeNull();
      expect(cachedAPI.cache.get('test', 'browser-only')).toBeTruthy();
    });
  });
});