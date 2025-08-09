# Example NixOS configuration with Nix for Humanity voice interface
{ config, pkgs, lib, ... }:

{
  # Import the Nix for Humanity modules
  imports = [
    # Your other imports...
    ./hardware-configuration.nix
    
    # Add Nix for Humanity voice module
    "${builtins.fetchGit {
      url = "https://github.com/Luminous-Dynamics/nix-for-humanity";
      ref = "main";
    }}/modules/voice.nix"
  ];

  # Enable Nix for Humanity with voice interface
  services.nixForHumanity.voice = {
    enable = true;
    
    # Voice recognition settings
    whisperModel = "base";        # Options: tiny, base, small, medium, large
    language = "en";              # Language code for recognition
    device = "cpu";               # Use "cuda" if you have GPU
    
    # Voice synthesis settings
    piperVoice = "en_US-amy-medium";  # Natural sounding voice
    speechRate = 1.0;                 # Normal speed (0.5-2.0)
    
    # Wake word configuration
    wakeWord = "hey nix";         # What to say to activate
    
    # Audio settings
    sampleRate = 16000;           # Audio quality
    chunkDuration = 0.1;          # Response time vs CPU usage
    
    # Automatic setup
    autoDownloadModels = true;    # Download models on first run
  };
  
  # Ensure audio works properly
  sound.enable = true;
  hardware.pulseaudio.enable = true;
  
  # Alternative: use PipeWire (modern audio stack)
  # services.pipewire = {
  #   enable = true;
  #   alsa.enable = true;
  #   pulse.enable = true;
  # };
  
  # Add your user to audio group
  users.users.youruser = {
    extraGroups = [ "audio" ];
  };
  
  # Optional: Install the CLI/TUI tools system-wide
  environment.systemPackages = with pkgs; [
    # Nix for Humanity CLI and TUI
    (import "${builtins.fetchGit {
      url = "https://github.com/Luminous-Dynamics/nix-for-humanity";
      ref = "main";
    }}/flake.nix").packages.${system}.nix-for-humanity
    
    # Additional audio tools for testing
    pavucontrol  # GUI audio control
    alsa-utils   # Command line audio utilities
  ];
  
  # Optional: Set up convenient aliases
  programs.bash.shellAliases = {
    # Voice shortcuts
    "nix-voice" = "systemctl --user status nix-humanity-voice";
    "voice-start" = "systemctl --user start nix-humanity-voice";
    "voice-stop" = "systemctl --user stop nix-humanity-voice";
    "voice-logs" = "journalctl --user -u nix-humanity-voice -f";
    
    # Test commands
    "test-mic" = "arecord -d 3 /tmp/test.wav && aplay /tmp/test.wav";
    "test-voice" = "/etc/nix-humanity/enable-voice.sh";
  };
  
  # System configuration continues...
}