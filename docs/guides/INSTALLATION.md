# 📦 Installation Guide - Nix for Humanity

## Quick Start (Try it now!)

```bash
# Run directly with flakes (no installation needed)
nix run github:Luminous-Dynamics/nix-for-humanity

# Or clone and run locally
git clone https://github.com/Luminous-Dynamics/nix-for-humanity
cd nix-for-humanity
nix develop  # Enter development shell
npm install
npm run tauri:dev
```

## Installation Methods

### 1. 🚀 As a Flake (Recommended)

Add to your `flake.nix`:

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    nix-for-humanity.url = "github:Luminous-Dynamics/nix-for-humanity";
  };

  outputs = { self, nixpkgs, nix-for-humanity, ... }: {
    nixosConfigurations.myhost = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        ./configuration.nix
        nix-for-humanity.nixosModules.default
        {
          services.nix-for-humanity = {
            enable = true;
            # Optional: Enable voice input
            voice.enable = true;
          };
        }
      ];
    };
  };
}
```

### 2. 📌 As a NixOS Module

In your `/etc/nixos/configuration.nix`:

```nix
{ config, pkgs, ... }:

{
  imports = [
    "${builtins.fetchTarball {
      url = "https://github.com/Luminous-Dynamics/nix-for-humanity/archive/main.tar.gz";
    }}/nixos-module.nix"
  ];

  services.nix-for-humanity = {
    enable = true;
    
    # Port configuration (default: 3456)
    port = 3456;
    
    # Voice settings
    voice = {
      enable = true;
      model = "base";  # tiny, base, small, or medium
    };
    
    # Security settings
    security = {
      sandboxLevel = "normal";  # strict, normal, or permissive
      requireConfirmation = true;  # Confirm system changes
    };
    
    # Open firewall for network access
    openFirewall = false;  # Set true for remote access
  };
}
```

Then rebuild:
```bash
sudo nixos-rebuild switch
```

### 3. 🏠 User Installation (Home Manager)

For per-user installation without system-wide changes:

```nix
{ config, pkgs, ... }:

{
  home.packages = with pkgs; [
    (nix-for-humanity.packages.${system}.default)
  ];
  
  # Auto-start on login
  systemd.user.services.nix-for-humanity = {
    Unit = {
      Description = "Nix for Humanity - Personal Assistant";
      After = [ "graphical-session.target" ];
    };
    Service = {
      Type = "simple";
      ExecStart = "${pkgs.nix-for-humanity}/bin/nix-for-humanity --user-mode";
      Restart = "on-failure";
    };
    Install = {
      WantedBy = [ "default.target" ];
    };
  };
}
```

### 4. 💻 Standalone Binary

Download and run without NixOS:

```bash
# Download latest release
curl -L https://github.com/Luminous-Dynamics/nix-for-humanity/releases/latest/download/nix-for-humanity-linux-x64 -o nix-for-humanity
chmod +x nix-for-humanity

# Run it
./nix-for-humanity
```

## 🎤 Voice Setup (Optional)

Voice recognition requires additional setup:

### 1. Download Whisper Model
```bash
# The service will download automatically on first use
# Or manually download:
mkdir -p ~/.local/share/nix-for-humanity/models
wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin \
  -O ~/.local/share/nix-for-humanity/models/ggml-base.en.bin
```

### 2. Grant Microphone Access
```bash
# For PulseAudio
pactl list sources  # Check available microphones

# For PipeWire
pw-cli list-objects | grep Audio
```

### 3. Test Voice Input
```bash
nix-for-humanity --test-voice
# Say: "Hello, can you hear me?"
```

## ⚙️ Configuration

### System Service Configuration

Create `/etc/nix-for-humanity/config.toml`:

```toml
# Server settings
[server]
port = 3456
host = "127.0.0.1"

# Voice settings
[voice]
enabled = true
model = "base"
language = "en"
silence_threshold = 2.0

# Security
[security]
sandbox_level = "normal"
require_confirmation = true
allowed_commands = ["install", "remove", "update", "query"]

# Logging
[logging]
level = "info"
file = "/var/log/nix-for-humanity.log"
```

### User Configuration

Create `~/.config/nix-for-humanity/preferences.toml`:

```toml
# Personal preferences
[interface]
theme = "auto"  # light, dark, or auto
show_hints = true
voice_feedback = true

[shortcuts]
wake_word = "hey nix"
push_to_talk = "ctrl+space"

[privacy]
save_history = false
anonymous_metrics = false
```

## 🔍 Verification

### Check Installation
```bash
# Check if service is running
systemctl status nix-for-humanity

# Check version
nix-for-humanity --version

# Run diagnostics
nix-for-humanity --diagnose
```

### Test Commands
```bash
# Test text input
echo "what's installed?" | nix-for-humanity --stdin

# Test interactive mode
nix-for-humanity --interactive

# Test with dry-run
nix-for-humanity --dry-run "install firefox"
```

## 🚧 Troubleshooting

### Service Won't Start
```bash
# Check logs
journalctl -u nix-for-humanity -f

# Check permissions
ls -la /var/lib/nix-for-humanity

# Run in debug mode
NIX_FOR_HUMANITY_LOG=debug nix-for-humanity
```

### Voice Not Working
```bash
# Test microphone
arecord -l  # List devices
arecord -d 5 test.wav  # Record 5 seconds
aplay test.wav  # Play back

# Check permissions
groups  # Should include 'audio'

# Test Whisper
nix-for-humanity --test-whisper
```

### Connection Issues
```bash
# Check if port is open
ss -tlnp | grep 3456

# Test API
curl http://localhost:3456/api/health

# Check firewall
sudo iptables -L | grep 3456
```

## 📚 Next Steps

1. **Read the User Guide** - [USER_GUIDE.md](USER_GUIDE.md)
2. **Learn Commands** - [docs/COMMANDS.md](COMMANDS.md)
3. **Configure Settings** - [docs/CONFIGURATION.md](CONFIGURATION.md)
4. **Join Community** - [Discord](https://discord.gg/nix-for-humanity)

## 🆘 Getting Help

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/Luminous-Dynamics/nix-for-humanity/issues)
- **Community**: [Matrix Chat](https://matrix.to/#/#nix-for-humanity:matrix.org)
- **Email**: support@luminousdynamics.org

---

*Installation should be as natural as the interface itself. If you're struggling, we've failed - please let us know!*