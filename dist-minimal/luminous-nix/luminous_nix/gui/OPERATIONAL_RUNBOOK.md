# 📖 Operational Runbook - AI-Driven Interface Generation System

## 🎯 System Overview

The AI-Driven Interface Generation System is a production-ready application that generates user interfaces from natural language requests using AI, with continuous learning and optimization capabilities.

### Core Components
- **Interface Generation Engine**: Natural language to UI conversion
- **Pattern Analysis System**: Usage pattern detection and insights
- **Feedback Collection**: User feedback and sentiment analysis
- **A/B Testing Framework**: Interface variation testing
- **Automatic Optimization**: Self-improving system
- **Performance Monitoring**: Real-time metrics tracking

## 🚀 Deployment

### Prerequisites
- Python 3.8+
- SQLite3
- 2GB free disk space
- Linux/Unix environment (tested on NixOS, Ubuntu, CentOS)

### Initial Deployment
```bash
# 1. Clone repository
git clone <repository-url>
cd luminous-nix/src/luminous_nix/gui

# 2. Run deployment script
chmod +x deploy.sh
sudo ./deploy.sh

# 3. Verify deployment
./health_check.sh
```

### Configuration
Primary configuration file: `/etc/luminous-nix-gui/config.json`

Key settings:
```json
{
  "optimization": {
    "min_confidence": 0.7,      # Minimum confidence for auto-optimization
    "cooldown_hours": 24,        # Hours between optimization runs
    "auto_apply": true           # Auto-apply optimizations
  },
  "performance": {
    "slow_response_threshold_ms": 1000,  # Alert threshold
    "metric_retention_days": 30          # Data retention
  }
}
```

Environment variables:
```bash
LUMINOUS_DEBUG_MODE=false
LUMINOUS_OPTIMIZATION_MIN_CONFIDENCE=0.7
LUMINOUS_DATA_DIR=/var/lib/luminous-nix-gui
```

## 🔧 Operations

### Starting the System

#### Method 1: Systemd Service
```bash
# Start service
sudo systemctl start luminous-gui

# Enable auto-start on boot
sudo systemctl enable luminous-gui

# Check status
sudo systemctl status luminous-gui
```

#### Method 2: Direct Execution
```bash
cd /opt/luminous-nix-gui
python3 production_deployment.py
```

#### Method 3: API Server
```bash
# Start API server
python3 api_server.py --host 0.0.0.0 --port 5000

# With debug mode
python3 api_server.py --debug
```

### Stopping the System
```bash
# Graceful shutdown
sudo systemctl stop luminous-gui

# Force stop (emergency)
sudo systemctl kill luminous-gui
```

### Monitoring

#### Real-time Dashboard
```bash
# Interactive dashboard (requires terminal with color support)
python3 monitoring_dashboard.py

# Simple mode (works in any terminal)
python3 monitoring_dashboard.py --simple
```

#### Health Checks
```bash
# Quick health check
./health_check.sh

# Detailed health report
python3 -c "
import asyncio
from production_deployment import ProductionDeployment
asyncio.run(ProductionDeployment().run_health_checks())
"
```

#### View Logs
```bash
# Service logs
tail -f /var/log/luminous-nix-gui/service.log

# Error logs
tail -f /var/log/luminous-nix-gui/service-error.log

# Health check logs
tail -f /var/log/luminous-nix-gui/health.log
```

## 📊 Key Metrics

### Performance Metrics
- **Interface Generation Time**: Target < 300ms
- **Pattern Analysis Time**: Target < 100ms
- **API Response Time**: Target < 200ms
- **Cache Hit Rate**: Target > 80%

### Business Metrics
- **Daily Active Users**: Monitor trend
- **Interfaces Generated**: Track volume
- **User Satisfaction**: Feedback sentiment > 0.7
- **A/B Test Success Rate**: Improvement > 5%

### System Metrics
- **CPU Usage**: Alert if > 80%
- **Memory Usage**: Alert if > 80%
- **Disk Space**: Alert if < 1GB free
- **Error Rate**: Alert if > 5%

## 🚨 Troubleshooting

### Common Issues

#### Issue: Service Won't Start
```bash
# Check for port conflicts
sudo netstat -tulpn | grep 5000

# Check permissions
ls -la /var/lib/luminous-nix-gui

# Check Python dependencies
python3 -c "import flask, jwt, sqlite3"

# View detailed error
sudo journalctl -u luminous-gui -n 50
```

#### Issue: Database Locked
```bash
# Stop all services
sudo systemctl stop luminous-gui

# Check for stale locks
lsof /var/lib/luminous-nix-gui/learning.db

# Kill stuck processes
kill -9 <pid>

# Restart service
sudo systemctl start luminous-gui
```

#### Issue: High Memory Usage
```bash
# Check memory consumers
ps aux --sort=-%mem | head -10

# Clear cache
python3 -c "
from production_deployment import ProductionDeployment
import asyncio
asyncio.run(ProductionDeployment().cleanup_old_data())
"

# Restart service
sudo systemctl restart luminous-gui
```

#### Issue: Slow Performance
```bash
# Check database size
du -h /var/lib/luminous-nix-gui/learning.db

# Run optimization
python3 -c "
from production_deployment import ProductionDeployment
import asyncio
asyncio.run(ProductionDeployment().run_optimization_cycle())
"

# Analyze slow queries (if debug enabled)
grep "slow_query" /var/log/luminous-nix-gui/service.log
```

## 🔄 Maintenance Tasks

### Daily Tasks
1. **Health Check**: Automated via cron
2. **Log Review**: Check for errors/warnings
3. **Metrics Review**: Monitor dashboard

### Weekly Tasks
1. **Performance Review**: Analyze trends
2. **Optimization Cycle**: Manual trigger if needed
3. **Backup Database**: See backup procedure

### Monthly Tasks
1. **Data Cleanup**: Remove old records
2. **Security Updates**: Apply patches
3. **Capacity Planning**: Review growth trends

## 💾 Backup & Recovery

### Backup Procedure
```bash
# Stop service
sudo systemctl stop luminous-gui

# Backup database
cp /var/lib/luminous-nix-gui/learning.db \
   /backup/luminous-gui-$(date +%Y%m%d).db

# Backup configuration
tar -czf /backup/luminous-gui-config-$(date +%Y%m%d).tar.gz \
    /etc/luminous-nix-gui/

# Restart service
sudo systemctl start luminous-gui
```

### Recovery Procedure
```bash
# Stop service
sudo systemctl stop luminous-gui

# Restore database
cp /backup/luminous-gui-YYYYMMDD.db \
   /var/lib/luminous-nix-gui/learning.db

# Restore configuration
tar -xzf /backup/luminous-gui-config-YYYYMMDD.tar.gz -C /

# Run migrations (if needed)
cd /opt/luminous-nix-gui
python3 -c "
from database_migrations import DatabaseMigrationManager
DatabaseMigrationManager('/var/lib/luminous-nix-gui/learning.db').migrate_to_version()
"

# Start service
sudo systemctl start luminous-gui
```

## 📈 Scaling

### Vertical Scaling
- Increase CPU cores for parallel processing
- Add RAM for larger caches
- Use SSD for database storage

### Horizontal Scaling
1. **Load Balancer**: HAProxy/Nginx in front
2. **Multiple API Servers**: Run multiple instances
3. **Shared Database**: PostgreSQL instead of SQLite
4. **Distributed Cache**: Redis for shared caching

### Performance Tuning
```bash
# Increase connection pool size
export LUMINOUS_CONNECTION_POOL_SIZE=20

# Increase cache size
export LUMINOUS_CACHE_MAX_SIZE=10000

# Enable WAL mode for SQLite
export LUMINOUS_ENABLE_WAL_MODE=true
```

## 🔐 Security

### API Authentication
- Default: JWT tokens (24-hour expiry)
- Production: Integrate with enterprise SSO

### Rate Limiting
- Default: 200 requests/day per IP
- Configurable per endpoint

### Data Protection
- Database encryption at rest
- TLS for API communications
- Regular security updates

## 📝 API Reference

### Base URL
```
http://localhost:5000/api
```

### Authentication
```bash
# Get token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}'

# Use token
curl -H "Authorization: Bearer <token>" \
  http://localhost:5000/api/interface/generate
```

### Key Endpoints
- `POST /api/interface/generate` - Generate interface
- `GET /api/patterns/insights` - Get insights
- `POST /api/feedback/collect` - Submit feedback
- `GET /api/performance/metrics` - Get metrics
- `GET /api/docs` - Full API documentation

## 🆘 Emergency Procedures

### System Unresponsive
1. Check system resources (CPU, memory, disk)
2. Kill stuck processes
3. Restart service
4. Check logs for root cause

### Data Corruption
1. Stop service immediately
2. Backup current state
3. Run database integrity check
4. Restore from last known good backup
5. Apply missing migrations

### Security Breach
1. Isolate system from network
2. Preserve logs for investigation
3. Reset all credentials
4. Apply security patches
5. Restore from clean backup

## 📞 Support Contacts

### Internal Team
- **System Admin**: admin@example.com
- **Development**: dev-team@example.com
- **On-Call**: +1-xxx-xxx-xxxx

### Escalation Path
1. L1: System monitoring alerts
2. L2: Operations team
3. L3: Development team
4. L4: Architecture team

## 📚 Additional Resources

### Documentation
- [Architecture Guide](COMPREHENSIVE_CODE_REVIEW.md)
- [API Documentation](http://localhost:5000/api/docs)
- [Development Guide](PRODUCTION_READY_SUMMARY.md)

### Tools
- **Monitoring**: `monitoring_dashboard.py`
- **Testing**: `integration_test_suite.py`
- **Deployment**: `deploy.sh`
- **Health Check**: `health_check.sh`

### Training Materials
- System overview presentation
- Troubleshooting workshop
- Performance tuning guide

## 🔄 Change Management

### Deployment Process
1. Test in staging environment
2. Create rollback plan
3. Schedule maintenance window
4. Deploy with blue-green strategy
5. Verify with health checks
6. Monitor for 24 hours

### Version Control
- Git tags for releases
- Semantic versioning (X.Y.Z)
- Changelog maintenance
- Migration scripts for database

---

## 📌 Quick Reference Card

### Essential Commands
```bash
# Service control
sudo systemctl start|stop|restart|status luminous-gui

# Health check
./health_check.sh

# View logs
tail -f /var/log/luminous-nix-gui/service.log

# Run optimization
python3 production_deployment.py

# Start monitoring
python3 monitoring_dashboard.py

# API server
python3 api_server.py

# Run tests
python3 integration_test_suite.py
```

### Key File Locations
- **Application**: `/opt/luminous-nix-gui/`
- **Configuration**: `/etc/luminous-nix-gui/`
- **Data**: `/var/lib/luminous-nix-gui/`
- **Logs**: `/var/log/luminous-nix-gui/`

### Critical Metrics Thresholds
- Response Time: < 1000ms
- Error Rate: < 5%
- CPU Usage: < 80%
- Memory Usage: < 80%
- Disk Space: > 1GB free

---

*Last Updated: 2024*
*Version: 1.0.0*
*Status: Production Ready*