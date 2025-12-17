## Deprecated: use flake devShells instead (nix develop .#voice or .#gpu)
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    # Python with packages
    (python311.withPackages(ps: with ps; [
      pip
      setuptools
      wheel
      numpy
      torch
      torchaudio
      torchvision
      # openai-whisper is not in nixpkgs yet
    ]))
    
    # System libraries needed by PyTorch
    stdenv.cc.cc.lib
    zlib
    libGL
    libGLU
    
    # Audio libraries for Whisper
    ffmpeg
    portaudio
  ];
  
  shellHook = ''
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.zlib}/lib:$LD_LIBRARY_PATH"
    echo "🌟 NixOS PyTorch environment activated!"
    echo "   PyTorch should now import correctly"
    echo "   Run: python -c 'import torch; print(torch.__version__)'"
  '';
}
