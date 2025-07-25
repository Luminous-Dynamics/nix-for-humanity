#!/usr/bin/env bash

# Nix for Humanity - Alpha Demo Script
# Simple demo launcher for the web-based implementation

set -e

echo "🌟 Nix for Humanity - Alpha Demo"
echo "================================"
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Must be run from web-based implementation directory"
    echo "   cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/implementations/web-based"
    exit 1
fi

# Check for node
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is required but not installed"
    echo "   Please install Node.js 18+ or enter a nix shell with node"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Build the project
echo "🔨 Building project..."
npm run build

# Check if build succeeded
if [ ! -d "dist" ]; then
    echo "❌ Error: Build failed - dist directory not created"
    exit 1
fi

# Kill any existing server on port 8080
if lsof -i :8080 > /dev/null 2>&1; then
    echo "🛑 Stopping existing server on port 8080..."
    kill $(lsof -t -i:8080) 2>/dev/null || true
    sleep 1
fi

# Start simple HTTP server
echo "🚀 Starting web server on http://localhost:8080"
echo ""

# Use Python's built-in server if available, otherwise use Node
if command -v python3 &> /dev/null; then
    echo "📡 Using Python HTTP server..."
    python3 -m http.server 8080 &
elif command -v python &> /dev/null; then
    echo "📡 Using Python HTTP server..."
    python -m SimpleHTTPServer 8080 &
else
    echo "📡 Using Node HTTP server..."
    npx http-server -p 8080 &
fi

SERVER_PID=$!

# Wait a moment for server to start
sleep 2

# Try to open browser
echo "🌐 Opening browser..."
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8080
elif command -v open &> /dev/null; then
    open http://localhost:8080
else
    echo "⚠️  Could not auto-open browser"
    echo "   Please open: http://localhost:8080"
fi

echo ""
echo "✅ Demo is running!"
echo ""
echo "📝 Try these commands in the interface:"
echo "   - install firefox"
echo "   - what's my ip address"
echo "   - show disk usage"
echo "   - update system"
echo "   - help"
echo ""
echo "🛑 Press Ctrl+C to stop the demo"
echo ""

# Wait for user to stop
trap "kill $SERVER_PID 2>/dev/null; echo ''; echo '👋 Demo stopped'; exit 0" INT
wait $SERVER_PID