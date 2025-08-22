{
  description = "Nix for Humanity - Natural Language Interface for NixOS";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    rust-overlay.url = "github:oxalica/rust-overlay";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, rust-overlay, poetry2nix }:
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
        
        # Poetry2nix for Python dependencies
        poetry2nix-lib = poetry2nix.lib.mkPoetry2Nix { inherit pkgs; };
        
        # Create Python environment from pyproject.toml
        # Create Python environment with TUI dependencies manually
        # This avoids poetry2nix complexity for now
        poetryEnv = pkgs.python311.withPackages (ps: with ps; [
          # Core dependencies from pyproject.toml
          requests
          click
          colorama
          python-dotenv
          
          # TUI dependencies (from extras.tui)
          textual
          rich
          blessed
          pyperclip
          
          # Tree-sitter for AST parsing (Phase A-Prime)
          tree-sitter
          # Note: tree-sitter-nix grammar will be built separately
          
          # Other useful packages for development
          pyyaml
          pytest
          pytest-asyncio
          pytest-cov
          pytest-mock
          ipython
        ]);
        
        # Also create a Python 3.13 environment for main app (without heavy research deps)
        pythonMainEnv = pkgs.python313.withPackages (ps: with ps; [
          pip
          virtualenv
          flask
          gunicorn
          requests
          pytest
          pytest-asyncio
          pytest-cov
          pytest-mock
          pyyaml
          rich
          click
          colorama
          python-dotenv
        ]);
        
        # Create TUI runner script
        runTuiApp = pkgs.writeShellScriptBin "run-tui-app" ''
          #!/usr/bin/env bash
          set -e
          
          echo "🌟 Launching Nix for Humanity TUI..."
          echo "All dependencies are handled by Nix - no pip install needed!"
          echo
          
          cd ${toString ./.}
          export PYTHONPATH="${toString ./.}:$PYTHONPATH"
          
          # Launch the TUI with poetry2nix-managed Python
          exec ${poetryEnv}/bin/python -m nix_humanity.interfaces.tui "$@"
        '';
        
        # Create Grandma Mode launcher
        grandmaNix = pkgs.writeShellScriptBin "grandma-nix" ''
          #!/usr/bin/env bash
          set -e
          
          cd ${toString ./.}
          export PYTHONPATH="${toString ./.}/src:$PYTHONPATH"
          
          # Launch Grandma Mode with proper Python environment
          exec ${poetryEnv}/bin/python ${toString ./.}/bin/grandma-nix "$@"
        '';
        
        # Create main ask-nix launcher
        askNix = pkgs.writeShellScriptBin "ask-nix" ''
          #!/usr/bin/env bash
          set -e
          
          cd ${toString ./.}
          export PYTHONPATH="${toString ./.}/src:$PYTHONPATH"
          export NIX_HUMANITY_PYTHON_BACKEND=true
          
          # Launch with proper Python environment
          exec ${poetryEnv}/bin/python ${toString ./.}/bin/ask-nix "$@"
        '';
        
        # Create our custom ask-nix-guru command
        askNixGuru = pkgs.writeShellScriptBin "ask-nix-guru" ''
          #!/usr/bin/env bash
          
          # Sacred Trinity: Human asks, Local LLM answers with NixOS expertise
          
          if [ $# -eq 0 ]; then
            echo "🧙 Ask the Nix Guru anything about NixOS!"
            echo "Usage: ask-nix-guru 'How do I install a package?'"
            exit 1
          fi
          
          QUESTION="$*"
          
          # Check if ollama is running
          if ! ${pkgs.curl}/bin/curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
            echo "⚠️  Starting Ollama service..."
            ${pkgs.ollama}/bin/ollama serve &
            sleep 5
          fi
          
          # Model selection - Mistral-7B is our default for Sacred Trinity
          DEFAULT_MODEL="mistral:7b"
          MODEL=''${NIX_GURU_MODEL:-$DEFAULT_MODEL}
          
          # Sacred Trinity Model Choice: Mistral-7B
          # - Perfect balance of performance and accuracy
          # - Runs smoothly on 6GB RAM (accessible to most)
          # - Excellent NixOS technical understanding
          # - Fast response times for interactive development
          #
          # Alternative models (set NIX_GURU_MODEL to override):
          # - deepseek-coder:6.7b - Code-focused (8GB RAM)
          # - codellama:13b-instruct - More detailed explanations (16GB RAM)
          # - mixtral:8x7b - Best quality but needs 32GB RAM
          # - phi:2.7b - Tiny model for limited RAM (3GB)
          
          echo "📊 Using model: $MODEL"
          
          # Check if model exists, pull if not
          if ! ${pkgs.ollama}/bin/ollama list | grep -q "$MODEL"; then
            echo "📥 Downloading $MODEL (this happens once)..."
            ${pkgs.ollama}/bin/ollama pull $MODEL
          fi
          
          # Craft a NixOS-specific prompt
          PROMPT="You are a NixOS expert. Answer this question concisely and accurately: $QUESTION
          
          Focus on:
          1. Practical NixOS/Nix solutions
          2. Correct syntax and best practices
          3. Common pitfalls to avoid
          
          Answer:"
          
          echo "🤔 Consulting the Nix Guru..."
          echo
          
          # Query the model
          ${pkgs.ollama}/bin/ollama run $MODEL "$PROMPT" 2>/dev/null
          
          echo
          echo "💡 Tip: Save useful answers to docs/nix-knowledge/ for training data!"
        '';
      in
      {
        # Development shell
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # Rust toolchain
            rustToolchain
            pkg-config
            
            # Tauri dependencies
            webkitgtk_4_1  # Uses libsoup3 (secure)
            librsvg
            
            # Node.js for frontend
            nodejs_20
            nodePackages.npm
            
            # Build tools
            openssl
            cmake
            
            # Development tools
            nodePackages.typescript
            nodePackages.pnpm
            # vite and tsx are installed via npm/pnpm
            
            # System tools for testing
            curl
            jq
            
            # Python environments
            poetryEnv          # Python 3.11 with all research dependencies
            pythonMainEnv      # Python 3.13 for main application
            
            # Voice interface dependencies
            (python311.withPackages (ps: with ps; [
              openai-whisper
              sounddevice
              numpy
              pyaudio
              torch
              torchaudio
            ]))
            piper-tts       # Text-to-speech
            portaudio       # Audio I/O
            espeak-ng       # TTS fallback
            ffmpeg          # Audio processing
            sox             # Sound processing
            
            # ActivityWatch for user behavior monitoring
            activitywatch   # Privacy-first activity tracking
            
            # Documentation tools
            mdbook
            pandoc
            
            # NixOS specific tools
            nix-prefetch-git
            nixfmt
            nil # Nix LSP
            
            # Local LLM integration
            ollama
            askNixGuru
            
            # TUI launcher
            runTuiApp
            
            # Grandma Mode and ask-nix launchers
            grandmaNix
            askNix
            
            # Development utilities
            git
            ripgrep
            fd
            yq
            httpie
            
            # Quality tools
            shellcheck
            hadolint
            
            # Demo creation tools
            vhs              # Terminal GIF recorder (Charm)
            asciinema        # Terminal session recorder
            imagemagick      # Image conversion (SVG to PNG)
            ffmpeg-full      # Video processing
            gifsicle         # GIF optimization
            termtosvg        # Terminal to SVG converter
            
            # Enhanced tools from our integration
            llama-cpp        # Ultra-fast local LLM inference
            faiss            # Facebook AI Similarity Search
            gum              # Charm's beautiful CLI interactions
            charm-freeze     # Generate beautiful code screenshots
            # mistral-rs     # Rust-based Mistral (if available)
            
            # Code quality tools (system-level)
            ruff             # Ultra-fast Python linter
            black            # Python formatter
            mypy             # Type checker
            bandit           # Security scanner
          ];

          shellHook = ''
            echo "🌟 Welcome to Nix for Humanity Development Environment! 🌟"
            echo "========================================================="
            echo "Rust: $(rustc --version)"
            echo "Node.js: $(node --version)"
            echo "npm: $(npm --version)"
            echo "TypeScript: $(tsc --version)"
            echo ""
            echo "🐍 Python Environments:"
            echo "  Python 3.11 (research): Available via poetry environment"
            echo "  Python 3.13 (main app): Available as python3.13"
            echo "  Use poetry environment for full feature set including DoWhy"
            echo ""
            echo "📚 Available commands:"
            echo "  grandma-nix       - REAL NixOS for non-technical users"
            echo "  ask-nix           - Natural language NixOS interface"
            echo "  run-tui-app       - Launch the beautiful TUI (no pip install needed!)"
            echo "  ask-nix-guru      - Query local LLM for NixOS expertise"
            echo "  npm test          - Run NLP engine tests"
            echo "  npm run build     - Build all packages"
            echo "  npm run tauri:dev - Start Tauri development"
            echo "  npm run tauri:build - Build Tauri app"
            echo ""
            echo "🎬 Demo creation tools:"
            echo "  vhs demo-tui.tape - Create high-quality terminal GIFs"
            echo "  asciinema rec    - Record terminal sessions"
            echo "  ./create-demo-nixos.sh - Guided demo creation"
            echo ""
            echo "📊 ActivityWatch Integration:"
            echo "  aw-qt             - Start ActivityWatch GUI"
            echo "  aw-server         - Start headless server"
            echo "  Web UI: http://localhost:5600"
            echo ""
            echo "🤖 Sacred Trinity Workflow:"
            echo "  1. Human (you) provides vision and requirements"
            echo "  2. Claude architects the solution"
            echo "  3. Local LLM provides NixOS-specific expertise"
            echo ""
            echo "💡 Example: ask-nix-guru 'How do I create a systemd service in NixOS?'"
            echo ""
            
            # Set up project-specific env vars
            export NIX_FOR_HUMANITY_ROOT="$PWD"
            export NODE_ENV="development"
            
            # Ensure Ollama data directory exists
            mkdir -p ~/.ollama
            
            # Create knowledge collection directory
            mkdir -p docs/nix-knowledge/{questions,answers,examples}
            
            echo "✨ Environment ready! Let's democratize NixOS together!"
          '';
          
          # Environment variables for Tauri
          WEBKIT_DISABLE_COMPOSITING_MODE = "1";
        };

        # Package
        packages = {
          default = self.packages.${system}.luminous-nix;
          luminous-nix = self.packages.${system}.nix-for-humanity;  # Alias for compatibility
          ask-nix-guru = askNixGuru;
          grandma-nix = grandmaNix;
          ask-nix = askNix;
          run-tui-app = runTuiApp;
          ollama = pkgs.ollama;
          
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
              webkitgtk_4_1  # Uses libsoup3 (secure)
              librsvg
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
              license = licenses.mit;
              maintainers = with maintainers; [ ]; # Add maintainers
              platforms = platforms.linux;
            };
          };
        };

        # App runner for development
        apps = {
          default = flake-utils.lib.mkApp {
            drv = grandmaNix;  # Default to Grandma Mode for accessibility
          };
          grandma-nix = flake-utils.lib.mkApp {
            drv = grandmaNix;
          };
          ask-nix = flake-utils.lib.mkApp {
            drv = askNix;
          };
          ask-nix-guru = flake-utils.lib.mkApp {
            drv = askNixGuru;
          };
          run-tui-app = flake-utils.lib.mkApp {
            drv = runTuiApp;
          };
        };
      }
    ) // {
      # NixOS modules
      nixosModules = {
        default = { config, lib, pkgs, ... }: with lib; {
          options.programs.nix-for-humanity = {
            enable = mkEnableOption "Nix for Humanity - Natural Language Interface for NixOS";
          };
          
          config = mkIf config.programs.nix-for-humanity.enable {
            environment.systemPackages = [ self.packages.${pkgs.system}.nix-for-humanity ];
          };
        };
        
        # Voice interface module
        voice = import ./modules/voice.nix;
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