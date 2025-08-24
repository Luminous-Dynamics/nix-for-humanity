#!/bin/bash
# Start Sacred Council Dashboard

echo "🛡️ Sacred Council Dashboard Launcher"
echo "===================================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    echo "Please install Node.js first:"
    echo "  nix-env -iA nixos.nodejs"
    exit 1
fi

# Navigate to dashboard directory
cd "$(dirname "$0")"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

# Start the dashboard
echo "🚀 Starting Sacred Council Dashboard..."
echo "   Server: http://localhost:8888"
echo "   Events: /tmp/sacred-council-events.json"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run the server
npm start