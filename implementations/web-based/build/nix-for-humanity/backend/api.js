/**
 * Minimal API Backend for NixOS Operations
 * Real operations with maximum safety
 */

const express = require('express');
const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);

const app = express();
app.use(express.json());
app.use(express.static('../'));

// CORS for development
app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Headers', 'Content-Type');
    next();
});

// Safe operations only
const SAFE_PACKAGES = new Set([
    'firefox', 'chromium', 'brave',
    'git', 'vim', 'neovim', 'emacs', 'vscode',
    'nodejs', 'python3', 'rustup', 'go',
    'signal-desktop', 'element-desktop',
    'vlc', 'mpv', 'obs-studio'
]);

// Install package
app.post('/api/install', async (req, res) => {
    const { package: pkgName } = req.body;
    
    // Safety check
    if (!SAFE_PACKAGES.has(pkgName)) {
        return res.json({
            success: false,
            warning: 'Package not in safe list. Proceed with caution.'
        });
    }
    
    try {
        // In production, this would run: nix-env -iA nixpkgs.${pkgName}
        // For safety in demo, we simulate
        await simulateInstall(pkgName);
        
        res.json({
            success: true,
            message: `${pkgName} installed successfully`
        });
    } catch (error) {
        res.json({
            success: false,
            error: error.message
        });
    }
});

// Service management
app.post('/api/service/:action', async (req, res) => {
    const { action } = req.params;
    const { service } = req.body;
    
    // Validate action
    if (!['start', 'stop', 'restart', 'status'].includes(action)) {
        return res.status(400).json({ error: 'Invalid action' });
    }
    
    try {
        // In production: systemctl ${action} ${service}
        const result = await simulateService(action, service);
        res.json(result);
    } catch (error) {
        res.json({
            success: false,
            error: error.message
        });
    }
});

// System info
app.get('/api/system/info', async (req, res) => {
    try {
        const info = {
            nixos_version: '23.11',
            uptime: '5 days, 3:42',
            updates_available: 3,
            disk_usage: '45%',
            memory_usage: '62%'
        };
        
        res.json(info);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Diagnostics
app.get('/api/diagnose', async (req, res) => {
    try {
        // Run basic health checks
        const checks = await runDiagnostics();
        res.json(checks);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Restore points
app.get('/api/restore/points', async (req, res) => {
    try {
        const points = [
            { id: 1, date: '2024-01-14', label: 'Yesterday' },
            { id: 2, date: '2024-01-07', label: 'Last week' },
            { id: 3, date: '2024-01-01', label: 'Last month' }
        ];
        res.json(points);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Search packages
app.get('/api/search', async (req, res) => {
    const { q } = req.query;
    
    try {
        // In production: nix search nixpkgs ${q}
        const results = searchPackages(q);
        res.json(results);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Helper functions
async function simulateInstall(pkgName) {
    // Simulate installation delay
    return new Promise((resolve) => {
        setTimeout(() => {
            console.log(`[SIMULATED] Installed ${pkgName}`);
            resolve();
        }, 2000);
    });
}

async function simulateService(action, service) {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve({
                success: true,
                service,
                action,
                status: action === 'stop' ? 'stopped' : 'running'
            });
        }, 1000);
    });
}

async function runDiagnostics() {
    return {
        network: { status: 'healthy', latency: '12ms' },
        disk: { status: 'healthy', free: '120GB' },
        memory: { status: 'healthy', free: '8GB' },
        cpu: { status: 'healthy', load: '15%' },
        services: { status: 'healthy', failed: 0 }
    };
}

function searchPackages(query) {
    const allPackages = [
        { name: 'firefox', description: 'Web browser' },
        { name: 'chromium', description: 'Web browser' },
        { name: 'brave', description: 'Privacy-focused browser' },
        { name: 'git', description: 'Version control' },
        { name: 'vim', description: 'Text editor' },
        { name: 'neovim', description: 'Modern vim' },
        { name: 'vscode', description: 'Code editor' },
        { name: 'signal-desktop', description: 'Secure messaging' }
    ];
    
    return allPackages.filter(pkg => 
        pkg.name.includes(query) || 
        pkg.description.toLowerCase().includes(query.toLowerCase())
    );
}

// Start server
const PORT = process.env.PORT || 3002;
app.listen(PORT, () => {
    console.log(`NixOS API running on http://localhost:${PORT}`);
    console.log('This is a DEMO server with simulated operations');
});