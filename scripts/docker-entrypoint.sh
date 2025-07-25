#!/bin/bash
# Docker entrypoint script for NixOS GUI
# Handles different runtime modes and initialization

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🌟 NixOS GUI Container Starting...${NC}"
echo "Mode: ${1:-tauri}"
echo ""

# Function to wait for service
wait_for_service() {
    local host=$1
    local port=$2
    local service=$3
    local max_attempts=30
    local attempt=0
    
    echo -n "Waiting for $service..."
    while ! nc -z $host $port 2>/dev/null; do
        attempt=$((attempt + 1))
        if [ $attempt -gt $max_attempts ]; then
            echo -e " ${RED}Failed!${NC}"
            return 1
        fi
        echo -n "."
        sleep 1
    done
    echo -e " ${GREEN}Ready!${NC}"
    return 0
}

# Create required directories
mkdir -p /var/log/nixos-gui /var/run

# Set environment variables for supervisor
export START_TAURI=false
export START_PYTHON=false
export START_REDIS=false

# Configure based on mode
case "${1:-tauri}" in
    tauri)
        echo "Starting in Tauri mode..."
        export START_TAURI=true
        export START_REDIS=true
        
        # Check if running with display
        if [ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ]; then
            echo -e "${YELLOW}Warning: No display detected. Tauri may not start properly.${NC}"
            echo "Consider running with: docker run -e DISPLAY=:0 -v /tmp/.X11-unix:/tmp/.X11-unix"
        fi
        ;;
        
    python)
        echo "Starting in Python fallback mode..."
        export START_PYTHON=true
        export START_REDIS=true
        ;;
        
    web)
        echo "Starting in web-only mode..."
        # Only nginx will run
        ;;
        
    dev)
        echo "Starting in development mode..."
        export START_TAURI=true
        export START_PYTHON=true
        export START_REDIS=true
        
        # Enable debug logging
        export RUST_LOG=debug
        export NODE_ENV=development
        export LOG_LEVEL=debug
        ;;
        
    test)
        echo "Starting in test mode..."
        export START_PYTHON=true
        
        # Run tests and exit
        echo "Running test suite..."
        cd /app/test
        ./run-basic-tests.sh
        exit $?
        ;;
        
    *)
        echo -e "${RED}Unknown mode: $1${NC}"
        echo "Available modes: tauri, python, web, dev, test"
        exit 1
        ;;
esac

# Generate secrets if not provided
if [ -z "$JWT_SECRET" ]; then
    export JWT_SECRET=$(openssl rand -hex 32)
    echo "Generated JWT secret"
fi

if [ -z "$SESSION_SECRET" ]; then
    export SESSION_SECRET=$(openssl rand -hex 32)
    echo "Generated session secret"
fi

# Write environment to file for services
cat > /app/.env << EOF
NODE_ENV=${NODE_ENV:-production}
PORT=8080
HTTPS_PORT=8443
JWT_SECRET=$JWT_SECRET
SESSION_SECRET=$SESSION_SECRET
REDIS_URL=redis://localhost:6379
LOG_LEVEL=${LOG_LEVEL:-info}
SSL_CERT=/app/ssl/cert.pem
SSL_KEY=/app/ssl/key.pem
EOF

# Check SSL certificates
if [ ! -f /app/ssl/cert.pem ] || [ ! -f /app/ssl/key.pem ]; then
    echo "Generating SSL certificates..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /app/ssl/key.pem -out /app/ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=NixOS-GUI/CN=localhost" 2>/dev/null
fi

# Set correct permissions
chown -R nixgui:nixgui /app /var/log/nixos-gui 2>/dev/null || true

# Start supervisor
echo ""
echo -e "${GREEN}Starting services...${NC}"
echo "Access the application at:"
echo "  - https://localhost:8443 (HTTPS)"
echo "  - http://localhost:8080 (HTTP - redirects to HTTPS)"
echo ""

# Handle signals
trap 'echo "Shutting down..."; supervisorctl stop all; exit 0' SIGTERM SIGINT

# Start supervisord
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf