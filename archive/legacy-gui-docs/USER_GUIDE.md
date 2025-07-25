# NixOS GUI User Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard](#dashboard)
3. [Package Management](#package-management)
4. [Configuration Management](#configuration-management)
5. [Service Management](#service-management)
6. [Generation Management](#generation-management)
7. [User Management](#user-management)
8. [System Information](#system-information)
9. [Keyboard Shortcuts](#keyboard-shortcuts)
10. [Tips and Tricks](#tips-and-tricks)

## Getting Started

### First Login

When you first access NixOS GUI:

1. **Navigate to the GUI**
   - Local: http://localhost:8080
   - Remote: http://your-server-ip:8080

2. **Login**
   - Username: Your system username
   - Password: Your system password
   - You must be in the `wheel` or `nixos-gui` group

3. **Onboarding Wizard**
   - The wizard will guide you through initial setup
   - Set your preferences (theme, notifications)
   - Learn about key features
   - Can be re-run from Help menu

### Interface Overview

```
┌─────────────────────────────────────────────┐
│  [≡] NixOS GUI            [🔍] [👤] [?] [⚙️] │ <- Header
├─────────────┬───────────────────────────────┤
│             │                               │
│ ▼ Dashboard │                               │
│ 📦 Packages │        Main Content Area      │
│ ⚙️ Config   │                               │
│ 🔧 Services │                               │
│ 🔄 Gens     │                               │
│ 👥 Users    │                               │
│ ℹ️ System   │                               │
│             │                               │
└─────────────┴───────────────────────────────┘
     Sidebar              Content
```

## Dashboard

The dashboard provides a quick overview of your system:

### System Status
- **Hostname**: Your system's name
- **NixOS Version**: Currently running version
- **Uptime**: How long the system has been running
- **Load Average**: System load (1, 5, 15 minutes)

### Quick Stats
- **Installed Packages**: Total count with size
- **Running Services**: Active system services
- **System Generations**: Available configurations
- **Disk Usage**: Root filesystem usage

### Recent Activity
- Last configuration changes
- Recent package installations
- Service status changes
- Error notifications

## Package Management

### Searching Packages

1. **Basic Search**
   - Type package name in search box
   - Results appear as you type
   - Shows package name, version, description

2. **Advanced Search**
   - Click filter icon
   - Filter by:
     - Category (development, games, tools)
     - Platform (linux, darwin)
     - License (free, unfree)
     - Installed status

3. **Search Tips**
   - Use wildcards: `fire*` finds firefox, firewall, etc.
   - Search descriptions: Add quotes for exact phrases
   - Keyboard shortcut: `Ctrl+K` for quick search

### Installing Packages

1. **Find Package**
   - Search for desired package
   - Read description and details

2. **Check Requirements**
   - Click package name for details
   - View dependencies
   - Check disk space requirement

3. **Install**
   - Click "Install" button
   - Review changes in preview
   - Confirm installation

4. **Monitor Progress**
   - Progress bar shows download/build status
   - View logs if needed
   - Get notification when complete

### Removing Packages

1. **Find Installed Package**
   - Go to "Installed" tab
   - Or search and look for checkmark

2. **Remove**
   - Click "Remove" button
   - **Warning**: Some packages are system-critical
   - Review dependencies that will also be removed

3. **Confirm**
   - Check the impact
   - Confirm removal
   - System rebuilds automatically

### Package Details

Click any package to see:
- **Description**: What the package does
- **Homepage**: Project website
- **License**: Software license
- **Maintainers**: Who maintains it in nixpkgs
- **Platforms**: Supported systems
- **Dependencies**: Required packages
- **Dependents**: Packages that need this

## Configuration Management

### Editing Configuration

1. **Open Editor**
   - Click "Configuration" in sidebar
   - Your `/etc/nixos/configuration.nix` loads

2. **Editor Features**
   - Syntax highlighting for Nix
   - Auto-completion for options
   - Error highlighting in real-time
   - Bracket matching
   - Code folding

3. **Making Changes**
   ```nix
   # Example: Add a package
   environment.systemPackages = with pkgs; [
     firefox
     vim
     git
   ];
   
   # Example: Enable a service
   services.openssh.enable = true;
   ```

### Validation

Before applying changes:

1. **Syntax Check**
   - Click "Validate" button
   - Checks for Nix syntax errors
   - Highlights problematic lines

2. **Evaluation Test**
   - Tests if configuration evaluates
   - Catches missing options
   - Identifies undefined variables

3. **Dry Run**
   - Shows what would change
   - No actual system modifications
   - Safe way to preview

### Applying Changes

1. **Save Configuration**
   - Click "Save" or `Ctrl+S`
   - Creates automatic backup

2. **Apply Changes**
   - Click "Apply" button
   - Choose rebuild type:
     - **Switch**: Apply immediately
     - **Boot**: Apply on next boot
     - **Test**: Apply temporarily

3. **Monitor Progress**
   - Build log appears
   - Shows each derivation built
   - Errors highlighted in red

4. **Rollback if Needed**
   - If something breaks, use previous generation
   - Or restore from backup

### Configuration Tips

#### Organizing Imports
```nix
{ config, pkgs, ... }:
{
  imports = [
    ./hardware-configuration.nix
    ./networking.nix
    ./users.nix
    ./services.nix
  ];
}
```

#### Using Variables
```nix
let
  myPackages = with pkgs; [
    firefox
    thunderbird
  ];
in {
  environment.systemPackages = myPackages;
}
```

## Service Management

### Viewing Services

1. **Service List**
   - Shows all systemd services
   - Status indicators:
     - 🟢 Active (running)
     - 🔴 Failed
     - ⚪ Inactive
     - 🔄 Activating

2. **Filtering**
   - Search by name
   - Filter by status
   - Show only enabled services
   - System vs user services

### Managing Services

1. **Start/Stop**
   - Click toggle to start/stop
   - Requires authentication
   - See immediate status change

2. **Enable/Disable**
   - Right-click → Enable/Disable
   - Persists across reboots
   - Updates configuration.nix

3. **Restart**
   - Useful after config changes
   - Minimal downtime
   - Shows restart status

### Service Details

Click any service to see:
- **Status**: Current state and substatus
- **Description**: What the service does
- **Loaded**: Service file location
- **Process**: Main PID and command
- **Memory**: Current usage
- **Logs**: Recent log entries

### Viewing Logs

1. **Quick View**
   - Last 50 lines in detail view
   - Color-coded by severity

2. **Full Logs**
   - Click "View Full Logs"
   - Opens log viewer
   - Features:
     - Search/filter
     - Export logs
     - Follow mode (real-time)

## Generation Management

### Understanding Generations

Each system rebuild creates a new generation:
- Snapshot of your system configuration
- Allows rollback to any previous state
- Bootloader entries for each generation

### Generation List

Shows for each generation:
- **Number**: Generation ID
- **Date**: When created
- **Current**: Which is active
- **Description**: What changed
- **Size**: Disk space used

### Switching Generations

1. **Temporary Switch**
   - Click "Switch To"
   - Changes active generation
   - Reverts on reboot

2. **Permanent Switch**
   - Click "Set as Default"
   - Updates bootloader
   - Persists after reboot

### Comparing Generations

1. **Select Two Generations**
   - Check boxes next to generations
   - Click "Compare"

2. **View Differences**
   - Configuration diff
   - Package changes
   - Service modifications

### Cleaning Up

1. **Delete Old Generations**
   - Select generations to remove
   - Cannot delete current/default
   - Frees disk space

2. **Automatic Cleanup**
   - Set retention policy
   - Keep last N generations
   - Keep by age

## User Management

### Viewing Users

Lists all system users with:
- Username and full name
- Groups membership
- Home directory
- Shell
- Last login

### Managing Users

1. **Add User**
   - Click "Add User"
   - Fill in details:
     - Username (required)
     - Full name
     - Password
     - Groups
     - Shell

2. **Modify User**
   - Click username
   - Change properties
   - Add/remove groups
   - Reset password

3. **Delete User**
   - Select user
   - Click "Delete"
   - Option to keep home directory

### Group Management

1. **View Groups**
   - Switch to Groups tab
   - See members of each group

2. **Important Groups**
   - `wheel`: System administrators
   - `nixos-gui`: GUI access
   - `audio`: Sound access
   - `video`: Graphics access
   - `networkmanager`: Network configuration

## System Information

### Hardware Info
- CPU model and cores
- Memory (RAM) usage
- Disk drives and partitions
- Network interfaces
- Graphics cards

### Software Info
- NixOS version
- Kernel version
- Nix version
- Channel information
- Architecture (x86_64, etc.)

### Performance Metrics
- CPU usage graph
- Memory usage over time
- Disk I/O statistics
- Network traffic
- System load

## Keyboard Shortcuts

### Global Shortcuts
- `F1` - Open help
- `Ctrl+K` - Quick search
- `Ctrl+S` - Save current work
- `Ctrl+Z` - Undo
- `Ctrl+Shift+Z` - Redo
- `Esc` - Close dialogs

### Navigation
- `Alt+1` - Go to Dashboard
- `Alt+2` - Go to Packages
- `Alt+3` - Go to Configuration
- `Alt+4` - Go to Services
- `Alt+5` - Go to Generations
- `Alt+6` - Go to Users
- `Alt+7` - Go to System Info

### Editor Shortcuts
- `Ctrl+F` - Find
- `Ctrl+H` - Find and replace
- `Ctrl+G` - Go to line
- `Ctrl+/` - Toggle comment
- `Tab` - Indent
- `Shift+Tab` - Outdent

### Admin Shortcuts
- `Ctrl+Shift+C` - Configuration editor
- `Ctrl+Shift+R` - Rebuild system
- `Ctrl+Shift+S` - System check
- `Ctrl+Shift+A` - Audit logs

## Tips and Tricks

### Performance Tips

1. **Use Search Filters**
   - Narrow results before searching
   - Reduces server load
   - Faster results

2. **Batch Operations**
   - Install multiple packages at once
   - Group configuration changes
   - Single rebuild is faster

3. **Monitor Resources**
   - Check CPU/RAM before heavy operations
   - Schedule updates during low usage
   - Use nice levels for builds

### Safety Tips

1. **Always Validate**
   - Before applying configuration
   - Catches errors early
   - Prevents broken systems

2. **Keep Generations**
   - Don't delete recent generations
   - Test changes before cleanup
   - Easy rollback available

3. **Backup Important Files**
   - Configuration.nix
   - Custom modules
   - User data

### Power User Features

1. **Command Palette**
   - Press `Ctrl+Shift+P`
   - Type command name
   - Quick access to any feature

2. **Configuration Snippets**
   - Save frequently used configs
   - Insert with autocomplete
   - Share with others

3. **Bulk Operations**
   - Multi-select packages
   - Batch service management
   - Mass user updates

4. **Export/Import**
   - Export configuration
   - Share with other systems
   - Version control friendly

### Troubleshooting

1. **If GUI Won't Load**
   - Check service: `systemctl status nixos-gui`
   - Verify port: `ss -tlnp | grep 8080`
   - Check logs: `journalctl -u nixos-gui`

2. **If Changes Don't Apply**
   - Check for syntax errors
   - Verify disk space
   - Look for conflicting options

3. **If System Breaks**
   - Boot previous generation
   - Access GUI in safe mode
   - Restore from backup

## Getting Help

### In-App Help
- Press `F1` anywhere
- Hover over `?` icons
- Check tooltips

### Resources
- [Documentation](https://nixos-gui.org/docs)
- [Community Forum](https://discourse.nixos.org)
- [Issue Tracker](https://github.com/nixos/nixos-gui/issues)
- [Chat Support](https://matrix.to/#/#nixos-gui:matrix.org)

Remember: NixOS GUI is designed to make system management easier, but understanding NixOS concepts will help you use it more effectively. Don't hesitate to explore and experiment - you can always roll back!