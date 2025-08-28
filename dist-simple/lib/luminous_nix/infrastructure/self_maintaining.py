"""
Self-Maintaining Infrastructure for Luminous Nix
Automated testing, self-healing, and predictive optimization
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, Callable
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import psutil
import numpy as np
from pathlib import Path
import json
import traceback
import subprocess
import sys

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """System health status levels"""
    EXCELLENT = "excellent"   # All metrics optimal
    GOOD = "good"            # Minor issues, self-healing
    DEGRADED = "degraded"    # Performance issues
    CRITICAL = "critical"    # Needs intervention
    FAILED = "failed"        # System failure


class ResourceType(Enum):
    """System resource types"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    PROCESS = "process"


class RecoveryStrategy(Enum):
    """Self-healing recovery strategies"""
    RESTART = "restart"           # Restart component
    ROLLBACK = "rollback"         # Rollback to previous version
    CACHE_CLEAR = "cache_clear"   # Clear caches
    MEMORY_RELEASE = "memory_release"  # Release memory
    REINDEX = "reindex"          # Rebuild indexes
    REPAIR = "repair"            # Run repair procedures
    ESCALATE = "escalate"        # Escalate to user


@dataclass
class SystemMetrics:
    """Current system metrics snapshot"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    response_time_ms: float
    error_rate: float
    throughput: float
    active_users: int
    health_score: float = 0.0  # Calculated
    
    def calculate_health_score(self) -> float:
        """Calculate overall health score (0-100)"""
        score = 100.0
        
        # CPU penalty
        if self.cpu_percent > 80:
            score -= (self.cpu_percent - 80) * 0.5
        
        # Memory penalty
        if self.memory_percent > 85:
            score -= (self.memory_percent - 85) * 0.8
        
        # Disk penalty
        if self.disk_percent > 90:
            score -= (self.disk_percent - 90) * 1.0
        
        # Response time penalty
        if self.response_time_ms > 1000:
            score -= min((self.response_time_ms - 1000) / 100, 20)
        
        # Error rate penalty
        score -= self.error_rate * 100
        
        self.health_score = max(0, min(100, score))
        return self.health_score


@dataclass
class HealthIssue:
    """Represents a detected health issue"""
    issue_id: str
    component: str
    severity: HealthStatus
    description: str
    detected_at: datetime
    metrics: SystemMetrics
    suggested_recovery: RecoveryStrategy
    auto_recoverable: bool = True
    recovery_attempts: int = 0
    resolved_at: Optional[datetime] = None
    resolution: Optional[str] = None


@dataclass
class TestResult:
    """Result of an automated test"""
    test_name: str
    passed: bool
    duration_ms: float
    timestamp: datetime
    error_message: Optional[str] = None
    coverage: Optional[float] = None
    performance_regression: bool = False


class SelfHealingEngine:
    """Automatic error recovery and system repair"""
    
    def __init__(self):
        self.issues: Dict[str, HealthIssue] = {}
        self.recovery_history: List[Dict[str, Any]] = []
        self.recovery_rules: Dict[str, Callable] = {}
        
        # Register default recovery strategies
        self._register_default_strategies()
        
    def _register_default_strategies(self):
        """Register default recovery strategies"""
        self.recovery_rules = {
            RecoveryStrategy.RESTART: self._restart_component,
            RecoveryStrategy.ROLLBACK: self._rollback_version,
            RecoveryStrategy.CACHE_CLEAR: self._clear_caches,
            RecoveryStrategy.MEMORY_RELEASE: self._release_memory,
            RecoveryStrategy.REINDEX: self._rebuild_indexes,
            RecoveryStrategy.REPAIR: self._run_repair,
            RecoveryStrategy.ESCALATE: self._escalate_to_user
        }
    
    async def diagnose_issue(self, metrics: SystemMetrics, component: str) -> Optional[HealthIssue]:
        """Diagnose health issues from metrics"""
        issues = []
        
        # High CPU usage
        if metrics.cpu_percent > 90:
            issues.append(HealthIssue(
                issue_id=f"cpu_{datetime.now().timestamp()}",
                component=component,
                severity=HealthStatus.CRITICAL if metrics.cpu_percent > 95 else HealthStatus.DEGRADED,
                description=f"High CPU usage: {metrics.cpu_percent:.1f}%",
                detected_at=datetime.now(),
                metrics=metrics,
                suggested_recovery=RecoveryStrategy.RESTART,
                auto_recoverable=True
            ))
        
        # Memory leak detection
        if metrics.memory_percent > 85:
            issues.append(HealthIssue(
                issue_id=f"memory_{datetime.now().timestamp()}",
                component=component,
                severity=HealthStatus.CRITICAL if metrics.memory_percent > 95 else HealthStatus.DEGRADED,
                description=f"High memory usage: {metrics.memory_percent:.1f}%",
                detected_at=datetime.now(),
                metrics=metrics,
                suggested_recovery=RecoveryStrategy.MEMORY_RELEASE,
                auto_recoverable=True
            ))
        
        # Disk space
        if metrics.disk_percent > 90:
            issues.append(HealthIssue(
                issue_id=f"disk_{datetime.now().timestamp()}",
                component=component,
                severity=HealthStatus.CRITICAL,
                description=f"Low disk space: {100-metrics.disk_percent:.1f}% free",
                detected_at=datetime.now(),
                metrics=metrics,
                suggested_recovery=RecoveryStrategy.CACHE_CLEAR,
                auto_recoverable=True
            ))
        
        # Response time degradation
        if metrics.response_time_ms > 2000:
            issues.append(HealthIssue(
                issue_id=f"performance_{datetime.now().timestamp()}",
                component=component,
                severity=HealthStatus.DEGRADED,
                description=f"Slow response time: {metrics.response_time_ms:.0f}ms",
                detected_at=datetime.now(),
                metrics=metrics,
                suggested_recovery=RecoveryStrategy.REINDEX,
                auto_recoverable=True
            ))
        
        # High error rate
        if metrics.error_rate > 0.05:  # >5% errors
            issues.append(HealthIssue(
                issue_id=f"errors_{datetime.now().timestamp()}",
                component=component,
                severity=HealthStatus.CRITICAL if metrics.error_rate > 0.1 else HealthStatus.DEGRADED,
                description=f"High error rate: {metrics.error_rate*100:.1f}%",
                detected_at=datetime.now(),
                metrics=metrics,
                suggested_recovery=RecoveryStrategy.ROLLBACK,
                auto_recoverable=False  # Requires investigation
            ))
        
        # Store issues
        for issue in issues:
            self.issues[issue.issue_id] = issue
        
        return issues[0] if issues else None
    
    async def attempt_recovery(self, issue: HealthIssue) -> bool:
        """Attempt automatic recovery for an issue"""
        if not issue.auto_recoverable:
            logger.warning(f"Issue {issue.issue_id} requires manual intervention")
            await self._escalate_to_user(issue)
            return False
        
        if issue.recovery_attempts >= 3:
            logger.error(f"Max recovery attempts reached for {issue.issue_id}")
            issue.auto_recoverable = False
            await self._escalate_to_user(issue)
            return False
        
        issue.recovery_attempts += 1
        strategy = issue.suggested_recovery
        
        logger.info(f"Attempting {strategy.value} recovery for {issue.issue_id}")
        
        # Execute recovery strategy
        recovery_func = self.recovery_rules.get(strategy)
        if recovery_func:
            success = await recovery_func(issue)
            
            if success:
                issue.resolved_at = datetime.now()
                issue.resolution = f"Auto-recovered using {strategy.value}"
                logger.info(f"Successfully recovered from {issue.issue_id}")
                
                # Record recovery
                self.recovery_history.append({
                    'issue_id': issue.issue_id,
                    'strategy': strategy.value,
                    'timestamp': datetime.now().isoformat(),
                    'attempts': issue.recovery_attempts,
                    'success': True
                })
                
                return True
        
        return False
    
    async def _restart_component(self, issue: HealthIssue) -> bool:
        """Restart a system component"""
        try:
            component = issue.component
            logger.info(f"Restarting {component}")
            
            # Simulated restart
            # In production, would use systemctl or process management
            await asyncio.sleep(2)
            
            return True
        except Exception as e:
            logger.error(f"Failed to restart component: {e}")
            return False
    
    async def _rollback_version(self, issue: HealthIssue) -> bool:
        """Rollback to previous version"""
        try:
            logger.info("Initiating rollback to previous version")
            
            # In production: git checkout previous version or nix rollback
            # Simulated rollback
            await asyncio.sleep(3)
            
            return True
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    async def _clear_caches(self, issue: HealthIssue) -> bool:
        """Clear system caches"""
        try:
            cache_dirs = [
                Path.home() / ".cache/luminous-nix",
                Path("/tmp/luminous-cache")
            ]
            
            for cache_dir in cache_dirs:
                if cache_dir.exists():
                    for file in cache_dir.glob("*"):
                        file.unlink()
            
            logger.info("Caches cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Cache clearing failed: {e}")
            return False
    
    async def _release_memory(self, issue: HealthIssue) -> bool:
        """Release unused memory"""
        try:
            import gc
            gc.collect()
            
            # Clear any in-memory caches
            # This would be component-specific in production
            
            logger.info("Memory released")
            return True
        except Exception as e:
            logger.error(f"Memory release failed: {e}")
            return False
    
    async def _rebuild_indexes(self, issue: HealthIssue) -> bool:
        """Rebuild database indexes"""
        try:
            logger.info("Rebuilding indexes")
            
            # In production: rebuild actual database indexes
            await asyncio.sleep(2)
            
            return True
        except Exception as e:
            logger.error(f"Index rebuild failed: {e}")
            return False
    
    async def _run_repair(self, issue: HealthIssue) -> bool:
        """Run repair procedures"""
        try:
            logger.info("Running repair procedures")
            
            # Component-specific repair logic
            await asyncio.sleep(2)
            
            return True
        except Exception as e:
            logger.error(f"Repair failed: {e}")
            return False
    
    async def _escalate_to_user(self, issue: HealthIssue) -> bool:
        """Escalate issue to user"""
        logger.warning(f"""
        ⚠️ MANUAL INTERVENTION REQUIRED
        
        Issue: {issue.description}
        Component: {issue.component}
        Severity: {issue.severity.value}
        Detected: {issue.detected_at}
        Attempts: {issue.recovery_attempts}
        
        Suggested action: {issue.suggested_recovery.value}
        """)
        return False


class PredictiveOptimizer:
    """Predictive performance optimization based on patterns"""
    
    def __init__(self):
        self.metrics_history: List[SystemMetrics] = []
        self.patterns: Dict[str, List[float]] = {}
        self.predictions: Dict[str, float] = {}
        self.optimization_history: List[Dict[str, Any]] = []
        
    def record_metrics(self, metrics: SystemMetrics):
        """Record metrics for pattern analysis"""
        self.metrics_history.append(metrics)
        
        # Keep last 1000 metrics
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
    
    def predict_resource_needs(self, horizon_minutes: int = 30) -> Dict[str, float]:
        """Predict resource needs for the next N minutes"""
        if len(self.metrics_history) < 10:
            return {}
        
        predictions = {}
        
        # Simple moving average prediction
        # In production, use ARIMA or neural networks
        recent = self.metrics_history[-10:]
        
        predictions['cpu'] = np.mean([m.cpu_percent for m in recent]) * 1.1
        predictions['memory'] = np.mean([m.memory_percent for m in recent]) * 1.05
        predictions['disk'] = self.metrics_history[-1].disk_percent  # Disk changes slowly
        predictions['response_time'] = np.mean([m.response_time_ms for m in recent])
        
        # Detect trends
        if len(self.metrics_history) >= 30:
            cpu_trend = self._calculate_trend([m.cpu_percent for m in self.metrics_history[-30:]])
            memory_trend = self._calculate_trend([m.memory_percent for m in self.metrics_history[-30:]])
            
            # Adjust predictions based on trends
            predictions['cpu'] += cpu_trend * horizon_minutes
            predictions['memory'] += memory_trend * horizon_minutes
        
        self.predictions = predictions
        return predictions
    
    def suggest_optimizations(self) -> List[Dict[str, Any]]:
        """Suggest performance optimizations based on patterns"""
        suggestions = []
        
        if not self.predictions:
            return suggestions
        
        # High CPU prediction
        if self.predictions.get('cpu', 0) > 80:
            suggestions.append({
                'type': 'resource_scaling',
                'resource': 'cpu',
                'action': 'increase_workers',
                'reason': f"CPU usage predicted to reach {self.predictions['cpu']:.1f}%",
                'confidence': 0.8
            })
        
        # Memory pressure
        if self.predictions.get('memory', 0) > 85:
            suggestions.append({
                'type': 'memory_optimization',
                'resource': 'memory',
                'action': 'enable_gc_aggressive',
                'reason': f"Memory usage predicted to reach {self.predictions['memory']:.1f}%",
                'confidence': 0.75
            })
        
        # Response time degradation
        if self.predictions.get('response_time', 0) > 1500:
            suggestions.append({
                'type': 'performance_tuning',
                'resource': 'response_time',
                'action': 'enable_caching',
                'reason': f"Response time predicted at {self.predictions['response_time']:.0f}ms",
                'confidence': 0.7
            })
        
        return suggestions
    
    async def apply_optimization(self, optimization: Dict[str, Any]) -> bool:
        """Apply a suggested optimization"""
        try:
            opt_type = optimization['type']
            action = optimization['action']
            
            logger.info(f"Applying optimization: {action}")
            
            if action == 'increase_workers':
                # Increase worker processes
                # In production: adjust process pool size
                pass
            
            elif action == 'enable_gc_aggressive':
                # Enable aggressive garbage collection
                import gc
                gc.set_threshold(100, 5, 5)
            
            elif action == 'enable_caching':
                # Enable additional caching layers
                # In production: configure cache settings
                pass
            
            # Record optimization
            self.optimization_history.append({
                'timestamp': datetime.now().isoformat(),
                'optimization': optimization,
                'applied': True
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply optimization: {e}")
            return False
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend in values (rate of change)"""
        if len(values) < 2:
            return 0.0
        
        x = np.arange(len(values))
        y = np.array(values)
        
        # Simple linear regression
        A = np.vstack([x, np.ones(len(x))]).T
        m, c = np.linalg.lstsq(A, y, rcond=None)[0]
        
        return m  # Slope represents trend


class AutomatedTestRunner:
    """Automated testing and CI/CD pipeline"""
    
    def __init__(self):
        self.test_suites: Dict[str, List[Callable]] = {}
        self.test_results: List[TestResult] = []
        self.performance_baseline: Dict[str, float] = {}
        
    def register_test_suite(self, name: str, tests: List[Callable]):
        """Register a test suite"""
        self.test_suites[name] = tests
    
    async def run_test_suite(self, suite_name: str) -> List[TestResult]:
        """Run a specific test suite"""
        if suite_name not in self.test_suites:
            logger.error(f"Test suite {suite_name} not found")
            return []
        
        results = []
        tests = self.test_suites[suite_name]
        
        for test in tests:
            result = await self._run_single_test(test)
            results.append(result)
            self.test_results.append(result)
        
        return results
    
    async def _run_single_test(self, test: Callable) -> TestResult:
        """Run a single test"""
        test_name = test.__name__
        start_time = datetime.now()
        
        try:
            # Run test
            await test() if asyncio.iscoroutinefunction(test) else test()
            
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            # Check for performance regression
            regression = False
            if test_name in self.performance_baseline:
                baseline = self.performance_baseline[test_name]
                if duration > baseline * 1.2:  # 20% slower
                    regression = True
            
            return TestResult(
                test_name=test_name,
                passed=True,
                duration_ms=duration,
                timestamp=datetime.now(),
                performance_regression=regression
            )
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            return TestResult(
                test_name=test_name,
                passed=False,
                duration_ms=duration,
                timestamp=datetime.now(),
                error_message=str(e)
            )
    
    async def run_continuous_tests(self, interval_seconds: int = 300):
        """Run tests continuously at specified interval"""
        while True:
            for suite_name in self.test_suites.keys():
                results = await self.run_test_suite(suite_name)
                
                # Alert on failures
                failures = [r for r in results if not r.passed]
                if failures:
                    logger.error(f"Test failures in {suite_name}: {len(failures)}")
                    for failure in failures:
                        logger.error(f"  - {failure.test_name}: {failure.error_message}")
            
            await asyncio.sleep(interval_seconds)
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of test results"""
        if not self.test_results:
            return {'total': 0, 'passed': 0, 'failed': 0, 'pass_rate': 0}
        
        recent = self.test_results[-100:]  # Last 100 tests
        
        return {
            'total': len(recent),
            'passed': sum(1 for r in recent if r.passed),
            'failed': sum(1 for r in recent if not r.passed),
            'pass_rate': sum(1 for r in recent if r.passed) / len(recent),
            'avg_duration_ms': np.mean([r.duration_ms for r in recent]),
            'regressions': sum(1 for r in recent if r.performance_regression)
        }


class SelfMaintainingInfrastructure:
    """
    Main coordinator for self-maintaining infrastructure
    Combines monitoring, healing, optimization, and testing
    """
    
    def __init__(self):
        self.healing_engine = SelfHealingEngine()
        self.optimizer = PredictiveOptimizer()
        self.test_runner = AutomatedTestRunner()
        
        self.monitoring_active = False
        self.health_status = HealthStatus.GOOD
        self.last_check = datetime.now()
        
        # Metrics collection
        self.current_metrics: Optional[SystemMetrics] = None
        
        # Configuration
        self.check_interval = 30  # seconds
        self.optimization_threshold = 0.7  # Apply optimizations above this confidence
        
    async def start_monitoring(self):
        """Start continuous system monitoring"""
        self.monitoring_active = True
        logger.info("Self-maintaining infrastructure started")
        
        # Start monitoring loop
        asyncio.create_task(self._monitoring_loop())
        
        # Start continuous testing
        asyncio.create_task(self.test_runner.run_continuous_tests())
    
    async def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring_active = False
        logger.info("Self-maintaining infrastructure stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect metrics
                metrics = await self._collect_metrics()
                self.current_metrics = metrics
                
                # Record for prediction
                self.optimizer.record_metrics(metrics)
                
                # Calculate health
                health_score = metrics.calculate_health_score()
                self._update_health_status(health_score)
                
                # Diagnose issues
                issue = await self.healing_engine.diagnose_issue(metrics, "system")
                
                if issue:
                    # Attempt self-healing
                    success = await self.healing_engine.attempt_recovery(issue)
                    if not success:
                        self.health_status = HealthStatus.DEGRADED
                
                # Predictive optimization
                predictions = self.optimizer.predict_resource_needs()
                optimizations = self.optimizer.suggest_optimizations()
                
                for opt in optimizations:
                    if opt['confidence'] >= self.optimization_threshold:
                        await self.optimizer.apply_optimization(opt)
                
                self.last_check = datetime.now()
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                
            await asyncio.sleep(self.check_interval)
    
    async def _collect_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Simulated application metrics
        # In production, collect from actual application
        response_time = np.random.normal(200, 50)  # ms
        error_rate = np.random.exponential(0.01)  # errors
        throughput = np.random.normal(100, 20)  # requests/sec
        active_users = np.random.poisson(10)
        
        return SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_percent=disk.percent,
            response_time_ms=max(0, response_time),
            error_rate=min(1.0, error_rate),
            throughput=max(0, throughput),
            active_users=active_users
        )
    
    def _update_health_status(self, health_score: float):
        """Update overall health status"""
        if health_score >= 90:
            self.health_status = HealthStatus.EXCELLENT
        elif health_score >= 75:
            self.health_status = HealthStatus.GOOD
        elif health_score >= 50:
            self.health_status = HealthStatus.DEGRADED
        elif health_score >= 25:
            self.health_status = HealthStatus.CRITICAL
        else:
            self.health_status = HealthStatus.FAILED
    
    def get_infrastructure_status(self) -> Dict[str, Any]:
        """Get current infrastructure status"""
        return {
            'health_status': self.health_status.value,
            'last_check': self.last_check.isoformat(),
            'monitoring_active': self.monitoring_active,
            'current_metrics': {
                'cpu': self.current_metrics.cpu_percent if self.current_metrics else 0,
                'memory': self.current_metrics.memory_percent if self.current_metrics else 0,
                'disk': self.current_metrics.disk_percent if self.current_metrics else 0,
                'health_score': self.current_metrics.health_score if self.current_metrics else 0
            },
            'active_issues': len([i for i in self.healing_engine.issues.values() 
                                if not i.resolved_at]),
            'recoveries_performed': len(self.healing_engine.recovery_history),
            'optimizations_applied': len(self.optimizer.optimization_history),
            'test_summary': self.test_runner.get_test_summary(),
            'predictions': self.optimizer.predictions
        }


# Example test functions for automated testing
def test_basic_functionality():
    """Test basic system functionality"""
    assert True  # Placeholder
    
def test_performance():
    """Test system performance"""
    import time
    start = time.time()
    # Simulate work
    time.sleep(0.1)
    duration = time.time() - start
    assert duration < 0.2  # Should complete in 200ms

async def test_async_operation():
    """Test async operations"""
    await asyncio.sleep(0.05)
    assert True


# Demo
async def demo_self_maintaining():
    """Demonstrate self-maintaining infrastructure"""
    
    # Initialize infrastructure
    infra = SelfMaintainingInfrastructure()
    
    # Register test suites
    infra.test_runner.register_test_suite("basic", [
        test_basic_functionality,
        test_performance,
        test_async_operation
    ])
    
    # Start monitoring
    await infra.start_monitoring()
    
    # Let it run for a bit
    await asyncio.sleep(5)
    
    # Check status
    status = infra.get_infrastructure_status()
    print(f"Infrastructure status: {json.dumps(status, indent=2)}")
    
    # Stop monitoring
    await infra.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(demo_self_maintaining())