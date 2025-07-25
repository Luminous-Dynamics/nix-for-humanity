/**
 * Health Check and Monitoring Service for Nix for Humanity
 * Provides comprehensive system health monitoring
 */

const os = require('os');
const { exec } = require('child_process');
const { promisify } = require('util');
const fs = require('fs').promises;
const path = require('path');

const execAsync = promisify(exec);

class HealthMonitor {
  constructor(options = {}) {
    this.checks = new Map();
    this.metrics = new Map();
    this.startTime = Date.now();
    this.checkInterval = options.checkInterval || 30000; // 30 seconds
    this.retentionPeriod = options.retentionPeriod || 3600000; // 1 hour
    
    // Initialize checks
    this.initializeChecks();
    
    // Start periodic health checks
    if (options.autoStart !== false) {
      this.startPeriodicChecks();
    }
  }

  initializeChecks() {
    // System checks
    this.registerCheck('system', async () => this.checkSystem());
    this.registerCheck('memory', async () => this.checkMemory());
    this.registerCheck('disk', async () => this.checkDisk());
    this.registerCheck('network', async () => this.checkNetwork());
    
    // Service checks
    this.registerCheck('nlp', async () => this.checkNLPService());
    this.registerCheck('database', async () => this.checkDatabase());
    this.registerCheck('nix', async () => this.checkNixAvailability());
    
    // Security checks
    this.registerCheck('permissions', async () => this.checkPermissions());
    this.registerCheck('ssl', async () => this.checkSSLCertificates());
  }

  registerCheck(name, checkFunction) {
    this.checks.set(name, {
      name,
      check: checkFunction,
      lastResult: null,
      lastRun: null,
      consecutiveFailures: 0
    });
  }

  async runCheck(name) {
    const check = this.checks.get(name);
    if (!check) {
      throw new Error(`Unknown health check: ${name}`);
    }

    const startTime = Date.now();
    let result;

    try {
      result = await check.check();
      check.consecutiveFailures = 0;
    } catch (error) {
      result = {
        status: 'unhealthy',
        message: error.message,
        error: error.stack
      };
      check.consecutiveFailures++;
    }

    const duration = Date.now() - startTime;
    check.lastResult = {
      ...result,
      duration,
      timestamp: new Date().toISOString()
    };
    check.lastRun = Date.now();

    // Record metrics
    this.recordMetric(`health.${name}.duration`, duration);
    this.recordMetric(`health.${name}.status`, result.status === 'healthy' ? 1 : 0);

    return check.lastResult;
  }

  async runAllChecks() {
    const results = {};
    
    for (const [name, check] of this.checks) {
      results[name] = await this.runCheck(name);
    }
    
    return results;
  }

  // System health check
  async checkSystem() {
    const uptime = os.uptime();
    const loadAvg = os.loadavg();
    const cpuCount = os.cpus().length;
    
    // Check if load is too high
    const loadThreshold = cpuCount * 2;
    const currentLoad = loadAvg[0];
    
    return {
      status: currentLoad < loadThreshold ? 'healthy' : 'degraded',
      uptime,
      loadAverage: loadAvg,
      cpuCount,
      platform: os.platform(),
      architecture: os.arch(),
      nodeVersion: process.version,
      message: currentLoad < loadThreshold 
        ? 'System load is normal' 
        : 'System load is high'
    };
  }

  // Memory health check
  async checkMemory() {
    const totalMem = os.totalmem();
    const freeMem = os.freemem();
    const usedMem = totalMem - freeMem;
    const memoryUsagePercent = (usedMem / totalMem) * 100;
    
    // Process memory
    const processMemory = process.memoryUsage();
    
    return {
      status: memoryUsagePercent < 85 ? 'healthy' : 'degraded',
      system: {
        total: totalMem,
        free: freeMem,
        used: usedMem,
        percentage: Math.round(memoryUsagePercent)
      },
      process: {
        rss: processMemory.rss,
        heapTotal: processMemory.heapTotal,
        heapUsed: processMemory.heapUsed,
        external: processMemory.external
      },
      message: memoryUsagePercent < 85 
        ? 'Memory usage is normal' 
        : 'Memory usage is high'
    };
  }

  // Disk health check
  async checkDisk() {
    try {
      const { stdout } = await execAsync('df -h /');
      const lines = stdout.trim().split('\n');
      const diskInfo = lines[1].split(/\s+/);
      
      const usagePercent = parseInt(diskInfo[4]);
      
      return {
        status: usagePercent < 80 ? 'healthy' : 'degraded',
        filesystem: diskInfo[0],
        size: diskInfo[1],
        used: diskInfo[2],
        available: diskInfo[3],
        usagePercent,
        mountPoint: diskInfo[5],
        message: usagePercent < 80 
          ? 'Disk space is adequate' 
          : 'Disk space is running low'
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        message: 'Could not check disk space',
        error: error.message
      };
    }
  }

  // Network health check
  async checkNetwork() {
    try {
      // Check if we can resolve DNS
      const { stdout } = await execAsync('nslookup nixos.org');
      
      return {
        status: 'healthy',
        message: 'Network connectivity is good',
        dnsResolution: true
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        message: 'Network connectivity issues',
        dnsResolution: false,
        error: error.message
      };
    }
  }

  // NLP service health check
  async checkNLPService() {
    // Check if NLP patterns are loaded
    const patternsPath = path.join(__dirname, '../nlp/patterns.json');
    
    try {
      await fs.access(patternsPath);
      const stats = await fs.stat(patternsPath);
      
      return {
        status: 'healthy',
        message: 'NLP service is ready',
        patternsLoaded: true,
        patternsSize: stats.size,
        patternsModified: stats.mtime
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        message: 'NLP patterns not found',
        patternsLoaded: false,
        error: error.message
      };
    }
  }

  // Database health check
  async checkDatabase() {
    const dbPath = path.join(process.env.HOME, '.config/nix-for-humanity/data.db');
    
    try {
      await fs.access(dbPath);
      const stats = await fs.stat(dbPath);
      
      return {
        status: 'healthy',
        message: 'Database is accessible',
        path: dbPath,
        size: stats.size,
        modified: stats.mtime
      };
    } catch (error) {
      // Database might not exist yet, which is okay
      return {
        status: 'healthy',
        message: 'Database will be created on first use',
        exists: false
      };
    }
  }

  // Nix availability check
  async checkNixAvailability() {
    try {
      const { stdout } = await execAsync('nix --version');
      const version = stdout.trim();
      
      // Check if experimental features are enabled
      let experimentalFeatures = false;
      try {
        await execAsync('nix show-config | grep "experimental-features"');
        experimentalFeatures = true;
      } catch (e) {
        // Experimental features might not be enabled
      }
      
      return {
        status: 'healthy',
        message: 'Nix is available',
        version,
        experimentalFeatures
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        message: 'Nix is not available',
        error: error.message,
        suggestion: 'Please ensure Nix is installed and in PATH'
      };
    }
  }

  // Permissions check
  async checkPermissions() {
    const configDir = path.join(process.env.HOME, '.config/nix-for-humanity');
    
    try {
      // Check if we can write to config directory
      await fs.mkdir(configDir, { recursive: true });
      const testFile = path.join(configDir, '.write-test');
      await fs.writeFile(testFile, 'test');
      await fs.unlink(testFile);
      
      return {
        status: 'healthy',
        message: 'Permissions are correctly set',
        configDir,
        writable: true
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        message: 'Permission issues detected',
        configDir,
        writable: false,
        error: error.message
      };
    }
  }

  // SSL certificate check
  async checkSSLCertificates() {
    const sslPath = path.join(__dirname, '../../ssl');
    
    try {
      const certPath = path.join(sslPath, 'cert.pem');
      const keyPath = path.join(sslPath, 'key.pem');
      
      await fs.access(certPath);
      await fs.access(keyPath);
      
      // Check certificate expiry (basic check)
      const certStats = await fs.stat(certPath);
      const certAge = Date.now() - certStats.mtime.getTime();
      const daysOld = certAge / (1000 * 60 * 60 * 24);
      
      return {
        status: daysOld < 300 ? 'healthy' : 'degraded',
        message: daysOld < 300 
          ? 'SSL certificates are valid' 
          : 'SSL certificates may need renewal soon',
        certificateAge: Math.round(daysOld),
        sslEnabled: true
      };
    } catch (error) {
      return {
        status: 'degraded',
        message: 'SSL certificates not found (using HTTP)',
        sslEnabled: false,
        note: 'HTTPS recommended for production'
      };
    }
  }

  // Record metrics
  recordMetric(name, value) {
    if (!this.metrics.has(name)) {
      this.metrics.set(name, []);
    }
    
    const metric = {
      value,
      timestamp: Date.now()
    };
    
    this.metrics.get(name).push(metric);
    
    // Clean old metrics
    this.cleanOldMetrics(name);
  }

  cleanOldMetrics(name) {
    const metrics = this.metrics.get(name);
    const cutoff = Date.now() - this.retentionPeriod;
    
    const filtered = metrics.filter(m => m.timestamp > cutoff);
    this.metrics.set(name, filtered);
  }

  // Get aggregated metrics
  getMetrics(name, period = 300000) { // Default 5 minutes
    const metrics = this.metrics.get(name) || [];
    const cutoff = Date.now() - period;
    const recent = metrics.filter(m => m.timestamp > cutoff);
    
    if (recent.length === 0) {
      return null;
    }
    
    const values = recent.map(m => m.value);
    const sum = values.reduce((a, b) => a + b, 0);
    
    return {
      count: values.length,
      sum,
      average: sum / values.length,
      min: Math.min(...values),
      max: Math.max(...values),
      latest: values[values.length - 1]
    };
  }

  // Get overall health status
  async getOverallHealth() {
    const checks = await this.runAllChecks();
    
    let healthy = 0;
    let degraded = 0;
    let unhealthy = 0;
    
    for (const result of Object.values(checks)) {
      switch (result.status) {
        case 'healthy':
          healthy++;
          break;
        case 'degraded':
          degraded++;
          break;
        case 'unhealthy':
          unhealthy++;
          break;
      }
    }
    
    const total = healthy + degraded + unhealthy;
    const overallStatus = unhealthy > 0 ? 'unhealthy' : 
                         degraded > 0 ? 'degraded' : 'healthy';
    
    return {
      status: overallStatus,
      summary: {
        healthy,
        degraded,
        unhealthy,
        total
      },
      uptime: Date.now() - this.startTime,
      timestamp: new Date().toISOString(),
      checks
    };
  }

  // Start periodic health checks
  startPeriodicChecks() {
    this.checkTimer = setInterval(async () => {
      try {
        await this.runAllChecks();
      } catch (error) {
        console.error('Error in periodic health check:', error);
      }
    }, this.checkInterval);
  }

  // Stop periodic health checks
  stopPeriodicChecks() {
    if (this.checkTimer) {
      clearInterval(this.checkTimer);
      this.checkTimer = null;
    }
  }

  // Express route handlers
  getRoutes() {
    return {
      // Simple health check endpoint
      health: async (req, res) => {
        const health = await this.getOverallHealth();
        const statusCode = health.status === 'healthy' ? 200 : 
                          health.status === 'degraded' ? 200 : 503;
        
        res.status(statusCode).json(health);
      },
      
      // Specific check endpoint
      checkSpecific: async (req, res) => {
        const { check } = req.params;
        
        try {
          const result = await this.runCheck(check);
          res.json(result);
        } catch (error) {
          res.status(404).json({
            error: 'Check not found',
            message: error.message
          });
        }
      },
      
      // Metrics endpoint
      metrics: (req, res) => {
        const { metric, period } = req.query;
        
        if (metric) {
          const data = this.getMetrics(metric, parseInt(period) || 300000);
          res.json({ metric, data });
        } else {
          // Return all metrics
          const allMetrics = {};
          for (const [name, _] of this.metrics) {
            allMetrics[name] = this.getMetrics(name);
          }
          res.json(allMetrics);
        }
      },
      
      // Readiness probe (for k8s)
      ready: async (req, res) => {
        const nixCheck = await this.runCheck('nix');
        const nlpCheck = await this.runCheck('nlp');
        
        const ready = nixCheck.status === 'healthy' && 
                     nlpCheck.status === 'healthy';
        
        res.status(ready ? 200 : 503).json({
          ready,
          checks: { nix: nixCheck, nlp: nlpCheck }
        });
      },
      
      // Liveness probe (for k8s)
      live: (req, res) => {
        res.status(200).json({
          alive: true,
          uptime: Date.now() - this.startTime,
          pid: process.pid
        });
      }
    };
  }
}

module.exports = HealthMonitor;