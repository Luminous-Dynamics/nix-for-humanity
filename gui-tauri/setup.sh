#!/bin/bash
# Setup script for Tauri GUI

echo "🎨 Setting up Luminous Nix GUI with Tauri"
echo "=========================================="

# Check if Rust is installed
if ! command -v cargo &> /dev/null; then
    echo "❌ Rust not installed. Please install Rust first:"
    echo "   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm not installed. Please install Node.js first"
    exit 1
fi

# Install Tauri CLI if not installed
if ! command -v cargo-tauri &> /dev/null; then
    echo "📦 Installing Tauri CLI..."
    cargo install tauri-cli
fi

# Create Tauri project structure
echo "🏗️ Creating project structure..."
mkdir -p src-tauri
mkdir -p src
mkdir -p public

# Initialize package.json
echo "📋 Creating package.json..."
cat > package.json << 'EOF'
{
  "name": "luminous-nix-gui",
  "version": "0.1.0",
  "description": "Consciousness-first, AI-testable GUI for Luminous Nix",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "tauri": "tauri",
    "tauri-dev": "tauri dev",
    "tauri-build": "tauri build"
  },
  "dependencies": {
    "solid-js": "^1.8.0",
    "@tauri-apps/api": "^2.0.0",
    "valtio": "^1.13.0"
  },
  "devDependencies": {
    "@tauri-apps/cli": "^2.0.0",
    "vite": "^5.0.0",
    "vite-plugin-solid": "^2.10.0",
    "typescript": "^5.3.0"
  }
}
EOF

# Install dependencies
echo "📦 Installing dependencies..."
npm install

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Run 'npm run tauri-dev' to start development"
echo "  2. Edit src/App.tsx to build your interface"
echo "  3. Run 'npm run tauri-build' to create production build"