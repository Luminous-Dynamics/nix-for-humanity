#!/usr/bin/env bash

# 🚀 Start Nix for Humanity MVP

echo "🌟 Starting Nix for Humanity MVP..."
echo "=================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm packages are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Create storage directory if it doesn't exist
mkdir -p storage

# Start the server
echo "✨ Starting server on http://localhost:3456"
echo "📚 API docs: http://localhost:3456/api"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# For development, use nodemon if available
if [ "$NODE_ENV" = "development" ] && command -v npx &> /dev/null && npx nodemon --version &> /dev/null; then
    echo "🔄 Running in development mode with auto-reload"
    npm run dev
else
    npm start
fi