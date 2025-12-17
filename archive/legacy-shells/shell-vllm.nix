## Deprecated: use flake devShells instead (nix develop .#gpu)
{ pkgs ? import <nixpkgs> {} }:

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
      
      # For vLLM
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
    
    # System dependencies for vLLM
    gcc
    stdenv.cc.cc.lib
    cudaPackages.cudatoolkit
    cudaPackages.cudnn
    ncurses
    zlib
  ];
  
  shellHook = ''
    echo "🚀 vLLM + Gemma Shell Environment"
    echo "=================================="
    echo ""
    
    # Set up environment for CUDA
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.cudaPackages.cudatoolkit}/lib:$LD_LIBRARY_PATH"
    export CUDA_HOME="${pkgs.cudaPackages.cudatoolkit}"
    
    # Disable Ray if needed for single GPU
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
      echo "    pip install vllm --no-deps"
      echo "    pip install vllm-flash-attn xformers"
    else
      echo "✅ vLLM is available"
    fi
    
    echo ""
    echo "Available commands:"
    echo "  python test_vllm_gemma.py   - Test Gemma models with vLLM"
    echo "  python test_gemma_models.py - Download and test all Gemma models"
    echo ""
  '';
}
