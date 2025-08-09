{ pkgs ? import <nixpkgs> {} }:

let
  # Python environment with all voice dependencies
  pythonEnv = pkgs.python311.withPackages (ps: with ps; [
    # Core voice dependencies
    openai-whisper
    sounddevice
    numpy
    scipy
    
    # Audio processing
    librosa
    pyaudio
    
    # For Whisper
    torch
    torchvision
    torchaudio
    transformers
    
    # Additional dependencies
    requests
    tqdm
    more-itertools
  ]);
  
  # Piper TTS with voice models
  piperTTS = pkgs.piper-tts;
  
  # Voice models
  piperVoices = pkgs.fetchzip {
    url = "https://github.com/rhasspy/piper/releases/download/v1.0.0/voices.tar.gz";
    sha256 = "sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="; # Replace with actual
    stripRoot = false;
  };
  
  # Whisper models
  whisperModels = pkgs.runCommand "whisper-models" {} ''
    mkdir -p $out/share/whisper
    
    # Download models (in practice, you'd fetch these properly)
    # ${pkgs.wget}/bin/wget -O $out/share/whisper/base.pt \
    #   https://openaipublic.azureedge.net/main/whisper/models/base.pt
  '';

in pkgs.mkShell {
  name = "nix-humanity-voice";
  
  buildInputs = with pkgs; [
    # Python with all packages
    pythonEnv
    
    # Piper TTS
    piperTTS
    
    # Audio tools
    sox
    ffmpeg
    portaudio
    
    # System audio
    alsa-lib
    pulseaudio
  ];
  
  shellHook = ''
    echo "🎤 Nix for Humanity Voice Environment"
    echo "===================================="
    echo ""
    echo "Voice dependencies loaded:"
    echo "✅ Whisper (OpenAI speech recognition)"
    echo "✅ Piper TTS (text-to-speech)"
    echo "✅ Audio libraries (sounddevice, portaudio)"
    echo ""
    
    # Set up paths
    export PIPER_VOICE_DIR="$HOME/.local/share/piper/voices"
    export WHISPER_MODEL_DIR="$HOME/.cache/whisper"
    
    # Create directories
    mkdir -p "$PIPER_VOICE_DIR"
    mkdir -p "$WHISPER_MODEL_DIR"
    
    # Function to download Piper voices
    download_piper_voice() {
      local voice_name="$1"
      local voice_url="https://github.com/rhasspy/piper/releases/download/v1.0.0"
      
      if [ ! -f "$PIPER_VOICE_DIR/$voice_name.onnx" ]; then
        echo "📥 Downloading Piper voice: $voice_name"
        ${pkgs.wget}/bin/wget -q -O "$PIPER_VOICE_DIR/$voice_name.onnx" \
          "$voice_url/$voice_name.onnx"
        ${pkgs.wget}/bin/wget -q -O "$PIPER_VOICE_DIR/$voice_name.onnx.json" \
          "$voice_url/$voice_name.onnx.json"
        echo "✅ Voice downloaded: $voice_name"
      else
        echo "✅ Voice already available: $voice_name"
      fi
    }
    
    # Download default voice
    download_piper_voice "en_US-amy-medium"
    
    echo ""
    echo "To download additional voices:"
    echo "  download_piper_voice <voice-name>"
    echo ""
    echo "Available commands:"
    echo "  ./bin/nix-voice     - Start voice interface"
    echo "  ./setup_voice.py    - Run setup wizard"
    echo "  python -m whisper   - Test Whisper directly"
    echo "  piper --help        - Test Piper directly"
    echo ""
  '';
  
  # Environment variables
  PYTHONPATH = "$PYTHONPATH:${toString ./.}";
  NIX_HUMANITY_VOICE_ENABLED = "true";
  
  # Prevent pip from being used
  PIP_REQUIRE_VIRTUALENV = "true";
}