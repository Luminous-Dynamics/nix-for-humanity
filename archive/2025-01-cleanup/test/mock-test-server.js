#!/usr/bin/env node

// Mock test server for running tests
// Provides basic endpoints for testing without full implementation

const express = require('express');
const https = require('https');
const fs = require('fs');
const path = require('path');
const jwt = require('jsonwebtoken');
const WebSocket = require('ws');

const app = express();
app.use(express.json());

// Mock configuration
const config = {
    httpPort: 8080,
    httpsPort: 8443,
    jwtSecret: 'test-secret',
    sslCert: path.join(__dirname, '../ssl/cert.pem'),
    sslKey: path.join(__dirname, '../ssl/key.pem')
};

// Security headers
app.use((req, res, next) => {
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('X-Frame-Options', 'DENY');
    res.setHeader('X-XSS-Protection', '1; mode=block');
    res.setHeader('Strict-Transport-Security', 'max-age=31536000');
    res.setHeader('Content-Security-Policy', "default-src 'self'");
    next();
});

// Rate limiting simulation
let requestCounts = {};
app.use((req, res, next) => {
    const ip = req.ip;
    requestCounts[ip] = (requestCounts[ip] || 0) + 1;
    
    if (requestCounts[ip] > 100) {
        return res.status(429).json({ error: 'Too many requests' });
    }
    
    next();
});

// Reset rate limits every minute
setInterval(() => {
    requestCounts = {};
}, 60000);

// Authentication middleware
function authenticate(req, res, next) {
    const token = req.headers.authorization?.replace('Bearer ', '');
    
    if (!token) {
        return res.status(401).json({ error: 'No token provided' });
    }
    
    try {
        const decoded = jwt.verify(token, config.jwtSecret);
        req.user = decoded;
        next();
    } catch (error) {
        return res.status(403).json({ error: 'Invalid token' });
    }
}

// Routes
app.get('/api/health', (req, res) => {
    res.json({ status: 'healthy', timestamp: new Date() });
});

app.post('/api/auth/login', (req, res) => {
    const { username, password } = req.body;
    
    if (!username || !password) {
        return res.status(400).json({ error: 'Missing credentials' });
    }
    
    // Accept demo credentials
    if (username === 'admin' && (password === 'testpass' || password === 'changeme')) {
        const token = jwt.sign(
            { username, role: 'admin' },
            config.jwtSecret,
            { expiresIn: '24h' }
        );
        
        res.json({ token, user: { username, role: 'admin' } });
    } else {
        res.status(401).json({ error: 'Invalid credentials' });
    }
});

app.get('/api/auth/verify', authenticate, (req, res) => {
    res.json({ valid: true, user: req.user });
});

app.post('/api/packages/search', authenticate, (req, res) => {
    const { query } = req.body;
    
    if (!query || query.length < 2) {
        return res.status(400).json({ error: 'Invalid query' });
    }
    
    // Mock search results
    res.json([
        { name: 'git', version: '2.42.0', description: 'Version control' },
        { name: 'vim', version: '9.0', description: 'Text editor' }
    ]);
});

app.get('/api/packages/installed', authenticate, (req, res) => {
    res.json([
        { name: 'nodejs', version: '20.5.0' },
        { name: 'nixos-gui', version: '0.1.0' }
    ]);
});

app.get('/api/services', authenticate, (req, res) => {
    res.json([
        { name: 'nginx', status: 'active' },
        { name: 'sshd', status: 'inactive' }
    ]);
});

app.get('/api/configuration', authenticate, (req, res) => {
    res.json({
        content: '{ config, pkgs, ... }: { system.stateVersion = "25.11"; }'
    });
});

app.post('/api/configuration/validate', authenticate, (req, res) => {
    res.json({ valid: true });
});

app.get('/api/system/stats', authenticate, (req, res) => {
    res.json({
        cpu: { usage: 25.5, cores: 4 },
        memory: { total: 8000000000, used: 4000000000 },
        disk: { total: 100000000000, used: 50000000000 },
        network: { rx: 1024, tx: 512 }
    });
});

// Serve static files
app.use(express.static(path.join(__dirname, '../frontend')));

// Generate SSL certificates if needed
function ensureSSLCerts() {
    const sslDir = path.dirname(config.sslCert);
    
    if (!fs.existsSync(sslDir)) {
        fs.mkdirSync(sslDir, { recursive: true });
    }
    
    if (!fs.existsSync(config.sslCert) || !fs.existsSync(config.sslKey)) {
        console.log('Generating SSL certificates...');
        const { execSync } = require('child_process');
        execSync(`openssl req -x509 -newkey rsa:2048 -keyout ${config.sslKey} -out ${config.sslCert} -days 365 -nodes -subj "/CN=localhost"`);
    }
}

// Start servers
ensureSSLCerts();

// HTTPS server
const httpsOptions = {
    key: fs.readFileSync(config.sslKey),
    cert: fs.readFileSync(config.sslCert)
};

const httpsServer = https.createServer(httpsOptions, app);

// WebSocket server
const wss = new WebSocket.Server({ server: httpsServer });

wss.on('connection', (ws) => {
    console.log('WebSocket client connected');
    
    // Send periodic stats
    const interval = setInterval(() => {
        ws.send(JSON.stringify({
            type: 'system-stats',
            data: {
                cpu: { usage: Math.random() * 100 },
                timestamp: Date.now()
            }
        }));
    }, 5000);
    
    ws.on('close', () => {
        clearInterval(interval);
        console.log('WebSocket client disconnected');
    });
});

httpsServer.listen(config.httpsPort, () => {
    console.log(`🔒 Mock test server running on https://localhost:${config.httpsPort}`);
});

// HTTP redirect server
const http = require('http');
http.createServer((req, res) => {
    res.writeHead(301, { Location: `https://${req.headers.host}${req.url}` });
    res.end();
}).listen(config.httpPort, () => {
    console.log(`🔄 HTTP redirect server on http://localhost:${config.httpPort}`);
});

console.log('✅ Mock test server ready for testing');