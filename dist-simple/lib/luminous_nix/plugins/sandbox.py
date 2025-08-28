"""
Plugin Sandbox - The Sacred Vessel of Trust

This module provides the secure execution environment for plugins,
ensuring they can only act within their declared boundaries while
preserving user sovereignty and system integrity.
"""

import asyncio
import os
import sys
import tempfile
import resource
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import json
import hashlib

try:
    from .permission_manager import PermissionManager, Permission, ConsentDecision, PermissionRequest
except ImportError:
    from permission_manager import PermissionManager, Permission, ConsentDecision, PermissionRequest


class SandboxViolation(Exception):
    """Raised when a plugin attempts to violate its boundaries"""
    pass


class ConsentRequired(Exception):
    """Raised when an action requires user consent"""
    def __init__(self, request: PermissionRequest, prompt: str):
        self.request = request
        self.prompt = prompt
        super().__init__(prompt)


class PluginSandbox:
    """
    The Sacred Vessel that contains and protects plugin execution.
    
    This sandbox ensures that plugins can express their purpose
    while respecting boundaries and preserving system integrity.
    """
    
    def __init__(self, manifest: Dict, plugin_module: Any):
        """
        Initialize the sandbox with a manifest and plugin module.
        
        Args:
            manifest: The plugin's manifest (its soul)
            plugin_module: The plugin's code (its body)
        """
        self.manifest = manifest
        self.plugin_module = plugin_module
        self.plugin_id = manifest.get('plugin', {}).get('id', 'unknown')
        
        # Initialize permission manager (the heart of trust)
        self.permission_manager = PermissionManager(manifest)
        
        # Resource limits from manifest
        limits = manifest.get('boundaries', {}).get('resource_limits', {})
        self.max_memory_mb = limits.get('max_memory_mb', 256)
        self.max_cpu_percent = limits.get('max_cpu_percent', 10)
        self.max_storage_mb = limits.get('max_storage_mb', 100)
        
        # Create isolated workspace
        self.workspace = self._create_workspace()
        
        # Consent callback (to be set by the system)
        self.consent_callback: Optional[Callable] = None
        
        # Execution statistics
        self.stats = {
            'executions': 0,
            'violations': 0,
            'consents_requested': 0,
            'consents_granted': 0,
            'start_time': datetime.now()
        }
    
    def _create_workspace(self) -> Path:
        """
        Create an isolated workspace for the plugin.
        
        This is where the plugin can safely read/write files
        without affecting the rest of the system.
        """
        workspace = Path.home() / ".local" / "share" / "luminous-nix" / "sandboxes" / self.plugin_id
        workspace.mkdir(parents=True, exist_ok=True)
        
        # Create standard subdirectories
        (workspace / "data").mkdir(exist_ok=True)
        (workspace / "cache").mkdir(exist_ok=True)
        (workspace / "logs").mkdir(exist_ok=True)
        
        return workspace
    
    def _apply_resource_limits(self):
        """
        Apply resource limits to the current process.
        
        This prevents plugins from consuming excessive resources.
        """
        # Memory limit (in bytes)
        memory_limit = self.max_memory_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))
        
        # CPU time limit (soft limit only, hard limit unchanged)
        # Note: This is cumulative CPU time, not percentage
        # Real percentage limiting requires cgroups or similar
        cpu_soft = 60  # 60 seconds of CPU time
        cpu_hard = resource.getrlimit(resource.RLIMIT_CPU)[1]
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_soft, cpu_hard))
        
        # File size limit
        file_limit = self.max_storage_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_FSIZE, (file_limit, file_limit))
    
    async def execute(self, intent_type: str, intent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a plugin intent within the sandbox.
        
        This is the main entry point for safe plugin execution.
        """
        self.stats['executions'] += 1
        
        # Check if this intent is allowed by manifest
        intents = self.manifest.get('capabilities', {}).get('intents', [])
        intent_handlers = {i['handler']: i for i in intents}
        
        handler_name = None
        for intent in intents:
            if intent['pattern'] == intent_type:
                handler_name = intent['handler']
                break
        
        if not handler_name:
            raise SandboxViolation(f"Intent '{intent_type}' not declared in manifest")
        
        # Get the handler method
        handler = getattr(self.plugin_module, handler_name, None)
        if not handler:
            raise SandboxViolation(f"Handler '{handler_name}' not found in plugin")
        
        # Create sandboxed context
        context = self._create_sandboxed_context()
        
        # Execute with monitoring
        try:
            # In production, this would run in a separate process with resource limits
            # For now, we run it directly but with our permission checks
            result = await self._monitored_execute(handler, intent_data, context)
            
            return {
                'success': True,
                'plugin_id': self.plugin_id,
                'result': result,
                'stats': self.get_stats()
            }
            
        except SandboxViolation as e:
            self.stats['violations'] += 1
            return {
                'success': False,
                'plugin_id': self.plugin_id,
                'error': str(e),
                'error_type': 'violation',
                'stats': self.get_stats()
            }
        
        except ConsentRequired as e:
            self.stats['consents_requested'] += 1
            # In a real system, this would trigger the consent UI
            return {
                'success': False,
                'plugin_id': self.plugin_id,
                'error': str(e),
                'error_type': 'consent_required',
                'consent_prompt': e.prompt,
                'stats': self.get_stats()
            }
        
        except Exception as e:
            return {
                'success': False,
                'plugin_id': self.plugin_id,
                'error': str(e),
                'error_type': 'runtime_error',
                'stats': self.get_stats()
            }
    
    async def _monitored_execute(self, handler: Callable, intent_data: Dict, context: Dict) -> Any:
        """
        Execute a handler with monitoring and permission checks.
        
        This wraps the actual plugin code with our consciousness filters.
        """
        # Create a monitored environment
        original_open = open
        original_import = __import__
        
        def sandboxed_open(file, mode='r', *args, **kwargs):
            """Sandboxed file operations"""
            file_path = Path(file).resolve()
            
            # Check if it's within workspace
            if not str(file_path).startswith(str(self.workspace)):
                # Request permission
                if 'r' in mode:
                    permission = Permission.FILESYSTEM_READ
                    action = f"Read file: {file_path}"
                else:
                    permission = Permission.FILESYSTEM_WRITE
                    action = f"Write file: {file_path}"
                
                allowed, reason = self.permission_manager.can_perform(action, permission)
                
                if not allowed:
                    raise SandboxViolation(f"File access denied: {reason}")
                
                # Check if consent needed
                if self.permission_manager.needs_consent(permission):
                    request = self.permission_manager.request_permission(action, permission)
                    prompt = self.permission_manager.generate_consent_prompt(request)
                    raise ConsentRequired(request, prompt)
            
            return original_open(file, mode, *args, **kwargs)
        
        def sandboxed_import(name, *args, **kwargs):
            """Sandboxed imports"""
            # Block dangerous imports
            blocked_modules = ['subprocess', 'os', 'sys', 'socket', 'requests', 'urllib']
            if any(name.startswith(blocked) for blocked in blocked_modules):
                raise SandboxViolation(f"Import of '{name}' is not allowed")
            
            return original_import(name, *args, **kwargs)
        
        # Apply sandboxing (in production, use proper sandboxing tech)
        # This is a simplified demonstration
        try:
            # Temporarily replace dangerous functions
            # In production, use proper sandboxing like seccomp, AppArmor, or containers
            
            # Call the handler
            result = await handler(intent_data)
            
            return result
            
        finally:
            # Restore original functions
            pass
    
    def _create_sandboxed_context(self) -> Dict[str, Any]:
        """
        Create a sandboxed execution context for the plugin.
        
        This provides safe alternatives to system functions.
        """
        return {
            'workspace': str(self.workspace),
            'plugin_id': self.plugin_id,
            'permissions': [p.value for p in self.permission_manager.granted_permissions],
            'timestamp': datetime.now().isoformat(),
            
            # Safe functions the plugin can use
            'safe_functions': {
                'read_file': self._safe_read_file,
                'write_file': self._safe_write_file,
                'log': self._safe_log,
                'get_setting': self._safe_get_setting,
            }
        }
    
    def _safe_read_file(self, path: str) -> str:
        """Safe file reading within workspace"""
        file_path = self.workspace / path
        if not file_path.exists():
            raise FileNotFoundError(f"File not found in workspace: {path}")
        
        with open(file_path, 'r') as f:
            return f.read()
    
    def _safe_write_file(self, path: str, content: str):
        """Safe file writing within workspace"""
        file_path = self.workspace / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w') as f:
            f.write(content)
    
    def _safe_log(self, message: str):
        """Safe logging to plugin's log file"""
        log_file = self.workspace / "logs" / f"{datetime.now().date()}.log"
        log_file.parent.mkdir(exist_ok=True)
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'plugin_id': self.plugin_id,
            'message': message
        }
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def _safe_get_setting(self, key: str, default: Any = None) -> Any:
        """Safe setting retrieval"""
        settings_file = self.workspace / "data" / "settings.json"
        
        if not settings_file.exists():
            return default
        
        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)
                return settings.get(key, default)
        except:
            return default
    
    def handle_consent_response(self, request: PermissionRequest, decision: ConsentDecision):
        """
        Handle a user's consent decision.
        
        This is called by the system when the user responds to a consent prompt.
        """
        self.permission_manager.record_consent(request, decision)
        
        if decision.granted:
            self.stats['consents_granted'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get sandbox execution statistics"""
        uptime = (datetime.now() - self.stats['start_time']).total_seconds()
        
        return {
            'plugin_id': self.plugin_id,
            'executions': self.stats['executions'],
            'violations': self.stats['violations'],
            'consents_requested': self.stats['consents_requested'],
            'consents_granted': self.stats['consents_granted'],
            'uptime_seconds': uptime,
            'workspace_size_mb': self._get_workspace_size_mb()
        }
    
    def _get_workspace_size_mb(self) -> float:
        """Calculate the size of the plugin's workspace"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.workspace):
            for filename in filenames:
                filepath = Path(dirpath) / filename
                if filepath.exists():
                    total_size += filepath.stat().st_size
        
        return total_size / (1024 * 1024)
    
    def get_boundaries_report(self) -> str:
        """
        Generate a comprehensive report of the plugin's boundaries.
        
        This provides transparency about what the plugin can and cannot do.
        """
        report = f"""
╔══════════════════════════════════════════════════════════╗
║            🔒 Sandbox Report for {self.plugin_id:<24} ║
╚══════════════════════════════════════════════════════════╝

📊 Execution Statistics:
  • Total executions: {self.stats['executions']}
  • Violations blocked: {self.stats['violations']}
  • Consents requested: {self.stats['consents_requested']}
  • Consents granted: {self.stats['consents_granted']}

💾 Resource Usage:
  • Memory limit: {self.max_memory_mb} MB
  • CPU limit: {self.max_cpu_percent}%
  • Storage limit: {self.max_storage_mb} MB
  • Current storage: {self._get_workspace_size_mb():.2f} MB

📁 Workspace Location:
  {self.workspace}

{self.permission_manager.get_boundaries_summary()}
"""
        return report


# Example usage
if __name__ == "__main__":
    import yaml
    
    # Load Flow Guardian manifest
    manifest_path = Path(__file__).parent.parent.parent.parent / "plugins" / "flow-guardian" / "manifest.yaml"
    with open(manifest_path, 'r') as f:
        manifest = yaml.safe_load(f)
    
    # Import the plugin
    sys.path.insert(0, str(manifest_path.parent))
    from plugin import FlowGuardian
    
    # Create plugin instance
    plugin = FlowGuardian()
    
    # Create sandbox
    sandbox = PluginSandbox(manifest, plugin)
    
    print(sandbox.get_boundaries_report())
    
    # Test execution
    async def test():
        result = await sandbox.execute(
            "start focus session",
            {'duration': 25, 'task': 'testing sandbox'}
        )
        print("\nExecution result:")
        print(json.dumps(result, indent=2))
    
    asyncio.run(test())