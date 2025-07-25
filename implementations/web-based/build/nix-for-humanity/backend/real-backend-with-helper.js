/**
 * Production-Ready NixOS Backend with Privileged Helper Integration
 * Combines user-level operations with system-level operations via helper service
 */

const express = require('express');
const cors = require('cors');
const { exec, spawn } = require('child_process');
const { promisify } = require('util');
const path = require('path');
const fs = require('fs').promises;
const WebSocket = require('ws');
const winston = require('winston');
const crypto = require('crypto');
const cookieParser = require('cookie-parser');
const HelperClient = require('../privileged-helper/helper-client');
const AuthService = require('../auth/auth-service');
const { createAuthMiddleware, authenticateWebSocket } = require('../auth/auth-middleware');
const { createAuditMiddleware, auditErrorHandler } = require('../audit/audit-middleware');
const { auditLogger, AuditEventTypes } = require('../audit/audit-logger');

const execAsync = promisify(exec);

// Configuration
const config = {
    port: process.env.PORT || 7891,
    wsPort: process.env.WS_PORT || 7892,
    logLevel: process.env.LOG_LEVEL || 'info',
    maxJobAge: 24 * 60 * 60 * 1000, // 24 hours
    commandTimeout: 5 * 60 * 1000, // 5 minutes
    allowedPackages: process.env.ALLOWED_PACKAGES?.split(',') || null, // null = allow all
    helperSocket: process.env.HELPER_SOCKET || '/run/nixos-gui/helper.sock'
};

// Logger setup
const logger = winston.createLogger({
    level: config.logLevel,
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json()
    ),
    transports: [
        new winston.transports.File({ filename: 'error.log', level: 'error' }),
        new winston.transports.File({ filename: 'combined.log' }),
        new winston.transports.Console({
            format: winston.format.simple()
        })
    ]
});

// Express app setup
const app = express();
app.use(cors({
    credentials: true,
    origin: process.env.FRONTEND_URL || 'http://localhost:8080'
}));
app.use(express.json({ limit: '10mb' }));
app.use(cookieParser());

// Initialize authentication
const authService = new AuthService();
const auth = createAuthMiddleware(authService);

// Initialize audit logging
const audit = createAuditMiddleware({
    skipRoutes: ['/api/health', '/api/auth/verify'],
    includeBody: true,
    includeResponse: true
});

// Apply audit logging middleware
app.use(audit.logRequests);

// Request logging middleware
app.use((req, res, next) => {
    logger.info('Incoming request', {
        method: req.method,
        url: req.url,
        ip: req.ip,
        user: req.user?.username
    });
    next();
});

// Initialize helper client
const helperClient = new HelperClient({
    socketPath: config.helperSocket,
    timeout: config.commandTimeout * 2 // Double timeout for system operations
});

// Connect to helper service
helperClient.connect().catch(err => {
    logger.warn('Helper service not available', { error: err.message });
    logger.info('System operations will require manual authentication');
});

helperClient.on('error', (error) => {
    logger.error('Helper client error', { error: error.message });
});

helperClient.on('connected', () => {
    logger.info('Connected to helper service');
});

helperClient.on('disconnected', () => {
    logger.warn('Disconnected from helper service');
});

/**
 * Job management for async operations
 */
class JobManager {
    constructor() {
        this.jobs = new Map();
        this.jobCounter = 0;
    }

    createJob(type, metadata = {}) {
        const jobId = `job_${++this.jobCounter}_${Date.now()}`;
        const job = {
            id: jobId,
            type,
            status: 'pending',
            progress: 0,
            createdAt: new Date(),
            metadata,
            result: null,
            error: null
        };
        
        this.jobs.set(jobId, job);
        logger.info('Job created', { jobId, type });
        
        return jobId;
    }

    updateJob(jobId, updates) {
        const job = this.jobs.get(jobId);
        if (!job) return;
        
        Object.assign(job, updates);
        
        // Broadcast update via WebSocket
        broadcastJobUpdate(job);
    }

    getJob(jobId) {
        return this.jobs.get(jobId);
    }

    cleanupOldJobs() {
        const now = Date.now();
        for (const [jobId, job] of this.jobs) {
            if (now - job.createdAt.getTime() > config.maxJobAge) {
                this.jobs.delete(jobId);
            }
        }
    }
}

const jobManager = new JobManager();

// Cleanup old jobs periodically
setInterval(() => jobManager.cleanupOldJobs(), 60 * 60 * 1000); // Every hour

/**
 * WebSocket server for real-time updates
 */
const wss = new WebSocket.Server({ 
    port: config.wsPort,
    verifyClient: (info, cb) => {
        // Extract token from query string
        const url = new URL(info.req.url, `http://${info.req.headers.host}`);
        const token = url.searchParams.get('token');
        
        if (!token) {
            cb(false, 401, 'Unauthorized');
            return;
        }
        
        try {
            const decoded = authService.verifyAccessToken(token);
            info.req.user = decoded;
            cb(true);
        } catch (error) {
            cb(false, 401, 'Invalid token');
        }
    }
});

wss.on('connection', (ws, req) => {
    logger.info('WebSocket client connected', { username: req.user?.username });
    
    // Store user info on the WebSocket
    ws.user = req.user;
    
    ws.on('error', (error) => {
        logger.error('WebSocket error', { error: error.message });
    });
    
    ws.on('close', () => {
        logger.info('WebSocket client disconnected', { username: ws.user?.username });
    });
});

function broadcastJobUpdate(job) {
    const message = JSON.stringify({
        type: 'job-update',
        job
    });
    
    wss.clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
            // Only send job updates to the job owner or admins
            if (client.user && 
                (client.user.username === job.metadata.username || 
                 client.user.isAdmin)) {
                client.send(message);
            }
        }
    });
}

/**
 * Enhanced Nix operations with helper integration
 */
class NixOperations {
    constructor() {
        this.isFlakeSystem = null;
    }

    async checkNixVersion() {
        try {
            const { stdout } = await execAsync('nix --version');
            const match = stdout.match(/nix \(Nix\) (\d+)\.(\d+)/);
            if (match) {
                const major = parseInt(match[1]);
                const minor = parseInt(match[2]);
                this.isFlakeSystem = major > 2 || (major === 2 && minor >= 4);
            }
            return stdout.trim();
        } catch (error) {
            logger.error('Failed to check Nix version', { error });
            throw error;
        }
    }

    async searchPackages(query) {
        if (!query || query.length < 2) {
            throw new Error('Search query must be at least 2 characters');
        }

        const command = `nix search nixpkgs ${this.escapeShellArg(query)} --json`;
        
        try {
            const { stdout } = await execAsync(command, { 
                timeout: 30000,
                maxBuffer: 10 * 1024 * 1024 // 10MB
            });
            
            const results = JSON.parse(stdout || '{}');
            
            // Transform results to consistent format
            const packages = Object.entries(results).map(([attrPath, pkg]) => ({
                name: pkg.pname || attrPath.split('.').pop(),
                version: pkg.version,
                description: pkg.description || '',
                attrPath: attrPath.replace('legacyPackages.x86_64-linux.', '')
            }));
            
            return packages;
        } catch (error) {
            logger.error('Package search failed', { query, error });
            throw error;
        }
    }

    async installPackage(packageName, scope = 'user') {
        if (!this.isValidPackageName(packageName)) {
            throw new Error('Invalid package name');
        }

        if (config.allowedPackages && !config.allowedPackages.includes(packageName)) {
            throw new Error(`Package '${packageName}' is not in the allowed list`);
        }

        if (scope === 'system') {
            // Use helper service for system packages
            if (helperClient.connected) {
                return await helperClient.installSystemPackage(packageName);
            } else {
                // Return configuration snippet if helper not available
                return {
                    action: 'show-config',
                    snippet: `  environment.systemPackages = with pkgs; [\n    ${packageName}\n  ];`,
                    message: 'Add this to your /etc/nixos/configuration.nix and run nixos-rebuild'
                };
            }
        }

        // User-level installation
        const command = this.isFlakeSystem
            ? `nix profile install nixpkgs#${packageName}`
            : `nix-env -iA nixpkgs.${packageName}`;

        return await this.executeCommand(command);
    }

    async removePackage(packageName, scope = 'user') {
        if (!this.isValidPackageName(packageName)) {
            throw new Error('Invalid package name');
        }

        if (scope === 'system') {
            // Use helper service for system packages
            if (helperClient.connected) {
                return await helperClient.removeSystemPackage(packageName);
            } else {
                return {
                    action: 'manual-edit',
                    message: 'Remove the package from /etc/nixos/configuration.nix and run nixos-rebuild'
                };
            }
        }

        // User-level removal
        const command = this.isFlakeSystem
            ? `nix profile remove ${packageName}`
            : `nix-env -e ${packageName}`;

        return await this.executeCommand(command);
    }

    async executeCommand(command, options = {}) {
        return new Promise((resolve, reject) => {
            const proc = spawn('bash', ['-c', command]);
            let stdout = '';
            let stderr = '';

            const timeout = setTimeout(() => {
                proc.kill();
                reject(new Error(`Command timed out: ${command}`));
            }, options.timeout || config.commandTimeout);

            proc.stdout.on('data', (data) => {
                stdout += data.toString();
            });

            proc.stderr.on('data', (data) => {
                stderr += data.toString();
            });

            proc.on('close', (code) => {
                clearTimeout(timeout);
                
                if (code === 0) {
                    resolve({ stdout, stderr, code });
                } else {
                    reject(new Error(`Command failed: ${stderr || stdout}`));
                }
            });

            proc.on('error', (error) => {
                clearTimeout(timeout);
                reject(error);
            });
        });
    }

    isValidPackageName(name) {
        return /^[a-zA-Z0-9][a-zA-Z0-9._-]*$/.test(name);
    }

    escapeShellArg(arg) {
        return "'" + arg.replace(/'/g, "'\\''") + "'";
    }
}

const nixOps = new NixOperations();

// Initialize Nix version check
nixOps.checkNixVersion().catch(err => {
    logger.error('Failed to initialize Nix', { error: err });
});

/**
 * System operations via helper service
 */
class SystemOperations {
    async rebuildSystem(options = {}) {
        if (!helperClient.connected) {
            throw new Error('Helper service not available. Please run operations manually.');
        }
        
        return await helperClient.rebuildSystem(options);
    }

    async rollbackSystem() {
        if (!helperClient.connected) {
            throw new Error('Helper service not available. Please run "nixos-rebuild switch --rollback" manually.');
        }
        
        return await helperClient.rollbackSystem();
    }

    async editConfiguration(changes) {
        if (!helperClient.connected) {
            return {
                action: 'manual-edit',
                message: 'Please edit /etc/nixos/configuration.nix manually',
                changes
            };
        }
        
        return await helperClient.editConfiguration(changes);
    }

    async validateConfiguration() {
        if (!helperClient.connected) {
            return {
                action: 'manual-validate',
                command: 'nixos-rebuild dry-build',
                message: 'Run this command to validate your configuration'
            };
        }
        
        return await helperClient.validateConfiguration();
    }

    async getGenerations() {
        try {
            // Get list of generations
            const { stdout: listOutput } = await execAsync('nix-env --list-generations -p /nix/var/nix/profiles/system');
            
            // Parse generations
            const generations = [];
            const lines = listOutput.trim().split('\n');
            
            for (const line of lines) {
                const match = line.match(/^\s*(\d+)\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})/);
                if (match) {
                    const genNum = parseInt(match[1]);
                    const date = match[2];
                    
                    // Try to get kernel version for this generation
                    let kernel = 'Unknown';
                    try {
                        const { stdout: kernelOutput } = await execAsync(
                            `readlink /nix/var/nix/profiles/system-${genNum}-link/kernel 2>/dev/null | grep -oP 'linux-\\K[^/]+'`
                        );
                        if (kernelOutput.trim()) {
                            kernel = kernelOutput.trim();
                        }
                    } catch (e) {
                        // Ignore errors getting kernel version
                    }
                    
                    generations.push({
                        number: genNum,
                        date,
                        kernel,
                        description: line.includes('(current)') ? 'Current generation' : null
                    });
                }
            }
            
            // Get current generation
            const { stdout: currentGen } = await execAsync('readlink /nix/var/nix/profiles/system | grep -oP "system-\\K\\d+"');
            const current = parseInt(currentGen.trim());
            
            return {
                generations,
                current
            };
        } catch (error) {
            throw new Error(`Failed to get generations: ${error.message}`);
        }
    }

    async switchToGeneration(generation) {
        if (!helperClient.connected) {
            return {
                action: 'manual-switch',
                command: `sudo nixos-rebuild switch --rollback --to-generation ${generation}`,
                message: 'Run this command to switch to the specified generation'
            };
        }
        
        return await helperClient.switchToGeneration(generation);
    }

    async compareGenerations(from, to) {
        try {
            // This is a simplified comparison - in production, use proper Nix tools
            const fromPath = `/nix/var/nix/profiles/system-${from}-link`;
            const toPath = `/nix/var/nix/profiles/system-${to}-link`;
            
            // Compare packages
            const { stdout: fromPkgs } = await execAsync(`nix-store -q --references ${fromPath} | grep -E '[^-]+-[^-]+$' | sort`);
            const { stdout: toPkgs } = await execAsync(`nix-store -q --references ${toPath} | grep -E '[^-]+-[^-]+$' | sort`);
            
            const fromPkgSet = new Set(fromPkgs.trim().split('\n').filter(Boolean));
            const toPkgSet = new Set(toPkgs.trim().split('\n').filter(Boolean));
            
            const added = [...toPkgSet].filter(pkg => !fromPkgSet.has(pkg)).map(p => p.split('/').pop());
            const removed = [...fromPkgSet].filter(pkg => !toPkgSet.has(pkg)).map(p => p.split('/').pop());
            
            return {
                packages: {
                    added,
                    removed
                },
                services: {}, // Would need to parse configuration.nix for accurate service comparison
                configuration: `Use 'diff ${fromPath}/configuration.nix ${toPath}/configuration.nix' for detailed changes`
            };
        } catch (error) {
            throw new Error(`Failed to compare generations: ${error.message}`);
        }
    }

    async deleteGeneration(generation) {
        if (!helperClient.connected) {
            return {
                action: 'manual-delete',
                command: `sudo nix-env --delete-generations ${generation} -p /nix/var/nix/profiles/system`,
                message: 'Run this command to delete the specified generation'
            };
        }
        
        return await helperClient.deleteGeneration(generation);
    }

    async cleanGenerations(keep) {
        if (!helperClient.connected) {
            return {
                action: 'manual-clean',
                command: `sudo nix-collect-garbage -d --delete-older-than ${keep}d`,
                message: `Run this command to keep only the last ${keep} days of generations`
            };
        }
        
        return await helperClient.cleanGenerations(keep);
    }
}

const sysOps = new SystemOperations();

/**
 * Authentication Routes (Public)
 */

// Login
app.post('/api/auth/login', async (req, res) => {
    try {
        const { username, password } = req.body;
        const clientInfo = {
            ip: req.ip,
            userAgent: req.headers['user-agent']
        };
        
        const result = await authService.login(username, password, clientInfo);
        
        // Set refresh token as httpOnly cookie
        res.cookie('refreshToken', result.refreshToken, {
            httpOnly: true,
            secure: process.env.NODE_ENV === 'production',
            sameSite: 'strict',
            maxAge: 7 * 24 * 60 * 60 * 1000 // 7 days
        });
        
        res.json({
            success: true,
            accessToken: result.accessToken,
            sessionId: result.sessionId,
            user: result.user
        });
    } catch (error) {
        logger.error('Login failed', { error: error.message });
        res.status(401).json({
            success: false,
            error: error.message
        });
    }
});

// Logout
app.post('/api/auth/logout', auth.optionalAuth, (req, res) => {
    try {
        const refreshToken = req.cookies.refreshToken || req.body.refreshToken;
        authService.logout(req.session?.id, refreshToken);
        
        res.clearCookie('refreshToken');
        res.json({
            success: true,
            message: 'Logged out successfully'
        });
    } catch (error) {
        logger.error('Logout error', { error: error.message });
        res.json({
            success: true,
            message: 'Logged out'
        });
    }
});

// Refresh token
app.post('/api/auth/refresh', async (req, res) => {
    try {
        const refreshToken = req.cookies.refreshToken || req.body.refreshToken;
        const result = await authService.refreshAccessToken(refreshToken);
        
        res.json({
            success: true,
            accessToken: result.accessToken,
            user: result.user
        });
    } catch (error) {
        logger.error('Token refresh failed', { error: error.message });
        res.status(401).json({
            success: false,
            error: error.message
        });
    }
});

// Verify token
app.get('/api/auth/verify', auth.requireAuth, (req, res) => {
    res.json({
        success: true,
        user: req.user,
        sessionId: req.session.id
    });
});

// Get active sessions
app.get('/api/auth/sessions', auth.requireAuth, (req, res) => {
    const sessions = authService.getActiveSessions();
    const userSessions = sessions.filter(s => s.username === req.user.username);
    
    res.json({
        success: true,
        sessions: userSessions,
        current: req.session.id
    });
});

// Terminate session
app.delete('/api/auth/sessions/:sessionId', auth.requireAuth, (req, res) => {
    const { sessionId } = req.params;
    
    // Users can only terminate their own sessions
    const session = authService.getSession(sessionId);
    if (!session || session.user.username !== req.user.username) {
        return res.status(403).json({
            success: false,
            error: 'Cannot terminate this session'
        });
    }
    
    authService.logout(sessionId);
    
    res.json({
        success: true,
        message: 'Session terminated'
    });
});

/**
 * API Routes (Protected)
 */

// Health check (public)
app.get('/api/health', (req, res) => {
    res.json({
        status: 'healthy',
        version: '2.0.0',
        uptime: process.uptime(),
        helperConnected: helperClient.connected
    });
});

// System information (protected)
app.get('/api/system/info', auth.requireAuth, async (req, res) => {
    try {
        const [nixVersion, systemVersion, diskUsage, memory] = await Promise.all([
            nixOps.checkNixVersion(),
            execAsync('nixos-version 2>/dev/null || echo "Not NixOS"'),
            execAsync('df -h /nix/store | tail -1'),
            execAsync('free -h | grep Mem:')
        ]);

        const diskParts = diskUsage.stdout.split(/\s+/);
        const memParts = memory.stdout.split(/\s+/);

        res.json({
            success: true,
            nixVersion,
            systemVersion: systemVersion.stdout.trim(),
            helperAvailable: helperClient.connected,
            disk: {
                total: diskParts[1],
                used: diskParts[2],
                available: diskParts[3],
                percent: diskParts[4]
            },
            memory: {
                total: memParts[1],
                used: memParts[2],
                free: memParts[3]
            }
        });
    } catch (error) {
        logger.error('Failed to get system info', { error });
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Package search (protected)
app.post('/api/nix/search', auth.requireAuth, async (req, res) => {
    try {
        const { query } = req.body;
        const packages = await nixOps.searchPackages(query);
        
        res.json({
            success: true,
            packages,
            count: packages.length
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            error: error.message,
            suggestion: 'Try a different search term or check your internet connection'
        });
    }
});

// Package installation (protected with permission check)
app.post('/api/nix/install', auth.requireAuth, auth.requirePermission('packages.install.user'), async (req, res) => {
    try {
        const { package: packageName, scope = 'user' } = req.body;
        
        // Additional permission check for system packages
        if (scope === 'system' && !req.user.groups.includes('wheel')) {
            return res.status(403).json({
                success: false,
                error: 'Admin privileges required for system package installation'
            });
        }
        
        if (scope === 'system' && !helperClient.connected) {
            // Return configuration snippet for manual installation
            const result = await nixOps.installPackage(packageName, scope);
            return res.json({ success: true, ...result });
        }
        
        // Create job for async installation
        const jobId = jobManager.createJob('install', { 
            packageName, 
            scope,
            username: req.user.username
        });
        
        // Start installation in background
        nixOps.executeInstallation(jobId, packageName, scope).catch(error => {
            logger.error('Installation failed', { jobId, error });
        });
        
        res.json({
            success: true,
            jobId,
            message: 'Installation started'
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            error: error.message
        });
    }
});

// System rebuild (admin only)
app.post('/api/system/rebuild', auth.requireAuth, auth.requireAdmin, async (req, res) => {
    try {
        const { action = 'switch', upgrade = false } = req.body;
        
        const jobId = jobManager.createJob('rebuild', { 
            action, 
            upgrade,
            username: req.user.username
        });
        
        // Execute rebuild in background
        sysOps.rebuildSystem({ action, upgrade })
            .then(result => {
                jobManager.updateJob(jobId, {
                    status: 'completed',
                    progress: 100,
                    result
                });
            })
            .catch(error => {
                jobManager.updateJob(jobId, {
                    status: 'failed',
                    error: error.message
                });
            });
        
        res.json({
            success: true,
            jobId,
            message: 'System rebuild started'
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            error: error.message
        });
    }
});

// Get system generations (protected)
app.get('/api/system/generations', auth.requireAuth, async (req, res) => {
    try {
        const result = await sysOps.getGenerations();
        res.json({
            success: true,
            ...result
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            error: error.message
        });
    }
});

// Switch to specific generation (admin only)
app.post('/api/system/switch-generation', auth.requireAuth, auth.requireAdmin, async (req, res) => {
    try {
        const { generation } = req.body;
        
        if (!generation || generation < 1) {
            throw new Error('Invalid generation number');
        }
        
        const result = await sysOps.switchToGeneration(generation);
        res.json({
            success: true,
            ...result
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            error: error.message
        });
    }
});

// System rollback (admin only)
app.post('/api/system/rollback', auth.requireAuth, auth.requireAdmin, async (req, res) => {
    try {
        const result = await sysOps.rollbackSystem();
        res.json({
            success: true,
            result
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            error: error.message
        });
    }
});

// Compare generations (protected)
app.get('/api/system/compare-generations', auth.requireAuth, async (req, res) => {
    try {
        const { from, to } = req.query;
        
        if (!from || !to) {
            throw new Error('Both from and to generation numbers are required');
        }
        
        const result = await sysOps.compareGenerations(parseInt(from), parseInt(to));
        res.json({
            success: true,
            differences: result
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            error: error.message
        });
    }
});

// Delete generation (admin only)
app.delete('/api/system/generations/:generation', auth.requireAuth, auth.requireAdmin, async (req, res) => {
    try {
        const generation = parseInt(req.params.generation);
        
        if (!generation || generation < 1) {
            throw new Error('Invalid generation number');
        }
        
        const result = await sysOps.deleteGeneration(generation);
        res.json({
            success: true,
            ...result
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            error: error.message
        });
    }
});

// Clean old generations (admin only)
app.post('/api/system/clean-generations', auth.requireAuth, auth.requireAdmin, async (req, res) => {
    try {
        const { keep = 5 } = req.body;
        
        if (keep < 2) {
            throw new Error('Must keep at least 2 generations');
        }
        
        const result = await sysOps.cleanGenerations(keep);
        res.json({
            success: true,
            ...result
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            error: error.message
        });
    }
});

// Get current configuration (protected with permission)
app.get('/api/system/configuration', auth.requireAuth, auth.requirePermission('config.view'), async (req, res) => {
    try {
        const configPath = '/etc/nixos/configuration.nix';
        
        // Check if we can read the file directly
        try {
            const content = await fs.readFile(configPath, 'utf8');
            res.json({
                success: true,
                content,
                path: configPath
            });
        } catch (readError) {
            // If can't read directly, use helper service
            if (helperClient.connected) {
                const result = await helperClient.getConfiguration();
                res.json({
                    success: true,
                    ...result
                });
            } else {
                throw new Error('Cannot read configuration. Please check permissions.');
            }
        }
    } catch (error) {
        res.status(400).json({
            success: false,
            error: error.message,
            suggestion: 'You may need to run the GUI with appropriate permissions'
        });
    }
});

// Update configuration (admin only)
app.put('/api/system/configuration', auth.requireAuth, auth.requireAdmin, async (req, res) => {
    try {
        const { content, backup = true } = req.body;
        
        if (!content) {
            throw new Error('Configuration content is required');
        }
        
        // Create backup if requested
        let backupPath = null;
        if (backup) {
            backupPath = `/etc/nixos/configuration.nix.backup-${Date.now()}`;
        }
        
        // Use helper service to edit configuration
        const result = await sysOps.editConfiguration({ 
            content, 
            backupPath 
        });
        
        res.json({
            success: true,
            ...result
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            error: error.message
        });
    }
});

// Configuration validation (protected)
app.post('/api/system/validate', auth.requireAuth, async (req, res) => {
    try {
        const { content } = req.body;
        
        let result;
        if (content) {
            // Validate provided content
            result = await sysOps.validateConfiguration({ content });
        } else {
            // Validate current configuration
            result = await sysOps.validateConfiguration();
        }
        
        res.json({
            success: true,
            ...result
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            error: error.message
        });
    }
});

/**
 * Audit API Routes (Admin only)
 */

// Get audit report
app.post('/api/audit/report', auth.requireAuth, auth.requireAdmin, async (req, res) => {
    try {
        const { startDate, endDate, filters } = req.body;
        
        const report = await auditLogger.createAuditReport(
            new Date(startDate),
            new Date(endDate),
            filters
        );
        
        // Log that audit report was accessed
        audit.logAdminOperation('audit.export', {
            username: req.user.username,
            dateRange: { startDate, endDate },
            filters
        });
        
        res.json(report);
    } catch (error) {
        logger.error('Failed to generate audit report', { error });
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Export audit logs
app.post('/api/audit/export', auth.requireAuth, auth.requireAdmin, async (req, res) => {
    try {
        const { format = 'json', filters } = req.body;
        
        const data = await auditLogger.exportLogs(format, filters);
        
        // Set appropriate content type
        const contentTypes = {
            json: 'application/json',
            csv: 'text/csv',
            syslog: 'text/plain'
        };
        
        res.setHeader('Content-Type', contentTypes[format] || 'application/octet-stream');
        res.setHeader('Content-Disposition', `attachment; filename="audit-logs-${Date.now()}.${format}"`);
        
        res.send(data);
    } catch (error) {
        logger.error('Failed to export audit logs', { error });
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Get real-time audit events (WebSocket endpoint documented below)

// Job status (protected)
app.get('/api/job/:jobId', auth.requireAuth, (req, res) => {
    const job = jobManager.getJob(req.params.jobId);
    
    if (!job) {
        return res.status(404).json({
            success: false,
            error: 'Job not found'
        });
    }
    
    // Ensure user can only view their own jobs
    if (job.metadata.username && job.metadata.username !== req.user.username && !req.user.isAdmin) {
        return res.status(403).json({
            success: false,
            error: 'Access denied'
        });
    }
    
    res.json({
        success: true,
        job
    });
});

// Execute installation with progress tracking
nixOps.executeInstallation = async function(jobId, packageName, scope) {
    jobManager.updateJob(jobId, {
        status: 'running',
        progress: 10
    });

    try {
        // Check if package exists
        const packages = await this.searchPackages(packageName);
        if (packages.length === 0) {
            throw new Error(`Package '${packageName}' not found`);
        }

        jobManager.updateJob(jobId, {
            progress: 30
        });

        // Install package
        const result = await this.installPackage(packageName, scope);

        jobManager.updateJob(jobId, {
            status: 'completed',
            progress: 100,
            result
        });

    } catch (error) {
        jobManager.updateJob(jobId, {
            status: 'failed',
            error: error.message
        });
        throw error;
    }
};

// Error handling middleware (must be last)
app.use(auditErrorHandler);
app.use((err, req, res, next) => {
    logger.error('Unhandled error', {
        error: err.message,
        stack: err.stack,
        path: req.path,
        method: req.method
    });
    
    res.status(err.status || 500).json({
        success: false,
        error: process.env.NODE_ENV === 'production' 
            ? 'Internal server error' 
            : err.message
    });
});

// Start server
const server = app.listen(config.port, () => {
    logger.info(`Backend server running on port ${config.port}`);
    logger.info(`WebSocket server running on port ${config.wsPort}`);
    
    // Log server startup
    auditLogger.log('server.start', {
        port: config.port,
        wsPort: config.wsPort,
        nodeVersion: process.version,
        helperConnected: helperClient.connected
    });
});

// Graceful shutdown
process.on('SIGTERM', () => {
    logger.info('SIGTERM received, shutting down gracefully');
    
    server.close(() => {
        logger.info('HTTP server closed');
    });
    
    wss.close(() => {
        logger.info('WebSocket server closed');
    });
    
    helperClient.disconnect();
    
    setTimeout(() => {
        process.exit(0);
    }, 5000);
});

module.exports = app;