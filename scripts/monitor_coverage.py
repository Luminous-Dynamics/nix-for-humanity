#!/usr/bin/env python3
"""
from typing import List, Dict, Optional, Tuple
monitor_coverage.py - Automated coverage monitoring for consciousness-first testing
Part of the Nix for Humanity project's commitment to quality

This script monitors test coverage, tracks trends, and identifies gaps.
It supports both local development and CI/CD environments.
"""

import json
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Coverage thresholds
CRITICAL_PATH_THRESHOLD = 95.0  # NLP, command execution, safety
CORE_FEATURE_THRESHOLD = 90.0   # Learning, context, personality
UI_UX_THRESHOLD = 80.0          # CLI, TUI, formatting
OVERALL_THRESHOLD = 85.0        # Project-wide target

# Critical paths that need highest coverage
CRITICAL_PATHS = [
    "nix_humanity/nlp/",
    "nix_humanity/executor/",
    "nix_humanity/safety/",
    "nix_humanity/learning/bayesian_knowledge_tracing.py",
    "nix_humanity/learning/dynamic_bayesian_network.py",
]

# Core features needing high coverage
CORE_FEATURES = [
    "nix_humanity/learning/",
    "nix_humanity/context/",
    "nix_humanity/personality/",
    "nix_humanity/memory/",
]

# UI/UX components
UI_COMPONENTS = [
    "nix_humanity/cli/",
    "nix_humanity/tui/",
    "nix_humanity/formatting/",
]


class CoverageMonitor:
    """Monitor and track test coverage for consciousness-first testing."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.db_path = project_root / ".coverage_monitor" / "coverage_history.db"
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database for coverage tracking."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS coverage_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    overall_coverage REAL,
                    critical_coverage REAL,
                    core_coverage REAL,
                    ui_coverage REAL,
                    details JSON,
                    commit_hash TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS coverage_gaps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    file_path TEXT,
                    coverage_percent REAL,
                    missing_lines TEXT,
                    category TEXT
                )
            """)
    
    def run_coverage(self) -> Dict[str, any]:
        """Run coverage analysis and return results."""
        print("🧪 Running consciousness-first test coverage analysis...")
        
        # Run tests with coverage
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--cov=nix_humanity", 
             "--cov-report=json", "--cov-report=term-missing"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("❌ Tests failed! Coverage cannot be accurately measured.")
            print(result.stderr)
            return None
            
        # Parse coverage results
        coverage_file = Path("coverage.json")
        if not coverage_file.exists():
            print("❌ Coverage file not found!")
            return None
            
        with open(coverage_file) as f:
            coverage_data = json.load(f)
            
        return self._analyze_coverage(coverage_data)
    
    def _analyze_coverage(self, coverage_data: Dict) -> Dict[str, any]:
        """Analyze coverage data and categorize by component."""
        results = {
            "overall": coverage_data["totals"]["percent_covered"],
            "critical": 0.0,
            "core": 0.0,
            "ui": 0.0,
            "gaps": [],
            "timestamp": datetime.now().isoformat(),
            "commit": self._get_commit_hash()
        }
        
        # Analyze by category
        critical_stats = self._get_category_coverage(coverage_data, CRITICAL_PATHS)
        core_stats = self._get_category_coverage(coverage_data, CORE_FEATURES)
        ui_stats = self._get_category_coverage(coverage_data, UI_COMPONENTS)
        
        results["critical"] = critical_stats["percent"]
        results["core"] = core_stats["percent"]
        results["ui"] = ui_stats["percent"]
        
        # Find gaps
        for file_path, file_data in coverage_data["files"].items():
            coverage_percent = file_data["summary"]["percent_covered"]
            
            # Determine category and threshold
            category, threshold = self._categorize_file(file_path)
            
            if coverage_percent < threshold:
                results["gaps"].append({
                    "file": file_path,
                    "coverage": coverage_percent,
                    "threshold": threshold,
                    "category": category,
                    "missing_lines": file_data["missing_lines"]
                })
        
        return results
    
    def _get_category_coverage(self, coverage_data: Dict, paths: List[str]) -> Dict:
        """Calculate coverage for a category of paths."""
        total_statements = 0
        covered_statements = 0
        
        for file_path, file_data in coverage_data["files"].items():
            if any(path in file_path for path in paths):
                total_statements += file_data["summary"]["num_statements"]
                covered_statements += file_data["summary"]["covered_statements"]
        
        if total_statements == 0:
            return {"percent": 100.0, "statements": 0}
            
        return {
            "percent": (covered_statements / total_statements) * 100,
            "statements": total_statements,
            "covered": covered_statements
        }
    
    def _categorize_file(self, file_path: str) -> Tuple[str, float]:
        """Categorize a file and return its coverage threshold."""
        if any(path in file_path for path in CRITICAL_PATHS):
            return ("critical", CRITICAL_PATH_THRESHOLD)
        elif any(path in file_path for path in CORE_FEATURES):
            return ("core", CORE_FEATURE_THRESHOLD)
        elif any(path in file_path for path in UI_COMPONENTS):
            return ("ui", UI_UX_THRESHOLD)
        else:
            return ("other", OVERALL_THRESHOLD)
    
    def _get_commit_hash(self) -> Optional[str]:
        """Get current git commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except Exception:
            return None
    
    def save_results(self, results: Dict):
        """Save coverage results to database."""
        with sqlite3.connect(self.db_path) as conn:
            # Save overall results
            conn.execute("""
                INSERT INTO coverage_history 
                (overall_coverage, critical_coverage, core_coverage, 
                 ui_coverage, details, commit_hash)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                results["overall"],
                results["critical"],
                results["core"],
                results["ui"],
                json.dumps(results),
                results["commit"]
            ))
            
            # Save gaps
            for gap in results["gaps"]:
                conn.execute("""
                    INSERT INTO coverage_gaps
                    (file_path, coverage_percent, missing_lines, category)
                    VALUES (?, ?, ?, ?)
                """, (
                    gap["file"],
                    gap["coverage"],
                    json.dumps(gap["missing_lines"]),
                    gap["category"]
                ))
    
    def check_thresholds(self, results: Dict) -> bool:
        """Check if coverage meets all thresholds."""
        checks = [
            ("Overall", results["overall"], OVERALL_THRESHOLD),
            ("Critical Paths", results["critical"], CRITICAL_PATH_THRESHOLD),
            ("Core Features", results["core"], CORE_FEATURE_THRESHOLD),
            ("UI/UX", results["ui"], UI_UX_THRESHOLD)
        ]
        
        all_passed = True
        print("\n📊 Coverage Threshold Checks:")
        
        for name, actual, threshold in checks:
            if actual >= threshold:
                print(f"  ✅ {name}: {actual:.1f}% (threshold: {threshold}%)")
            else:
                print(f"  ❌ {name}: {actual:.1f}% (threshold: {threshold}%)")
                all_passed = False
        
        return all_passed
    
    def show_gaps(self, results: Dict):
        """Display coverage gaps that need attention."""
        if not results["gaps"]:
            print("\n✨ No coverage gaps found! Excellent work!")
            return
            
        print("\n⚠️  Coverage Gaps to Address:")
        
        # Group by category
        gaps_by_category = {}
        for gap in results["gaps"]:
            category = gap["category"]
            if category not in gaps_by_category:
                gaps_by_category[category] = []
            gaps_by_category[category].append(gap)
        
        # Display by priority
        for category in ["critical", "core", "ui", "other"]:
            if category in gaps_by_category:
                print(f"\n  {category.upper()} Components:")
                for gap in sorted(gaps_by_category[category], 
                                key=lambda x: x["coverage"]):
                    print(f"    • {gap['file']}: {gap['coverage']:.1f}% "
                          f"(needs {gap['threshold']:.0f}%)")
                    if gap["missing_lines"]:
                        print(f"      Missing lines: {len(gap['missing_lines'])}")
    
    def show_trends(self):
        """Display coverage trends over time."""
        with sqlite3.connect(self.db_path) as conn:
            # Get last 10 coverage reports
            cursor = conn.execute("""
                SELECT timestamp, overall_coverage, critical_coverage,
                       core_coverage, ui_coverage
                FROM coverage_history
                ORDER BY timestamp DESC
                LIMIT 10
            """)
            
            rows = cursor.fetchall()
            if len(rows) < 2:
                print("\n📈 Not enough data for trends yet.")
                return
                
            print("\n📈 Coverage Trends (last 10 runs):")
            
            # Show latest vs previous
            latest = rows[0]
            previous = rows[1]
            
            trends = [
                ("Overall", latest[1], previous[1]),
                ("Critical", latest[2], previous[2]),
                ("Core", latest[3], previous[3]),
                ("UI/UX", latest[4], previous[4])
            ]
            
            for name, current, prev in trends:
                delta = current - prev
                if delta > 0:
                    symbol = "📈"
                    change = f"+{delta:.1f}%"
                elif delta < 0:
                    symbol = "📉"
                    change = f"{delta:.1f}%"
                else:
                    symbol = "➡️"
                    change = "no change"
                    
                print(f"  {symbol} {name}: {current:.1f}% ({change})")
    
    def generate_report(self, results: Dict, output_file: Optional[Path] = None):
        """Generate detailed coverage report."""
        report = []
        report.append("# 🧪 Consciousness-First Testing Coverage Report")
        report.append(f"\nGenerated: {results['timestamp']}")
        if results['commit']:
            report.append(f"Commit: {results['commit'][:8]}")
        
        # Summary
        report.append("\n## Summary")
        report.append(f"- **Overall Coverage**: {results['overall']:.1f}%")
        report.append(f"- **Critical Paths**: {results['critical']:.1f}%")
        report.append(f"- **Core Features**: {results['core']:.1f}%")
        report.append(f"- **UI/UX Components**: {results['ui']:.1f}%")
        
        # Threshold status
        report.append("\n## Threshold Compliance")
        all_passed = self.check_thresholds(results)
        
        # Gaps
        if results["gaps"]:
            report.append("\n## Coverage Gaps")
            
            critical_gaps = [g for g in results["gaps"] if g["category"] == "critical"]
            if critical_gaps:
                report.append("\n### 🚨 Critical Gaps (Must Fix)")
                for gap in critical_gaps:
                    report.append(f"- `{gap['file']}`: {gap['coverage']:.1f}% "
                                f"(needs {gap['threshold']:.0f}%)")
            
            other_gaps = [g for g in results["gaps"] if g["category"] != "critical"]
            if other_gaps:
                report.append("\n### ⚠️  Other Gaps")
                for gap in other_gaps:
                    report.append(f"- `{gap['file']}`: {gap['coverage']:.1f}% "
                                f"(needs {gap['threshold']:.0f}%)")
        
        # Recommendations
        report.append("\n## Recommendations")
        if all_passed:
            report.append("✅ All coverage thresholds met! Continue maintaining high standards.")
        else:
            report.append("### Immediate Actions:")
            if results["critical"] < CRITICAL_PATH_THRESHOLD:
                report.append("1. **Focus on critical paths** - These are safety-critical components")
            if results["core"] < CORE_FEATURE_THRESHOLD:
                report.append("2. **Improve core feature coverage** - Essential for reliability")
            if results["overall"] < OVERALL_THRESHOLD:
                report.append("3. **Increase overall coverage** - Aim for comprehensive testing")
        
        # Write report
        report_text = "\n".join(report)
        
        if output_file:
            output_file.write_text(report_text)
            print(f"\n📄 Detailed report saved to: {output_file}")
        else:
            print("\n" + report_text)
        
        return all_passed


def main():
    """Main entry point for coverage monitoring."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Monitor test coverage for consciousness-first testing"
    )
    parser.add_argument(
        "--threshold-only", 
        action="store_true",
        help="Only check thresholds, don't run tests"
    )
    parser.add_argument(
        "--trends",
        action="store_true",
        help="Show coverage trends over time"
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Generate detailed report to file"
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI mode - fail if thresholds not met"
    )
    
    args = parser.parse_args()
    
    # Find project root
    project_root = Path(__file__).parent.parent
    monitor = CoverageMonitor(project_root)
    
    # Show trends if requested
    if args.trends:
        monitor.show_trends()
        return
    
    # Run coverage analysis
    results = monitor.run_coverage()
    if not results:
        sys.exit(1)
    
    # Save results
    monitor.save_results(results)
    
    # Check thresholds
    all_passed = monitor.check_thresholds(results)
    
    # Show gaps
    monitor.show_gaps(results)
    
    # Show trends
    monitor.show_trends()
    
    # Generate report if requested
    if args.report:
        monitor.generate_report(results, args.report)
    
    # Exit with appropriate code for CI
    if args.ci and not all_passed:
        print("\n❌ Coverage thresholds not met!")
        sys.exit(1)
    
    print("\n✨ Coverage monitoring complete!")


if __name__ == "__main__":
    main()