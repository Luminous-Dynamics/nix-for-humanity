## Deprecated: use flake devShells instead (nix develop)
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "huggingface-auth-shell";
  
  buildInputs = with pkgs; [
    # Python with huggingface-hub which includes the CLI
    (python312.withPackages (ps: with ps; [
      huggingface-hub
      transformers
      torch
      safetensors
      tokenizers
    ]))
  ];
  
  shellHook = ''
    echo "🤗 HuggingFace Authentication Shell"
    echo "===================================="
    echo ""
    echo "Available commands:"
    echo "  huggingface-cli login    - Login to HuggingFace"
    echo "  huggingface-cli whoami   - Check current auth status"
    echo "  huggingface-cli scan     - Scan cache for models"
    echo "  huggingface-cli download - Download models"
    echo ""
    echo "Python with huggingface-hub is available"
    echo ""
    
    # Check if already authenticated
    python -c "
from huggingface_hub import whoami
try:
    info = whoami()
    print('✅ Already authenticated as:', info['name'])
except:
    print('⚠️  Not authenticated. Run: huggingface-cli login')
" 2>/dev/null || true
  '';
}
