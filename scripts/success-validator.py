#!/usr/bin/env python3
"""
from typing import Tuple
Success Validator - Comprehensive validation of v1.0 readiness
Checks all aspects of the project against production criteria
"""

import os
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Tuple
import sys

class SuccessValidator:
    """Validate that Nix for Humanity meets v1.0 criteria."""
    
    def __init__(self):
        self.results = {}
        self.critical_failures = []
        
    def run_all_validations(self) -> bool:
        """Run comprehensive validation suite."""
        print("🔍 NIX FOR HUMANITY v1.0 SUCCESS VALIDATION")
        print("=" * 50)
        print()
        
        validations = [
            ("Structure", self.validate_structure),
            ("Performance", self.validate_performance),
            ("Functionality", self.validate_functionality),
            ("Code Quality", self.validate_code_quality),
            ("Documentation", self.validate_documentation),
            ("Testing", self.validate_testing),
            ("Security", self.validate_security),
            ("User Experience", self.validate_ux),
        ]
        
        all_passed = True
        
        for name, validator in validations:
            print(f"\n📋 Validating {name}...")
            passed, details = validator()
            self.results[name] = {
                "passed": passed,
                "details": details
            }
            
            if passed:
                print(f"✅ {name} validation PASSED")
            else:
                print(f"❌ {name} validation FAILED")
                all_passed = False
                if "critical" in details:
                    self.critical_failures.append(f"{name}: {details['critical']}")
        
        self.generate_report()
        return all_passed
    
    def validate_structure(self) -> Tuple[bool, Dict]:
        """Validate project structure meets standards."""
        details = {}
        passed = True
        
        # Check root directory cleanliness
        root_files = [f for f in os.listdir('.') if os.path.isfile(f)]
        py_files_in_root = [f for f in root_files if f.endswith('.py')]
        
        if len(root_files) > 15:
            details["root_files"] = f"Too many files in root: {len(root_files)}"
            passed = False
        
        if len(py_files_in_root) > 0:
            details["py_in_root"] = f"Python files in root: {py_files_in_root}"
            passed = False
        
        # Check for proper source structure
        required_dirs = ['src/nix_humanity', 'tests', 'docs', 'scripts']
        missing_dirs = [d for d in required_dirs if not os.path.exists(d)]
        
        if missing_dirs:
            details["missing_dirs"] = f"Missing directories: {missing_dirs}"
            passed = False
        
        # Check for no duplicate backends
        if os.path.exists('backend') and os.path.exists('nix_humanity'):
            details["duplicate_backends"] = "Both backend/ and nix_humanity/ exist"
            details["critical"] = "Duplicate backend implementations"
            passed = False
        
        return passed, details
    
    def validate_performance(self) -> Tuple[bool, Dict]:
        """Validate performance meets targets."""
        details = {}
        passed = True
        
        # Simple performance tests
        performance_tests = {
            "startup": ("./bin/ask-nix --version", 500),  # 500ms target
            "help": ("./bin/ask-nix help", 200),  # 200ms target
        }
        
        for test_name, (command, target_ms) in performance_tests.items():
            try:
                start = time.time()
                result = subprocess.run(
                    command.split(),
                    capture_output=True,
                    timeout=5
                )
                duration_ms = (time.time() - start) * 1000
                
                if duration_ms > target_ms:
                    details[test_name] = f"{duration_ms:.0f}ms (target: {target_ms}ms)"
                    passed = False
                else:
                    details[f"{test_name}_ok"] = f"{duration_ms:.0f}ms"
                    
            except Exception as e:
                details[test_name] = f"Failed: {str(e)}"
                passed = False
        
        # Check for performance validation report
        if not os.path.exists('PERFORMANCE_VALIDATION.md'):
            details["no_validation"] = "No performance validation report"
            passed = False
        
        return passed, details
    
    def validate_functionality(self) -> Tuple[bool, Dict]:
        """Validate core functionality works."""
        details = {}
        passed = True
        
        # Check CLI exists and is executable
        if not os.path.exists('./bin/ask-nix'):
            details["critical"] = "CLI not found"
            return False, details
        
        # Test basic commands
        test_commands = [
            ("help", "./bin/ask-nix help"),
            ("version", "./bin/ask-nix --version"),
            ("dry_run", "./bin/ask-nix 'install vim' --dry-run"),
        ]
        
        for test_name, command in test_commands:
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode != 0:
                    details[test_name] = "Command failed"
                    passed = False
                    
            except Exception as e:
                details[test_name] = f"Error: {str(e)}"
                passed = False
        
        # Check TUI exists
        if not os.path.exists('./bin/nix-tui'):
            details["no_tui"] = "TUI not found"
            # Not critical for v1.0
        
        return passed, details
    
    def validate_code_quality(self) -> Tuple[bool, Dict]:
        """Validate code quality standards."""
        details = {}
        passed = True
        
        # Check for type hints
        src_files = list(Path('src').rglob('*.py')) if Path('src').exists() else []
        
        if not src_files:
            src_files = list(Path('nix_humanity').rglob('*.py')) if Path('nix_humanity').exists() else []
        
        typed_files = 0
        for file in src_files[:20]:  # Sample
            try:
                with open(file, 'r') as f:
                    content = f.read()
                    if '-> ' in content or ': ' in content:
                        typed_files += 1
            except Exception:
                # TODO: Add proper error handling
                pass  # Silent for now, should log error
        
        if src_files:
            type_ratio = typed_files / min(20, len(src_files))
            if type_ratio < 0.7:
                details["low_type_hints"] = f"{type_ratio:.0%} files have type hints"
                passed = False
        
        # Check for excessive TODOs
        todo_count = 0
        for file in src_files:
            try:
                with open(file, 'r') as f:
                    todo_count += f.read().count('TODO')
            except Exception:
                # TODO: Add proper error handling
                pass  # Silent for now, should log error
        
        if todo_count > 50:
            details["too_many_todos"] = f"{todo_count} TODOs found"
            passed = False
        
        return passed, details
    
    def validate_documentation(self) -> Tuple[bool, Dict]:
        """Validate documentation quality."""
        details = {}
        passed = True
        
        # Check README
        if not os.path.exists('README.md'):
            details["critical"] = "No README.md"
            return False, details
        
        with open('README.md', 'r') as f:
            readme = f.read().lower()
            
            # Check for development status
            if not any(word in readme for word in ['alpha', 'beta', 'development', 'v1.0', 'release']):
                details["no_status"] = "README doesn't indicate development status"
                passed = False
            
            # Check for honest limitations
            if '❌' not in readme and 'not' not in readme:
                details["no_limitations"] = "README doesn't mention limitations"
                passed = False
            
            # Check for quick start
            if 'quick start' not in readme and 'getting started' not in readme:
                details["no_quickstart"] = "No quick start section"
                passed = False
        
        # Check for essential docs
        essential_docs = ['CONTRIBUTING.md', 'LICENSE']
        missing_docs = [doc for doc in essential_docs if not os.path.exists(doc) and not os.path.exists(f'docs/{doc}')]
        
        if missing_docs:
            details["missing_docs"] = f"Missing: {missing_docs}"
            passed = False
        
        return passed, details
    
    def validate_testing(self) -> Tuple[bool, Dict]:
        """Validate test coverage and quality."""
        details = {}
        passed = True
        
        # Check test directory
        if not os.path.exists('tests'):
            details["critical"] = "No tests directory"
            return False, details
        
        # Count test files
        test_files = list(Path('tests').rglob('test_*.py'))
        if len(test_files) < 5:
            details["few_tests"] = f"Only {len(test_files)} test files"
            passed = False
        
        # Check for real integration tests
        integration_tests = [f for f in test_files if 'integration' in str(f) or 'real' in str(f)]
        if len(integration_tests) < 2:
            details["no_integration"] = "Too few integration tests"
            passed = False
        
        # Check for excessive mocking
        if os.path.exists('tests/conftest.py'):
            with open('tests/conftest.py', 'r') as f:
                content = f.read()
                mock_count = content.count('mock') + content.count('Mock')
                if mock_count > 20:
                    details["too_much_mocking"] = f"{mock_count} mock references"
                    passed = False
        
        return passed, details
    
    def validate_security(self) -> Tuple[bool, Dict]:
        """Validate security practices."""
        details = {}
        passed = True
        
        # Check for hardcoded secrets
        secret_patterns = ['api_key', 'password', 'secret', 'token']
        
        for pattern in secret_patterns:
            try:
                result = subprocess.run(
                    f"grep -r '{pattern}' . --include='*.py' --exclude-dir='.git' | grep -v test | grep -v example",
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                if result.stdout and '=' in result.stdout:
                    details[f"possible_{pattern}"] = "Possible hardcoded secret"
                    passed = False
                    
            except Exception:
                # TODO: Add proper error handling
                pass  # Silent for now, should log error
        
        # Check for command injection vulnerabilities
        dangerous_patterns = ['shell=True', 'eval(', 'exec(']
        
        for pattern in dangerous_patterns:
            try:
                result = subprocess.run(
                    f"grep -r '{pattern}' . --include='*.py' --exclude-dir='.git' | wc -l",
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                count = int(result.stdout.strip())
                if count > 5:  # Some usage might be legitimate
                    details[f"dangerous_{pattern}"] = f"{count} occurrences"
                    
            except Exception:
                # TODO: Add proper error handling
                pass  # Silent for now, should log error
        
        return passed, details
    
    def validate_ux(self) -> Tuple[bool, Dict]:
        """Validate user experience."""
        details = {}
        passed = True
        
        # Check for helpful error messages
        error_files = []
        for file in Path('.').rglob('*.py'):
            if 'error' in file.name.lower():
                error_files.append(file)
        
        if len(error_files) < 1:
            details["no_error_handling"] = "No dedicated error handling"
            passed = False
        
        # Check for progress indicators
        progress_patterns = ['progress', 'spinner', 'loading']
        has_progress = False
        
        for pattern in progress_patterns:
            try:
                result = subprocess.run(
                    f"grep -r '{pattern}' . --include='*.py' --exclude-dir='.git' | head -1",
                    shell=True,
                    capture_output=True
                )
                if result.stdout:
                    has_progress = True
                    break
            except Exception:
                # TODO: Add proper error handling
                pass  # Silent for now, should log error
        
        if not has_progress:
            details["no_progress"] = "No progress indicators found"
            # Not critical
        
        return passed, details
    
    def generate_report(self):
        """Generate comprehensive validation report."""
        report = f"""
# v1.0 Success Validation Report

**Generated**: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Summary

**Total Validations**: {len(self.results)}
**Passed**: {sum(1 for r in self.results.values() if r['passed'])}
**Failed**: {sum(1 for r in self.results.values() if not r['passed'])}

## Critical Failures

"""
        
        if self.critical_failures:
            for failure in self.critical_failures:
                report += f"- ❌ {failure}\n"
        else:
            report += "✅ No critical failures\n"
        
        report += "\n## Detailed Results\n\n"
        
        for category, result in self.results.items():
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            report += f"### {category}: {status}\n\n"
            
            for key, value in result['details'].items():
                if key != 'critical':
                    if 'ok' in key:
                        report += f"- ✅ {key}: {value}\n"
                    else:
                        report += f"- ❌ {key}: {value}\n"
            
            report += "\n"
        
        report += """
## Release Decision

"""
        
        passed_count = sum(1 for r in self.results.values() if r['passed'])
        total_count = len(self.results)
        
        if self.critical_failures:
            report += "### 🔴 NOT READY FOR RELEASE\n\n"
            report += "Critical failures must be resolved first.\n"
        elif passed_count == total_count:
            report += "### 🟢 READY FOR RELEASE\n\n"
            report += "All validations passed! Ship it! 🚀\n"
        elif passed_count >= total_count * 0.8:
            report += "### 🟡 ALMOST READY\n\n"
            report += "Address remaining issues for a perfect release.\n"
        else:
            report += "### 🔴 NOT READY\n\n"
            report += "Significant work needed before release.\n"
        
        # Save report
        with open('V1_SUCCESS_VALIDATION.md', 'w') as f:
            f.write(report)
        
        print(f"\n📄 Full report saved to: V1_SUCCESS_VALIDATION.md")

def main():
    """Run success validation."""
    validator = SuccessValidator()
    
    print("🚀 Validating Nix for Humanity v1.0 readiness...")
    print("This comprehensive check ensures production quality.\n")
    
    success = validator.run_all_validations()
    
    if success:
        print("\n✅ ALL VALIDATIONS PASSED!")
        print("🎉 Nix for Humanity is ready for v1.0 release!")
    else:
        print("\n❌ Some validations failed.")
        print("📋 See V1_SUCCESS_VALIDATION.md for details.")
        
        if validator.critical_failures:
            print("\n🚨 Critical failures detected:")
            for failure in validator.critical_failures:
                print(f"   - {failure}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())