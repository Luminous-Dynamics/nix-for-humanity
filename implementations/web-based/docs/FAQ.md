# NixOS GUI Frequently Asked Questions

## Table of Contents

1. [General Questions](#general-questions)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Security](#security)
5. [Troubleshooting](#troubleshooting)
6. [Development](#development)

## General Questions

### What is NixOS GUI?

NixOS GUI is a web-based graphical interface for managing NixOS systems. It provides an intuitive way to:
- Install and remove packages
- Manage system services
- Edit system configuration
- Perform system updates and rollbacks
- Monitor system health

### Why use NixOS GUI instead of the command line?

While the command line is powerful, NixOS GUI offers:
- **Visual feedback**: See package descriptions, service states, and system status at a glance
- **Safety features**: Validation, confirmation dialogs, and easy rollback
- **Discoverability**: Browse available packages and options without memorizing commands
- **Multi-tasking**: Perform multiple operations with progress tracking
- **Accessibility**: Lower barrier to entry for new NixOS users

### Is NixOS GUI a replacement for configuration.nix?

No! NixOS GUI works *with* your configuration.nix file. It:
- Provides a visual editor with syntax highlighting
- Validates changes before applying
- Creates backups automatically
- Shows diffs before rebuilding
- Preserves the declarative nature of NixOS

### What versions of NixOS are supported?

NixOS GUI supports:
- NixOS 23.11 (stable)
- NixOS 24.05 (upcoming)
- NixOS unstable (with caveats)

Older versions may work but are not officially supported.

### Is NixOS GUI official?

NixOS GUI is a community project, not an official NixOS project. However, it follows NixOS best practices and integrates seamlessly with the NixOS ecosystem.

## Installation

### How do I install NixOS GUI?

The easiest way is using flakes:

```nix
# In your flake.nix
{
  inputs.nixos-gui.url = "github:nixos/nixos-gui";
  
  outputs = { self, nixpkgs, nixos-gui, ... }: {
    nixosConfigurations.yourhostname = nixpkgs.lib.nixosSystem {
      modules = [
        nixos-gui.nixosModules.default
        {
          services.nixos-gui.enable = true;
        }
      ];
    };
  };
}
```

Then rebuild: `sudo nixos-rebuild switch`

### Can I install it without flakes?

Yes! See the [Installation Guide](INSTALLATION.md#traditional-installation) for non-flakes installation.

### Do I need to open firewall ports?

By default, NixOS GUI only listens on localhost (127.0.0.1). If you want network access:

```nix
services.nixos-gui = {
  host = "0.0.0.0";  # Listen on all interfaces
  openFirewall = true;  # Opens ports 8080 and 8081
};
```

### Can I use a custom port?

Yes:

```nix
services.nixos-gui = {
  port = 9090;      # Web interface port
  wsPort = 9091;    # WebSocket port
};
```

### How do I enable HTTPS?

For production use, enable HTTPS:

```nix
services.nixos-gui = {
  ssl = {
    enable = true;
    cert = "/path/to/cert.pem";
    key = "/path/to/key.pem";
  };
};
```

Or use a reverse proxy like nginx with Let's Encrypt.

## Usage

### How do I access NixOS GUI?

After installation, open your browser and navigate to:
- Local access: http://localhost:8080
- Network access: http://your-server-ip:8080
- HTTPS: https://your-server:8080

### What credentials do I use?

NixOS GUI uses your system credentials. Login with:
- Username: Your NixOS username
- Password: Your system password

The user must be in the `wheel` or `nixos-gui` group.

### How do I search for packages?

1. Go to the Packages tab
2. Type in the search box
3. Results appear as you type
4. Click "Install" on any package

Or use the quick action bar: Press `/` and type "install firefox"

### Can I install multiple packages at once?

Yes! Select multiple packages with checkboxes, then click "Install Selected".

### How do I edit configuration.nix?

1. Go to the Configuration tab
2. The editor loads your `/etc/nixos/configuration.nix`
3. Make changes (with syntax highlighting)
4. Click "Validate" to check syntax
5. Click "Save" to write changes
6. Click "Rebuild" to apply

### What's the difference between rebuild actions?

- **Switch**: Build and activate immediately (most common)
- **Boot**: Build and activate on next boot
- **Test**: Build and activate temporarily (revert on reboot)
- **Build**: Just build, don't activate
- **Dry Build**: Show what would be built without building

### How do I rollback to a previous configuration?

1. Go to System → Generations
2. Find the generation you want
3. Click "Rollback to this generation"
4. Confirm the action

### Can I schedule operations?

Not yet, but it's on the roadmap. For now, use systemd timers or cron.

### How do I monitor system resources?

The Dashboard shows:
- CPU usage
- Memory usage
- Disk usage
- Network activity
- Recent system events

### Is there a mobile app?

No native app, but the web interface is mobile-responsive. Add it to your home screen for an app-like experience.

## Security

### Is NixOS GUI secure?

Yes, with multiple security layers:
- PAM authentication
- JWT tokens with short expiration
- Polkit for privileged operations
- Audit logging
- Input validation
- CSRF protection

### Who can access NixOS GUI?

By default, users in these groups:
- `wheel` (administrators)
- `nixos-gui` (GUI users)

Configure with:
```nix
services.nixos-gui.allowedGroups = [ "wheel" "trusted-users" ];
```

### Are my credentials stored?

No, credentials are never stored. NixOS GUI uses:
- PAM for authentication (one-time check)
- JWT tokens for sessions (in memory)
- Refresh tokens (HTTPOnly cookies)

### What operations require sudo/root?

All system operations use Polkit for authorization. You may need to:
- Enter your password for certain operations
- Be in the `wheel` group for system changes

### Is there an audit trail?

Yes, all operations are logged:
- Who performed the action
- What was changed
- When it happened
- Result of the operation

View logs in System → Audit Log

### Can I restrict features?

Yes, disable features you don't need:

```nix
services.nixos-gui.features = {
  packageManagement = true;
  serviceManagement = true;
  configurationEdit = false;  # Disable config editing
  systemRebuild = false;      # Disable rebuilds
};
```

## Troubleshooting

### NixOS GUI won't start

Check the service status:
```bash
systemctl status nixos-gui
journalctl -u nixos-gui -e
```

Common issues:
- Port already in use
- Missing dependencies
- Permission errors

### I can't login

1. Verify your credentials work in terminal
2. Check you're in allowed groups: `groups yourusername`
3. Check PAM configuration: `cat /etc/pam.d/nixos-gui`
4. Review auth logs: `journalctl -u nixos-gui | grep auth`

### "Permission denied" errors

Ensure your user is in the correct group:
```bash
sudo usermod -a -G nixos-gui yourusername
# Then logout and login again
```

### Package installation fails

1. Check internet connection
2. Verify channel is up-to-date: `sudo nix-channel --update`
3. Check disk space: `df -h`
4. Review build logs in the GUI

### WebSocket connection keeps dropping

This might be due to:
- Firewall/proxy interference
- Browser extensions (try incognito mode)
- Network instability

Try:
```nix
services.nixos-gui.websocket.pingInterval = 30000;  # 30 seconds
```

### The interface is slow

1. Check system resources (CPU, memory)
2. Try a different browser
3. Disable browser extensions
4. Check network latency (if remote)

### Configuration changes aren't applying

1. Ensure you clicked "Save" before "Rebuild"
2. Check for syntax errors (red underlines)
3. Verify the file was written: `cat /etc/nixos/configuration.nix`
4. Check rebuild logs for errors

### How do I reset NixOS GUI?

To completely reset:
```bash
# Stop service
sudo systemctl stop nixos-gui

# Remove state
sudo rm -rf /var/lib/nixos-gui

# Restart
sudo systemctl start nixos-gui
```

## Development

### How can I contribute?

1. Check [open issues](https://github.com/nixos/nixos-gui/issues)
2. Read the [Development Guide](DEVELOPMENT.md)
3. Fork, develop, test, and submit a PR
4. Join our [chat](https://matrix.to/#/#nixos-gui:matrix.org)

### What technology stack is used?

- **Frontend**: React, Redux, TypeScript
- **Backend**: Node.js, Express.js
- **System Integration**: C helper with Polkit
- **Build System**: Nix, Webpack
- **Testing**: Jest, Playwright

### How do I run tests?

```bash
# All tests
npm test

# Specific test suites
npm run test:unit
npm run test:integration
npm run test:e2e
```

### Can I add custom features?

Yes! NixOS GUI is designed to be extensible:
1. Fork the project
2. Add your feature
3. Test thoroughly
4. Submit a PR

Or create a plugin (coming soon).

### Where do I report bugs?

1. Check existing issues first
2. Create a [new issue](https://github.com/nixos/nixos-gui/issues/new)
3. Include:
   - NixOS version
   - Error messages
   - Steps to reproduce
   - Screenshots if applicable

### How do I get help?

- **Documentation**: Start with our comprehensive docs
- **GitHub Issues**: For bugs and feature requests  
- **Discussion Forum**: [discourse.nixos.org](https://discourse.nixos.org)
- **Real-time Chat**: [Matrix](https://matrix.to/#/#nixos-gui:matrix.org)
- **Stack Overflow**: Tag with `nixos-gui`

### Is there a roadmap?

Yes! See our [GitHub Project Board](https://github.com/nixos/nixos-gui/projects) for planned features:
- Plugin system
- Multi-system management
- Scheduled operations
- Mobile app
- Declarative GUI configuration

## Still Have Questions?

If your question isn't answered here:

1. Check the full documentation
2. Search existing GitHub issues
3. Ask on the forum or chat
4. Create a new issue with the "question" label

We're here to help! 🚀