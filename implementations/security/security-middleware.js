/**
 * Security Middleware for Nix for Humanity
 * Implements comprehensive security headers, CORS, and rate limiting
 */

const helmet = require('helmet');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const { v4: uuidv4 } = require('uuid');

class SecurityMiddleware {
  constructor(options = {}) {
    this.isDevelopment = process.env.NODE_ENV === 'development';
    this.allowedOrigins = options.allowedOrigins || this.getDefaultOrigins();
    this.trustedProxies = options.trustedProxies || ['loopback'];
  }

  getDefaultOrigins() {
    const origins = [
      'http://localhost:3456',
      'http://localhost:3457',
      'http://localhost:3458',
      'http://localhost:8080',
      'http://localhost:8081'
    ];

    // Add production origins if configured
    if (process.env.ALLOWED_ORIGINS) {
      origins.push(...process.env.ALLOWED_ORIGINS.split(','));
    }

    // Add Tauri app origin
    origins.push('tauri://localhost');
    origins.push('https://tauri.localhost');

    return origins;
  }

  // Configure Helmet for security headers
  getHelmetConfig() {
    return helmet({
      contentSecurityPolicy: {
        directives: {
          defaultSrc: ["'self'"],
          scriptSrc: [
            "'self'",
            "'unsafe-inline'", // Needed for some UI frameworks
            "'unsafe-eval'" // Only in development
          ].filter(src => this.isDevelopment || src !== "'unsafe-eval'"),
          styleSrc: ["'self'", "'unsafe-inline'"],
          imgSrc: ["'self'", "data:", "https:"],
          connectSrc: [
            "'self'",
            "ws://localhost:*",
            "wss://localhost:*",
            ...this.allowedOrigins
          ],
          fontSrc: ["'self'"],
          objectSrc: ["'none'"],
          mediaSrc: ["'self'"],
          frameSrc: ["'none'"],
          workerSrc: ["'self'", "blob:"],
          childSrc: ["'self'", "blob:"],
          formAction: ["'self'"],
          frameAncestors: ["'none'"],
          baseUri: ["'self'"],
          manifestSrc: ["'self'"]
        }
      },
      hsts: {
        maxAge: 31536000,
        includeSubDomains: true,
        preload: true
      },
      noSniff: true,
      xssFilter: true,
      referrerPolicy: { policy: 'same-origin' },
      permittedCrossDomainPolicies: false
    });
  }

  // Configure CORS
  getCorsConfig() {
    return cors({
      origin: (origin, callback) => {
        // Allow requests with no origin (like mobile apps or Postman)
        if (!origin) return callback(null, true);

        if (this.allowedOrigins.indexOf(origin) !== -1) {
          callback(null, true);
        } else {
          callback(new Error(`Origin ${origin} not allowed by CORS`));
        }
      },
      credentials: true,
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
      allowedHeaders: [
        'Content-Type',
        'Authorization',
        'X-Request-ID',
        'X-Session-ID'
      ],
      exposedHeaders: [
        'X-Request-ID',
        'X-RateLimit-Limit',
        'X-RateLimit-Remaining',
        'X-RateLimit-Reset'
      ],
      maxAge: 86400, // 24 hours
      optionsSuccessStatus: 200
    });
  }

  // Create rate limiters for different operations
  getRateLimiters() {
    // General API rate limit
    const apiLimiter = rateLimit({
      windowMs: 1 * 60 * 1000, // 1 minute
      max: 60, // 60 requests per minute
      message: {
        error: 'Too many requests',
        message: 'Please slow down. You can make up to 60 requests per minute.',
        retryAfter: 60
      },
      standardHeaders: true,
      legacyHeaders: false,
      keyGenerator: (req) => {
        // Use IP + user ID if authenticated
        const userId = req.user?.id || 'anonymous';
        return `${req.ip}:${userId}`;
      }
    });

    // Strict rate limit for authentication
    const authLimiter = rateLimit({
      windowMs: 15 * 60 * 1000, // 15 minutes
      max: 5, // 5 attempts per 15 minutes
      message: {
        error: 'Too many authentication attempts',
        message: 'Please wait 15 minutes before trying again.',
        retryAfter: 900
      },
      skipSuccessfulRequests: true, // Don't count successful logins
      standardHeaders: true,
      legacyHeaders: false
    });

    // Moderate rate limit for package operations
    const packageLimiter = rateLimit({
      windowMs: 5 * 60 * 1000, // 5 minutes
      max: 10, // 10 operations per 5 minutes
      message: {
        error: 'Too many package operations',
        message: 'Please wait before performing more package operations.',
        retryAfter: 300
      },
      standardHeaders: true,
      legacyHeaders: false
    });

    // Loose rate limit for queries
    const queryLimiter = rateLimit({
      windowMs: 1 * 60 * 1000, // 1 minute
      max: 100, // 100 queries per minute
      message: {
        error: 'Too many queries',
        message: 'Please reduce your query rate.',
        retryAfter: 60
      },
      standardHeaders: true,
      legacyHeaders: false
    });

    return {
      api: apiLimiter,
      auth: authLimiter,
      package: packageLimiter,
      query: queryLimiter
    };
  }

  // Add security headers
  securityHeaders() {
    return (req, res, next) => {
      // Add request ID for tracing
      req.id = req.headers['x-request-id'] || uuidv4();
      res.setHeader('X-Request-ID', req.id);

      // Add custom security headers
      res.setHeader('X-Content-Type-Options', 'nosniff');
      res.setHeader('X-Frame-Options', 'DENY');
      res.setHeader('X-XSS-Protection', '1; mode=block');
      res.setHeader('Permissions-Policy', 'geolocation=(), microphone=(), camera=()');
      
      // Remove sensitive headers
      res.removeHeader('X-Powered-By');
      res.removeHeader('Server');

      // Add timing headers for monitoring
      res.setHeader('X-Response-Time', Date.now());

      // Log security events
      if (req.method !== 'GET' && req.method !== 'OPTIONS') {
        console.log(`Security: ${req.method} ${req.path} from ${req.ip} (${req.id})`);
      }

      next();
    };
  }

  // Request sanitization
  sanitizeRequest() {
    return (req, res, next) => {
      // Limit request size
      if (req.headers['content-length'] > 10 * 1024 * 1024) { // 10MB
        return res.status(413).json({
          error: 'Request too large',
          message: 'Request body cannot exceed 10MB'
        });
      }

      // Sanitize common injection points
      ['query', 'params', 'body'].forEach(key => {
        if (req[key]) {
          req[key] = this.sanitizeObject(req[key]);
        }
      });

      next();
    };
  }

  // Recursively sanitize object
  sanitizeObject(obj) {
    if (typeof obj === 'string') {
      // Remove null bytes
      return obj.replace(/\0/g, '');
    } else if (Array.isArray(obj)) {
      return obj.map(item => this.sanitizeObject(item));
    } else if (obj && typeof obj === 'object') {
      const sanitized = {};
      for (const [key, value] of Object.entries(obj)) {
        // Skip prototype pollution keys
        if (key === '__proto__' || key === 'constructor' || key === 'prototype') {
          continue;
        }
        sanitized[key] = this.sanitizeObject(value);
      }
      return sanitized;
    }
    return obj;
  }

  // CSRF protection (for session-based auth)
  csrfProtection() {
    return (req, res, next) => {
      // Skip CSRF for API tokens
      if (req.headers.authorization?.startsWith('Bearer ')) {
        return next();
      }

      // Skip for safe methods
      if (['GET', 'HEAD', 'OPTIONS'].includes(req.method)) {
        return next();
      }

      // Check CSRF token
      const token = req.headers['x-csrf-token'] || req.body._csrf;
      const sessionToken = req.session?.csrfToken;

      if (!token || token !== sessionToken) {
        return res.status(403).json({
          error: 'CSRF validation failed',
          message: 'Invalid or missing CSRF token'
        });
      }

      next();
    };
  }

  // Trust proxy configuration
  configureTrustProxy(app) {
    if (this.trustedProxies === 'loopback') {
      app.set('trust proxy', 'loopback');
    } else if (Array.isArray(this.trustedProxies)) {
      app.set('trust proxy', this.trustedProxies);
    } else if (typeof this.trustedProxies === 'number') {
      app.set('trust proxy', this.trustedProxies);
    }
  }

  // Apply all security middleware
  apply(app) {
    // Configure proxy trust
    this.configureTrustProxy(app);

    // Apply security headers
    app.use(this.getHelmetConfig());
    app.use(this.securityHeaders());

    // Apply CORS
    app.use(this.getCorsConfig());

    // Apply request sanitization
    app.use(this.sanitizeRequest());

    // Get rate limiters
    const limiters = this.getRateLimiters();

    // Apply rate limiting to specific routes
    app.use('/api/auth/login', limiters.auth);
    app.use('/api/auth/register', limiters.auth);
    app.use('/api/packages/install', limiters.package);
    app.use('/api/packages/remove', limiters.package);
    app.use('/api/search', limiters.query);
    app.use('/api/', limiters.api);

    // Log security initialization
    console.log('Security middleware initialized with:');
    console.log(`- Allowed origins: ${this.allowedOrigins.join(', ')}`);
    console.log(`- Environment: ${this.isDevelopment ? 'development' : 'production'}`);
    console.log('- Rate limiting: enabled');
    console.log('- CORS: configured');
    console.log('- Security headers: applied');
  }

  // WebSocket security
  applyWebSocketSecurity(ws, req) {
    // Add security context to WebSocket
    ws.securityContext = {
      id: uuidv4(),
      ip: req.socket.remoteAddress,
      origin: req.headers.origin,
      userAgent: req.headers['user-agent']
    };

    // Rate limit WebSocket messages
    ws.messageCount = 0;
    ws.messageWindow = Date.now();

    ws.on('message', (data) => {
      // Reset window every minute
      if (Date.now() - ws.messageWindow > 60000) {
        ws.messageCount = 0;
        ws.messageWindow = Date.now();
      }

      // Rate limit: 60 messages per minute
      ws.messageCount++;
      if (ws.messageCount > 60) {
        ws.send(JSON.stringify({
          error: 'Rate limit exceeded',
          message: 'Please slow down your requests'
        }));
        ws.close(1008, 'Rate limit exceeded');
      }
    });
  }
}

module.exports = SecurityMiddleware;