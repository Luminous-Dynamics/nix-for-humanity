{
  description = "Luminous Nix - Natural language interface for NixOS with poetry2nix";
  
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
        poetry2nix-lib = poetry2nix.lib.mkPoetry2Nix { inherit pkgs; };
        inherit (poetry2nix-lib) mkPoetryApplication mkPoetryEnv defaultPoetryOverrides;
        
        # Common overrides for problematic Python packages
        pypkgs-build-requirements = {
          # Packages that need special build inputs
          duckdb = [ "pybind11" "setuptools" ];
          kuzu = [ "pybind11" "cmake" "setuptools" ];
          tree-sitter = [ "setuptools" ];
          faiss-cpu = [ "swig" "setuptools" ];
          llama-cpp-python = [ "cmake" "setuptools" ];
          chromadb = [ "setuptools" "wheel" ];
          # Fix for semgrep/jsonschema issues
          semgrep = [ "setuptools" "wheel" ];
          jsonschema = [ "setuptools" "wheel" ];
        };
        
        overrides = defaultPoetryOverrides.extend
          (self: super: 
            let
              # Handle packages that have platform issues
              platformFixes = {
                # Skip problematic packages or provide alternatives
                semgrep = super.semgrep.overridePythonAttrs (old: {
                  doCheck = false;
                  pythonImportsCheck = [];
                });
                jsonschema = super.jsonschema.overridePythonAttrs (old: {
                  doCheck = false;
                });
              };
              
              # Build requirement overrides
              buildReqOverrides = builtins.mapAttrs (package: reqs:
                if builtins.hasAttr package super then
                  (builtins.getAttr package super).overridePythonAttrs (old: {
                    buildInputs = (old.buildInputs or [ ]) ++ (builtins.map (pkg: 
                      if builtins.isString pkg then pkgs.python3.pkgs.${pkg} else pkg
                    ) reqs);
                  })
                else super.${package} or null
              ) pypkgs-build-requirements;
            in
              platformFixes // buildReqOverrides
          );
        
        # The main application (without problematic extras)
        luminousNixApp = mkPoetryApplication {
          projectDir = ./.;
          preferWheels = true;  # Use pre-built wheels when available
          
          # Override problematic packages
          inherit overrides;
          
          # Groups to include (empty means just core dependencies)
          groups = [ ];
          
          # Skip extras that have problematic packages
          # Don't include "security" which has semgrep
          extras = [ "tui" "voice" "docs" ];  # Skip "security", "all"
          
          meta = with pkgs.lib; {
            description = "Natural language interface for NixOS";
            homepage = "https://github.com/Luminous-Dynamics/luminous-nix";
            license = licenses.mit;
            mainProgram = "ask-nix";
          };
        };
        
        # Development environment (skip problematic security packages)
        devEnv = mkPoetryEnv {
          projectDir = ./.;
          preferWheels = true;
          inherit overrides;
          
          # Include dev dependencies but skip security extras
          groups = [ "dev" ];
          extras = [ "tui" "voice" "docs" "learning" ];  # Skip "security", "all"
        };
        
        # Documentation environment (includes MkDocs)
        docsEnv = mkPoetryEnv {
          projectDir = ./.;
          preferWheels = true;
          groups = [ "dev" ];  # MkDocs is in dev group
        };
        
      in {
        # The main package
        packages = {
          default = luminousNixApp;
          luminous-nix = luminousNixApp;
          
          # Documentation builder
          docs = pkgs.writeShellScriptBin "luminous-nix-docs" ''
            ${docsEnv}/bin/mkdocs "$@"
          '';
          
          # Docker image
          docker = pkgs.dockerTools.buildImage {
            name = "luminous-nix";
            tag = "latest";
            contents = [ luminousNixApp ];
            config = {
              Cmd = [ "${luminousNixApp}/bin/ask-nix" ];
            };
          };
        };
        
        # Development shell with all tools
        devShells = {
          default = pkgs.mkShell {
            buildInputs = with pkgs; [
              # The Poetry environment with all dependencies
              devEnv
              
              # Development tools
              poetry
              ruff
              black
              mypy
              
              # System dependencies needed for development
              gcc
              stdenv.cc.cc.lib
              zlib
              
              # For voice features
              portaudio
              ffmpeg
              
              # For building documentation
              docsEnv
              
              # Git and other tools
              git
              gh
              pre-commit
              
              # Nix tools
              nix-prefetch-git
              nixpkgs-fmt
              nil  # Nix LSP
            ];
            
            shellHook = ''
              echo "🌟 Luminous Nix Development Environment"
              echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
              echo "Available commands:"
              echo "  ask-nix       - Run the CLI"
              echo "  nix-tui       - Launch the TUI"
              echo "  poetry        - Manage dependencies"
              echo "  mkdocs serve  - Serve documentation"
              echo "  pytest        - Run tests"
              echo ""
              echo "Python: $(python --version)"
              echo "Poetry: $(poetry --version)"
              echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
              
              # Set up environment variables
              export LUMINOUS_NIX_DEV=1
              export PYTHONPATH="$PWD/src:$PYTHONPATH"
              
              # Activate the poetry environment if it exists
              if [ -f .venv/bin/activate ]; then
                source .venv/bin/activate
              fi
            '';
            
            # Environment variables
            LUMINOUS_NIX_DEV = "1";
            LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.zlib}/lib";
          };
          
          # Minimal shell for CI/CD
          ci = pkgs.mkShell {
            buildInputs = with pkgs; [
              devEnv
              poetry
              git
            ];
          };
          
          # Documentation shell
          docs = pkgs.mkShell {
            buildInputs = with pkgs; [
              docsEnv
              poetry
            ];
            shellHook = ''
              echo "📚 Documentation Environment"
              echo "Run 'mkdocs serve' to start the docs server"
            '';
          };
        };
        
        # Apps that can be run with `nix run`
        apps = {
          default = flake-utils.lib.mkApp {
            drv = luminousNixApp;
            name = "ask-nix";
          };
          
          ask-nix = flake-utils.lib.mkApp {
            drv = luminousNixApp;
            name = "ask-nix";
          };
          
          nix-tui = flake-utils.lib.mkApp {
            drv = luminousNixApp;
            name = "nix-tui";
          };
          
          docs = flake-utils.lib.mkApp {
            drv = self.packages.${system}.docs;
            name = "luminous-nix-docs";
          };
        };
        
        # Checks for CI
        checks = {
          luminous-nix = luminousNixApp;
          
          # Add test runner
          tests = pkgs.runCommand "luminous-nix-tests" {
            buildInputs = [ devEnv ];
          } ''
            cd ${./.}
            pytest tests/ -v
            touch $out
          '';
        };
      });
}
