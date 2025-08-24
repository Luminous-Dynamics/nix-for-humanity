"""
Code Quality Tools Integration
Ruff, MyPy, Bandit, Black, and Semgrep for pristine code
"""

import subprocess
import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

@dataclass
class QualityReport:
    """Comprehensive code quality report"""
    linting_errors: List[Dict[str, Any]] = field(default_factory=list)
    type_errors: List[Dict[str, Any]] = field(default_factory=list)
    security_issues: List[Dict[str, Any]] = field(default_factory=list)
    formatting_changes: List[str] = field(default_factory=list)
    complexity_metrics: Dict[str, Any] = field(default_factory=dict)
    passed: bool = False
    score: float = 0.0
    
    def to_markdown(self) -> str:
        """Generate markdown report"""
        md = "# Code Quality Report\n\n"
        
        # Overall score
        md += f"## Overall Score: {self.score:.1f}/100\n\n"
        
        # Linting
        md += f"### 🔍 Linting ({len(self.linting_errors)} issues)\n"
        if self.linting_errors:
            for error in self.linting_errors[:5]:
                md += f"- {error['file']}:{error['line']} - {error['message']}\n"
        else:
            md += "✅ No linting issues found!\n"
        md += "\n"
        
        # Type checking
        md += f"### 📝 Type Checking ({len(self.type_errors)} issues)\n"
        if self.type_errors:
            for error in self.type_errors[:5]:
                md += f"- {error['file']}:{error['line']} - {error['message']}\n"
        else:
            md += "✅ All types check out!\n"
        md += "\n"
        
        # Security
        md += f"### 🔒 Security ({len(self.security_issues)} issues)\n"
        if self.security_issues:
            for issue in self.security_issues[:5]:
                md += f"- **{issue['severity']}**: {issue['message']} ({issue['file']})\n"
        else:
            md += "✅ No security vulnerabilities detected!\n"
        md += "\n"
        
        # Complexity
        if self.complexity_metrics:
            md += "### 📊 Complexity Metrics\n"
            for metric, value in self.complexity_metrics.items():
                md += f"- {metric}: {value}\n"
        
        return md
        

class RuffLinter:
    """Ultra-fast Python linting with Ruff (100x faster than flake8)"""
    
    @staticmethod
    async def lint(path: Path, fix: bool = False) -> List[Dict[str, Any]]:
        """Run Ruff linter on code"""
        cmd = ["ruff", "check", str(path), "--output-format", "json"]
        
        if fix:
            cmd.append("--fix")
            
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        issues = []
        if stdout:
            try:
                # Ruff outputs JSON array of violations
                violations = json.loads(stdout.decode())
                for v in violations:
                    issues.append({
                        "file": v.get("filename", ""),
                        "line": v.get("location", {}).get("row", 0),
                        "column": v.get("location", {}).get("column", 0),
                        "code": v.get("code", ""),
                        "message": v.get("message", ""),
                        "fixable": v.get("fix") is not None
                    })
            except json.JSONDecodeError:
                logger.error(f"Failed to parse Ruff output: {stdout.decode()}")
                
        return issues
        
    @staticmethod
    async def format(path: Path) -> bool:
        """Format code with Ruff formatter"""
        cmd = ["ruff", "format", str(path)]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        await process.communicate()
        return process.returncode == 0
        

class MyPyChecker:
    """Static type checking with MyPy"""
    
    @staticmethod
    async def check(path: Path, strict: bool = False) -> List[Dict[str, Any]]:
        """Run MyPy type checker"""
        cmd = ["mypy", str(path), "--output", "json"]
        
        if strict:
            cmd.append("--strict")
            
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        errors = []
        if stdout:
            # MyPy outputs one JSON object per line
            for line in stdout.decode().split('\n'):
                if line.strip():
                    try:
                        error = json.loads(line)
                        errors.append({
                            "file": error.get("file", ""),
                            "line": error.get("line", 0),
                            "column": error.get("column", 0),
                            "message": error.get("message", ""),
                            "severity": error.get("severity", "error")
                        })
                    except json.JSONDecodeError:
                        pass
                        
        return errors
        

class BanditScanner:
    """Security vulnerability scanning with Bandit"""
    
    @staticmethod
    async def scan(path: Path, severity_level: str = "low") -> List[Dict[str, Any]]:
        """Scan for security issues"""
        cmd = [
            "bandit",
            "-r", str(path),
            "-f", "json",
            "-ll" if severity_level == "low" else "-l"
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        issues = []
        if stdout:
            try:
                result = json.loads(stdout.decode())
                for issue in result.get("results", []):
                    issues.append({
                        "file": issue.get("filename", ""),
                        "line": issue.get("line_number", 0),
                        "severity": issue.get("issue_severity", ""),
                        "confidence": issue.get("issue_confidence", ""),
                        "message": issue.get("issue_text", ""),
                        "test_id": issue.get("test_id", "")
                    })
            except json.JSONDecodeError:
                logger.error("Failed to parse Bandit output")
                
        return issues
        

class BlackFormatter:
    """Code formatting with Black"""
    
    @staticmethod
    async def format(path: Path, check_only: bool = False) -> Tuple[bool, List[str]]:
        """Format code with Black"""
        cmd = ["black", str(path)]
        
        if check_only:
            cmd.append("--check")
            cmd.append("--diff")
            
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        changes = []
        if check_only and stdout:
            # Parse diff output
            for line in stdout.decode().split('\n'):
                if line.startswith('+') or line.startswith('-'):
                    changes.append(line)
                    
        return process.returncode == 0, changes
        

class SemgrepAnalyzer:
    """Advanced pattern-based static analysis with Semgrep"""
    
    @staticmethod
    async def analyze(
        path: Path,
        config: str = "auto"  # auto, python, security
    ) -> List[Dict[str, Any]]:
        """Run Semgrep analysis"""
        cmd = [
            "semgrep",
            "--config", config,
            "--json",
            str(path)
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        findings = []
        if stdout:
            try:
                result = json.loads(stdout.decode())
                for finding in result.get("results", []):
                    findings.append({
                        "file": finding.get("path", ""),
                        "line": finding.get("start", {}).get("line", 0),
                        "message": finding.get("extra", {}).get("message", ""),
                        "severity": finding.get("extra", {}).get("severity", ""),
                        "rule_id": finding.get("check_id", "")
                    })
            except json.JSONDecodeError:
                logger.error("Failed to parse Semgrep output")
                
        return findings
        

class CodeQualityOrchestrator:
    """Orchestrate all code quality tools"""
    
    def __init__(self):
        self.ruff = RuffLinter
        self.mypy = MyPyChecker
        self.bandit = BanditScanner
        self.black = BlackFormatter
        self.semgrep = SemgrepAnalyzer
        
    async def full_quality_check(
        self,
        path: Path,
        fix: bool = False,
        strict: bool = False
    ) -> QualityReport:
        """Run comprehensive quality check"""
        
        report = QualityReport()
        
        # Run all checks in parallel
        tasks = [
            self.ruff.lint(path, fix=fix),
            self.mypy.check(path, strict=strict),
            self.bandit.scan(path),
            self.black.format(path, check_only=not fix),
            self.semgrep.analyze(path)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        if not isinstance(results[0], Exception):
            report.linting_errors = results[0]
            
        if not isinstance(results[1], Exception):
            report.type_errors = results[1]
            
        if not isinstance(results[2], Exception):
            report.security_issues = results[2]
            
        if not isinstance(results[3], Exception):
            formatted, changes = results[3]
            report.formatting_changes = changes
            
        if not isinstance(results[4], Exception):
            # Add semgrep findings to security issues
            for finding in results[4]:
                report.security_issues.append(finding)
                
        # Calculate score
        total_issues = (
            len(report.linting_errors) +
            len(report.type_errors) +
            len(report.security_issues) +
            len(report.formatting_changes)
        )
        
        # Score calculation (100 = perfect)
        if total_issues == 0:
            report.score = 100.0
        else:
            # Deduct points for issues
            deduction = min(total_issues * 2, 100)
            report.score = max(0, 100 - deduction)
            
        report.passed = report.score >= 70.0
        
        return report
        
    async def auto_fix(self, path: Path) -> Dict[str, Any]:
        """Automatically fix what can be fixed"""
        
        fixes_applied = {
            "ruff_fixes": 0,
            "formatting": False,
            "security_patches": 0
        }
        
        # Run Ruff with fix
        before_issues = await self.ruff.lint(path)
        after_issues = await self.ruff.lint(path, fix=True)
        fixes_applied["ruff_fixes"] = len(before_issues) - len(after_issues)
        
        # Format with Black
        formatted, _ = await self.black.format(path)
        fixes_applied["formatting"] = formatted
        
        logger.info(f"Applied fixes: {fixes_applied}")
        return fixes_applied
        
    async def ci_check(self, path: Path) -> bool:
        """CI/CD quality gate check"""
        report = await self.full_quality_check(path, strict=True)
        
        # Generate report
        print(report.to_markdown())
        
        # Fail if score too low
        if not report.passed:
            logger.error(f"Quality check failed! Score: {report.score}/100")
            return False
            
        logger.info(f"Quality check passed! Score: {report.score}/100")
        return True
        

# Pre-commit hook integration
async def pre_commit_quality_check():
    """Run quality checks before commit"""
    
    orchestrator = CodeQualityOrchestrator()
    
    # Get staged files
    process = await asyncio.create_subprocess_exec(
        "git", "diff", "--cached", "--name-only", "--diff-filter=ACMR",
        stdout=asyncio.subprocess.PIPE
    )
    
    stdout, _ = await process.communicate()
    files = stdout.decode().strip().split('\n')
    
    # Filter Python files
    python_files = [f for f in files if f.endswith('.py')]
    
    if not python_files:
        return True
        
    # Check each file
    all_passed = True
    for file in python_files:
        path = Path(file)
        if path.exists():
            report = await orchestrator.full_quality_check(path)
            if not report.passed:
                print(f"❌ {file} failed quality check (score: {report.score})")
                all_passed = False
            else:
                print(f"✅ {file} passed (score: {report.score})")
                
    return all_passed
    

# GitHub Actions integration
async def github_actions_quality():
    """Quality check for GitHub Actions"""
    
    orchestrator = CodeQualityOrchestrator()
    
    # Check entire src directory
    src_path = Path("src")
    report = await orchestrator.full_quality_check(src_path)
    
    # Generate report as GitHub Actions annotation
    for error in report.linting_errors:
        print(f"::error file={error['file']},line={error['line']}::{error['message']}")
        
    for error in report.type_errors:
        print(f"::warning file={error['file']},line={error['line']}::{error['message']}")
        
    for issue in report.security_issues:
        level = "error" if issue["severity"] == "HIGH" else "warning"
        print(f"::{level} file={issue['file']},line={issue['line']}::{issue['message']}")
        
    # Set output
    print(f"::set-output name=score::{report.score}")
    print(f"::set-output name=passed::{report.passed}")
    
    return report.passed