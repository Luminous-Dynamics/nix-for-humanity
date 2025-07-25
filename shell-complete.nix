{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "nixos-gui-complete-dev";
  
  buildInputs = with pkgs; [
    # === Core Development ===
    # Rust toolchain
    rustc
    cargo
    rustfmt
    clippy
    rust-analyzer
    cargo-tauri
    
    # Node.js ecosystem
    nodejs_20
    nodePackages.npm
    nodePackages.pnpm
    nodePackages.yarn
    bun # Fast JS runtime
    
    # Python ecosystem
    python3
    python3Packages.pip
    python3Packages.virtualenv
    python3Packages.pytest
    python3Packages.flask
    python3Packages.pyjwt
    
    # === Build Tools ===
    gcc
    gnumake
    cmake
    meson
    ninja
    pkg-config
    mold # Fast linker
    sccache # Build cache
    
    # === Tauri & GUI Dependencies ===
    gtk3
    webkitgtk_4_1
    librsvg
    cairo
    pango
    gdk-pixbuf
    libsoup_3
    openssl
    dbus
    
    # === Database & State Management ===
    sqlite
    redis
    postgresql
    etcd # For distributed config
    
    # === Message Queue & Event Systems ===
    rabbitmq-server
    kafka
    nats-server
    
    # === Container & Virtualization ===
    podman
    docker-compose
    qemu
    libvirt
    virt-manager
    
    # === Networking & Security ===
    wireguard-tools
    nebula
    tailscale
    vault # Secrets management
    mkcert
    cfssl # CloudFlare SSL tools
    step-cli # Certificate management
    
    # === Monitoring & Observability ===
    prometheus
    grafana
    loki # Log aggregation
    grafana-loki
    vector # Observability pipeline
    opentelemetry-collector
    jaeger # Distributed tracing
    
    # === Testing Tools ===
    k6 # Load testing
    vegeta # HTTP load testing
    drill # HTTP benchmarking
    wrk2 # Latency measurement
    artillery # Load testing
    
    # === Security Testing ===
    nmap
    rustscan # Fast port scanner
    nikto # Web scanner
    sqlmap # SQL injection testing
    burpsuite # Web security testing
    metasploit
    
    # === Documentation ===
    mdbook
    pandoc
    graphviz
    plantuml
    asciidoctor
    hugo # Static site generator
    
    # === Development Tools ===
    direnv
    tmux
    tmuxinator
    zellij # Modern terminal multiplexer
    alacritty # GPU accelerated terminal
    starship # Shell prompt
    fzf # Fuzzy finder
    ripgrep
    fd
    bat
    exa # Modern ls
    bottom # System monitor
    bandwhich # Network monitor
    procs # Modern ps
    dust # Disk usage
    
    # === Code Quality ===
    tokei # Code statistics
    loc # Lines of code counter
    hyperfine # Benchmarking
    criterion # Benchmarking framework
    flamegraph
    cargo-flamegraph
    perf-tools
    bpftrace # System tracing
    
    # === API Development ===
    httpie
    curlie # Better curl
    xh # Friendly HTTP client
    grpcurl
    grpcui
    bloomrpc # gRPC GUI client
    insomnia # API client
    
    # === Infrastructure as Code ===
    terraform
    ansible
    pulumi
    
    # === Nix Specific ===
    nix-prefetch-git
    nixpkgs-fmt
    alejandra # Nix formatter
    statix # Nix linter
    deadnix # Dead code finder
    nix-tree # Dependency viewer
    nix-du # Disk usage
    cachix # Binary cache
    
    # === Language Servers ===
    nil # Nix LSP
    rnix-lsp
    nodePackages.typescript-language-server
    nodePackages.vscode-langservers-extracted
    sumneko-lua-language-server
    gopls
    
    # === Version Control ===
    git
    gh # GitHub CLI
    glab # GitLab CLI
    hub # GitHub hub
    git-lfs
    gitui # Terminal UI for git
    lazygit # Terminal UI for git
    delta # Better git diff
    
    # === Sacred Tools ===
    figlet
    lolcat
    cowsay
    fortune
    cmatrix # Matrix rain
    pipes # Pipes screensaver
    sl # Steam locomotive
    
    # === AI/ML Tools (optional) ===
    ollama # Local LLM runner
    
    # === WebAssembly ===
    wasmtime
    wasmer
    wasm-pack
    
    # === Service Mesh ===
    consul
    nomad
    linkerd
    
    # === Backup & Sync ===
    restic
    borg
    rclone
    syncthing
  ];
  
  shellHook = ''
    echo "🌟 NixOS GUI Complete Development Environment 🌟"
    echo "==============================================="
    echo ""
    echo "Environment Summary:"
    echo "  Rust: $(rustc --version | cut -d' ' -f2)"
    echo "  Node: $(node --version)"
    echo "  Python: $(python3 --version | cut -d' ' -f2)"
    echo "  Tauri CLI: $(cargo tauri --version 2>/dev/null || echo 'Run: cargo install tauri-cli')"
    echo ""
    
    # Set up environment variables
    export RUST_BACKTRACE=1
    export RUST_LOG=debug
    export NODE_ENV=development
    
    # Rust optimizations
    export RUSTFLAGS="-C link-arg=-fuse-ld=mold"
    export CARGO_TARGET_DIR=target
    export RUSTC_WRAPPER=sccache
    
    # Security keys (generate if not exists)
    export JWT_SECRET=''${JWT_SECRET:-$(openssl rand -hex 32)}
    export SESSION_SECRET=''${SESSION_SECRET:-$(openssl rand -hex 32)}
    export TAURI_PRIVATE_KEY=''${TAURI_PRIVATE_KEY:-$(openssl rand -hex 32)}
    
    # Create directories
    mkdir -p .config/nixos-gui/{logs,data,cache,secrets}
    mkdir -p ssl test/results docs/api
    
    # Generate SSL certs if needed
    if [ ! -f ssl/cert.pem ]; then
      echo "Generating development SSL certificates..."
      mkcert -install 2>/dev/null || true
      mkcert -cert-file ssl/cert.pem -key-file ssl/key.pem \
        localhost 127.0.0.1 ::1 \
        nixos-gui.local \
        "*.nixos-gui.local"
    fi
    
    # Set up git hooks
    if [ -d .git ] && [ ! -f .git/hooks/pre-commit ]; then
      echo "Setting up git hooks..."
      cat > .git/hooks/pre-commit << 'EOF'
#!/usr/bin/env bash
cargo fmt --check
cargo clippy -- -D warnings
npm run lint
EOF
      chmod +x .git/hooks/pre-commit
    fi
    
    # Enhanced aliases
    alias nix-gui='cargo tauri dev'
    alias nix-gui-build='cargo tauri build'
    alias nix-test='cargo test && npm test'
    alias nix-bench='cargo bench && npm run bench'
    alias nix-security='cargo audit && npm audit'
    alias nix-update='cargo update && npm update'
    alias nix-clean='cargo clean && rm -rf node_modules'
    
    # Development functions
    watch-rust() {
      cargo watch -x check -x test -x run
    }
    
    watch-frontend() {
      npm run dev
    }
    
    start-services() {
      echo "Starting development services..."
      redis-server --daemonize yes
      nginx -c nginx.dev.conf 2>/dev/null || true
      echo "Services started!"
    }
    
    stop-services() {
      echo "Stopping development services..."
      redis-cli shutdown 2>/dev/null || true
      nginx -s stop 2>/dev/null || true
      echo "Services stopped!"
    }
    
    # Sacred development ritual
    sacred-start() {
      figlet -f slant "NixOS GUI" | lolcat
      echo ""
      echo "🧘 Setting sacred intention for conscious coding..."
      echo "🌊 May our code flow with clarity and purpose"
      echo "🛡️ May security be our foundation"
      echo "💫 May the user experience bring peace"
      echo ""
      fortune | cowsay | lolcat
      echo ""
    }
    
    # Show available commands
    echo "📚 Quick Reference:"
    echo "  nix-gui          - Start Tauri development server"
    echo "  nix-gui-build    - Build production release"
    echo "  nix-test         - Run all tests"
    echo "  nix-security     - Run security audit"
    echo "  watch-rust       - Auto-rebuild Rust on changes"
    echo "  watch-frontend   - Auto-rebuild frontend"
    echo "  start-services   - Start dev services (Redis, etc)"
    echo "  sacred-start     - Begin with sacred intention"
    echo ""
    echo "📖 Documentation:"
    echo "  mdbook serve docs - Start documentation server"
    echo "  cargo doc --open  - Open Rust API docs"
    echo ""
    echo "🔒 Security:"
    echo "  cargo audit      - Check for vulnerabilities"
    echo "  cargo deny check - Check dependencies"
    echo "  rustscan -a localhost - Port scan"
    echo ""
    echo "📊 Performance:"
    echo "  cargo flamegraph - Generate flame graph"
    echo "  hyperfine './target/release/nixos-gui' - Benchmark"
    echo "  k6 run test/load-test.js - Load test"
    echo ""
    
    # Check if in git repo
    if [ -d .git ]; then
      echo "📦 Git Status:"
      git status -sb
      echo ""
    fi
    
    # Sacred greeting
    if [ "$SACRED_MODE" = "1" ]; then
      sacred-start
    fi
    
    echo "✨ Environment ready! Happy coding! ✨"
  '';
  
  # Environment variables
  RUST_SRC_PATH = "${pkgs.rust.packages.stable.rustPlatform.rustLibSrc}";
  LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
    pkgs.openssl
    pkgs.webkitgtk_4_1
    pkgs.gtk3
    pkgs.cairo
    pkgs.gdk-pixbuf
    pkgs.glib
    pkgs.dbus
    pkgs.librsvg
    pkgs.libsoup_3
  ];
  
  # Additional paths
  PKG_CONFIG_PATH = pkgs.lib.makeSearchPathOutput "dev" "lib/pkgconfig" [
    pkgs.openssl
    pkgs.dbus
    pkgs.glib
  ];
}