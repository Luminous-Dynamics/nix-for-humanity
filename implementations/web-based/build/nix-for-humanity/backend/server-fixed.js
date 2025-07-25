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

// WebSocket server
const wss = new WebSocket.Server({ port: 7892 });

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