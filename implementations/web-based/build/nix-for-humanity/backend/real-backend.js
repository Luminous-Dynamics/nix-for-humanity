/**
 * Production-Ready NixOS Backend
 * Real operations with comprehensive error handling
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

const execAsync = promisify(exec);

// Configuration
const config = {
    port: process.env.PORT || 7891,
    wsPort: process.env.WS_PORT || 7892,
    logLevel: process.env.LOG_LEVEL || 'info',
    maxJobAge: 24 * 60 * 60 * 1000, // 24 hours
    commandTimeout: 5 * 60 * 1000, // 5 minutes
    allowedPackages: process.env.ALLOWED_PACKAGES?.split(',') || null // null = allow all
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
app.use(cors());
app.use(express.json({ limit: '10mb' }));

// Request logging middleware
app.use((req, res, next) => {
    logger.info(`${req.method} ${req.path}`, { 
        ip: req.ip, 
        userAgent: req.get('user-agent') 
    });
    next();
});

// WebSocket setup
const wss = new WebSocket.Server({ port: config.wsPort });
const wsClients = new Map();

wss.on('connection', (ws, req) => {
    const clientId = crypto.randomUUID();
    wsClients.set(clientId, ws);
    logger.info(`WebSocket client connected: ${clientId}`);
    
    ws.on('close', () => {
        wsClients.delete(clientId);
        logger.info(`WebSocket client disconnected: ${clientId}`);
    });
    
    ws.on('error', (error) => {
        logger.error(`WebSocket error for client ${clientId}:`, error);
    });
});

// Job management
class JobManager {
    constructor() {
        this.jobs = new Map();
        this.jobCounter = 0;
        
        // Clean up old jobs periodically
        setInterval(() => this.cleanupOldJobs(), 60 * 60 * 1000); // Every hour
    }
    
    createJob(type, data) {
        const jobId = `job_${++this.jobCounter}_${Date.now()}`;
        const job = {
            id: jobId,
            type,
            data,
            status: 'pending',
            progress: 0,
            output: [],
            error: null,
            createdAt: new Date(),
            updatedAt: new Date()
        };
        
        this.jobs.set(jobId, job);
        logger.info(`Job created: ${jobId}`, { type, data });
        return jobId;
    }
    
    updateJob(jobId, updates) {
        const job = this.jobs.get(jobId);
        if (!job) return null;
        
        Object.assign(job, updates, { updatedAt: new Date() });
        this.broadcastJobUpdate(job);
        return job;
    }
    
    getJob(jobId) {
        return this.jobs.get(jobId);
    }
    
    broadcastJobUpdate(job) {
        const message = JSON.stringify({
            type: 'job-update',
            job: {
                id: job.id,
                type: job.type,
                status: job.status,
                progress: job.progress,
                error: job.error
            }
        });
        
        wsClients.forEach(ws => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(message);
            }
        });
    }
    
    cleanupOldJobs() {
        const now = Date.now();
        let cleaned = 0;
        
        for (const [jobId, job] of this.jobs.entries()) {
            if (now - job.createdAt.getTime() > config.maxJobAge) {
                this.jobs.delete(jobId);
                cleaned++;
            }
        }
        
        if (cleaned > 0) {
            logger.info(`Cleaned up ${cleaned} old jobs`);
        }
    }
}

const jobManager = new JobManager();

// Nix operations handler
class NixOperations {
    constructor() {
        this.experimentalFeatures = null;
        this.checkExperimentalFeatures();
    }
    
    async checkExperimentalFeatures() {
        try {
            const { stdout } = await execAsync('nix --version');
            const version = stdout.trim();
            
            // Check if experimental features are enabled
            try {
                await execAsync('nix flake --help', { timeout: 5000 });
                this.experimentalFeatures = true;
                logger.info('Nix experimental features enabled');
            } catch {
                this.experimentalFeatures = false;
                logger.warn('Nix experimental features not enabled');
            }
        } catch (error) {
            logger.error('Failed to check Nix version:', error);
        }
    }
    
    async searchPackages(query) {
        const startTime = Date.now();
        
        try {
            let command, parseJson = false;
            
            if (this.experimentalFeatures) {
                // Use new nix search with JSON output
                command = `nix search nixpkgs ${this.escapeShellArg(query)} --json`;
                parseJson = true;
            } else {
                // Fallback to nix-env
                command = `nix-env -qaP | grep -i ${this.escapeShellArg(query)}`;
            }
            
            const { stdout, stderr } = await execAsync(command, {
                timeout: 30000,
                maxBuffer: 10 * 1024 * 1024
            });
            
            const packages = parseJson 
                ? this.parseNixSearchJson(stdout)
                : this.parseNixEnvOutput(stdout);
            
            logger.info(`Package search completed in ${Date.now() - startTime}ms`, {
                query,
                resultCount: packages.length
            });
            
            return { success: true, packages };
            
        } catch (error) {
            logger.error('Package search failed:', error);
            return {
                success: false,
                error: error.message,
                suggestion: 'Try a simpler search term or check your internet connection'
            };
        }
    }
    
    async installPackage(packageName, scope = 'user') {
        if (scope === 'system') {
            // For system packages, return configuration snippet
            return {
                success: true,
                action: 'show-config',
                snippet: this.generateSystemPackageSnippet(packageName),
                instructions: 'Add this to your /etc/nixos/configuration.nix and run: sudo nixos-rebuild switch'
            };
        }
        
        // Validate package name
        if (!this.isValidPackageName(packageName)) {
            throw new Error('Invalid package name');
        }
        
        // Check if package is allowed (if restrictions are configured)
        if (config.allowedPackages && !config.allowedPackages.includes(packageName)) {
            throw new Error(`Package ${packageName} is not in the allowed list`);
        }
        
        const jobId = jobManager.createJob('install', { package: packageName, scope });
        
        // Execute installation asynchronously
        this.executeInstallation(jobId, packageName);
        
        return { success: true, jobId };
    }
    
    async executeInstallation(jobId, packageName) {
        const job = jobManager.getJob(jobId);
        if (!job) return;
        
        jobManager.updateJob(jobId, { status: 'running', progress: 10 });
        
        try {
            // First, check if package exists
            jobManager.updateJob(jobId, { 
                status: 'running', 
                progress: 20,
                output: [...job.output, 'Checking package availability...']
            });
            
            const searchResult = await this.searchPackages(packageName);
            if (!searchResult.success || searchResult.packages.length === 0) {
                throw new Error(`Package '${packageName}' not found`);
            }
            
            // Determine installation method
            let installProcess;
            
            if (this.experimentalFeatures) {
                // Use nix profile install
                installProcess = spawn('nix', [
                    'profile', 'install', `nixpkgs#${packageName}`,
                    '--no-write-lock-file'
                ]);
            } else {
                // Use nix-env
                installProcess = spawn('nix-env', ['-iA', `nixpkgs.${packageName}`]);
            }
            
            jobManager.updateJob(jobId, { 
                status: 'running', 
                progress: 30,
                output: [...job.output, `Installing ${packageName}...`]
            });
            
            // Handle process output
            installProcess.stdout.on('data', (data) => {
                const output = data.toString();
                const currentJob = jobManager.getJob(jobId);
                
                // Update progress based on output
                let progress = currentJob.progress;
                if (output.includes('downloading')) progress = 40;
                if (output.includes('building')) progress = 60;
                if (output.includes('installing')) progress = 80;
                
                jobManager.updateJob(jobId, {
                    progress,
                    output: [...currentJob.output, output.trim()]
                });
            });
            
            installProcess.stderr.on('data', (data) => {
                const error = data.toString();
                const currentJob = jobManager.getJob(jobId);
                
                // Some stderr output is informational
                if (!error.includes('error:') && !error.includes('fatal:')) {
                    jobManager.updateJob(jobId, {
                        output: [...currentJob.output, error.trim()]
                    });
                }
            });
            
            // Handle process completion
            installProcess.on('close', (code) => {
                if (code === 0) {
                    jobManager.updateJob(jobId, {
                        status: 'completed',
                        progress: 100,
                        output: [...job.output, `Successfully installed ${packageName}`]
                    });
                    
                    logger.info(`Package installed successfully: ${packageName}`);
                } else {
                    const errorMsg = `Installation failed with exit code ${code}`;
                    jobManager.updateJob(jobId, {
                        status: 'failed',
                        error: errorMsg
                    });
                    
                    logger.error(`Package installation failed: ${packageName}`, { exitCode: code });
                }
            });
            
            // Set timeout
            setTimeout(() => {
                if (jobManager.getJob(jobId)?.status === 'running') {
                    installProcess.kill();
                    jobManager.updateJob(jobId, {
                        status: 'failed',
                        error: 'Installation timed out'
                    });
                }
            }, config.commandTimeout);
            
        } catch (error) {
            jobManager.updateJob(jobId, {
                status: 'failed',
                error: error.message
            });
            
            logger.error(`Installation error for ${packageName}:`, error);
        }
    }
    
    async removePackage(packageName) {
        const jobId = jobManager.createJob('remove', { package: packageName });
        
        try {
            let command;
            
            if (this.experimentalFeatures) {
                // First, find the package in profile
                const { stdout } = await execAsync('nix profile list --json');
                const profiles = JSON.parse(stdout);
                
                const packageEntry = Object.entries(profiles).find(([_, info]) => 
                    info.pname === packageName
                );
                
                if (!packageEntry) {
                    throw new Error(`Package '${packageName}' not found in profile`);
                }
                
                command = `nix profile remove ${packageEntry[0]}`;
            } else {
                command = `nix-env -e ${this.escapeShellArg(packageName)}`;
            }
            
            const { stdout, stderr } = await execAsync(command, {
                timeout: 30000
            });
            
            jobManager.updateJob(jobId, {
                status: 'completed',
                progress: 100,
                output: [stdout || `Successfully removed ${packageName}`]
            });
            
            return { success: true, jobId };
            
        } catch (error) {
            jobManager.updateJob(jobId, {
                status: 'failed',
                error: error.message
            });
            
            throw error;
        }
    }
    
    async getSystemInfo() {
        try {
            const [nixVersion, systemVersion, diskUsage, memoryInfo] = await Promise.all([
                execAsync('nix --version').then(r => r.stdout.trim()).catch(() => 'Unknown'),
                execAsync('nixos-version').then(r => r.stdout.trim()).catch(() => 'Unknown'),
                execAsync('df -h /nix/store | tail -1').then(r => {
                    const parts = r.stdout.trim().split(/\s+/);
                    return { used: parts[2], total: parts[1], percent: parts[4] };
                }).catch(() => ({ used: 'Unknown', total: 'Unknown', percent: 'Unknown' })),
                execAsync('free -h | grep Mem:').then(r => {
                    const parts = r.stdout.trim().split(/\s+/);
                    return { used: parts[2], total: parts[1], available: parts[6] };
                }).catch(() => ({ used: 'Unknown', total: 'Unknown', available: 'Unknown' }))
            ]);
            
            return {
                nixVersion,
                systemVersion,
                disk: diskUsage,
                memory: memoryInfo,
                experimentalFeatures: this.experimentalFeatures
            };
            
        } catch (error) {
            logger.error('Failed to get system info:', error);
            throw error;
        }
    }
    
    // Helper methods
    escapeShellArg(arg) {
        return `'${arg.replace(/'/g, "'\\''")}'`;
    }
    
    isValidPackageName(name) {
        return /^[a-zA-Z0-9][a-zA-Z0-9\-_.]*$/.test(name);
    }
    
    parseNixSearchJson(jsonStr) {
        try {
            const results = JSON.parse(jsonStr);
            return Object.entries(results).map(([attrPath, info]) => ({
                name: info.pname || attrPath.split('.').pop(),
                version: info.version || 'unknown',
                description: info.description || 'No description available',
                attrPath
            }));
        } catch (error) {
            logger.error('Failed to parse nix search JSON:', error);
            return [];
        }
    }
    
    parseNixEnvOutput(output) {
        const lines = output.trim().split('\n').filter(Boolean);
        return lines.map(line => {
            const parts = line.split(/\s+/);
            const attrPath = parts[0];
            const nameVersion = parts[1] || '';
            const match = nameVersion.match(/^([^-]+)-(.+)$/);
            
            return {
                name: match ? match[1] : nameVersion,
                version: match ? match[2] : 'unknown',
                description: parts.slice(2).join(' ') || 'No description available',
                attrPath
            };
        });
    }
    
    generateSystemPackageSnippet(packageName) {
        return `# Add ${packageName} to system packages
environment.systemPackages = with pkgs; [
  # ... existing packages ...
  ${packageName}
];`;
    }
}

const nixOps = new NixOperations();

// Service management
class ServiceManager {
    async getServiceStatus(serviceName) {
        try {
            const { stdout } = await execAsync(
                `systemctl is-active ${this.escapeServiceName(serviceName)}`,
                { timeout: 5000 }
            );
            
            return { active: stdout.trim() === 'active' };
        } catch {
            return { active: false };
        }
    }
    
    async manageService(serviceName, action) {
        const validActions = ['start', 'stop', 'restart', 'enable', 'disable', 'status'];
        if (!validActions.includes(action)) {
            throw new Error('Invalid service action');
        }
        
        const needsSudo = ['enable', 'disable'].includes(action);
        const command = needsSudo 
            ? `sudo systemctl ${action} ${this.escapeServiceName(serviceName)}`
            : `systemctl ${action} ${this.escapeServiceName(serviceName)}`;
        
        if (needsSudo) {
            // For system services that need sudo, return instructions
            return {
                success: true,
                requiresSudo: true,
                command,
                instructions: 'This operation requires administrator privileges. Run the command in a terminal.'
            };
        }
        
        try {
            const { stdout, stderr } = await execAsync(command, { timeout: 10000 });
            
            return {
                success: true,
                output: stdout || stderr || `Service ${serviceName} ${action} completed`
            };
        } catch (error) {
            throw new Error(`Failed to ${action} service: ${error.message}`);
        }
    }
    
    escapeServiceName(name) {
        return name.replace(/[^a-zA-Z0-9@._-]/g, '');
    }
}

const serviceManager = new ServiceManager();

// API Routes

// Health check
app.get('/api/health', (req, res) => {
    res.json({ 
        status: 'healthy',
        version: '2.0.0',
        uptime: process.uptime()
    });
});

// System info
app.get('/api/system/info', async (req, res) => {
    try {
        const info = await nixOps.getSystemInfo();
        res.json({ success: true, ...info });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Search packages
app.post('/api/nix/search', async (req, res) => {
    try {
        const { query } = req.body;
        
        if (!query || query.length < 2) {
            return res.status(400).json({
                success: false,
                error: 'Search query must be at least 2 characters'
            });
        }
        
        const result = await nixOps.searchPackages(query);
        res.json(result);
        
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

// Install package
app.post('/api/nix/install', async (req, res) => {
    try {
        const { package: packageName, scope = 'user' } = req.body;
        
        if (!packageName) {
            return res.status(400).json({
                success: false,
                error: 'Package name is required'
            });
        }
        
        const result = await nixOps.installPackage(packageName, scope);
        res.json(result);
        
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

// Remove package
app.post('/api/nix/remove', async (req, res) => {
    try {
        const { package: packageName } = req.body;
        
        if (!packageName) {
            return res.status(400).json({
                success: false,
                error: 'Package name is required'
            });
        }
        
        const result = await nixOps.removePackage(packageName);
        res.json(result);
        
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

// Get job status
app.get('/api/job/:jobId', (req, res) => {
    const job = jobManager.getJob(req.params.jobId);
    
    if (!job) {
        return res.status(404).json({ success: false, error: 'Job not found' });
    }
    
    res.json({
        success: true,
        job: {
            id: job.id,
            type: job.type,
            status: job.status,
            progress: job.progress,
            output: job.output,
            error: job.error,
            createdAt: job.createdAt,
            updatedAt: job.updatedAt
        }
    });
});

// Service management
app.post('/api/service/:action', async (req, res) => {
    try {
        const { action } = req.params;
        const { service } = req.body;
        
        if (!service) {
            return res.status(400).json({
                success: false,
                error: 'Service name is required'
            });
        }
        
        const result = await serviceManager.manageService(service, action);
        res.json(result);
        
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

// System diagnostics
app.post('/api/diagnose', async (req, res) => {
    try {
        const { target = 'system' } = req.body;
        
        const diagnostics = {
            nix: await nixOps.getSystemInfo(),
            services: {
                networkManager: await serviceManager.getServiceStatus('NetworkManager'),
                nix: await serviceManager.getServiceStatus('nix-daemon')
            }
        };
        
        res.json({ success: true, diagnostics });
        
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Package info with preview
app.post('/api/nix/preview', async (req, res) => {
    try {
        const { action, package: packageName, scope, service, config } = req.body;
        
        let preview = {};
        
        switch (action) {
            case 'install':
                // Get package info for preview
                const searchResult = await nixOps.searchPackages(packageName);
                const packageInfo = searchResult.packages?.[0];
                
                preview = {
                    package: packageInfo || { name: packageName },
                    downloadSize: 'Calculating...',
                    dependencies: [],
                    willModify: scope === 'system' ? ['/etc/nixos/configuration.nix'] : []
                };
                break;
                
            case 'service':
                preview = {
                    service,
                    changes: [`${service} will be configured`],
                    requiresRestart: true
                };
                break;
                
            default:
                preview = { action, details: 'Preview not available' };
        }
        
        res.json({ success: true, preview });
        
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

// Error handling middleware
app.use((err, req, res, next) => {
    logger.error('Unhandled error:', err);
    res.status(500).json({
        success: false,
        error: 'Internal server error',
        message: process.env.NODE_ENV === 'development' ? err.message : undefined
    });
});

// Start server
app.listen(config.port, () => {
    logger.info(`NixOS backend server running on port ${config.port}`);
    logger.info(`WebSocket server running on port ${config.wsPort}`);
    logger.info(`Experimental features: ${nixOps.experimentalFeatures ? 'enabled' : 'disabled'}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
    logger.info('SIGTERM received, shutting down gracefully');
    
    wss.close(() => {
        logger.info('WebSocket server closed');
    });
    
    process.exit(0);
});

module.exports = { app, nixOps, serviceManager, jobManager };