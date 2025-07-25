// Add this to the top of server.js after the imports

const DEMO_MODE = process.env.DEMO_MODE !== 'false';

if (DEMO_MODE) {
    console.log('🎭 Running in DEMO MODE - Using mock data');
}

// Mock data for demo mode
const MOCK_PACKAGES = [
    { name: 'firefox', version: '120.0', description: 'A free and open source web browser' },
    { name: 'vim', version: '9.0', description: 'Vi IMproved - enhanced vi editor' },
    { name: 'git', version: '2.42', description: 'Distributed version control system' },
    { name: 'nodejs', version: '20.0', description: 'JavaScript runtime built on Chrome\'s V8' },
    { name: 'python3', version: '3.11', description: 'High-level programming language' }
];

const MOCK_SERVICES = [
    { name: 'nginx', status: 'active', enabled: true, description: 'Web server' },
    { name: 'sshd', status: 'active', enabled: true, description: 'SSH daemon' },
    { name: 'postgresql', status: 'inactive', enabled: false, description: 'Database server' }
];

// Add these routes BEFORE the existing routes in server.js

// Mock Authentication
app.post('/api/auth/login', (req, res) => {
    if (DEMO_MODE) {
        const { username, password } = req.body;
        if (username === 'demo' && password === 'demo') {
            res.json({
                success: true,
                token: 'demo-token-' + Date.now(),
                user: { username: 'demo', role: 'admin', groups: ['wheel'] }
            });
        } else {
            res.status(401).json({ 
                success: false, 
                message: 'Invalid credentials. Use demo/demo' 
            });
        }
    } else {
        // Real auth would go here
        res.status(501).json({ message: 'Real auth not implemented' });
    }
});

// Mock Package Search
app.get('/api/packages/search', (req, res) => {
    if (DEMO_MODE) {
        const query = req.query.q || '';
        const filtered = MOCK_PACKAGES.filter(p => 
            p.name.includes(query) || p.description.toLowerCase().includes(query.toLowerCase())
        );
        res.json({ success: true, packages: filtered });
    } else {
        // Real search would go here
        res.status(501).json({ message: 'Real search not implemented' });
    }
});

// Mock Service List
app.get('/api/services', (req, res) => {
    if (DEMO_MODE) {
        res.json({ success: true, services: MOCK_SERVICES });
    } else {
        // Real service list would go here
        res.status(501).json({ message: 'Real services not implemented' });
    }
});

// Health Check
app.get('/health', (req, res) => {
    res.json({ 
        status: 'ok', 
        mode: DEMO_MODE ? 'demo' : 'production',
        timestamp: new Date().toISOString()
    });
});

// System Info
app.get('/api/system/info', (req, res) => {
    if (DEMO_MODE) {
        res.json({
            success: true,
            system: {
                nixosVersion: '23.11',
                hostname: 'demo-system',
                uptime: '2 days, 4:32',
                kernel: '6.1.0',
                cpu: 'Intel Core i7',
                memory: { total: 16384, used: 8192, free: 8192 },
                disk: { total: 512000, used: 256000, free: 256000 }
            }
        });
    } else {
        res.status(501).json({ message: 'Real system info not implemented' });
    }
});