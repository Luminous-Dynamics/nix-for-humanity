# 🎯 NixOS GUI - Maintainer Quick Reference

## 🚀 Essential Commands

```bash
# Development
npm start           # Start dev server (port 8080)
npm test           # Run test suite
npm run build      # Build for production
npm run lint       # Check code quality

# Maintenance
npm audit          # Check security vulnerabilities
npm update         # Update dependencies
npm run db:migrate # Run database migrations
npm run cache:clear # Clear all caches

# Deployment
npm run docker:build # Build Docker image
npm run deploy:prod  # Deploy to production
npm run rollback     # Rollback last deployment
```

## 📍 Key Files & Locations

```
/src/
├── server.js          # Main backend entry
├── frontend/
│   └── App.tsx       # React app root
├── api/
│   └── routes.js     # API endpoints
└── auth/
    └── auth-service.js # Authentication

/config/
├── default.json      # Default settings
├── production.json   # Production overrides
└── security.json     # Security settings

/plugin-system/
├── plugin-api.js     # Plugin SDK
└── plugins/          # Installed plugins

/monitoring/
├── dashboard.html    # Metrics dashboard
└── health-check.sh   # System health script
```

## 🔧 Common Tasks

### Add New API Endpoint
```javascript
// In /src/api/routes.js
router.post('/api/new-endpoint', authenticate, async (req, res) => {
  // Implementation
});
```

### Create New Plugin
```bash
npm run plugin:create my-plugin
cd plugins/my-plugin
npm install
npm run dev
```

### Update Documentation
```bash
cd docs/
# Edit markdown files
npm run docs:build  # Generate static site
```

## 🚨 Troubleshooting

### Service Won't Start
```bash
# Check logs
journalctl -u nixos-gui -n 100

# Verify ports
sudo lsof -i :8080

# Reset service
sudo systemctl restart nixos-gui
```

### Database Issues
```bash
# Backup first!
cp /var/lib/nixos-gui/db.sqlite /tmp/backup.db

# Check integrity
sqlite3 /var/lib/nixos-gui/db.sqlite "PRAGMA integrity_check;"

# Rebuild if needed
npm run db:rebuild
```

### Performance Problems
```bash
# Check metrics
curl http://localhost:8080/api/metrics

# Clear caches
npm run cache:clear

# Analyze slow queries
npm run db:analyze
```

## 🔒 Security Checklist

- [ ] All secrets in environment variables
- [ ] HTTPS enabled in production
- [ ] Rate limiting configured
- [ ] Input validation on all endpoints
- [ ] Regular dependency updates
- [ ] Security headers present
- [ ] Audit logging enabled

## 📊 Key Metrics

Monitor these daily:
- **Response Time**: < 200ms (target)
- **Error Rate**: < 1% (critical)
- **Active Users**: Track growth
- **Plugin Installs**: Ecosystem health
- **Memory Usage**: < 500MB typical
- **CPU Usage**: < 30% normal

## 🔑 Important URLs

### Development
- http://localhost:8080 - Main app
- http://localhost:8080/api - API root
- http://localhost:8080/dashboard - Monitoring
- http://localhost:8080/docs - Documentation

### Production
- https://[domain] - Production app
- https://[domain]/health - Health check
- https://status.[domain] - Status page
- https://api.[domain]/docs - API docs

## 📱 Support Escalation

1. **Community Support** (Discord/Forum)
   - General questions
   - How-to guides
   - Feature requests

2. **GitHub Issues**
   - Bug reports
   - Documentation fixes
   - Code contributions

3. **Security Issues**
   - security@[domain]
   - Use PGP encryption
   - Follow responsible disclosure

4. **Emergency**
   - System outages
   - Data loss
   - Security breaches
   - Contact: [emergency contacts]

## 🎯 Daily Checklist

- [ ] Check monitoring dashboard
- [ ] Review error logs
- [ ] Scan GitHub issues
- [ ] Respond to Discord questions
- [ ] Update status page
- [ ] Plan tomorrow's priorities

## 💡 Pro Tips

1. **Use tmux** for persistent sessions
2. **Enable debug mode** with DEBUG=nixos-gui:*
3. **Test locally first** - always
4. **Document weird fixes** in TROUBLESHOOTING.md
5. **Automate repetitive tasks**
6. **Take breaks** - prevent burnout

## 🚀 Release Process

```bash
# 1. Update version
npm version patch/minor/major

# 2. Run tests
npm test

# 3. Build release
npm run build:release

# 4. Tag release
git tag -a v1.0.1 -m "Release notes"

# 5. Push to GitHub
git push origin main --tags

# 6. Deploy
npm run deploy:prod

# 7. Announce
# - GitHub release
# - Discord announcement
# - Blog post
```

## 📞 Quick Contacts

- **Lead Maintainer**: [Name] - [email]
- **Security Team**: security@[domain]
- **Infrastructure**: ops@[domain]
- **Community**: community@[domain]

---

**Remember**: You're maintaining a tool that makes NixOS accessible to thousands. Every decision matters, but don't let perfection block progress.

**Stay calm, test thoroughly, and ship confidently!** 🚀