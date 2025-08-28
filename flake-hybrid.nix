{
  description = "Luminous Nix - Hybrid approach with Poetry";
  
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };
  
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        
        # Python with basic packages
        pythonEnv = pkgs.python3.withPackages (ps: with ps; [
          pip
          setuptools
          wheel
          virtualenv
        ]);
        
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # Python environment
            pythonEnv
            poetry
            
            # Development tools
            ruff
            black
            mypy
            
            # System dependencies for packages
            gcc
            stdenv.cc.cc.lib
            zlib
            libffi
            openssl
            
            # For Data Trinity databases
            sqlite
            postgresql
            
            # For voice features
            portaudio
            ffmpeg
            
            # Git and tools
            git
            gh
            jq
            
            # Documentation
            pandoc
          ];
          
          shellHook = ''
            echo "🌟 Luminous Nix Development Environment (Hybrid)"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            echo "This uses Poetry for Python packages and Nix for system deps."
            echo ""
            echo "Quick Start:"
            echo "  1. poetry install     # Install Python deps"
            echo "  2. poetry run ask-nix # Run the CLI"
            echo ""
            echo "Available tools:"
            echo "  poetry - Python dependency management"
            echo "  python - Python ${pkgs.python3.version}"
            echo "  ruff   - Fast Python linter"
            echo "  black  - Python formatter"
            echo "  mypy   - Type checker"
            echo ""
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            
            # Set up environment
            export PYTHONPATH="$PWD/src:$PYTHONPATH"
            export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.zlib}/lib:$LD_LIBRARY_PATH"
            
            # Create virtual environment if needed
            if [ ! -d ".venv" ]; then
              echo "Creating Poetry virtual environment..."
              poetry config virtualenvs.in-project true
              poetry install --no-interaction --no-root
            fi
            
            # Activate if it exists
            if [ -f ".venv/bin/activate" ]; then
              source .venv/bin/activate
            fi
          '';
          
          # Environment variables
          LUMINOUS_NIX_DEV = "1";
          NIX_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
            pkgs.stdenv.cc.cc
            pkgs.zlib
            pkgs.libffi
            pkgs.openssl
          ];
          NIX_LD = "${pkgs.stdenv.cc.cc}/lib/ld-linux-x86-64.so.2";
        };
        
        # Minimal shell for CI
        devShells.ci = pkgs.mkShell {
          buildInputs = with pkgs; [
            pythonEnv
            poetry
            git
          ];
          
          shellHook = ''
            poetry install --no-interaction
            poetry run pytest tests/
          '';
        };
        
        # Documentation shell
        devShells.docs = pkgs.mkShell {
          buildInputs = with pkgs; [
            pythonEnv
            poetry
            pandoc
          ];
          
          shellHook = ''
            poetry install --no-interaction
            echo "Run: poetry run mkdocs serve"
          '';
        };
      });
}