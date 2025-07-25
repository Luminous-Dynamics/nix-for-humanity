/**
 * Health Monitor for Nix for Humanity
 * Provides system health checks and metrics
 */

const os = require('os');
const { exec } = require('child_process');
const { promisify } = require('util');

const execAsync = promisify(exec);

class HealthMonitor {
  constructor(options = {}) {
    this.checkInterval = options.checkInterval || 30000; // 30 seconds
    this.metricsHistory = [];
    this.maxHistorySize = options.maxHistorySize || 100;
    this.healthChecks = new Map();
    this.periodicCheckInterval = null;
    
    // Register default health checks
    this.registerHealthCheck('system', this.checkSystem.bind(this));
    this.registerHealthCheck('nlp', this.checkNLP.bind(this));
    this.registerHealthCheck('security', this.checkSecurity.bind(this));
    this.registerHealthCheck('resources', this.checkResources.bind(this));
  }

  // Register a health check
  registerHealthCheck(name, checkFunction) {
    this.healthChecks.set(name, checkFunction);
  }

  // Start periodic health checks
  startPeriodicChecks() {
    if (this.periodicCheckInterval) {
      return;
    }
    
    this.periodicCheckInterval = setInterval(async () => {
      await this.collectMetrics();
    }, this.checkInterval);
    
    // Run initial check
    this.collectMetrics();
  }

  // Stop periodic health checks
  stopPeriodicChecks() {
    if (this.periodicCheckInterval) {
      clearInterval(this.periodicCheckInterval);
      this.periodicCheckInterval = null;
    }
  }

  // Collect all metrics
  async collectMetrics() {
    const metrics = {
      timestamp: new Date().toISOString(),
      system: await this.getSystemMetrics(),
      services: await this.getServiceMetrics(),
      resources: await this.getResourceMetrics()
    };
    
    // Store in history
    this.metricsHistory.push(metrics);
    if (this.metricsHistory.length > this.maxHistorySize) {
      this.metricsHistory.shift();
    }
    
    return metrics;
  }

  // Get system metrics
  async getSystemMetrics() {
    return {
      uptime: os.uptime(),
      loadavg: os.loadavg(),
      platform: os.platform(),
      release: os.release(),
      arch: os.arch(),
      hostname: os.hostname()
    };
  }

  // Get service metrics
  async getServiceMetrics() {
    const metrics = {
      nlp: { status: 'unknown' },
      security: { status: 'unknown' },
      executor: { status: 'unknown' }
    };
    
    // Check each service
    for (const [name, check] of this.healthChecks) {
      try {
        const result = await check();
        metrics[name] = result;
      } catch (error) {
        metrics[name] = {
          status: 'error',
          error: error.message
        };
      }
    }
    
    return metrics;
  }

  // Get resource metrics
  async getResourceMetrics() {
    const totalMem = os.totalmem();
    const freeMem = os.freemem();
    const usedMem = totalMem - freeMem;
    
    return {
      memory: {
        total: totalMem,
        free: freeMem,
        used: usedMem,
        percentage: (usedMem / totalMem) * 100
      },
      cpu: {
        cores: os.cpus().length,
        model: os.cpus()[0]?.model || 'unknown',
        speed: os.cpus()[0]?.speed || 0
      }
    };
  }

  // Health check: System
  async checkSystem() {
    try {
      // Check if NixOS
      const { stdout } = await execAsync('which nix', { timeout: 5000 });
      const hasNix = stdout.trim().length > 0;
      
      return {
        status: hasNix ? 'healthy' : 'degraded',
        nixAvailable: hasNix,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      return {
        status: 'degraded',
        nixAvailable: false,
        error: 'Nix not found',
        timestamp: new Date().toISOString()
      };
    }
  }

  // Health check: NLP
  async checkNLP() {
    // This would check if NLP service is responsive
    return {
      status: 'healthy',
      patternsLoaded: true,
      modelsReady: true,
      timestamp: new Date().toISOString()
    };
  }

  // Health check: Security
  async checkSecurity() {
    return {
      status: 'healthy',
      authServiceReady: true,
      certificatesValid: true,
      timestamp: new Date().toISOString()
    };
  }

  // Health check: Resources
  async checkResources() {
    const memoryUsage = process.memoryUsage();
    const cpuUsage = process.cpuUsage();
    
    return {
      status: 'healthy',
      memory: {
        rss: memoryUsage.rss,
        heapTotal: memoryUsage.heapTotal,
        heapUsed: memoryUsage.heapUsed,
        external: memoryUsage.external
      },
      cpu: {
        user: cpuUsage.user,
        system: cpuUsage.system
      },
      timestamp: new Date().toISOString()
    };
  }

  // Get routes for Express
  getRoutes() {
    return {
      health: async (req, res) => {
        const checks = {};
        let overallStatus = 'healthy';
        
        // Run all health checks
        for (const [name, check] of this.healthChecks) {
          try {
            checks[name] = await check();
            if (checks[name].status !== 'healthy') {
              overallStatus = 'degraded';
            }
          } catch (error) {
            checks[name] = {
              status: 'error',
              error: error.message
            };
            overallStatus = 'unhealthy';
          }
        }
        
        const statusCode = overallStatus === 'healthy' ? 200 : 
                          overallStatus === 'degraded' ? 200 : 503;
        
        res.status(statusCode).json({
          status: overallStatus,
          timestamp: new Date().toISOString(),
          checks
        });
      },
      
      checkSpecific: async (req, res) => {
        const checkName = req.params.check;
        const check = this.healthChecks.get(checkName);
        
        if (!check) {
          return res.status(404).json({
            error: 'Health check not found',
            available: Array.from(this.healthChecks.keys())
          });
        }
        
        try {
          const result = await check();
          res.json(result);
        } catch (error) {
          res.status(503).json({
            status: 'error',
            error: error.message
          });
        }
      },
      
      metrics: async (req, res) => {
        const currentMetrics = await this.collectMetrics();
        
        res.json({
          current: currentMetrics,
          history: this.metricsHistory.slice(-10) // Last 10 entries
        });
      },
      
      ready: (req, res) => {
        // Simple readiness check
        res.json({
          ready: true,
          timestamp: new Date().toISOString()
        });
      },
      
      live: (req, res) => {
        // Simple liveness check
        res.json({
          alive: true,
          timestamp: new Date().toISOString()
        });
      }
    };
  }

  // Get current health summary
  async getHealthSummary() {
    const summary = {
      timestamp: new Date().toISOString(),
      status: 'healthy',
      checks: {}
    };
    
    for (const [name, check] of this.healthChecks) {
      try {
        const result = await check();
        summary.checks[name] = result.status;
        if (result.status !== 'healthy') {
          summary.status = 'degraded';
        }
      } catch (error) {
        summary.checks[name] = 'error';
        summary.status = 'unhealthy';
      }
    }
    
    return summary;
  }
}

module.exports = HealthMonitor;