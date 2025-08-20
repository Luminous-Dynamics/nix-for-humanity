# Nix shell for database dependencies
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    # Python and Poetry
    python313
    poetry
    
    # C++ libraries needed for DuckDB and Kùzu
    stdenv.cc.cc.lib
    gcc
    
    # Additional libraries that might be needed
    zlib
    bzip2
    openssl
    
    # Build tools
    pkg-config
    cmake
  ];
  
  shellHook = ''
    echo "🌟 Database Development Shell"
    echo "This provides the C++ libraries needed for DuckDB and Kùzu"
    echo ""
    echo "Run: poetry run python create_data_trinity_schema.py"
    echo ""
    
    # Set library paths
    export LD_LIBRARY_PATH=${pkgs.stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH
  '';
}