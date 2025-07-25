# NixOS GUI Troubleshooting Guide

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Common Issues](#common-issues)
3. [Service Problems](#service-problems)
4. [Authentication Issues](#authentication-issues)
5. [Network & Connection Issues](#network--connection-issues)
6. [Package Management Issues](#package-management-issues)
7. [Configuration Issues](#configuration-issues)
8. [Performance Issues](#performance-issues)
9. [Helper Service Issues](#helper-service-issues)
10. [Advanced Debugging](#advanced-debugging)

## Quick Diagnostics

Run this diagnostic script to check common issues:

```bash
#!/bin/bash
echo "=== NixOS GUI Diagnostics ==="

# Check service status
echo -e "\n[Service Status]"
systemctl is-active nixos-gui && echo "✓ Web service is running" || echo "✗ Web service is not running"
systemctl is-active nixos-gui-helper && echo "✓ Helper service is running" || echo "✗ Helper service is not running"

# Check ports
echo -e "\n[Port Status]"
ss -tlnp 2>/dev/null | grep -q ":8080" && echo "✓ Port 8080 is listening" || echo "✗ Port 8080 is not listening"
ss -tlnp 2>/dev/null | grep -q ":8081" && echo "✓ Port 8081 is listening" || echo "✗ Port 8081 is not listening"

# Check permissions
echo -e "\n[Permissions]"
[ -S /run/nixos-gui/helper.sock ] && echo "✓ Helper socket exists" || echo "✗ Helper socket missing"
groups | grep -q "nixos-gui" && echo "✓ User in nixos-gui group" || echo "✗ User not in nixos-gui group"

# Check disk space
echo -e "\n[Disk Space]"
df -h / | awk 'NR==2 {print "Root filesystem:", $4, "free"}'
df -h /nix | awk 'NR==2 {print "Nix store:", $4, "free"}'

# Recent errors
echo -e "\n[Recent Errors]"
journalctl -u nixos-gui -p err -n 5 --no-pager
```

Save as `nixos-gui-diagnose.sh` and run with `bash nixos-gui-diagnose.sh`.

## Common Issues

### Service Won't Start

**Symptoms:**
- Cannot access web interface
- `systemctl status nixos-gui` shows failed

**Solutions:**

1. **Check logs for specific error:**
   ```bash
   journalctl -u nixos-gui -e --no-pager
   ```

2. **Port already in use:**
   ```bash
   # Find what's using the port
   sudo lsof -i :8080
   
   # Solution: Change port in configuration
   services.nixos-gui.port = 8090;
   ```

3. **Missing dependencies:**
   ```bash
   # Rebuild with trace
   sudo nixos-rebuild switch --show-trace
   ```

4. **Permission errors:**
   ```bash
   # Fix ownership
   sudo chown -R nixos-gui:nixos-gui /var/lib/nixos-gui
   sudo chmod 750 /var/lib/nixos-gui
   ```

### Cannot Access Web Interface

**Symptoms:**
- Service is running but browser shows error
- "Connection refused" or timeout

**Solutions:**

1. **Check binding address:**
   ```nix
   # For local access only (default)
   services.nixos-gui.host = "127.0.0.1";
   
   # For network access
   services.nixos-gui.host = "0.0.0.0";
   ```

2. **Firewall blocking:**
   ```nix
   # Open firewall
   services.nixos-gui.openFirewall = true;
   
   # Or manually
   networking.firewall.allowedTCPPorts = [ 8080 8081 ];
   ```

3. **SELinux/AppArmor:**
   ```bash
   # Check SELinux
   getenforce
   
   # Temporarily disable to test
   sudo setenforce 0
   ```

### Page Loads But Shows Errors

**Symptoms:**
- Interface loads but features don't work
- JavaScript errors in console

**Solutions:**

1. **Clear browser cache:**
   - Hard refresh: Ctrl+Shift+R (Cmd+Shift+R on Mac)
   - Clear site data in browser settings

2. **Check WebSocket connection:**
   - Open browser console (F12)
   - Look for WebSocket errors
   - Verify port 8081 is accessible

3. **Verify API connectivity:**
   ```bash
   # Test API endpoint
   curl http://localhost:8080/api/health
   ```

## Service Problems

### Helper Service Fails

**Symptoms:**
- Operations fail with "Helper not available"
- `systemctl status nixos-gui-helper` shows failed

**Solutions:**

1. **Check helper logs:**
   ```bash
   journalctl -u nixos-gui-helper -e
   ```

2. **Rebuild helper:**
   ```bash
   cd /var/lib/nixos-gui
   sudo -u nixos-gui make -C helper clean
   sudo -u nixos-gui make -C helper
   ```

3. **Check socket permissions:**
   ```bash
   ls -la /run/nixos-gui/helper.sock
   # Should be: srw-rw---- nixos-gui nixos-gui
   ```

4. **Polkit configuration:**
   ```bash
   # Verify polkit rules
   cat /etc/polkit-1/rules.d/nixos-gui.rules
   
   # Test polkit auth
   pkcheck --action-id org.nixos.gui.manage --process $$
   ```

### Operations Timeout

**Symptoms:**
- Package installations hang
- Service operations timeout
- No progress updates

**Solutions:**

1. **Increase timeout:**
   ```nix
   services.nixos-gui.timeouts = {
     operation = 300;  # 5 minutes
     build = 3600;     # 1 hour
   };
   ```

2. **Check system resources:**
   ```bash
   # CPU and memory
   htop
   
   # Disk I/O
   iotop
   
   # Network
   iftop
   ```

3. **Clear Nix locks:**
   ```bash
   # Remove stale locks
   sudo rm -f /nix/var/nix/db/db.lock
   sudo rm -f /nix/var/nix/profiles/per-user/*/profile.lock
   ```

## Authentication Issues

### Cannot Login

**Symptoms:**
- "Invalid credentials" error
- Login page refreshes without error

**Solutions:**

1. **Verify credentials:**
   ```bash
   # Test system authentication
   su - yourusername
   ```

2. **Check PAM configuration:**
   ```bash
   # Verify PAM service exists
   cat /etc/pam.d/nixos-gui
   
   # Test PAM authentication
   pamtester nixos-gui yourusername authenticate
   ```

3. **User not in allowed groups:**
   ```bash
   # Check current groups
   groups yourusername
   
   # Add to nixos-gui group
   sudo usermod -a -G nixos-gui yourusername
   
   # Logout and login for changes to take effect
   ```

4. **Session issues:**
   ```bash
   # Clear session data
   sudo rm -rf /var/lib/nixos-gui/sessions/*
   sudo systemctl restart nixos-gui
   ```

### Token Expired Errors

**Symptoms:**
- Frequent logouts
- "Token expired" messages

**Solutions:**

1. **Extend token lifetime:**
   ```nix
   services.nixos-gui.auth = {
     tokenExpiry = "30m";      # Access token
     refreshExpiry = "7d";     # Refresh token
   };
   ```

2. **Check system time:**
   ```bash
   # Verify time is correct
   date
   
   # Sync time
   sudo systemctl restart systemd-timesyncd
   ```

3. **Clear browser cookies:**
   - Delete cookies for the site
   - Try incognito/private mode

### Permission Denied

**Symptoms:**
- Can login but operations fail
- "Insufficient permissions" errors

**Solutions:**

1. **Check group membership:**
   ```bash
   # For admin operations, need wheel group
   sudo usermod -a -G wheel yourusername
   ```

2. **Verify feature permissions:**
   ```nix
   # Check enabled features
   services.nixos-gui.features = {
     packageManagement = true;
     serviceManagement = true;
     configurationEdit = true;
     systemRebuild = true;
   };
   ```

3. **Polkit debugging:**
   ```bash
   # Enable polkit debugging
   sudo POLKIT_DEBUG=1 journalctl -u polkit -f
   ```

## Network & Connection Issues

### WebSocket Disconnections

**Symptoms:**
- Real-time updates stop working
- "Connection lost" messages
- Progress bars freeze

**Solutions:**

1. **Adjust WebSocket settings:**
   ```nix
   services.nixos-gui.websocket = {
     pingInterval = 30000;     # 30 seconds
     pingTimeout = 60000;      # 60 seconds
     reconnectDelay = 1000;    # 1 second
     maxReconnectAttempts = 10;
   };
   ```

2. **Proxy/firewall issues:**
   ```nginx
   # If using nginx proxy
   location /ws {
     proxy_pass http://localhost:8081;
     proxy_http_version 1.1;
     proxy_set_header Upgrade $http_upgrade;
     proxy_set_header Connection "upgrade";
     proxy_set_header Host $host;
     proxy_read_timeout 86400;
   }
   ```

3. **Browser issues:**
   - Disable browser extensions
   - Try different browser
   - Check browser console for errors

### Slow Response Times

**Symptoms:**
- Interface feels sluggish
- Long delays for operations
- Timeouts

**Solutions:**

1. **Enable compression:**
   ```nix
   services.nixos-gui.compression = true;
   ```

2. **Check network latency:**
   ```bash
   # If accessing remotely
   ping server-ip
   traceroute server-ip
   ```

3. **Optimize database:**
   ```bash
   # Vacuum SQLite database
   sudo -u nixos-gui sqlite3 /var/lib/nixos-gui/db.sqlite "VACUUM;"
   ```

## Package Management Issues

### Package Search Not Working

**Symptoms:**
- No search results
- Search takes forever
- Errors when searching

**Solutions:**

1. **Update package cache:**
   ```bash
   # Update channels
   sudo nix-channel --update
   
   # Rebuild package cache
   sudo rm -rf /var/lib/nixos-gui/package-cache
   sudo systemctl restart nixos-gui
   ```

2. **Check channel configuration:**
   ```bash
   # List channels
   sudo nix-channel --list
   
   # Add nixpkgs if missing
   sudo nix-channel --add https://nixos.org/channels/nixos-23.11 nixpkgs
   ```

3. **Memory issues with large queries:**
   ```nix
   services.nixos-gui.limits = {
     maxSearchResults = 100;   # Limit results
     searchTimeout = 30;       # 30 seconds
   };
   ```

### Package Installation Fails

**Symptoms:**
- Build errors
- "No space left" errors  
- Dependency conflicts

**Solutions:**

1. **Check disk space:**
   ```bash
   df -h /nix/store
   
   # Clean up if needed
   sudo nix-collect-garbage -d
   ```

2. **Resolve conflicts:**
   ```bash
   # Check for conflicts
   nix-env -qa | grep package-name
   
   # Force installation
   nix-env -iA nixpkgs.package-name
   ```

3. **Build failures:**
   ```bash
   # Try building manually
   nix-build '<nixpkgs>' -A package-name
   
   # Check build logs
   nix log /nix/store/hash-package-name.drv
   ```

## Configuration Issues

### Cannot Save Configuration

**Symptoms:**
- Save button doesn't work
- "Permission denied" when saving
- Changes lost after save

**Solutions:**

1. **Check file permissions:**
   ```bash
   ls -la /etc/nixos/configuration.nix
   # Should be writable by root or wheel group
   ```

2. **Backup directory issues:**
   ```bash
   # Ensure backup directory exists
   sudo mkdir -p /var/lib/nixos-gui/backups
   sudo chown nixos-gui:nixos-gui /var/lib/nixos-gui/backups
   ```

3. **Syntax validation:**
   ```bash
   # Validate manually
   nix-instantiate --parse /etc/nixos/configuration.nix
   ```

### Rebuild Failures

**Symptoms:**
- Rebuild hangs or fails
- No error messages
- System in inconsistent state

**Solutions:**

1. **Check build logs:**
   ```bash
   # View detailed logs
   sudo nixos-rebuild switch --show-trace
   ```

2. **Out of memory:**
   ```nix
   # Limit build jobs
   nix.settings = {
     max-jobs = 2;
     cores = 2;
   };
   ```

3. **Rollback if needed:**
   ```bash
   # List generations
   sudo nix-env --list-generations -p /nix/var/nix/profiles/system
   
   # Rollback
   sudo nixos-rebuild switch --rollback
   ```

## Performance Issues

### High CPU Usage

**Symptoms:**
- System becomes unresponsive
- Fan noise increases
- Slow interface

**Solutions:**

1. **Limit concurrent operations:**
   ```nix
   services.nixos-gui.limits = {
     maxConcurrentJobs = 2;
     maxConcurrentBuilds = 1;
   };
   ```

2. **Check for runaway processes:**
   ```bash
   # Find high CPU processes
   top -u nixos-gui
   
   # Kill if necessary
   sudo systemctl restart nixos-gui
   ```

3. **Disable unnecessary features:**
   ```nix
   services.nixos-gui.features = {
     realtimeMetrics = false;
     autoRefresh = false;
   };
   ```

### High Memory Usage

**Symptoms:**
- Out of memory errors
- System swapping
- Slow performance

**Solutions:**

1. **Limit memory usage:**
   ```nix
   systemd.services.nixos-gui = {
     serviceConfig = {
       MemoryMax = "1G";
       MemoryHigh = "750M";
     };
   };
   ```

2. **Reduce cache sizes:**
   ```nix
   services.nixos-gui.cache = {
     packageCacheSize = 1000;  # Entries
     sessionTimeout = "1h";
   };
   ```

3. **Check for memory leaks:**
   ```bash
   # Monitor memory over time
   sudo journalctl -u nixos-gui -f | grep memory
   ```

## Helper Service Issues

### Helper Not Responding

**Symptoms:**
- "Helper service unavailable"
- Operations hang indefinitely

**Solutions:**

1. **Restart helper:**
   ```bash
   sudo systemctl restart nixos-gui-helper
   ```

2. **Check IPC socket:**
   ```bash
   # Socket should exist
   ls -la /run/nixos-gui/helper.sock
   
   # Test socket
   echo "PING" | sudo -u nixos-gui socat - UNIX-CONNECT:/run/nixos-gui/helper.sock
   ```

3. **Rebuild helper:**
   ```bash
   cd /path/to/nixos-gui
   make -C helper clean
   make -C helper
   sudo make -C helper install
   ```

### Polkit Authorization Failed

**Symptoms:**
- "Not authorized" errors
- Password prompts that always fail

**Solutions:**

1. **Check polkit rules:**
   ```bash
   # List rules
   ls -la /etc/polkit-1/rules.d/
   
   # Verify nixos-gui rules
   cat /etc/polkit-1/rules.d/10-nixos-gui.rules
   ```

2. **Test polkit manually:**
   ```bash
   # Test as your user
   pkexec --user root /bin/echo "Polkit works"
   ```

3. **Add polkit rule:**
   ```javascript
   // /etc/polkit-1/rules.d/10-nixos-gui.rules
   polkit.addRule(function(action, subject) {
     if (action.id.indexOf("org.nixos.gui.") == 0) {
       if (subject.isInGroup("wheel") || subject.isInGroup("nixos-gui")) {
         return polkit.Result.YES;
       }
     }
   });
   ```

## Advanced Debugging

### Enable Debug Logging

```nix
services.nixos-gui = {
  logLevel = "debug";
  debug = {
    api = true;
    websocket = true;
    helper = true;
    auth = true;
  };
};
```

### Trace Specific Operations

```bash
# Trace package operations
NIXOS_GUI_TRACE=packages sudo -u nixos-gui node /var/lib/nixos-gui/server.js

# Trace all
NIXOS_GUI_TRACE=* sudo -u nixos-gui node /var/lib/nixos-gui/server.js
```

### Manual Testing

```bash
# Test API endpoints
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'

# Test WebSocket
websocat ws://localhost:8081/ws

# Test helper
echo '{"action":"ping"}' | sudo -u nixos-gui /var/lib/nixos-gui/helper/nixos-gui-helper
```

### Core Dumps

```bash
# Enable core dumps
ulimit -c unlimited

# Run with core dumps
sudo -u nixos-gui GOTRACEBACK=crash /var/lib/nixos-gui/server

# Analyze core dump
gdb /var/lib/nixos-gui/helper/nixos-gui-helper core
```

### Strace Analysis

```bash
# Trace system calls
sudo strace -f -p $(pgrep nixos-gui)

# Trace specific calls
sudo strace -e open,stat -p $(pgrep nixos-gui)
```

## Getting Further Help

If these solutions don't resolve your issue:

1. **Collect debugging information:**
   ```bash
   nixos-gui-debug-report > debug-report.txt
   ```

2. **Check for known issues:**
   - [GitHub Issues](https://github.com/nixos/nixos-gui/issues)
   - [NixOS Discourse](https://discourse.nixos.org)

3. **Create detailed bug report:**
   - NixOS version
   - NixOS GUI version
   - Error messages
   - Steps to reproduce
   - Debug logs

4. **Get help:**
   - GitHub Issues (for bugs)
   - Matrix chat (for quick help)
   - NixOS Discourse (for discussions)

Remember: Most issues have simple solutions. Check the basics first!