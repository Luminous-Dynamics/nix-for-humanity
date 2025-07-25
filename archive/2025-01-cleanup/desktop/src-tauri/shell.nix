{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    # Rust toolchain
    rustc
    cargo
    rustfmt
    clippy
    
    # Build essentials
    pkg-config
    gcc
    gnumake
    
    # Tauri dependencies
    openssl
    openssl.dev
    
    # GTK and related libraries
    gtk3
    gtk3.dev
    glib
    glib.dev
    cairo
    pango
    gdk-pixbuf
    atk
    
    # WebKit for web view
    webkitgtk_4_1
    webkitgtk_4_1.dev
    
    # libsoup for networking (WebKit dependency)
    libsoup_3
    libsoup_3.dev
    
    # Additional GTK dependencies
    gobject-introspection
    gobject-introspection.dev
    
    # System tray support
    libappindicator-gtk3
    
    # Additional required libraries
    librsvg
    libayatana-appindicator
    
    # X11 libraries (if needed)
    xorg.libX11
    xorg.libXcursor
    xorg.libXrandr
    xorg.libXi
    
    # Wayland libraries (for modern display servers)
    wayland
    libxkbcommon
    
    # Development tools
    gdb
    valgrind
    strace
    
    # Node.js for frontend development
    nodejs_20
    nodePackages.npm
    nodePackages.pnpm
    
    # Python (for any build scripts)
    python3
  ];

  # Environment variables for building
  shellHook = ''
    echo "🌟 NixOS GUI Development Environment (Full Tauri) 🌟"
    echo
    echo "Setting up environment variables..."
    
    # Set PKG_CONFIG_PATH for all libraries
    export PKG_CONFIG_PATH="${pkgs.openssl.dev}/lib/pkgconfig:$PKG_CONFIG_PATH"
    export PKG_CONFIG_PATH="${pkgs.gtk3.dev}/lib/pkgconfig:$PKG_CONFIG_PATH"
    export PKG_CONFIG_PATH="${pkgs.webkitgtk_4_1.dev}/lib/pkgconfig:$PKG_CONFIG_PATH"
    export PKG_CONFIG_PATH="${pkgs.libsoup_3.dev}/lib/pkgconfig:$PKG_CONFIG_PATH"
    export PKG_CONFIG_PATH="${pkgs.glib.dev}/lib/pkgconfig:$PKG_CONFIG_PATH"
    
    # Set library paths
    export LD_LIBRARY_PATH="${pkgs.openssl.out}/lib:$LD_LIBRARY_PATH"
    export LD_LIBRARY_PATH="${pkgs.gtk3}/lib:$LD_LIBRARY_PATH"
    export LD_LIBRARY_PATH="${pkgs.webkitgtk_4_1}/lib:$LD_LIBRARY_PATH"
    export LD_LIBRARY_PATH="${pkgs.libsoup_3}/lib:$LD_LIBRARY_PATH"
    
    # GDK/GTK environment
    export GDK_PIXBUF_MODULE_PATH="${pkgs.librsvg}/lib/gdk-pixbuf-2.0/2.10.0/loaders"
    export GIO_MODULE_DIR="${pkgs.glib-networking}/lib/gio/modules"
    
    # Rust specific
    export RUST_BACKTRACE=1
    export RUST_LOG=nixos_gui=debug,tauri=info
    
    # Node/npm setup
    export NODE_OPTIONS="--max-old-space-size=4096"
    
    echo "Environment configured! ✨"
    echo
    echo "Available commands:"
    echo "  cargo build         - Build the Rust backend"
    echo "  cargo tauri dev     - Run in development mode"
    echo "  cargo tauri build   - Build for production"
    echo "  npm install         - Install frontend dependencies"
    echo "  npm run tauri dev   - Alternative dev command"
    echo
    echo "Testing commands:"
    echo "  pkg-config --exists webkit2gtk-4.1  - Check WebKit"
    echo "  pkg-config --exists gtk+-3.0        - Check GTK"
    echo "  pkg-config --modversion openssl     - Check OpenSSL"
    echo
    echo "Current directory: $(pwd)"
    echo "Rust version: $(rustc --version)"
    echo "Cargo version: $(cargo --version)"
    echo "Node version: $(node --version)"
    echo
    echo "🧘 Ready for consciousness-first development!"
  '';
  
  # Ensure locale is set properly
  LOCALE_ARCHIVE = "${pkgs.glibcLocales}/lib/locale/locale-archive";
  
  # Additional environment variables
  OPENSSL_DIR = "${pkgs.openssl.dev}";
  OPENSSL_LIB_DIR = "${pkgs.openssl.out}/lib";
  OPENSSL_INCLUDE_DIR = "${pkgs.openssl.dev}/include";
}