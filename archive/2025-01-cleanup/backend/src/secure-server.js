const express = require('express');
const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');
const compression = require('compression');
const helmet = require('helmet');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const { Server } = require('socket.io');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

// Import existing modules
const CachedPackageService = require('./services/package-service-cached');
const ConfigService = require('./services/config-service');
const ServiceManager = require('./services/service-manager');

class SecureNixOSServer {
    constructor(config = {}) {
        this.config = {
            httpPort: process.env.HTTP_PORT || 8080,
            httpsPort: process.env.HTTPS_PORT || 8443,
            wsPort: process.env.WS_PORT || 8091,
            host: process.env.HOST || 'localhost',
            jwtSecret: process.env.JWT_SECRET || this.generateSecret(),
            sessionSecret: process.env.SESSION_SECRET || this.generateSecret(),
            sslCert: process.env.SSL_CERT || path.join(__dirname, '../../ssl/cert.pem'),
            sslKey: process.env.SSL_KEY || path.join(__dirname, '../../ssl/key.pem'),
            ...config
        };

        this.app = express();
        this.setupMiddleware();
        this.setupRoutes();
    }

    generateSecret() {
        return require('crypto').randomBytes(64).toString('hex');
    }

    setupMiddleware() {
        // Security headers with Helmet
        this.app.use(helmet({
            contentSecurityPolicy: {
                directives: {
                    defaultSrc: ["'self'"],
                    scriptSrc: ["'self'", "'unsafe-inline'"],
                    styleSrc: ["'self'", "'unsafe-inline'"],
                    imgSrc: ["'self'", "data:", "https:"],
                    connectSrc: ["'self'", "ws://localhost:*", "wss://localhost:*"],
                    fontSrc: ["'self'"],
                    objectSrc: ["'none'"],
                    mediaSrc: ["'self'"],
                    frameSrc: ["'none'"],
                },
            },
            hsts: {
                maxAge: 31536000,
                includeSubDomains: true,
                preload: true
            }
        }));

        // Compression
        this.app.use(compression());

        // CORS configuration
        const corsOptions = {
            origin: (origin, callback) => {
                const allowedOrigins = [
                    `https://localhost:${this.config.httpsPort}`,
                    `http://localhost:${this.config.httpPort}`,
                    'https://localhost:3000', // Development
                ];
                
                if (!origin || allowedOrigins.indexOf(origin) !== -1) {
                    callback(null, true);
                } else {
                    callback(new Error('Not allowed by CORS'));
                }
            },
            credentials: true,
            optionsSuccessStatus: 200
        };
        this.app.use(cors(corsOptions));

        // Body parsing
        this.app.use(express.json({ limit: '10mb' }));
        this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));

        // Rate limiting
        const limiter = rateLimit({
            windowMs: 15 * 60 * 1000, // 15 minutes
            max: 100, // Limit each IP to 100 requests per windowMs
            message: 'Too many requests, please try again later.',
            standardHeaders: true,
            legacyHeaders: false,
        });
        this.app.use('/api/', limiter);

        // Stricter rate limit for auth endpoints
        const authLimiter = rateLimit({
            windowMs: 15 * 60 * 1000,
            max: 5,
            skipSuccessfulRequests: true,
        });
        this.app.use('/api/auth/', authLimiter);

        // Request logging
        this.app.use((req, res, next) => {
            console.log(`${new Date().toISOString()} ${req.method} ${req.url}`);
            next();
        });

        // Static files
        this.app.use(express.static(path.join(__dirname, '../../frontend')));
    }

    setupRoutes() {
        // Health check endpoint
        this.app.get('/api/health', (req, res) => {
            res.json({
                status: 'healthy',
                timestamp: new Date().toISOString(),
                uptime: process.uptime()
            });
        });

        // Authentication routes
        this.app.post('/api/auth/login', this.handleLogin.bind(this));
        this.app.post('/api/auth/logout', this.authenticate.bind(this), this.handleLogout.bind(this));
        this.app.get('/api/auth/verify', this.authenticate.bind(this), (req, res) => {
            res.json({ valid: true, user: req.user });
        });

        // Package management routes (protected)
        this.app.post('/api/packages/search', this.authenticate.bind(this), this.handlePackageSearch.bind(this));
        this.app.get('/api/packages/installed', this.authenticate.bind(this), this.handleInstalledPackages.bind(this));
        this.app.post('/api/packages/install', this.authenticate.bind(this), this.requireAdmin.bind(this), this.handlePackageInstall.bind(this));
        this.app.post('/api/packages/remove', this.authenticate.bind(this), this.requireAdmin.bind(this), this.handlePackageRemove.bind(this));

        // Configuration routes (protected)
        this.app.get('/api/configuration', this.authenticate.bind(this), this.handleGetConfiguration.bind(this));
        this.app.post('/api/configuration', this.authenticate.bind(this), this.requireAdmin.bind(this), this.handleSaveConfiguration.bind(this));
        this.app.post('/api/configuration/validate', this.authenticate.bind(this), this.handleValidateConfiguration.bind(this));

        // Service management routes (protected)
        this.app.get('/api/services', this.authenticate.bind(this), this.handleGetServices.bind(this));
        this.app.post('/api/services/:name/start', this.authenticate.bind(this), this.requireAdmin.bind(this), this.handleStartService.bind(this));
        this.app.post('/api/services/:name/stop', this.authenticate.bind(this), this.requireAdmin.bind(this), this.handleStopService.bind(this));
        this.app.post('/api/services/:name/restart', this.authenticate.bind(this), this.requireAdmin.bind(this), this.handleRestartService.bind(this));

        // System stats (authenticated)
        this.app.get('/api/system/stats', this.authenticate.bind(this), this.handleSystemStats.bind(this));

        // Error handling
        this.app.use(this.errorHandler.bind(this));
    }

    // Authentication middleware
    authenticate(req, res, next) {
        const token = req.headers.authorization?.replace('Bearer ', '');
        
        if (!token) {
            return res.status(401).json({ error: 'No token provided' });
        }

        try {
            const decoded = jwt.verify(token, this.config.jwtSecret);
            req.user = decoded;
            next();
        } catch (error) {
            return res.status(403).json({ error: 'Invalid token' });
        }
    }

    requireAdmin(req, res, next) {
        if (req.user.role !== 'admin') {
            return res.status(403).json({ error: 'Admin access required' });
        }
        next();
    }

    // Route handlers
    async handleLogin(req, res) {
        const { username, password } = req.body;
        
        // Input validation
        if (!username || !password) {
            return res.status(400).json({ error: 'Username and password required' });
        }

        // In production, check against real user database
        // For now, using a demo user
        const demoUser = {
            username: 'admin',
            // Password: 'nixos-sacred' (hashed)
            passwordHash: '$2b$10$YourHashedPasswordHere',
            role: 'admin'
        };

        if (username !== demoUser.username) {
            return res.status(401).json({ error: 'Invalid credentials' });
        }

        // For demo purposes, accept any password
        // In production, use: const valid = await bcrypt.compare(password, user.passwordHash);
        const valid = true;

        if (!valid) {
            return res.status(401).json({ error: 'Invalid credentials' });
        }

        const token = jwt.sign(
            { 
                username: demoUser.username, 
                role: demoUser.role,
                iat: Date.now()
            },
            this.config.jwtSecret,
            { expiresIn: '24h' }
        );

        res.json({
            token,
            user: {
                username: demoUser.username,
                role: demoUser.role
            }
        });
    }

    handleLogout(req, res) {
        // In production, invalidate token in database
        res.json({ message: 'Logged out successfully' });
    }

    async handlePackageSearch(req, res) {
        try {
            const { query } = req.body;
            
            // Input validation
            if (!query || typeof query !== 'string' || query.length < 2) {
                return res.status(400).json({ error: 'Invalid search query' });
            }

            // Sanitize query
            const sanitizedQuery = query.replace(/[^a-zA-Z0-9\-_.]/g, '');
            
            const packageService = new CachedPackageService();
            const results = await packageService.search(sanitizedQuery);
            
            res.json(results);
        } catch (error) {
            console.error('Package search error:', error);
            res.status(500).json({ error: 'Search failed' });
        }
    }

    async handleInstalledPackages(req, res) {
        try {
            const packageService = new CachedPackageService();
            const packages = await packageService.listInstalled();
            res.json(packages);
        } catch (error) {
            console.error('List installed packages error:', error);
            res.status(500).json({ error: 'Failed to list packages' });
        }
    }

    async handlePackageInstall(req, res) {
        try {
            const { package: packageName } = req.body;
            
            // Validate package name
            if (!packageName || !/^[a-zA-Z0-9\-_.]+$/.test(packageName)) {
                return res.status(400).json({ error: 'Invalid package name' });
            }

            const packageService = new CachedPackageService();
            const result = await packageService.install(packageName);
            
            res.json(result);
        } catch (error) {
            console.error('Package install error:', error);
            res.status(500).json({ error: 'Installation failed' });
        }
    }

    async handlePackageRemove(req, res) {
        try {
            const { package: packageName } = req.body;
            
            // Validate package name
            if (!packageName || !/^[a-zA-Z0-9\-_.]+$/.test(packageName)) {
                return res.status(400).json({ error: 'Invalid package name' });
            }

            const packageService = new CachedPackageService();
            const result = await packageService.remove(packageName);
            
            res.json(result);
        } catch (error) {
            console.error('Package remove error:', error);
            res.status(500).json({ error: 'Removal failed' });
        }
    }

    async handleGetConfiguration(req, res) {
        try {
            const configService = new ConfigService();
            const config = await configService.getConfiguration();
            res.json({ content: config });
        } catch (error) {
            console.error('Get configuration error:', error);
            res.status(500).json({ error: 'Failed to load configuration' });
        }
    }

    async handleSaveConfiguration(req, res) {
        try {
            const { content } = req.body;
            
            if (!content || typeof content !== 'string') {
                return res.status(400).json({ error: 'Invalid configuration content' });
            }

            const configService = new ConfigService();
            
            // Validate before saving
            const validation = await configService.validate(content);
            if (!validation.valid) {
                return res.status(400).json({ 
                    error: 'Invalid configuration', 
                    details: validation.errors 
                });
            }

            const result = await configService.save(content);
            res.json(result);
        } catch (error) {
            console.error('Save configuration error:', error);
            res.status(500).json({ error: 'Failed to save configuration' });
        }
    }

    async handleValidateConfiguration(req, res) {
        try {
            const { content } = req.body;
            
            if (!content || typeof content !== 'string') {
                return res.status(400).json({ error: 'Invalid configuration content' });
            }

            const configService = new ConfigService();
            const validation = await configService.validate(content);
            
            res.json(validation);
        } catch (error) {
            console.error('Validate configuration error:', error);
            res.status(500).json({ error: 'Validation failed' });
        }
    }

    async handleGetServices(req, res) {
        try {
            const serviceManager = new ServiceManager();
            const services = await serviceManager.listServices();
            res.json(services);
        } catch (error) {
            console.error('Get services error:', error);
            res.status(500).json({ error: 'Failed to list services' });
        }
    }

    async handleStartService(req, res) {
        try {
            const { name } = req.params;
            
            // Validate service name
            if (!name || !/^[a-zA-Z0-9\-_.]+$/.test(name)) {
                return res.status(400).json({ error: 'Invalid service name' });
            }

            const serviceManager = new ServiceManager();
            const result = await serviceManager.startService(name);
            
            res.json(result);
        } catch (error) {
            console.error('Start service error:', error);
            res.status(500).json({ error: 'Failed to start service' });
        }
    }

    async handleStopService(req, res) {
        try {
            const { name } = req.params;
            
            // Validate service name
            if (!name || !/^[a-zA-Z0-9\-_.]+$/.test(name)) {
                return res.status(400).json({ error: 'Invalid service name' });
            }

            const serviceManager = new ServiceManager();
            const result = await serviceManager.stopService(name);
            
            res.json(result);
        } catch (error) {
            console.error('Stop service error:', error);
            res.status(500).json({ error: 'Failed to stop service' });
        }
    }

    async handleRestartService(req, res) {
        try {
            const { name } = req.params;
            
            // Validate service name
            if (!name || !/^[a-zA-Z0-9\-_.]+$/.test(name)) {
                return res.status(400).json({ error: 'Invalid service name' });
            }

            const serviceManager = new ServiceManager();
            const result = await serviceManager.restartService(name);
            
            res.json(result);
        } catch (error) {
            console.error('Restart service error:', error);
            res.status(500).json({ error: 'Failed to restart service' });
        }
    }

    async handleSystemStats(req, res) {
        try {
            const stats = await this.getSystemStats();
            res.json(stats);
        } catch (error) {
            console.error('Get system stats error:', error);
            res.status(500).json({ error: 'Failed to get system stats' });
        }
    }

    async getSystemStats() {
        const os = require('os');
        
        return {
            cpu: {
                usage: os.loadavg()[0] * 10, // Rough approximation
                cores: os.cpus().length
            },
            memory: {
                total: os.totalmem(),
                used: os.totalmem() - os.freemem(),
                free: os.freemem()
            },
            disk: {
                // Would need proper disk stats implementation
                total: 100 * 1024 * 1024 * 1024, // 100GB dummy
                used: 50 * 1024 * 1024 * 1024,   // 50GB dummy
                free: 50 * 1024 * 1024 * 1024    // 50GB dummy
            },
            network: {
                // Would need proper network stats implementation
                rx: Math.random() * 1024 * 1024, // Random KB/s
                tx: Math.random() * 1024 * 1024  // Random KB/s
            },
            uptime: os.uptime()
        };
    }

    errorHandler(err, req, res, next) {
        console.error('Server error:', err);
        
        res.status(err.status || 500).json({
            error: process.env.NODE_ENV === 'production' 
                ? 'Internal server error' 
                : err.message,
            ...(process.env.NODE_ENV !== 'production' && { stack: err.stack })
        });
    }

    async start() {
        // Create HTTPS server
        let httpsServer;
        
        try {
            const httpsOptions = {
                key: fs.readFileSync(this.config.sslKey),
                cert: fs.readFileSync(this.config.sslCert)
            };
            
            httpsServer = https.createServer(httpsOptions, this.app);
            
            httpsServer.listen(this.config.httpsPort, () => {
                console.log(`🔒 HTTPS Server running on https://localhost:${this.config.httpsPort}`);
            });
        } catch (error) {
            console.error('Failed to start HTTPS server:', error);
            console.log('Starting HTTP server only...');
        }

        // Create HTTP server (redirects to HTTPS)
        const httpServer = http.createServer((req, res) => {
            res.writeHead(301, { 
                Location: `https://${req.headers.host}${req.url}` 
            });
            res.end();
        });

        httpServer.listen(this.config.httpPort, () => {
            console.log(`🔄 HTTP Server redirecting from http://localhost:${this.config.httpPort}`);
        });

        // Create WebSocket server
        const wsServer = httpsServer || httpServer;
        const io = new Server(wsServer, {
            cors: {
                origin: [`https://localhost:${this.config.httpsPort}`],
                credentials: true
            }
        });

        // WebSocket authentication
        io.use((socket, next) => {
            const token = socket.handshake.auth.token;
            
            if (!token) {
                return next(new Error('Authentication required'));
            }

            try {
                const decoded = jwt.verify(token, this.config.jwtSecret);
                socket.user = decoded;
                next();
            } catch (err) {
                next(new Error('Invalid token'));
            }
        });

        io.on('connection', (socket) => {
            console.log('WebSocket client connected:', socket.user.username);
            
            // Send system stats every 5 seconds
            const statsInterval = setInterval(async () => {
                const stats = await this.getSystemStats();
                socket.emit('system-stats', stats);
            }, 5000);

            socket.on('subscribe', (data) => {
                console.log('Client subscribed to:', data.stream);
                socket.join(data.stream);
            });

            socket.on('disconnect', () => {
                clearInterval(statsInterval);
                console.log('WebSocket client disconnected');
            });
        });

        console.log('✨ NixOS GUI Secure Server ready!');
        console.log('🔐 JWT Secret:', this.config.jwtSecret.substring(0, 10) + '...');
        console.log('📝 Default login: admin / any-password (demo mode)');
        
        // Notify systemd that we're ready
        if (process.env.NOTIFY_SOCKET) {
            try {
                require('sd-notify').ready();
                console.log('📢 Notified systemd: ready');
            } catch (error) {
                // sd-notify not available, that's OK
            }
        }
    }
}

// Create SSL certificates if they don't exist
function createSSLCertificates() {
    const sslDir = path.join(__dirname, '../../ssl');
    
    if (!fs.existsSync(sslDir)) {
        fs.mkdirSync(sslDir, { recursive: true });
    }

    const certPath = path.join(sslDir, 'cert.pem');
    const keyPath = path.join(sslDir, 'key.pem');

    if (!fs.existsSync(certPath) || !fs.existsSync(keyPath)) {
        console.log('📜 Generating self-signed SSL certificates...');
        
        const { execSync } = require('child_process');
        try {
            execSync(`openssl req -x509 -newkey rsa:4096 -keyout ${keyPath} -out ${certPath} -days 365 -nodes -subj "/C=US/ST=Sacred/L=Digital/O=NixOS-GUI/CN=localhost"`, {
                stdio: 'pipe'
            });
            console.log('✅ SSL certificates generated');
        } catch (error) {
            console.error('Failed to generate SSL certificates:', error);
            console.log('Please create them manually or run with sudo');
        }
    }
}

// Export for use
module.exports = SecureNixOSServer;

// Run if called directly
if (require.main === module) {
    createSSLCertificates();
    
    const server = new SecureNixOSServer();
    server.start().catch(error => {
        console.error('Failed to start server:', error);
        process.exit(1);
    });
}