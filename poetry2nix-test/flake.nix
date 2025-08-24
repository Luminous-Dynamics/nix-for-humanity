{
  description = "Luminous Nix - Natural Language Interface for NixOS (poetry2nix version)";

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
        
        # Create poetry2nix instance
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) 
          mkPoetryApplication 
          mkPoetryEnv 
          overrides;
        
        # Python version to use
        python = pkgs.python311;
        
        # Common overrides for problematic packages
        commonOverrides = overrides.withDefaults (final: prev: {
          # Fix for packages that need compilation
          numpy = prev.numpy.override {
            preferWheel = true;
          };
          
          # Fix for torch - use CPU version to avoid CUDA complexity
          torch = prev.torch-bin;
          
          # Fix for tree-sitter - needs compilation
          tree-sitter = prev.tree-sitter.overridePythonAttrs (old: {
            buildInputs = (old.buildInputs or []) ++ [ pkgs.tree-sitter ];
            nativeBuildInputs = (old.nativeBuildInputs or []) ++ [ 
              pkgs.pkg-config 
            ];
          });
          
          # Fix for duckdb
          duckdb = prev.duckdb.override {
            preferWheel = true;
          };
          
          # Fix for chromadb dependencies
          chromadb = prev.chromadb.override {
            preferWheel = true;
          };
          
          # Fix for kuzu
          kuzu = prev.kuzu.override {
            preferWheel = true;
          };
          
          # Fix for faiss-cpu
          faiss-cpu = prev.faiss-cpu.override {
            preferWheel = true;
          };
          
          # Fix for llama-cpp-python
          llama-cpp-python = prev.llama-cpp-python.overridePythonAttrs (old: {
            buildInputs = (old.buildInputs or []) ++ [
              pkgs.llama-cpp
            ];
            preferWheel = false;  # Need to build from source to link with system llama-cpp
          });
          
          # Fix for packages with special dependencies
          openai-whisper = prev.openai-whisper.overridePythonAttrs (old: {
            propagatedBuildInputs = (old.propagatedBuildInputs or []) ++ [
              final.triton-bin  # Use binary version to avoid conflicts
            ];
          });
          
          # Disable some problematic optional dependencies for now
          pandas = prev.pandas.override {
            preferWheel = true;
          };
          
          # Voice packages
          vosk = prev.vosk.override {
            preferWheel = true;
          };
          
          piper-tts = prev.piper-tts.overridePythonAttrs (old: {
            buildInputs = (old.buildInputs or []) ++ [
              pkgs.piper-tts
            ];
          });
          
          # Fix textual and dependencies
          textual = prev.textual.override {
            preferWheel = true;
          };
          
          rich = prev.rich.override {
            preferWheel = true;
          };
        });
        
        # Create the Poetry application
        luminousNixApp = mkPoetryApplication {
          projectDir = ./.;
          python = python;
          overrides = commonOverrides;
          
          # Include all extras by default for full functionality
          extras = [ "tui" "voice" "ml" "advanced" "web" ];
          
          # Prefer wheels where possible for faster builds
          preferWheels = true;
        };
        
        # Create development environment
        poetryDevEnv = mkPoetryEnv {
          projectDir = ./.;
          python = python;
          overrides = commonOverrides;
          
          # Include all extras for development
          extras = [ "tui" "voice" "ml" "advanced" "web" ];
          
          # Enable editable install for development
          editablePackageSources = {
            luminous_nix = ./src;
          };
        };
        
        # System packages needed alongside Python env
        systemPackages = with pkgs; [
          # LLM tools
          ollama
          llama-cpp
          
          # Voice tools
          espeak-ng
          piper-tts
          ffmpeg
          portaudio
          sox
          
          # Development tools
          git
          ripgrep
          fd
          jq
          curl
          httpie
          
          # Demo and documentation tools
          asciinema
          gum
          charm-freeze
          vhs
          imagemagick
          gifsicle
          
          # Code quality tools (system level)
          ruff
          black
          mypy
          bandit
          
          # Activity monitoring
          activitywatch
          
          # Nix tools
          nil
          nixfmt
          nix-prefetch-git
        ];
        
      in {
        # The main package
        packages = {
          default = luminousNixApp;
          
          # Alternative: include the app with system tools
          luminous-nix-full = pkgs.symlinkJoin {
            name = "luminous-nix-full";
            paths = [ luminousNixApp ] ++ systemPackages;
          };
        };
        
        # Development shells
        devShells = {
          # Default: Full poetry2nix environment
          default = pkgs.mkShell {
            buildInputs = [
              poetryDevEnv
              pkgs.poetry  # Keep Poetry for adding new dependencies
            ] ++ systemPackages;
            
            shellHook = ''
              echo "🌟 Luminous Nix Development Environment (poetry2nix)"
              echo "======================================================"
              echo ""
              echo "✨ All Python dependencies managed by Nix!"
              echo "📦 No virtual environment needed!"
              echo "🚀 Binary caching enabled for fast builds!"
              echo ""
              echo "Python: ${python.version}"
              echo "Available: ask-nix, all Python packages from pyproject.toml"
              echo ""
              echo "Tips:"
              echo "  - Edit pyproject.toml and run 'nix develop' to update"
              echo "  - Use 'poetry add <package>' to add new dependencies"
              echo "  - Then exit and re-enter shell to apply changes"
              echo ""
              
              # Set Python path for convenience
              export PYTHONPATH="$PWD/src:$PYTHONPATH"
            '';
          };
          
          # Minimal shell for quick testing
          minimal = pkgs.mkShell {
            buildInputs = [
              poetryDevEnv
            ];
            
            shellHook = ''
              echo "Minimal Luminous Nix shell (Python only)"
              export PYTHONPATH="$PWD/src:$PYTHONPATH"
            '';
          };
          
          # Fallback: Traditional Poetry-based shell (for comparison)
          poetry-classic = import ./shell.nix { inherit pkgs; };
        };
        
        # Apps for direct execution
        apps = {
          # Run ask-nix directly
          ask-nix = flake-utils.lib.mkApp {
            drv = pkgs.writeShellScriptBin "ask-nix" ''
              export PYTHONPATH="${luminousNixApp}/lib/python${python.pythonVersion}/site-packages:$PYTHONPATH"
              exec ${luminousNixApp}/bin/ask-nix "$@"
            '';
          };
          
          # Run the TUI
          nix-tui = flake-utils.lib.mkApp {
            drv = pkgs.writeShellScriptBin "nix-tui" ''
              export PYTHONPATH="${luminousNixApp}/lib/python${python.pythonVersion}/site-packages:$PYTHONPATH"
              exec ${luminousNixApp}/bin/nix-tui "$@"
            '';
          };
        };
        
        # Checks for CI/CD
        checks = {
          # Run tests using poetry2nix environment
          pytest = pkgs.runCommand "pytest-check" {
            buildInputs = [ poetryDevEnv ];
          } ''
            cd ${./.}
            python -m pytest tests/ -v
            touch $out
          '';
          
          # Type checking
          mypy = pkgs.runCommand "mypy-check" {
            buildInputs = [ poetryDevEnv pkgs.mypy ];
          } ''
            cd ${./.}
            mypy src/ --ignore-missing-imports
            touch $out
          '';
          
          # Linting
          ruff = pkgs.runCommand "ruff-check" {
            buildInputs = [ pkgs.ruff ];
          } ''
            cd ${./.}
            ruff check src/
            touch $out
          '';
        };
      });
}