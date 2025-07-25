# 🚀 NixOS GUI - Production Deployment Guide

This guide covers deploying NixOS GUI in production environments with security, performance, and reliability best practices.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Security Hardening](#security-hardening)
3. [Performance Optimization](#performance-optimization)
4. [High Availability](#high-availability)
5. [Monitoring & Logging](#monitoring--logging)
6. [Backup & Recovery](#backup--recovery)
7. [Deployment Checklist](#deployment-checklist)

## Prerequisites

### System Requirements

- **OS**: NixOS 23.11 or newer
- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 20GB free space
- **Network**: Static IP or domain name

### Software Requirements

- SSL certificates (Let's Encrypt recommended)
- Redis (optional, for distributed caching)
- Prometheus (optional, for monitoring)
- Backup solution (restic, borg, etc.)

## Security Hardening

### 1. Enable HTTPS

```nix
{ config, pkgs, ... }:

{
  services.nixos-gui = {
    enable = true;
    ssl = {
      enable = true;
      certFile = "/etc/ssl/certs/nixos-gui.crt";
      keyFile = "/etc/ssl/private/nixos-gui.key";
    };
  };

  # Or use Let's Encrypt
  security.acme = {
    acceptTerms = true;
    defaults.email = "admin@example.com";
    certs."gui.example.com" = {
      webroot = "/var/lib/acme/acme-challenge";
    };
  };

  services.nginx = {
    enable = true;
    virtualHosts."gui.example.com" = {
      enableACME = true;
      forceSSL = true;
      locations."/" = {
        proxyPass = "http://localhost:8080";
        proxyWebsockets = true;
      };
    };
  };
}
```

### 2. Configure Firewall

```nix
{
  # Only allow HTTPS from outside
  networking.firewall = {
    enable = true;
    allowedTCPPorts = [ 443 ];
    # Block direct access to GUI port
    extraCommands = ''
      iptables -A INPUT -p tcp --dport 8080 -s 127.0.0.1 -j ACCEPT
      iptables -A INPUT -p tcp --dport 8080 -j DROP
    '';
  };
}
```

### 3. Restrict Access

```nix
{
  services.nixos-gui = {
    # Limit to specific groups
    allowedGroups = [ "nixos-admins" ];
    
    # IP whitelist
    allowedIPs = [
      "10.0.0.0/8"
      "192.168.1.0/24"
    ];
    
    # Enable MFA
    mfa = {
      enable = true;
      provider = "totp";
    };
  };
}
```

### 4. Security Headers

```nix
{
  services.nixos-gui = {
    securityHeaders = {
      enable = true;
      csp = "default-src 'self'; script-src 'self' 'unsafe-inline'";
      hsts = {
        enable = true;
        maxAge = 31536000;
        includeSubDomains = true;
      };
    };
  };
}
```

## Performance Optimization

### 1. Enable Production Mode

```nix
{
  services.nixos-gui = {
    productionMode = true;
    
    # Performance settings
    workers = 4;  # Match CPU cores
    maxConnections = 1000;
    
    # Enable compression
    compression = {
      enable = true;
      level = 6;
    };
  };
}
```

### 2. Configure Redis Cache

```nix
{
  services.redis.servers.nixos-gui = {
    enable = true;
    port = 6380;
    maxmemory = "2gb";
    maxmemoryPolicy = "allkeys-lru";
  };

  services.nixos-gui = {
    cache = {
      type = "redis";
      redis = {
        host = "localhost";
        port = 6380;
        db = 0;
      };
    };
  };
}
```

### 3. CDN Integration

```nix
{
  services.nixos-gui = {
    cdn = {
      enable = true;
      url = "https://cdn.example.com";
      # Or use Cloudflare
      cloudflare = {
        enable = true;
        zoneId = "your-zone-id";
      };
    };
  };
}
```

### 4. Database Optimization

```nix
{
  services.nixos-gui = {
    database = {
      # Use PostgreSQL for better performance
      type = "postgresql";
      postgresql = {
        host = "localhost";
        database = "nixos_gui";
        user = "nixos_gui";
      };
      
      # Connection pooling
      pool = {
        min = 5;
        max = 20;
        idleTimeout = 300000;
      };
    };
  };
}
```

## High Availability

### 1. Load Balancing

```nix
{
  services.nginx = {
    upstreams.nixos-gui = {
      servers = {
        "app1.internal:8080" = {};
        "app2.internal:8080" = {};
        "app3.internal:8080" = {};
      };
      extraConfig = ''
        least_conn;
        keepalive 32;
      '';
    };
    
    virtualHosts."gui.example.com" = {
      locations."/" = {
        proxyPass = "http://nixos-gui";
      };
    };
  };
}
```

### 2. Session Sharing

```nix
{
  services.nixos-gui = {
    sessions = {
      store = "redis";
      redis = {
        host = "redis.internal";
        port = 6379;
        prefix = "nixos-gui:session:";
      };
    };
  };
}
```

### 3. Health Checks

```nix
{
  services.nixos-gui = {
    healthCheck = {
      enable = true;
      path = "/health";
      interval = 30;
    };
  };

  # Configure monitoring
  services.prometheus = {
    enable = true;
    scrapeConfigs = [{
      job_name = "nixos-gui";
      static_configs = [{
        targets = [ "localhost:8080" ];
      }];
      scrape_interval = "30s";
    }];
  };
}
```

## Monitoring & Logging

### 1. Structured Logging

```nix
{
  services.nixos-gui = {
    logging = {
      level = "info";
      format = "json";
      outputs = [
        "stdout"
        "/var/log/nixos-gui/app.log"
      ];
      
      # Log rotation
      rotation = {
        enable = true;
        maxSize = "100MB";
        maxFiles = 10;
        compress = true;
      };
    };
  };
}
```

### 2. Metrics Export

```nix
{
  services.nixos-gui = {
    metrics = {
      enable = true;
      prometheus = {
        enable = true;
        port = 9090;
      };
    };
  };

  # Grafana dashboard
  services.grafana = {
    enable = true;
    provision = {
      dashboards.settings.providers = [{
        name = "nixos-gui";
        options.path = ./dashboards;
      }];
    };
  };
}
```

### 3. Alerting

```nix
{
  services.prometheus = {
    alertmanager = {
      enable = true;
      configuration = {
        route = {
          receiver = "admin";
          group_wait = "30s";
          group_interval = "5m";
          repeat_interval = "12h";
        };
        receivers = [{
          name = "admin";
          email_configs = [{
            to = "admin@example.com";
            from = "alerts@example.com";
          }];
        }];
      };
    };
    
    rules = [''
      groups:
      - name: nixos-gui
        rules:
        - alert: NixOSGUIDown
          expr: up{job="nixos-gui"} == 0
          for: 5m
          labels:
            severity: critical
          annotations:
            summary: "NixOS GUI is down"
            
        - alert: HighErrorRate
          expr: rate(nixos_gui_errors_total[5m]) > 0.05
          for: 10m
          labels:
            severity: warning
          annotations:
            summary: "High error rate detected"
    ''];
  };
}
```

## Backup & Recovery

### 1. Automated Backups

```nix
{
  services.nixos-gui = {
    backup = {
      enable = true;
      schedule = "daily";
      retention = {
        daily = 7;
        weekly = 4;
        monthly = 6;
      };
    };
  };

  # Or use restic
  services.restic.backups.nixos-gui = {
    paths = [
      "/var/lib/nixos-gui"
      "/etc/nixos"
    ];
    repository = "s3:s3.amazonaws.com/backup-bucket/nixos-gui";
    timerConfig = {
      OnCalendar = "daily";
    };
    pruneOpts = [
      "--keep-daily 7"
      "--keep-weekly 4"
      "--keep-monthly 6"
    ];
  };
}
```

### 2. Disaster Recovery

```bash
#!/usr/bin/env bash
# restore-nixos-gui.sh

# Stop service
systemctl stop nixos-gui

# Restore data
restic -r s3:s3.amazonaws.com/backup-bucket/nixos-gui restore latest \
  --target / --include /var/lib/nixos-gui

# Restore configuration
restic -r s3:s3.amazonaws.com/backup-bucket/nixos-gui restore latest \
  --target / --include /etc/nixos

# Rebuild system
nixos-rebuild switch

# Start service
systemctl start nixos-gui
```

## Deployment Checklist

### Pre-Deployment

- [ ] SSL certificates obtained and configured
- [ ] Firewall rules configured
- [ ] Backup solution tested
- [ ] Monitoring configured
- [ ] Load testing completed
- [ ] Security scan performed

### Deployment

- [ ] Deploy to staging first
- [ ] Run smoke tests
- [ ] Check all integrations
- [ ] Verify SSL configuration
- [ ] Test backup/restore
- [ ] Monitor for 24 hours

### Post-Deployment

- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Review security logs
- [ ] Test incident response
- [ ] Document any issues
- [ ] Update runbooks

## Production Configuration Example

```nix
# /etc/nixos/nixos-gui-prod.nix
{ config, pkgs, ... }:

{
  imports = [ ./nixos-gui-base.nix ];

  services.nixos-gui = {
    enable = true;
    productionMode = true;
    
    # Performance
    workers = 8;
    maxConnections = 2000;
    
    # Security
    ssl.enable = true;
    mfa.enable = true;
    allowedGroups = [ "nixos-admins" ];
    
    # High Availability
    cache.type = "redis";
    sessions.store = "redis";
    database.type = "postgresql";
    
    # Monitoring
    metrics.prometheus.enable = true;
    logging.format = "json";
    
    # Backup
    backup.enable = true;
  };

  # Supporting services
  services.redis.servers.nixos-gui.enable = true;
  services.postgresql.enable = true;
  services.prometheus.enable = true;
  services.grafana.enable = true;
  
  # Security
  networking.firewall.enable = true;
  security.acme.acceptTerms = true;
}
```

## Troubleshooting Production Issues

### High CPU Usage
1. Check worker count matches CPU cores
2. Review cache hit rates
3. Enable query optimization
4. Check for infinite loops in logs

### Memory Leaks
1. Monitor Node.js heap usage
2. Check Redis memory usage
3. Review connection pooling
4. Enable memory profiling

### Slow Response Times
1. Check database query performance
2. Review cache configuration
3. Enable compression
4. Check network latency

### Connection Errors
1. Verify firewall rules
2. Check SSL configuration
3. Review proxy settings
4. Monitor connection limits

## Security Incident Response

1. **Detect**: Monitor logs and alerts
2. **Contain**: Isolate affected systems
3. **Investigate**: Review audit logs
4. **Remediate**: Apply fixes
5. **Recover**: Restore from backups
6. **Review**: Update security measures

## Performance Benchmarks

Expected performance in production:

- **Page Load**: < 1 second
- **API Response**: < 100ms (cached)
- **Package Search**: < 200ms
- **Configuration Apply**: < 5 seconds
- **Concurrent Users**: 500+
- **Uptime**: 99.9%

## Support

For production support:
- **Documentation**: https://docs.nixos-gui.org
- **Enterprise Support**: support@nixos-gui.org
- **Security Issues**: security@nixos-gui.org
- **Community**: https://discourse.nixos.org

---

Remember: Always test in staging before deploying to production!