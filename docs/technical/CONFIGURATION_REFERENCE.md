# ⚙️ Configuration Reference - Nix for Humanity

> Complete reference for all configuration options

**Last Updated**: 2025-07-25
**Status**: Current
**Audience**: System Administrators, Advanced Users

## Overview

This document provides a complete reference for all configuration options in Nix for Humanity. Configuration can be set through NixOS modules, environment variables, or runtime settings.

## Table of Contents

- [Configuration Methods](#configuration-methods)
- [Core Settings](#core-settings)
- [Interface Configuration](#interface-configuration)
- [Learning System](#learning-system)
- [Voice Configuration](#voice-configuration)
- [Security Settings](#security-settings)
- [Performance Tuning](#performance-tuning)
- [Integration Options](#integration-options)
- [Advanced Settings](#advanced-settings)
- [Environment Variables](#environment-variables)
- [Examples](#examples)

## Configuration Methods

### 1. NixOS Module (Recommended)

```nix
# /etc/nixos/configuration.nix
{
  services.nix-for-humanity = {
    enable = true;
    # ... settings here
  };
}
```

### 2. Home Manager

```nix
# ~/.config/home-manager/home.nix
{
  programs.nix-for-humanity = {
    enable = true;
    # ... settings here
  };
}
```

### 3. Configuration File

```yaml
# ~/.config/nix-for-humanity/config.yaml
interface:
  language: en-US
  theme: auto
# ... more settings
```

### 4. Environment Variables

```bash
export NFH_LANGUAGE="en-US"
export NFH_DEBUG="true"
```

## Core Settings

### `enable`
- **Type**: Boolean
- **Default**: `false`
- **Description**: Enable Nix for Humanity service
- **Example**: `enable = true;`

### `package`
- **Type**: Package
- **Default**: `pkgs.nix-for-humanity`
- **Description**: Package to use (for custom builds)
- **Example**: `package = pkgs.nix-for-humanity-unstable;`

### `user`
- **Type**: String
- **Default**: Current user
- **Description**: User to run service as
- **Example**: `user = "alice";`

### `multiUser`
- **Type**: Boolean
- **Default**: `false`
- **Description**: Enable multi-user mode
- **Example**: `multiUser = true;`

### `users`
- **Type**: List of strings
- **Default**: `[]`
- **Description**: Users allowed to use the service (multiUser mode)
- **Example**: `users = [ "alice" "bob" "charlie" ];`

## Interface Configuration

### `interface.defaultInput`
- **Type**: Enum: `"text"` | `"voice"` | `"auto"`
- **Default**: `"text"`
- **Description**: Default input method
- **Example**: `interface.defaultInput = "voice";`

### `interface.language`
- **Type**: String (ISO 639-1)
- **Default**: `"en-US"`
- **Description**: Interface language
- **Supported**: en-US, en-GB, es, fr, de, ja, zh
- **Example**: `interface.language = "es";`

### `interface.theme`
- **Type**: Enum: `"light"` | `"dark"` | `"auto"`
- **Default**: `"auto"`
- **Description**: Color theme
- **Example**: `interface.theme = "dark";`

### `interface.fontSize`
- **Type**: Integer (10-32)
- **Default**: `14`
- **Description**: Base font size in pixels
- **Example**: `interface.fontSize = 18;`

### `interface.highContrast`
- **Type**: Boolean
- **Default**: `false`
- **Description**: Enable high contrast mode
- **Example**: `interface.highContrast = true;`

### `interface.animations`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Enable interface animations
- **Example**: `interface.animations = false;`

### `interface.compactMode`
- **Type**: Boolean
- **Default**: `false`
- **Description**: Use compact interface layout
- **Example**: `interface.compactMode = true;`

## Learning System

### `learning.enabled`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Enable AI learning from interactions
- **Example**: `learning.enabled = false;`

### `learning.adaptationSpeed`
- **Type**: Enum: `"slow"` | `"moderate"` | `"fast"`
- **Default**: `"moderate"`
- **Description**: How quickly AI adapts to patterns
- **Example**: `learning.adaptationSpeed = "fast";`

### `learning.privacyLevel`
- **Type**: Enum: `"minimal"` | `"balanced"` | `"full"`
- **Default**: `"balanced"`
- **Description**: Privacy vs learning trade-off
- **Details**:
  - `minimal`: No persistence, no learning
  - `balanced`: Learn patterns, respect privacy
  - `full`: Maximum learning and adaptation
- **Example**: `learning.privacyLevel = "minimal";`

### `learning.retentionDays`
- **Type**: Integer (0-365)
- **Default**: `30`
- **Description**: Days to retain learning data (0 = forever)
- **Example**: `learning.retentionDays = 7;`

### `learning.shareAnonymousPatterns`
- **Type**: Boolean
- **Default**: `false`
- **Description**: Share anonymized patterns with community
- **Example**: `learning.shareAnonymousPatterns = true;`

### `learning.excludePatterns`
- **Type**: List of strings
- **Default**: `[]`
- **Description**: Patterns to never learn
- **Example**: `learning.excludePatterns = [ "password" "secret" ];`

## Voice Configuration

### `voice.enabled`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Enable voice input
- **Example**: `voice.enabled = false;`

### `voice.engine`
- **Type**: Enum: `"whisper"` | `"webkit"` | `"native"`
- **Default**: `"whisper"`
- **Description**: Voice recognition engine
- **Example**: `voice.engine = "native";`

### `voice.model`
- **Type**: String
- **Default**: `"base.en"`
- **Description**: Whisper model to use
- **Options**: 
  - `"tiny.en"` - 39MB, fastest
  - `"base.en"` - 142MB, balanced
  - `"small.en"` - 466MB, accurate
  - `"medium.en"` - 1.5GB, very accurate
- **Example**: `voice.model = "small.en";`

### `voice.pushToTalk`
- **Type**: Boolean
- **Default**: `false`
- **Description**: Require button press for voice
- **Example**: `voice.pushToTalk = true;`

### `voice.autoDetectLanguage`
- **Type**: Boolean
- **Default**: `false`
- **Description**: Automatically detect spoken language
- **Example**: `voice.autoDetectLanguage = true;`

### `voice.audio.device`
- **Type**: String
- **Default**: `"default"`
- **Description**: Audio input device
- **Example**: `voice.audio.device = "hw:1,0";`

### `voice.audio.sampleRate`
- **Type**: Integer
- **Default**: `16000`
- **Description**: Audio sample rate in Hz
- **Example**: `voice.audio.sampleRate = 48000;`

### `voice.audio.noiseSupression`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Enable noise suppression
- **Example**: `voice.audio.noiseSupression = false;`

### `voice.audio.echoCancellation`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Enable echo cancellation
- **Example**: `voice.audio.echoCancellation = false;`

### `voice.audio.gain`
- **Type**: Float (0.1-10.0)
- **Default**: `1.0`
- **Description**: Microphone gain adjustment
- **Example**: `voice.audio.gain = 1.5;`

## Security Settings

### `security.sandboxing`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Enable command sandboxing
- **Example**: `security.sandboxing = false;`

### `security.auditLogging`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Log all commands for audit
- **Example**: `security.auditLogging = false;`

### `security.requireAuth`
- **Type**: List of strings
- **Default**: `[ "system-modification" ]`
- **Description**: Operations requiring authentication
- **Options**: 
  - `"system-modification"`
  - `"package-installation"`
  - `"service-management"`
  - `"user-management"`
  - `"all"`
- **Example**: `security.requireAuth = [ "all" ];`

### `security.allowedCommands`
- **Type**: List of strings or null
- **Default**: `null` (all allowed)
- **Description**: Whitelist of allowed operations
- **Example**: `security.allowedCommands = [ "search" "status" "help" ];`

### `security.blockedCommands`
- **Type**: List of strings
- **Default**: `[]`
- **Description**: Blacklist of blocked operations
- **Example**: `security.blockedCommands = [ "delete" "remove" ];`

### `security.paranoidMode`
- **Type**: Boolean
- **Default**: `false`
- **Description**: Require confirmation for everything
- **Example**: `security.paranoidMode = true;`

### `security.encryption.enabled`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Encrypt stored data
- **Example**: `security.encryption.enabled = false;`

### `security.encryption.algorithm`
- **Type**: String
- **Default**: `"aes-256-gcm"`
- **Description**: Encryption algorithm
- **Example**: `security.encryption.algorithm = "chacha20-poly1305";`

## Performance Tuning

### `performance.maxMemory`
- **Type**: String
- **Default**: `"2G"`
- **Description**: Maximum memory usage
- **Example**: `performance.maxMemory = "4G";`

### `performance.cpuQuota`
- **Type**: String
- **Default**: `"200%"`
- **Description**: CPU quota (100% = 1 core)
- **Example**: `performance.cpuQuota = "400%";`

### `performance.cache.enabled`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Enable response caching
- **Example**: `performance.cache.enabled = false;`

### `performance.cache.size`
- **Type**: String
- **Default**: `"1G"`
- **Description**: Maximum cache size
- **Example**: `performance.cache.size = "500M";`

### `performance.cache.ttl`
- **Type**: Integer
- **Default**: `3600`
- **Description**: Cache time-to-live in seconds
- **Example**: `performance.cache.ttl = 7200;`

### `performance.models.preload`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Preload AI models at startup
- **Example**: `performance.models.preload = false;`

### `performance.models.quantization`
- **Type**: Enum: `"none"` | `"int8"` | `"int4"`
- **Default**: `"int8"`
- **Description**: Model quantization for size/speed
- **Example**: `performance.models.quantization = "int4";`

### `performance.parallelism`
- **Type**: Integer
- **Default**: Number of CPU cores
- **Description**: Maximum parallel operations
- **Example**: `performance.parallelism = 4;`

## Integration Options

### `integrations.sacredBridge.enabled`
- **Type**: Boolean
- **Default**: `false`
- **Description**: Connect to Sacred Bridge service
- **Example**: `integrations.sacredBridge.enabled = true;`

### `integrations.sacredBridge.url`
- **Type**: String
- **Default**: `"http://localhost:7777"`
- **Description**: Sacred Bridge URL
- **Example**: `integrations.sacredBridge.url = "https://bridge.local:7777";`

### `integrations.ai.enabled`
- **Type**: Boolean
- **Default**: `false`
- **Description**: Enable external AI services
- **Example**: `integrations.ai.enabled = true;`

### `integrations.ai.provider`
- **Type**: Enum: `"local"` | `"claude"` | `"openai"` | `"ollama"`
- **Default**: `"local"`
- **Description**: AI provider for enhanced capabilities
- **Example**: `integrations.ai.provider = "claude";`

### `integrations.ai.apiKey`
- **Type**: String or null
- **Default**: `null`
- **Description**: API key for cloud AI services
- **Example**: `integrations.ai.apiKey = "sk-...";`

### `integrations.ai.model`
- **Type**: String
- **Default**: Provider-specific
- **Description**: AI model to use
- **Example**: `integrations.ai.model = "claude-3-sonnet";`

### `integrations.plugins.enabled`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Enable plugin system
- **Example**: `integrations.plugins.enabled = false;`

### `integrations.plugins.directory`
- **Type**: String
- **Default**: `"~/.config/nix-for-humanity/plugins"`
- **Description**: Plugin directory
- **Example**: `integrations.plugins.directory = "/opt/nfh/plugins";`

### `integrations.plugins.autoLoad`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Automatically load plugins
- **Example**: `integrations.plugins.autoLoad = false;`

## Advanced Settings

### `advanced.debugMode`
- **Type**: Boolean
- **Default**: `false`
- **Description**: Enable debug logging
- **Example**: `advanced.debugMode = true;`

### `advanced.logLevel`
- **Type**: Enum: `"error"` | `"warn"` | `"info"` | `"debug"` | `"trace"`
- **Default**: `"info"`
- **Description**: Logging verbosity
- **Example**: `advanced.logLevel = "debug";`

### `advanced.telemetry.enabled`
- **Type**: Boolean
- **Default**: `false`
- **Description**: Send anonymous usage statistics
- **Example**: `advanced.telemetry.enabled = true;`

### `advanced.experimental.enabled`
- **Type**: Boolean
- **Default**: `false`
- **Description**: Enable experimental features
- **Example**: `advanced.experimental.enabled = true;`

### `advanced.customPrompts`
- **Type**: Attribute set
- **Default**: `{}`
- **Description**: Custom prompt templates
- **Example**: 
  ```nix
  advanced.customPrompts = {
    greeting = "Hello! How can I assist you today?";
    error = "I encountered an issue: {error}";
  };
  ```

### `advanced.hooks.preCommand`
- **Type**: String or null
- **Default**: `null`
- **Description**: Script to run before commands
- **Example**: `advanced.hooks.preCommand = "/usr/local/bin/pre-command.sh";`

### `advanced.hooks.postCommand`
- **Type**: String or null
- **Default**: `null`
- **Description**: Script to run after commands
- **Example**: `advanced.hooks.postCommand = "/usr/local/bin/post-command.sh";`

## Environment Variables

All settings can be overridden with environment variables:

| Variable | Description | Example |
|----------|-------------|------|
| `NFH_DEBUG` | Enable debug mode | `true` |
| `NFH_LOG_LEVEL` | Set log level | `debug` |
| `NFH_LANGUAGE` | Interface language | `es` |
| `NFH_THEME` | Color theme | `dark` |
| `NFH_VOICE_ENABLED` | Enable voice | `false` |
| `NFH_LEARNING_ENABLED` | Enable learning | `false` |
| `NFH_DATA_DIR` | Data directory | `/var/lib/nfh` |
| `NFH_CACHE_DIR` | Cache directory | `/var/cache/nfh` |
| `NFH_CONFIG_FILE` | Config file path | `/etc/nfh/config.yaml` |

## Examples

### Minimal Configuration

```nix
{
  services.nix-for-humanity = {
    enable = true;
  };
}
```

### Privacy-Focused Configuration

```nix
{
  services.nix-for-humanity = {
    enable = true;
    
    learning = {
      enabled = false;
      privacyLevel = "minimal";
    };
    
    voice.enabled = false;
    
    security = {
      paranoidMode = true;
      auditLogging = false;
    };
    
    integrations.ai.enabled = false;
  };
}
```

### Developer Configuration

```nix
{
  services.nix-for-humanity = {
    enable = true;
    
    interface = {
      defaultInput = "text";
      theme = "dark";
      compactMode = true;
    };
    
    learning = {
      adaptationSpeed = "fast";
      privacyLevel = "full";
    };
    
    performance = {
      maxMemory = "8G";
      cpuQuota = "800%";
      models.quantization = "none";
    };
    
    advanced = {
      debugMode = true;
      experimental.enabled = true;
    };
  };
}
```

### Multi-User Family Configuration

```nix
{
  services.nix-for-humanity = {
    enable = true;
    multiUser = true;
    users = [ "parent" "teen" "child" ];
    
    interface = {
      defaultInput = "voice";
      language = "en-US";
      fontSize = 16;
    };
    
    security = {
      requireAuth = [ "system-modification" "package-installation" ];
      blockedCommands = [ "delete" "remove" ];
    };
    
    voice = {
      enabled = true;
      pushToTalk = true;
      model = "small.en";
    };
  };
}
```

### Accessibility-Optimized Configuration

```nix
{
  services.nix-for-humanity = {
    enable = true;
    
    interface = {
      fontSize = 20;
      highContrast = true;
      animations = false;
    };
    
    voice = {
      enabled = true;
      audio = {
        gain = 2.0;
        noiseSupression = true;
      };
    };
    
    learning = {
      adaptationSpeed = "slow";
    };
  };
}
```

## Validation

Configuration is validated at:
1. **Build time** - NixOS module system checks types
2. **Runtime** - Service validates on startup
3. **Hot reload** - Changes validated before applying

Invalid configuration will:
- Prevent NixOS rebuild (module errors)
- Fall back to defaults (runtime errors)
- Log detailed error messages

## Migration from Previous Versions

When upgrading:
1. Old settings are automatically migrated
2. Deprecated options show warnings
3. Breaking changes documented in CHANGELOG.md

## Getting Help

- Check your current configuration: `nix-for-humanity --show-config`
- Validate configuration: `nix-for-humanity --validate-config`
- Generate example config: `nix-for-humanity --generate-config`
- Ask your AI partner: "show me my current settings"

---

**Remember**: Start simple and add configuration as needed. The defaults are designed to work well for most users.

*"The best configuration is the one you don't have to think about."*