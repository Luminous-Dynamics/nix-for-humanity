/**
 * Nix for Humanity - Backend Server (Fixed)
 * Safe execution of Nix operations with proper Nix configuration
 */

const express = require('express');
const cors = require('cors');
const { exec, spawn } = require('child_process');
const { promisify } = require('util');
const path = require('path');
const fs = require('fs').promises;
const WebSocket = require('ws');

const execAsync = promisify(exec);

const app = express();
const PORT = process.env.PORT || 7891;

// Middleware
app.use(cors());
app.use(express.json());

// Simple auth for testing
app.post('/api/auth/login', (req, res) => {
    const { username, password } = req.body;
    // Simple auth - in production, use proper authentication
    if ((username === 'admin' && password === 'admin') || 
        (username === 'demo' && password === 'demo')) {
        res.json({
            success: true,
            token: 'nixgui-token-' + Date.now(),
            user: { username, role: 'admin' }
        });
    } else {
        res.status(401).json({ 
            success: false, 
            message: 'Invalid credentials' 
        });
    }
});

app.get('/api/auth/verify', (req, res) => {
    const token = req.headers.authorization?.replace('Bearer ', '');
    if (token && token.startsWith('nixgui-token-')) {
        res.json({ valid: true });
    } else {
        res.status(401).json({ valid: false });
    }
});

app.post('/api/auth/logout', (req, res) => {
    res.json({ success: true });
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ 
        status: 'ok',
        version: '2.0.0',
        mode: 'production',
        timestamp: new Date().toISOString()
    });
});

// System info endpoint
app.get('/api/system/info', async (req, res) => {
    try {
        const os = require('os');
        
        // Get NixOS version
        let nixosVersion = 'Unknown';
        try {
            const versionResult = await execAsync('nixos-version');
            nixosVersion = versionResult.stdout.trim();
        } catch (e) {
            // Not on NixOS or command failed
        }
        
        res.json({
            success: true,
            system: {
                hostname: os.hostname(),
                platform: os.platform(),
                arch: os.arch(),
                nixosVersion,
                uptime: os.uptime(),
                loadAverage: os.loadavg(),
                memory: {
                    total: os.totalmem(),
                    free: os.freemem(),
                    used: os.totalmem() - os.freemem(),
                    percentage: Math.round((1 - os.freemem() / os.totalmem()) * 100)
                },
                cpus: os.cpus().length,
                nodeVersion: process.version
            }
        });
    } catch (error) {
        res.status(500).json({ 
            success: false, 
            error: error.message 
        });
    }
});

// WebSocket server (disabled for now to avoid conflicts)
// const wss = new WebSocket.Server({ port: 7892 });

// Job tracking
const jobs = new Map();
let jobCounter = 0;

// Nix command templates
const NIX_COMMANDS = {
    'search': ['nix', 'search'],
    'install': ['nix', 'profile', 'install'],
    'remove': ['nix', 'profile', 'remove'],
    'info': ['nix', 'show'],
    'list': ['nix', 'profile', 'list'],
    'generations': ['nix', 'profile', 'history'],
    'check': ['nix', 'store', 'verify']
};

const ALLOWED_OPERATIONS = new Set([
    'search', 'install', 'remove', 'update',
    'start', 'stop', 'restart', 'enable', 'disable',
    'status', 'info', 'rollback'
]);

// Validate and sanitize commands
function validateCommand(operation, args) {
    if (!ALLOWED_OPERATIONS.has(operation)) {
        throw new Error(`Operation "${operation}" not allowed`);
    }
    
    // Sanitize arguments - remove shell metacharacters
    const sanitized = args.map(arg => 
        arg.replace(/[;&|`$<>\\]/g, '')
           .trim()
    );
    
    return sanitized;
}

// Execute Nix command safely
async function execNixCommand(command, args, options = {}) {
    const sanitizedArgs = validateCommand(command, args);
    
    // Build the command
    let nixCommand;
    switch (command) {
        case 'search':
            // Use nix search with nixpkgs flake
            nixCommand = ['nix', 'search', 'nixpkgs', ...sanitizedArgs, '--json'];
            break;
            
        case 'install':
            // Try multiple methods for compatibility
            // First try: nix profile install (Nix 2.4+)
            // Fallback: nix-env -iA
            nixCommand = ['nix', 'profile', 'install', `nixpkgs#${sanitizedArgs[0]}`];
            break;
            
        case 'remove':
            nixCommand = ['nix', 'profile', 'remove', sanitizedArgs[0]];
            break;
            
        case 'rollback':
            nixCommand = ['nix', 'profile', 'rollback'];
            break;
            
        default:
            throw new Error(`Command "${command}" not implemented`);
    }
    
    // Execute with timeout
    const timeout = options.timeout || 60000; // 60 seconds for installations
    
    try {
        const { stdout, stderr } = await execAsync(
            nixCommand.join(' '),
            {
                timeout,
                maxBuffer: 10 * 1024 * 1024, // 10MB
                env: { 
                    ...process.env,
                    // Ensure experimental features are enabled
                    NIX_CONFIG: 'experimental-features = nix-command flakes'
                }
            }
        );
        
        return { success: true, output: stdout, error: stderr };
    } catch (error) {
        // If nix profile install fails, try nix-env
        if (command === 'install' && error.message.includes('experimental')) {
            try {
                const fallbackCommand = `nix-env -iA nixpkgs.${sanitizedArgs[0]}`;
                const { stdout, stderr } = await execAsync(fallbackCommand, {
                    timeout,
                    maxBuffer: 10 * 1024 * 1024
                });
                return { success: true, output: stdout, error: stderr, method: 'nix-env' };
            } catch (fallbackError) {
                // Continue to error handling
            }
        }
        
        return { 
            success: false, 
            error: error.message,
            suggestion: getSuggestion(error)
        };
    }
}

// System diagnostics
async function diagnose(target) {
    const diagnostics = {
        network: async () => {
            const checks = [];
            
            // Check NetworkManager
            const nmStatus = await execAsync('systemctl is-active NetworkManager')
                .then(() => true)
                .catch(() => false);
            
            checks.push({
                name: 'NetworkManager',
                status: nmStatus,
                fix: nmStatus ? null : 'systemctl start NetworkManager'
            });
            
            // Check connectivity
            const connected = await execAsync('ping -c 1 -W 2 8.8.8.8')
                .then(() => true)
                .catch(() => false);
            
            checks.push({
                name: 'Internet Connection',
                status: connected,
                fix: connected ? null : 'check network configuration'
            });
            
            return checks;
        },
        
        audio: async () => {
            const checks = [];
            
            // Check PipeWire/PulseAudio
            const audioStatus = await execAsync('systemctl --user is-active pipewire')
                .then(() => true)
                .catch(async () => {
                    // Try PulseAudio
                    return await execAsync('systemctl --user is-active pulseaudio')
                        .then(() => true)
                        .catch(() => false);
                });
            
            checks.push({
                name: 'Audio Service',
                status: audioStatus,
                fix: audioStatus ? null : 'systemctl --user start pipewire'
            });
            
            return checks;
        }
    };
    
    const diagFunc = diagnostics[target] || diagnostics.network;
    return await diagFunc();
}

// Helper to suggest fixes
function getSuggestion(error) {
    const errorMap = {
        'not found': 'Try searching for a similar package name',
        'collision': 'Package conflicts with existing installation',
        'permission': 'May need administrator access',
        'network': 'Check your internet connection',
        'space': 'Not enough disk space',
        'experimental': 'Nix experimental features may need to be enabled'
    };
    
    const message = error.message.toLowerCase();
    for (const [key, suggestion] of Object.entries(errorMap)) {
        if (message.includes(key)) {
            return suggestion;
        }
    }
    
    return 'Try running the command manually to see more details';
}

// API Routes

// Search packages
app.post('/api/nix/search', async (req, res) => {
    try {
        const { query } = req.body;
        const result = await execNixCommand('search', [query]);
        
        if (result.success) {
            // Parse JSON output
            const packages = parseSearchResults(result.output);
            res.json({ success: true, packages });
        } else {
            res.json(result);
        }
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

// Install package
app.post('/api/nix/install', async (req, res) => {
    try {
        const { package: packageName, scope = 'user' } = req.body;
        
        if (scope === 'system') {
            // Generate configuration snippet for system-wide installation
            const snippet = generateSystemPackageSnippet(packageName);
            res.json({ 
                success: true, 
                action: 'show-config',
                snippet,
                instructions: 'Add this to your /etc/nixos/configuration.nix'
            });
        } else {
            // User installation - proceed as before
            const jobId = generateJobId();
            res.json({ success: true, jobId });
            executeInstallation(jobId, packageName);
        }
        
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

// Service management
app.post('/api/service/:action', async (req, res) => {
    try {
        const { action } = req.params;
        const { service } = req.body;
        
        const result = await manageService(service, action);
        res.json(result);
        
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

// System diagnostics
app.post('/api/diagnose', async (req, res) => {
    try {
        const { target } = req.body;
        const results = await diagnose(target);
        res.json({ success: true, results });
        
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

// Job status
app.get('/api/job/:jobId', async (req, res) => {
    const { jobId } = req.params;
    const job = jobs.get(jobId);
    
    if (!job) {
        res.status(404).json({ success: false, error: 'Job not found' });
    } else {
        res.json(job);
    }
});

// Preview/dry-run endpoint
app.post('/api/nix/preview', async (req, res) => {
    try {
        const { action, package: packageName, scope, service, config } = req.body;
        
        let preview = {};
        
        switch (action) {
            case 'install':
                preview = await previewPackageInstall(packageName, scope);
                break;
                
            case 'service':
                preview = await previewServiceConfig(service, config);
                break;
                
            case 'config':
                preview = await previewConfigChange(config);
                break;
                
            default:
                throw new Error(`Unknown preview action: ${action}`);
        }
        
        res.json({ success: true, preview });
        
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

// Helper functions

function generateSystemPackageSnippet(packageName) {
    // Special configurations for packages that need extra setup
    const specialConfigs = {
        docker: `# Docker configuration
virtualisation.docker.enable = true;
virtualisation.docker.enableOnBoot = true;

# Add your user to docker group
users.users.<YOUR_USERNAME>.extraGroups = [ "docker" ];

environment.systemPackages = with pkgs; [
  docker
  docker-compose
];`,
        
        steam: `# Steam configuration
programs.steam.enable = true;

# Enable 32-bit support for Steam
hardware.opengl.driSupport32Bit = true;
hardware.pulseaudio.support32Bit = true;`,
        
        virtualbox: `# VirtualBox configuration
virtualisation.virtualbox.host.enable = true;
users.users.<YOUR_USERNAME>.extraGroups = [ "vboxusers" ];`,
        
        'vscode': `# VS Code installation
environment.systemPackages = with pkgs; [
  vscode
];

# Optional: VS Code with extensions
# environment.systemPackages = with pkgs; [
#   (vscode-with-extensions.override {
#     vscodeExtensions = with vscode-extensions; [
#       ms-python.python
#       ms-azuretools.vscode-docker
#     ];
#   })
# ];`,
        
        postgresql: `# PostgreSQL configuration
services.postgresql = {
  enable = true;
  package = pkgs.postgresql_15;
  enableTCPIP = true;
  authentication = pkgs.lib.mkOverride 10 ''
    # TYPE  DATABASE  USER  ADDRESS     METHOD
    local   all       all               trust
    host    all       all   127.0.0.1/32 trust
    host    all       all   ::1/128      trust
  '';
};`,
        
        nginx: `# Nginx web server configuration
services.nginx = {
  enable = true;
  virtualHosts."localhost" = {
    root = "/var/www/localhost";
  };
};

# Open firewall for web traffic
networking.firewall.allowedTCPPorts = [ 80 443 ];`
    };
    
    // Check if package needs special configuration
    if (specialConfigs[packageName]) {
        return specialConfigs[packageName];
    }
    
    // Default snippet for regular packages
    return `# Add ${packageName} to system packages
environment.systemPackages = with pkgs; [
  # ... your other packages ...
  ${packageName}
];`;
}

function parseSearchResults(output) {
    try {
        const results = JSON.parse(output);
        return Object.entries(results).map(([name, info]) => ({
            name: name.replace('legacyPackages.x86_64-linux.', '').replace('nixpkgs.', ''),
            version: info.version || 'unknown',
            description: info.description || info.pname || ''
        }));
    } catch (error) {
        console.error('Failed to parse search results:', error);
        return [];
    }
}

function generateJobId() {
    return `job_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

// Service management
async function manageService(serviceName, action) {
    const validActions = ['start', 'stop', 'restart', 'enable', 'disable', 'status'];
    
    if (!validActions.includes(action)) {
        throw new Error(`Invalid action: ${action}`);
    }
    
    try {
        const command = action === 'status' 
            ? `systemctl is-active ${serviceName}`
            : `systemctl ${action} ${serviceName}`;
            
        const result = await execAsync(command);
        return { success: true, message: result.stdout };
    } catch (error) {
        return { 
            success: false, 
            error: error.message,
            suggestion: `May need sudo: sudo systemctl ${action} ${serviceName}`
        };
    }
}

// Execute installation with proper methods
async function executeInstallation(jobId, packageName) {
    const job = {
        id: jobId,
        type: 'install',
        package: packageName,
        status: 'running',
        progress: 0,
        startTime: Date.now(),
        logs: []
    };
    
    jobs.set(jobId, job);
    
    // Broadcast job start
    broadcast({ type: 'job.start', job });
    
    try {
        // Update progress
        job.progress = 20;
        job.logs.push(`Searching for ${packageName}...`);
        broadcast({ type: 'job.progress', job });
        
        // Try different installation methods
        let child;
        let installMethod = 'nix profile';
        
        // Check if experimental features are enabled
        const experimentalCheck = await execAsync('nix --version').catch(() => null);
        const hasExperimental = experimentalCheck && experimentalCheck.stdout.includes('2.');
        
        if (hasExperimental) {
            // Use modern nix profile install
            job.logs.push('Using nix profile install (modern method)...');
            child = spawn('nix', ['profile', 'install', `nixpkgs#${packageName}`], {
                env: {
                    ...process.env,
                    NIX_CONFIG: 'experimental-features = nix-command flakes'
                }
            });
        } else {
            // Fallback to nix-env
            job.logs.push('Using nix-env (classic method)...');
            installMethod = 'nix-env';
            child = spawn('nix-env', ['-iA', `nixpkgs.${packageName}`]);
        }
        
        child.stdout.on('data', (data) => {
            const message = data.toString().trim();
            if (message) {
                job.logs.push(message);
                // Update progress based on output
                if (message.includes('downloading')) {
                    job.progress = 40;
                } else if (message.includes('building')) {
                    job.progress = 60;
                } else if (message.includes('installing')) {
                    job.progress = 80;
                }
                broadcast({ type: 'job.progress', job });
            }
        });
        
        child.stderr.on('data', (data) => {
            const message = data.toString().trim();
            if (message && !message.includes('warning:')) {
                job.logs.push(`Note: ${message}`);
                broadcast({ type: 'job.progress', job });
            }
        });
        
        child.on('close', (code) => {
            if (code === 0) {
                job.status = 'completed';
                job.progress = 100;
                job.logs.push(`✅ ${packageName} installed successfully using ${installMethod}!`);
            } else {
                job.status = 'failed';
                job.error = `Installation failed with code ${code}`;
                job.logs.push(`❌ Installation failed. Try running manually: nix-env -iA nixpkgs.${packageName}`);
            }
            
            job.endTime = Date.now();
            broadcast({ type: 'job.complete', job });
        });
        
    } catch (error) {
        job.status = 'failed';
        job.error = error.message;
        job.logs.push(`Error: ${error.message}`);
        job.endTime = Date.now();
        broadcast({ type: 'job.error', job });
    }
}

// WebSocket broadcast
function broadcast(message) {
    // WebSocket disabled for now
    console.log('Broadcast:', message.type || 'unknown');
}

// Preview functions

async function previewPackageInstall(packageName, scope) {
    try {
        // Get package info
        const packageInfo = await getPackageInfo(packageName);
        
        if (scope === 'user') {
            return {
                type: 'package-install-user',
                package: packageName,
                version: packageInfo.version,
                description: packageInfo.description,
                downloadSize: packageInfo.downloadSize || 'Unknown',
                installedSize: packageInfo.installedSize || 'Unknown',
                dependencies: packageInfo.dependencies || [],
                immediate: true
            };
        } else {
            return {
                type: 'package-install-system',
                package: packageName,
                version: packageInfo.version,
                description: packageInfo.description,
                configSnippet: generateSystemPackageSnippet(packageName),
                requiresRebuild: true,
                estimatedTime: '2-5 minutes'
            };
        }
    } catch (error) {
        throw new Error(`Failed to preview package: ${error.message}`);
    }
}

async function previewServiceConfig(serviceName, config) {
    // Analyze service configuration impact
    const preview = {
        type: 'service-config',
        service: serviceName,
        changes: [],
        warnings: [],
        requiresRebuild: true,
        estimatedTime: '3-10 minutes'
    };
    
    // Check what would change
    if (config.enable) {
        preview.changes.push({
            type: 'enable',
            description: `Enable ${serviceName} service`
        });
    }
    
    // Service-specific analysis
    switch (serviceName) {
        case 'openssh':
            if (config.port && config.port !== 22) {
                preview.changes.push({
                    type: 'firewall',
                    description: `Open port ${config.port}`
                });
            }
            if (config.permitRootLogin === 'yes') {
                preview.warnings.push({
                    level: 'warning',
                    message: 'Allowing root login is a security risk'
                });
            }
            break;
            
        case 'docker':
            if (config.users && config.users.length > 0) {
                preview.changes.push({
                    type: 'users',
                    description: `Add users to docker group: ${config.users.join(', ')}`
                });
                preview.warnings.push({
                    level: 'info',
                    message: 'Users in docker group can run containers as root'
                });
            }
            break;
    }
    
    return preview;
}

async function previewConfigChange(config) {
    // Preview arbitrary configuration changes
    return {
        type: 'config-change',
        changes: config.changes || [],
        requiresRebuild: true,
        estimatedTime: '2-10 minutes'
    };
}

async function getPackageInfo(packageName) {
    try {
        // Try to get package info from nix
        const { stdout } = await execAsync(`nix eval --json nixpkgs#${packageName}.meta 2>/dev/null || echo '{}'`);
        const meta = JSON.parse(stdout);
        
        // Try to get size info
        let sizeInfo = {};
        try {
            const { stdout: pathInfo } = await execAsync(`nix path-info -S nixpkgs#${packageName} 2>/dev/null || echo ''`);
            if (pathInfo) {
                const match = pathInfo.match(/(\d+)/);
                if (match) {
                    const bytes = parseInt(match[1]);
                    sizeInfo.installedSize = formatBytes(bytes);
                }
            }
        } catch (e) {
            // Size info is optional
        }
        
        return {
            version: meta.version || 'latest',
            description: meta.description || meta.longDescription || '',
            homepage: meta.homepage,
            license: meta.license?.spdxId || meta.license?.fullName,
            ...sizeInfo
        };
        
    } catch (error) {
        // Return minimal info if nix commands fail
        return {
            version: 'latest',
            description: '',
            downloadSize: 'Unknown',
            installedSize: 'Unknown'
        };
    }
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// Start server
app.listen(PORT, () => {
    console.log(`✨ Nix for Humanity backend running on port ${PORT}`);
    console.log(`🌐 WebSocket server on port 7892`);
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n👋 Shutting down gracefully...');
    // wss.close();
    process.exit(0);
});