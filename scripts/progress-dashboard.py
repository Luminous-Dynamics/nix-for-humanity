#!/usr/bin/env python3
"""
Progress Dashboard for Nix for Humanity Improvement Plan
Tracks metrics and visualizes progress toward 10/10 excellence
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import sys

class ProgressDashboard:
    """Track and visualize improvement progress."""
    
    def __init__(self):
        self.metrics_file = Path("metrics/progress.json")
        self.metrics_file.parent.mkdir(exist_ok=True)
        self.current_metrics = self.collect_metrics()
        
    def collect_metrics(self) -> Dict:
        """Collect current project metrics."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "structure": self.analyze_structure(),
            "code_quality": self.analyze_code_quality(),
            "test_health": self.analyze_tests(),
            "documentation": self.analyze_docs(),
            "performance": self.analyze_performance(),
            "overall_score": 0.0
        }
        
        # Calculate overall score
        scores = [
            metrics["structure"]["score"],
            metrics["code_quality"]["score"],
            metrics["test_health"]["score"],
            metrics["documentation"]["score"],
            metrics["performance"]["score"]
        ]
        metrics["overall_score"] = sum(scores) / len(scores)
        
        return metrics
    
    def analyze_structure(self) -> Dict:
        """Analyze project structure health."""
        root_files = len([f for f in os.listdir('.') if os.path.isfile(f)])
        
        # Check for proper structure
        proper_dirs = ['src', 'tests', 'docs', 'scripts', 'examples']
        existing_dirs = sum(1 for d in proper_dirs if os.path.exists(d))
        
        # Check for mess indicators
        test_files_in_root = len([f for f in os.listdir('.') if f.startswith('test_') and f.endswith('.py')])
        status_files_in_root = len([f for f in os.listdir('.') if '_COMPLETE.md' in f or '_REPORT.md' in f])
        
        score = 10.0
        issues = []
        
        if root_files > 15:
            score -= 3.0
            issues.append(f"Too many root files: {root_files} (target: <15)")
        
        if existing_dirs < len(proper_dirs):
            score -= 2.0
            issues.append(f"Missing directories: {len(proper_dirs) - existing_dirs}")
        
        if test_files_in_root > 0:
            score -= 2.0
            issues.append(f"Test files in root: {test_files_in_root}")
        
        if status_files_in_root > 0:
            score -= 1.0
            issues.append(f"Status files in root: {status_files_in_root}")
        
        # Check for duplicate backends
        if os.path.exists('backend') and os.path.exists('nix_humanity'):
            score -= 2.0
            issues.append("Duplicate backend directories exist")
        
        return {
            "score": max(0, score),
            "root_files": root_files,
            "proper_structure": existing_dirs == len(proper_dirs),
            "issues": issues
        }
    
    def analyze_code_quality(self) -> Dict:
        """Analyze code quality metrics."""
        score = 10.0
        issues = []
        
        try:
            # Count Python files
            py_files = list(Path('.').rglob('*.py'))
            py_files = [f for f in py_files if 'venv' not in str(f) and '__pycache__' not in str(f)]
            
            # Check for code duplication indicators
            function_names = set()
            duplicates = []
            
            for file in py_files[:20]:  # Sample first 20 files
                try:
                    with open(file, 'r') as f:
                        content = f.read()
                        # Simple function detection
                        import re
                        functions = re.findall(r'def\s+(\w+)\s*\(', content)
                        for func in functions:
                            if func in function_names and func != '__init__':
                                duplicates.append(func)
                            function_names.add(func)
                except Exception:
                    # TODO: Add proper error handling
                    pass  # Silent for now, should log error
            
            if duplicates:
                score -= 2.0
                issues.append(f"Duplicate functions found: {len(set(duplicates))}")
            
            # Check for type hints (sample)
            typed_files = 0
            for file in py_files[:10]:
                try:
                    with open(file, 'r') as f:
                        if '-> ' in f.read():
                            typed_files += 1
                except Exception:
                    # TODO: Add proper error handling
                    pass  # Silent for now, should log error
            
            type_hint_ratio = typed_files / min(10, len(py_files)) if py_files else 0
            if type_hint_ratio < 0.7:
                score -= 1.0
                issues.append(f"Low type hint usage: {type_hint_ratio:.0%}")
            
            # Check for proper imports
            bad_imports = 0
            for file in py_files[:20]:
                try:
                    with open(file, 'r') as f:
                        content = f.read()
                        if 'sys.path.append' in content or 'sys.path.insert' in content:
                            bad_imports += 1
                except Exception:
                    # TODO: Add proper error handling
                    pass  # Silent for now, should log error
            
            if bad_imports > 3:
                score -= 2.0
                issues.append(f"Path manipulation in {bad_imports} files")
            
        except Exception as e:
            issues.append(f"Analysis error: {e}")
            score = 5.0
        
        return {
            "score": max(0, score),
            "total_files": len(py_files) if 'py_files' in locals() else 0,
            "issues": issues
        }
    
    def analyze_tests(self) -> Dict:
        """Analyze test health."""
        score = 10.0
        issues = []
        
        try:
            # Check test structure
            if not os.path.exists('tests'):
                score -= 5.0
                issues.append("No tests directory")
            else:
                # Check for test organization
                test_dirs = ['unit', 'integration', 'e2e']
                existing_test_dirs = sum(1 for d in test_dirs if os.path.exists(f'tests/{d}'))
                if existing_test_dirs < len(test_dirs):
                    score -= 2.0
                    issues.append(f"Missing test directories: {len(test_dirs) - existing_test_dirs}")
            
            # Check for excessive mocking
            if os.path.exists('tests/conftest.py'):
                with open('tests/conftest.py', 'r') as f:
                    content = f.read()
                    mock_count = content.count('mock') + content.count('Mock')
                    if mock_count > 20:
                        score -= 3.0
                        issues.append(f"Excessive mocking: {mock_count} references")
            
            # Check for real integration tests
            integration_tests = list(Path('tests').rglob('*integration*.py')) if os.path.exists('tests') else []
            if len(integration_tests) < 3:
                score -= 2.0
                issues.append(f"Few integration tests: {len(integration_tests)}")
            
        except Exception as e:
            issues.append(f"Test analysis error: {e}")
            score = 5.0
        
        return {
            "score": max(0, score),
            "has_tests": os.path.exists('tests'),
            "issues": issues
        }
    
    def analyze_docs(self) -> Dict:
        """Analyze documentation quality."""
        score = 10.0
        issues = []
        
        try:
            # Check README
            if os.path.exists('README.md'):
                with open('README.md', 'r') as f:
                    readme = f.read()
                    
                    # Check for honesty indicators
                    if 'work in progress' not in readme.lower() and 'alpha' not in readme.lower():
                        score -= 2.0
                        issues.append("README doesn't indicate development status")
                    
                    if '✅' in readme and '❌' not in readme:
                        score -= 1.0
                        issues.append("README only shows successes, not limitations")
            else:
                score -= 5.0
                issues.append("No README.md")
            
            # Check for excessive vision docs
            vision_docs = list(Path('.').rglob('*VISION*.md'))
            if len(vision_docs) > 3:
                score -= 2.0
                issues.append(f"Too many vision documents: {len(vision_docs)}")
            
        except Exception as e:
            issues.append(f"Doc analysis error: {e}")
            score = 5.0
        
        return {
            "score": max(0, score),
            "has_readme": os.path.exists('README.md'),
            "issues": issues
        }
    
    def analyze_performance(self) -> Dict:
        """Analyze performance claims vs reality."""
        score = 10.0
        issues = []
        
        # Check if performance validation exists
        if not os.path.exists('PERFORMANCE_VALIDATION.md'):
            score -= 3.0
            issues.append("No performance validation report")
        
        # Check for benchmark tests
        benchmark_tests = list(Path('.').rglob('*benchmark*.py'))
        if len(benchmark_tests) < 2:
            score -= 2.0
            issues.append(f"Few benchmark tests: {len(benchmark_tests)}")
        
        return {
            "score": max(0, score),
            "has_benchmarks": len(benchmark_tests) > 0,
            "issues": issues
        }
    
    def save_metrics(self):
        """Save current metrics to file."""
        # Load existing metrics
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                all_metrics = json.load(f)
        else:
            all_metrics = []
        
        # Add current metrics
        all_metrics.append(self.current_metrics)
        
        # Keep only last 100 entries
        all_metrics = all_metrics[-100:]
        
        # Save
        with open(self.metrics_file, 'w') as f:
            json.dump(all_metrics, f, indent=2)
    
    def generate_report(self):
        """Generate progress report."""
        m = self.current_metrics
        
        # Calculate improvement if we have history
        improvement = ""
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                history = json.load(f)
                if len(history) > 1:
                    prev_score = history[-2]["overall_score"] if len(history) > 1 else m["overall_score"]
                    improvement = f" ({m['overall_score'] - prev_score:+.1f})"
        
        # Console output with colors
        print("\n" + "="*60)
        print("🎯 NIX FOR HUMANITY PROGRESS DASHBOARD")
        print("="*60)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n📊 OVERALL SCORE: {m['overall_score']:.1f}/10{improvement}")
        print("="*60)
        
        # Category breakdown
        categories = [
            ("📁 Project Structure", m["structure"]),
            ("💻 Code Quality", m["code_quality"]),
            ("🧪 Test Health", m["test_health"]),
            ("📚 Documentation", m["documentation"]),
            ("⚡ Performance", m["performance"])
        ]
        
        for name, data in categories:
            status = "🟢" if data["score"] >= 8 else "🟡" if data["score"] >= 6 else "🔴"
            print(f"\n{status} {name}: {data['score']:.1f}/10")
            
            if data["issues"]:
                for issue in data["issues"]:
                    print(f"   ⚠️  {issue}")
            else:
                print(f"   ✅ No issues found!")
        
        # Generate HTML report
        self.generate_html_report()
        
        print("\n" + "="*60)
        print("📈 NEXT STEPS:")
        
        # Prioritized recommendations
        if m["structure"]["score"] < 7:
            print("1. Run ./scripts/reorganize-project.sh")
        elif m["code_quality"]["score"] < 7:
            print("1. Run python scripts/consolidate-backend.py")
        elif m["test_health"]["score"] < 7:
            print("1. Run ./scripts/test-infrastructure.sh")
        elif m["documentation"]["score"] < 7:
            print("1. Run ./scripts/create-honest-readme.sh")
        else:
            print("1. Focus on remaining issues above")
        
        print("\n📄 Full report: metrics/dashboard.html")
        print("="*60 + "\n")
    
    def generate_html_report(self):
        """Generate HTML dashboard."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Nix for Humanity Progress Dashboard</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .score-big {{
            font-size: 72px;
            font-weight: bold;
            color: {'#22c55e' if self.current_metrics['overall_score'] >= 8 else '#f59e0b' if self.current_metrics['overall_score'] >= 6 else '#ef4444'};
        }}
        .category {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .category-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .score {{
            font-size: 24px;
            font-weight: bold;
        }}
        .issues {{
            margin-top: 10px;
            padding-left: 20px;
        }}
        .issue {{
            color: #dc2626;
            margin: 5px 0;
        }}
        .good {{
            color: #22c55e;
        }}
        .warning {{
            color: #f59e0b;
        }}
        .bad {{
            color: #ef4444;
        }}
        .progress-bar {{
            width: 100%;
            height: 20px;
            background: #e5e7eb;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 10px;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(to right, #ef4444, #f59e0b, #22c55e);
            transition: width 0.3s ease;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Nix for Humanity Progress Dashboard</h1>
        <div class="score-big">{self.current_metrics['overall_score']:.1f}/10</div>
        <p>Target: 10/10 Production Excellence</p>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
"""
        
        # Add categories
        categories = [
            ("📁 Project Structure", self.current_metrics["structure"]),
            ("💻 Code Quality", self.current_metrics["code_quality"]),
            ("🧪 Test Health", self.current_metrics["test_health"]),
            ("📚 Documentation", self.current_metrics["documentation"]),
            ("⚡ Performance", self.current_metrics["performance"])
        ]
        
        for name, data in categories:
            score_class = 'good' if data['score'] >= 8 else 'warning' if data['score'] >= 6 else 'bad'
            
            html += f"""
    <div class="category">
        <div class="category-header">
            <h2>{name}</h2>
            <span class="score {score_class}">{data['score']:.1f}/10</span>
        </div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {data['score']*10}%"></div>
        </div>
"""
            
            if data['issues']:
                html += '        <div class="issues">\n'
                for issue in data['issues']:
                    html += f'            <div class="issue">⚠️ {issue}</div>\n'
                html += '        </div>\n'
            else:
                html += '        <div class="issues"><div class="good">✅ No issues found!</div></div>\n'
            
            html += '    </div>\n'
        
        html += """
</body>
</html>
"""
        
        # Save HTML
        os.makedirs('metrics', exist_ok=True)
        with open('metrics/dashboard.html', 'w') as f:
            f.write(html)

def main():
    """Run progress dashboard."""
    dashboard = ProgressDashboard()
    dashboard.save_metrics()
    dashboard.generate_report()

if __name__ == "__main__":
    main()