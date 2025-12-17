## Deprecated: use flake devShells instead (nix develop .#gpu)
{ pkgs ? import <nixpkgs> { config.allowUnfree = true; } }:

pkgs.mkShell {
  name = "vllm-gemma-shell";
  
  buildInputs = with pkgs; [
    # Python with all needed packages
    (python312.withPackages (ps: with ps; [
      huggingface-hub
      transformers
      torch
      torchvision
      torchaudio
      safetensors
      tokenizers
      accelerate
      sentencepiece
      protobuf
      numpy
      scipy
      
      # For vLLM installation
      pip
      setuptools
      wheel
      packaging
      psutil
      ray
      aiohttp
      fastapi
      uvicorn
    ]))
    
    # System dependencies
    gcc
    stdenv.cc.cc.lib
  ];
  
  shellHook = ''
    echo "🚀 vLLM + Gemma Shell Environment (Simple)"
    echo "=========================================="
    echo ""
    
    # Set up environment
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH"
    
    # Disable Ray for single GPU
    export VLLM_SKIP_RAY=1
    
    # Check authentication
    python -c "
from huggingface_hub import whoami
try:
    info = whoami()
    print('✅ HuggingFace authenticated as:', info['name'])
except:
    print('⚠️  Not authenticated. Token should be at ~/.cache/huggingface/token')
" 2>/dev/null || true
    
    # Check for vLLM
    if ! python -c "import vllm" 2>/dev/null; then
      echo ""
      echo "⚠️  vLLM not installed. Install with:"
      echo "    pip install vllm"
    else
      echo "✅ vLLM is available"
    fi
    
    echo ""
    echo "Commands:"
    echo "  pip install vllm         - Install vLLM"
    echo "  python test_vllm_gemma.py - Test Gemma models"
    echo ""
  '';
}
