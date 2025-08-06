# 🔄 NixOS CLI to GUI Migration Guide

This guide helps experienced NixOS command-line users transition to using NixOS GUI while maintaining their productivity.

## 📋 Table of Contents

1. [Why Use the GUI?](#why-use-the-gui)
2. [Command Mappings](#command-mappings)
3. [Workflow Translations](#workflow-translations)
4. [Power User Features](#power-user-features)
5. [Hybrid Usage](#hybrid-usage)
6. [Common Concerns](#common-concerns)

## Why Use the GUI?

### Benefits for CLI Users

- **Visual Feedback**: See system state at a glance
- **Error Prevention**: Validation before applying changes
- **Discoverability**: Find packages and options easier
- **History Tracking**: Visual audit trail of changes
- **Concurrent Tasks**: Multiple operations without terminal juggling
- **Team Collaboration**: Easier onboarding for new admins

### What You Don't Lose

- **Full Control**: All operations available via API
- **Automation**: Scriptable via REST API
- **Terminal Access**: Integrated terminal for complex tasks
- **Raw Config Access**: Direct configuration editing
- **Performance**: Optimized for speed

## Command Mappings

### Package Management

| CLI Command | GUI Equivalent | Shortcut |
|------------|----------------|----------|
| `nix search nixpkgs firefox` | Packages → Search "firefox" | `Ctrl+/` |
| `nix-env -iA nixpkgs.firefox` | Packages → Firefox → Install | `Enter` |
| `nix-env -e firefox` | Installed → Firefox → Remove | `Delete` |
| `nix-env -q` | Packages → Installed tab | `Alt+2` |
| `nix-env --upgrade` | Packages → Update All | `Ctrl+U` |

### Configuration Management

| CLI Command | GUI Equivalent | Shortcut |
|------------|----------------|----------|
| `sudo nano /etc/nixos/configuration.nix` | Configuration tab | `Alt+3` |
| `sudo nixos-rebuild switch` | Configuration → Apply | `Ctrl+Enter` |
| `sudo nixos-rebuild test` | Configuration → Test | `Ctrl+T` |
| `sudo nixos-rebuild boot` | Configuration → Apply → Boot only | - |
| `nixos-option services.openssh.enable` | Configuration → Search "openssh" | `Ctrl+F` |

### Service Management

| CLI Command | GUI Equivalent | Shortcut |
|------------|----------------|----------|
| `systemctl status nginx` | Services → nginx → Details | Click |
| `sudo systemctl start nginx` | Services → nginx → Start | `S` |
| `sudo systemctl stop nginx` | Services → nginx → Stop | `X` |
| `sudo systemctl restart nginx` | Services → nginx → Restart | `R` |
| `journalctl -u nginx -f` | Services → nginx → View Logs | `L` |

### Generation Management

| CLI Command | GUI Equivalent | Shortcut |
|------------|----------------|----------|
| `sudo nix-env --list-generations` | Generations tab | `Alt+4` |
| `sudo nixos-rebuild switch --rollback` | Generations → Previous → Switch | Click |
| `sudo nix-collect-garbage -d` | Generations → Clean Old | `Ctrl+D` |
| `sudo nix-env --switch-generation 42` | Generations → #42 → Switch | Click |

## Workflow Translations

### 1. Installing Software

**CLI Workflow:**
```bash
nix search nixpkgs neovim
nix-env -iA nixpkgs.neovim
# or edit configuration.nix
sudo nixos-rebuild switch
```

**GUI Workflow:**
1. Press `Ctrl+/` to focus search
2. Type "neovim"
3. Click Install or press Enter
4. (Optional) Add to configuration for persistence

### 2. Troubleshooting Services

**CLI Workflow:**
```bash
systemctl status postgresql
journalctl -u postgresql -n 50
sudo systemctl restart postgresql
tail -f /var/log/postgresql/postgresql.log
```

**GUI Workflow:**
1. Services tab → Filter "postgres"
2. Click service row for details
3. View inline status and recent logs
4. Click Restart button
5. Enable "Follow Logs" for real-time updates

### 3. System Update

**CLI Workflow:**
```bash
sudo nix-channel --update
sudo nixos-rebuild switch --upgrade
# Check for errors
journalctl -xe
```

**GUI Workflow:**
1. Dashboard → Update System widget
2. Click "Check Updates"
3. Review changes in diff view
4. Click "Apply Updates"
5. Monitor progress with real-time feedback

### 4. Configuration Rollback

**CLI Workflow:**
```bash
# Something broke
sudo nixos-rebuild switch --rollback
# or specific generation
sudo nix-env --switch-generation 45
```

**GUI Workflow:**
1. Generations tab
2. Find last working generation (marked with status)
3. Click "Compare" to see differences
4. Click "Switch" to rollback
5. Optional: Set as boot default

## Power User Features

### 1. Keyboard Navigation

Complete keyboard control without mouse:

```
Tab         - Navigate elements
Shift+Tab   - Navigate backwards
Arrow Keys  - Navigate lists/menus
Enter       - Activate/Select
Escape      - Cancel/Close
Space       - Toggle checkboxes
```

### 2. Command Palette

Press `Ctrl+P` to open command palette:

```
> install firefox       - Quick install
> restart nginx        - Service control  
> edit ssh config      - Jump to config section
> generation 42        - Switch generation
> help shortcuts       - View all shortcuts
```

### 3. API Integration

Use the GUI's API from CLI:

```bash
# Get auth token
TOKEN=$(curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass"}' | jq -r .token)

# Search packages
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/packages/search?q=firefox

# Install package
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/packages/install \
  -d '{"package":"firefox"}'

# Apply configuration
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/config/apply
```

### 4. Integrated Terminal

Press `Ctrl+`` ` to open integrated terminal:

- Runs in GUI context
- Access to GUI environment variables
- Quick commands without leaving GUI
- History shared with main terminal

### 5. Batch Operations

Select multiple items with:
- `Ctrl+Click` - Toggle selection
- `Shift+Click` - Range selection
- `Ctrl+A` - Select all

Then apply bulk actions:
- Install/remove multiple packages
- Start/stop multiple services
- Compare multiple generations

## Hybrid Usage

### Best of Both Worlds

Use GUI for:
- System overview and monitoring
- Package discovery and search
- Visual configuration editing
- Service management
- Team collaboration

Use CLI for:
- Automation and scripting
- Complex operations
- Remote management
- Quick one-liners
- Pipeline integration

### CLI Aliases for GUI

Add to your shell config:

```bash
# Quick GUI launchers
alias nix-gui='xdg-open http://localhost:8080'
alias ngs='nix-gui-search'  # Custom search function
alias ngi='nix-gui-install' # Custom install function

# GUI API shortcuts
nix-gui-search() {
  curl -s "http://localhost:8080/api/packages/search?q=$1" | jq
}

nix-gui-install() {
  curl -X POST "http://localhost:8080/api/packages/install" \
    -d "{\"package\":\"$1\"}"
}

# Open GUI to specific section
alias ngp='xdg-open http://localhost:8080/packages'
alias ngc='xdg-open http://localhost:8080/config'
alias ngs='xdg-open http://localhost:8080/services'
```

## Common Concerns

### "I'm faster in the terminal"

- **True for**: Single, well-known commands
- **GUI wins for**: Exploration, monitoring, complex workflows
- **Solution**: Use both! GUI doesn't replace CLI

### "GUIs hide important details"

- **Not this one**: Full config access, detailed logs, raw API
- **Transparency**: Every action shows equivalent CLI command
- **Advanced mode**: Disable simplifications

### "I need my custom scripts"

- **API First**: Everything in GUI available via API
- **Webhooks**: Trigger scripts from GUI events
- **Integration**: Call your scripts from GUI

### "What about remote servers?"

- **Web-based**: Access from anywhere
- **SSH Tunnel**: `ssh -L 8080:localhost:8080 server`
- **VPN**: Secure remote access
- **API**: Scriptable remote management

### "Configuration flexibility"

- **Raw Edit**: Full configuration.nix access
- **Templates**: Save and share configurations
- **Modules**: GUI respects all NixOS modules
- **Version Control**: Git integration for configs

## Tips for CLI Veterans

1. **Start with shortcuts**: Learn keyboard shortcuts first
2. **Use command palette**: Faster than clicking for power users
3. **Customize layout**: Arrange dashboard for your workflow
4. **Enable advanced mode**: Show all options and details
5. **Use the API**: Script complex workflows
6. **Keep terminal handy**: `Ctrl+`` ` for quick access

## Gradual Migration Path

### Week 1: Monitoring Only
- Use GUI for system dashboard
- Keep using CLI for changes
- Get familiar with layout

### Week 2: Package Management  
- Try package search in GUI
- Compare with CLI results
- Use GUI for exploration

### Week 3: Service Management
- Monitor services in GUI
- Try start/stop operations
- Use log viewer

### Week 4: Configuration
- Edit configuration in GUI
- Use validation features
- Try rollback via GUI

### Month 2: Full Integration
- Use GUI as primary interface
- Fall back to CLI as needed
- Share knowledge with team

## Advanced Integration

### Custom Commands

Add your commands to GUI:

```nix
services.nixos-gui.customCommands = {
  "Backup System" = {
    command = "/usr/local/bin/backup-system.sh";
    icon = "save";
    confirmation = true;
  };
  "Deploy to Production" = {
    command = "deploy-prod";
    icon = "rocket";
    requiresAuth = true;
  };
};
```

### Workflow Automation

```javascript
// GUI automation script
const gui = require('nixos-gui-client');

async function updateAndRestart() {
  await gui.packages.update();
  await gui.config.apply();
  await gui.services.restart(['nginx', 'postgresql']);
  await gui.notify('System updated and restarted');
}
```

## Conclusion

NixOS GUI complements CLI usage rather than replacing it. Power users gain:

- Visual system state awareness
- Faster package discovery
- Safer configuration changes
- Better team collaboration
- Preserved automation capabilities

The GUI is another tool in your toolbox - use it when it helps, skip it when it doesn't.

---

**Remember**: `F1` shows all keyboard shortcuts, and `Ctrl+P` opens the command palette for CLI-like efficiency!