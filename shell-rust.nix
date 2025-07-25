{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "nixos-gui-rust-dev";
  
  buildInputs = with pkgs; [
    # Rust toolchain
    rustc
    cargo
    rustfmt
    clippy
    rust-analyzer
    
    # Tauri dependencies
    pkg-config
    openssl
    gtk3
    webkitgtk_4_1
    librsvg
    pango
    atk
    gdk-pixbuf
    cairo
    libsoup_3
    
    # Additional system libraries
    dbus
    glib
    
    # Build tools
    gcc
    gnumake
    cmake
    
    # Node.js for Tauri frontend
    nodejs_20
    nodePackages.npm
    nodePackages.pnpm
    
    # Tauri CLI
    cargo-tauri
    
    # Development tools
    mold # Fast linker
    sccache # Build cache
    cargo-watch
    cargo-edit
    cargo-audit
    cargo-outdated
    cargo-nextest # Better test runner
    bacon # Background rust checker
    
    # Debugging tools
    gdb
    lldb
    valgrind
    
    # Performance tools
    hyperfine
    flamegraph
    
    # Documentation
    mdbook
    
    # WebView debugging
    chromium # For debugging WebView
    
    # Additional for NixOS integration
    nix-prefetch-git
    nixpkgs-fmt
    nil  # Nix LSP
    
    # Python for scripts
    python3
    
    # Security tools
    cargo-deny
    cargo-crev
    
    # Git
    git
    gh
  ];
  
  shellHook = ''
    echo "🦀 NixOS GUI Rust/Tauri Development Environment"
    echo "=============================================="
    echo "Rust: $(rustc --version)"
    echo "Cargo: $(cargo --version)"
    echo "Node.js: $(node --version)"
    echo ""
    echo "Available commands:"
    echo "  cargo tauri dev       - Start Tauri development"
    echo "  cargo tauri build     - Build for production"
    echo "  cargo test            - Run tests"
    echo "  cargo clippy          - Run linter"
    echo "  bacon                 - Start background checker"
    echo "  cargo watch -x run    - Auto-rebuild on changes"
    echo ""
    
    # Set up Rust environment
    export RUST_BACKTRACE=1
    export RUST_LOG=debug
    
    # Optimize for development
    export CARGO_TARGET_DIR=target
    export RUSTFLAGS="-C link-arg=-fuse-ld=mold"
    
    # Enable sccache
    export RUSTC_WRAPPER=sccache
    
    # Tauri environment
    export TAURI_PRIVATE_KEY=$(openssl rand -hex 32)
    export TAURI_KEY_PASSWORD=$(openssl rand -hex 16)
    
    # Create project structure if needed
    if [ ! -f Cargo.toml ] && [ ! -d src-tauri ]; then
      echo ""
      echo "💡 No Tauri project found. Initialize with:"
      echo "   cargo tauri init"
      echo ""
    fi
    
    # Aliases for common tasks
    alias ct='cargo tauri'
    alias ctd='cargo tauri dev'
    alias ctb='cargo tauri build'
    alias cw='cargo watch'
    alias cc='cargo clippy'
    alias cf='cargo fmt'
    
    # Function to create new Tauri project
    create-tauri-project() {
      echo "Creating new Tauri project..."
      cargo tauri init \
        --app-name nixos-gui \
        --window-title "NixOS Configuration Manager" \
        --dist-dir ../frontend/dist \
        --dev-path http://localhost:3000
    }
    
    # Function to setup frontend
    setup-frontend() {
      echo "Setting up frontend..."
      if [ ! -f package.json ]; then
        npm init -y
        npm install --save-dev \
          @tauri-apps/api \
          @tauri-apps/cli \
          vite \
          @vitejs/plugin-react \
          react \
          react-dom \
          typescript \
          @types/react \
          @types/react-dom
      fi
    }
    
    echo ""
    echo "🌟 Consciousness-First Rust Development"
    echo "Sacred pauses between compilations 🧘"
    echo ""
  '';
  
  # Environment variables
  RUST_SRC_PATH = "${pkgs.rust.packages.stable.rustPlatform.rustLibSrc}";
  
  # LD_LIBRARY_PATH for runtime
  LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
    pkgs.openssl
    pkgs.webkitgtk_4_1
    pkgs.gtk3
    pkgs.cairo
    pkgs.gdk-pixbuf
    pkgs.glib
    pkgs.dbus
    pkgs.librsvg
  ];
}