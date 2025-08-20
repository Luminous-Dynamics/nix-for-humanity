#!/usr/bin/env python3
"""
from typing import List, Dict, Optional
Automated Coverage Monitoring System - Nix for Humanity

This script provides comprehensive coverage monitoring and reporting for the
Testing Foundation. It tracks progress toward the 95% coverage goal and
provides detailed analysis of coverage trends.

Part of the Testing Foundation excellence initiative.
"""

import os
import sys
import json
import time
import sqlite3
import subprocess
import argparse
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from xml.etree import ElementTree as ET

@dataclass
class CoverageMetrics:
    """Coverage metrics for a specific timestamp."""
    timestamp: str
    overall_coverage: float
    lines_covered: int
    lines_total: int
    components: Dict[str, float]
    critical_paths: Dict[str, float]
    target_progress: float  # Progress toward 95% goal

@dataclass
class CoverageReport:
    """Complete coverage analysis report."""
    current_metrics: CoverageMetrics
    trend_analysis: Dict[str, Any]
    recommendations: List[str]
    alerts: List[str]
    milestone_progress: Dict[str, float]

class CoverageMonitor:
    """Automated coverage monitoring and analysis system."""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.db_path = self.project_root / ".coverage_monitor" / "coverage_history.db"
        self.reports_dir = self.project_root / ".coverage_monitor" / "reports"
        
        # Ensure directories exist
        self.db_path.parent.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Coverage targets
        self.TARGET_OVERALL = 95.0
        self.TARGET_CRITICAL = 95.0
        self.TARGET_CORE = 90.0
        self.TARGET_UI = 80.0
        
        # Component mapping
        self.COMPONENTS = {
            "nlp": ["src/nlp/", "luminous_nix/nlp/"],
            "command_executor": ["src/executor/", "luminous_nix/executor/"],
            "cli": ["src/cli/", "bin/", "luminous_nix/cli/"],
            "backend": ["src/backend/", "luminous_nix/backend/"],
            "learning": ["src/learning/", "luminous_nix/learning/"],
            "security": ["src/security/", "luminous_nix/security/"],
            "ui": ["src/ui/", "src/tui/", "luminous_nix/ui/"]
        }
        
        # Critical paths (must meet 95% target)
        self.CRITICAL_PATHS = [
            "luminous_nix/nlp/intent_recognition.py",
            "luminous_nix/executor/command_executor.py",
            "luminous_nix/security/input_validator.py",
            "luminous_nix/backend/native_api.py"
        ]
    
    def _init_database(self):
        """Initialize SQLite database for coverage tracking."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS coverage_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    overall_coverage REAL NOT NULL,
                    lines_covered INTEGER NOT NULL,
                    lines_total INTEGER NOT NULL,
                    components TEXT NOT NULL,
                    critical_paths TEXT NOT NULL,
                    target_progress REAL NOT NULL,
                    git_commit TEXT,
                    git_branch TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS coverage_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    component TEXT,
                    message TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    resolved BOOLEAN DEFAULT FALSE
                )
            """)
    
    def run_coverage_analysis(self, skip_tests: bool = False) -> Optional[CoverageMetrics]:
        """Run comprehensive coverage analysis."""
        if skip_tests:
            print("📊 Parsing existing coverage data...")
            # Parse existing coverage results
            if not self._coverage_files_exist():
                print("⚠️ No existing coverage files found. Run tests first with:")
                print("   python -m pytest --cov=luminous_nix --cov-report=xml --cov-report=json")
                return None
            return self._parse_coverage_results()
        
        print("🔍 Running coverage analysis with tests...")
        
        try:
            # Run tests with coverage (optimized for speed)
            result = subprocess.run([
                "python", "-m", "pytest", 
                "--cov=luminous_nix",
                "--cov-report=xml",
                "--cov-report=json",
                "--cov-report=html:htmlcov",
                "-x",  # Stop on first failure
                "--tb=short",  # Short traceback format
                "tests/"
            ], capture_output=True, text=True, cwd=self.project_root, timeout=300)  # 5 minute timeout
            
            if result.returncode != 0:
                print(f"❌ Tests failed: {result.stderr}")
                return None
            
            # Parse coverage results
            return self._parse_coverage_results()
            
        except subprocess.TimeoutExpired:
            print("⚠️ Coverage analysis timed out after 5 minutes")
            print("💡 Try using --no-run to analyze existing coverage data")
            return None
        except Exception as e:
            print(f"❌ Coverage analysis failed: {e}")
            return None
    
    def _coverage_files_exist(self) -> bool:
        """Check if coverage files exist."""
        xml_path = self.project_root / "coverage.xml"
        json_path = self.project_root / "coverage.json"
        return xml_path.exists() or json_path.exists()
    
    def _parse_coverage_results(self) -> CoverageMetrics:
        """Parse coverage results from XML and JSON reports."""
        timestamp = datetime.datetime.now().isoformat()
        
        # Parse XML coverage report
        xml_path = self.project_root / "coverage.xml"
        if xml_path.exists():
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Overall coverage
            overall_coverage = float(root.get('line-rate', 0)) * 100
            lines_covered = int(root.get('lines-covered', 0))
            lines_total = int(root.get('lines-valid', 0))
        else:
            overall_coverage = 0.0
            lines_covered = 0
            lines_total = 0
        
        # Parse JSON for detailed component analysis
        json_path = self.project_root / "coverage.json"
        components = {}
        critical_paths = {}
        
        if json_path.exists():
            with open(json_path, 'r') as f:
                coverage_data = json.load(f)
                files_data = coverage_data.get('files', {})
                
                # Calculate component coverage
                for component, paths in self.COMPONENTS.items():
                    component_files = []
                    for file_path, file_data in files_data.items():
                        if any(path in file_path for path in paths):
                            component_files.append(file_data)
                    
                    if component_files:
                        total_covered = sum(f['summary']['covered_lines'] for f in component_files)
                        total_lines = sum(f['summary']['num_statements'] for f in component_files)
                        components[component] = (total_covered / total_lines * 100) if total_lines > 0 else 0
                    else:
                        components[component] = 0.0
                
                # Calculate critical path coverage
                for critical_path in self.CRITICAL_PATHS:
                    if critical_path in files_data:
                        file_data = files_data[critical_path]
                        covered = file_data['summary']['covered_lines']
                        total = file_data['summary']['num_statements']
                        critical_paths[critical_path] = (covered / total * 100) if total > 0 else 0
                    else:
                        critical_paths[critical_path] = 0.0
        
        # Calculate progress toward 95% target
        target_progress = (overall_coverage / self.TARGET_OVERALL) * 100
        
        return CoverageMetrics(
            timestamp=timestamp,
            overall_coverage=overall_coverage,
            lines_covered=lines_covered,
            lines_total=lines_total,
            components=components,
            critical_paths=critical_paths,
            target_progress=target_progress
        )
    
    def store_metrics(self, metrics: CoverageMetrics):
        """Store coverage metrics in database."""
        # Get git info
        git_commit = self._get_git_commit()
        git_branch = self._get_git_branch()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO coverage_history 
                (timestamp, overall_coverage, lines_covered, lines_total, 
                 components, critical_paths, target_progress, git_commit, git_branch)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.timestamp,
                metrics.overall_coverage,
                metrics.lines_covered,
                metrics.lines_total,
                json.dumps(metrics.components),
                json.dumps(metrics.critical_paths),
                metrics.target_progress,
                git_commit,
                git_branch
            ))
    
    def generate_report(self, metrics: CoverageMetrics) -> CoverageReport:
        """Generate comprehensive coverage analysis report."""
        # Analyze trends
        trend_analysis = self._analyze_trends()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metrics)
        
        # Check for alerts
        alerts = self._check_alerts(metrics)
        
        # Calculate milestone progress
        milestone_progress = {
            "overall_to_95": (metrics.overall_coverage / 95.0) * 100,
            "critical_paths_ready": sum(1 for cov in metrics.critical_paths.values() if cov >= 95.0),
            "components_at_target": sum(1 for component, cov in metrics.components.items() 
                                      if cov >= self._get_component_target(component))
        }
        
        return CoverageReport(
            current_metrics=metrics,
            trend_analysis=trend_analysis,
            recommendations=recommendations,
            alerts=alerts,
            milestone_progress=milestone_progress
        )
    
    def _analyze_trends(self) -> Dict[str, Any]:
        """Analyze coverage trends over time."""
        with sqlite3.connect(self.db_path) as conn:
            # Get last 10 measurements
            cursor = conn.execute("""
                SELECT timestamp, overall_coverage, target_progress 
                FROM coverage_history 
                ORDER BY timestamp DESC 
                LIMIT 10
            """)
            history = cursor.fetchall()
        
        if len(history) < 2:
            return {"trend": "insufficient_data", "measurements": len(history)}
        
        # Calculate trend
        recent_coverage = [row[1] for row in history[:5]]
        older_coverage = [row[1] for row in history[5:]]
        
        recent_avg = sum(recent_coverage) / len(recent_coverage)
        older_avg = sum(older_coverage) / len(older_coverage) if older_coverage else recent_avg
        
        trend_direction = "improving" if recent_avg > older_avg else "declining" if recent_avg < older_avg else "stable"
        trend_rate = abs(recent_avg - older_avg)
        
        return {
            "trend": trend_direction,
            "rate": trend_rate,
            "recent_average": recent_avg,
            "measurements": len(history),
            "velocity": self._calculate_velocity(history)
        }
    
    def _calculate_velocity(self, history: List[Tuple]) -> float:
        """Calculate coverage improvement velocity (percentage points per day)."""
        if len(history) < 2:
            return 0.0
        
        # Get first and last measurements
        latest = history[0]
        oldest = history[-1]
        
        latest_time = datetime.datetime.fromisoformat(latest[0])
        oldest_time = datetime.datetime.fromisoformat(oldest[0])
        
        time_diff = (latest_time - oldest_time).total_seconds() / 86400  # days
        coverage_diff = latest[1] - oldest[1]
        
        return coverage_diff / time_diff if time_diff > 0 else 0.0
    
    def _generate_recommendations(self, metrics: CoverageMetrics) -> List[str]:
        """Generate actionable recommendations based on current metrics."""
        recommendations = []
        
        # Overall coverage recommendations
        if metrics.overall_coverage < 70:
            recommendations.append("🚨 URGENT: Overall coverage below 70%. Focus on basic unit tests.")
        elif metrics.overall_coverage < 85:
            recommendations.append("📈 Priority: Add integration tests to reach 85% milestone.")
        elif metrics.overall_coverage < 95:
            recommendations.append("🎯 Target: Focus on edge cases and error paths to reach 95%.")
        
        # Component-specific recommendations
        for component, coverage in metrics.components.items():
            target = self._get_component_target(component)
            if coverage < target - 10:
                recommendations.append(f"⚠️ Component '{component}': {coverage:.1f}% (target: {target}%)")
            elif coverage < target:
                recommendations.append(f"📝 Component '{component}': Close to target, needs {target-coverage:.1f}% more")
        
        # Critical path recommendations
        critical_below_target = [path for path, cov in metrics.critical_paths.items() if cov < 95.0]
        if critical_below_target:
            recommendations.append(f"🔥 Critical paths need attention: {len(critical_below_target)} below 95%")
        
        # Testing strategy recommendations
        if metrics.overall_coverage > 80:
            recommendations.append("✨ Good foundation! Focus on scenario-based and integration tests.")
        
        if not recommendations:
            recommendations.append("🎉 Excellent coverage! Maintain quality and consider mutation testing.")
        
        return recommendations
    
    def _check_alerts(self, metrics: CoverageMetrics) -> List[str]:
        """Check for coverage alerts and store them."""
        alerts = []
        
        # Coverage regression alert
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT overall_coverage FROM coverage_history 
                ORDER BY timestamp DESC LIMIT 2
            """)
            recent = cursor.fetchall()
            
            if len(recent) >= 2:
                current = recent[0][0]
                previous = recent[1][0]
                
                if current < previous - 2.0:  # 2% regression threshold
                    alert = f"📉 Coverage regression: {current:.1f}% (was {previous:.1f}%)"
                    alerts.append(alert)
                    self._store_alert("regression", None, alert, "warning")
        
        # Critical path alerts
        for path, coverage in metrics.critical_paths.items():
            if coverage < 80:
                alert = f"🚨 Critical path '{path}' only {coverage:.1f}% covered"
                alerts.append(alert)
                self._store_alert("critical_low", path, alert, "critical")
            elif coverage < 95:
                alert = f"⚠️ Critical path '{path}' needs {95-coverage:.1f}% more coverage"
                alerts.append(alert)
                self._store_alert("critical_medium", path, alert, "warning")
        
        # Milestone alerts
        if metrics.target_progress < 50:
            alert = "🎯 Still far from 95% target - focus on basic unit tests"
            alerts.append(alert)
            self._store_alert("milestone", "overall", alert, "info")
        elif metrics.target_progress > 95:
            alert = "🏆 95% coverage target achieved! Consider stretch goals."
            alerts.append(alert)
            self._store_alert("milestone", "overall", alert, "success")
        
        return alerts
    
    def _store_alert(self, alert_type: str, component: Optional[str], message: str, severity: str):
        """Store alert in database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO coverage_alerts (timestamp, alert_type, component, message, severity)
                VALUES (?, ?, ?, ?, ?)
            """, (datetime.datetime.now().isoformat(), alert_type, component, message, severity))
    
    def _get_component_target(self, component: str) -> float:
        """Get coverage target for specific component."""
        critical_components = ["nlp", "command_executor", "security", "backend"]
        if component in critical_components:
            return self.TARGET_CRITICAL
        elif component in ["learning", "ui"]:
            return self.TARGET_CORE
        else:
            return self.TARGET_UI
    
    def _get_git_commit(self) -> Optional[str]:
        """Get current git commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"], 
                capture_output=True, text=True, cwd=self.project_root
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except Exception:
            return None
    
    def _get_git_branch(self) -> Optional[str]:
        """Get current git branch name."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"], 
                capture_output=True, text=True, cwd=self.project_root
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except Exception:
            return None
    
    def print_report(self, report: CoverageReport):
        """Print comprehensive coverage report to console."""
        metrics = report.current_metrics
        
        print("\n" + "="*80)
        print("📊 COVERAGE MONITORING REPORT")
        print("="*80)
        
        # Current Status
        print(f"\n🎯 CURRENT STATUS ({metrics.timestamp[:19]})")
        print("-" * 50)
        print(f"Overall Coverage:     {metrics.overall_coverage:6.2f}% (Target: 95.0%)")
        print(f"Lines Covered:        {metrics.lines_covered:6,} / {metrics.lines_total:,}")
        print(f"Target Progress:      {metrics.target_progress:6.2f}%")
        
        # Component Breakdown
        print(f"\n🧩 COMPONENT BREAKDOWN")
        print("-" * 50)
        for component, coverage in metrics.components.items():
            target = self._get_component_target(component)
            status = "✅" if coverage >= target else "⚠️" if coverage >= target - 10 else "❌"
            print(f"{status} {component:15} {coverage:6.2f}% (Target: {target:4.0f}%)")
        
        # Critical Paths
        print(f"\n🔥 CRITICAL PATHS")
        print("-" * 50)
        for path, coverage in metrics.critical_paths.items():
            status = "✅" if coverage >= 95 else "⚠️" if coverage >= 80 else "❌"
            short_path = path.split('/')[-1] if '/' in path else path
            print(f"{status} {short_path:25} {coverage:6.2f}%")
        
        # Trend Analysis
        trend = report.trend_analysis
        print(f"\n📈 TREND ANALYSIS")
        print("-" * 50)
        print(f"Trend Direction:      {trend.get('trend', 'unknown').upper()}")
        if trend.get('rate'):
            print(f"Rate of Change:       {trend['rate']:+6.2f} percentage points")
        if trend.get('velocity'):
            print(f"Velocity:            {trend['velocity']:+6.2f}%/day")
        print(f"Historical Data:      {trend.get('measurements', 0)} measurements")
        
        # Milestone Progress
        milestones = report.milestone_progress
        print(f"\n🏆 MILESTONE PROGRESS")
        print("-" * 50)
        print(f"Progress to 95%:      {milestones['overall_to_95']:6.2f}%")
        print(f"Critical Paths Ready: {milestones['critical_paths_ready']}/{len(metrics.critical_paths)}")
        print(f"Components at Target: {milestones['components_at_target']}/{len(metrics.components)}")
        
        # Recommendations
        if report.recommendations:
            print(f"\n💡 RECOMMENDATIONS")
            print("-" * 50)
            for rec in report.recommendations:
                print(f"   {rec}")
        
        # Alerts
        if report.alerts:
            print(f"\n🚨 ALERTS")
            print("-" * 50)
            for alert in report.alerts:
                print(f"   {alert}")
        
        print("\n" + "="*80)
    
    def save_report(self, report: CoverageReport):
        """Save report to JSON file."""
        timestamp = report.current_metrics.timestamp[:19].replace(':', '-')
        report_file = self.reports_dir / f"coverage_report_{timestamp}.json"
        
        # Convert to serializable format
        report_data = {
            "current_metrics": asdict(report.current_metrics),
            "trend_analysis": report.trend_analysis,
            "recommendations": report.recommendations,
            "alerts": report.alerts,
            "milestone_progress": report.milestone_progress
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"📁 Report saved to: {report_file}")
    
    def generate_html_dashboard(self, report: CoverageReport):
        """Generate HTML dashboard for coverage monitoring."""
        dashboard_file = self.reports_dir / "coverage_dashboard.html"
        
        # Get historical data for charts
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT timestamp, overall_coverage, target_progress 
                FROM coverage_history 
                ORDER BY timestamp ASC 
                LIMIT 50
            """)
            history = cursor.fetchall()
        
        # Generate HTML
        html_content = self._generate_dashboard_html(report, history)
        
        with open(dashboard_file, 'w') as f:
            f.write(html_content)
        
        print(f"📊 Dashboard saved to: {dashboard_file}")
    
    def _generate_dashboard_html(self, report: CoverageReport, history: List[Tuple]) -> str:
        """Generate HTML dashboard content."""
        metrics = report.current_metrics
        
        # Prepare chart data
        chart_data = {
            "timestamps": [h[0][:19] for h in history],
            "coverage": [h[1] for h in history],
            "target_progress": [h[2] for h in history]
        }
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nix for Humanity - Coverage Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 30px; }}
        .header h1 {{ margin: 0; font-size: 2.5em; }}
        .header p {{ margin: 10px 0 0; opacity: 0.9; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .card {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        .metric {{ text-align: center; }}
        .metric-value {{ font-size: 3em; font-weight: bold; margin: 10px 0; }}
        .metric-label {{ color: #666; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px; }}
        .progress-bar {{ background: #e1e5e9; border-radius: 10px; height: 20px; margin: 15px 0; overflow: hidden; }}
        .progress-fill {{ background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%); height: 100%; transition: width 0.3s ease; }}
        .component-list {{ list-style: none; padding: 0; }}
        .component-item {{ display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #eee; }}
        .component-item:last-child {{ border-bottom: none; }}
        .status-badge {{ padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }}
        .status-good {{ background: #d4edda; color: #155724; }}
        .status-warning {{ background: #fff3cd; color: #856404; }}
        .status-danger {{ background: #f8d7da; color: #721c24; }}
        .recommendations {{ background: #f8f9fa; border-left: 4px solid #007bff; padding: 20px; border-radius: 0 8px 8px 0; }}
        .chart-container {{ position: relative; height: 300px; margin-top: 20px; }}
        .alert {{ padding: 12px 16px; border-radius: 8px; margin: 10px 0; }}
        .alert-success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .alert-warning {{ background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }}
        .alert-danger {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
        .timestamp {{ color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 Coverage Dashboard</h1>
            <p>Nix for Humanity - Testing Foundation Excellence</p>
            <p class="timestamp">Last updated: {metrics.timestamp[:19]}</p>
        </div>
        
        <div class="grid">
            <div class="card metric">
                <div class="metric-label">Overall Coverage</div>
                <div class="metric-value" style="color: {'#28a745' if metrics.overall_coverage >= 95 else '#ffc107' if metrics.overall_coverage >= 80 else '#dc3545'}">{metrics.overall_coverage:.1f}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {metrics.overall_coverage}%"></div>
                </div>
                <small>{metrics.lines_covered:,} / {metrics.lines_total:,} lines</small>
            </div>
            
            <div class="card metric">
                <div class="metric-label">Target Progress</div>
                <div class="metric-value" style="color: {'#28a745' if metrics.target_progress >= 100 else '#007bff'}">{metrics.target_progress:.1f}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {min(metrics.target_progress, 100)}%"></div>
                </div>
                <small>Progress toward 95% goal</small>
            </div>
            
            <div class="card metric">
                <div class="metric-label">Components at Target</div>
                <div class="metric-value" style="color: #007bff">{report.milestone_progress['components_at_target']}/{len(metrics.components)}</div>
                <small>Meeting coverage targets</small>
            </div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>📊 Coverage Trend</h3>
                <div class="chart-container">
                    <canvas id="coverageChart"></canvas>
                </div>
            </div>
            
            <div class="card">
                <h3>🧩 Component Status</h3>
                <ul class="component-list">
                    {"".join([f'''
                    <li class="component-item">
                        <span>{component.replace('_', ' ').title()}</span>
                        <span>
                            <span class="status-badge {'status-good' if coverage >= self._get_component_target(component) else 'status-warning' if coverage >= self._get_component_target(component) - 10 else 'status-danger'}">{coverage:.1f}%</span>
                        </span>
                    </li>
                    ''' for component, coverage in metrics.components.items()])}
                </ul>
            </div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>🔥 Critical Paths</h3>
                <ul class="component-list">
                    {"".join([f'''
                    <li class="component-item">
                        <span>{path.split('/')[-1] if '/' in path else path}</span>
                        <span>
                            <span class="status-badge {'status-good' if coverage >= 95 else 'status-warning' if coverage >= 80 else 'status-danger'}">{coverage:.1f}%</span>
                        </span>
                    </li>
                    ''' for path, coverage in metrics.critical_paths.items()])}
                </ul>
            </div>
            
            <div class="card recommendations">
                <h3>💡 Recommendations</h3>
                {"".join([f"<p>• {rec}</p>" for rec in report.recommendations])}
            </div>
        </div>
        
        {f'''
        <div class="card">
            <h3>🚨 Active Alerts</h3>
            {"".join([f'<div class="alert {'alert-danger' if 'URGENT' in alert or '🚨' in alert else 'alert-warning' if '⚠️' in alert else 'alert-success'}">{alert}</div>' for alert in report.alerts])}
        </div>
        ''' if report.alerts else ''}
    </div>
    
    <script>
        // Coverage trend chart
        const ctx = document.getElementById('coverageChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(chart_data["timestamps"][-20:])},
                datasets: [{{
                    label: 'Coverage %',
                    data: {json.dumps(chart_data["coverage"][-20:])},
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    fill: true,
                    tension: 0.4
                }}, {{
                    label: '95% Target',
                    data: Array(20).fill(95),
                    borderColor: '#28a745',
                    borderDash: [5, 5],
                    fill: false
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
        """

def main():
    """Main entry point for coverage monitoring."""
    parser = argparse.ArgumentParser(description="Automated Coverage Monitoring for Nix for Humanity")
    parser.add_argument("--project-root", help="Project root directory", default=None)
    parser.add_argument("--no-run", action="store_true", help="Skip running tests, analyze existing results")
    parser.add_argument("--dashboard", action="store_true", help="Generate HTML dashboard")
    parser.add_argument("--save-report", action="store_true", help="Save JSON report")
    parser.add_argument("--alert-threshold", type=float, default=2.0, help="Coverage regression alert threshold")
    parser.add_argument("--init-only", action="store_true", help="Only initialize directories and database")
    
    args = parser.parse_args()
    
    # Initialize monitor
    monitor = CoverageMonitor(args.project_root)
    
    # If only initializing, just set up directories and exit
    if args.init_only:
        print("✅ Coverage monitoring initialized")
        return 0
    
    # Run coverage analysis
    metrics = monitor.run_coverage_analysis(skip_tests=args.no_run)
    if not metrics:
        print("❌ Failed to get coverage analysis")
        if args.no_run:
            print("💡 No existing coverage data found. Run without --no-run first.")
        return 1
    
    # Store metrics
    monitor.store_metrics(metrics)
    
    # Generate comprehensive report
    report = monitor.generate_report(metrics)
    
    # Print report to console
    monitor.print_report(report)
    
    # Save report if requested
    if args.save_report:
        monitor.save_report(report)
    
    # Generate dashboard if requested
    if args.dashboard:
        monitor.generate_html_dashboard(report)
    
    # Return appropriate exit code
    if report.alerts and any("🚨" in alert for alert in report.alerts):
        return 1  # Critical alerts present
    
    return 0

if __name__ == "__main__":
    exit(main())