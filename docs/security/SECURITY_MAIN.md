# Security Guide

## Table of Contents
- [Security Model](#security-model)
- [Authentication](#authentication)
- [Authorization](#authorization)
- [Audit Logging](#audit-logging)
- [Network Security](#network-security)
- [Data Protection](#data-protection)
- [Best Practices](#best-practices)
- [Security Checklist](#security-checklist)

## Security Model

NixOS GUI follows the principle of least privilege and defense in depth.

### Core Principles

1. **Separation of Concerns**
   - Web interface runs as unprivileged user
   - System operations through privileged helper
   - Clear boundary between user and system space

2. **Explicit Authorization**
   - All system changes require explicit authorization
   - Uses native Linux security mechanisms (PAM, Polkit)
   - No bypass of system security

3. **Audit Trail**
   - All actions are logged
   - Tamper-resistant audit logs
   - Configurable retention policies

## Authentication

### PAM Integration

NixOS GUI uses the system's PAM (Pluggable Authentication Modules) for user authentication:

```javascript
// Authentication flow
1. User provides credentials
2. Credentials passed to PAM
3. PAM validates against system users
4. Session token generated on success
```

### Session Management

- **JWT Tokens**: Stateless authentication tokens
- **Secure Storage**: Tokens stored in httpOnly cookies
- **Expiration**: Configurable timeout (default: 1 hour)
- **Refresh**: Automatic token refresh before expiration

### Multi-Factor Authentication

Enable MFA for additional security:

```nix
services.nixos-gui = {
  security = {
    mfa = {
      enable = true;
      providers = [ "totp" "webauthn" ];
    };
  };
};
```

## Authorization

### Group-Based Access

Access is controlled through Linux groups:

```nix
services.nixos-gui = {
  # Only users in these groups can access
  allowedGroups = [ "wheel" "nixos-gui" ];
};
```

### Polkit Integration

System operations use Polkit for fine-grained authorization:

```xml
<!-- /etc/polkit-1/rules.d/nixos-gui.rules -->
polkit.addRule(function(action, subject) {
    if (action.id.indexOf("org.nixos.gui.") === 0) {
        if (subject.isInGroup("wheel")) {
            return polkit.Result.YES;
        }
        return polkit.Result.AUTH_ADMIN;
    }
});
```

### Role-Based Permissions

| Role | Permissions |
|------|------------|
| Viewer | View system state, logs |
| Operator | Manage services, view configs |
| Administrator | Full system management |

## Audit Logging

### What's Logged

All security-relevant events are logged:

- Authentication attempts (success/failure)
- Authorization decisions
- Configuration changes
- Service management actions
- System operations
- API access

### Log Format

```json
{
  "timestamp": "2024-01-20T15:30:45.123Z",
  "level": "info",
  "category": "security",
  "event": "auth.login.success",
  "user": "alice",
  "ip": "192.168.1.100",
  "userAgent": "Mozilla/5.0...",
  "sessionId": "anonymized-session-id",
  "metadata": {
    "mfa": true,
    "loginMethod": "password"
  }
}
```

### Log Security

- **Rotation**: Daily rotation with compression
- **Retention**: Configurable (default: 90 days)
- **Protection**: Logs are write-only for app user
- **Anonymization**: Sensitive data is hashed

### Viewing Audit Logs

```bash
# View recent security events
nixos-gui audit --tail 100

# Search for specific user
nixos-gui audit --user alice

# Export for analysis
nixos-gui audit --export --format json > audit.json
```

## Network Security

### HTTPS Configuration

Always use HTTPS in production:

```nix
services.nixos-gui = {
  ssl = {
    enable = true;
    certificate = "/etc/ssl/certs/nixos-gui.crt";
    key = "/etc/ssl/private/nixos-gui.key";
    
    # Force HTTPS
    forceSSL = true;
    
    # HSTS
    hstsMaxAge = 31536000;
  };
};
```

### Firewall Rules

```nix
networking.firewall = {
  # Only allow from local network
  extraCommands = ''
    iptables -A INPUT -p tcp --dport 8080 -s 192.168.1.0/24 -j ACCEPT
    iptables -A INPUT -p tcp --dport 8080 -j DROP
  '';
};
```

### Rate Limiting

Protect against brute force attacks:

```nix
services.nixos-gui = {
  rateLimiting = {
    enable = true;
    
    # Max requests per minute
    windowMs = 60000;
    max = 100;
    
    # Auth endpoint stricter limits
    auth = {
      windowMs = 300000; # 5 minutes
      max = 5;
    };
  };
};
```

## Data Protection

### Secrets Management

Never store secrets in:
- Git repositories
- Configuration files
- Environment variables in systemd

Instead use:
- NixOS secrets management
- HashiCorp Vault integration
- Systemd credentials

```nix
systemd.services.nixos-gui = {
  serviceConfig = {
    LoadCredential = [
      "jwt-secret:/run/secrets/nixos-gui/jwt"
      "db-password:/run/secrets/nixos-gui/db"
    ];
  };
};
```

### Database Security

- **Encryption**: Database encrypted at rest
- **Access**: Unix socket only, no network access
- **Backups**: Encrypted backup support

### API Security

- **CORS**: Strict origin validation
- **CSP**: Content Security Policy headers
- **XSS**: Input sanitization and output encoding
- **CSRF**: Token validation for state changes

## Best Practices

### Deployment Security

1. **Minimize Attack Surface**
   ```nix
   services.nixos-gui = {
     # Disable unused features
     features = {
       experimental = false;
       plugins = false;
     };
   };
   ```

2. **Regular Updates**
   ```bash
   # Check for updates
   nixos-gui --check-updates
   
   # Update via Nix
   nix-channel --update
   nixos-rebuild switch
   ```

3. **Security Headers**
   ```nix
   services.nixos-gui = {
     securityHeaders = {
       enable = true;
       csp = "default-src 'self'";
       hsts = true;
       noSniff = true;
       xssProtection = true;
     };
   };
   ```

### Operational Security

1. **Monitor Logs**
   ```bash
   # Set up alerts for suspicious activity
   journalctl -u nixos-gui -f | grep -E "(failed|error|unauthorized)"
   ```

2. **Regular Audits**
   ```bash
   # Review user access
   nixos-gui users list
   
   # Check recent changes
   nixos-gui audit --category config --days 7
   ```

3. **Backup Configuration**
   ```bash
   # Backup current config
   nixos-gui config backup > backup.json
   
   # Encrypted backup
   nixos-gui config backup | gpg -e > backup.json.gpg
   ```

## Security Checklist

### Initial Setup
- [ ] Change default JWT secret
- [ ] Configure allowed groups
- [ ] Enable HTTPS
- [ ] Set up firewall rules
- [ ] Configure audit log retention

### Ongoing Maintenance
- [ ] Review audit logs weekly
- [ ] Update packages monthly
- [ ] Rotate secrets quarterly
- [ ] Security audit annually
- [ ] Test backup restoration

### Incident Response
- [ ] Document security contacts
- [ ] Define escalation procedures
- [ ] Test incident response plan
- [ ] Maintain security runbooks

## Reporting Security Issues

Found a security vulnerability? Please:

1. **DO NOT** open a public issue
2. Email security@nixos-gui.org with:
   - Vulnerability description
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)
3. Allow 90 days for fix before disclosure

We follow responsible disclosure and will:
- Acknowledge receipt within 48 hours
- Provide regular updates on progress
- Credit researchers (unless anonymity requested)
- Issue security advisories when fixed

## Additional Resources

- [OWASP Security Guidelines](https://owasp.org/)
- [NixOS Security](https://nixos.org/manual/nixos/stable/#sec-security)
- [Linux Security Modules](https://www.kernel.org/doc/html/latest/admin-guide/LSM/index.html)
- [CIS Benchmarks](https://www.cisecurity.org/)