{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    # Tauri dependencies
    pkg-config
    openssl
    gtk3
    webkitgtk
    libsoup
    
    # Rust
    rustc
    cargo
    rustfmt
    clippy
    
    # Node.js
    nodejs_20
    nodePackages.pnpm
    
    # Development tools
    git
    ripgrep
    fd
  ];
  
  shellHook = ''
    echo "🚀 Nix for Humanity Development Environment"
    echo "=================================="
    echo "Available commands:"
    echo "  npm run tauri:dev    - Start development server"
    echo "  npm run tauri:build  - Build production app"
    echo "  cargo test           - Run Rust tests"
    echo "  npm test             - Run TypeScript tests"
    echo ""
    echo "First time setup:"
    echo "  npm install"
    echo ""
  '';
  
  # Set up environment variables
  RUST_BACKTRACE = 1;
  WEBKIT_DISABLE_COMPOSITING_MODE = 1; # Helps with some GPU issues
}