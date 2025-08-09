# 🎯 Nix for Humanity - Command Quick Reference

## ✅ Currently Implemented (v0.5.5)

### 📦 Package Management
- `install [package]` - Install software
- `remove [package]` - Uninstall software  
- `search [query]` - Find packages
- `list installed` - Show installed packages

### 🔧 System Maintenance
- `update system` - Update everything
- `garbage collect` - Free disk space
- `list generations` - Show system snapshots
- `switch generation [n]` - Restore previous state
- `rollback` - Go to previous generation
- `rebuild` - Apply configuration changes

### ⚙️ Configuration
- `edit config` - Open configuration.nix
- `show config` - Display configuration
- `configure [service]` - Service setup help

### ℹ️ Information
- `check status` - System health check
- `explain [topic]` - Learn NixOS concepts
- `help` - Show available commands

### 🌐 Network Management ✨ NEW!
- `show network` - Network status
- `show ip` - Display IP addresses
- `connect wifi [SSID]` - WiFi setup
- `list wifi` - Scan networks
- `test internet` - Connectivity check

### ⚡ Service Management ✨ NEW!
- `start [service]` - Start service
- `stop [service]` - Stop service
- `restart [service]` - Restart service
- `service status [name]` - Check status
- `list services` - All services
- `enable [service]` - Auto-start on boot
- `disable [service]` - Don't auto-start
- `show logs [service]` - Service logs

### 👤 User Management ✨ NEW!
- `create user [name]` - Add user
- `list users` - Show users
- `add [user] to [group]` - Groups
- `change password` - Update password
- `grant sudo [user]` - Admin access

### 💾 Storage Management ✨ NEW!
- `disk usage` - Storage info
- `analyze disk` - What's using space
- `mount [device]` - Mount drives
- `unmount [device]` - Unmount safely
- `find large files` - Space hogs

---

## 🚀 Next to Implement (Phase 2)

---

## 🔮 Future Commands (Phase 2+)

### 🔒 Security
- `check updates` - Security updates
- `configure ssh` - SSH setup
- `generate ssh key` - Create keys
- `configure firewall` - Firewall rules

### 🖥️ Hardware
- `show hardware` - System info
- `configure audio` - Sound setup
- `manage bluetooth` - Bluetooth
- `battery status` - Power info

### 📦 Advanced Packages
- `pin package` - Prevent updates
- `package info [name]` - Details
- `show dependencies` - Dep tree
- `use unstable` - Mix channels

### 🐳 Containers
- `setup docker` - Docker config
- `manage containers` - Container ops
- `setup podman` - Alternative

---

## 💡 Usage Examples

### Current Commands
```bash
ask-nix "install firefox"
ask-nix "my system is running out of space"  # → suggests garbage collect
ask-nix "show me previous versions"          # → list generations
ask-nix "help me edit my configuration"     # → edit config
```

### Upcoming Commands (Phase 1)
```bash
ask-nix "what's my ip address"              # → show ip
ask-nix "connect to MyWiFi network"         # → connect wifi MyWiFi
ask-nix "is nginx running?"                 # → service status nginx
ask-nix "restart the web server"            # → restart nginx
ask-nix "add john as a user"               # → create user john
ask-nix "how much disk space do I have?"   # → disk usage
```

### Smart Context (Future)
```bash
ask-nix "stop nginx"
ask-nix "actually restart it instead"       # → understands "it" = nginx
ask-nix "show its logs"                     # → show logs nginx
```

---

## 📈 Progress Tracker

| Category | Implemented | Planned | Total |
|----------|------------|---------|-------|
| Package Management | 4 | 6 | 10 |
| System Maintenance | 6 | 4 | 10 |
| Network | 5 | 3 | 8 |
| Services | 8 | 1 | 9 |
| Users | 5 | 3 | 8 |
| Storage | 5 | 5 | 10 |
| Configuration | 3 | 2 | 5 |
| **TOTAL** | **36** | **24** | **60** |

**Current Coverage**: 60% of planned commands implemented! 🎉

---

*Quick tip: Focus on the commands that users ask about most often in NixOS forums and chat rooms!*