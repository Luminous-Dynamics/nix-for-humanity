{
  description = "Luminous Nix - Testing poetry2nix migration";

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
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryEnv mkPoetryApplication;
        
        # Create environment from pyproject.toml and poetry.lock
        poetryEnv = mkPoetryEnv {
          projectDir = ./.;
          python = pkgs.python311;
          preferWheels = true;  # Use pre-built wheels when available
          
          # Handle any remaining problematic packages
          overrides = poetry2nix.lib.defaultPoetryOverrides.extend
            (self: super: {
              # Override specific packages if needed
              # For example, packages with C extensions
              duckdb = super.duckdb.override {
                preferWheel = true;
              };
              chromadb = super.chromadb.override {
                preferWheel = true;
              };
              kuzu = super.kuzu.override {
                preferWheel = true;
              };
            });
        };
        
        # Build the application
        app = mkPoetryApplication {
          projectDir = ./.;
          python = pkgs.python311;
          preferWheels = true;
        };
        
      in
      {
        packages = {
          default = app;
          env = poetryEnv;
        };
        
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            poetryEnv
            poetry
            
            # System libraries for Data Trinity
            stdenv.cc.cc.lib
            
            # Development tools
            git
            gnumake
            nodejs
          ];
          
          shellHook = ''
            echo "🌟 Luminous Nix - Poetry2nix Environment"
            echo "========================================="
            echo "✅ mkdocstrings removed - no infinite recursion!"
            echo "✅ All dependencies from poetry.lock"
            echo "✅ Data Trinity libraries included"
            echo ""
            echo "Python: $(python --version)"
            echo "Poetry: $(poetry --version)"
            echo ""
            echo "Available commands:"
            echo "  ask-nix - Natural language NixOS interface"
            echo "  nix-tui - Beautiful terminal UI"
            echo ""
            export LD_LIBRARY_PATH=${pkgs.stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH
          '';
        };
        
        apps.default = {
          type = "app";
          program = "${app}/bin/ask-nix";
        };
      });
}