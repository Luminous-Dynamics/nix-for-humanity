{
  description = "NixOS GUI - Consciousness-First System Management";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    rust-overlay = {
      url = "github:oxalica/rust-overlay";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, rust-overlay }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        overlays = [ (import rust-overlay) ];
        pkgs = import nixpkgs {
          inherit system overlays;
        };
        
        rustToolchain = pkgs.rust-bin.stable.latest.default.override {
          extensions = [ "rust-src" "rustfmt" "clippy" ];
        };
        
        # Common build inputs for all platforms
        commonBuildInputs = with pkgs; [
          openssl
          openssl.dev
          pkg-config
          
          # Core dependencies
          glib
          glib.dev
          cairo
          pango
          gdk-pixbuf
          atk
          gobject-introspection
          gobject-introspection.dev
          
          # System tray
          libappindicator-gtk3
          libayatana-appindicator
          
          # Additional libraries
          librsvg
          libxkbcommon
          
          # Development tools
          nodejs_20
          nodePackages.npm
          nodePackages.pnpm
        ];
        
        # Platform-specific inputs
        linuxBuildInputs = with pkgs; [
          gtk3
          gtk3.dev
          webkitgtk_4_1
          webkitgtk_4_1.dev
          libsoup_3
          libsoup_3.dev
          
          # X11
          xorg.libX11
          xorg.libXcursor
          xorg.libXrandr
          xorg.libXi
          
          # Wayland
          wayland
        ];
        
        darwinBuildInputs = with pkgs; [
          darwin.apple_sdk.frameworks.AppKit
          darwin.apple_sdk.frameworks.WebKit
        ];
        
        buildInputs = commonBuildInputs ++ 
          (if pkgs.stdenv.isLinux then linuxBuildInputs else darwinBuildInputs);
        
      in
      {
        devShells.default = pkgs.mkShell {
          inherit buildInputs;
          
          nativeBuildInputs = with pkgs; [
            rustToolchain
            cargo-tauri
          ];
          
          shellHook = ''
            echo "🌟 NixOS GUI Development Environment (Flake) 🌟"
            echo
            echo "Rust: $(rustc --version)"
            echo "Cargo: $(cargo --version)"
            echo "Node: $(node --version)"
            echo
            
            # Set up environment
            export RUST_BACKTRACE=1
            export RUST_LOG=nixos_gui=debug,tauri=info
            
            # PKG_CONFIG paths
            export PKG_CONFIG_PATH="${pkgs.openssl.dev}/lib/pkgconfig:$PKG_CONFIG_PATH"
            ${pkgs.lib.optionalString pkgs.stdenv.isLinux ''
              export PKG_CONFIG_PATH="${pkgs.gtk3.dev}/lib/pkgconfig:$PKG_CONFIG_PATH"
              export PKG_CONFIG_PATH="${pkgs.webkitgtk_4_1.dev}/lib/pkgconfig:$PKG_CONFIG_PATH"
              export PKG_CONFIG_PATH="${pkgs.libsoup_3.dev}/lib/pkgconfig:$PKG_CONFIG_PATH"
            ''}
            
            # OpenSSL
            export OPENSSL_DIR="${pkgs.openssl.dev}"
            export OPENSSL_LIB_DIR="${pkgs.openssl.out}/lib"
            export OPENSSL_INCLUDE_DIR="${pkgs.openssl.dev}/include"
            
            echo "Commands:"
            echo "  cargo tauri dev     - Run in development mode"
            echo "  cargo tauri build   - Build for production"
            echo "  cargo test          - Run tests"
            echo
            echo "🧘 Ready for consciousness-first development!"
          '';
        };
        
        # Optional: package definition for building the app
        packages.default = pkgs.rustPlatform.buildRustPackage rec {
          pname = "nixos-gui";
          version = "0.1.0";
          
          src = ./.;
          
          cargoLock = {
            lockFile = ./Cargo.lock;
          };
          
          nativeBuildInputs = [ pkgs.pkg-config ];
          inherit buildInputs;
          
          # Tauri specific build
          buildPhase = ''
            cargo tauri build
          '';
          
          installPhase = ''
            mkdir -p $out/bin
            cp target/release/nixos-gui $out/bin/
          '';
          
          meta = with pkgs.lib; {
            description = "Consciousness-first GUI for NixOS system management";
            homepage = "https://github.com/Luminous-Dynamics/nixos-gui";
            license = licenses.mit;
            maintainers = [ ];
            platforms = platforms.all;
          };
        };
      });
}