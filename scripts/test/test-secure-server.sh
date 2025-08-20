#!/usr/bin/env bash

# Test script for the secure NixOS GUI server
# July 22, 2025

echo "🔐 Testing Secure NixOS GUI Server..."
echo "===================================="

# Check dependencies
echo "✓ Checking dependencies..."
MISSING_DEPS=()

command -v node >/dev/null 2>&1 || MISSING_DEPS+=("node")
command -v npm >/dev/null 2>&1 || MISSING_DEPS+=("npm")
command -v openssl >/dev/null 2>&1 || MISSING_DEPS+=("openssl")

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    echo "❌ Missing dependencies: ${MISSING_DEPS[*]}"
    echo "Please install them first."
    exit 1
fi

# Generate SSL certificates if needed
if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
    echo ""
    echo "📜 SSL certificates not found. Generating..."
    ./scripts/generate-ssl.sh
fi

# Install npm dependencies if needed
if [ ! -d "node_modules" ]; then
    echo ""
    echo "📦 Installing dependencies..."
    npm install express compression helmet cors socket.io bcrypt jsonwebtoken sqlite3 sqlite redis express-rate-limit
fi

# Create test environment variables
cat > .env.test << EOF
NODE_ENV=development
HTTP_PORT=8080
HTTPS_PORT=8443
WS_PORT=8091
JWT_SECRET=test-secret-change-in-production
SESSION_SECRET=test-session-secret-change-in-production
SSL_CERT=ssl/cert.pem
SSL_KEY=ssl/key.pem
EOF

# Create package-service stub
mkdir -p backend/src/services
cat > backend/src/services/package-service-cached.js << 'EOF'
class CachedPackageService {
    async search(query) {
        // Mock search results
        return [
            { name: 'git', version: '2.42.0', description: 'Distributed version control system' },
            { name: 'vim', version: '9.0', description: 'Vi IMproved, a programmer text editor' },
            { name: 'firefox', version: '115.0', description: 'Mozilla Firefox web browser' }
        ].filter(pkg => pkg.name.includes(query));
    }
    
    async listInstalled() {
        return [
            { name: 'nixos-gui', version: '0.1.0' },
            { name: 'nodejs', version: '20.5.0' }
        ];
    }
    
    async install(packageName) {
        return { success: true, message: `Mock install of ${packageName}` };
    }
    
    async remove(packageName) {
        return { success: true, message: `Mock remove of ${packageName}` };
    }
}

module.exports = CachedPackageService;
EOF

# Create other service stubs
cat > backend/src/services/config-service.js << 'EOF'
class ConfigService {
    async getConfiguration() {
        return `{ config, pkgs, ... }:
{
  imports = [ ./hardware-configuration.nix ];
  
  boot.loader.systemd-boot.enable = true;
  
  networking.hostName = "nixos-sacred";
  
  environment.systemPackages = with pkgs; [
    vim
    git
    firefox
  ];
  
  system.stateVersion = "25.11";
}`;
    }
    
    async validate(content) {
        return { valid: true };
    }
    
    async save(content) {
        return { success: true, message: 'Configuration saved (mock)' };
    }
}

module.exports = ConfigService;
EOF

cat > backend/src/services/service-manager.js << 'EOF'
class ServiceManager {
    async listServices() {
        return [
            { name: 'nginx', status: 'active', description: 'Web server' },
            { name: 'sshd', status: 'inactive', description: 'SSH daemon' },
            { name: 'nixos-gui', status: 'active', description: 'NixOS GUI service' }
        ];
    }
    
    async startService(name) {
        return { success: true, message: `Started ${name} (mock)` };
    }
    
    async stopService(name) {
        return { success: true, message: `Stopped ${name} (mock)` };
    }
    
    async restartService(name) {
        return { success: true, message: `Restarted ${name} (mock)` };
    }
}

module.exports = ServiceManager;
EOF

# Start the server
echo ""
echo "🚀 Starting secure server..."
echo ""
echo "📝 Server Details:"
echo "   HTTP:  http://localhost:8080 (redirects to HTTPS)"
echo "   HTTPS: https://localhost:8443"
echo "   WS:    wss://localhost:8443"
echo ""
echo "🔐 Login Credentials:"
echo "   Username: admin"
echo "   Password: any-password (demo mode)"
echo ""
echo "⚠️  Note: Your browser will warn about the self-signed certificate."
echo "   This is normal for development. Click 'Advanced' and 'Proceed'."
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server with environment variables
export $(cat .env.test | xargs)
node backend/src/secure-server.js