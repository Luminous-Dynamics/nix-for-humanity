#!/usr/bin/env python3
"""
from typing import List, Optional
Polish Rough Edges - Comprehensive code quality and completeness checker for Nix for Humanity

This script identifies and prioritizes issues that need to be fixed before production release.
"""

import os
import sys
import re
import ast
import json
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class IssueSeverity(Enum):
    CRITICAL = "🚨 CRITICAL"
    HIGH = "⚠️  HIGH"
    MEDIUM = "🔧 MEDIUM"
    LOW = "📝 LOW"
    INFO = "ℹ️  INFO"


class IssueCategory(Enum):
    TEST_FAILURE = "Test Failure"
    MISSING_IMPLEMENTATION = "Missing Implementation"
    TODO_FIXME = "TODO/FIXME"
    ERROR_HANDLING = "Error Handling"
    PERFORMANCE = "Performance"
    IMPORT_ERROR = "Import/Dependency"
    CODE_QUALITY = "Code Quality"
    DOCUMENTATION = "Documentation"
    SECURITY = "Security"
    DEPRECATED = "Deprecated Code"


@dataclass
class Issue:
    category: IssueCategory
    severity: IssueSeverity
    file_path: str
    line_number: Optional[int]
    description: str
    suggestion: str = ""
    code_snippet: str = ""
    
    def __lt__(self, other):
        # Sort by severity first, then category
        severity_order = [IssueSeverity.CRITICAL, IssueSeverity.HIGH, 
                         IssueSeverity.MEDIUM, IssueSeverity.LOW, IssueSeverity.INFO]
        return (severity_order.index(self.severity), self.category.value) < \
               (severity_order.index(other.severity), other.category.value)


class RoughEdgeScanner:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.issues: List[Issue] = []
        self.stats = defaultdict(int)
        
    def scan_all(self):
        """Run all scans and collect issues"""
        print("🔍 Starting comprehensive scan for rough edges...")
        print("=" * 80)
        
        # Run each scanner
        self._run_tests()
        self._scan_todos_and_fixmes()
        self._scan_incomplete_features()
        self._check_error_handling()
        self._scan_performance_issues()
        self._verify_imports()
        self._check_code_quality()
        self._check_deprecated_code()
        self._check_security_issues()
        
        # Sort issues by priority
        self.issues.sort()
        
        # Print summary
        self._print_summary()
        
        # Generate detailed report
        self._generate_report()
        
    def _run_tests(self):
        """Run test suite and identify failures"""
        print("\n📋 Running test suite...")
        
        test_cmd = ["pytest", "-v", "--tb=short", "--no-header", 
                   str(self.project_root / "tests")]
        
        try:
            result = subprocess.run(test_cmd, capture_output=True, text=True, 
                                  cwd=self.project_root)
            
            # Parse test output for failures
            if result.returncode != 0:
                # Extract failed tests
                failed_tests = re.findall(r'FAILED (.+?) - (.+)', result.stdout)
                for test_name, error_msg in failed_tests:
                    self.issues.append(Issue(
                        category=IssueCategory.TEST_FAILURE,
                        severity=IssueSeverity.CRITICAL,
                        file_path=test_name.split('::')[0],
                        line_number=None,
                        description=f"Test failure: {test_name}",
                        suggestion=f"Fix test or implementation: {error_msg}"
                    ))
                    self.stats['test_failures'] += 1
                    
            # Check for skipped tests
            skipped_tests = re.findall(r'SKIPPED \[(\d+)\]', result.stdout)
            if skipped_tests:
                self.stats['skipped_tests'] = int(skipped_tests[0])
                
        except Exception as e:
            self.issues.append(Issue(
                category=IssueCategory.TEST_FAILURE,
                severity=IssueSeverity.HIGH,
                file_path="test_suite",
                line_number=None,
                description=f"Failed to run test suite: {str(e)}",
                suggestion="Ensure pytest is installed and tests are properly configured"
            ))
            
    def _scan_todos_and_fixmes(self):
        """Scan for TODO and FIXME comments"""
        print("\n🔍 Scanning for TODO/FIXME comments...")
        
        patterns = [
            (r'#\\s*TODO:?\\s*(.+)', 'TODO'),
            (r'#\\s*FIXME:?\\s*(.+)', 'FIXME'),
            (r'#\\s*HACK:?\\s*(.+)', 'HACK'),
            (r'#\\s*XXX:?\\s*(.+)', 'XXX'),
            (r'#\\s*BUG:?\\s*(.+)', 'BUG'),
        ]
        
        for py_file in self._get_python_files():
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        for pattern, tag in patterns:
                            match = re.search(pattern, line)
                            if match:
                                severity = IssueSeverity.HIGH if tag in ['FIXME', 'BUG'] else IssueSeverity.MEDIUM
                                self.issues.append(Issue(
                                    category=IssueCategory.TODO_FIXME,
                                    severity=severity,
                                    file_path=str(py_file.relative_to(self.project_root)),
                                    line_number=line_num,
                                    description=f"{tag}: {match.group(1)}",
                                    suggestion=f"Address {tag} comment",
                                    code_snippet=line.strip()
                                ))
                                self.stats[f'{tag.lower()}_count'] += 1
            except Exception as e:
                print(f"Error scanning {py_file}: {e}")
                
    def _scan_incomplete_features(self):
        """Scan for incomplete implementations and stubs"""
        print("\n🔍 Scanning for incomplete features...")
        
        incomplete_patterns = [
            (r'raise\\s+NotImplementedError', 'NotImplementedError'),
            (r'pass\\s*#.*implement', 'Empty implementation'),
            (r'return\\s+None\\s*#.*implement', 'Stub return'),
            (r'\\.\\.\\.', 'Ellipsis placeholder'),
            (r'print\\(["\']Not implemented', 'Not implemented message'),
        ]
        
        for py_file in self._get_python_files():
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for stub functions/methods
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Check for single-line pass/ellipsis bodies
                        if len(node.body) == 1:
                            stmt = node.body[0]
                            if isinstance(stmt, ast.Pass):
                                self.issues.append(Issue(
                                    category=IssueCategory.MISSING_IMPLEMENTATION,
                                    severity=IssueSeverity.HIGH,
                                    file_path=str(py_file.relative_to(self.project_root)),
                                    line_number=node.lineno,
                                    description=f"Empty function: {node.name}",
                                    suggestion="Implement function or remove if not needed"
                                ))
                                self.stats['empty_functions'] += 1
                            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and stmt.value.value == ...:
                                self.issues.append(Issue(
                                    category=IssueCategory.MISSING_IMPLEMENTATION,
                                    severity=IssueSeverity.HIGH,
                                    file_path=str(py_file.relative_to(self.project_root)),
                                    line_number=node.lineno,
                                    description=f"Stub function with ellipsis: {node.name}",
                                    suggestion="Complete implementation"
                                ))
                                self.stats['stub_functions'] += 1
                                
                # Check for pattern matches
                for line_num, line in enumerate(content.splitlines(), 1):
                    for pattern, desc in incomplete_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            self.issues.append(Issue(
                                category=IssueCategory.MISSING_IMPLEMENTATION,
                                severity=IssueSeverity.HIGH,
                                file_path=str(py_file.relative_to(self.project_root)),
                                line_number=line_num,
                                description=desc,
                                suggestion="Complete the implementation",
                                code_snippet=line.strip()
                            ))
                            self.stats['incomplete_implementations'] += 1
                            
            except Exception as e:
                print(f"Error scanning {py_file}: {e}")
                
    def _check_error_handling(self):
        """Check for missing or poor error handling"""
        print("\n🔍 Checking error handling...")
        
        for py_file in self._get_python_files():
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                tree = ast.parse(content)
                
                # Check for bare except clauses
                for node in ast.walk(tree):
                    if isinstance(node, ast.ExceptHandler):
                        if node.type is None:  # bare except
                            self.issues.append(Issue(
                                category=IssueCategory.ERROR_HANDLING,
                                severity=IssueSeverity.MEDIUM,
                                file_path=str(py_file.relative_to(self.project_root)),
                                line_number=node.lineno,
                                description="Bare except clause",
                                suggestion="Specify exception type or use Exception"
                            ))
                            self.stats['bare_excepts'] += 1
                            
                    # Check for empty except blocks
                    if isinstance(node, ast.ExceptHandler):
                        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                            self.issues.append(Issue(
                                category=IssueCategory.ERROR_HANDLING,
                                severity=IssueSeverity.HIGH,
                                file_path=str(py_file.relative_to(self.project_root)),
                                line_number=node.lineno,
                                description="Empty except block (silently swallowing errors)",
                                suggestion="Log the error or handle it appropriately"
                            ))
                            self.stats['empty_excepts'] += 1
                            
                # Check for missing error handling in critical functions
                critical_patterns = [
                    (r'open\\s*\\(', 'File operations without error handling'),
                    (r'subprocess\\.(run|call|check_output)', 'Subprocess without error handling'),
                    (r'requests\\.(get|post|put|delete)', 'HTTP requests without error handling'),
                    (r'json\\.loads?\\s*\\(', 'JSON parsing without error handling'),
                ]
                
                for line_num, line in enumerate(content.splitlines(), 1):
                    for pattern, desc in critical_patterns:
                        if re.search(pattern, line):
                            # Simple heuristic: check if within try block
                            # (This is simplified; proper AST analysis would be better)
                            if not any(word in content.splitlines()[max(0, line_num-5):line_num] 
                                      for word in ['try:', 'except']):
                                self.issues.append(Issue(
                                    category=IssueCategory.ERROR_HANDLING,
                                    severity=IssueSeverity.MEDIUM,
                                    file_path=str(py_file.relative_to(self.project_root)),
                                    line_number=line_num,
                                    description=desc,
                                    suggestion="Add try/except block for error handling",
                                    code_snippet=line.strip()
                                ))
                                self.stats['missing_error_handling'] += 1
                                
            except Exception as e:
                print(f"Error checking {py_file}: {e}")
                
    def _scan_performance_issues(self):
        """Scan for potential performance bottlenecks"""
        print("\n🔍 Scanning for performance issues...")
        
        performance_patterns = [
            (r'time\\.sleep\\s*\\(\\s*(\\d+)', 'Long sleep duration', IssueSeverity.MEDIUM),
            (r'for .+ in .+:\\s*for .+ in .+:', 'Nested loops', IssueSeverity.LOW),
            (r'\\.append\\(.+\\)\\s*#.*loop', 'List append in loop', IssueSeverity.LOW),
            (r'subprocess\\.(run|call).*shell=True', 'Shell=True in subprocess', IssueSeverity.HIGH),
            (r'eval\\s*\\(', 'Use of eval()', IssueSeverity.CRITICAL),
            (r'exec\\s*\\(', 'Use of exec()', IssueSeverity.CRITICAL),
        ]
        
        for py_file in self._get_python_files():
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for line_num, line in enumerate(content.splitlines(), 1):
                    for pattern, desc, severity in performance_patterns:
                        match = re.search(pattern, line)
                        if match:
                            self.issues.append(Issue(
                                category=IssueCategory.PERFORMANCE,
                                severity=severity,
                                file_path=str(py_file.relative_to(self.project_root)),
                                line_number=line_num,
                                description=desc,
                                suggestion="Consider optimizing for better performance",
                                code_snippet=line.strip()
                            ))
                            self.stats['performance_issues'] += 1
                            
            except Exception as e:
                print(f"Error scanning {py_file}: {e}")
                
    def _verify_imports(self):
        """Verify all imports and check for missing dependencies"""
        print("\n🔍 Verifying imports and dependencies...")
        
        for py_file in self._get_python_files():
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        module_name = None
                        if isinstance(node, ast.Import):
                            module_name = node.names[0].name
                        elif isinstance(node, ast.ImportFrom) and node.module:
                            module_name = node.module
                            
                        if module_name:
                            # Try to import the module
                            try:
                                __import__(module_name)
                            except ImportError as e:
                                # Check if it's a relative import within the project
                                if not module_name.startswith('.'):
                                    self.issues.append(Issue(
                                        category=IssueCategory.IMPORT_ERROR,
                                        severity=IssueSeverity.HIGH,
                                        file_path=str(py_file.relative_to(self.project_root)),
                                        line_number=node.lineno,
                                        description=f"Import error: {module_name}",
                                        suggestion=f"Install missing dependency or fix import path: {str(e)}"
                                    ))
                                    self.stats['import_errors'] += 1
                                    
            except Exception as e:
                print(f"Error verifying imports in {py_file}: {e}")
                
    def _check_code_quality(self):
        """Check for general code quality issues"""
        print("\n🔍 Checking code quality...")
        
        quality_patterns = [
            (r'print\\s*\\(', 'Debug print statement', IssueSeverity.LOW),
            (r'#\\s*print', 'Commented out print', IssueSeverity.INFO),
            (r'import\\s+\\*', 'Star import', IssueSeverity.MEDIUM),
            (r'global\\s+', 'Use of global', IssueSeverity.MEDIUM),
            (r'assert\\s+', 'Assert in production code', IssueSeverity.LOW),
            (r'^\\s*#.*\\btemporary\\b', 'Temporary code', IssueSeverity.MEDIUM),
            (r'^\\s*#.*\\bhack\\b', 'Hack comment', IssueSeverity.MEDIUM),
        ]
        
        for py_file in self._get_python_files():
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check line length
                for line_num, line in enumerate(content.splitlines(), 1):
                    if len(line) > 120:
                        self.issues.append(Issue(
                            category=IssueCategory.CODE_QUALITY,
                            severity=IssueSeverity.INFO,
                            file_path=str(py_file.relative_to(self.project_root)),
                            line_number=line_num,
                            description=f"Line too long ({len(line)} characters)",
                            suggestion="Break line to improve readability"
                        ))
                        self.stats['long_lines'] += 1
                        
                    # Check patterns
                    for pattern, desc, severity in quality_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            self.issues.append(Issue(
                                category=IssueCategory.CODE_QUALITY,
                                severity=severity,
                                file_path=str(py_file.relative_to(self.project_root)),
                                line_number=line_num,
                                description=desc,
                                suggestion="Consider refactoring",
                                code_snippet=line.strip()
                            ))
                            self.stats['quality_issues'] += 1
                            
                # Check for large functions
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                        if func_lines > 50:
                            self.issues.append(Issue(
                                category=IssueCategory.CODE_QUALITY,
                                severity=IssueSeverity.LOW,
                                file_path=str(py_file.relative_to(self.project_root)),
                                line_number=node.lineno,
                                description=f"Large function: {node.name} ({func_lines} lines)",
                                suggestion="Consider breaking into smaller functions"
                            ))
                            self.stats['large_functions'] += 1
                            
            except Exception as e:
                print(f"Error checking quality in {py_file}: {e}")
                
    def _check_deprecated_code(self):
        """Check for deprecated patterns and old code"""
        print("\n🔍 Checking for deprecated code...")
        
        deprecated_patterns = [
            (r'\\.format\\s*\\(', 'Old string formatting', 'Use f-strings'),
            (r'%\\s*\\(.*\\)\\s*%', 'Old % formatting', 'Use f-strings'),
            (r'os\\.path\\.join', 'os.path', 'Consider using pathlib'),
            (r'urllib2', 'urllib2', 'Use urllib or requests'),
            (r'\\.has_key\\s*\\(', 'dict.has_key()', 'Use "in" operator'),
        ]
        
        for py_file in self._get_python_files():
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        for pattern, desc, suggestion in deprecated_patterns:
                            if re.search(pattern, line):
                                self.issues.append(Issue(
                                    category=IssueCategory.DEPRECATED,
                                    severity=IssueSeverity.LOW,
                                    file_path=str(py_file.relative_to(self.project_root)),
                                    line_number=line_num,
                                    description=f"Deprecated: {desc}",
                                    suggestion=suggestion,
                                    code_snippet=line.strip()
                                ))
                                self.stats['deprecated_code'] += 1
                                
            except Exception as e:
                print(f"Error checking {py_file}: {e}")
                
    def _check_security_issues(self):
        """Check for potential security issues"""
        print("\n🔍 Checking for security issues...")
        
        security_patterns = [
            (r'pickle\\.loads?\\s*\\(', 'Pickle deserialization', IssueSeverity.HIGH),
            (r'input\\s*\\(.*\\)', 'Raw input() in Python 2 style', IssueSeverity.LOW),
            (r'os\\.system\\s*\\(', 'os.system() call', IssueSeverity.HIGH),
            (r'eval\\s*\\(', 'eval() usage', IssueSeverity.CRITICAL),
            (r'exec\\s*\\(', 'exec() usage', IssueSeverity.CRITICAL),
            (r'__import__\\s*\\(', 'Dynamic import', IssueSeverity.MEDIUM),
            (r'shell\\s*=\\s*True', 'shell=True in subprocess', IssueSeverity.HIGH),
        ]
        
        for py_file in self._get_python_files():
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        for pattern, desc, severity in security_patterns:
                            if re.search(pattern, line):
                                self.issues.append(Issue(
                                    category=IssueCategory.SECURITY,
                                    severity=severity,
                                    file_path=str(py_file.relative_to(self.project_root)),
                                    line_number=line_num,
                                    description=f"Security concern: {desc}",
                                    suggestion="Review for security implications",
                                    code_snippet=line.strip()
                                ))
                                self.stats['security_issues'] += 1
                                
            except Exception as e:
                print(f"Error checking {py_file}: {e}")
                
    def _get_python_files(self) -> List[Path]:
        """Get all Python files in the project"""
        python_files = []
        exclude_dirs = {'__pycache__', '.git', 'venv', 'env', '.venv', 
                       'node_modules', 'dist', 'build', '.pytest_cache'}
        
        for root, dirs, files in os.walk(self.project_root):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
                    
        return python_files
        
    def _print_summary(self):
        """Print a summary of findings"""
        print("\n" + "=" * 80)
        print("📊 SCAN SUMMARY")
        print("=" * 80)
        
        # Count by severity
        severity_counts = defaultdict(int)
        category_counts = defaultdict(int)
        
        for issue in self.issues:
            severity_counts[issue.severity] += 1
            category_counts[issue.category] += 1
            
        print("\n🎯 Issues by Severity:")
        for severity in IssueSeverity:
            count = severity_counts[severity]
            if count > 0:
                print(f"  {severity.value}: {count}")
                
        print("\n📁 Issues by Category:")
        for category in IssueCategory:
            count = category_counts[category]
            if count > 0:
                print(f"  {category.value}: {count}")
                
        print("\n📈 Additional Statistics:")
        for stat, count in sorted(self.stats.items()):
            if count > 0:
                print(f"  {stat.replace('_', ' ').title()}: {count}")
                
        print(f"\n🔢 Total Issues Found: {len(self.issues)}")
        
    def _generate_report(self):
        """Generate detailed report file"""
        report_path = self.project_root / "rough-edges-report.md"
        
        with open(report_path, 'w') as f:
            f.write("# Nix for Humanity - Rough Edges Report\n\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Executive Summary
            f.write("## Executive Summary\n\n")
            
            critical_count = sum(1 for i in self.issues if i.severity == IssueSeverity.CRITICAL)
            high_count = sum(1 for i in self.issues if i.severity == IssueSeverity.HIGH)
            
            if critical_count > 0:
                f.write(f"**⚠️ {critical_count} CRITICAL issues require immediate attention!**\n\n")
            if high_count > 0:
                f.write(f"**🔧 {high_count} HIGH priority issues should be addressed before release.**\n\n")
                
            f.write(f"Total issues found: {len(self.issues)}\n\n")
            
            # Priority Action Items
            f.write("## Priority Action Items\n\n")
            
            # Group critical and high priority items
            priority_issues = [i for i in self.issues 
                             if i.severity in [IssueSeverity.CRITICAL, IssueSeverity.HIGH]]
            
            if priority_issues:
                f.write("### Must Fix Before Release:\n\n")
                for i, issue in enumerate(priority_issues[:10], 1):
                    f.write(f"{i}. **{issue.severity.value}** - {issue.category.value}: "
                           f"{issue.description}\n")
                    f.write(f"   - File: `{issue.file_path}`")
                    if issue.line_number:
                        f.write(f" (line {issue.line_number})")
                    f.write("\n")
                    if issue.suggestion:
                        f.write(f"   - Suggestion: {issue.suggestion}\n")
                    f.write("\n")
                    
            # Detailed Issues by Category
            f.write("\n## Detailed Issues by Category\n\n")
            
            # Group by category
            issues_by_category = defaultdict(list)
            for issue in self.issues:
                issues_by_category[issue.category].append(issue)
                
            for category in IssueCategory:
                if category in issues_by_category:
                    f.write(f"### {category.value}\n\n")
                    
                    # Further group by severity within category
                    by_severity = defaultdict(list)
                    for issue in issues_by_category[category]:
                        by_severity[issue.severity].append(issue)
                        
                    for severity in IssueSeverity:
                        if severity in by_severity:
                            f.write(f"#### {severity.value}\n\n")
                            for issue in by_severity[severity]:
                                f.write(f"- `{issue.file_path}`")
                                if issue.line_number:
                                    f.write(f":{issue.line_number}")
                                f.write(f" - {issue.description}\n")
                                if issue.code_snippet:
                                    f.write(f"  ```python\n  {issue.code_snippet}\n  ```\n")
                                if issue.suggestion:
                                    f.write(f"  > {issue.suggestion}\n")
                                f.write("\n")
                                
            # Recommendations
            f.write("\n## Recommendations\n\n")
            
            if critical_count > 0:
                f.write("1. **Address all CRITICAL issues immediately** - "
                       "These represent serious bugs or security vulnerabilities.\n\n")
                
            if self.stats.get('test_failures', 0) > 0:
                f.write("2. **Fix failing tests** - "
                       f"{self.stats['test_failures']} tests are currently failing.\n\n")
                
            if self.stats.get('missing_error_handling', 0) > 10:
                f.write("3. **Improve error handling** - "
                       "Many critical operations lack proper error handling.\n\n")
                
            if self.stats.get('todo_count', 0) + self.stats.get('fixme_count', 0) > 20:
                f.write("4. **Address technical debt** - "
                       f"{self.stats.get('todo_count', 0) + self.stats.get('fixme_count', 0)} "
                       "TODO/FIXME items need attention.\n\n")
                
            if self.stats.get('security_issues', 0) > 0:
                f.write("5. **Security review needed** - "
                       f"{self.stats['security_issues']} potential security issues found.\n\n")
                
            # Next Steps
            f.write("\n## Next Steps\n\n")
            f.write("1. Review and fix all CRITICAL issues\n")
            f.write("2. Address HIGH priority issues\n")
            f.write("3. Run tests again after fixes\n")
            f.write("4. Consider refactoring areas with multiple issues\n")
            f.write("5. Update documentation for any API changes\n")
            
        print(f"\n📄 Detailed report saved to: {report_path}")
        

def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent
    
    scanner = RoughEdgeScanner(project_root)
    scanner.scan_all()
    
    # Return exit code based on critical issues
    critical_count = sum(1 for i in scanner.issues if i.severity == IssueSeverity.CRITICAL)
    return 1 if critical_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())