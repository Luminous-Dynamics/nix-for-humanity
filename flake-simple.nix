{
  description = "Luminous Nix - Simplified poetry2nix flake";
  
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };
  
  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        
        # Use poetry2nix with minimal configuration
        poetry2nix-lib = poetry2nix.lib.mkPoetry2Nix { inherit pkgs; };
        
        # Simple Poetry environment without complex overrides
        poetryEnv = poetry2nix-lib.mkPoetryEnv {
          projectDir = ./.;
          preferWheels = true;
          
          # Skip problematic packages for now
          overrides = poetry2nix-lib.defaultPoetryOverrides.extend (self: super: {
            # Disable checks for packages that cause issues
            semgrep = null;  # Skip semgrep entirely
            jsonschema = super.jsonschema.overridePythonAttrs (old: {
              doCheck = false;
            });
            duckdb = super.duckdb.overridePythonAttrs (old: {
              doCheck = false;
              buildInputs = (old.buildInputs or []) ++ [ pkgs.python3.pkgs.pybind11 ];
            });
            chromadb = super.chromadb.overridePythonAttrs (old: {
              doCheck = false;
            });
          });
        };
        
      in {
        # Simple development shell that should work
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # Basic Python environment from Poetry
            poetryEnv
            
            # Essential tools
            poetry
            git
            
            # Python development tools
            python3
            python3.pkgs.pip
            
            # System dependencies
            gcc
            stdenv.cc.cc.lib
            zlib
          ];
          
          shellHook = ''
            echo "🌟 Luminous Nix - Simplified Development Environment"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            echo "This is a simplified environment that skips"
            echo "problematic packages. Use for basic development."
            echo ""
            echo "Available:"
            echo "  poetry     - Manage dependencies"
            echo "  python     - Python interpreter"
            echo "  git        - Version control"
            echo ""
            echo "To use:"
            echo "  poetry install"
            echo "  poetry run ask-nix help"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
          '';
          
          # Environment variables
          PYTHONPATH = "$PWD/src:$PYTHONPATH";
          LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.zlib}/lib";
        };
        
        # Fallback to traditional Poetry workflow
        devShells.poetry = pkgs.mkShell {
          buildInputs = with pkgs; [
            python3
            poetry
            gcc
            stdenv.cc.cc.lib
          ];
          
          shellHook = ''
            echo "📦 Traditional Poetry Environment"
            echo "Run: poetry install && poetry run ask-nix help"
          '';
        };
      });
}