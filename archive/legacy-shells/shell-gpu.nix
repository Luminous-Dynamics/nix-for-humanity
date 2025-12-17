# Deprecated: use flake devShells instead (nix develop .#gpu)
# Nix shell for GPU-accelerated Luminous Nix development
# Provides ONNX Runtime and CUDA dependencies

{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "luminous-nix-gpu";
  
  buildInputs = with pkgs; [
    # Python and Poetry
    python311
    poetry
    
    # CUDA support (if NVIDIA GPU available)
    cudaPackages.cudatoolkit
    cudaPackages.cudnn
    
    # System libraries needed for ONNX Runtime
    gcc
    glibc
    stdenv.cc.cc.lib
    
    # OpenCL support (for Intel/AMD GPUs)
    ocl-icd
    opencl-headers
    
    # GPU utilities
    pciutils  # For lspci
    nvtop     # GPU monitoring
    
    # Audio for TTS
    portaudio
    sox       # For voice effects
    
    # Python packages (system-wide for shell)
    (python311.withPackages (ps: with ps; [
      numpy
      pip
      setuptools
      wheel
      # Note: onnxruntime-gpu must be installed via pip
      # as Nix package may be outdated
    ]))
  ];
  
  shellHook = ''
    echo "🚀 Luminous Nix GPU Development Shell"
    echo "======================================"
    echo
    
    # Check for NVIDIA GPU
    if command -v nvidia-smi &> /dev/null; then
      echo "✅ NVIDIA GPU detected"
      nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || echo "⚠️  Driver issue detected"
    else
      echo "ℹ️  No NVIDIA GPU detected"
    fi
    echo
    
    echo "📦 Installing ONNX Runtime GPU support..."
    echo "To install in your Poetry environment:"
    echo "  poetry shell"
    echo "  pip install onnxruntime-gpu  # For NVIDIA"
    echo "  pip install onnxruntime      # For CPU only"
    echo
    
    echo "🧪 Test commands:"
    echo "  python3 piper_gpu_accelerated.py --detect"
    echo "  python3 piper_gpu_accelerated.py --benchmark"
    echo
    
    # Set CUDA environment if available
    if [ -d "${cudaPackages.cudatoolkit}/lib" ]; then
      export CUDA_PATH="${cudaPackages.cudatoolkit}"
      export CUDA_HOME="${cudaPackages.cudatoolkit}"
      export LD_LIBRARY_PATH="${cudaPackages.cudatoolkit}/lib:${cudaPackages.cudnn}/lib:$LD_LIBRARY_PATH"
      echo "✅ CUDA environment configured"
    fi
    
    # Activate Poetry if pyproject.toml exists
    if [ -f "pyproject.toml" ]; then
      echo
      echo "📚 Poetry project detected"
      echo "Run 'poetry shell' to activate the environment"
    fi
  '';
  
  # Environment variables
  CUDA_PATH = "${pkgs.cudaPackages.cudatoolkit}";
  CUDA_HOME = "${pkgs.cudaPackages.cudatoolkit}";
  
  # Allow unfree packages (needed for CUDA)
  NIXPKGS_ALLOW_UNFREE = "1";
}
