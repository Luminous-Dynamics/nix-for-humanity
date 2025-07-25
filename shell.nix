{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "nixos-gui-dev";
  
  buildInputs = with pkgs; [
    # Core development tools
    nodejs_20
    nodePackages.npm
    nodePackages.pnpm
    nodePackages.yarn
    
    # Build tools
    gnumake
    gcc
    pkg-config
    
    # SSL/TLS support
    openssl
    
    # Testing tools
    curl
    jq
    httpie
    
    # Security tools
    nmap
    
    # Database tools (if needed)
    sqlite
    redis
    
    # Python for fallback scripts
    python3
    python3Packages.pip
    python3Packages.flask
    python3Packages.gunicorn
    
    # System utilities
    htop
    lsof
    netcat
    
    # Git and version control
    git
    gh  # GitHub CLI
    
    # Documentation
    pandoc
    
    # Container tools (optional)
    podman
    docker-compose
    
    # Monitoring tools
    prometheus
    grafana
    
    # Load testing tools
    apacheHttpd  # for ab (Apache Bench)
    siege
    
    # Certificate generation
    mkcert
    
    # Process management
    supervisor
    tmux
    
    # Editor support
    neovim
    ripgrep
    fd
  ];
  
  shellHook = ''
    echo "🌟 NixOS GUI Development Environment"
    echo "===================================="
    echo "Node.js: $(node --version)"
    echo "npm: $(npm --version)"
    echo "Python: $(python3 --version)"
    echo ""
    echo "Available commands:"
    echo "  npm start      - Start development servers"
    echo "  npm test       - Run test suite"
    echo "  npm run build  - Build for production"
    echo "  make dev       - Start with make"
    echo ""
    echo "Environment setup complete! 🚀"
    
    # Set up environment variables
    export NODE_ENV=development
    export JWT_SECRET=$(openssl rand -hex 32)
    export SESSION_SECRET=$(openssl rand -hex 32)
    export NIXOS_GUI_PORT=8080
    export NIXOS_GUI_HTTPS_PORT=8443
    
    # Create SSL certificates if they don't exist
    if [ ! -f ssl/cert.pem ]; then
      echo "Generating SSL certificates..."
      mkdir -p ssl
      mkcert -install
      mkcert -cert-file ssl/cert.pem -key-file ssl/key.pem localhost 127.0.0.1 ::1
    fi
    
    # Set up Python virtual environment for fallback
    if [ ! -d .venv ]; then
      echo "Setting up Python virtual environment..."
      python3 -m venv .venv
    fi
    
    # Source Python venv
    source .venv/bin/activate
    
    # Install Python dependencies if requirements.txt exists
    if [ -f requirements.txt ]; then
      pip install -r requirements.txt
    fi
    
    # Create necessary directories
    mkdir -p logs
    mkdir -p data
    mkdir -p test/results
    
    # Add project scripts to PATH
    export PATH=$PWD/scripts:$PATH
    
    # Alias for quick commands
    alias nix-gui-start="npm start"
    alias nix-gui-test="npm test"
    alias nix-gui-build="npm run build"
    alias nix-gui-secure="npm run start:secure"
    
    # Function to check all services
    check-services() {
      echo "Checking services..."
      lsof -i :8080 >/dev/null 2>&1 && echo "✅ HTTP server on :8080" || echo "❌ HTTP server not running"
      lsof -i :8443 >/dev/null 2>&1 && echo "✅ HTTPS server on :8443" || echo "❌ HTTPS server not running"
      lsof -i :6379 >/dev/null 2>&1 && echo "✅ Redis on :6379" || echo "❌ Redis not running"
    }
    
    echo ""
    echo "💡 Tips:"
    echo "  - Run 'nix-shell' to enter this environment"
    echo "  - Run 'check-services' to verify running services"
    echo "  - SSL certificates are in the ssl/ directory"
    echo "  - Logs are written to the logs/ directory"
    echo ""
  '';
  
  # Environment variables
  NIXOS_GUI_DEV = "1";
  NODE_OPTIONS = "--max-old-space-size=4096";
  
  # Prevent npm from accessing system directories
  NPM_CONFIG_PREFIX = "$PWD/.npm-global";
  
  # Python settings
  PYTHONPATH = "$PWD";
  
  # SSL settings
  NODE_TLS_REJECT_UNAUTHORIZED = "0"; # For development only
}