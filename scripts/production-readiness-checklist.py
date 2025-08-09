#!/usr/bin/env python3
"""
Production Readiness Checklist for Nix for Humanity

This script provides a prioritized checklist of what needs to be done
before the production release.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict
from dataclasses import dataclass
from enum import Enum

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class Priority(Enum):
    BLOCKER = "🚨 BLOCKER"
    CRITICAL = "⚠️  CRITICAL"
    HIGH = "🔧 HIGH"
    MEDIUM = "📝 MEDIUM"
    LOW = "ℹ️  LOW"


@dataclass
class ChecklistItem:
    priority: Priority
    category: str
    description: str
    action: str
    files: List[str] = None
    estimated_time: str = ""


class ProductionReadinessChecker:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.checklist: List[ChecklistItem] = []
        
    def run_all_checks(self):
        """Run all production readiness checks"""
        print("🚀 Nix for Humanity - Production Readiness Checklist")
        print("=" * 80)
        
        # Check critical issues
        self._check_syntax_errors()
        self._check_core_functionality()
        self._check_test_coverage()
        self._check_documentation()
        self._check_security()
        self._check_performance()
        self._check_user_experience()
        self._check_deployment()
        
        # Generate report
        self._generate_checklist()
        
    def _check_syntax_errors(self):
        """Check for syntax errors that block execution"""
        # Known syntax errors from previous scan
        syntax_errors = [
            "features/v3.0/xai/test_xai_causal_engine.py",
            "scripts/perform-consolidation.py",
            "scripts/train-nixos-expert.py",
            "tests/integration/test_error_intelligence_integration.py",
            "tests/test_component_integration.py",
        ]
        
        if syntax_errors:
            self.checklist.append(ChecklistItem(
                priority=Priority.BLOCKER,
                category="Syntax Errors",
                description=f"{len(syntax_errors)} files have syntax errors preventing execution",
                action="Fix syntax errors in all files",
                files=syntax_errors[:5],  # Show first 5
                estimated_time="1-2 hours"
            ))
            
    def _check_core_functionality(self):
        """Check core features are working"""
        # Test basic commands
        core_commands = [
            ("ask-nix help", "Basic help command"),
            ("ask-nix 'search firefox' --dry-run", "Package search"),
            ("ask-nix 'install firefox' --dry-run", "Package installation"),
            ("nix-tui --help", "TUI interface"),
        ]
        
        working = []
        broken = []
        
        for cmd, desc in core_commands:
            try:
                result = subprocess.run(
                    cmd.split(), 
                    capture_output=True,
                    timeout=5,
                    cwd=self.project_root
                )
                if result.returncode == 0:
                    working.append(desc)
                else:
                    broken.append((cmd, desc))
            except Exception:
                broken.append((cmd, desc))
                
        if broken:
            self.checklist.append(ChecklistItem(
                priority=Priority.CRITICAL,
                category="Core Functionality",
                description=f"{len(broken)} core commands not working",
                action="Fix broken commands: " + ", ".join([desc for _, desc in broken]),
                estimated_time="2-4 hours"
            ))
            
        # Check native backend
        native_backend_file = self.project_root / "src/nix_humanity/nix/native_backend.py"
        if native_backend_file.exists():
            with open(native_backend_file) as f:
                content = f.read()
                if "TODO" in content or "NotImplementedError" in content:
                    self.checklist.append(ChecklistItem(
                        priority=Priority.HIGH,
                        category="Native Backend",
                        description="Native Python-Nix backend has incomplete implementations",
                        action="Complete all TODO items in native backend",
                        files=["src/nix_humanity/nix/native_backend.py"],
                        estimated_time="4-6 hours"
                    ))
                    
    def _check_test_coverage(self):
        """Check test coverage and failing tests"""
        # Run quick test check
        try:
            result = subprocess.run(
                ["pytest", "--collect-only", "-q"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            # Parse test count
            if "error" in result.stderr.lower():
                self.checklist.append(ChecklistItem(
                    priority=Priority.CRITICAL,
                    category="Tests",
                    description="Test collection failing - syntax or import errors",
                    action="Fix test collection errors before running tests",
                    estimated_time="2-3 hours"
                ))
            else:
                # Try to run a subset of tests
                result = subprocess.run(
                    ["pytest", "-x", "--tb=no", "-q"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                    timeout=30
                )
                
                if "failed" in result.stdout:
                    self.checklist.append(ChecklistItem(
                        priority=Priority.HIGH,
                        category="Tests",
                        description="Tests are failing",
                        action="Fix failing tests to ensure reliability",
                        estimated_time="4-8 hours"
                    ))
                    
        except Exception:
            self.checklist.append(ChecklistItem(
                priority=Priority.HIGH,
                category="Tests",
                description="Unable to run test suite",
                action="Ensure pytest is properly configured",
                estimated_time="1-2 hours"
            ))
            
    def _check_documentation(self):
        """Check documentation completeness"""
        critical_docs = [
            ("README.md", "Main project documentation"),
            ("docs/QUICKSTART.md", "Quick start guide"),
            ("docs/CONTRIBUTING.md", "Contribution guidelines"),
            ("CHANGELOG.md", "Version history"),
        ]
        
        missing_docs = []
        for doc_path, desc in critical_docs:
            if not (self.project_root / doc_path).exists():
                missing_docs.append((doc_path, desc))
                
        if missing_docs:
            self.checklist.append(ChecklistItem(
                priority=Priority.MEDIUM,
                category="Documentation",
                description=f"{len(missing_docs)} critical documentation files missing",
                action="Create missing documentation files",
                files=[path for path, _ in missing_docs],
                estimated_time="2-4 hours"
            ))
            
        # Check if docs match reality
        self.checklist.append(ChecklistItem(
            priority=Priority.MEDIUM,
            category="Documentation",
            description="Documentation may not reflect current implementation",
            action="Review and update all documentation to match actual functionality",
            estimated_time="4-6 hours"
        ))
        
    def _check_security(self):
        """Check for security issues"""
        security_patterns = [
            ("subprocess.*shell=True", "Shell injection risk"),
            ("eval\\(", "Code injection risk"),
            ("exec\\(", "Code injection risk"),
            ("pickle\\.loads", "Deserialization vulnerability"),
        ]
        
        security_issues = []
        for pattern, risk in security_patterns:
            try:
                result = subprocess.run(
                    ["grep", "-r", pattern, "src/", "--include=*.py"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root
                )
                if result.stdout:
                    count = len(result.stdout.strip().split('\n'))
                    security_issues.append((risk, count))
            except:
                pass
                
        if security_issues:
            self.checklist.append(ChecklistItem(
                priority=Priority.CRITICAL,
                category="Security",
                description=f"Found {len(security_issues)} types of security risks",
                action="Review and fix security vulnerabilities: " + 
                       ", ".join([f"{risk} ({count} instances)" for risk, count in security_issues]),
                estimated_time="2-4 hours"
            ))
            
    def _check_performance(self):
        """Check performance considerations"""
        self.checklist.append(ChecklistItem(
            priority=Priority.MEDIUM,
            category="Performance",
            description="Native Python-Nix API integration incomplete",
            action="Complete native backend integration for 10x-1500x performance gains",
            files=["src/nix_humanity/nix/native_backend.py"],
            estimated_time="8-12 hours"
        ))
        
        # Check for performance anti-patterns
        self.checklist.append(ChecklistItem(
            priority=Priority.LOW,
            category="Performance",
            description="Code may have performance bottlenecks",
            action="Profile and optimize hot paths, especially in NLP and execution",
            estimated_time="4-6 hours"
        ))
        
    def _check_user_experience(self):
        """Check user experience elements"""
        # Check error messages
        self.checklist.append(ChecklistItem(
            priority=Priority.HIGH,
            category="User Experience",
            description="Error messages need to be user-friendly",
            action="Review all error messages for clarity and helpfulness",
            files=["src/nix_humanity/core/educational_errors.py"],
            estimated_time="3-4 hours"
        ))
        
        # Check first-run experience
        self.checklist.append(ChecklistItem(
            priority=Priority.MEDIUM,
            category="User Experience",
            description="First-run wizard needs testing",
            action="Test and polish the first-run experience",
            files=["src/nix_humanity/core/first_run_wizard.py"],
            estimated_time="2-3 hours"
        ))
        
    def _check_deployment(self):
        """Check deployment readiness"""
        deployment_files = [
            ("flake.nix", "Nix flake configuration"),
            ("pyproject.toml", "Python package configuration"),
            (".github/workflows/ci.yml", "CI/CD pipeline"),
        ]
        
        missing = []
        for file_path, desc in deployment_files:
            if not (self.project_root / file_path).exists():
                missing.append((file_path, desc))
                
        if missing:
            self.checklist.append(ChecklistItem(
                priority=Priority.HIGH,
                category="Deployment",
                description=f"{len(missing)} deployment configuration files missing",
                action="Create deployment configurations",
                files=[path for path, _ in missing],
                estimated_time="2-4 hours"
            ))
            
    def _generate_checklist(self):
        """Generate the final checklist report"""
        # Sort by priority
        priority_order = [Priority.BLOCKER, Priority.CRITICAL, Priority.HIGH, Priority.MEDIUM, Priority.LOW]
        self.checklist.sort(key=lambda x: priority_order.index(x.priority))
        
        # Calculate totals
        total_time = 0
        time_by_priority = {p: 0 for p in Priority}
        
        # Print checklist
        print("\n📋 PRODUCTION READINESS CHECKLIST")
        print("=" * 80)
        
        current_priority = None
        for item in self.checklist:
            if item.priority != current_priority:
                current_priority = item.priority
                print(f"\n{item.priority.value} Priority Items:")
                print("-" * 40)
                
            print(f"\n✓ {item.category}: {item.description}")
            print(f"  Action: {item.action}")
            if item.files:
                print(f"  Files: {', '.join(item.files[:3])}")
                if len(item.files) > 3:
                    print(f"         ... and {len(item.files) - 3} more")
            if item.estimated_time:
                print(f"  Time estimate: {item.estimated_time}")
                # Parse time for totals
                hours = 0
                if "-" in item.estimated_time:
                    hours = int(item.estimated_time.split("-")[1].split()[0])
                else:
                    hours = int(item.estimated_time.split()[0])
                total_time += hours
                time_by_priority[item.priority] += hours
                
        # Summary
        print("\n" + "=" * 80)
        print("📊 SUMMARY")
        print("=" * 80)
        
        for priority in priority_order:
            count = sum(1 for item in self.checklist if item.priority == priority)
            if count > 0:
                print(f"{priority.value}: {count} items (~{time_by_priority[priority]} hours)")
                
        print(f"\nTotal estimated time: {total_time} hours ({total_time/8:.1f} days)")
        
        # Recommendations
        print("\n🎯 RECOMMENDED ACTION PLAN:")
        print("=" * 80)
        print("1. Fix all BLOCKER issues first (syntax errors)")
        print("2. Address CRITICAL issues (core functionality, security)")
        print("3. Fix HIGH priority items (tests, deployment)")
        print("4. Polish MEDIUM priority items (docs, UX)")
        print("5. Consider LOW priority items for v1.1")
        
        print("\n💡 Quick wins to focus on:")
        print("- Fix the 14 syntax errors (1-2 hours)")
        print("- Get basic CLI commands working reliably")
        print("- Ensure tests can at least run without errors")
        print("- Update README with accurate information")
        
        # Save report
        report_path = self.project_root / "production-readiness-report.md"
        with open(report_path, 'w') as f:
            f.write("# Nix for Humanity - Production Readiness Report\n\n")
            f.write(f"Generated: {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- Total items: {len(self.checklist)}\n")
            f.write(f"- Estimated time: {total_time} hours\n")
            f.write(f"- Blocker issues: {sum(1 for i in self.checklist if i.priority == Priority.BLOCKER)}\n\n")
            
            f.write("## Detailed Checklist\n\n")
            
            current_priority = None
            for item in self.checklist:
                if item.priority != current_priority:
                    current_priority = item.priority
                    f.write(f"\n### {item.priority.value}\n\n")
                    
                f.write(f"#### {item.category}: {item.description}\n")
                f.write(f"- **Action**: {item.action}\n")
                if item.files:
                    f.write(f"- **Files**: {', '.join(item.files)}\n")
                if item.estimated_time:
                    f.write(f"- **Time estimate**: {item.estimated_time}\n")
                f.write("\n")
                
        print(f"\n📄 Detailed report saved to: {report_path}")


def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent
    
    checker = ProductionReadinessChecker(project_root)
    checker.run_all_checks()


if __name__ == "__main__":
    main()