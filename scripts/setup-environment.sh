#!/usr/bin/env bash

# NixOS GUI Environment Setup Script
# Sets up complete development environment

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 NixOS GUI Environment Setup${NC}"
echo "=============================="
echo ""

# Function to check command availability
check_command() {
    if command -v $1 >/dev/null 2>&1; then
        echo -e "${GREEN}✅ $1 is installed${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 is not installed${NC}"
        return 1
    fi
}

# Function to create directory if it doesn't exist
ensure_dir() {
    if [ ! -d "$1" ]; then
        mkdir -p "$1"
        echo -e "${GREEN}✅ Created directory: $1${NC}"
    fi
}

# Check environment
echo -e "${BLUE}Checking environment...${NC}"
echo ""

HAS_NODE=false
HAS_PYTHON=false
HAS_NIX=false

check_command "node" && HAS_NODE=true
check_command "npm" 
check_command "python3" && HAS_PYTHON=true
check_command "pip3" || check_command "pip"
check_command "nix-shell" && HAS_NIX=true
check_command "openssl"
check_command "git"
check_command "make"

echo ""

# Create necessary directories
echo -e "${BLUE}Creating project directories...${NC}"
ensure_dir "ssl"
ensure_dir "logs"
ensure_dir "data"
ensure_dir "test/results"
ensure_dir "frontend/js"
ensure_dir "frontend/css"
ensure_dir "backend/src"
ensure_dir "scripts"

# Generate SSL certificates
echo ""
echo -e "${BLUE}Setting up SSL certificates...${NC}"
if [ ! -f ssl/cert.pem ] || [ ! -f ssl/key.pem ]; then
    echo "Generating self-signed SSL certificate..."
    openssl req -x509 -newkey rsa:2048 \
        -keyout ssl/key.pem -out ssl/cert.pem \
        -days 365 -nodes \
        -subj "/C=US/ST=State/L=City/O=NixOS-GUI/CN=localhost"
    echo -e "${GREEN}✅ SSL certificates generated${NC}"
else
    echo -e "${GREEN}✅ SSL certificates already exist${NC}"
fi

# Create .env file
echo ""
echo -e "${BLUE}Setting up environment variables...${NC}"
if [ ! -f .env ]; then
    cat > .env << EOF
# NixOS GUI Environment Variables
NODE_ENV=development
PORT=8080
HTTPS_PORT=8443
JWT_SECRET=$(openssl rand -hex 32)
SESSION_SECRET=$(openssl rand -hex 32)
REDIS_URL=redis://localhost:6379
LOG_LEVEL=debug
SSL_CERT=ssl/cert.pem
SSL_KEY=ssl/key.pem
EOF
    echo -e "${GREEN}✅ Created .env file${NC}"
else
    echo -e "${YELLOW}⚠️  .env file already exists${NC}"
fi

# Setup based on available tools
echo ""
echo -e "${BLUE}Setting up development environment...${NC}"

if [ "$HAS_NIX" = true ]; then
    echo -e "${GREEN}Using Nix environment${NC}"
    echo "Run 'nix-shell' to enter the development environment"
    
elif [ "$HAS_NODE" = true ]; then
    echo -e "${GREEN}Using Node.js environment${NC}"
    echo "Installing npm dependencies..."
    npm install
    
elif [ "$HAS_PYTHON" = true ]; then
    echo -e "${YELLOW}Using Python fallback environment${NC}"
    
    # Set up Python virtual environment
    if [ ! -d .venv ]; then
        echo "Creating Python virtual environment..."
        python3 -m venv .venv
    fi
    
    echo "Activating virtual environment..."
    source .venv/bin/activate
    
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
    
else
    echo -e "${RED}❌ No suitable development environment found!${NC}"
    echo "Please install one of the following:"
    echo "  - Nix (recommended): curl -L https://nixos.org/nix/install | sh"
    echo "  - Node.js: https://nodejs.org/"
    echo "  - Python 3: https://www.python.org/"
    exit 1
fi

# Create helper scripts
echo ""
echo -e "${BLUE}Creating helper scripts...${NC}"

# Start script
cat > scripts/start.sh << 'EOF'
#!/usr/bin/env bash
if command -v npm >/dev/null 2>&1; then
    npm start
elif [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
    python3 test/python-test-server.py
else
    echo "No suitable runtime found"
    exit 1
fi
EOF
chmod +x scripts/start.sh

# Test script
cat > scripts/test.sh << 'EOF'
#!/usr/bin/env bash
cd test
if [ -x run-all-tests.sh ]; then
    ./run-all-tests.sh
else
    ./run-basic-tests.sh
fi
EOF
chmod +x scripts/test.sh

echo -e "${GREEN}✅ Helper scripts created${NC}"

# Create documentation
echo ""
echo -e "${BLUE}Updating documentation...${NC}"

cat > DEVELOPMENT.md << 'EOF'
# NixOS GUI Development Guide

## Quick Start

### Using Nix (Recommended)
```bash
nix-shell
make dev
```

### Using Node.js
```bash
npm install
npm start
```

### Using Python (Fallback)
```bash
source .venv/bin/activate
python3 test/python-test-server.py
```

## Available Commands

- `make dev` - Start development server
- `make test` - Run tests
- `make build` - Build for production
- `make security-test` - Run security audit
- `make clean` - Clean build artifacts

## Environment Variables

See `.env` file for configuration options.

## SSL Certificates

Self-signed certificates are in the `ssl/` directory.

## Testing

Run the complete test suite:
```bash
make all-tests
```
EOF

echo -e "${GREEN}✅ Documentation updated${NC}"

# Final summary
echo ""
echo -e "${GREEN}🎉 Environment setup complete!${NC}"
echo ""
echo "Next steps:"
echo ""

if [ "$HAS_NIX" = true ]; then
    echo "1. Enter the Nix shell:"
    echo "   nix-shell"
    echo ""
fi

echo "2. Start the development server:"
echo "   make dev"
echo ""
echo "3. Run tests:"
echo "   make test"
echo ""
echo "4. Access the application:"
echo "   https://localhost:8443"
echo ""
echo "Happy coding! 🚀"