## Deprecated: use flake devShells instead (nix develop)
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    # Python and core packages
    python311
    python311Packages.numpy
    python311Packages.torch
    python311Packages.scipy
    python311Packages.scikit-learn
    python311Packages.pandas
    
    # System libraries needed
    zlib
    stdenv.cc.cc.lib
    blas
    lapack
    
    # Poetry for package management
    poetry
  ];
  
  shellHook = ''
    echo "🌟 NumPy-enabled environment loaded!"
    echo "Run: poetry install && poetry run python"
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.zlib}/lib:$LD_LIBRARY_PATH"
  '';
}
