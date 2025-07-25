#!/usr/bin/env bash

# Build script for Nix for Humanity
echo "🏗️ Building Nix for Humanity..."

# Create dist directories
mkdir -p dist/nlp/layers
mkdir -p dist/ui
mkdir -p dist-cjs/nlp/layers
mkdir -p dist-cjs/ui

# Compile TypeScript to ES modules
echo "📦 Building ES modules..."
npx tsc

# Compile TypeScript to CommonJS for tests
echo "📦 Building CommonJS modules..."
npx tsc -p tsconfig.cjs.json

# Copy non-TypeScript files
echo "📋 Copying additional files..."
cp index.html dist/

# Create a simple dev server script
cat > serve.js << 'EOF'
const express = require('express');
const path = require('path');

const app = express();
const PORT = 3456;

// Serve static files
app.use(express.static('.'));

// Enable CORS for development
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  next();
});

// Serve index.html for root
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(PORT, () => {
  console.log(`🚀 Nix for Humanity running at http://localhost:${PORT}`);
  console.log('📝 Type "install firefox" or click the microphone to speak');
});
EOF

echo "✅ Build complete!"
echo ""
echo "To run:"
echo "  npm start"
echo ""
echo "To test:"
echo "  npm test"