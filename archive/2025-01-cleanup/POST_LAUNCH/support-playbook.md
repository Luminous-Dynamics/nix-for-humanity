# 📞 NixOS GUI - Post-Launch Support Playbook

This playbook provides structured procedures for supporting NixOS GUI after launch.

## 🎯 Support Tiers

### Tier 1: Community Support (0-24h response)
- GitHub Issues
- Discord/Forum
- Documentation self-service
- Community volunteers

### Tier 2: Core Team Support (4-8h response)
- Critical bugs
- Security issues
- Performance problems
- Major feature requests

### Tier 3: Emergency Support (1h response)
- Production outages
- Security breaches
- Data corruption
- Critical vulnerabilities

## 📋 Common Support Scenarios

### 1. "GUI Won't Start"

**Diagnosis Steps:**
```bash
# Check service status
systemctl status nixos-gui

# Check port availability
sudo lsof -i :8080

# Review logs
journalctl -u nixos-gui -n 50

# Verify configuration
nixos-gui --validate-config
```

**Common Causes & Solutions:**

| Symptom | Cause | Solution |
|---------|-------|----------|
| Port in use | Another service on 8080 | Change port in config |
| Permission denied | User not in wheel group | `sudo usermod -aG wheel username` |
| Service fails | Missing dependencies | `sudo nixos-rebuild switch` |
| Database locked | Improper shutdown | Remove lock file |

**Response Template:**
```markdown
Hi [User],

Thank you for reporting this issue. Let's troubleshoot your NixOS GUI startup problem:

1. First, check if the service is running:
   ```
   systemctl status nixos-gui
   ```

2. If it's not running, check the logs:
   ```
   journalctl -u nixos-gui -n 50
   ```

3. Common fix - restart the service:
   ```
   sudo systemctl restart nixos-gui
   ```

If this doesn't resolve the issue, please share:
- The output from the above commands
- Your NixOS version
- When the issue started

Best regards,
NixOS GUI Support Team
```

### 2. "Can't Install Packages"

**Diagnosis Steps:**
```bash
# Check Nix daemon
systemctl status nix-daemon

# Verify user permissions
groups $USER

# Test Nix directly
nix-env -qa firefox

# Check disk space
df -h /nix/store
```

**Response Template:**
```markdown
Hi [User],

I understand you're having trouble installing packages. Let's diagnose:

1. Verify your user has permission:
   - Are you in the 'wheel' group? Check with: `groups`
   - Can you run: `nix-env -qa firefox`?

2. Check system resources:
   - Disk space: `df -h /nix/store`
   - Nix daemon: `systemctl status nix-daemon`

3. Try these solutions:
   - Clear cache: Settings → Advanced → Clear Package Cache
   - Refresh package list: Ctrl+R on packages tab
   - Manual install: `nix-env -iA nixos.packagename`

Please share any error messages you see.

Best regards,
NixOS GUI Support Team
```

### 3. "Plugin Not Working"

**Diagnosis Steps:**
```bash
# List installed plugins
ls -la /var/lib/nixos-gui/plugins/

# Check plugin logs
grep "plugin-id" /var/log/nixos-gui/app.log

# Verify permissions
nixos-gui plugin list

# Test in safe mode
nixos-gui --safe-mode
```

**Response Template:**
```markdown
Hi [User],

Let's troubleshoot the plugin issue:

1. Check if the plugin is enabled:
   - Go to Plugins tab
   - Find your plugin
   - Ensure it's toggled ON

2. Try these steps:
   - Disable and re-enable the plugin
   - Check plugin permissions match requirements
   - Clear browser cache (Ctrl+Shift+R)

3. For persistent issues:
   - Start GUI in safe mode (disables all plugins)
   - Re-install the problematic plugin
   - Check for plugin updates

Which plugin are you having trouble with? Any error messages?

Best regards,
NixOS GUI Support Team
```

### 4. "Performance Issues"

**Diagnosis Steps:**
```bash
# Check system resources
htop

# Monitor GUI specifically
systemctl status nixos-gui --no-pager

# Check cache hit rate
curl http://localhost:8080/api/metrics | jq .cache

# Database size
du -h /var/lib/nixos-gui/db.sqlite
```

**Response Template:**
```markdown
Hi [User],

Let's improve your NixOS GUI performance:

1. Quick fixes:
   - Clear browser cache
   - Reduce number of active plugins
   - Close unused tabs in GUI

2. System optimization:
   - Enable Redis caching (significant speed boost)
   - Vacuum database: `nixos-gui db vacuum`
   - Increase worker processes in settings

3. Please check:
   - RAM usage when slow
   - Number of packages installed
   - Browser console for errors (F12)

What specific operations are slow?

Best regards,
NixOS GUI Support Team
```

## 🔧 Advanced Troubleshooting

### Database Issues

```bash
# Backup current database
cp /var/lib/nixos-gui/db.sqlite /tmp/backup.sqlite

# Check integrity
sqlite3 /var/lib/nixos-gui/db.sqlite "PRAGMA integrity_check;"

# Rebuild if corrupted
nixos-gui db rebuild

# Restore from backup
nixos-gui db restore /path/to/backup
```

### Authentication Problems

```bash
# Test PAM directly
su testuser -c 'echo success'

# Check Polkit rules
pkaction --verbose --action-id org.nixos.gui.manage

# Reset user session
redis-cli DEL "session:*"

# Generate new secrets
nixos-gui auth reset-secrets
```

### Plugin Conflicts

```bash
# Start without plugins
nixos-gui --no-plugins

# Load plugins one by one
nixos-gui --plugin specific-plugin

# Check plugin dependencies
nixos-gui plugin deps plugin-name

# Force plugin update
nixos-gui plugin update --force plugin-name
```

## 📊 Support Metrics Tracking

### Key Metrics to Monitor

1. **Response Times**
   - First response: Target < 4 hours
   - Resolution: Target < 24 hours
   - Escalation rate: Target < 10%

2. **Issue Categories**
   - Installation: 30%
   - Usage questions: 40%
   - Bugs: 20%
   - Feature requests: 10%

3. **User Satisfaction**
   - Resolved on first response: Target > 60%
   - User satisfaction: Target > 4.5/5
   - Repeat issues: Target < 5%

### Weekly Support Report Template

```markdown
# NixOS GUI Support Report - Week of [DATE]

## Summary
- Total tickets: [NUMBER]
- Resolved: [NUMBER] ([PERCENTAGE]%)
- Average response time: [TIME]
- User satisfaction: [SCORE]/5

## Top Issues
1. [ISSUE] - [COUNT] reports
2. [ISSUE] - [COUNT] reports
3. [ISSUE] - [COUNT] reports

## Notable Bugs
- [BUG DESCRIPTION] - Fixed in v[VERSION]
- [BUG DESCRIPTION] - Workaround provided

## Improvements Made
- [IMPROVEMENT]
- [IMPROVEMENT]

## Next Week Focus
- [PRIORITY ITEM]
- [PRIORITY ITEM]
```

## 🎓 Support Team Training

### Onboarding Checklist

- [ ] Access to support channels
- [ ] Read all documentation
- [ ] Complete test installation
- [ ] Shadow experienced supporter
- [ ] Handle 5 supervised tickets
- [ ] Review common issues guide
- [ ] Learn escalation procedures

### Required Knowledge

1. **Technical**
   - NixOS basics
   - GUI architecture
   - Common Linux troubleshooting
   - Plugin system

2. **Soft Skills**
   - Empathetic communication
   - Clear explanations
   - Patience with beginners
   - Professional tone

### Response Guidelines

1. **Always**
   - Acknowledge within 4 hours
   - Be friendly and professional
   - Provide clear steps
   - Follow up on solutions

2. **Never**
   - Assume user expertise
   - Dismiss concerns
   - Provide root passwords
   - Make system changes remotely

## 📈 Escalation Matrix

| Issue Type | Tier 1 | Tier 2 | Tier 3 |
|------------|--------|--------|--------|
| How-to questions | ✓ | | |
| Configuration help | ✓ | | |
| Bug reports | ✓ | ✓ | |
| Performance issues | ✓ | ✓ | |
| Security concerns | | ✓ | ✓ |
| Data loss | | | ✓ |
| Production outages | | | ✓ |

## 🔐 Security Response

### Security Issue Reported

1. **Immediate Actions**
   - Acknowledge privately
   - Don't discuss publicly
   - Assess severity
   - Begin investigation

2. **Investigation**
   - Reproduce issue
   - Determine impact
   - Develop fix
   - Test thoroughly

3. **Resolution**
   - Deploy patch
   - Notify affected users
   - Update documentation
   - Post-mortem analysis

### CVE Process

1. Request CVE number
2. Prepare security advisory
3. Coordinate disclosure
4. Release patch
5. Public announcement

## 📚 Knowledge Base Articles

### Must-Have Articles

1. **Getting Started**
   - First-time setup
   - Basic navigation
   - Common tasks

2. **Troubleshooting**
   - Startup issues
   - Performance tuning
   - Plugin problems

3. **Advanced Topics**
   - Custom configurations
   - API usage
   - Plugin development

### Article Template

```markdown
# [TITLE]

## Problem
Brief description of the issue

## Solution
Step-by-step resolution

## Additional Information
- Related articles
- External resources
- Version notes

## Still Need Help?
Contact support options

Last updated: [DATE]
Applies to: NixOS GUI v[VERSION]+
```

## 🤝 Community Management

### Discord/Forum Moderation

1. **Daily Tasks**
   - Monitor help channels
   - Answer questions
   - Redirect complex issues
   - Update pinned messages

2. **Weekly Tasks**
   - Community stats report
   - Highlight helpful members
   - Update FAQ
   - Plan community events

### Community Recognition

- **Helper of the Month**: Most helpful community member
- **Plugin of the Month**: Best new plugin
- **Contributor Badge**: Significant contributions
- **Beta Tester Badge**: Early adopters

## 🚀 Continuous Improvement

### Feedback Loop

1. Collect user feedback
2. Analyze common issues
3. Improve documentation
4. Update FAQ
5. Enhance features
6. Measure satisfaction

### Monthly Review

- Top support issues
- Documentation gaps
- Feature requests
- Performance metrics
- Team performance
- Process improvements

---

Remember: Every support interaction is an opportunity to improve the product and strengthen the community!