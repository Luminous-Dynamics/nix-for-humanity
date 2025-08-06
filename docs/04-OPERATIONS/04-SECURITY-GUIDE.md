# 🔒 Security Guide - Nix for Humanity

*Comprehensive security features and configuration*

## Overview

Nix for Humanity implements defense-in-depth security with multiple layers of protection while maintaining usability for all personas. Our consciousness-first approach ensures security enhances rather than hinders the user experience.

## Security Architecture

### Multi-Layer Defense System

```
┌─────────────────────────────────────────┐
│         User Input Layer                 │
│    (Rate Limiting & Input Validation)    │
├─────────────────────────────────────────┤
│      Enhanced Threat Detection           │
│  (Pattern Analysis & Behavioral Checks)  │
├─────────────────────────────────────────┤
│        Trust & Context Layer             │
│    (User Profiling & Adaptive Security)  │
├─────────────────────────────────────────┤
│      Command Execution Sandbox           │
│    (Isolated Execution & Monitoring)     │
├─────────────────────────────────────────┤
│         System Protection                │
│      (NixOS Security Features)           │
└─────────────────────────────────────────┘
```

## Core Security Features

### 1. Enhanced Input Validation

Our enhanced validator provides comprehensive protection against:

- **Command Injection**: Blocks shell metacharacters and escape sequences
- **Path Traversal**: Prevents directory traversal attacks
- **XSS Attacks**: Sanitizes all output for safe display
- **SQL Injection**: Not applicable (no SQL queries from user input)
- **Buffer Overflow**: Input length limits enforced

Example validation in action:
```python
# Malicious input blocked
"install firefox; rm -rf /"  → Blocked: Command injection detected
"install ../../../etc/passwd" → Blocked: Path traversal detected
"install <script>alert()</script>" → Sanitized output
```

### 2. Rate Limiting

Protects against abuse and DoS attacks:

- **Per-User Limits**: 60 requests/minute, 600 requests/hour
- **Burst Protection**: Allows temporary spikes up to 10 requests
- **IP Whitelisting**: Trusted IPs bypass rate limiting
- **Adaptive Limits**: Adjusts based on user trust level

### 3. Behavioral Analysis

Detects anomalous usage patterns:

- **Command Sequences**: Identifies suspicious command patterns
- **Timing Analysis**: Detects automated/scripted attacks
- **Persona Consistency**: Alerts on behavior changes
- **Learning Patterns**: Adapts to legitimate user behavior

### 4. Trust-Based Security

Progressive trust system that adapts security based on user history:

- **Initial Trust**: New users start at 0.3 (low trust)
- **Trust Building**: +0.01 per successful command
- **Trust Penalties**: -0.1 per security violation
- **Trust Privileges**: Higher trust = fewer restrictions

Trust levels and their effects:
```yaml
Low Trust (0.0-0.3):
  - All commands require confirmation
  - Strict rate limiting
  - Enhanced validation active
  - No batch operations

Medium Trust (0.3-0.7):
  - Selective confirmations
  - Normal rate limiting
  - Standard validation
  - Limited batch operations

High Trust (0.7-0.9):
  - Minimal confirmations
  - Relaxed rate limiting
  - Optimized validation
  - Full batch operations

Trusted (0.9-1.0):
  - Confirmation only for dangerous commands
  - Minimal rate limiting
  - Fast-path validation
  - Advanced features unlocked
```

## Security Configuration

### Configuration File Location

Security settings are stored in `config/security_config.yaml`. The system searches for configuration in this order:

1. User-specified path
2. `~/.config/nix-humanity/security.yaml`
3. `/etc/nix-humanity/security.yaml`
4. Default built-in configuration

### Key Configuration Options

#### Global Security Level

```yaml
security:
  level: balanced  # Options: strict, balanced, permissive
```

- **Strict**: Maximum security, all features enabled
- **Balanced**: Good security with usability (default)
- **Permissive**: Relaxed security for trusted environments

#### Rate Limiting

```yaml
rate_limiting:
  enabled: true
  requests_per_minute: 60
  requests_per_hour: 600
  burst_size: 10
  whitelist:
    - "127.0.0.1"
    - "192.168.1.0/24"  # Trust local network
```

#### Validation Settings

```yaml
validation:
  max_input_length: 1000
  enhanced_detection: true
  behavioral_analysis:
    enabled: true
    history_window: 20
    anomaly_threshold: 0.7
```

#### Execution Policies

```yaml
execution:
  require_confirmation: true
  always_confirm:
    - "remove"
    - "update_system"
    - "rollback_system"
  max_execution_time: 300
  default_dry_run: true  # Safe by default
```

## Persona-Specific Security

Each persona has tailored security settings:

### Grandma Rose (Maximum Safety)
```yaml
grandma_rose:
  security_level: "strict"
  require_confirmation: true
  simplified_warnings: true
  voice_verification: true
```

### Maya (ADHD - Speed with Safety)
```yaml
maya_adhd:
  security_level: "balanced"
  require_confirmation: false  # For speed
  quick_undo: true
  batch_limits: 5  # Prevent accidents
```

### Dr. Sarah (Power User)
```yaml
dr_sarah:
  security_level: "balanced"
  advanced_features: true
  batch_operations: true
  detailed_logging: true
```

### Jamie (Privacy Advocate)
```yaml
jamie_privacy:
  security_level: "strict"
  anonymize_everything: true
  no_logging: true
  local_only: true
```

## Threat Detection Patterns

### Built-in Patterns

The system detects these threat patterns automatically:

1. **System Destruction**
   - `rm -rf /`
   - `dd if=/dev/zero of=/dev/sda`
   - Format commands

2. **Remote Execution**
   - `curl | sh` patterns
   - `wget && execute` chains
   - Base64 encoded commands

3. **Privilege Escalation**
   - Sudo injection attempts
   - SUID manipulation
   - Permission changes to system files

4. **Data Exfiltration**
   - Unexpected network connections
   - Large data transfers
   - Credential harvesting attempts

5. **Persistence Mechanisms**
   - Cron job creation
   - Service installation
   - Startup script modification

### Custom Patterns

Add your own threat patterns:

```yaml
threats:
  custom_patterns:
    - pattern: "bitcoinminer"
      threat_type: "cryptomining"
      severity: "high"
    - pattern: "tor.*hidden.*service"
      threat_type: "anonymity_tool"
      severity: "medium"
```

## Privacy Features

### Data Minimization

- **Local Processing**: All validation happens on-device
- **No Telemetry**: Unless explicitly enabled
- **Anonymized Logs**: User data stripped from logs
- **Ephemeral Sessions**: Data cleared after timeout

### User Control

- **Data Export**: Export all collected data
- **Data Deletion**: Complete removal on request
- **Opt-out Options**: Disable any tracking
- **Transparency**: See exactly what's collected

## Security Best Practices

### For Users

1. **Regular Updates**: Keep Nix for Humanity updated
2. **Strong Authentication**: Use secure passwords
3. **Review Confirmations**: Read before confirming
4. **Report Suspicious Behavior**: Help improve security

### For Administrators

1. **Review Logs Regularly**
   ```bash
   tail -f /var/log/nix-humanity/security.log
   ```

2. **Adjust Security Levels**
   ```bash
   # Edit security configuration
   nano ~/.config/nix-humanity/security.yaml
   
   # Reload configuration
   ask-nix --reload-config
   ```

3. **Monitor Trust Levels**
   ```bash
   ask-nix --show-trust-levels
   ```

4. **Update Threat Patterns**
   ```bash
   ask-nix --update-threat-db
   ```

## Incident Response

### If You Suspect a Security Issue

1. **Immediate Actions**
   - Stop using the affected command
   - Save any error messages
   - Note the exact input used

2. **Reporting**
   ```bash
   ask-nix --report-security-issue
   ```
   
   Or email: security@luminousdynamics.org

3. **Temporary Mitigation**
   ```bash
   # Increase security level temporarily
   ask-nix --security-level strict
   ```

### Security Alerts

The system provides real-time alerts for:

- Multiple failed attempts
- Detected threat patterns
- Unusual behavior patterns
- Trust level changes

View alerts:
```bash
ask-nix --show-security-alerts
```

## Advanced Security Features

### Command Sandboxing

All commands execute in a restricted environment:

- **Limited filesystem access**
- **Network restrictions**
- **Resource limits**
- **Audit logging**

### Rollback Protection

Automatic system snapshots before risky operations:

```bash
# System automatically creates snapshot
You: update system
System: Creating security snapshot... Done.
System: Proceeding with update...
```

### Learning Without Compromising Privacy

Our learning system:

- **Learns patterns, not data**
- **Stores behaviors, not content**
- **Generalizes for privacy**
- **Never shares individual data**

## Security Roadmap

### Current (v0.8.3)
- ✅ Basic input validation
- ✅ Rate limiting
- ✅ Enhanced threat detection
- ✅ Trust-based security
- ✅ Behavioral analysis

### Coming Soon
- 🚧 Voice authentication
- 🚧 Biometric monitoring
- 🚧 Advanced anomaly detection
- 🚧 Federated threat intelligence
- 🚧 Hardware security module support

## Compliance

Nix for Humanity is designed with privacy regulations in mind:

- **GDPR Compliant**: User control over data
- **CCPA Ready**: California privacy rights
- **HIPAA Considerations**: For healthcare use
- **SOC 2 Principles**: Security best practices

## Conclusion

Security in Nix for Humanity is not about restriction—it's about enabling safe, confident use of powerful system tools. Our multi-layered approach ensures that:

- Grandma Rose is protected from accidents
- Maya can work quickly without risk
- Dr. Sarah has power with accountability
- Jamie's privacy is absolutely respected

Security is not a feature—it's woven into every interaction, making the system safer for everyone while maintaining the natural, conversational interface that makes Nix for Humanity special.

---

*"Security that protects without imprisoning, that guides without restricting—this is consciousness-first security."* 🛡️🌊