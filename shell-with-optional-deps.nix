{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "luminous-nix-optional-deps";
  
  buildInputs = with pkgs; [
    # Python with scientific/ML packages
    (python311.withPackages (ps: with ps; [
      # Core dependencies (already in main shell.nix)
      click
      rich
      prompt-toolkit
      requests
      
      # Optional dependencies for v0.6.1 features
      numpy           # For ML health predictions
      pyyaml          # For POML processing
      scikit-learn    # For advanced ML features
      pandas          # For data analysis
      matplotlib      # For visualization
      
      # Additional useful packages
      scipy           # Scientific computing
      statsmodels     # Statistical modeling
    ]))
    
    # System dependencies
    gcc
    pkg-config
    
    # Development tools
    poetry
    ruff
    black
  ];
  
  shellHook = ''
    echo "🌟 Luminous Nix Development Shell - With Optional Dependencies"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ numpy available for ML features"
    echo "✅ pyyaml available for POML processing"
    echo "✅ scikit-learn for advanced ML"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "To test with optional dependencies:"
    echo "  python test_v0.6.1_integration.py"
    echo ""
    echo "To run Luminous Nix with full features:"
    echo "  ./bin/ask-nix --help"
    echo ""
    
    # Set environment variables
    export LUMINOUS_NIX_OPTIONAL_DEPS=1
    export PYTHONPATH="$PWD/src:$PYTHONPATH"
  '';
}