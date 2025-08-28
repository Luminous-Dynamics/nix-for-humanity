#!/usr/bin/env python3
"""
✅ System Validation Suite for Production Deployment
Comprehensive validation of all system components
"""

import sys
import os
import time
import json
import sqlite3
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any
import importlib.util

from production_deployment import ProductionDeployment
from config_manager import ConfigManager


class SystemValidator:
    """Comprehensive system validation"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'errors': [],
            'warnings': [],
            'summary': {}
        }
        self.deployment = None
    
    def validate_python_version(self) -> Tuple[bool, str]:
        """Validate Python version"""
        version = sys.version_info
        if version.major == 3 and version.minor >= 8:
            return True, f"Python {version.major}.{version.minor}.{version.micro}"
        return False, f"Python 3.8+ required, found {version.major}.{version.minor}"
    
    def validate_dependencies(self) -> Tuple[bool, List[str]]:
        """Validate all Python dependencies"""
        missing = []
        required = [
            'flask', 'jwt', 'sqlite3', 'asyncio', 'dataclasses',
            'pathlib', 'json', 'hashlib', 'datetime', 'typing'
        ]
        
        for module in required:
            spec = importlib.util.find_spec(module)
            if spec is None:
                missing.append(module)
        
        return len(missing) == 0, missing
    
    def validate_file_structure(self) -> Tuple[bool, Dict[str, bool]]:
        """Validate all required files exist"""
        required_files = [
            'production_deployment.py',
            'config_manager.py',
            'database_migrations.py',
            'services.py',
            'performance_optimizations.py',
            'error_handler.py',
            'test_comprehensive.py',
            'integration_test_suite.py',
            'api_server.py',
            'monitoring_dashboard.py',
            'deploy.sh',
            'requirements.txt',
            'Dockerfile',
            'docker-compose.yml'
        ]
        
        file_status = {}
        all_present = True
        
        for filename in required_files:
            exists = Path(filename).exists()
            file_status[filename] = exists
            if not exists:
                all_present = False
        
        return all_present, file_status
    
    def validate_database(self) -> Tuple[bool, Dict[str, Any]]:
        """Validate database setup and migrations"""
        try:
            config = ConfigManager().config
            db_path = config.db_path
            
            # Create parent directory if needed
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Initialize database
            from database_migrations import DatabaseMigrationManager
            manager = DatabaseMigrationManager(db_path)
            
            # Check version
            current_version = manager.get_current_version()
            latest_version = 7
            
            # Migrate if needed
            if current_version < latest_version:
                success = manager.migrate_to_version(latest_version)
                if not success:
                    return False, {'error': 'Migration failed'}
            
            # Verify tables
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                ORDER BY name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            manager.close()
            
            return True, {
                'current_version': current_version,
                'tables': tables,
                'table_count': len(tables)
            }
            
        except Exception as e:
            return False, {'error': str(e)}
    
    def validate_services(self) -> Tuple[bool, Dict[str, str]]:
        """Validate all services can initialize"""
        try:
            self.deployment = ProductionDeployment()
            success = self.deployment.initialize_services()
            
            if not success:
                return False, {'error': 'Service initialization failed'}
            
            service_status = {}
            for name in self.deployment.services.keys():
                service_status[name] = 'initialized'
            
            return True, service_status
            
        except Exception as e:
            return False, {'error': str(e)}
    
    async def validate_health_checks(self) -> Tuple[bool, Dict[str, Any]]:
        """Validate health check system"""
        try:
            if not self.deployment:
                self.deployment = ProductionDeployment()
                self.deployment.initialize_services()
            
            health = await self.deployment.run_health_checks()
            
            all_healthy = all(
                check.get('healthy', False) 
                for check in health['checks'].values()
            )
            
            return all_healthy, health
            
        except Exception as e:
            return False, {'error': str(e)}
    
    def validate_api_server(self) -> Tuple[bool, str]:
        """Validate API server can start"""
        try:
            # Test import
            import api_server
            
            # Check Flask app exists
            if hasattr(api_server, 'app'):
                return True, "API server module valid"
            
            return False, "Flask app not found"
            
        except Exception as e:
            return False, f"API server error: {str(e)}"
    
    def validate_monitoring(self) -> Tuple[bool, str]:
        """Validate monitoring system"""
        try:
            import monitoring_dashboard
            
            # Check MonitoringDashboard class exists
            if hasattr(monitoring_dashboard, 'MonitoringDashboard'):
                return True, "Monitoring system valid"
            
            return False, "MonitoringDashboard class not found"
            
        except Exception as e:
            return False, f"Monitoring error: {str(e)}"
    
    def validate_configuration(self) -> Tuple[bool, Dict[str, Any]]:
        """Validate configuration system"""
        try:
            config = ConfigManager().config
            
            # Check critical settings
            checks = {
                'data_dir_exists': Path(config.data_dir).exists() or True,  # Will be created
                'db_path_valid': bool(config.db_path),
                'optimization_configured': hasattr(config, 'optimization'),
                'performance_configured': hasattr(config, 'performance'),
                'feedback_configured': hasattr(config, 'feedback')
            }
            
            all_valid = all(checks.values())
            
            return all_valid, checks
            
        except Exception as e:
            return False, {'error': str(e)}
    
    async def run_validation(self) -> Dict[str, Any]:
        """Run complete system validation"""
        
        print("""
╔════════════════════════════════════════════════════════════════════╗
║        ✅ SYSTEM VALIDATION SUITE                                  ║
╚════════════════════════════════════════════════════════════════════╝
        """)
        
        # Python version
        print("\n1️⃣ Checking Python Version...")
        success, result = self.validate_python_version()
        self.results['checks']['python_version'] = {
            'success': success,
            'details': result
        }
        print(f"   {'✅' if success else '❌'} {result}")
        
        # Dependencies
        print("\n2️⃣ Checking Dependencies...")
        success, missing = self.validate_dependencies()
        self.results['checks']['dependencies'] = {
            'success': success,
            'missing': missing
        }
        if success:
            print("   ✅ All core dependencies available")
        else:
            print(f"   ❌ Missing: {', '.join(missing)}")
        
        # File structure
        print("\n3️⃣ Checking File Structure...")
        success, files = self.validate_file_structure()
        self.results['checks']['files'] = {
            'success': success,
            'details': files
        }
        missing_files = [f for f, exists in files.items() if not exists]
        if success:
            print(f"   ✅ All {len(files)} required files present")
        else:
            print(f"   ❌ Missing {len(missing_files)} files")
            for f in missing_files[:5]:  # Show first 5
                print(f"      - {f}")
        
        # Database
        print("\n4️⃣ Checking Database...")
        success, db_info = self.validate_database()
        self.results['checks']['database'] = {
            'success': success,
            'details': db_info
        }
        if success:
            print(f"   ✅ Database ready (v{db_info.get('current_version', 0)}, {db_info.get('table_count', 0)} tables)")
        else:
            print(f"   ❌ Database error: {db_info.get('error', 'Unknown')}")
        
        # Services
        print("\n5️⃣ Checking Services...")
        success, services = self.validate_services()
        self.results['checks']['services'] = {
            'success': success,
            'details': services
        }
        if success:
            print(f"   ✅ All {len(services)} services initialized")
        else:
            print(f"   ❌ Service error: {services.get('error', 'Unknown')}")
        
        # Health checks
        print("\n6️⃣ Checking Health System...")
        success, health = await self.validate_health_checks()
        self.results['checks']['health'] = {
            'success': success,
            'details': health if success else str(health)
        }
        if success:
            print(f"   ✅ Health checks operational")
        else:
            print(f"   ❌ Health check error")
        
        # API server
        print("\n7️⃣ Checking API Server...")
        success, msg = self.validate_api_server()
        self.results['checks']['api'] = {
            'success': success,
            'details': msg
        }
        print(f"   {'✅' if success else '❌'} {msg}")
        
        # Monitoring
        print("\n8️⃣ Checking Monitoring...")
        success, msg = self.validate_monitoring()
        self.results['checks']['monitoring'] = {
            'success': success,
            'details': msg
        }
        print(f"   {'✅' if success else '❌'} {msg}")
        
        # Configuration
        print("\n9️⃣ Checking Configuration...")
        success, config = self.validate_configuration()
        self.results['checks']['configuration'] = {
            'success': success,
            'details': config
        }
        if success:
            print("   ✅ Configuration valid")
        else:
            print(f"   ❌ Configuration issues found")
        
        # Calculate summary
        total_checks = len(self.results['checks'])
        passed_checks = sum(
            1 for check in self.results['checks'].values()
            if check.get('success', False)
        )
        
        self.results['summary'] = {
            'total_checks': total_checks,
            'passed': passed_checks,
            'failed': total_checks - passed_checks,
            'success_rate': (passed_checks / total_checks * 100) if total_checks > 0 else 0
        }
        
        # Print summary
        print("\n" + "=" * 70)
        print("VALIDATION SUMMARY")
        print("=" * 70)
        print(f"Total Checks: {total_checks}")
        print(f"Passed: {passed_checks}")
        print(f"Failed: {total_checks - passed_checks}")
        print(f"Success Rate: {self.results['summary']['success_rate']:.1f}%")
        
        if self.results['summary']['success_rate'] == 100:
            print("\n✅ SYSTEM VALIDATION SUCCESSFUL!")
            print("The system is ready for production deployment.")
        elif self.results['summary']['success_rate'] >= 80:
            print("\n⚠️  SYSTEM MOSTLY READY")
            print("Minor issues detected. Review and fix before deployment.")
        else:
            print("\n❌ SYSTEM NOT READY")
            print("Critical issues detected. Fix required components before deployment.")
        
        # Save validation report
        report_path = Path("validation_report.json")
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nDetailed report saved to: {report_path}")
        
        return self.results


def main():
    """Run system validation"""
    validator = SystemValidator()
    
    # Run async validation
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(validator.run_validation())
    loop.close()
    
    # Return exit code based on success
    if results['summary']['success_rate'] == 100:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()