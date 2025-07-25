/**
 * Nix for Humanity - Backend Server
 * Safe execution of Nix operations with consciousness
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
app.use(express.static(path.join(__dirname, '..')));

// WebSocket for real-time updates
const wss = new WebSocket.Server({ port: 7892 });

// Safety configuration
const SAFE_COMMANDS = {
    'search': ['nix', 'search'],
    'info': ['nix', 'show'],
    'list': ['nix-env', '-q'],
    'generations': ['nix-env', '--list-generations'],
    'check': ['nix-store', '--verify', '--check-contents']
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
            nixCommand = ['nix', 'search', 'nixpkgs', ...sanitizedArgs, '--json'];
            break;
            
        case 'install':
            // Use home-manager or nix-env for user installs
            nixCommand = ['nix-env', '-iA', `nixpkgs.${sanitizedArgs[0]}`];
            break;
            
        case 'remove':
            nixCommand = ['nix-env', '-e', sanitizedArgs[0]];
            break;
            
        case 'rollback':
            nixCommand = ['nix-env', '--rollback'];
            break;
            
        default:
            throw new Error(`Command "${command}" not implemented`);
    }
    
    // Execute with timeout
    const timeout = options.timeout || 30000;
    
    try {
        const { stdout, stderr } = await execAsync(
            nixCommand.join(' '),
            {
                timeout,
                maxBuffer: 10 * 1024 * 1024, // 10MB
                env: { ...process.env, NIX_PATH: process.env.NIX_PATH || 'nixpkgs=/nix/var/nix/profiles/per-user/root/channels/nixos' }
            }
        );
        
        return { success: true, output: stdout, error: stderr };
    } catch (error) {
        return { 
            success: false, 
            error: error.message,
            suggestion: getSuggestion(error)
        };
    }
}

// Service management
async function manageService(service, action) {
    const validActions = ['start', 'stop', 'restart', 'enable', 'disable', 'status'];
    
    if (!validActions.includes(action)) {
        throw new Error(`Invalid service action: ${action}`);
    }
    
    // Sanitize service name
    const safeService = service.replace(/[^a-zA-Z0-9-_.]/g, '');
    
    try {
        const { stdout } = await execAsync(
            `systemctl ${action} ${safeService}`,
            { timeout: 10000 }
        );
        
        return { success: true, output: stdout };
    } catch (error) {
        // Try with sudo if permission denied
        if (error.message.includes('permission')) {
            return {
                success: false,
                error: 'Administrator permission required',
                needsSudo: true
            };
        }
        
        return { success: false, error: error.message };
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
        'space': 'Not enough disk space'
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
        const { package: packageName } = req.body;
        const jobId = generateJobId();
        
        // Send immediate response
        res.json({ success: true, jobId });
        
        // Execute installation asynchronously
        executeInstallation(jobId, packageName);
        
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

// Helper functions

function parseSearchResults(output) {
    try {
        const results = JSON.parse(output);
        return Object.entries(results).map(([name, info]) => ({
            name: name.replace('legacyPackages.x86_64-linux.', '').replace('nixpkgs.', ''),
            version: info.version || 'unknown',
            description: info.description || ''
        }));
    } catch {
        return [];
    }
}

function generateJobId() {
    return `job_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

// Job tracking
const jobs = new Map();

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
        
        // Execute installation
        const child = spawn('nix-env', ['-iA', `nixpkgs.${packageName}`]);
        
        child.stdout.on('data', (data) => {
            const message = data.toString();
            job.logs.push(message);
            job.progress = Math.min(90, job.progress + 10);
            broadcast({ type: 'job.progress', job });
        });
        
        child.stderr.on('data', (data) => {
            const message = data.toString();
            if (!message.includes('warning:')) {
                job.logs.push(`Error: ${message}`);
            }
        });
        
        child.on('close', (code) => {
            if (code === 0) {
                job.status = 'completed';
                job.progress = 100;
                job.logs.push(`✅ ${packageName} installed successfully!`);
            } else {
                job.status = 'failed';
                job.error = `Installation failed with code ${code}`;
            }
            
            job.endTime = Date.now();
            broadcast({ type: 'job.complete', job });
        });
        
    } catch (error) {
        job.status = 'failed';
        job.error = error.message;
        job.endTime = Date.now();
        broadcast({ type: 'job.error', job });
    }
}

// WebSocket broadcast
function broadcast(message) {
    wss.clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify(message));
        }
    });
}

// Start server
app.listen(PORT, () => {
    console.log(`✨ Nix for Humanity backend running on port ${PORT}`);
    console.log(`🌐 WebSocket server on port 7892`);
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n👋 Shutting down gracefully...');
    wss.close();
    process.exit(0);
});