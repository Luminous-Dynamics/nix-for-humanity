# 🌟 NixOS GUI Installation Guide

## Prerequisites

- NixOS system (or Linux with Nix installed)
- X11 or Wayland display server
- Administrative privileges for system configuration

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Luminous-Dynamics/nixos-gui.git
cd nixos-gui
```

### 2. Enter Development Environment

```bash
# Using nix-shell (traditional)
cd src-tauri
nix-shell

# Or using flakes (recommended)
nix develop
```

### 3. Install Frontend Dependencies

```bash
npm install
```

### 4. Run in Development Mode

```bash
# From the project root
npm run tauri:dev

# Or from src-tauri directory
cargo tauri dev
```

## Building for Production

### 1. Build the Application

```bash
# In nix-shell
npm run tauri:build
```

### 2. Find the Built Application

The built application will be in:
- Linux: `src-tauri/target/release/bundle/`
- AppImage: `src-tauri/target/release/bundle/appimage/`
- Deb: `src-tauri/target/release/bundle/deb/`

## NixOS Module Installation

### 1. Add to Your Configuration

```nix
# /etc/nixos/configuration.nix
{ config, pkgs, ... }:

{
  imports = [
    ./hardware-configuration.nix
    (fetchTarball "https://github.com/Luminous-Dynamics/nixos-gui/archive/main.tar.gz")
  ];

  services.nixos-gui = {
    enable = true;
    port = 7878;  # Optional, default is 7878
  };
}
```

### 2. Rebuild Your System

```bash
sudo nixos-rebuild switch
```

### 3. Access the GUI

- Desktop App: Launch from your application menu
- System Tray: Look for the NixOS icon
- Web Interface: http://localhost:7878 (if web mode enabled)

## Troubleshooting

### Missing Dependencies

If you get errors about missing libraries:

```bash
# Ensure you're in nix-shell
nix-shell

# Check dependencies
./test-deps.sh
```

### WebKit Errors

For WebKit-related errors:

```bash
# Install system dependencies (non-NixOS)
sudo apt-get install webkit2gtk-4.0 # Debian/Ubuntu
sudo dnf install webkit2gtk3-devel  # Fedora
```

### Permission Errors

The application needs permission to:
- Read `/etc/nixos/` configuration
- Execute `nixos-rebuild` (requires sudo)
- Manage systemd services

Run with appropriate privileges:

```bash
# Development
sudo -E cargo tauri dev

# Production
pkexec nixos-gui
```

## Configuration

### Sacred Features

Enable consciousness-first features in `~/.config/nixos-gui/settings.json`:

```json
{
  "sacred": {
    "enablePauses": true,
    "pauseInterval": 25,
    "coherenceTracking": true,
    "intentionReminders": true
  }
}
```

### Security

For production use, configure permissions:

```nix
# In your NixOS configuration
security.polkit.extraConfig = ''
  polkit.addRule(function(action, subject) {
    if (action.id == "org.nixos.gui.manage-system" &&
        subject.isInGroup("wheel")) {
      return polkit.Result.YES;
    }
  });
'';
```

## Development

### Running Tests

```bash
# Backend tests
cargo test

# Frontend tests
npm test

# Integration tests
npm run test:integration
```

### Contributing

1. Fork the repository
2. Create a sacred branch: `git checkout -b sacred-feature`
3. Make your changes mindfully
4. Test thoroughly
5. Submit a PR with clear intentions

## Sacred Development Practices

Remember:
- 🧘 Take sacred pauses every 25 minutes
- 🎯 Set clear intentions before coding sessions
- 🌊 Code flows better when you're coherent
- 💫 Every function is a prayer, every commit a ceremony

## Support

- Issues: https://github.com/Luminous-Dynamics/nixos-gui/issues
- Discord: [Sacred Development Circle]
- Email: support@luminousdynamics.org

---

*"We are not building software. We are midwifing a new form of consciousness into being."*