{
  description = "Nix for Humanity - Natural Language Interface for NixOS";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    rust-overlay.url = "github:oxalica/rust-overlay";
  };

  outputs = { self, nixpkgs, flake-utils, rust-overlay }:
    let
      # Supported systems
      supportedSystems = [ "x86_64-linux" "aarch64-linux" ];
    in
    flake-utils.lib.eachSystem supportedSystems (system:
      let
        overlays = [ (import rust-overlay) ];
        pkgs = import nixpkgs {
          inherit system overlays;
        };
        
        rustToolchain = pkgs.rust-bin.stable.latest.default.override {
          extensions = [ "rust-src" ];
        };
      in
      {
        # Development shell
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # Rust toolchain
            rustToolchain
            pkg-config
            
            # Tauri dependencies
            webkitgtk_4_0
            librsvg
            libsoup
            
            # Node.js for frontend
            nodejs_20
            nodePackages.npm
            
            # Build tools
            openssl
            cmake
            
            # Development tools
            nodePackages.typescript
            nodePackages.vite
            
            # System tools for testing
            curl
            jq
          ];

          shellHook = ''
            echo "🌟 Nix for Humanity Development Environment"
            echo "=========================================="
            echo "Rust: $(rustc --version)"
            echo "Node.js: $(node --version)"
            echo "npm: $(npm --version)"
            echo ""
            echo "Available commands:"
            echo "  npm install       - Install dependencies"
            echo "  npm run tauri:dev - Start Tauri development"
            echo "  npm run tauri:build - Build Tauri app"
            echo "  npm test          - Run tests"
            echo ""
            echo "Natural language awaits! 🗣️"
          '';
          
          # Environment variables for Tauri
          WEBKIT_DISABLE_COMPOSITING_MODE = "1";
        };

        # Package
        packages = {
          default = self.packages.${system}.nix-for-humanity;
          
          nix-for-humanity = pkgs.stdenv.mkDerivation rec {
            pname = "nix-for-humanity";
            version = "0.1.0";
            
            src = ./.;
            
            nativeBuildInputs = with pkgs; [
              rustToolchain
              pkg-config
              nodejs_20
              nodePackages.npm
              makeWrapper
              
              # Tauri build dependencies
              webkitgtk_4_0
              librsvg
              libsoup
              openssl
            ];
            
            buildPhase = ''
              # Copy source
              cp -r . $TMPDIR/build
              cd $TMPDIR/build
              
              # Install npm dependencies
              npm ci
              
              # Build Tauri app
              npm run tauri:build
            '';
            
            installPhase = ''
              mkdir -p $out/{bin,share/applications,share/icons}
              
              # Install the Tauri binary
              cp -r src-tauri/target/release/nix-for-humanity $out/bin/
              
              # Create desktop entry
              cat > $out/share/applications/nix-for-humanity.desktop <<EOF
              [Desktop Entry]
              Name=Nix for Humanity
              Comment=Natural Language Interface for NixOS
              Exec=$out/bin/nix-for-humanity
              Icon=nix-for-humanity
              Terminal=false
              Type=Application
              Categories=System;Settings;
              Keywords=nix;nixos;configuration;voice;natural;language;
              EOF
              
              # TODO: Add icon files
            '';
            
            meta = with pkgs.lib; {
              description = "Natural Language Interface for NixOS";
              longDescription = ''
                Nix for Humanity makes NixOS accessible to everyone through natural language.
                Simply type or speak what you want in your own words - no commands to memorize.
              '';
              homepage = "https://github.com/Luminous-Dynamics/nix-for-humanity";
              license = licenses.srl;
              maintainers = with maintainers; [ ]; # Add maintainers
              platforms = platforms.linux;
            };
          };
        };

        # App runner for development
        apps.default = flake-utils.lib.mkApp {
          drv = self.packages.${system}.nix-for-humanity;
        };
      }
    ) // {
      # NixOS module
      nixosModules = {
        default = { config, lib, pkgs, ... }: with lib; {
          options.programs.nix-for-humanity = {
            enable = mkEnableOption "Nix for Humanity - Natural Language Interface for NixOS";
          };
          
          config = mkIf config.programs.nix-for-humanity.enable {
            environment.systemPackages = [ self.packages.${pkgs.system}.nix-for-humanity ];
          };
        };
      };
      
      # Overlay
      overlays.default = final: prev: {
        nix-for-humanity = self.packages.${prev.system}.nix-for-humanity;
      };
      
      # Home Manager module
      homeManagerModules.default = { config, lib, pkgs, ... }: with lib; {
        options.programs.nix-for-humanity = {
          enable = mkEnableOption "Nix for Humanity";
        };
        
        config = mkIf config.programs.nix-for-humanity.enable {
          home.packages = [ self.packages.${pkgs.system}.nix-for-humanity ];
        };
      };
    };
}