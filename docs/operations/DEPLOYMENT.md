# 🚀 Deployment Guide - Nix for Humanity

> Production deployment guide for the natural language interface for NixOS

**Last Updated**: 2025-07-25
**Status**: Current
**Audience**: System Administrators, DevOps

## Overview

This guide covers deploying Nix for Humanity in production environments. The system is designed to be deployed locally on individual NixOS machines, maintaining our privacy-first philosophy.

## Table of Contents

- [Deployment Options](#deployment-options)
- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
- [Configuration](#configuration)
- [Security Hardening](#security-hardening)
- [Monitoring](#monitoring)
- [Backup and Recovery](#backup-and-recovery)
- [Troubleshooting Deployment](#troubleshooting-deployment)
- [Upgrade Procedures](#upgrade-procedures)

## Deployment Options

### 1. Single User Installation (Recommended)

Ideal for personal computers and workstations.

```nix
# flake.nix
{
  inputs.nix-for-humanity.url = "github:Luminous-Dynamics/nix-for-humanity";
  
  outputs = { self, nixpkgs, nix-for-humanity }: {
    nixosConfigurations.mycomputer = nixpkgs.lib.nixosSystem {
      modules = [
        nix-for-humanity.nixosModules.default
        {
          services.nix-for-humanity = {
            enable = true;
            user = "myusername";
          };
        }
      ];
    };
  };
}
```

### 2. Multi-User Installation

For shared family computers or small teams.

```nix
{
  services.nix-for-humanity = {
    enable = true;
    multiUser = true;
    users = [ "alice" "bob" "charlie" ];
    
    # Each user gets isolated learning data
    isolation = {
      enabled = true;
      sharePatterns = false;  # Don't share between users
    };
  };
}
```

### 3. Kiosk Mode

For public or limited-access systems.

```nix
{
  services.nix-for-humanity = {
    enable = true;
    mode = "kiosk";
    
    kiosk = {
      allowedCommands = [
        "search"
        "status"
        "help"
      ];
      
      # No persistence in kiosk mode
      ephemeral = true;
      
      # Reset after idle
      idleTimeout = 300;  # 5 minutes
    };
  };
}
```

## System Requirements

### Minimum Requirements

```yaml
Hardware:
  CPU: 2 cores @ 2.0GHz
  RAM: 4GB (2GB available)
  Storage: 2GB free space
  Network: Not required (local-first)

Software:
  OS: NixOS 23.11 or later
  Kernel: 5.15 or later
  Audio: PulseAudio or PipeWire (for voice)
```

### Recommended Requirements

```yaml
Hardware:
  CPU: 4 cores @ 2.5GHz
  RAM: 8GB
  Storage: 10GB free space
  Microphone: USB or built-in (for voice)

Software:
  OS: NixOS 24.05 or later
  Display: Wayland or X11
  Audio: PipeWire (better latency)
```

### Performance Scaling

| Users | CPU Cores | RAM | Storage |
|-------|-----------|-----|------|
| 1 | 2 | 2GB | 2GB |
| 5 | 4 | 4GB | 10GB |
| 10 | 8 | 8GB | 20GB |
| 20+ | Contact support | | |

## Installation Methods

### Method 1: NixOS Module (Recommended)

```bash
# Add to your flake inputs
nix flake update

# Rebuild with the module
sudo nixos-rebuild switch --flake .#mycomputer
```

### Method 2: Home Manager

For user-level installation without system access.

```nix
# home.nix
{
  imports = [ nix-for-humanity.homeManagerModules.default ];
  
  programs.nix-for-humanity = {
    enable = true;
    settings = {
      voice.enabled = true;
      learning.enabled = true;
    };
  };
}
```

### Method 3: Direct Binary

For testing or non-NixOS systems (limited functionality).

```bash
# Download latest release
wget https://github.com/Luminous-Dynamics/nix-for-humanity/releases/latest/nix-for-humanity-x86_64-linux

# Make executable
chmod +x nix-for-humanity-x86_64-linux

# Run
./nix-for-humanity-x86_64-linux
```

### Method 4: Container Deployment

For isolation or testing.

```bash
# Using Docker
docker run -it \
  --device /dev/snd \
  -v /run/user/1000/pulse:/run/user/1000/pulse \
  -v ~/.config/nix-for-humanity:/config \
  ghcr.io/luminous-dynamics/nix-for-humanity:latest

# Using Podman (rootless)
podman run -it \
  --userns=keep-id \
  --security-opt label=disable \
  -v ~/.config/nix-for-humanity:/config:Z \
  ghcr.io/luminous-dynamics/nix-for-humanity:latest
```

## Configuration

### Basic Configuration

```nix
# /etc/nixos/nix-for-humanity.nix
{
  services.nix-for-humanity = {
    enable = true;
    
    # Core settings
    interface = {
      defaultInput = "text";  # or "voice"
      language = "en-US";
      theme = "auto";  # auto, light, dark
    };
    
    # Learning configuration
    learning = {
      enabled = true;
      adaptationSpeed = "moderate";  # slow, moderate, fast
      privacyLevel = "balanced";     # minimal, balanced, full
    };
    
    # Voice settings
    voice = {
      enabled = true;
      engine = "whisper";  # whisper or webkit
      model = "base.en";   # tiny, base, small, medium
      
      # Microphone settings
      audio = {
        device = "default";
        noiseSupression = true;
        echoCancellation = true;
      };
    };
    
    # Security settings
    security = {
      sandboxing = true;
      auditLogging = true;
      requireAuth = ["system-modification"];
    };
  };
}
```

### Advanced Configuration

```nix
{
  services.nix-for-humanity = {
    # Performance tuning
    performance = {
      maxMemory = "2G";
      cpuQuota = "200%";  # 2 cores
      
      # Caching
      cache = {
        enabled = true;
        size = "1G";
        ttl = 3600;  # 1 hour
      };
      
      # Model optimization
      models = {
        preload = true;
        quantization = "int8";  # Smaller, faster
      };
    };
    
    # Integration settings
    integrations = {
      # Sacred Bridge connection
      sacredBridge = {
        enabled = false;  # Enable if part of Luminous-Dynamics
        url = "http://localhost:7777";
      };
      
      # External AI (optional)
      ai = {
        enabled = false;
        provider = "local";  # local, claude, openai
        apiKey = null;       # Set if using cloud
      };
    };
    
    # Custom vocabulary
    vocabulary = {
      customPackageNames = {
        "photoshop" = "gimp";
        "word" = "libreoffice-writer";
        "excel" = "libreoffice-calc";
      };
      
      aliases = [
        { from = "install the thing for photos"; to = "install gimp"; }
        { from = "python stuff"; to = "python3 python3Packages.pip"; }
      ];
    };
  };
}
```

### Environment Variables

```bash
# /etc/systemd/system/nix-for-humanity.service.d/override.conf
[Service]
Environment="NFH_LOG_LEVEL=info"
Environment="NFH_DATA_DIR=/var/lib/nix-for-humanity"
Environment="NFH_CACHE_DIR=/var/cache/nix-for-humanity"
Environment="NFH_DEBUG=false"
```

## Security Hardening

### 1. Systemd Hardening

```ini
# Automatic with NixOS module, or manual:
[Service]
# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=/var/lib/nix-for-humanity

# Sandboxing
SystemCallFilter=@system-service
SystemCallErrorNumber=EPERM
RestrictNamespaces=true
RestrictRealtime=true
LockPersonality=true

# Network (not needed)
PrivateNetwork=true
RestrictAddressFamilies=AF_UNIX
```

### 2. Polkit Rules

```javascript
// /etc/polkit-1/rules.d/50-nix-for-humanity.rules
polkit.addRule(function(action, subject) {
  if (action.id.indexOf("org.nixos.nix-for-humanity") === 0) {
    if (subject.isInGroup("nix-for-humanity")) {
      return polkit.Result.AUTH_SELF_KEEP;
    }
  }
});
```

### 3. AppArmor Profile

```bash
# /etc/apparmor.d/nix-for-humanity
#include <tunables/global>

/nix/store/*/bin/nix-for-humanity {
  #include <abstractions/base>
  #include <abstractions/audio>
  
  # Read access
  /etc/nixos/** r,
  /nix/store/** r,
  @{HOME}/.config/nix-for-humanity/** rw,
  
  # Write access
  /var/lib/nix-for-humanity/** rw,
  /var/cache/nix-for-humanity/** rw,
  
  # Deny network
  deny network,
}
```

### 4. SELinux Context (if using)

```bash
# Set contexts
semanage fcontext -a -t nix_for_humanity_exec_t '/nix/store/.*/bin/nix-for-humanity'
semanage fcontext -a -t nix_for_humanity_data_t '/var/lib/nix-for-humanity(/.*)?'
restorecon -Rv /var/lib/nix-for-humanity
```

## Monitoring

### Health Checks

```nix
# Enable built-in monitoring
services.nix-for-humanity.monitoring = {
  enable = true;
  
  healthcheck = {
    interval = 60;  # seconds
    timeout = 10;
    
    alerts = {
      email = "admin@example.com";
      webhook = "https://monitoring.example.com/webhook";
    };
  };
  
  metrics = {
    prometheus = {
      enable = true;
      port = 9100;
    };
  };
};
```

### Prometheus Metrics

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'nix-for-humanity'
    static_configs:
      - targets: ['localhost:9100']
    metric_relabel_configs:
      - source_labels: [__name__]
        regex: 'nfh_(.*)'
        target_label: __name__
        replacement: 'nix_for_humanity_${1}'
```

### Key Metrics to Monitor

```yaml
Performance:
  - nfh_response_time_ms
  - nfh_intent_recognition_accuracy
  - nfh_memory_usage_bytes
  - nfh_cpu_usage_percent

Usage:
  - nfh_commands_processed_total
  - nfh_active_users
  - nfh_learning_patterns_stored
  - nfh_voice_recognitions_total

Errors:
  - nfh_recognition_failures_total
  - nfh_execution_errors_total
  - nfh_timeouts_total
```

### Logging

```nix
# Structured logging configuration
services.nix-for-humanity.logging = {
  level = "info";
  format = "json";
  
  outputs = [
    {
      type = "file";
      path = "/var/log/nix-for-humanity/app.log";
      rotate = {
        size = "100M";
        keep = 7;
      };
    }
    {
      type = "syslog";
      facility = "local0";
    }
  ];
  
  # Privacy-preserving logging
  privacy = {
    maskUserInput = true;
    excludePatterns = [
      "password"
      "secret"
      "key"
    ];
  };
};
```

## Backup and Recovery

### What to Backup

```yaml
Critical:
  - /var/lib/nix-for-humanity/users/  # User learning data
  - /etc/nixos/nix-for-humanity.nix   # Configuration
  
Optional:
  - /var/cache/nix-for-humanity/       # Cache (regeneratable)
  - /var/log/nix-for-humanity/         # Logs (rotated)
```

### Backup Script

```bash
#!/usr/bin/env bash
# /usr/local/bin/backup-nfh

BACKUP_DIR="/backup/nix-for-humanity/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Stop service for consistency
systemctl stop nix-for-humanity

# Backup data
tar -czf "$BACKUP_DIR/userdata.tar.gz" /var/lib/nix-for-humanity/users/
cp /etc/nixos/nix-for-humanity.nix "$BACKUP_DIR/"

# Restart service
systemctl start nix-for-humanity

# Rotate old backups
find /backup/nix-for-humanity -mtime +30 -delete
```

### Recovery Procedure

```bash
# Restore from backup
BACKUP_DATE="20250125-120000"

# Stop service
systemctl stop nix-for-humanity

# Restore data
tar -xzf "/backup/nix-for-humanity/$BACKUP_DATE/userdata.tar.gz" -C /

# Restore config
cp "/backup/nix-for-humanity/$BACKUP_DATE/nix-for-humanity.nix" /etc/nixos/

# Rebuild
nixos-rebuild switch

# Verify
systemctl status nix-for-humanity
```

## Troubleshooting Deployment

### Common Issues

#### Service Won't Start

```bash
# Check status
systemctl status nix-for-humanity

# Check logs
journalctl -u nix-for-humanity -f

# Verify permissions
ls -la /var/lib/nix-for-humanity

# Test configuration
nix-for-humanity --test-config
```

#### Voice Not Working

```bash
# Check audio devices
arecord -l

# Test microphone
arecord -d 5 test.wav && aplay test.wav

# Verify permissions
groups | grep audio

# Check PulseAudio/PipeWire
systemctl --user status pulseaudio
```

#### High Memory Usage

```nix
# Reduce model size
services.nix-for-humanity.voice.model = "tiny.en";

# Limit cache
services.nix-for-humanity.performance.cache.size = "500M";

# Enable swap
swapDevices = [ { device = "/swapfile"; size = 4096; } ];
```

### Debug Mode

```bash
# Enable debug logging
export NFH_DEBUG=true
export NFH_LOG_LEVEL=debug

# Run in foreground
nix-for-humanity --foreground --debug

# Trace system calls
strace -f nix-for-humanity

# Profile performance
perf record -g nix-for-humanity
perf report
```

## Upgrade Procedures

### Standard Upgrade

```bash
# Update flake
nix flake update nix-for-humanity

# Test in VM first
nixos-rebuild build-vm
./result/bin/run-*-vm

# Apply upgrade
sudo nixos-rebuild switch

# Verify
nix-for-humanity --version
```

### Major Version Upgrade

```bash
# 1. Backup everything
/usr/local/bin/backup-nfh

# 2. Read changelog
curl -L https://github.com/Luminous-Dynamics/nix-for-humanity/blob/main/CHANGELOG.md

# 3. Test extensively
nixos-rebuild test

# 4. Schedule maintenance window
echo "System upgrade scheduled" | wall

# 5. Perform upgrade
nixos-rebuild switch

# 6. Verify all users
for user in $(users); do
  sudo -u $user nix-for-humanity --test
done
```

### Rollback Procedure

```bash
# List generations
nixos-rebuild list-generations

# Rollback to previous
nixos-rebuild switch --rollback

# Or specific generation
nixos-rebuild switch --generation 42

# Verify
nix-for-humanity --version
```

## Production Checklist

### Pre-Deployment

- [ ] Hardware meets requirements
- [ ] NixOS version compatible
- [ ] Backup system configured
- [ ] Monitoring configured
- [ ] Security policies reviewed
- [ ] User training completed

### Deployment

- [ ] Configuration validated
- [ ] Service starts successfully
- [ ] Health checks passing
- [ ] Voice input tested
- [ ] Learning system initialized
- [ ] Permissions verified

### Post-Deployment

- [ ] Monitor logs for 24 hours
- [ ] Verify backup runs
- [ ] Check user satisfaction
- [ ] Document any issues
- [ ] Schedule first update
- [ ] Plan capacity review

## Support

### Getting Help

- **Documentation**: https://docs.luminousdynamics.org
- **Issues**: https://github.com/Luminous-Dynamics/nix-for-humanity/issues
- **Discord**: https://discord.gg/luminous-dynamics
- **Email**: support@luminousdynamics.org

### Logs to Provide

When reporting issues, include:

```bash
# System info
nixos-version
nix-for-humanity --version

# Service logs
journalctl -u nix-for-humanity --since "1 hour ago" > nfh-logs.txt

# Configuration (sanitized)
nix eval --json '.#nixosConfigurations.mycomputer.config.services.nix-for-humanity' > nfh-config.json
```

---

**Remember**: Deploy with care, monitor with wisdom, and always prioritize user privacy and system stability.

*"A good deployment is invisible to users—they just notice that everything works better."*