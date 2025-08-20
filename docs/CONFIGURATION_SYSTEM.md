# 🎛️ Configuration System Documentation

## Overview

Nix for Humanity provides a comprehensive configuration system that allows users to customize every aspect of their experience. The system supports:

- **Multiple configuration sources** (system, user, project, environment)
- **Configuration profiles** (persona-specific settings)
- **Custom aliases and shortcuts**
- **Hierarchical configuration with inheritance**
- **Type-safe schema with validation**
- **Multiple file formats** (YAML, JSON, TOML)

## Quick Start

### Using the CLI

```bash
# Show current configuration
ask-nix settings show

# Run configuration wizard
ask-nix settings wizard

# Apply a profile
ask-nix settings use maya

# Set a specific value
ask-nix settings set ui.default_personality technical
ask-nix settings set performance.timeout 60

# List available profiles
ask-nix settings profiles

# Add an alias
ask-nix settings add-alias gc "collect garbage"

# Add a shortcut
ask-nix settings add-shortcut dev-setup "install git" "install vim" "install docker"
```

### Configuration File

Create `~/.config/nix-for-humanity/config.yaml`:

```yaml
# Basic configuration
ui:
  default_personality: "friendly"
  show_commands: true
  use_colors: true

performance:
  fast_mode: false
  timeout: 30

privacy:
  local_only: true
  data_collection: "minimal"

# Custom aliases
aliases:
  aliases:
    i: "install"
    s: "search"
    up: "update system"
  
  shortcuts:
    dev-setup:
      - "install git vim tmux"
      - "install docker"
```

## Configuration Schema

### Core Settings

```yaml
core:
  version: "0.8.3"              # Config version
  backend: "python"             # Backend: python, nodejs, hybrid
  data_directory: "~/.local/share/nix-for-humanity"
  cache_directory: "~/.cache/nix-for-humanity"
  log_level: "info"             # debug, info, warn, error
```

### UI Settings

```yaml
ui:
  default_personality: "friendly"  # minimal, friendly, encouraging, technical, accessible
  response_format: "structured"    # plain, structured, json, yaml
  show_commands: true             # Show underlying NixOS commands
  confirm_actions: true           # Ask before executing
  use_colors: true                # Colored output
  progress_indicators: true       # Show progress bars
  theme: "default"                # default, dark, light, high-contrast
  
  # Custom messages
  greeting: "Hello! How can I help?"
  farewell: "Goodbye!"
  error_prefix: "Oops!"
  success_prefix: "Great!"
```

### Performance Settings

```yaml
performance:
  fast_mode: false              # Speed over accuracy
  cache_responses: true         # Cache common queries
  parallel_processing: true     # Use multiple cores
  memory_limit: "512MB"         # Max memory usage
  timeout: 30                   # Command timeout (seconds)
  
  # Advanced
  worker_threads: 4
  cache_size: 1000
  batch_size: 10
  prefetch_common: true
```

### Privacy Settings

```yaml
privacy:
  data_collection: "minimal"    # none, minimal, standard, full
  share_anonymous_stats: false
  local_only: true
  encrypt_data: true
  auto_cleanup: true
  
  # Retention
  log_retention_days: 30
  cache_retention_days: 7
  learning_retention_days: 365
  
  # Security
  allowed_commands:
    - "nix-env"
    - "nixos-rebuild"
    - "nix-channel"
  forbidden_patterns:
    - "rm -rf /"
    - "dd if="
```

## Configuration Locations

Configuration files are loaded in this order (later overrides earlier):

1. **System**: `/etc/nix-for-humanity/config.yaml`
2. **User**: `~/.config/nix-for-humanity/config.yaml`
3. **Legacy**: `~/.nix-for-humanity/config.yaml` (auto-migrated)
4. **Project**: `./.luminous-nix/config.yaml`
5. **Environment**: `NIX_HUMANITY_*` variables

## Environment Variables

Override any setting with environment variables:

```bash
# Core settings
export NIX_HUMANITY_BACKEND=python
export NIX_HUMANITY_LOG_LEVEL=debug

# UI settings
export NIX_HUMANITY_PERSONALITY=minimal
export NIX_HUMANITY_NO_COLOR=true

# Performance
export NIX_HUMANITY_FAST_MODE=true
export NIX_HUMANITY_TIMEOUT=60

# Features
export NIX_HUMANITY_VOICE_ENABLED=true
export NIX_HUMANITY_LEARNING_ENABLED=true

# Accessibility
export NIX_HUMANITY_SCREEN_READER=true
export NIX_HUMANITY_HIGH_CONTRAST=true
```

## User Profiles

### Built-in Profiles

Nix for Humanity includes 10 pre-configured profiles for different user personas:

1. **grandma-rose** - Voice-first, patient, encouraging (age 75)
2. **maya** - Lightning-fast, minimal interface (16, ADHD)
3. **alex** - Screen-reader optimized (28, blind developer)
4. **dr-sarah** - Precise, technical (35, researcher)
5. **carlos** - Learning-focused (52, career switcher)
6. **viktor** - Simple, clear (67, ESL)
7. **david** - Efficient (42, tired sys admin)
8. **priya** - Quick, technical (34, developer)
9. **luna** - Structured, predictable (14, autistic)
10. **jamie** - Privacy-focused (19, privacy advocate)

### Using Profiles

```bash
# Apply a profile
ask-nix settings use maya

# Use profile for single command
ask-nix --profile alex "search screen readers"

# Set default profile
ask-nix settings set profile_name maya
```

### Creating Custom Profiles

```bash
# Save current settings as profile
ask-nix settings save-profile my-profile --description "My custom settings"

# Create profile in wizard
ask-nix settings wizard --profile base-profile
```

Or create manually in `~/.config/nix-for-humanity/profiles/my-profile.json`:

```json
{
  "name": "my-profile",
  "description": "My custom profile",
  "base_profile": "friendly",
  "config_overrides": {
    "ui": {
      "default_personality": "technical",
      "show_commands": true
    },
    "performance": {
      "fast_mode": true
    }
  }
}
```

## Aliases and Shortcuts

### Command Aliases

Map short names to full commands:

```yaml
aliases:
  aliases:
    i: "install"
    s: "search"
    r: "remove"
    up: "update system"
    gc: "collect garbage"
```

Use via CLI:
```bash
ask-nix settings add-alias ll "list installed"
ask-nix settings add-alias up "update system"
```

### Command Shortcuts

Execute multiple commands with one name:

```yaml
aliases:
  shortcuts:
    dev-setup:
      - "install git vim tmux"
      - "install docker"
      - "install vscode"
    
    clean:
      - "collect garbage"
      - "optimize store"
    
    full-update:
      - "update channels"
      - "update system"
      - "collect garbage"
```

Use via CLI:
```bash
ask-nix settings add-shortcut morning "update channels" "show news" "check updates"
```

## Advanced Features

### Configuration Validation

```bash
# Validate current config
ask-nix settings validate

# Validate specific file
ask-nix settings validate --file /path/to/config.yaml
```

### Import/Export

```bash
# Export current config
ask-nix settings export -o my-config.yaml

# Export as JSON
ask-nix settings export -o config.json --format json

# Import config
ask-nix settings import config.yaml

# Share with team (strips personal data)
ask-nix settings export --sanitize -o team-config.yaml
```

### Configuration Management

```bash
# Reset to defaults
ask-nix settings reset

# Show what changed
ask-nix settings diff

# Backup current config
ask-nix settings backup

# Restore from backup
ask-nix settings restore
```

## API Usage

### Python API

```python
from luminous_nix.config import get_config_manager, ConfigSchema

# Get manager
manager = get_config_manager()

# Access configuration
config = manager.config
print(f"Personality: {config.ui.default_personality}")

# Get specific value
timeout = manager.get('performance.timeout', default=30)

# Set value
manager.set('ui.use_colors', False)

# Apply profile
manager.apply_profile('maya')

# Save changes
manager.save()

# Add alias programmatically
manager.add_alias('gc', 'collect garbage')

# Validate
errors = manager.validate()
if errors:
    print(f"Config errors: {errors}")
```

### Creating Custom Configurations

```python
from luminous_nix.config.schema import ConfigSchema, UIConfig, Personality

# Create custom config
config = ConfigSchema()
config.ui.default_personality = Personality.TECHNICAL
config.performance.fast_mode = True
config.voice.enabled = True

# Add custom aliases
config.aliases.aliases['up'] = 'update system'

# Validate
errors = config.validate()

# Save
from luminous_nix.config.loader import ConfigLoader
loader = ConfigLoader()
loader.save_config(config, "~/.config/nix-for-humanity/config.yaml")
```

## Best Practices

1. **Start with a profile** - Choose the profile closest to your needs
2. **Use the wizard** - Run `ask-nix settings wizard` for guided setup
3. **Test changes** - Use `--dry-run` to preview command effects
4. **Version control** - Keep your config in git for team sharing
5. **Document custom settings** - Add comments to your config.yaml
6. **Regular backups** - Use `ask-nix settings backup` periodically

## Troubleshooting

### Config not loading

```bash
# Check which config files are loaded
ask-nix settings show --debug

# Validate syntax
ask-nix settings validate

# Reset if corrupted
ask-nix settings reset --backup-first
```

### Profile not found

```bash
# List all profiles
ask-nix settings profiles

# Check profile directory
ls ~/.config/nix-for-humanity/profiles/
```

### Environment variables not working

```bash
# Check current environment
env | grep NIX_HUMANITY

# Test with explicit override
NIX_HUMANITY_DEBUG=true ask-nix settings show
```

## Migration from Older Versions

The configuration system automatically migrates settings from older locations:

- `~/.nix-for-humanity/config.yaml` → `~/.config/nix-for-humanity/config.yaml`
- Old format settings are converted to new schema
- Backups are created as `.migrated` files

To manually migrate:

```bash
ask-nix settings migrate --from ~/.old-config.yaml
```

## Security Considerations

1. **API keys** - Store in separate secure files, not main config
2. **Permissions** - Config files should be readable only by owner
3. **Allowed commands** - Whitelist only necessary commands
4. **Forbidden patterns** - Add dangerous patterns to blocklist
5. **Encryption** - Enable `encrypt_data` for sensitive information

---

The configuration system is designed to grow with you - from simple aliases to complex multi-profile setups. Start simple and add complexity as needed!