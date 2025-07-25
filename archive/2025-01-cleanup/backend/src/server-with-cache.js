const express = require('express');
const compression = require('compression');
const helmet = require('helmet');
const cors = require('cors');
const { createServer } = require('http');
const { Server } = require('socket.io');
const sqlite3 = require('sqlite3');
const { open } = require('sqlite');
const redis = require('redis');
const path = require('path');

// Import cache modules
const { 
  initCache, 
  createCacheMiddleware, 
  createInvalidationMiddleware 
} = require('./cache');

// Import services
const CachedPackageService = require('./services/package-service-cached');
const ConfigService = require('./services/config-service');
const ServiceManager = require('./services/service-manager');

// Import middleware
const { authMiddleware } = require('./middleware/auth');
const { auditMiddleware } = require('./middleware/audit');
const { rateLimiter } = require('./middleware/rate-limit');
const { errorHandler } = require('./middleware/error-handler');

class Server {
  constructor(config = {}) {
    this.config = {
      port: process.env.PORT || 8080,
      host: process.env.HOST || 'localhost',
      dbPath: process.env.DB_PATH || '/var/lib/nixos-gui/db.sqlite',
      redisUrl: process.env.REDIS_URL,
      cacheEnabled: process.env.CACHE_ENABLED !== 'false',
      ...config
    };

    this.app = express();
    this.server = createServer(this.app);
    this.io = new Server(this.server, {
      cors: {
        origin: process.env.CORS_ORIGIN || 'http://localhost:3000',
        credentials: true
      }
    });
  }

  async init() {
    // Initialize database
    this.db = await open({
      filename: this.config.dbPath,
      driver: sqlite3.Database
    });

    // Initialize Redis (optional)
    if (this.config.redisUrl) {
      this.redis = redis.createClient({
        url: this.config.redisUrl
      });
      await this.redis.connect();
      console.log('Redis connected');
    }

    // Initialize cache
    if (this.config.cacheEnabled) {
      await initCache(this.db, this.redis, {
        ttl: 300000, // 5 minutes default
        maxSize: 100 * 1024 * 1024 // 100MB
      });
      console.log('Cache layer initialized');
    }

    // Initialize services
    this.initServices();

    // Setup middleware
    this.setupMiddleware();

    // Setup routes
    this.setupRoutes();

    // Setup WebSocket
    this.setupWebSocket();

    // Warm cache
    if (this.config.cacheEnabled) {
      this.warmCache();
    }
  }

  initServices() {
    // Initialize event bus
    const EventEmitter = require('events');
    this.eventBus = new EventEmitter();

    // Initialize services with caching
    this.packageService = new CachedPackageService(
      this.nixClient,
      this.eventBus
    );

    this.configService = new ConfigService();
    this.serviceManager = new ServiceManager();
  }

  setupMiddleware() {
    // Security
    this.app.use(helmet({
      contentSecurityPolicy: {
        directives: {
          defaultSrc: ["'self'"],
          scriptSrc: ["'self'", "'unsafe-inline'"],
          styleSrc: ["'self'", "'unsafe-inline'"],
          imgSrc: ["'self'", "data:", "https:"],
          connectSrc: ["'self'", "ws:", "wss:"]
        }
      }
    }));

    // CORS
    this.app.use(cors({
      origin: process.env.CORS_ORIGIN || 'http://localhost:3000',
      credentials: true
    }));

    // Compression
    this.app.use(compression());

    // Body parsing
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true }));

    // Rate limiting
    this.app.use('/api/', rateLimiter);

    // Authentication
    this.app.use('/api/', authMiddleware);

    // Audit logging
    this.app.use('/api/', auditMiddleware);

    // Cache middleware
    if (this.config.cacheEnabled) {
      // Response caching
      this.app.use('/api/', createCacheMiddleware({
        defaultTTL: 300000,
        excludePaths: ['/api/auth', '/api/ws'],
        excludeMethods: ['POST', 'PUT', 'DELETE', 'PATCH']
      }));

      // Cache invalidation
      this.app.use('/api/', createInvalidationMiddleware());
    }

    // Static files
    this.app.use(express.static(path.join(__dirname, '../../frontend/dist')));
  }

  setupRoutes() {
    // API routes
    const apiRouter = express.Router();

    // Health check
    apiRouter.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        cache: this.config.cacheEnabled ? 'enabled' : 'disabled',
        redis: this.redis ? 'connected' : 'not configured'
      });
    });

    // Cache statistics endpoint
    if (this.config.cacheEnabled) {
      apiRouter.get('/cache/stats', async (req, res) => {
        const cache = require('./cache').getCache();
        const stats = cache.getStats();
        res.json(stats);
      });

      apiRouter.delete('/cache/clear', async (req, res) => {
        const cache = require('./cache').getCache();
        await cache.clear();
        res.json({ message: 'Cache cleared' });
      });
    }

    // Package routes
    apiRouter.get('/packages/search', async (req, res, next) => {
      try {
        const { q, limit, offset } = req.query;
        const results = await this.packageService.search(q, {
          limit: parseInt(limit) || 20,
          offset: parseInt(offset) || 0
        });
        res.json(results);
      } catch (error) {
        next(error);
      }
    });

    apiRouter.get('/packages/installed', async (req, res, next) => {
      try {
        const installed = await this.packageService.getInstalled();
        res.json(installed);
      } catch (error) {
        next(error);
      }
    });

    apiRouter.get('/packages/:name', async (req, res, next) => {
      try {
        const details = await this.packageService.getDetails(req.params.name);
        res.json(details);
      } catch (error) {
        next(error);
      }
    });

    apiRouter.post('/packages/install', async (req, res, next) => {
      try {
        const { package: packageName } = req.body;
        const result = await this.packageService.install(packageName);
        res.json(result);
      } catch (error) {
        next(error);
      }
    });

    // Mount API router
    this.app.use('/api', apiRouter);

    // Error handling
    this.app.use(errorHandler);

    // Catch-all for SPA
    this.app.get('*', (req, res) => {
      res.sendFile(path.join(__dirname, '../../frontend/dist/index.html'));
    });
  }

  setupWebSocket() {
    // Authentication for WebSocket
    this.io.use((socket, next) => {
      const token = socket.handshake.auth.token;
      // Validate token
      if (token) {
        next();
      } else {
        next(new Error('Authentication required'));
      }
    });

    this.io.on('connection', (socket) => {
      console.log('Client connected:', socket.id);

      // Subscribe to events
      socket.on('subscribe', (channels) => {
        channels.forEach(channel => {
          socket.join(channel);
        });
      });

      // Forward events from event bus to clients
      const forwardEvent = (eventName) => {
        this.eventBus.on(eventName, (data) => {
          socket.emit(eventName, data);
        });
      };

      // Register event forwarding
      [
        'package:install:start',
        'package:install:progress',
        'package:install:success',
        'package:install:error',
        'service:status:change',
        'config:change',
        'generation:switch'
      ].forEach(forwardEvent);

      socket.on('disconnect', () => {
        console.log('Client disconnected:', socket.id);
      });
    });
  }

  async warmCache() {
    console.log('Warming cache...');
    
    try {
      // Warm package cache
      await this.packageService.warmCache();
      
      // Pre-cache system info
      // await this.systemService.getInfo();
      
      // Pre-cache service list
      // await this.serviceManager.listServices();
      
      console.log('Cache warming complete');
    } catch (error) {
      console.error('Cache warming failed:', error);
    }
  }

  async start() {
    await this.init();

    return new Promise((resolve) => {
      this.server.listen(this.config.port, this.config.host, () => {
        console.log(`NixOS GUI server listening on http://${this.config.host}:${this.config.port}`);
        console.log(`Cache: ${this.config.cacheEnabled ? 'Enabled' : 'Disabled'}`);
        console.log(`Redis: ${this.redis ? 'Connected' : 'Not configured'}`);
        resolve();
      });
    });
  }

  async stop() {
    // Stop cache cleanup
    if (this.config.cacheEnabled) {
      const cache = require('./cache').getCache();
      await cache.stop();
    }

    // Close connections
    if (this.redis) {
      await this.redis.quit();
    }

    await this.db.close();
    
    return new Promise((resolve) => {
      this.server.close(resolve);
    });
  }
}

// Export for use
module.exports = Server;

// Start server if run directly
if (require.main === module) {
  const server = new Server();
  
  server.start().catch(error => {
    console.error('Failed to start server:', error);
    process.exit(1);
  });

  // Graceful shutdown
  process.on('SIGTERM', async () => {
    console.log('SIGTERM received, shutting down gracefully...');
    await server.stop();
    process.exit(0);
  });

  process.on('SIGINT', async () => {
    console.log('SIGINT received, shutting down gracefully...');
    await server.stop();
    process.exit(0);
  });
}