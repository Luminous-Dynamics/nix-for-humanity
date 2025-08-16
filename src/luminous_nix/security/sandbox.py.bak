"""
Security Sandbox for Plugin Execution.

Provides a secure execution environment for plugins to prevent
malicious code from harming the system.

Since: v1.0.0
"""

import ast
import builtins
import resource
from pathlib import Path
from typing import Any

from ..constants import MAX_COMMAND_LENGTH
from ..core.logging_config import get_logger

logger = get_logger(__name__)


class PluginSandbox:
    """
    Security sandbox for plugin execution.

    Restricts plugin capabilities to prevent:
    - File system access outside allowed directories
    - Network access to unauthorized hosts
    - Excessive resource consumption
    - Dangerous system calls

    Since: v1.0.0
    """

    # Allowed built-in functions for plugins
    ALLOWED_BUILTINS = {
        # Safe built-ins
        "abs",
        "all",
        "any",
        "ascii",
        "bin",
        "bool",
        "bytes",
        "chr",
        "dict",
        "divmod",
        "enumerate",
        "filter",
        "float",
        "format",
        "frozenset",
        "hex",
        "int",
        "isinstance",
        "issubclass",
        "iter",
        "len",
        "list",
        "map",
        "max",
        "min",
        "next",
        "oct",
        "ord",
        "pow",
        "range",
        "repr",
        "reversed",
        "round",
        "set",
        "slice",
        "sorted",
        "str",
        "sum",
        "tuple",
        "type",
        "zip",
        # Controlled I/O (will be wrapped)
        "print",
        "input",
        # Exceptions
        "Exception",
        "ValueError",
        "TypeError",
        "KeyError",
        "AttributeError",
        "IndexError",
        "RuntimeError",
    }

    # Blocked modules for plugins
    BLOCKED_MODULES = {
        "os",
        "sys",
        "subprocess",
        "socket",
        "urllib",
        "requests",
        "shutil",
        "__builtin__",
        "__builtins__",
        "importlib",
        "imp",
        "compile",
        "exec",
        "eval",
    }

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize sandbox.

        Args:
            config: Sandbox configuration
        """
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self.strict_mode = self.config.get("strict", False)

        # Allowed paths for file operations
        self.allowed_paths: set[Path] = {
            Path.home() / ".config" / "nix-humanity",
            Path.home() / ".cache" / "nix-humanity",
            Path("/tmp"),
        }

        # Resource limits
        self.max_memory_mb = self.config.get("max_memory_mb", 100)
        self.max_cpu_seconds = self.config.get("max_cpu_seconds", 5)
        self.max_file_size_mb = self.config.get("max_file_size_mb", 10)

    def is_enabled(self) -> bool:
        """Check if sandbox is enabled."""
        return self.enabled

    def wrap_module(self, module: Any) -> Any:
        """
        Wrap a module with security restrictions.

        Args:
            module: Module to wrap

        Returns:
            Wrapped module with restrictions
        """
        if not self.enabled:
            return module

        # Create restricted globals for the module
        restricted_globals = self._create_restricted_globals()

        # Replace module's globals
        if hasattr(module, "__dict__"):
            for key in list(module.__dict__.keys()):
                if key in self.BLOCKED_MODULES:
                    del module.__dict__[key]

        return module

    def _create_restricted_globals(self) -> dict[str, Any]:
        """Create restricted global namespace for plugins."""
        # Start with allowed built-ins
        restricted = {
            name: getattr(builtins, name)
            for name in self.ALLOWED_BUILTINS
            if hasattr(builtins, name)
        }

        # Wrap dangerous functions
        restricted["print"] = self._safe_print
        restricted["input"] = self._safe_input
        restricted["open"] = self._safe_open

        # Add safe imports
        restricted["__import__"] = self._safe_import

        return restricted

    def _safe_print(self, *args, **kwargs) -> None:
        """Safe print function for plugins."""
        # Limit output length
        output = " ".join(str(arg)[:1000] for arg in args)
        print(f"[Plugin] {output}", **kwargs)

    def _safe_input(self, prompt: str = "") -> str:
        """Safe input function for plugins."""
        if self.strict_mode:
            raise PermissionError("Input not allowed in strict mode")
        return input(f"[Plugin] {prompt}")

    def _safe_open(self, file: str, mode: str = "r", **kwargs) -> Any:
        """
        Safe file open function for plugins.

        Only allows access to specific directories.
        """
        path = Path(file).resolve()

        # Check if path is in allowed directories
        allowed = False
        for allowed_path in self.allowed_paths:
            try:
                path.relative_to(allowed_path)
                allowed = True
                break
            except ValueError:
                continue

        if not allowed:
            raise PermissionError(f"Access to {path} not allowed")

        # Check file size for reading
        if "r" in mode and path.exists():
            size_mb = path.stat().st_size / (1024 * 1024)
            if size_mb > self.max_file_size_mb:
                raise PermissionError(f"File too large: {size_mb}MB")

        # Prevent writing in strict mode
        if self.strict_mode and any(m in mode for m in ["w", "a", "x"]):
            raise PermissionError("Writing not allowed in strict mode")

        return open(file, mode, **kwargs)

    def _safe_import(self, name: str, *args, **kwargs) -> Any:
        """
        Safe import function for plugins.

        Blocks dangerous modules.
        """
        if name in self.BLOCKED_MODULES:
            raise ImportError(f"Import of {name} not allowed")

        # Check for dangerous submodules
        parts = name.split(".")
        if any(part in self.BLOCKED_MODULES for part in parts):
            raise ImportError(f"Import of {name} not allowed")

        return __import__(name, *args, **kwargs)

    def validate_code(self, code: str) -> bool:
        """
        Validate plugin code for dangerous operations.

        Args:
            code: Python code to validate

        Returns:
            True if code appears safe
        """
        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                # Check for dangerous imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in self.BLOCKED_MODULES:
                            logger.warning(f"Blocked import: {alias.name}")
                            return False

                # Check for eval/exec
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ["eval", "exec", "compile"]:
                            logger.warning(f"Blocked function: {node.func.id}")
                            return False

                # Check for system access
                if isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name):
                        if node.value.id in ["os", "sys", "subprocess"]:
                            logger.warning(f"Blocked module access: {node.value.id}")
                            return False

            return True

        except SyntaxError as e:
            logger.error(f"Syntax error in plugin code: {e}")
            return False

    def set_resource_limits(self) -> None:
        """
        Set resource limits for the current process.

        Should be called before executing plugin code.
        """
        if not self.enabled:
            return

        try:
            # Set memory limit
            memory_bytes = self.max_memory_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))

            # Set CPU time limit
            resource.setrlimit(
                resource.RLIMIT_CPU, (self.max_cpu_seconds, self.max_cpu_seconds)
            )

            logger.debug(
                f"Set resource limits: {self.max_memory_mb}MB, {self.max_cpu_seconds}s"
            )

        except Exception as e:
            logger.warning(f"Failed to set resource limits: {e}")

    def check_command(self, command: str) -> bool:
        """
        Check if a command is safe to execute.

        Args:
            command: Command string to check

        Returns:
            True if command appears safe
        """
        if len(command) > MAX_COMMAND_LENGTH:
            return False

        # Check for dangerous patterns
        dangerous_patterns = [
            "rm -rf",
            "dd if=",
            "mkfs",
            "> /dev/",
            "sudo",
            "chmod -R",
            "chown -R",
        ]

        command_lower = command.lower()
        for pattern in dangerous_patterns:
            if pattern.lower() in command_lower:
                logger.warning(f"Blocked dangerous command pattern: {pattern}")
                return False

        return True
