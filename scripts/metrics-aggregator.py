#!/usr/bin/env python3
"""
from typing import List
Metrics Aggregator - Combines all project metrics into executive summary
Provides high-level view of transformation progress
"""

import json
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class MetricsAggregator:
    """Aggregate and visualize all project metrics."""
    
    def __init__(self):
        self.metrics_dir = Path("metrics")
        self.metrics_dir.mkdir(exist_ok=True)
        
    def collect_all_metrics(self) -> Dict:
        """Collect metrics from all sources."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "progress": self.load_progress_metrics(),
            "git": self.collect_git_metrics(),
            "tests": self.collect_test_metrics(),
            "performance": self.collect_performance_metrics(),
            "quality": self.collect_quality_metrics(),
        }
        
        return metrics
    
    def load_progress_metrics(self) -> Dict:
        """Load progress dashboard metrics."""
        progress_file = self.metrics_dir / "progress.json"
        
        if progress_file.exists():
            with open(progress_file, 'r') as f:
                data = json.load(f)
                if data:
                    return data[-1]  # Latest metrics
        
        return {}
    
    def collect_git_metrics(self) -> Dict:
        """Collect git statistics."""
        metrics = {}
        
        try:
            # Commit count
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                capture_output=True,
                text=True
            )
            metrics["total_commits"] = int(result.stdout.strip())
            
            # Recent activity
            result = subprocess.run(
                ["git", "log", "--since=1.week", "--oneline"],
                capture_output=True,
                text=True
            )
            metrics["commits_this_week"] = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
            
            # Contributors
            result = subprocess.run(
                ["git", "shortlog", "-sn"],
                capture_output=True,
                text=True
            )
            metrics["contributors"] = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
            
            # File count
            result = subprocess.run(
                ["git", "ls-files"],
                capture_output=True,
                text=True
            )
            metrics["total_files"] = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
            
        except Exception:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
        
        return metrics
    
    def collect_test_metrics(self) -> Dict:
        """Collect test metrics."""
        metrics = {}
        
        try:
            # Count test files
            test_files = list(Path('tests').rglob('test_*.py')) if Path('tests').exists() else []
            metrics["test_files"] = len(test_files)
            
            # Check coverage report
            coverage_file = Path('.coverage')
            if coverage_file.exists():
                result = subprocess.run(
                    ["coverage", "report", "--format=json"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    coverage_data = json.loads(result.stdout)
                    metrics["coverage_percent"] = coverage_data.get("totals", {}).get("percent_covered", 0)
            
        except Exception:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
        
        return metrics
    
    def collect_performance_metrics(self) -> Dict:
        """Collect performance metrics."""
        metrics = {}
        
        # Check for performance validation
        perf_file = Path("PERFORMANCE_VALIDATION.md")
        if perf_file.exists():
            metrics["performance_validated"] = True
            
            # Extract speedup numbers
            with open(perf_file, 'r') as f:
                content = f.read()
                
                # Simple extraction of speedup claims
                import re
                speedups = re.findall(r'(\d+)x faster', content)
                if speedups:
                    metrics["max_speedup"] = max(int(s) for s in speedups)
                    metrics["avg_speedup"] = sum(int(s) for s in speedups) / len(speedups)
        
        return metrics
    
    def collect_quality_metrics(self) -> Dict:
        """Collect code quality metrics."""
        metrics = {}
        
        try:
            # Python files
            py_files = list(Path('.').rglob('*.py'))
            py_files = [f for f in py_files if 'venv' not in str(f) and '__pycache__' not in str(f)]
            metrics["python_files"] = len(py_files)
            
            # Lines of code
            total_lines = 0
            for file in py_files[:100]:  # Sample
                try:
                    with open(file, 'r') as f:
                        total_lines += len(f.readlines())
                except Exception:
                    # TODO: Add proper error handling
                    pass  # Silent for now, should log error
            
            metrics["lines_of_code"] = total_lines
            
            # Documentation files
            doc_files = list(Path('.').rglob('*.md'))
            metrics["documentation_files"] = len(doc_files)
            
        except Exception:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
        
        return metrics
    
    def generate_trend_chart(self, history: List[Dict]):
        """Generate trend chart from historical data."""
        if len(history) < 2:
            return
        
        # Extract data for plotting
        timestamps = []
        overall_scores = []
        
        for entry in history:
            if 'timestamp' in entry and 'overall_score' in entry:
                timestamps.append(datetime.fromisoformat(entry['timestamp']))
                overall_scores.append(entry['overall_score'])
        
        if len(timestamps) < 2:
            return
        
        # Create plot
        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, overall_scores, 'b-o', linewidth=2, markersize=8)
        
        # Add target line
        plt.axhline(y=10, color='g', linestyle='--', label='Target (10/10)')
        
        # Formatting
        plt.xlabel('Date')
        plt.ylabel('Overall Score')
        plt.title('Nix for Humanity Quality Score Trend')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Format x-axis
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gcf().autofmt_xdate()
        
        # Set y-axis limits
        plt.ylim(0, 10.5)
        
        # Save
        plt.tight_layout()
        plt.savefig(self.metrics_dir / 'quality_trend.png', dpi=150)
        plt.close()
    
    def generate_executive_summary(self, metrics: Dict):
        """Generate executive summary report."""
        progress = metrics.get('progress', {})
        git = metrics.get('git', {})
        tests = metrics.get('tests', {})
        performance = metrics.get('performance', {})
        quality = metrics.get('quality', {})
        
        # Calculate completion percentage
        target_score = 10.0
        current_score = progress.get('overall_score', 0)
        completion_percent = (current_score / target_score) * 100
        
        summary = f"""
# Executive Summary - Nix for Humanity

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🎯 Transformation Progress

**Overall Completion**: {completion_percent:.1f}%
**Current Score**: {current_score:.1f}/10
**Target Score**: 10/10

## 📊 Key Metrics

### Development Activity
- Total Commits: {git.get('total_commits', 0):,}
- This Week: {git.get('commits_this_week', 0)} commits
- Contributors: {git.get('contributors', 0)}
- Project Files: {git.get('total_files', 0):,}

### Code Quality
- Python Files: {quality.get('python_files', 0):,}
- Lines of Code: {quality.get('lines_of_code', 0):,}
- Documentation Files: {quality.get('documentation_files', 0)}
- Test Coverage: {tests.get('coverage_percent', 0):.1f}%

### Testing
- Test Files: {tests.get('test_files', 0)}
- Integration Tests: {'✅' if tests.get('test_files', 0) > 10 else '❌'}

### Performance
- Validated: {'✅' if performance.get('performance_validated') else '❌'}
"""
        
        if performance.get('max_speedup'):
            summary += f"- Max Speedup: {performance['max_speedup']}x\n"
            summary += f"- Avg Speedup: {performance.get('avg_speedup', 0):.1f}x\n"
        
        summary += f"""

## 📈 Progress by Category

| Category | Score | Status |
|----------|-------|--------|
| Structure | {progress.get('structure', {}).get('score', 0):.1f}/10 | {'🟢' if progress.get('structure', {}).get('score', 0) >= 8 else '🟡' if progress.get('structure', {}).get('score', 0) >= 6 else '🔴'} |
| Code Quality | {progress.get('code_quality', {}).get('score', 0):.1f}/10 | {'🟢' if progress.get('code_quality', {}).get('score', 0) >= 8 else '🟡' if progress.get('code_quality', {}).get('score', 0) >= 6 else '🔴'} |
| Test Health | {progress.get('test_health', {}).get('score', 0):.1f}/10 | {'🟢' if progress.get('test_health', {}).get('score', 0) >= 8 else '🟡' if progress.get('test_health', {}).get('score', 0) >= 6 else '🔴'} |
| Documentation | {progress.get('documentation', {}).get('score', 0):.1f}/10 | {'🟢' if progress.get('documentation', {}).get('score', 0) >= 8 else '🟡' if progress.get('documentation', {}).get('score', 0) >= 6 else '🔴'} |
| Performance | {progress.get('performance', {}).get('score', 0):.1f}/10 | {'🟢' if progress.get('performance', {}).get('score', 0) >= 8 else '🟡' if progress.get('performance', {}).get('score', 0) >= 6 else '🔴'} |

## 🎯 Estimated Time to Completion

"""
        
        # Estimate completion based on current progress
        if git.get('commits_this_week', 0) > 0:
            weeks_active = git.get('total_commits', 0) / max(git.get('commits_this_week', 1), 1)
            progress_per_week = current_score / max(weeks_active, 1)
            remaining_score = target_score - current_score
            
            if progress_per_week > 0:
                weeks_remaining = remaining_score / progress_per_week
                completion_date = datetime.now() + timedelta(weeks=weeks_remaining)
                
                summary += f"- Current Rate: +{progress_per_week:.2f} points/week\n"
                summary += f"- Weeks Remaining: {weeks_remaining:.1f}\n"
                summary += f"- Estimated Completion: {completion_date.strftime('%Y-%m-%d')}\n"
            else:
                summary += "- Unable to estimate (no recent progress)\n"
        else:
            summary += "- Unable to estimate (no recent activity)\n"
        
        summary += """

## 🚦 Release Readiness

"""
        
        if current_score >= 9.5:
            summary += "### 🟢 READY FOR RELEASE\n\nAll systems go! Time to ship! 🚀"
        elif current_score >= 8.0:
            summary += "### 🟡 ALMOST READY\n\nFinal polish needed before release."
        elif current_score >= 6.0:
            summary += "### 🟠 IN PROGRESS\n\nSteady progress, maintain momentum."
        else:
            summary += "### 🔴 EARLY STAGE\n\nSignificant work required."
        
        summary += """

## 📋 Recommendations

"""
        
        # Priority recommendations
        priorities = []
        
        if progress.get('structure', {}).get('score', 0) < 7:
            priorities.append("1. **Fix Project Structure** - Run reorganization scripts")
        elif progress.get('test_health', {}).get('score', 0) < 7:
            priorities.append("1. **Improve Test Coverage** - Add real integration tests")
        elif progress.get('code_quality', {}).get('score', 0) < 7:
            priorities.append("1. **Enhance Code Quality** - Consolidate duplicates")
        elif progress.get('documentation', {}).get('score', 0) < 7:
            priorities.append("1. **Update Documentation** - Ensure accuracy")
        else:
            priorities.append("1. **Final Polish** - Address remaining issues")
        
        priorities.extend([
            "2. Maintain weekly progress reviews",
            "3. Keep feature freeze active",
            "4. Run validation suite regularly"
        ])
        
        summary += "\n".join(priorities)
        
        summary += """

---

*Use this summary for stakeholder updates and strategic decisions.*
"""
        
        # Save summary
        with open(self.metrics_dir / 'EXECUTIVE_SUMMARY.md', 'w') as f:
            f.write(summary)
        
        print(f"\n📄 Executive summary saved to: {self.metrics_dir}/EXECUTIVE_SUMMARY.md")
    
    def save_metrics_history(self, metrics: Dict):
        """Save metrics to history file."""
        history_file = self.metrics_dir / "metrics_history.json"
        
        # Load existing history
        if history_file.exists():
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        # Add current metrics
        history.append(metrics)
        
        # Keep last 100 entries
        history = history[-100:]
        
        # Save
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        return history

def main():
    """Run metrics aggregation."""
    aggregator = MetricsAggregator()
    
    print("📊 Aggregating Nix for Humanity metrics...")
    
    # Collect all metrics
    metrics = aggregator.collect_all_metrics()
    
    # Save to history
    history = aggregator.save_metrics_history(metrics)
    
    # Generate trend chart
    if len(history) > 1:
        print("📈 Generating trend chart...")
        aggregator.generate_trend_chart(history)
    
    # Generate executive summary
    print("📄 Generating executive summary...")
    aggregator.generate_executive_summary(metrics)
    
    # Display key metrics
    progress = metrics.get('progress', {})
    if progress:
        score = progress.get('overall_score', 0)
        print(f"\n🎯 Current Score: {score:.1f}/10")
        print(f"📊 Completion: {(score/10)*100:.1f}%")
    
    print("\n✅ Metrics aggregation complete!")
    print(f"📁 Results in: {aggregator.metrics_dir}/")

if __name__ == "__main__":
    main()