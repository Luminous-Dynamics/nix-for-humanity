# 🎓 NixOS GUI - Knowledge Transfer Document

This document captures critical knowledge about the NixOS GUI system for future maintainers and developers.

## 🧠 System Knowledge

### Core Concepts

#### 1. Architecture Philosophy
- **Declarative First**: Everything follows NixOS philosophy
- **Security by Default**: Never trust user input
- **Plugin Isolation**: Each plugin runs in its own sandbox
- **Fail Safe**: System degrades gracefully

#### 2. Design Decisions

**Why Node.js Backend?**
- Rapid development
- Rich ecosystem
- Easy plugin system
- Good async support
- WebSocket native

**Why Vanilla JS Frontend?**
- No framework lock-in
- Smaller bundle size
- Better performance
- Easier maintenance
- Web Components future

**Why SQLite Default?**
- Zero configuration
- Single file backup
- Good enough for 99% of users
- Easy PostgreSQL migration path

### Critical Code Paths

#### 1. Authentication Flow
```
User Login → PAM Check → Generate JWT → Create Session → Return Token
                ↓ (fail)
          Polkit Fallback → Verify Privileges → Continue or Reject
```

**Key Files**:
- `/auth/auth-service.js` - PAM integration
- `/middleware/auth.js` - JWT verification
- `/polkit/policies.js` - Privilege rules

#### 2. Package Operations
```
Search Request → Cache Check → Nix Search → Parse Results → Update Cache → Return
                      ↓ (miss)
              Direct Nix Query → Transform → Cache → Return
```

**Key Files**:
- `/services/package-manager.js` - Core logic
- `/cache/package-cache.js` - Caching layer
- `/helpers/nix-wrapper.js` - Nix integration

#### 3. Plugin Loading
```
Discovery → Validation → Sandboxing → API Injection → Initialization
    ↓           ↓            ↓            ↓               ↓
Scan Dir   Check Manifest  Create VM  Inject Safe API  Call init()
```

**Key Files**:
- `/plugin-system/plugin-manager.js` - Orchestration
- `/plugin-system/plugin-validator.js` - Security checks
- `/plugin-system/plugin-sandbox.js` - Isolation

### Common Gotchas

#### 1. State Management
- **Problem**: Frontend state can desync from backend
- **Solution**: WebSocket events for real-time updates
- **Watch for**: Race conditions in concurrent operations

#### 2. Permission Elevation
- **Problem**: Some operations need root privileges
- **Solution**: Polkit helper service
- **Watch for**: User not in wheel group

#### 3. Cache Invalidation
- **Problem**: Stale data after system changes
- **Solution**: File watchers on `/etc/nixos`
- **Watch for**: Manual edits outside GUI

#### 4. Plugin Security
- **Problem**: Malicious plugins could harm system
- **Solution**: Capability-based permissions
- **Watch for**: Permission escalation attempts

## 🔍 Debugging Guide

### Common Issues

#### "Cannot find module X"
```bash
# Usually means node_modules out of sync
rm -rf node_modules package-lock.json
npm install
```

#### "Permission denied" on service start
```bash
# Check systemd service file
systemctl cat nixos-gui

# Verify user exists
id nixos-gui

# Check file permissions
ls -la /var/lib/nixos-gui
```

#### Slow performance
```bash
# Check cache hit rate
curl http://localhost:8080/api/metrics | jq .cache

# Look for slow queries
grep "SLOW" /var/log/nixos-gui/app.log

# Monitor in real-time
tail -f /var/log/nixos-gui/app.log | grep "response_time"
```

### Debug Tools

#### Enable Debug Logging
```javascript
// In production
DEBUG=nixos-gui:* nixos-gui

// Specific modules
DEBUG=nixos-gui:auth,nixos-gui:cache nixos-gui
```

#### Performance Profiling
```bash
# Start with profiler
node --inspect nixos-gui

# Connect Chrome DevTools
chrome://inspect

# Take heap snapshot for memory leaks
kill -USR2 $(pgrep nixos-gui)
```

#### API Testing
```bash
# Test with curl
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'

# Full API test suite
npm run test:api
```

## 🏗️ Development Workflows

### Adding a New Feature

1. **Plan the API**
   ```javascript
   // routes/feature.js
   router.post('/api/feature/action', authenticate, async (req, res) => {
     // Implementation
   });
   ```

2. **Add Service Layer**
   ```javascript
   // services/feature-service.js
   class FeatureService {
     async performAction(params) {
       // Business logic
     }
   }
   ```

3. **Update Frontend**
   ```javascript
   // frontend/js/feature.js
   async function callFeature() {
     const result = await api.post('/api/feature/action', data);
   }
   ```

4. **Add Tests**
   ```javascript
   // tests/feature.test.js
   describe('Feature', () => {
     test('should perform action', async () => {
       // Test implementation
     });
   });
   ```

### Creating a Plugin

1. **Scaffold Structure**
   ```bash
   npx create-nixos-gui-plugin my-plugin
   ```

2. **Define Manifest**
   ```json
   {
     "id": "my-plugin",
     "permissions": ["ui.menu", "system.packages.read"]
   }
   ```

3. **Implement Logic**
   ```javascript
   class MyPlugin {
     async initialize(api) {
       await api.ui.registerMenuItem({...});
     }
   }
   ```

4. **Test in Isolation**
   ```bash
   npm run dev --plugin=my-plugin
   ```

## 📚 Tribal Knowledge

### Performance Tips

1. **Database Indexes**
   - Package name searches need index
   - Generation queries benefit from timestamp index
   - Service status lookups should be cached

2. **Caching Strategy**
   - Package searches: 5 minute TTL
   - Service status: 10 second TTL
   - Configuration: Invalidate on file change
   - User sessions: 24 hour TTL

3. **WebSocket Optimization**
   - Batch updates within 100ms window
   - Use compression for large payloads
   - Implement heartbeat for connection health

### Security Best Practices

1. **Input Validation**
   - Never trust user input
   - Validate at edge (API layer)
   - Sanitize for display
   - Use parameterized queries

2. **Authentication**
   - JWT expires in 24 hours
   - Refresh tokens in httpOnly cookies
   - Rate limit auth endpoints
   - Log all auth attempts

3. **Plugin Security**
   - Validate all manifests
   - Scan for dangerous patterns
   - Limit resource usage
   - Monitor API calls

### Deployment Wisdom

1. **Zero-Downtime Updates**
   ```bash
   # Start new version on different port
   nixos-gui --port 8081 &
   
   # Health check
   curl http://localhost:8081/api/health
   
   # Switch nginx/load balancer
   # Stop old version
   ```

2. **Database Migrations**
   - Always backup first
   - Test rollback procedure
   - Run in transaction
   - Have recovery plan

3. **Monitoring Setup**
   - Alert on error rate > 1%
   - Page if response time > 1s
   - Monitor disk usage
   - Track active sessions

## 🎯 Quick Reference

### Important Paths
```
/var/lib/nixos-gui/         # Data directory
├── db.sqlite               # Main database
├── plugins/                # Installed plugins
├── cache/                  # File cache
└── uploads/                # Temporary files

/var/log/nixos-gui/         # Logs
├── app.log                 # Application log
├── error.log               # Error log
├── audit.log               # Security audit
└── access.log              # HTTP access

/etc/nixos-gui/             # Configuration
├── config.json             # App config
└── secrets/                # Sensitive data
```

### Key Environment Variables
```bash
NODE_ENV=production         # Production mode
DEBUG=nixos-gui:*          # Debug logging
PORT=8080                  # Listen port
DATABASE_URL=...           # Database connection
REDIS_URL=...              # Redis connection
JWT_SECRET=...             # JWT signing key
SESSION_SECRET=...         # Session encryption
```

### Useful Commands
```bash
# Development
npm run dev                 # Start dev server
npm test                   # Run tests
npm run lint               # Check code style
npm run build              # Build for production

# Production
nixos-gui --help           # Show options
nixos-gui --validate       # Check config
nixos-gui migrate          # Run migrations
nixos-gui plugin list      # List plugins

# Debugging
DEBUG=* nixos-gui          # Full debug output
NODE_OPTIONS="--inspect"   # Enable debugger
strace -f nixos-gui        # System call trace
tcpdump -i lo port 8080    # Network trace
```

## 🤝 Handoff Notes

### For New Maintainers

1. **First Week**
   - Read all documentation
   - Run test suite
   - Deploy to test environment
   - Review recent issues

2. **First Month**
   - Make small fixes
   - Review PRs
   - Engage with community
   - Plan improvements

3. **Ongoing**
   - Keep dependencies updated
   - Monitor security advisories
   - Respond to user feedback
   - Maintain documentation

### Key Relationships

- **NixOS Core Team**: Coordinate for NixOS changes
- **Security Team**: Report vulnerabilities
- **Plugin Authors**: API compatibility
- **Large Users**: Feature requests and testing

### Future Considerations

1. **Rust Migration**: Backend performance improvement
2. **GraphQL API**: More flexible queries
3. **Mobile Apps**: Native experiences
4. **Cloud Sync**: Multi-device support
5. **AI Features**: Smart suggestions

---

**Remember**: The code is the easy part. Understanding why it exists and how it's used is what matters. When in doubt, ask the community!