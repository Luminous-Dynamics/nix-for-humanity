{ config, pkgs, lib, ... }:

{
  # 🎮 Luminous Nix for Steam Deck - Natural Language Gaming Revolution
  # Turn your Steam Deck into an AI-powered gaming companion
  
  imports = [
    # Hardware support
    "${fetchTarball "https://github.com/Jovian-Experiments/Jovian-NixOS/archive/development.tar.gz"}/modules"
  ];
  
  # Steam Deck hardware configuration
  jovian = {
    devices.steamdeck = {
      enable = true;
      autoUpdate = false;  # We manage updates via Nix
      enableGyroDSU = true;  # Gyroscope support
    };
    
    steam = {
      enable = true;
      autoStart = true;
      user = "deck";  # Default Steam Deck user
      desktopSession = "gamescope-wayland";
    };
    
    decky-loader.enable = true;  # Plugin support
  };

  # Luminous Nix integration
  environment.systemPackages = with pkgs; [
    # Voice control dependencies
    sox
    piper-tts
    whisper-cpp
    
    # Natural language interface
    (writeScriptBin "hey-deck" ''
      #!${pkgs.bash}/bin/bash
      # Voice assistant for Steam Deck
      
      COMMAND="$*"
      
      if [ -z "$COMMAND" ]; then
        # Voice input mode
        echo "🎤 Listening... (Press Ctrl+C to cancel)"
        COMMAND=$(${pkgs.whisper-cpp}/bin/whisper-cpp --model base.en --threads 4 --capture 5)
      fi
      
      # Process with Luminous Nix
      ${luminous-nix}/bin/ask-nix "$COMMAND"
    '')
    
    # Game management tools
    (writeScriptBin "deck-game-manager" ''
      #!${pkgs.bash}/bin/bash
      
      case "$1" in
        install)
          echo "🎮 Installing game: $2"
          ask-nix "install game $2 with recommended settings"
          ;;
        optimize)
          echo "⚡ Optimizing for: $2"
          ask-nix "optimize $2 for steam deck"
          ;;
        mods)
          echo "🔧 Managing mods for: $2"
          ask-nix "install popular mods for $2"
          ;;
        battery)
          echo "🔋 Optimizing battery for: $2"
          ask-nix "configure $2 for maximum battery life"
          ;;
        *)
          echo "Usage: deck-game-manager [install|optimize|mods|battery] [game]"
          ;;
      esac
    '')
    
    # Performance profiles
    (writeScriptBin "deck-profile" ''
      #!${pkgs.bash}/bin/bash
      
      case "$1" in
        battery)
          echo "🔋 Switching to battery saver mode"
          ${pkgs.gamescope}/bin/gamescope-msg system set-tdp 7
          ${pkgs.gamescope}/bin/gamescope-msg system set-gpu-freq 400
          ;;
        balanced)
          echo "⚖️ Switching to balanced mode"
          ${pkgs.gamescope}/bin/gamescope-msg system set-tdp 10
          ${pkgs.gamescope}/bin/gamescope-msg system set-gpu-freq 800
          ;;
        performance)
          echo "🚀 Switching to performance mode"
          ${pkgs.gamescope}/bin/gamescope-msg system set-tdp 15
          ${pkgs.gamescope}/bin/gamescope-msg system set-gpu-freq 1600
          ;;
        auto)
          echo "🤖 AI-driven profile selection"
          ask-nix "optimize performance for current game"
          ;;
        *)
          echo "Usage: deck-profile [battery|balanced|performance|auto]"
          ;;
      esac
    '')
    
    # Essential Steam Deck tools
    mangohud  # Performance overlay
    gamescope  # Valve's compositor
    gamemode  # Performance governor
    
    # Additional launchers
    heroic  # Epic/GOG games
    lutris  # Everything else
    
    # Emulation station
    emulationstation-de
    retroarch
    
    # System tools
    htop
    nvtop  # GPU monitoring
    steamcmd  # Command-line Steam
    
    # Media tools
    mpv  # Video player
    spotify  # Music streaming
  ];

  # Kernel optimizations for Steam Deck
  boot.kernelPackages = pkgs.linuxPackages_zen;  # Optimized for gaming
  boot.kernelParams = [
    "amd_pstate=active"  # Better CPU governor
    "amdgpu.ppfeaturemask=0xffffffff"  # Full GPU control
    "video=eDP-1:800x1280"  # Native resolution
  ];

  # Power management for handheld
  services.tlp = {
    enable = true;
    settings = {
      CPU_SCALING_GOVERNOR_ON_AC = "performance";
      CPU_SCALING_GOVERNOR_ON_BAT = "powersave";
      
      # Steam Deck specific
      PLATFORM_PROFILE_ON_AC = "performance";
      PLATFORM_PROFILE_ON_BAT = "balanced";
      
      # Don't touch GPU (Gamescope handles it)
      RADEON_DPM_STATE_ON_AC = "performance";
      RADEON_DPM_STATE_ON_BAT = "battery";
    };
  };

  # Audio configuration
  services.pipewire = {
    enable = true;
    alsa.enable = true;
    pulse.enable = true;
    
    # Steam Deck audio fixes
    config.pipewire = {
      "context.properties" = {
        "default.clock.rate" = 48000;
        "default.clock.quantum" = 1024;
        "default.clock.min-quantum" = 512;
        "default.clock.max-quantum" = 2048;
      };
    };
  };

  # Network optimization for gaming
  networking = {
    networkmanager.enable = true;
    
    # Reduce latency
    firewall = {
      enable = true;
      allowedTCPPorts = [ 27036 27037 ];  # Steam
      allowedUDPPorts = [ 27031 27036 ];  # Steam
    };
  };

  # Filesystem optimizations
  fileSystems."/" = {
    options = [ "noatime" "nodiratime" "discard" ];
  };

  # ZRAM for better memory management
  zramSwap = {
    enable = true;
    memoryPercent = 50;
    algorithm = "zstd";
  };

  # Enable Steam Deck specific services
  services = {
    # Gyro/accelerometer support
    iio-sensor-proxy.enable = true;
    
    # Better thermal management
    thermald.enable = true;
    
    # Bluetooth (for controllers)
    blueman.enable = true;
  };

  # User configuration for deck user
  users.users.deck = {
    isNormalUser = true;
    description = "Steam Deck User";
    extraGroups = [ "wheel" "video" "audio" "input" "gamemode" ];
    
    # Auto-login
    initialPassword = "deck";
  };

  # Auto-login to gamescope session
  services.xserver = {
    enable = true;
    displayManager = {
      lightdm.enable = false;
      sddm = {
        enable = true;
        autoLogin = {
          enable = true;
          user = "deck";
        };
      };
    };
  };

  # Luminous Nix voice commands configuration
  programs.luminous-nix = {
    enable = true;
    
    voiceCommands = {
      enable = true;
      wakeWord = "hey deck";
      
      commands = {
        # Gaming commands
        "install * game" = "steam-installer search '$1' && steam-installer install";
        "play *" = "steam steam://run/$(steam-game-id '$1')";
        "optimize * for battery" = "deck-profile battery && game-optimizer '$1' --battery";
        "show fps" = "mangohud --toggle";
        "take screenshot" = "grim screenshot-$(date +%Y%m%d-%H%M%S).png";
        
        # System commands
        "battery status" = "cat /sys/class/power_supply/BAT0/capacity";
        "go to desktop" = "gamescope-msg system switch-to-desktop";
        "go to game mode" = "gamescope-msg system switch-to-gamemode";
        "update system" = "ask-nix 'update nixos safely'";
        
        # Performance commands
        "boost performance" = "deck-profile performance";
        "save battery" = "deck-profile battery";
        "auto optimize" = "deck-profile auto";
      };
    };
    
    # AI-powered game recommendations
    gameAdvisor = {
      enable = true;
      localLLM = "mistral-7b";  # Runs on Deck!
      
      features = [
        "compatibility-check"  # Will this game run?
        "settings-optimizer"   # Best settings for 60fps
        "mod-recommendations"  # Suggested mods
        "similar-games"       # Games you might like
      ];
    };
  };

  # Quick switcher for desktop/gaming mode
  environment.shellAliases = {
    "desktop" = "systemctl --user start plasma-workspace";
    "gamemode" = "systemctl --user start gamescope-session";
    "hey" = "hey-deck";
    
    # Quick game launchers
    "steam" = "gamescope -W 1280 -H 800 -e -- steam";
    "heroic" = "gamescope -W 1280 -H 800 -e -- heroic";
  };

  # System state version
  system.stateVersion = "24.05";
}