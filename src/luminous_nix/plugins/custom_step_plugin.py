"""
CustomStepPlugin - Domain-Specific Step Types

Demonstrates StepHandler extension point for adding custom step types
beyond the built-in ones.

Features:
- HTTP request steps
- File operation steps
- Extensible step type system
"""

from typing import Any, Dict, Optional
from pathlib import Path
import urllib.request
import urllib.error

from luminous_nix.core.plugin_registry import Plugin
from luminous_nix.core.extension_points import StepHandler
from luminous_nix.core.execution_plan import ExecutionStep


class HttpStepHandler(StepHandler):
    """
    StepHandler for HTTP request steps.

    Supports GET, POST, PUT, DELETE requests.
    """

    def can_handle(self, step_type: str) -> bool:
        """
        Check if this handler can handle the step type.

        Args:
            step_type: Type of step

        Returns:
            True if step type is HTTP-related
        """
        http_types = [
            'http_request', 'http_get', 'http_post',
            'http_put', 'http_delete'
        ]
        return step_type in http_types

    def execute(self, step: ExecutionStep, context: Dict[str, Any]) -> Any:
        """
        Execute HTTP request step.

        Args:
            step: ExecutionStep with HTTP parameters
            context: Execution context

        Returns:
            Dictionary with response data
        """
        params = step.parameters

        url = params.get('url')
        method = params.get('method', 'GET').upper()
        headers = params.get('headers', {})
        data = params.get('data')
        timeout = params.get('timeout', 30)

        if not url:
            return {
                'success': False,
                'error': 'URL parameter required'
            }

        try:
            # Create request
            req = urllib.request.Request(
                url,
                data=data.encode() if data else None,
                headers=headers,
                method=method
            )

            # Execute request
            with urllib.request.urlopen(req, timeout=timeout) as response:
                body = response.read().decode('utf-8')
                return {
                    'success': True,
                    'status_code': response.status,
                    'body': body,
                    'headers': dict(response.headers)
                }

        except urllib.error.HTTPError as e:
            return {
                'success': False,
                'error': f"HTTP {e.code}: {e.reason}",
                'status_code': e.code
            }

        except urllib.error.URLError as e:
            return {
                'success': False,
                'error': f"URL Error: {e.reason}"
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Request failed: {str(e)}"
            }


class FileOperationStepHandler(StepHandler):
    """
    StepHandler for file operation steps.

    Supports read, write, delete, copy operations.
    """

    def can_handle(self, step_type: str) -> bool:
        """
        Check if this handler can handle the step type.

        Args:
            step_type: Type of step

        Returns:
            True if step type is file-related
        """
        file_types = [
            'file_operation', 'file_read', 'file_write',
            'file_delete', 'file_copy'
        ]
        return step_type in file_types

    def execute(self, step: ExecutionStep, context: Dict[str, Any]) -> Any:
        """
        Execute file operation step.

        Args:
            step: ExecutionStep with file operation parameters
            context: Execution context

        Returns:
            Dictionary with operation result
        """
        params = step.parameters

        operation = params.get('operation', 'read')
        path = params.get('path')

        if not path:
            return {
                'success': False,
                'error': 'Path parameter required'
            }

        path = Path(path)

        try:
            if operation == 'read':
                return self._read_file(path)
            elif operation == 'write':
                content = params.get('content', '')
                return self._write_file(path, content)
            elif operation == 'delete':
                return self._delete_file(path)
            elif operation == 'copy':
                dest = params.get('destination')
                if not dest:
                    return {
                        'success': False,
                        'error': 'Destination parameter required for copy'
                    }
                return self._copy_file(path, Path(dest))
            else:
                return {
                    'success': False,
                    'error': f"Unknown operation: {operation}"
                }

        except Exception as e:
            return {
                'success': False,
                'error': f"File operation failed: {str(e)}"
            }

    def _read_file(self, path: Path) -> Dict[str, Any]:
        """
        Read file contents.

        Args:
            path: File path

        Returns:
            Dictionary with file contents
        """
        if not path.exists():
            return {
                'success': False,
                'error': f"File not found: {path}"
            }

        content = path.read_text()
        return {
            'success': True,
            'operation': 'read',
            'path': str(path),
            'content': content,
            'size': len(content)
        }

    def _write_file(self, path: Path, content: str) -> Dict[str, Any]:
        """
        Write file contents.

        Args:
            path: File path
            content: Content to write

        Returns:
            Dictionary with operation result
        """
        # Create parent directory if needed
        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(content)

        return {
            'success': True,
            'operation': 'write',
            'path': str(path),
            'size': len(content)
        }

    def _delete_file(self, path: Path) -> Dict[str, Any]:
        """
        Delete file.

        Args:
            path: File path

        Returns:
            Dictionary with operation result
        """
        if not path.exists():
            return {
                'success': False,
                'error': f"File not found: {path}"
            }

        path.unlink()

        return {
            'success': True,
            'operation': 'delete',
            'path': str(path)
        }

    def _copy_file(self, src: Path, dest: Path) -> Dict[str, Any]:
        """
        Copy file.

        Args:
            src: Source path
            dest: Destination path

        Returns:
            Dictionary with operation result
        """
        if not src.exists():
            return {
                'success': False,
                'error': f"Source file not found: {src}"
            }

        # Create destination parent directory if needed
        dest.parent.mkdir(parents=True, exist_ok=True)

        # Copy file
        import shutil
        shutil.copy2(src, dest)

        return {
            'success': True,
            'operation': 'copy',
            'source': str(src),
            'destination': str(dest)
        }


class CustomStepPlugin(Plugin):
    """
    Example plugin demonstrating custom step types.

    Adds HTTP request and file operation steps to the execution system.

    Example:
        >>> plugin = CustomStepPlugin()
        >>> registry.register(plugin)
        >>> registry.enable_plugin("custom-step-plugin")
        >>> # Now can use http_request and file_operation steps
    """

    def __init__(self):
        """Initialize custom step plugin"""
        super().__init__()

        self.http_handler: Optional[HttpStepHandler] = None
        self.file_handler: Optional[FileOperationStepHandler] = None

    @property
    def name(self) -> str:
        """Plugin name"""
        return "custom-step-plugin"

    @property
    def version(self) -> str:
        """Plugin version"""
        return "1.0.0"

    @property
    def author(self) -> str:
        """Plugin author"""
        return "Luminous Dynamics"

    @property
    def description(self) -> str:
        """Plugin description"""
        return "Adds HTTP and file operation step types"

    def on_load(self) -> None:
        """Called when plugin is loaded"""
        pass

    def on_enable(self) -> None:
        """
        Called when plugin is enabled.

        Creates and registers custom step handlers.
        """
        self.http_handler = HttpStepHandler()
        self.file_handler = FileOperationStepHandler()

    def on_disable(self) -> None:
        """
        Called when plugin is disabled.
        """
        self.http_handler = None
        self.file_handler = None

    def on_unload(self) -> None:
        """Called when plugin is unloaded"""
        pass


if __name__ == "__main__":
    # Example usage
    print("CustomStepPlugin Example")
    print("-" * 50)

    # Create plugin
    plugin = CustomStepPlugin()

    # Simulate plugin lifecycle
    plugin.on_load()
    plugin.on_enable()

    # Test HTTP handler
    print("\n1. HTTP Request Example:")
    step1 = ExecutionStep(
        id="http_test",
        name="Test HTTP GET",
        handler=lambda p: None,
        parameters={
            'type': 'http_request',
            'url': 'https://httpbin.org/get',
            'method': 'GET'
        },
        depends_on=set(),
        provides={'response'},
        requires=set()
    )

    result1 = plugin.http_handler.execute(step1, {})
    print(f"Success: {result1.get('success')}")
    if result1.get('success'):
        print(f"Status: {result1.get('status_code')}")

    # Test file handler
    print("\n2. File Operation Example:")
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
        tmp_path = tmp.name

    step2 = ExecutionStep(
        id="file_test",
        name="Test File Write",
        handler=lambda p: None,
        parameters={
            'type': 'file_operation',
            'operation': 'write',
            'path': tmp_path,
            'content': 'Hello from CustomStepPlugin!'
        },
        depends_on=set(),
        provides={'file_path'},
        requires=set()
    )

    result2 = plugin.file_handler.execute(step2, {})
    print(f"Success: {result2.get('success')}")
    print(f"Path: {result2.get('path')}")

    # Read it back
    step3 = ExecutionStep(
        id="file_read_test",
        name="Test File Read",
        handler=lambda p: None,
        parameters={
            'type': 'file_operation',
            'operation': 'read',
            'path': tmp_path
        },
        depends_on=set(),
        provides={'content'},
        requires=set()
    )

    result3 = plugin.file_handler.execute(step3, {})
    if result3.get('success'):
        print(f"Content: {result3.get('content')}")

    # Cleanup
    Path(tmp_path).unlink()

    # Disable plugin
    plugin.on_disable()
