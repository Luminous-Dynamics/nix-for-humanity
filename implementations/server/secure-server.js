/**
 * Secure Server Implementation for Nix for Humanity
 * Integrates all security improvements and best practices
 */

const express = require('express');
const https = require('https');
const fs = require('fs');
const path = require('path');
const WebSocket = require('ws');
const session = require('express-session');
const SessionStore = require('connect-sqlite3')(session);

// Security services
const AuthenticationService = require('../security/auth-service');
const { ValidationService, ValidationError } = require('../security/validation-service');
const ErrorHandler = require('../security/error-handler');
const SecurityMiddleware = require('../security/security-middleware');
const HealthMonitor = require('../monitoring/health-monitor');

// NLP and command services
const NLPService = require('../nlp/nlp-service');
const EnhancedCommandExecutor = require('../core/enhanced-command-executor');

class SecureNixForHumanityServer {
  constructor(options = {}) {
    this.port = options.port || process.env.PORT || 3456;
    this.wsPort = options.wsPort || process.env.WS_PORT || 3457;
    this.isDevelopment = process.env.NODE_ENV === 'development';
    
    // Initialize services
    this.auth = new AuthenticationService();
    this.validation = new ValidationService();
    this.errorHandler = new ErrorHandler();
    this.security = new SecurityMiddleware();
    this.health = new HealthMonitor();
    this.nlp = new NLPService();
    this.executor = new EnhancedCommandExecutor();
    
    // Set up progress monitoring
    this.setupProgressMonitoring();
    
    // Initialize Express app
    this.app = express();
    this.setupMiddleware();
    this.setupRoutes();
    
    // Setup WebSocket server
    this.setupWebSocket();
  }

  setupMiddleware() {
    // Body parsing
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));
    
    // Session management
    this.app.use(session({
      store: new SessionStore({
        db: path.join(process.env.HOME, '.config/nix-for-humanity/sessions.db')
      }),
      secret: process.env.SESSION_SECRET || 'change-this-in-production',
      resave: false,
      saveUninitialized: false,
      cookie: {
        secure: !this.isDevelopment, // HTTPS only in production
        httpOnly: true,
        maxAge: 24 * 60 * 60 * 1000, // 24 hours
        sameSite: 'strict'
      }
    }));
    
    // Apply security middleware
    this.security.apply(this.app);
    
    // Request logging
    this.app.use((req, res, next) => {
      const start = Date.now();
      res.on('finish', () => {
        const duration = Date.now() - start;
        console.log(`${req.method} ${req.path} ${res.statusCode} ${duration}ms`);
      });
      next();
    });
  }

  setupRoutes() {
    // Health check routes
    const healthRoutes = this.health.getRoutes();
    this.app.get('/health', healthRoutes.health);
    this.app.get('/health/:check', healthRoutes.checkSpecific);
    this.app.get('/metrics', healthRoutes.metrics);
    this.app.get('/ready', healthRoutes.ready);
    this.app.get('/live', healthRoutes.live);
    
    // Authentication routes
    this.app.post('/api/auth/register', this.handleRegister.bind(this));
    this.app.post('/api/auth/login', this.handleLogin.bind(this));
    this.app.post('/api/auth/logout', this.handleLogout.bind(this));
    this.app.get('/api/auth/verify', this.requireAuth.bind(this), this.handleVerify.bind(this));
    this.app.post('/api/auth/refresh', this.handleRefresh.bind(this));
    
    // NLP routes (protected)
    this.app.post('/api/nlp/process', this.requireAuth.bind(this), this.handleNLPProcess.bind(this));
    this.app.post('/api/nlp/voice', this.requireAuth.bind(this), this.handleVoiceInput.bind(this));
    
    // Package operations (protected)
    this.app.post('/api/packages/search', this.requireAuth.bind(this), this.handlePackageSearch.bind(this));
    this.app.post('/api/packages/install', this.requireAuth.bind(this), this.handlePackageInstall.bind(this));
    this.app.post('/api/packages/remove', this.requireAuth.bind(this), this.handlePackageRemove.bind(this));
    this.app.get('/api/packages/list', this.requireAuth.bind(this), this.handlePackageList.bind(this));
    
    // Service operations (protected)
    this.app.post('/api/services/:operation', this.requireAuth.bind(this), this.handleServiceOperation.bind(this));
    
    // System information (protected)
    this.app.get('/api/system/info', this.requireAuth.bind(this), this.handleSystemInfo.bind(this));
    this.app.get('/api/system/logs', this.requireAuth.bind(this), this.handleSystemLogs.bind(this));
    
    // Error handling
    this.app.use(this.handleErrors.bind(this));
  }

  // Authentication handlers
  async handleRegister(req, res, next) {
    try {
      const validated = this.validation.validate(req.body, 'registerRequest');
      
      const user = await this.auth.registerUser(
        validated.username,
        validated.password,
        { email: validated.email }
      );
      
      res.status(201).json({
        success: true,
        message: 'User registered successfully',
        user: {
          username: user.username,
          role: user.role
        }
      });
    } catch (error) {
      next(error);
    }
  }

  async handleLogin(req, res, next) {
    try {
      const validated = this.validation.validate(req.body, 'loginRequest');
      
      const user = await this.auth.validateUser(
        validated.username,
        validated.password
      );
      
      if (!user) {
        return res.status(401).json({
          success: false,
          message: 'Invalid credentials'
        });
      }
      
      const tokens = this.auth.generateTokens(user);
      
      // Set session
      req.session.user = user;
      req.session.csrfToken = require('crypto').randomBytes(32).toString('hex');
      
      res.json({
        success: true,
        message: 'Login successful',
        user: {
          username: user.username,
          role: user.role
        },
        tokens,
        csrfToken: req.session.csrfToken
      });
    } catch (error) {
      next(error);
    }
  }

  async handleLogout(req, res) {
    req.session.destroy((err) => {
      if (err) {
        console.error('Session destruction error:', err);
      }
      res.json({
        success: true,
        message: 'Logged out successfully'
      });
    });
  }

  async handleVerify(req, res) {
    res.json({
      success: true,
      user: req.user
    });
  }

  async handleRefresh(req, res, next) {
    try {
      const { refreshToken } = req.body;
      
      if (!refreshToken) {
        return res.status(401).json({
          success: false,
          message: 'Refresh token required'
        });
      }
      
      const decoded = this.auth.verifyRefreshToken(refreshToken);
      const tokens = this.auth.generateTokens(decoded);
      
      res.json({
        success: true,
        tokens
      });
    } catch (error) {
      next(error);
    }
  }

  // NLP handlers
  async handleNLPProcess(req, res, next) {
    try {
      const validated = this.validation.validate(req.body, 'nlpInput');
      
      // Process through NLP
      const intent = await this.nlp.processInput(validated.text, validated.context);
      
      // Validate the command
      const command = this.validation.sanitizeCommand(intent.command, intent.args);
      
      // Execute command
      const result = await this.executor.execute(command, {
        user: req.user,
        dryRun: req.query.dryRun === 'true'
      });
      
      res.json({
        success: true,
        intent,
        command,
        result
      });
    } catch (error) {
      next(error);
    }
  }

  async handleVoiceInput(req, res, next) {
    try {
      const validated = this.validation.validate(req.body, 'voiceInput');
      
      // Process voice to text
      const text = await this.nlp.processVoice(validated.audio, {
        format: validated.format,
        sampleRate: validated.sampleRate
      });
      
      // Process as text
      req.body = { text, context: req.body.context };
      await this.handleNLPProcess(req, res, next);
    } catch (error) {
      next(error);
    }
  }

  // Package operation handlers
  async handlePackageSearch(req, res, next) {
    try {
      const { query } = req.body;
      const sanitizedQuery = this.validation.validatePackageName(query);
      
      const results = await this.executor.searchPackages(sanitizedQuery);
      
      res.json({
        success: true,
        query: sanitizedQuery,
        results
      });
    } catch (error) {
      next(error);
    }
  }

  async handlePackageInstall(req, res, next) {
    try {
      const validated = this.validation.validate(req.body, 'packageOperation');
      
      const result = await this.executor.installPackage(
        validated.package,
        validated.options
      );
      
      res.json({
        success: true,
        package: validated.package,
        result
      });
    } catch (error) {
      next(error);
    }
  }

  async handlePackageRemove(req, res, next) {
    try {
      const validated = this.validation.validate(req.body, 'packageOperation');
      
      const result = await this.executor.removePackage(
        validated.package,
        validated.options
      );
      
      res.json({
        success: true,
        package: validated.package,
        result
      });
    } catch (error) {
      next(error);
    }
  }

  async handlePackageList(req, res, next) {
    try {
      const packages = await this.executor.listPackages();
      
      res.json({
        success: true,
        packages
      });
    } catch (error) {
      next(error);
    }
  }

  // Service operation handler
  async handleServiceOperation(req, res, next) {
    try {
      const validated = this.validation.validate({
        operation: req.params.operation,
        service: req.body.service
      }, 'serviceOperation');
      
      const result = await this.executor.serviceOperation(
        validated.service,
        validated.operation
      );
      
      res.json({
        success: true,
        service: validated.service,
        operation: validated.operation,
        result
      });
    } catch (error) {
      next(error);
    }
  }

  // System information handlers
  async handleSystemInfo(req, res, next) {
    try {
      const info = await this.executor.getSystemInfo();
      
      res.json({
        success: true,
        system: info
      });
    } catch (error) {
      next(error);
    }
  }

  async handleSystemLogs(req, res, next) {
    try {
      const validated = this.validation.validate(req.query, 'systemQuery');
      
      const logs = await this.executor.getSystemLogs({
        service: validated.filter,
        lines: parseInt(req.query.lines) || 100
      });
      
      res.json({
        success: true,
        logs: this.validation.sanitizeOutput(logs)
      });
    } catch (error) {
      next(error);
    }
  }

  // Authentication middleware
  async requireAuth(req, res, next) {
    const token = req.headers.authorization?.replace('Bearer ', '');
    
    if (!token) {
      return res.status(401).json({
        success: false,
        message: 'Authentication required'
      });
    }
    
    try {
      const decoded = this.auth.verifyToken(token);
      req.user = decoded;
      next();
    } catch (error) {
      return res.status(401).json({
        success: false,
        message: 'Invalid or expired token'
      });
    }
  }

  // Error handling middleware
  handleErrors(error, req, res, next) {
    // Handle validation errors
    if (error instanceof ValidationError) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: error.errors
      });
    }
    
    // Handle other errors
    const userError = this.errorHandler.handle(error, {
      operation: req.method,
      target: req.path,
      originalCommand: req.body?.text
    });
    
    // Log the error
    console.error('Request error:', {
      id: req.id,
      method: req.method,
      path: req.path,
      error: error.stack
    });
    
    // Send user-friendly response
    const statusCode = error.statusCode || 500;
    res.status(statusCode).json({
      success: false,
      ...userError,
      requestId: req.id
    });
  }

  // WebSocket setup
  setupWebSocket() {
    this.wss = new WebSocket.Server({ port: this.wsPort });
    
    this.wss.on('connection', (ws, req) => {
      console.log('WebSocket connection established');
      
      // Apply WebSocket security
      this.security.applyWebSocketSecurity(ws, req);
      
      // Handle authentication
      ws.on('message', async (data) => {
        try {
          const message = JSON.parse(data);
          
          if (message.type === 'auth') {
            const decoded = this.auth.verifyToken(message.token);
            ws.userId = decoded.username;
            ws.authenticated = true;
            ws.send(JSON.stringify({ type: 'auth', success: true }));
          } else if (!ws.authenticated) {
            ws.send(JSON.stringify({ 
              type: 'error', 
              message: 'Authentication required' 
            }));
          } else {
            // Handle other message types
            await this.handleWebSocketMessage(ws, message);
          }
        } catch (error) {
          ws.send(JSON.stringify({
            type: 'error',
            message: this.errorHandler.handle(error).message
          }));
        }
      });
      
      ws.on('close', () => {
        console.log('WebSocket connection closed');
      });
    });
  }

  async handleWebSocketMessage(ws, message) {
    switch (message.type) {
      case 'nlp':
        const intent = await this.nlp.processInput(message.text);
        ws.send(JSON.stringify({ type: 'intent', data: intent }));
        break;
        
      case 'voice-stream':
        // Handle streaming voice data
        await this.nlp.processVoiceStream(message.data, (text) => {
          ws.send(JSON.stringify({ type: 'transcript', text }));
        });
        break;
        
      case 'command-status':
        // Send command execution status
        const status = this.executor.getExecutionStatus(message.executionId);
        ws.send(JSON.stringify({ type: 'status', data: status }));
        break;
        
      case 'cancel-command':
        // Cancel a running command
        const cancelled = await this.executor.cancelExecution(message.executionId);
        ws.send(JSON.stringify({ 
          type: 'cancel-result', 
          success: cancelled,
          executionId: message.executionId 
        }));
        break;
        
      default:
        ws.send(JSON.stringify({ 
          type: 'error', 
          message: 'Unknown message type' 
        }));
    }
  }

  // Set up progress monitoring
  setupProgressMonitoring() {
    // Listen for execution events
    this.executor.on('executionStart', (event) => {
      this.broadcastToWebSockets({
        type: 'executionStart',
        data: event
      });
    });
    
    this.executor.on('progress', (event) => {
      this.broadcastToWebSockets({
        type: 'progress',
        data: event
      });
    });
    
    this.executor.on('executionComplete', (event) => {
      this.broadcastToWebSockets({
        type: 'executionComplete',
        data: event
      });
    });
    
    this.executor.on('executionError', (event) => {
      this.broadcastToWebSockets({
        type: 'executionError',
        data: event
      });
    });
  }

  // Broadcast to all authenticated WebSocket clients
  broadcastToWebSockets(message) {
    if (!this.wss) return;
    
    this.wss.clients.forEach((client) => {
      if (client.readyState === 1 && client.authenticated) {
        client.send(JSON.stringify(message));
      }
    });
  }

  // Start the server
  async start() {
    // Initialize services
    await this.auth.ensureInitialized();
    
    // Create default admin user if none exists
    const users = await this.auth.listUsers();
    if (users.length === 0) {
      console.log('Creating default admin user...');
      await this.auth.registerUser('admin', 'changeMe123!', { role: 'admin' });
      console.log('Default admin user created. Please change the password!');
    }
    
    // Start HTTPS server
    if (!this.isDevelopment) {
      const httpsOptions = {
        key: fs.readFileSync(path.join(__dirname, '../../ssl/key.pem')),
        cert: fs.readFileSync(path.join(__dirname, '../../ssl/cert.pem'))
      };
      
      https.createServer(httpsOptions, this.app).listen(this.port, () => {
        console.log(`🔒 Secure server running on https://localhost:${this.port}`);
      });
    } else {
      // HTTP in development only
      this.app.listen(this.port, () => {
        console.log(`🚀 Development server running on http://localhost:${this.port}`);
      });
    }
    
    console.log(`🌐 WebSocket server running on ws://localhost:${this.wsPort}`);
    console.log(`📊 Health check available at /health`);
    console.log(`🔐 Security: ${this.isDevelopment ? 'Development mode' : 'Production mode'}`);
  }

  // Graceful shutdown
  async shutdown() {
    console.log('Shutting down server...');
    
    // Stop health checks
    this.health.stopPeriodicChecks();
    
    // Close WebSocket server
    this.wss.close();
    
    // Close Express server
    if (this.server) {
      this.server.close();
    }
    
    console.log('Server shut down successfully');
  }
}

// Create and start server
if (require.main === module) {
  const server = new SecureNixForHumanityServer();
  
  // Handle shutdown signals
  process.on('SIGTERM', () => server.shutdown());
  process.on('SIGINT', () => server.shutdown());
  
  // Start server
  server.start().catch(error => {
    console.error('Failed to start server:', error);
    process.exit(1);
  });
}

module.exports = SecureNixForHumanityServer;