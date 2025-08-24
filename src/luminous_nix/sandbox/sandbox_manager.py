"""
Sandbox Manager for Safe AI Self-Modification

This provides a safe environment for the AI to modify its own code
without risking the production system.
"""

import tempfile
import shutil
import subprocess
import json
import ast
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import hashlib
import sys
import os


class SandboxManager:
    """Manages isolated sandbox environments for AI modifications"""
    
    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path.cwd()
        self.sandbox_dir = None
        self.original_branch = None
        self.sandbox_id = None
        self.modification_log = []
        
    def create_sandbox(self) -> Path:
        """Create an isolated sandbox environment"""
        # Generate unique sandbox ID
        self.sandbox_id = f"sandbox_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.getpid()}"
        
        # Create temporary directory
        self.sandbox_dir = Path(tempfile.mkdtemp(prefix=f"ai_{self.sandbox_id}_"))
        
        print(f"🛡️ Creating sandbox: {self.sandbox_id}")
        print(f"📁 Location: {self.sandbox_dir}")
        
        # Copy source code (excluding .git for speed, we'll init fresh)
        self._copy_source_code()
        
        # Initialize git for tracking changes
        self._init_git()
        
        # Create virtual environment
        self._create_venv()
        
        # Log creation
        self.modification_log.append({
            "action": "sandbox_created",
            "timestamp": datetime.now().isoformat(),
            "path": str(self.sandbox_dir)
        })
        
        print(f"✅ Sandbox ready: {self.sandbox_dir}")
        return self.sandbox_dir
    
    def _copy_source_code(self):
        """Copy source code to sandbox, excluding unnecessary files"""
        exclude_patterns = [
            ".git", "__pycache__", "*.pyc", ".pytest_cache",
            "node_modules", "target", "dist", "build",
            ".venv", "venv", "env"
        ]
        
        def should_exclude(path: Path) -> bool:
            for pattern in exclude_patterns:
                if pattern in str(path):
                    return True
            return False
        
        # Copy files
        for item in self.base_path.rglob("*"):
            if item.is_file() and not should_exclude(item):
                relative = item.relative_to(self.base_path)
                target = self.sandbox_dir / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target)
    
    def _init_git(self):
        """Initialize git in sandbox for tracking changes"""
        subprocess.run(
            ["git", "init"],
            cwd=self.sandbox_dir,
            capture_output=True,
            check=True
        )
        
        subprocess.run(
            ["git", "config", "user.email", "ai@luminous.local"],
            cwd=self.sandbox_dir,
            capture_output=True
        )
        
        subprocess.run(
            ["git", "config", "user.name", "AI Self-Modifier"],
            cwd=self.sandbox_dir,
            capture_output=True
        )
        
        # Initial commit
        subprocess.run(
            ["git", "add", "."],
            cwd=self.sandbox_dir,
            capture_output=True
        )
        
        subprocess.run(
            ["git", "commit", "-m", "Initial sandbox state"],
            cwd=self.sandbox_dir,
            capture_output=True
        )
    
    def _create_venv(self):
        """Create virtual environment in sandbox"""
        venv_path = self.sandbox_dir / "venv"
        
        # Create venv
        subprocess.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            capture_output=True,
            check=True
        )
        
        # Install dependencies if requirements.txt exists
        req_file = self.sandbox_dir / "requirements.txt"
        if req_file.exists():
            pip_cmd = venv_path / "bin" / "pip"
            subprocess.run(
                [str(pip_cmd), "install", "-r", str(req_file)],
                capture_output=True
            )
        
        # Install poetry dependencies if pyproject.toml exists
        if (self.sandbox_dir / "pyproject.toml").exists():
            pip_cmd = venv_path / "bin" / "pip"
            subprocess.run(
                [str(pip_cmd), "install", "poetry"],
                capture_output=True
            )
            poetry_cmd = venv_path / "bin" / "poetry"
            subprocess.run(
                [str(poetry_cmd), "install"],
                cwd=self.sandbox_dir,
                capture_output=True
            )
    
    def apply_modification(self, modification: Dict[str, Any]) -> bool:
        """Apply a modification in the sandbox"""
        if not self.sandbox_dir:
            raise RuntimeError("No sandbox created")
        
        print(f"🔧 Applying modification: {modification.get('description', 'unnamed')}")
        
        success = True
        for file_mod in modification.get("file_modifications", []):
            file_path = self.sandbox_dir / file_mod["path"]
            
            if not file_path.exists():
                print(f"❌ File not found: {file_path}")
                success = False
                continue
            
            # Backup original
            backup_path = file_path.with_suffix(file_path.suffix + ".backup")
            shutil.copy2(file_path, backup_path)
            
            try:
                # Apply modification based on type
                if file_mod["type"] == "replace":
                    self._apply_replace(file_path, file_mod)
                elif file_mod["type"] == "ast_transform":
                    self._apply_ast_transform(file_path, file_mod)
                elif file_mod["type"] == "insert":
                    self._apply_insert(file_path, file_mod)
                
                print(f"✅ Modified: {file_mod['path']}")
                
            except Exception as e:
                print(f"❌ Failed to modify {file_mod['path']}: {e}")
                # Restore backup
                shutil.move(backup_path, file_path)
                success = False
        
        # Commit changes
        if success:
            self._commit_changes(modification.get("description", "AI modification"))
        
        self.modification_log.append({
            "action": "modification_applied",
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "description": modification.get("description")
        })
        
        return success
    
    def _apply_replace(self, file_path: Path, modification: Dict):
        """Apply a simple text replacement"""
        content = file_path.read_text()
        content = content.replace(
            modification["old_text"],
            modification["new_text"]
        )
        file_path.write_text(content)
    
    def _apply_ast_transform(self, file_path: Path, modification: Dict):
        """Apply an AST-based transformation (safer for Python code)"""
        source = file_path.read_text()
        tree = ast.parse(source)
        
        # Apply transformation (simplified example)
        transformer = modification.get("transformer")
        if transformer:
            tree = transformer(tree)
        
        # Convert back to source
        import astor  # Would need to install
        new_source = astor.to_source(tree)
        file_path.write_text(new_source)
    
    def _apply_insert(self, file_path: Path, modification: Dict):
        """Insert text at a specific location"""
        lines = file_path.read_text().splitlines()
        line_num = modification.get("line", len(lines))
        lines.insert(line_num, modification["text"])
        file_path.write_text("\n".join(lines))
    
    def _commit_changes(self, message: str):
        """Commit current changes in sandbox"""
        subprocess.run(
            ["git", "add", "."],
            cwd=self.sandbox_dir,
            capture_output=True
        )
        
        subprocess.run(
            ["git", "commit", "-m", f"AI Modification: {message}"],
            cwd=self.sandbox_dir,
            capture_output=True
        )
    
    def run_tests(self) -> Tuple[bool, List[Dict]]:
        """Run test suite in sandbox"""
        if not self.sandbox_dir:
            raise RuntimeError("No sandbox created")
        
        print("🧪 Running tests in sandbox...")
        
        results = []
        
        # Run pytest if available
        pytest_cmd = self.sandbox_dir / "venv" / "bin" / "pytest"
        if pytest_cmd.exists():
            result = subprocess.run(
                [str(pytest_cmd), "--json-report", "--json-report-file=test_results.json"],
                cwd=self.sandbox_dir,
                capture_output=True
            )
            
            results.append({
                "type": "pytest",
                "passed": result.returncode == 0,
                "output": result.stdout.decode()
            })
        
        # Run custom tests
        test_script = self.sandbox_dir / "run_tests.py"
        if test_script.exists():
            python_cmd = self.sandbox_dir / "venv" / "bin" / "python"
            result = subprocess.run(
                [str(python_cmd), str(test_script)],
                cwd=self.sandbox_dir,
                capture_output=True
            )
            
            results.append({
                "type": "custom",
                "passed": result.returncode == 0,
                "output": result.stdout.decode()
            })
        
        all_passed = all(r["passed"] for r in results)
        
        self.modification_log.append({
            "action": "tests_run",
            "timestamp": datetime.now().isoformat(),
            "passed": all_passed,
            "results": results
        })
        
        return all_passed, results
    
    def run_security_scan(self) -> Tuple[bool, List[Dict]]:
        """Run security scanning in sandbox"""
        print("🔒 Running security scan...")
        
        issues = []
        
        # Check for dangerous patterns
        dangerous_patterns = [
            (r"exec\(", "Arbitrary code execution"),
            (r"eval\(", "Eval usage"),
            (r"__import__", "Dynamic import"),
            (r"subprocess.*shell=True", "Shell injection risk"),
            (r"os\.system", "System call"),
        ]
        
        for py_file in self.sandbox_dir.rglob("*.py"):
            content = py_file.read_text()
            for pattern, description in dangerous_patterns:
                import re
                if re.search(pattern, content):
                    issues.append({
                        "file": str(py_file.relative_to(self.sandbox_dir)),
                        "issue": description,
                        "severity": "high"
                    })
        
        # Run bandit if available
        bandit_cmd = self.sandbox_dir / "venv" / "bin" / "bandit"
        if bandit_cmd.exists():
            result = subprocess.run(
                [str(bandit_cmd), "-r", ".", "-f", "json"],
                cwd=self.sandbox_dir,
                capture_output=True
            )
            
            if result.stdout:
                bandit_results = json.loads(result.stdout)
                for issue in bandit_results.get("results", []):
                    issues.append({
                        "file": issue["filename"],
                        "issue": issue["issue_text"],
                        "severity": issue["issue_severity"]
                    })
        
        passed = len([i for i in issues if i["severity"] == "high"]) == 0
        
        self.modification_log.append({
            "action": "security_scan",
            "timestamp": datetime.now().isoformat(),
            "passed": passed,
            "issues": issues
        })
        
        return passed, issues
    
    def get_diff(self) -> str:
        """Get diff of changes made in sandbox"""
        if not self.sandbox_dir:
            return ""
        
        result = subprocess.run(
            ["git", "diff", "HEAD~1"],
            cwd=self.sandbox_dir,
            capture_output=True,
            text=True
        )
        
        return result.stdout
    
    def export_changes(self, output_path: Path) -> bool:
        """Export validated changes as a patch file"""
        if not self.sandbox_dir:
            return False
        
        print(f"📦 Exporting changes to {output_path}")
        
        # Create patch
        result = subprocess.run(
            ["git", "format-patch", "-1", "--stdout"],
            cwd=self.sandbox_dir,
            capture_output=True,
            text=True
        )
        
        output_path.write_text(result.stdout)
        
        # Also save metadata
        metadata_path = output_path.with_suffix(".json")
        metadata = {
            "sandbox_id": self.sandbox_id,
            "created": self.modification_log[0]["timestamp"],
            "modifications": len([l for l in self.modification_log if l["action"] == "modification_applied"]),
            "tests_passed": any(l["passed"] for l in self.modification_log if l["action"] == "tests_run"),
            "security_passed": any(l["passed"] for l in self.modification_log if l["action"] == "security_scan"),
            "log": self.modification_log
        }
        
        metadata_path.write_text(json.dumps(metadata, indent=2))
        
        print(f"✅ Changes exported to {output_path}")
        return True
    
    def cleanup(self):
        """Clean up sandbox environment"""
        if self.sandbox_dir and self.sandbox_dir.exists():
            print(f"🧹 Cleaning up sandbox: {self.sandbox_dir}")
            shutil.rmtree(self.sandbox_dir)
            self.sandbox_dir = None
    
    def __enter__(self):
        """Context manager entry"""
        self.create_sandbox()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()


class SafetyValidator:
    """Validates that modifications are safe to apply"""
    
    @staticmethod
    def validate_modification(modification: Dict) -> Tuple[bool, List[str]]:
        """Validate a modification request"""
        issues = []
        
        # Check file count
        file_count = len(modification.get("file_modifications", []))
        if file_count > 10:
            issues.append(f"Too many files modified ({file_count} > 10)")
        
        # Check for forbidden files
        forbidden_patterns = [
            "sandbox_manager.py",
            "safety_validator.py",
            ".git",
            "*.key",
            "*.pem"
        ]
        
        for file_mod in modification.get("file_modifications", []):
            path = file_mod["path"]
            for pattern in forbidden_patterns:
                if pattern in path:
                    issues.append(f"Forbidden file: {path}")
        
        # Check modification size
        for file_mod in modification.get("file_modifications", []):
            if "new_text" in file_mod:
                lines = file_mod["new_text"].count("\n")
                if lines > 500:
                    issues.append(f"Modification too large: {lines} lines")
        
        return len(issues) == 0, issues


class ModificationRequest:
    """Standard format for AI modification requests"""
    
    def __init__(self, description: str = ""):
        self.id = hashlib.md5(f"{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        self.timestamp = datetime.now()
        self.description = description
        self.file_modifications = []
        self.tests = []
        self.risk_level = "low"  # low/medium/high
        self.requires_human_review = True
    
    def add_file_modification(self, path: str, mod_type: str, **kwargs):
        """Add a file modification"""
        self.file_modifications.append({
            "path": path,
            "type": mod_type,  # replace/insert/ast_transform
            **kwargs
        })
    
    def add_test(self, test_type: str, test_spec: Dict):
        """Add a test that must pass"""
        self.tests.append({
            "type": test_type,
            "spec": test_spec
        })
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "description": self.description,
            "file_modifications": self.file_modifications,
            "tests": self.tests,
            "risk_level": self.risk_level,
            "requires_human_review": self.requires_human_review
        }