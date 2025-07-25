{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "nixos-gui-minimal";
  
  buildInputs = with pkgs; [
    # Rust toolchain
    rustc
    cargo
    pkg-config
    
    # Essential Tauri dependencies
    openssl
    openssl.dev
    
    # For testing without full GUI
    # We'll add GTK dependencies later
    
    # Basic tools
    git
    curl
    jq
  ];
  
  shellHook = ''
    echo "🌟 NixOS GUI Minimal Dev Environment"
    echo "===================================="
    echo "Rust: $(rustc --version)"
    echo "Cargo: $(cargo --version)"
    echo ""
    
    # Set up OpenSSL for Rust
    export PKG_CONFIG_PATH="${pkgs.openssl.dev}/lib/pkgconfig:$PKG_CONFIG_PATH"
    export OPENSSL_DIR="${pkgs.openssl.dev}"
    export OPENSSL_LIB_DIR="${pkgs.openssl.out}/lib"
    export OPENSSL_INCLUDE_DIR="${pkgs.openssl.dev}/include"
    
    echo "OpenSSL configured for Rust builds"
    echo ""
    echo "Try: cd src-tauri && cargo check"
  '';
}