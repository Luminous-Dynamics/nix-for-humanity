# NixOS GUI Installation Guide

## Table of Contents

1. [Requirements](#requirements)
2. [Installation Methods](#installation-methods)
   - [Flakes Installation](#flakes-installation-recommended)
   - [Traditional Installation](#traditional-installation)
   - [Development Installation](#development-installation)
3. [Configuration Options](#configuration-options)
4. [Post-Installation Setup](#post-installation-setup)
5. [Upgrading](#upgrading)
6. [Uninstallation](#uninstallation)
7. [Troubleshooting](#troubleshooting)

## Requirements

### System Requirements

- **Operating System**: NixOS 23.11 or later
- **Architecture**: x86_64-linux or aarch64-linux
- **Memory**: Minimum 1GB RAM (2GB recommended)
- **Disk Space**: 500MB for installation
- **Network**: Internet connection for package management

### User Requirements

- User account with sudo privileges
- Member of `wheel` group (or configured group)
- Basic familiarity with NixOS configuration

### Browser Requirements

- Modern web browser with JavaScript enabled:
  - Firefox 91+
  - Chrome/Chromium 92+
  - Safari 14+
  - Edge 92+

## Installation Methods

### Flakes Installation (Recommended)

Flakes provide reproducible, declarative installation with version pinning.

#### Step 1: Enable Flakes

Add to `/etc/nixos/configuration.nix`:

```nix
{
  nix.settings.experimental-features = [ "nix-command" "flakes" ];
}
```

Rebuild: `sudo nixos-rebuild switch`

#### Step 2: Create System Flake

Create `/etc/nixos/flake.nix`:

```nix
{
  description = "My NixOS System";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    nixos-gui.url = "github:nixos/nixos-gui";
  };

  outputs = { self, nixpkgs, nixos-gui }: {
    nixosConfigurations.yourhostname = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        ./configuration.nix
        nixos-gui.nixosModules.default
        {
          services.nixos-gui = {
            enable = true;
            # Additional options here
          };
        }
      ];
    };
  };
}
```

#### Step 3: Apply Configuration

```bash
sudo nixos-rebuild switch --flake /etc/nixos#yourhostname
```

### Traditional Installation

For systems without flakes or stable channel users.

#### Step 1: Fetch Module

Add to `/etc/nixos/configuration.nix`:

```nix
{ config, pkgs, ... }:
let
  nixos-gui = builtins.fetchTarball {
    url = "https://github.com/nixos/nixos-gui/archive/v2.0.0.tar.gz";
    # Pin to specific commit for reproducibility
    # sha256 = "sha256:0000000000000000000000000000000000000000000000000000";
  };
in
{
  imports = [
    ./hardware-configuration.nix
    "${nixos-gui}/nixos-module"
  ];

  services.nixos-gui = {
    enable = true;
  };
}
```

#### Step 2: Rebuild System

```bash
sudo nixos-rebuild switch
```

### Development Installation

For contributors or testing latest features.

#### Step 1: Clone Repository

```bash
git clone https://github.com/nixos/nixos-gui.git
cd nixos-gui
```

#### Step 2: Link Module

Add to `/etc/nixos/configuration.nix`:

```nix
{
  imports = [
    ./hardware-configuration.nix
    /path/to/nixos-gui/nixos-module
  ];

  services.nixos-gui = {
    enable = true;
    package = /path/to/nixos-gui;
  };
}
```

#### Step 3: Development Mode

```bash
# Enter development shell
nix develop

# Install dependencies
npm install

# Build package
npm run build

# Apply to system
sudo nixos-rebuild switch
```

## Configuration Options

### Basic Configuration

```nix
services.nixos-gui = {
  enable = true;
  
  # Network binding
  host = "127.0.0.1";  # Default: localhost only
  port = 8080;         # Default web port
  wsPort = 8081;       # Default WebSocket port
  
  # User/group for service
  user = "nixos-gui";
  group = "nixos-gui";
  
  # Logging
  logLevel = "info";   # error, warn, info, debug
};
```

### Security Configuration

```nix
services.nixos-gui = {
  enable = true;
  
  # Access control
  allowedGroups = [ "wheel" "nixos-gui" "admin" ];
  
  # SSL/TLS
  ssl = {
    enable = true;
    cert = "/path/to/cert.pem";
    key = "/path/to/key.pem";
  };
  
  # Feature restrictions
  features = {
    packageManagement = true;
    serviceManagement = true;
    configurationEdit = true;
    systemRebuild = true;
    generationManagement = true;
    auditLogging = true;
  };
};
```

### Network Access

#### Local Access Only (Default)

```nix
services.nixos-gui = {
  enable = true;
  host = "127.0.0.1";
};
```

#### LAN Access

```nix
services.nixos-gui = {
  enable = true;
  host = "0.0.0.0";  # Bind to all interfaces
  openFirewall = true;
};

# Or manually:
networking.firewall.allowedTCPPorts = [ 8080 8081 ];
```

#### Internet Access (Use HTTPS!)

```nix
services.nixos-gui = {
  enable = true;
  host = "0.0.0.0";
  
  ssl = {
    enable = true;
    cert = "/etc/ssl/certs/nixos-gui.crt";
    key = "/etc/ssl/private/nixos-gui.key";
  };
  
  # Use reverse proxy instead
  nginx = {
    enable = true;
    virtualHost = "nixos-gui.example.com";
  };
};

# Nginx configuration
services.nginx = {
  enable = true;
  recommendedTlsSettings = true;
  recommendedOptimisation = true;
  recommendedGzipSettings = true;
  recommendedProxySettings = true;
  
  virtualHosts."nixos-gui.example.com" = {
    enableACME = true;  # Let's Encrypt
    forceSSL = true;
  };
};

# ACME for Let's Encrypt
security.acme = {
  acceptTerms = true;
  defaults.email = "admin@example.com";
};
```

### Advanced Options

```nix
services.nixos-gui = {
  enable = true;
  
  # Custom package build
  package = pkgs.nixos-gui.override {
    # Custom Node.js version
    nodejs = pkgs.nodejs_20;
  };
  
  # Resource limits
  systemd.services.nixos-gui = {
    serviceConfig = {
      MemoryLimit = "1G";
      CPUQuota = "50%";
    };
  };
};
```

## Post-Installation Setup

### 1. Verify Installation

```bash
# Check service status
systemctl status nixos-gui
systemctl status nixos-gui-helper

# Check ports
ss -tlnp | grep -E "8080|8081"

# View logs
journalctl -u nixos-gui -f
```

### 2. Create Admin User

```nix
# In configuration.nix
users.users.nixadmin = {
  isNormalUser = true;
  description = "NixOS GUI Administrator";
  extraGroups = [ "wheel" "nixos-gui" ];
  hashedPassword = "$6$...";  # Use mkpasswd
};
```

Or add existing user to group:

```bash
sudo usermod -a -G nixos-gui yourusername
```

### 3. First Access

1. Open browser to http://localhost:8080
2. Login with system credentials
3. Complete onboarding wizard
4. Configure preferences

### 4. Security Hardening

#### Enable HTTPS

For production use, always enable HTTPS:

```nix
services.nixos-gui.ssl = {
  enable = true;
  cert = "/etc/nixos/ssl/cert.pem";
  key = "/etc/nixos/ssl/key.pem";
};
```

#### Restrict Access

Limit to specific groups:

```nix
services.nixos-gui.allowedGroups = [ "admins" ];
```

#### Enable Audit Logging

```nix
services.nixos-gui.features.auditLogging = true;
```

## Upgrading

### Flakes Update

```bash
# Update flake input
nix flake update nixos-gui

# Or update all inputs
nix flake update

# Rebuild system
sudo nixos-rebuild switch --flake .#yourhostname
```

### Traditional Update

Update the URL in configuration.nix to latest release:

```nix
nixos-gui = builtins.fetchTarball {
  url = "https://github.com/nixos/nixos-gui/archive/v2.1.0.tar.gz";
};
```

### Version Compatibility

- v2.x → v2.y: Compatible, no config changes needed
- v1.x → v2.x: See migration guide

## Uninstallation

### Step 1: Disable Service

```nix
services.nixos-gui.enable = false;
```

Or remove the entire configuration block.

### Step 2: Rebuild

```bash
sudo nixos-rebuild switch
```

### Step 3: Cleanup (Optional)

```bash
# Remove state files
sudo rm -rf /var/lib/nixos-gui

# Remove user (if created)
sudo userdel nixos-gui

# Remove group
sudo groupdel nixos-gui
```

## Troubleshooting

### Service Won't Start

#### Check Logs

```bash
journalctl -u nixos-gui -e --no-pager
```

#### Common Issues

1. **Port Already in Use**
   ```bash
   # Find what's using port
   sudo lsof -i :8080
   
   # Solution: Change port in config
   services.nixos-gui.port = 8090;
   ```

2. **Permission Denied**
   ```
   Error: EACCES: permission denied
   ```
   Solution: Check file permissions in `/var/lib/nixos-gui`

3. **Module Not Found**
   ```
   error: module nixos-gui not found
   ```
   Solution: Verify import path is correct

### Can't Access GUI

1. **Check Service Running**
   ```bash
   systemctl is-active nixos-gui
   ```

2. **Check Firewall**
   ```bash
   sudo iptables -L -n | grep 8080
   ```

3. **Test Connectivity**
   ```bash
   curl http://localhost:8080/health
   ```

### Login Issues

1. **Verify User Groups**
   ```bash
   groups yourusername
   ```

2. **Check PAM Configuration**
   ```bash
   sudo pamtester login yourusername authenticate
   ```

3. **Reset User Password**
   ```bash
   sudo passwd yourusername
   ```

### Build Failures

1. **Clear Nix Store**
   ```bash
   nix-collect-garbage -d
   ```

2. **Check Disk Space**
   ```bash
   df -h /nix/store
   ```

3. **Verbose Build**
   ```bash
   sudo nixos-rebuild switch --show-trace
   ```

### Getting Help

If you encounter issues:

1. Check [FAQ](FAQ.md)
2. Search [existing issues](https://github.com/nixos/nixos-gui/issues)
3. Ask on [community forum](https://discourse.nixos.org)
4. Join [chat support](https://matrix.to/#/#nixos-gui:matrix.org)

When reporting issues, include:
- NixOS version: `nixos-version`
- Error messages from logs
- Relevant configuration
- Steps to reproduce