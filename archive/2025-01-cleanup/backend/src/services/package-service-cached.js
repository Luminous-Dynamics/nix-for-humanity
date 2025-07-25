const { Cacheable, CacheEvict } = require('../cache/cache-decorators');
const { utils: cacheUtils } = require('../cache');

/**
 * Package service with caching
 */
class CachedPackageService {
  constructor(nixClient, eventBus) {
    this.nix = nixClient;
    this.events = eventBus;
  }

  /**
   * Search packages with caching
   */
  @Cacheable({
    ttl: 600000, // 10 minutes
    key: function(query, options) {
      return `packages:search:${query}:${JSON.stringify(options)}`;
    }
  })
  async search(query, options = {}) {
    const {
      limit = 20,
      offset = 0,
      channel = 'nixpkgs'
    } = options;

    // Perform search
    const results = await this.nix.search(query, {
      limit,
      offset,
      channel
    });

    // Emit event
    this.events.emit('package:search', {
      query,
      count: results.length,
      cached: false
    });

    return results;
  }

  /**
   * Get package details with caching
   */
  async getDetails(packageName) {
    return cacheUtils.remember(
      `packages:details:${packageName}`,
      async () => {
        const details = await this.nix.getPackageInfo(packageName);
        
        // Enrich with additional data
        details.installed = await this.isInstalled(packageName);
        details.dependencies = await this.getDependencies(packageName);
        
        return details;
      },
      300000 // 5 minutes
    );
  }

  /**
   * Get installed packages with caching
   */
  @Cacheable({
    ttl: 60000, // 1 minute
    prefix: 'packages:installed'
  })
  async getInstalled() {
    const packages = await this.nix.getInstalledPackages();
    
    // Group by category
    const categorized = packages.reduce((acc, pkg) => {
      const category = this.categorizePackage(pkg);
      if (!acc[category]) acc[category] = [];
      acc[category].push(pkg);
      return acc;
    }, {});

    return {
      packages,
      categories: categorized,
      total: packages.length
    };
  }

  /**
   * Install package - invalidates cache
   */
  @CacheEvict({
    pattern: 'packages:*'
  })
  async install(packageName, options = {}) {
    // Emit start event
    this.events.emit('package:install:start', { package: packageName });

    try {
      // Install package
      const result = await this.nix.installPackage(packageName, options);

      // Emit success event
      this.events.emit('package:install:success', {
        package: packageName,
        result
      });

      // Invalidate specific caches
      await this.invalidatePackageCache(packageName);

      return result;
    } catch (error) {
      // Emit error event
      this.events.emit('package:install:error', {
        package: packageName,
        error: error.message
      });
      throw error;
    }
  }

  /**
   * Remove package - invalidates cache
   */
  @CacheEvict({
    pattern: 'packages:*'
  })
  async remove(packageName) {
    const result = await this.nix.removePackage(packageName);
    
    // Invalidate specific caches
    await this.invalidatePackageCache(packageName);
    
    return result;
  }

  /**
   * Check if package is installed
   */
  async isInstalled(packageName) {
    return cacheUtils.remember(
      `packages:is-installed:${packageName}`,
      async () => {
        const installed = await this.getInstalled();
        return installed.packages.some(pkg => pkg.name === packageName);
      },
      30000 // 30 seconds
    );
  }

  /**
   * Get package dependencies
   */
  async getDependencies(packageName) {
    return cacheUtils.remember(
      `packages:dependencies:${packageName}`,
      async () => {
        return this.nix.getPackageDependencies(packageName);
      },
      3600000 // 1 hour
    );
  }

  /**
   * Get available versions
   */
  @Cacheable({
    ttl: 3600000, // 1 hour
    key: (name) => `packages:versions:${name}`
  })
  async getVersions(packageName) {
    return this.nix.getAvailableVersions(packageName);
  }

  /**
   * Bulk operations with caching
   */
  async searchBulk(queries) {
    const results = await Promise.all(
      queries.map(query => this.search(query))
    );

    return queries.reduce((acc, query, index) => {
      acc[query] = results[index];
      return acc;
    }, {});
  }

  /**
   * Get package statistics
   */
  @Cacheable({
    ttl: 300000, // 5 minutes
    prefix: 'packages:stats'
  })
  async getStatistics() {
    const installed = await this.getInstalled();
    const totalSize = await this.nix.getStorageUsage();
    
    return {
      installedCount: installed.total,
      categoryCounts: Object.keys(installed.categories).reduce((acc, cat) => {
        acc[cat] = installed.categories[cat].length;
        return acc;
      }, {}),
      totalSize,
      averageSize: installed.total > 0 ? totalSize / installed.total : 0
    };
  }

  /**
   * Invalidate package-specific cache
   */
  async invalidatePackageCache(packageName) {
    const cache = require('../cache').getCache();
    
    await Promise.all([
      cache.delete(`packages:details:${packageName}`),
      cache.delete(`packages:is-installed:${packageName}`),
      cache.delete(`packages:dependencies:${packageName}`),
      cache.delete(`packages:versions:${packageName}`)
    ]);
  }

  /**
   * Categorize package
   */
  categorizePackage(pkg) {
    const { name, meta } = pkg;
    
    if (name.includes('python') || meta?.maintainers?.includes('python')) {
      return 'development';
    }
    if (name.includes('lib') || name.startsWith('lib')) {
      return 'libraries';
    }
    if (meta?.section === 'games') {
      return 'games';
    }
    if (name.includes('font') || meta?.section === 'fonts') {
      return 'fonts';
    }
    if (meta?.section === 'admin' || name.includes('system')) {
      return 'system';
    }
    
    return 'applications';
  }

  /**
   * Warm up cache
   */
  async warmCache() {
    console.log('Warming package cache...');
    
    // Pre-cache common searches
    const commonSearches = [
      'firefox', 'git', 'vim', 'emacs', 'vscode',
      'docker', 'nodejs', 'python', 'rust', 'go'
    ];

    await Promise.all(
      commonSearches.map(query => 
        this.search(query).catch(err => 
          console.error(`Failed to warm cache for ${query}:`, err)
        )
      )
    );

    // Pre-cache installed packages
    await this.getInstalled();
    
    console.log('Package cache warmed');
  }
}

module.exports = CachedPackageService;