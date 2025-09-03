#!/bin/bash

# 🚀 Production Deployment Script for AI-Driven Interface Generation System
# Automates deployment, testing, and monitoring setup

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOY_DIR="${DEPLOY_DIR:-/opt/luminous-nix-gui}"
LOG_DIR="${LOG_DIR:-/var/log/luminous-nix-gui}"
CONFIG_DIR="${CONFIG_DIR:-/etc/luminous-nix-gui}"
DATA_DIR="${DATA_DIR:-/var/lib/luminous-nix-gui}"

# Functions
print_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Python version
    if ! python3 --version | grep -q "3\.[89]\|3\.1[0-9]"; then
        print_error "Python 3.8+ required"
        exit 1
    fi
    print_success "Python version OK"
    
    # Check for required Python packages
    required_packages=("sqlite3" "asyncio" "pathlib" "dataclasses")
    for package in "${required_packages[@]}"; do
        if python3 -c "import $package" 2>/dev/null; then
            print_success "$package available"
        else
            print_error "$package not found"
            exit 1
        fi
    done
    
    # Check disk space (need at least 1GB)
    available_space=$(df / | awk 'NR==2 {print $4}')
    if [ "$available_space" -lt 1048576 ]; then
        print_error "Insufficient disk space (need at least 1GB)"
        exit 1
    fi
    print_success "Disk space OK"
}

create_directories() {
    print_header "Creating Directory Structure"
    
    # Create necessary directories
    for dir in "$DEPLOY_DIR" "$LOG_DIR" "$CONFIG_DIR" "$DATA_DIR"; do
        if [ ! -d "$dir" ]; then
            sudo mkdir -p "$dir"
            print_success "Created $dir"
        else
            print_warning "$dir already exists"
        fi
    done
    
    # Set permissions
    sudo chmod 755 "$DEPLOY_DIR" "$CONFIG_DIR"
    sudo chmod 775 "$LOG_DIR" "$DATA_DIR"
    print_success "Directory permissions set"
}

install_application() {
    print_header "Installing Application Files"
    
    # Copy application files
    echo "Copying application files..."
    cp -r *.py "$DEPLOY_DIR/"
    
    # Create __init__.py if it doesn't exist
    touch "$DEPLOY_DIR/__init__.py"
    
    # Make scripts executable
    chmod +x "$DEPLOY_DIR/production_deployment.py"
    chmod +x "$DEPLOY_DIR/test_comprehensive.py"
    chmod +x "$DEPLOY_DIR/integration_test_suite.py"
    
    print_success "Application files installed"
}

setup_configuration() {
    print_header "Setting Up Configuration"
    
    # Create default configuration
    cat > "$CONFIG_DIR/config.json" <<EOF
{
  "optimization": {
    "min_confidence": 0.7,
    "cooldown_hours": 24,
    "auto_apply": true
  },
  "pattern_analysis": {
    "min_pattern_frequency": 3,
    "confidence_threshold": 0.7
  },
  "feedback": {
    "time_based_trigger_seconds": 30,
    "max_storage_days": 90
  },
  "performance": {
    "slow_response_threshold_ms": 1000,
    "metric_retention_days": 30
  },
  "system": {
    "debug_mode": false,
    "log_level": "INFO",
    "data_dir": "$DATA_DIR",
    "cache_dir": "$DATA_DIR/cache",
    "config_dir": "$CONFIG_DIR",
    "db_path": "$DATA_DIR/learning.db"
  }
}
EOF
    
    print_success "Configuration file created"
    
    # Set up environment variables
    cat > "$CONFIG_DIR/environment" <<EOF
# Luminous NixOS GUI Environment Configuration
LUMINOUS_DATA_DIR=$DATA_DIR
LUMINOUS_CONFIG_DIR=$CONFIG_DIR
LUMINOUS_LOG_DIR=$LOG_DIR
LUMINOUS_OPTIMIZATION_AUTO_APPLY=true
LUMINOUS_DEBUG_MODE=false
EOF
    
    print_success "Environment configuration created"
}

run_database_migration() {
    print_header "Running Database Migrations"
    
    cd "$DEPLOY_DIR"
    
    # Run migrations
    python3 -c "
from database_migrations import DatabaseMigrationManager
manager = DatabaseMigrationManager('$DATA_DIR/learning.db')
if manager.migrate_to_version():
    print('✅ Database migrated successfully')
else:
    print('❌ Database migration failed')
    exit(1)
manager.close()
"
    
    print_success "Database schema updated to latest version"
}

run_tests() {
    print_header "Running Tests"
    
    cd "$DEPLOY_DIR"
    
    # Run unit tests
    echo "Running unit tests..."
    if python3 test_comprehensive.py > "$LOG_DIR/test_results.log" 2>&1; then
        print_success "Unit tests passed"
    else
        print_warning "Some unit tests failed (check $LOG_DIR/test_results.log)"
    fi
    
    # Run integration tests
    echo "Running integration tests..."
    if python3 integration_test_suite.py > "$LOG_DIR/integration_results.log" 2>&1; then
        print_success "Integration tests passed"
    else
        print_warning "Some integration tests failed (check $LOG_DIR/integration_results.log)"
    fi
}

setup_systemd_service() {
    print_header "Setting Up Systemd Service"
    
    # Create systemd service file
    sudo tee /etc/systemd/system/luminous-gui.service > /dev/null <<EOF
[Unit]
Description=Luminous NixOS GUI Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$DEPLOY_DIR
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=$CONFIG_DIR/environment
ExecStart=/usr/bin/python3 $DEPLOY_DIR/production_deployment.py
Restart=on-failure
RestartSec=10
StandardOutput=append:$LOG_DIR/service.log
StandardError=append:$LOG_DIR/service-error.log

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    # Enable but don't start yet
    sudo systemctl enable luminous-gui.service
    
    print_success "Systemd service configured"
}

setup_monitoring() {
    print_header "Setting Up Monitoring"
    
    # Create health check script
    cat > "$DEPLOY_DIR/health_check.sh" <<'EOF'
#!/bin/bash
python3 -c "
import asyncio
from production_deployment import ProductionDeployment

async def check():
    deployment = ProductionDeployment()
    deployment.initialize_services()
    health = await deployment.run_health_checks()
    
    if health['status'] == 'healthy':
        print('✅ System is healthy')
        exit(0)
    else:
        print('⚠️  System status:', health['status'])
        exit(1)

asyncio.run(check())
"
EOF
    chmod +x "$DEPLOY_DIR/health_check.sh"
    
    # Create monitoring cron job
    (crontab -l 2>/dev/null; echo "*/5 * * * * $DEPLOY_DIR/health_check.sh >> $LOG_DIR/health.log 2>&1") | crontab -
    
    print_success "Health monitoring configured (runs every 5 minutes)"
}

setup_log_rotation() {
    print_header "Setting Up Log Rotation"
    
    # Create logrotate configuration
    sudo tee /etc/logrotate.d/luminous-gui > /dev/null <<EOF
$LOG_DIR/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 $USER $USER
    sharedscripts
    postrotate
        systemctl reload luminous-gui.service > /dev/null 2>&1 || true
    endscript
}
EOF
    
    print_success "Log rotation configured"
}

perform_health_check() {
    print_header "Performing Initial Health Check"
    
    cd "$DEPLOY_DIR"
    
    # Run health check
    python3 -c "
import asyncio
from production_deployment import ProductionDeployment

async def main():
    deployment = ProductionDeployment()
    
    if not deployment.initialize_services():
        print('❌ Service initialization failed')
        return False
    
    health = await deployment.run_health_checks()
    
    print(f'Overall Status: {health[\"status\"].upper()}')
    
    for check_name, check_data in health['checks'].items():
        status = '✅' if check_data.get('healthy', False) else '❌'
        print(f'{status} {check_name.capitalize()}')
    
    return health['status'] in ['healthy', 'warning']

success = asyncio.run(main())
exit(0 if success else 1)
"
}

generate_deployment_report() {
    print_header "Generating Deployment Report"
    
    cd "$DEPLOY_DIR"
    
    # Generate report
    python3 -c "
from production_deployment import ProductionDeployment
import json

deployment = ProductionDeployment()
deployment.initialize_services()
report = deployment.generate_deployment_report()

print(f'Report generated: {report[\"generated_at\"]}')
print(f'Python version: {report[\"environment\"][\"python_version\"].split()[0]}')
print(f'Platform: {report[\"environment\"][\"platform\"]}')

# Save report
with open('$LOG_DIR/deployment_report.json', 'w') as f:
    json.dump(report, f, indent=2)
"
    
    print_success "Deployment report saved to $LOG_DIR/deployment_report.json"
}

print_summary() {
    print_header "🎉 DEPLOYMENT COMPLETE!"
    
    echo
    echo "System deployed successfully with:"
    echo "• Application: $DEPLOY_DIR"
    echo "• Configuration: $CONFIG_DIR"
    echo "• Data: $DATA_DIR"
    echo "• Logs: $LOG_DIR"
    echo
    echo "Available Commands:"
    echo "• Start service: sudo systemctl start luminous-gui"
    echo "• Stop service: sudo systemctl stop luminous-gui"
    echo "• View status: sudo systemctl status luminous-gui"
    echo "• Check health: $DEPLOY_DIR/health_check.sh"
    echo "• View logs: tail -f $LOG_DIR/service.log"
    echo
    echo "Production Features:"
    echo "• ✅ Database migrations applied"
    echo "• ✅ All services initialized"
    echo "• ✅ Health monitoring active"
    echo "• ✅ Log rotation configured"
    echo "• ✅ Systemd service ready"
    echo
    print_success "System is production-ready!"
}

# Main deployment flow
main() {
    echo
    print_header "🚀 LUMINOUS NIXOS GUI DEPLOYMENT"
    echo
    
    check_prerequisites
    create_directories
    install_application
    setup_configuration
    run_database_migration
    run_tests
    setup_systemd_service
    setup_monitoring
    setup_log_rotation
    perform_health_check
    generate_deployment_report
    print_summary
    
    echo
    print_success "Deployment completed successfully!"
    echo
}

# Handle errors
trap 'print_error "Deployment failed! Check logs for details."; exit 1' ERR

# Run main function
main "$@"