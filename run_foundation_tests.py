#!/usr/bin/env python3
"""
Foundation Testing Script - Run comprehensive tests and generate reports.
Part of "Week 1: Stop the Bleeding" initiative.
"""

import subprocess
import sys
import json
import time
from pathlib import Path
from datetime import datetime

class FoundationTester:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "coverage": 0,
            "critical_issues": [],
            "warnings": [],
            "ready_features": [],
            "broken_features": []
        }
        
    def run_tests(self):
        """Run the comprehensive test suite."""
        print("🧪 Running Foundation Tests...")
        print("=" * 50)
        
        # Check if pytest is available
        try:
            subprocess.run(["poetry", "show", "pytest"], 
                         capture_output=True, check=True)
        except:
            print("⚠️  Installing pytest first...")
            subprocess.run(["poetry", "add", "--group", "dev", "pytest", "pytest-cov"])
        
        # Run tests with coverage
        print("\n📊 Running tests with coverage...")
        result = subprocess.run([
            "poetry", "run", "pytest",
            "tests/test_core_functionality.py",
            "-v",
            "--tb=short",
            "--cov=src/luminous_nix",
            "--cov-report=term-missing",
            "--cov-report=json"
        ], capture_output=True, text=True)
        
        # Parse results
        self.parse_test_results(result)
        
        # Check actual functionality
        self.test_real_commands()
        
        # Generate report
        self.generate_report()
        
    def parse_test_results(self, result):
        """Parse pytest output."""
        output = result.stdout + result.stderr
        
        # Extract test counts
        if "passed" in output:
            import re
            match = re.search(r'(\d+) passed', output)
            if match:
                self.results["tests_passed"] = int(match.group(1))
        
        if "failed" in output:
            match = re.search(r'(\d+) failed', output)
            if match:
                self.results["tests_failed"] = int(match.group(1))
        
        self.results["tests_run"] = self.results["tests_passed"] + self.results["tests_failed"]
        
        # Try to get coverage
        try:
            with open("coverage.json", "r") as f:
                cov_data = json.load(f)
                self.results["coverage"] = cov_data.get("totals", {}).get("percent_covered", 0)
        except:
            pass
            
        print(f"✅ Passed: {self.results['tests_passed']}")
        print(f"❌ Failed: {self.results['tests_failed']}")
        print(f"📊 Coverage: {self.results['coverage']:.1f}%")
        
    def test_real_commands(self):
        """Test actual CLI commands."""
        print("\n🔧 Testing Real Commands...")
        print("-" * 40)
        
        commands_to_test = [
            ("Basic help", "./bin/ask-nix help"),
            ("Search firefox", "./bin/ask-nix search firefox"),
            ("Install (dry-run)", "./bin/ask-nix --dry-run install firefox"),
            ("Configuration check", "./bin/ask-nix show config"),
            ("Version info", "./bin/ask-nix --version")
        ]
        
        for name, cmd in commands_to_test:
            print(f"\nTesting: {name}")
            print(f"Command: {cmd}")
            
            try:
                result = subprocess.run(
                    cmd.split(),
                    capture_output=True,
                    text=True,
                    timeout=5,
                    cwd="/srv/luminous-dynamics/11-meta-consciousness/luminous-nix"
                )
                
                if result.returncode == 0:
                    print(f"  ✅ {name} works!")
                    self.results["ready_features"].append(name)
                else:
                    print(f"  ❌ {name} failed!")
                    self.results["broken_features"].append(name)
                    self.results["critical_issues"].append({
                        "feature": name,
                        "error": result.stderr[:200]
                    })
                    
            except subprocess.TimeoutExpired:
                print(f"  ⏱️ {name} timed out!")
                self.results["critical_issues"].append({
                    "feature": name,
                    "error": "Command timed out after 5 seconds"
                })
            except Exception as e:
                print(f"  💥 {name} crashed: {e}")
                self.results["broken_features"].append(name)
                self.results["critical_issues"].append({
                    "feature": name,
                    "error": str(e)
                })
                
    def generate_report(self):
        """Generate comprehensive test report."""
        print("\n" + "=" * 50)
        print("📋 FOUNDATION TEST REPORT")
        print("=" * 50)
        
        # Calculate readiness
        total_features = len(self.results["ready_features"]) + len(self.results["broken_features"])
        if total_features > 0:
            readiness = (len(self.results["ready_features"]) / total_features) * 100
        else:
            readiness = 0
            
        print(f"\n🎯 Launch Readiness: {readiness:.0f}%")
        
        if readiness < 50:
            print("🔴 NOT READY FOR LAUNCH")
            recommendation = "Focus on fixing critical issues"
        elif readiness < 80:
            print("🟡 NEEDS MORE WORK")
            recommendation = "Fix major issues before soft launch"
        else:
            print("🟢 ALMOST READY")
            recommendation = "Polish and prepare for launch"
            
        print(f"Recommendation: {recommendation}")
        
        # Working features
        if self.results["ready_features"]:
            print(f"\n✅ Working Features ({len(self.results['ready_features'])}):")
            for feature in self.results["ready_features"]:
                print(f"  • {feature}")
        
        # Broken features
        if self.results["broken_features"]:
            print(f"\n❌ Broken Features ({len(self.results['broken_features'])}):")
            for feature in self.results["broken_features"]:
                print(f"  • {feature}")
        
        # Critical issues
        if self.results["critical_issues"]:
            print(f"\n🚨 Critical Issues to Fix ({len(self.results['critical_issues'])}):")
            for issue in self.results["critical_issues"][:5]:  # Show top 5
                print(f"  • {issue['feature']}: {issue['error'][:100]}...")
        
        # Save JSON report
        report_path = Path("test_report.json")
        with open(report_path, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📄 Full report saved to: {report_path}")
        
        # Next steps
        print("\n🎯 Next Steps:")
        print("1. Fix all critical issues in broken features")
        print("2. Add error handling to prevent crashes")
        print("3. Improve test coverage to >80%")
        print("4. Document what actually works")
        print("5. Create fallback mechanisms for failures")
        
        return readiness

def main():
    """Run foundation testing."""
    print("""
╔══════════════════════════════════════════════════════╗
║     🏗️  FOUNDATION TESTING - Week 1: Stop the Bleeding ║
╚══════════════════════════════════════════════════════╝

Testing what actually works vs what we claim works...
    """)
    
    tester = FoundationTester()
    readiness = tester.run_tests()
    
    print(f"""
╔══════════════════════════════════════════════════════╗
║  Overall Readiness: {readiness:.0f}%                        ║
║  Priority: Fix critical issues before anything else   ║
╚══════════════════════════════════════════════════════╝
    """)
    
    return 0 if readiness > 50 else 1

if __name__ == "__main__":
    sys.exit(main())