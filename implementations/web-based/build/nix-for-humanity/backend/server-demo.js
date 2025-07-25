/**
 * NixOS GUI Backend - Demo Mode Server
 * Safe demo version with mock data
 */

const express = require('express');
const cors = require('cors');
const WebSocket = require('ws');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 7891;

// Middleware
app.use(cors({
    origin: ['http://localhost:8080', 'http://localhost:8081', 'http://127.0.0.1:8080'],
    credentials: true
}));
app.use(express.json());

// Demo mode flag
const DEMO_MODE = true;
console.log('🎭 Running in DEMO MODE - Using mock data');

// Mock data
const MOCK_PACKAGES = [
    { name: 'firefox', version: '120.0.1', description: 'A free and open source web browser' },
    { name: 'chromium', version: '119.0', description: 'Open source web browser from Google' },
    { name: 'vim', version: '9.0.1234', description: 'Vi IMproved - enhanced vi editor' },
    { name: 'neovim', version: '0.9.4', description: 'Vim-fork focused on extensibility' },
    { name: 'git', version: '2.42.0', description: 'Distributed version control system' },
    { name: 'nodejs_20', version: '20.10.0', description: 'JavaScript runtime built on V8' },
    { name: 'python311', version: '3.11.6', description: 'High-level programming language' },
    { name: 'vscode', version: '1.84.2', description: 'Visual Studio Code editor' },
    { name: 'htop', version: '3.2.2', description: 'Interactive process viewer' },
    { name: 'docker', version: '24.0.7', description: 'Container platform' }
];

const MOCK_SERVICES = [
    { name: 'nginx', status: 'active', enabled: true, description: 'High performance web server' },
    { name: 'sshd', status: 'active', enabled: true, description: 'OpenSSH secure shell daemon' },
    { name: 'postgresql', status: 'inactive', enabled: false, description: 'PostgreSQL database server' },
    { name: 'redis', status: 'inactive', enabled: false, description: 'In-memory data structure store' },
    { name: 'docker', status: 'active', enabled: true, description: 'Docker container runtime' },
    { name: 'NetworkManager', status: 'active', enabled: true, description: 'Network connection manager' }
];

// Mock installed packages
let installedPackages = ['vim', 'git', 'htop'];

// Health check
app.get('/health', (req, res) => {
    res.json({ 
        status: 'ok', 
        mode: 'demo',
        version: '2.0.0',
        timestamp: new Date().toISOString()
    });
});

// Authentication endpoints
app.post('/api/auth/login', (req, res) => {
    const { username, password } = req.body;
    
    if (username === 'demo' && password === 'demo') {
        res.json({
            success: true,
            token: 'demo-token-' + Date.now(),
            user: { 
                username: 'demo', 
                role: 'admin', 
                groups: ['wheel', 'users'],
                home: '/home/demo'
            }
        });
    } else {
        res.status(401).json({ 
            success: false, 
            message: 'Invalid credentials. Use demo/demo for demo mode.' 
        });
    }
});

app.post('/api/auth/logout', (req, res) => {
    res.json({ success: true, message: 'Logged out successfully' });
});

app.get('/api/auth/verify', (req, res) => {
    const token = req.headers.authorization?.replace('Bearer ', '');
    if (token && token.startsWith('demo-token-')) {
        res.json({ valid: true, user: { username: 'demo', role: 'admin' } });
    } else {
        res.status(401).json({ valid: false });
    }
});

// Package management endpoints
app.get('/api/packages/search', (req, res) => {
    const query = (req.query.q || '').toLowerCase();
    const filtered = MOCK_PACKAGES.filter(p => 
        p.name.toLowerCase().includes(query) || 
        p.description.toLowerCase().includes(query)
    );
    
    res.json({ 
        success: true, 
        packages: filtered,
        total: filtered.length
    });
});

app.get('/api/packages/installed', (req, res) => {
    const installed = MOCK_PACKAGES.filter(p => installedPackages.includes(p.name));
    res.json({ 
        success: true, 
        packages: installed,
        total: installed.length
    });
});

app.post('/api/packages/install', (req, res) => {
    const { package: packageName } = req.body;
    
    if (!packageName) {
        return res.status(400).json({ success: false, message: 'Package name required' });
    }
    
    // Simulate installation
    setTimeout(() => {
        if (!installedPackages.includes(packageName)) {
            installedPackages.push(packageName);
        }
        
        // Send success through WebSocket if connected
        broadcast({
            type: 'package.installed',
            data: { package: packageName, success: true }
        });
    }, 2000);
    
    res.json({ 
        success: true, 
        message: `Installing ${packageName}...`,
        jobId: 'demo-job-' + Date.now()
    });
});

app.post('/api/packages/remove', (req, res) => {
    const { package: packageName } = req.body;
    
    installedPackages = installedPackages.filter(p => p !== packageName);
    
    res.json({ 
        success: true, 
        message: `Removed ${packageName} (demo mode)`
    });
});

// Service management endpoints
app.get('/api/services', (req, res) => {
    res.json({ 
        success: true, 
        services: MOCK_SERVICES,
        total: MOCK_SERVICES.length
    });
});

app.post('/api/services/:name/start', (req, res) => {
    const service = MOCK_SERVICES.find(s => s.name === req.params.name);
    if (service) {
        service.status = 'active';
        res.json({ success: true, message: `Started ${req.params.name}` });
    } else {
        res.status(404).json({ success: false, message: 'Service not found' });
    }
});

app.post('/api/services/:name/stop', (req, res) => {
    const service = MOCK_SERVICES.find(s => s.name === req.params.name);
    if (service) {
        service.status = 'inactive';
        res.json({ success: true, message: `Stopped ${req.params.name}` });
    } else {
        res.status(404).json({ success: false, message: 'Service not found' });
    }
});

app.post('/api/services/:name/enable', (req, res) => {
    const service = MOCK_SERVICES.find(s => s.name === req.params.name);
    if (service) {
        service.enabled = true;
        res.json({ success: true, message: `Enabled ${req.params.name}` });
    } else {
        res.status(404).json({ success: false, message: 'Service not found' });
    }
});

// System information
app.get('/api/system/info', (req, res) => {
    res.json({
        success: true,
        system: {
            hostname: 'nixos-demo',
            nixosVersion: '23.11 (Tapir)',
            kernel: '6.1.63',
            uptime: '2 days, 4:32:15',
            loadAverage: [0.52, 0.58, 0.59],
            cpu: {
                model: 'Intel Core i7-9750H',
                cores: 6,
                threads: 12
            },
            memory: {
                total: 16384,
                used: 8432,
                free: 7952,
                percent: 51.5
            },
            disk: {
                total: 512000,
                used: 245760,
                free: 266240,
                percent: 48
            }
        }
    });
});

// Configuration endpoints
app.get('/api/config', (req, res) => {
    const mockConfig = `{ config, pkgs, ... }:

{
  imports = [
    ./hardware-configuration.nix
  ];

  # Boot loader
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  # Networking
  networking.hostName = "nixos-demo";
  networking.networkmanager.enable = true;

  # Services
  services.xserver.enable = true;
  services.xserver.displayManager.gdm.enable = true;
  services.xserver.desktopManager.gnome.enable = true;

  # Packages
  environment.systemPackages = with pkgs; [
    vim
    git
    firefox
  ];

  system.stateVersion = "23.11";
}`;

    res.json({ 
        success: true, 
        content: mockConfig,
        path: '/etc/nixos/configuration.nix'
    });
});

// WebSocket for real-time updates
const wss = new WebSocket.Server({ port: 7892 });

function broadcast(message) {
    wss.clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify(message));
        }
    });
}

wss.on('connection', (ws) => {
    console.log('WebSocket client connected');
    
    ws.send(JSON.stringify({
        type: 'connected',
        message: 'Connected to NixOS GUI (Demo Mode)'
    }));
    
    ws.on('close', () => {
        console.log('WebSocket client disconnected');
    });
});

// Error handling
app.use((err, req, res, next) => {
    console.error('Error:', err);
    res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: DEMO_MODE ? err.message : 'An error occurred'
    });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({
        success: false,
        message: `Endpoint ${req.path} not found`
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`✅ NixOS GUI Backend (Demo Mode) running on http://localhost:${PORT}`);
    console.log(`📡 WebSocket server running on ws://localhost:7892`);
    console.log(`\n📝 Login with: demo/demo`);
});