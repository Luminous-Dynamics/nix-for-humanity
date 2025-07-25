#!/usr/bin/env bash

# Test script for the integrated NixOS GUI frontend
# July 22, 2025

echo "🌟 Testing NixOS GUI Frontend Integration..."
echo "========================================="

# Check if all required files exist
echo "✓ Checking frontend files..."

FILES=(
    "frontend/index.html"
    "frontend/css/consciousness-first.css"
    "frontend/js/main.js"
    "frontend/js/websocket-client.js"
    "frontend/js/smart-suggestions.js"
    "frontend/js/health-dashboard.js"
    "frontend/js/ai-assistant.js"
    "frontend/js/package-manager.js"
)

ALL_PRESENT=true
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file MISSING"
        ALL_PRESENT=false
    fi
done

if [ "$ALL_PRESENT" = false ]; then
    echo "❌ Some files are missing. Please check the setup."
    exit 1
fi

echo ""
echo "✓ All frontend files present!"
echo ""

# Create remaining JS files that are referenced but not yet created
echo "Creating additional required JS files..."

# Service Manager
cat > frontend/js/service-manager.js << 'EOF'
// Service Manager Component
class ServiceManager {
    constructor(apiUrl) {
        this.apiUrl = apiUrl;
        this.services = [];
    }

    async init() {
        console.log('🔧 Initializing Service Manager...');
        await this.loadServices();
    }

    async loadServices() {
        try {
            const response = await fetch(`${this.apiUrl}/api/services`);
            if (response.ok) {
                this.services = await response.json();
                this.displayServices();
            }
        } catch (error) {
            console.error('Failed to load services:', error);
        }
    }

    displayServices() {
        const container = document.getElementById('services-grid');
        if (!container || this.services.length === 0) return;
        
        container.innerHTML = this.services.map(service => `
            <div class="service-card">
                <h4>${service.name}</h4>
                <p>Status: ${service.status}</p>
                <button onclick="window.nixosGUI.serviceManager.toggleService('${service.name}')">
                    ${service.status === 'active' ? 'Stop' : 'Start'}
                </button>
            </div>
        `).join('');
    }

    async toggleService(name) {
        console.log(`Toggling service: ${name}`);
        // Implementation here
    }
}
EOF

# Config Editor
cat > frontend/js/config-editor.js << 'EOF'
// Configuration Editor Component
class ConfigEditor {
    constructor(apiUrl) {
        this.apiUrl = apiUrl;
        this.originalConfig = '';
    }

    async init() {
        console.log('📝 Initializing Config Editor...');
        await this.loadConfiguration();
        this.setupEventListeners();
    }

    async loadConfiguration() {
        try {
            const response = await fetch(`${this.apiUrl}/api/configuration`);
            if (response.ok) {
                const config = await response.json();
                this.displayConfiguration(config.content);
            }
        } catch (error) {
            console.error('Failed to load configuration:', error);
        }
    }

    displayConfiguration(content) {
        const editor = document.getElementById('config-editor');
        if (editor) {
            editor.value = content;
            this.originalConfig = content;
        }
    }

    setupEventListeners() {
        const saveBtn = document.getElementById('config-save');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveConfiguration());
        }
    }

    async saveConfiguration() {
        const editor = document.getElementById('config-editor');
        if (!editor) return;
        
        console.log('Saving configuration...');
        window.updateStatus('Saving configuration...');
    }

    updateRebuildProgress(progress) {
        console.log(`Rebuild progress: ${progress}%`);
    }
}
EOF

# Create a simple test server
cat > frontend/test-server.js << 'EOF'
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 8080;

const mimeTypes = {
    '.html': 'text/html',
    '.js': 'text/javascript',
    '.css': 'text/css'
};

const server = http.createServer((req, res) => {
    console.log(`${req.method} ${req.url}`);
    
    let filePath = '.' + req.url;
    if (filePath === './') {
        filePath = './index.html';
    }

    const extname = path.extname(filePath);
    const contentType = mimeTypes[extname] || 'application/octet-stream';

    fs.readFile(filePath, (error, content) => {
        if (error) {
            if (error.code === 'ENOENT') {
                res.writeHead(404);
                res.end('File not found');
            } else {
                res.writeHead(500);
                res.end('Server error: ' + error.code);
            }
        } else {
            res.writeHead(200, { 'Content-Type': contentType });
            res.end(content, 'utf-8');
        }
    });
});

server.listen(PORT, () => {
    console.log(`🌟 Test server running at http://localhost:${PORT}/`);
    console.log('📁 Serving from:', process.cwd());
    console.log('Press Ctrl+C to stop');
});
EOF

echo "✓ Additional JS files created"
echo ""

# Start the test server
echo "Starting test server..."
cd frontend
node test-server.js &
SERVER_PID=$!

echo ""
echo "✅ Frontend test server started!"
echo ""
echo "🌐 Open http://localhost:8080 in your browser"
echo "📝 Check the browser console for any errors"
echo ""
echo "Press Ctrl+C to stop the test server"

# Wait for interrupt
trap "kill $SERVER_PID 2>/dev/null; echo ''; echo '✨ Test server stopped. We flow! 🌊'" EXIT

wait $SERVER_PID