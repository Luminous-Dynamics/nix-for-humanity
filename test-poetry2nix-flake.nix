{
  description = "Test poetry2nix with mkdocstrings removed";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, poetry2nix, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryEnv;
        
        # Test if we can build the environment now
        poetryEnv = mkPoetryEnv {
          projectDir = ./.;
          python = pkgs.python311;
          preferWheels = true;
        };
        
      in
      {
        packages.default = poetryEnv;
        
        devShells.default = pkgs.mkShell {
          buildInputs = [ poetryEnv ];
          
          shellHook = ''
            echo "✅ Poetry2nix environment builds successfully!"
            echo "mkdocstrings removed - no more infinite recursion!"
            python --version
          '';
        };
      });
}