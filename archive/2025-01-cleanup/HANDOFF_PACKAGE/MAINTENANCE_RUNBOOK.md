# 🔧 NixOS GUI - Maintenance Runbook

This runbook provides step-by-step procedures for common maintenance tasks.

## 📋 Table of Contents

1. [Daily Operations](#daily-operations)
2. [Incident Response](#incident-response)
3. [Performance Issues](#performance-issues)
4. [Security Procedures](#security-procedures)
5. [Update Procedures](#update-procedures)
6. [Backup & Recovery](#backup--recovery)

## Daily Operations

### Morning Health Check (10 minutes)

```bash
#!/bin/bash
# morning-check.sh

echo "🌅 NixOS GUI Morning Health Check"
echo "================================="

# 1. Check service status
echo "1. Service Status:"
systemctl status nixos-gui --no-pager | grep "Active:"

# 2. Check error rate
echo -e "\n2. Recent Errors (last hour):"
journalctl -u nixos-gui --since "1 hour ago" | grep -c ERROR

# 3. Check disk space
echo -e "\n3. Disk Usage:"
df -h /var/lib/nixos-gui

# 4. Check memory usage
echo -e "\n4. Memory Usage:"
systemctl status nixos-gui --no-pager | grep "Memory:"

# 5. Check active sessions
echo -e "\n5. Active Sessions:"
curl -s http://localhost:8080/api/metrics | jq .activeSessions

# 6. Check response time
echo -e "\n6. API Response Time:"
time curl -s http://localhost:8080/api/health > /dev/null

echo -e "\n✅ Health check complete"
```

### Log Rotation Check

```bash
# Check log sizes
du -sh /var/log/nixos-gui/*

# Force rotation if needed
logrotate -f /etc/logrotate.d/nixos-gui

# Clean old logs (>30 days)
find /var/log/nixos-gui -name "*.log.*" -mtime +30 -delete
```

## Incident Response

### Service Down

**Symptoms**: GUI not accessible, 502 errors

**Response**:
```bash
# 1. Check service status
systemctl status nixos-gui

# 2. Check for port conflicts
lsof -i :8080

# 3. Review recent logs
journalctl -u nixos-gui -n 100 --no-pager

# 4. Restart service
sudo systemctl restart nixos-gui

# 5. If still failing, check configuration
nixos-gui --validate-config

# 6. Emergency rollback
sudo nixos-rebuild switch --rollback
```

### High CPU Usage

**Symptoms**: System slow, CPU > 80%

**Response**:
```bash
# 1. Identify process
top -p $(pgrep -f nixos-gui)

# 2. Check for infinite loops
strace -p $(pgrep -f nixos-gui) -c

# 3. Review slow queries
grep "SLOW QUERY" /var/log/nixos-gui/app.log

# 4. Check cache hit rate
curl http://localhost:8080/api/metrics | jq .cache

# 5. Restart with increased resources
systemctl edit nixos-gui
# Add: CPUQuota=200%

# 6. Enable profiling
NODE_ENV=production NODE_OPTIONS="--inspect" nixos-gui
```

### Memory Leak

**Symptoms**: Growing memory usage over time

**Response**:
```bash
# 1. Monitor memory growth
while true; do
  ps aux | grep nixos-gui | grep -v grep
  sleep 60
done

# 2. Generate heap dump
kill -USR2 $(pgrep -f nixos-gui)
# Dumps to /var/lib/nixos-gui/heap-*.heapsnapshot

# 3. Analyze with Chrome DevTools
# Copy heapsnapshot to local machine and analyze

# 4. Temporary fix - restart periodically
systemctl restart nixos-gui

# 5. Add memory limit
systemctl edit nixos-gui
# Add: MemoryMax=2G
```

## Performance Issues

### Slow Page Load

```bash
# 1. Check network latency
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8080

# 2. Verify static assets are cached
curl -I http://localhost:8080/static/app.js | grep Cache-Control

# 3. Check gzip compression
curl -H "Accept-Encoding: gzip" -I http://localhost:8080

# 4. Review bundle size
du -sh /var/lib/nixos-gui/static/*

# 5. Enable CDN (if available)
nixos-gui config set cdn.enable true
```

### Database Queries Slow

```bash
# 1. Check database size
sqlite3 /var/lib/nixos-gui/db.sqlite "SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size();"

# 2. Analyze queries
sqlite3 /var/lib/nixos-gui/db.sqlite "EXPLAIN QUERY PLAN SELECT * FROM packages WHERE name LIKE '%firefox%';"

# 3. Vacuum database
sqlite3 /var/lib/nixos-gui/db.sqlite "VACUUM;"

# 4. Rebuild indexes
sqlite3 /var/lib/nixos-gui/db.sqlite "REINDEX;"

# 5. Consider PostgreSQL migration for large deployments
```

## Security Procedures

### Security Scan

```bash
#!/bin/bash
# security-scan.sh

echo "🔒 Security Scan Starting..."

# 1. Check for vulnerable dependencies
npm audit --production

# 2. Scan for secrets
truffleHog --regex --entropy=True /var/lib/nixos-gui

# 3. Check file permissions
find /var/lib/nixos-gui -type f -perm 777

# 4. Review authentication logs
grep "AUTH" /var/log/nixos-gui/audit.log | tail -20

# 5. Check SSL configuration
nmap --script ssl-enum-ciphers -p 443 localhost

echo "✅ Security scan complete"
```

### Responding to Security Alert

1. **Assess Severity**
   ```bash
   # Check if actively exploited
   grep -i "exploit\|attack" /var/log/nixos-gui/audit.log
   ```

2. **Immediate Mitigation**
   ```bash
   # Block suspicious IPs
   iptables -A INPUT -s SUSPICIOUS_IP -j DROP
   
   # Disable affected feature
   nixos-gui config set features.FEATURE_NAME false
   ```

3. **Investigation**
   ```bash
   # Export audit logs
   journalctl -u nixos-gui --since "2 hours ago" > incident.log
   
   # Check for unauthorized changes
   git -C /etc/nixos status
   ```

4. **Remediation**
   ```bash
   # Update to patched version
   nix-channel --update
   sudo nixos-rebuild switch
   ```

## Update Procedures

### Minor Update (Patch)

```bash
# 1. Check current version
nixos-gui --version

# 2. Review changelog
curl https://api.github.com/repos/nixos/nixos-gui/releases/latest

# 3. Test in staging
nix-build -A nixos-gui

# 4. Update production
sudo nix-channel --update
sudo nixos-rebuild switch

# 5. Verify
nixos-gui --version
systemctl status nixos-gui
```

### Major Update

```bash
# 1. Full backup
/usr/local/bin/backup-nixos-gui.sh

# 2. Review breaking changes
cat CHANGELOG.md | grep BREAKING

# 3. Test migration
nixos-gui migrate --dry-run

# 4. Schedule maintenance window
echo "Maintenance: $(date -d '+2 days' '+%Y-%m-%d 02:00')"

# 5. Perform update
sudo nixos-rebuild switch

# 6. Run migration
nixos-gui migrate

# 7. Verify all features
nixos-gui test --comprehensive
```

## Backup & Recovery

### Automated Backup Script

```bash
#!/bin/bash
# /usr/local/bin/backup-nixos-gui.sh

BACKUP_DIR="/backup/nixos-gui"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR/$DATE"

# 1. Backup database
sqlite3 /var/lib/nixos-gui/db.sqlite ".backup $BACKUP_DIR/$DATE/db.sqlite"

# 2. Backup configuration
cp -r /etc/nixos "$BACKUP_DIR/$DATE/config"

# 3. Backup plugins
tar -czf "$BACKUP_DIR/$DATE/plugins.tar.gz" /var/lib/nixos-gui/plugins

# 4. Backup logs (last 7 days)
find /var/log/nixos-gui -mtime -7 -exec tar -rf "$BACKUP_DIR/$DATE/logs.tar" {} \;
gzip "$BACKUP_DIR/$DATE/logs.tar"

# 5. Create manifest
cat > "$BACKUP_DIR/$DATE/manifest.txt" <<EOF
Backup Date: $DATE
NixOS GUI Version: $(nixos-gui --version)
Database Size: $(du -h /var/lib/nixos-gui/db.sqlite | cut -f1)
Config Hash: $(sha256sum /etc/nixos/configuration.nix | cut -d' ' -f1)
EOF

# 6. Clean old backups (keep 30 days)
find "$BACKUP_DIR" -maxdepth 1 -type d -mtime +30 -exec rm -rf {} \;

echo "✅ Backup complete: $BACKUP_DIR/$DATE"
```

### Recovery Procedure

```bash
#!/bin/bash
# recover-nixos-gui.sh

BACKUP_PATH=$1

if [ -z "$BACKUP_PATH" ]; then
  echo "Usage: $0 /path/to/backup"
  exit 1
fi

# 1. Stop service
sudo systemctl stop nixos-gui

# 2. Restore database
cp "$BACKUP_PATH/db.sqlite" /var/lib/nixos-gui/db.sqlite
chown nixos-gui:nixos-gui /var/lib/nixos-gui/db.sqlite

# 3. Restore plugins
tar -xzf "$BACKUP_PATH/plugins.tar.gz" -C /

# 4. Restore configuration
cp -r "$BACKUP_PATH/config/"* /etc/nixos/

# 5. Rebuild system
sudo nixos-rebuild switch

# 6. Start service
sudo systemctl start nixos-gui

# 7. Verify
systemctl status nixos-gui
curl http://localhost:8080/api/health
```

## Monitoring Commands

### Real-time Monitoring

```bash
# Watch active connections
watch -n 1 'ss -tunap | grep :8080'

# Monitor API calls
tail -f /var/log/nixos-gui/access.log | grep "/api/"

# Track memory usage
watch -n 5 'ps aux | grep nixos-gui | grep -v grep'

# Monitor error rate
watch -n 10 'journalctl -u nixos-gui --since "1 minute ago" | grep -c ERROR'
```

### Performance Metrics

```bash
# Generate performance report
cat > perf-report.sh <<'EOF'
#!/bin/bash
echo "NixOS GUI Performance Report - $(date)"
echo "====================================="
echo
echo "Response Times (last hour):"
grep "response_time" /var/log/nixos-gui/metrics.log | \
  awk '{sum+=$2; count++} END {print "Average:", sum/count, "ms"}'
echo
echo "Cache Hit Rate:"
curl -s http://localhost:8080/api/metrics | jq .cache.hitRate
echo
echo "Active Sessions:"
curl -s http://localhost:8080/api/metrics | jq .sessions.active
echo
echo "Database Size:"
du -h /var/lib/nixos-gui/db.sqlite
EOF

chmod +x perf-report.sh
./perf-report.sh
```

## Emergency Contacts

- **On-Call Engineer**: Check PagerDuty
- **Security Team**: security@nixos-gui.org
- **Database Admin**: dba@nixos-gui.org
- **Network Team**: network@nixos-gui.org

## Quick Reference

### Service Control
```bash
systemctl start nixos-gui
systemctl stop nixos-gui
systemctl restart nixos-gui
systemctl status nixos-gui
```

### Log Locations
- Application: `/var/log/nixos-gui/app.log`
- Access: `/var/log/nixos-gui/access.log`
- Error: `/var/log/nixos-gui/error.log`
- Audit: `/var/log/nixos-gui/audit.log`

### Configuration
- NixOS: `/etc/nixos/configuration.nix`
- App Config: `/var/lib/nixos-gui/config.json`
- Secrets: `/run/secrets/nixos-gui/*`

### Useful Aliases
```bash
alias nxg-logs='journalctl -u nixos-gui -f'
alias nxg-restart='sudo systemctl restart nixos-gui'
alias nxg-status='systemctl status nixos-gui'
alias nxg-metrics='curl -s http://localhost:8080/api/metrics | jq'
```

---

Remember: When in doubt, check the logs first!