# 🚨 NixOS GUI - Emergency Procedures

**THIS DOCUMENT CONTAINS CRITICAL PROCEDURES FOR EMERGENCY SITUATIONS**

## 🔥 Critical Incidents

### 1. Complete Service Failure

**Symptoms**: GUI completely inaccessible, all health checks failing

**IMMEDIATE ACTIONS**:

```bash
# 1. VERIFY THE ISSUE
curl -I http://localhost:8080 || echo "SERVICE DOWN"
systemctl is-active nixos-gui || echo "SERVICE INACTIVE"

# 2. ATTEMPT QUICK RECOVERY
sudo systemctl restart nixos-gui

# 3. IF STILL DOWN - CHECK BASICS
# Port conflict?
sudo lsof -i :8080
# Disk full?
df -h /
# Out of memory?
free -h

# 4. EMERGENCY ROLLBACK
sudo nixos-rebuild switch --rollback

# 5. START IN SAFE MODE
sudo -u nixos-gui NODE_ENV=safe nixos-gui --port 8081
```

### 2. Security Breach Detected

**Symptoms**: Unauthorized access, suspicious activity in logs

**IMMEDIATE ACTIONS**:

```bash
# 1. ISOLATE THE SYSTEM
# Block all external access
sudo iptables -I INPUT -p tcp --dport 8080 -j DROP
sudo iptables -I INPUT -p tcp --dport 443 -j DROP

# 2. PRESERVE EVIDENCE
# Snapshot logs
tar -czf /tmp/incident-$(date +%Y%m%d-%H%M%S).tar.gz /var/log/nixos-gui/

# 3. STOP THE SERVICE
sudo systemctl stop nixos-gui

# 4. REVOKE ALL SESSIONS
redis-cli --scan --pattern "session:*" | xargs redis-cli DEL

# 5. ROTATE SECRETS
export NEW_JWT_SECRET=$(openssl rand -hex 64)
export NEW_SESSION_SECRET=$(openssl rand -hex 64)

# 6. RESTART WITH NEW SECRETS
sudo systemctl start nixos-gui
```

### 3. Data Corruption

**Symptoms**: Errors about corrupted database, inconsistent state

**IMMEDIATE ACTIONS**:

```bash
# 1. STOP SERVICE TO PREVENT FURTHER DAMAGE
sudo systemctl stop nixos-gui

# 2. BACKUP CORRUPTED DATA (for investigation)
cp /var/lib/nixos-gui/db.sqlite /tmp/corrupted-db-$(date +%Y%m%d).sqlite

# 3. ATTEMPT RECOVERY
sqlite3 /var/lib/nixos-gui/db.sqlite "PRAGMA integrity_check;"

# 4. IF CORRUPTED - RESTORE FROM BACKUP
# Find latest backup
LATEST_BACKUP=$(ls -t /backup/nixos-gui/*/db.sqlite | head -1)
cp "$LATEST_BACKUP" /var/lib/nixos-gui/db.sqlite

# 5. VERIFY AND RESTART
sqlite3 /var/lib/nixos-gui/db.sqlite "PRAGMA integrity_check;"
sudo systemctl start nixos-gui
```

### 4. Runaway Resource Usage

**Symptoms**: CPU 100%, Memory exhausted, System unresponsive

**IMMEDIATE ACTIONS**:

```bash
# 1. IDENTIFY THE CULPRIT
top -b -n 1 | grep nixos-gui

# 2. EMERGENCY KILL IF NECESSARY
sudo kill -TERM $(pgrep -f nixos-gui)
# If not responding:
sudo kill -KILL $(pgrep -f nixos-gui)

# 3. CLEAR CACHE AND TEMP FILES
redis-cli FLUSHALL
rm -rf /tmp/nixos-gui-*

# 4. START WITH RESOURCE LIMITS
cat > /etc/systemd/system/nixos-gui.service.d/limits.conf <<EOF
[Service]
CPUQuota=50%
MemoryMax=1G
EOF

# 5. RESTART SERVICE
sudo systemctl daemon-reload
sudo systemctl start nixos-gui
```

## 🔧 Recovery Procedures

### Quick Diagnostics Script

```bash
#!/bin/bash
# emergency-diagnostics.sh

echo "=== NixOS GUI Emergency Diagnostics ==="
echo "Time: $(date)"
echo

echo "1. Service Status:"
systemctl status nixos-gui --no-pager || echo "FAILED"

echo -e "\n2. Port Status:"
lsof -i :8080 || echo "Port not in use"

echo -e "\n3. Recent Errors:"
journalctl -u nixos-gui --since "10 minutes ago" | grep -i error | tail -5

echo -e "\n4. Disk Space:"
df -h / /var/lib/nixos-gui

echo -e "\n5. Memory Status:"
free -h

echo -e "\n6. Database Status:"
sqlite3 /var/lib/nixos-gui/db.sqlite "PRAGMA integrity_check;" || echo "DB CHECK FAILED"

echo -e "\n7. Network Connectivity:"
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/api/health || echo "UNREACHABLE"

echo -e "\n=== End Diagnostics ==="
```

### Safe Mode Startup

```bash
#!/bin/bash
# start-safe-mode.sh

# Disable all plugins
mkdir -p /var/lib/nixos-gui/plugins.disabled
mv /var/lib/nixos-gui/plugins/* /var/lib/nixos-gui/plugins.disabled/ 2>/dev/null

# Start with minimal config
cat > /tmp/nixos-gui-safe.json <<EOF
{
  "port": 8081,
  "workers": 1,
  "cache": {
    "type": "memory",
    "maxSize": "100MB"
  },
  "plugins": {
    "enabled": false
  },
  "rateLimit": {
    "max": 10,
    "window": "1m"
  }
}
EOF

# Start service in foreground
sudo -u nixos-gui NODE_ENV=production nixos-gui --config /tmp/nixos-gui-safe.json
```

## 📞 Emergency Contacts

### Escalation Chain

1. **Level 1 - On-Call Engineer**
   - Check PagerDuty
   - Response time: 15 minutes

2. **Level 2 - Team Lead**
   - Phone: [REDACTED]
   - Response time: 30 minutes

3. **Level 3 - Security Team**
   - Email: security@nixos-gui.org
   - Phone: [REDACTED]
   - For: Security breaches only

4. **Level 4 - Executive**
   - Phone: [REDACTED]
   - For: Major outages > 2 hours

### External Support

- **NixOS Support**: https://nixos.org/community
- **Node.js Security**: security@nodejs.org
- **Database Corruption**: PostgreSQL IRC #postgresql

## 🔄 Rollback Procedures

### Application Rollback

```bash
# 1. List available versions
ls -la /nix/store/*nixos-gui*/bin/nixos-gui

# 2. Quick rollback to previous
sudo nixos-rebuild switch --rollback

# 3. Rollback to specific generation
sudo nixos-rebuild switch --generation 42
```

### Database Rollback

```bash
# 1. Stop service
sudo systemctl stop nixos-gui

# 2. List backups
ls -t /backup/nixos-gui/*/db.sqlite

# 3. Restore specific backup
cp /backup/nixos-gui/20240120_020000/db.sqlite /var/lib/nixos-gui/db.sqlite

# 4. Fix permissions
chown nixos-gui:nixos-gui /var/lib/nixos-gui/db.sqlite

# 5. Restart
sudo systemctl start nixos-gui
```

## 🛡️ Preventive Measures

### Health Check Cron

```bash
# Add to root crontab
*/5 * * * * /usr/local/bin/nixos-gui-health-check.sh || /usr/local/bin/nixos-gui-alert.sh
```

### Auto-Recovery Script

```bash
#!/bin/bash
# /usr/local/bin/nixos-gui-auto-recovery.sh

MAX_ATTEMPTS=3
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
  if systemctl is-active nixos-gui >/dev/null; then
    exit 0
  fi
  
  echo "Attempt $((ATTEMPT+1)) to recover nixos-gui"
  systemctl restart nixos-gui
  sleep 30
  
  ATTEMPT=$((ATTEMPT+1))
done

# If we get here, manual intervention needed
echo "CRITICAL: nixos-gui failed to recover after $MAX_ATTEMPTS attempts" | \
  mail -s "NixOS GUI Critical Alert" oncall@nixos-gui.org
```

## 📊 Post-Incident

### Incident Report Template

```markdown
## Incident Report - [DATE]

### Summary
- **Duration**: [START] - [END]
- **Impact**: [Users affected, features impacted]
- **Severity**: [Critical/Major/Minor]

### Timeline
- [TIME]: Initial detection
- [TIME]: First response
- [TIME]: Root cause identified
- [TIME]: Fix implemented
- [TIME]: Service restored

### Root Cause
[Detailed explanation]

### Resolution
[Steps taken to resolve]

### Prevention
[Changes to prevent recurrence]

### Lessons Learned
[What went well, what didn't]
```

## ⚡ Quick Commands

```bash
# Emergency restart
sudo systemctl restart nixos-gui

# View real-time logs
journalctl -u nixos-gui -f

# Check service health
curl http://localhost:8080/api/health

# Emergency stop
sudo systemctl stop nixos-gui

# Start in debug mode
DEBUG=* nixos-gui

# Clear all caches
redis-cli FLUSHALL

# Backup database NOW
sqlite3 /var/lib/nixos-gui/db.sqlite ".backup /tmp/emergency-backup.sqlite"

# Check what's listening on port
lsof -i :8080

# Kill by port
fuser -k 8080/tcp

# System resource check
htop -p $(pgrep -d, -f nixos-gui)
```

---

**Remember**: 
1. Stay calm
2. Preserve evidence
3. Communicate status
4. Document everything
5. Learn from incidents

**When in doubt**: Rollback first, investigate later!