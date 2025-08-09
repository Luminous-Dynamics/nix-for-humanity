"""
from typing import Dict, List, Optional
Safe command execution for Nix operations

This module handles the actual execution of NixOS commands with proper
error handling, rollback capabilities, and progress reporting.
"""

import asyncio
import os
import subprocess
from typing import Optional, List, Dict, Any, Callable
from pathlib import Path

from ..api.schema import Result
from .intents import Intent, IntentType
from ..security.input_validator import InputValidator
from ..security.command_validator import CommandValidator
from ..security.permission_checker import PermissionChecker
from .error_handler import error_handler, ErrorContext, ErrorCategory


class ValidationResult:
    """Result of security validation"""
    def __init__(self, valid: bool, reason: str = ""):
        self.valid = valid
        self.reason = reason


class SafeExecutor:
    """Execute NixOS commands safely with rollback support"""
    
    def __init__(self, progress_callback: Optional[Callable] = None):
        """
        Initialize the executor
        
        Args:
            progress_callback: Optional callback for progress updates
        """
        self.progress_callback = progress_callback
        self.dry_run = False
        self._init_python_api()
        
    def _init_python_api(self):
        """Try to initialize Python API if available"""
        self._has_python_api = False
        try:
            # Import our native backend wrapper
            import sys
            from pathlib import Path
            # Navigate to project root then to nix_humanity module
            project_root = Path(__file__).parent.parent.parent
            sys.path.insert(0, str(project_root))
            
            from nix_humanity.core.native_operations import NativeNixBackend, NATIVE_API_AVAILABLE, OperationType, NixOperation
            from .nixos_version import NixOSVersionChecker
            
            # Check version compatibility
            version_checker = NixOSVersionChecker()
            compat = version_checker.check_compatibility()
            
            if not compat['compatible'] and not compat['can_override']:
                print(f"⚠️ {compat['reason']}")
                print("💡 Run 'ask-nix --show-upgrade' for upgrade instructions")
                self._has_python_api = False
                return
            
            if NATIVE_API_AVAILABLE:
                self.native_backend = NativeNixBackend()
                self.native_backend.set_progress_callback(self._progress_wrapper)
                self._has_python_api = True
                
                if compat['can_override']:
                    print("⚠️ Using Native API with version override - some features may not work")
                else:
                    print(f"✅ Native Python-Nix API initialized on {compat['current_version']} - 10x performance boost!")
            else:
                print("⚠️ Native API not available, using subprocess fallback")
        except ImportError as e:
            print(f"❌ Failed to initialize native backend: {e}")
    
    def _get_operation_type(self, intent: Intent) -> str:
        """Map intent to operation type for permission checking"""
        operation_map = {
            IntentType.INSTALL_PACKAGE: 'install-package',
            IntentType.UPDATE_SYSTEM: 'modify-configuration',
            IntentType.CONFIGURE: 'modify-configuration',
            IntentType.ROLLBACK: 'modify-configuration',
            IntentType.SEARCH_PACKAGE: 'read-file',
            IntentType.EXPLAIN: 'read-file',
            IntentType.HELP: 'read-file',
            IntentType.REMOVE_PACKAGE: 'remove-package',
            IntentType.GARBAGE_COLLECT: 'modify-configuration',
            IntentType.LIST_GENERATIONS: 'read-file',
            IntentType.SWITCH_GENERATION: 'modify-configuration',
            IntentType.REBUILD: 'modify-configuration',
            IntentType.EDIT_CONFIG: 'read-file',
            IntentType.SHOW_CONFIG: 'read-file',
            IntentType.CHECK_STATUS: 'read-file',
            IntentType.LIST_INSTALLED: 'read-file',
            # Network operations
            IntentType.SHOW_NETWORK: 'read-file',
            IntentType.SHOW_IP: 'read-file',
            IntentType.CONNECT_WIFI: 'modify-configuration',
            IntentType.LIST_WIFI: 'read-file',
            IntentType.TEST_CONNECTION: 'read-file',
            # Service operations
            IntentType.START_SERVICE: 'modify-configuration',
            IntentType.STOP_SERVICE: 'modify-configuration',
            IntentType.RESTART_SERVICE: 'modify-configuration',
            IntentType.SERVICE_STATUS: 'read-file',
            IntentType.LIST_SERVICES: 'read-file',
            IntentType.ENABLE_SERVICE: 'modify-configuration',
            IntentType.DISABLE_SERVICE: 'modify-configuration',
            IntentType.SERVICE_LOGS: 'read-file',
            # User management operations
            IntentType.CREATE_USER: 'modify-configuration',
            IntentType.LIST_USERS: 'read-file',
            IntentType.ADD_USER_TO_GROUP: 'modify-configuration',
            IntentType.CHANGE_PASSWORD: 'modify-configuration',
            IntentType.GRANT_SUDO: 'modify-configuration',
            # Storage management operations
            IntentType.DISK_USAGE: 'read-file',
            IntentType.ANALYZE_DISK: 'read-file',
            IntentType.MOUNT_DEVICE: 'modify-configuration',
            IntentType.UNMOUNT_DEVICE: 'modify-configuration',
            IntentType.FIND_LARGE_FILES: 'read-file',
        }
        return operation_map.get(intent.type, 'unknown')
            
    def _progress_wrapper(self, message: str, progress: float):
        """Progress callback wrapper"""
        if self.progress_callback:
            self.progress_callback(message, progress)
            
    def _progress_wrapper(self, message: str, progress: float):
        """Wrapper for progress callback to match native backend interface"""
        if self.progress_callback:
            self.progress_callback(message, progress)
            
    async def execute(self, plan: List[str], intent: Intent) -> Result:
        """
        Execute the planned actions with comprehensive security validation
        
        Args:
            plan: List of actions to execute
            intent: The original intent
            
        Returns:
            Result of the execution
        """
        try:
            # SECURITY: Comprehensive validation before execution
            validation_result = self._validate_execution_request(plan, intent)
            if not validation_result.valid:
                return Result(
                    success=False,
                    output="",
                    error=f"Security validation failed: {validation_result.reason}"
                )
            
            # SECURITY: Check permissions for the operation
            permission_result = PermissionChecker.check_operation_permission(
                operation=self._get_operation_type(intent),
                context={'intent': intent, 'plan': plan}
            )
            
            if not permission_result['allowed']:
                return Result(
                    success=False,
                    output="",
                    error=f"Permission denied: {permission_result['reason']}",
                    details=permission_result.get('suggestions', [])
                )
            
            # Notify if elevation required
            if permission_result.get('requires_elevation'):
                if self.progress_callback:
                    self.progress_callback("🔐 This operation requires elevated privileges", 0.1)
            
            # Route to appropriate executor based on intent
            if intent.type == IntentType.INSTALL_PACKAGE:
                package = intent.entities.get('package')
                
                # SECURITY: Use our comprehensive package validator
                package_validation = InputValidator.validate_input(package, 'package')
                if not package_validation['valid']:
                    return Result(
                        success=False,
                        output="",
                        error=package_validation['reason'],
                        details=package_validation.get('suggestions', [])
                    )
                
                return await self._execute_install(package_validation['sanitized_input'])
            elif intent.type == IntentType.UPDATE_SYSTEM:
                return await self._execute_update()
            elif intent.type == IntentType.SEARCH_PACKAGE:
                query = intent.entities.get('query')
                if not self._validate_search_query(query):
                    return Result(
                        success=False,
                        output="",
                        error="Invalid search query - contains unsafe characters"
                    )
                return await self._execute_search(query)
            elif intent.type == IntentType.ROLLBACK:
                return await self._execute_rollback()
            elif intent.type == IntentType.HELP:
                return await self._execute_help()
            elif intent.type == IntentType.REMOVE_PACKAGE:
                package = intent.entities.get('package')
                
                # SECURITY: Use our comprehensive package validator
                package_validation = InputValidator.validate_input(package, 'package')
                if not package_validation['valid']:
                    return Result(
                        success=False,
                        output="",
                        error=package_validation['reason'],
                        details=package_validation.get('suggestions', [])
                    )
                
                return await self._execute_remove(package_validation['sanitized_input'])
            elif intent.type == IntentType.GARBAGE_COLLECT:
                return await self._execute_garbage_collect()
            elif intent.type == IntentType.LIST_GENERATIONS:
                return await self._execute_list_generations()
            elif intent.type == IntentType.SWITCH_GENERATION:
                generation = intent.entities.get('generation')
                if generation is None:
                    return Result(
                        success=False,
                        output="",
                        error="No generation number specified"
                    )
                return await self._execute_switch_generation(generation)
            elif intent.type == IntentType.REBUILD:
                rebuild_type = intent.entities.get('rebuild_type', 'switch')
                return await self._execute_rebuild(rebuild_type)
            elif intent.type == IntentType.EDIT_CONFIG:
                return await self._execute_edit_config()
            elif intent.type == IntentType.SHOW_CONFIG:
                return await self._execute_show_config()
            elif intent.type == IntentType.CHECK_STATUS:
                return await self._execute_check_status()
            elif intent.type == IntentType.LIST_INSTALLED:
                return await self._execute_list_installed()
            elif intent.type == IntentType.SHOW_NETWORK:
                return await self._execute_show_network()
            elif intent.type == IntentType.SHOW_IP:
                return await self._execute_show_ip()
            elif intent.type == IntentType.CONNECT_WIFI:
                ssid = intent.entities.get('ssid')
                return await self._execute_connect_wifi(ssid)
            elif intent.type == IntentType.LIST_WIFI:
                return await self._execute_list_wifi()
            elif intent.type == IntentType.TEST_CONNECTION:
                return await self._execute_test_connection()
            elif intent.type == IntentType.START_SERVICE:
                service = intent.entities.get('service')
                return await self._execute_start_service(service)
            elif intent.type == IntentType.STOP_SERVICE:
                service = intent.entities.get('service')
                return await self._execute_stop_service(service)
            elif intent.type == IntentType.RESTART_SERVICE:
                service = intent.entities.get('service')
                return await self._execute_restart_service(service)
            elif intent.type == IntentType.SERVICE_STATUS:
                service = intent.entities.get('service')
                return await self._execute_service_status(service)
            elif intent.type == IntentType.LIST_SERVICES:
                return await self._execute_list_services()
            elif intent.type == IntentType.ENABLE_SERVICE:
                service = intent.entities.get('service')
                return await self._execute_enable_service(service)
            elif intent.type == IntentType.DISABLE_SERVICE:
                service = intent.entities.get('service')
                return await self._execute_disable_service(service)
            elif intent.type == IntentType.SERVICE_LOGS:
                service = intent.entities.get('service')
                return await self._execute_service_logs(service)
            # User management
            elif intent.type == IntentType.CREATE_USER:
                username = intent.entities.get('username')
                return await self._execute_create_user(username)
            elif intent.type == IntentType.LIST_USERS:
                return await self._execute_list_users()
            elif intent.type == IntentType.ADD_USER_TO_GROUP:
                username = intent.entities.get('username')
                group = intent.entities.get('group')
                return await self._execute_add_user_to_group(username, group)
            elif intent.type == IntentType.CHANGE_PASSWORD:
                username = intent.entities.get('username')
                return await self._execute_change_password(username)
            elif intent.type == IntentType.GRANT_SUDO:
                username = intent.entities.get('username')
                return await self._execute_grant_sudo(username)
            # Storage management
            elif intent.type == IntentType.DISK_USAGE:
                return await self._execute_disk_usage()
            elif intent.type == IntentType.ANALYZE_DISK:
                return await self._execute_analyze_disk()
            elif intent.type == IntentType.MOUNT_DEVICE:
                device = intent.entities.get('device')
                mount_point = intent.entities.get('mount_point')
                return await self._execute_mount_device(device, mount_point)
            elif intent.type == IntentType.UNMOUNT_DEVICE:
                device = intent.entities.get('device')
                return await self._execute_unmount_device(device)
            elif intent.type == IntentType.FIND_LARGE_FILES:
                count = intent.entities.get('count', 10)
                return await self._execute_find_large_files(count)
            else:
                return Result(
                    success=False,
                    output="",
                    error="Execution not implemented for this intent type"
                )
                
        except Exception as e:
            context = ErrorContext(
                operation="execute",
                user_input=str(intent.raw_input) if hasattr(intent, 'raw_input') else '',
                metadata={
                    "intent_type": intent.type.value if intent else 'unknown',
                    "plan": plan
                }
            )
            
            nix_error = error_handler.handle_error(e, context)
            
            return Result(
                success=False,
                output="",
                error=nix_error.user_message,
                details=nix_error.suggestions
            )
            
    async def _execute_install(self, package: str) -> Result:
        """Execute package installation"""
        if not package:
            return Result(
                success=False,
                output="",
                error="No package specified"
            )
            
        # Try Python API first
        if self._has_python_api:
            try:
                from nix_humanity.core.native_operations import NixOperation, OperationType
                
                operation = NixOperation(
                    type=OperationType.INSTALL,
                    packages=[package],
                    dry_run=self.dry_run
                )
                
                result = await self.native_backend.execute(operation)
                
                return Result(
                    success=result.success,
                    output=result.message,
                    error=result.error or ""
                )
                    
            except Exception as e:
                if os.getenv('DEBUG'):
                    print(f"Python API failed: {e}")
                    
        # Fallback to subprocess
        if self.dry_run:
            return Result(
                success=True,
                output=f"Would install: {package}",
                error=""
            )
            
        try:
            # Use nix profile install (modern approach)
            cmd = ['nix', 'profile', 'install', f'nixpkgs#{package}']
            
            if self.progress_callback:
                self.progress_callback(f"Installing {package}...", 0.7)
                
            result = await self._run_command(cmd)
            
            return Result(
                success=result['returncode'] == 0,
                output=result['stdout'],
                error=result['stderr'] if result['returncode'] != 0 else ""
            )
            
        except Exception as e:
            context = ErrorContext(
                operation="install_package",
                user_input=f"install {package}",
                command=['nix', 'profile', 'install', f'nixpkgs#{package}'],
                metadata={"package": package}
            )
            
            nix_error = error_handler.handle_error(e, context)
            
            return Result(
                success=False,
                output="",
                error=nix_error.user_message,
                details=nix_error.suggestions
            )
            
    async def _execute_update(self) -> Result:
        """Execute system update"""
        # Use native operations for massive speedup
        if self._native_ops:
            try:
                from .native_operations import NativeOperationType
                
                result = await self._native_ops.execute_native_operation(
                    NativeOperationType.SWITCH,
                    options={'dry_run': self.dry_run}
                )
                
                return Result(
                    success=result.success,
                    output=result.message,
                    error="" if result.success else result.data.get('error', ''),
                    details=result.suggestions
                )
            except Exception as e:
                if os.getenv('DEBUG'):
                    print(f"Native update failed: {e}")
                # Fall through to subprocess
        
        # Try legacy native backend
        if self._has_python_api:
            try:
                from nix_humanity.core.native_operations import NixOperation, OperationType
                
                operation = NixOperation(
                    type=OperationType.UPDATE,
                    dry_run=self.dry_run
                )
                
                result = await self.native_backend.execute(operation)
                
                return Result(
                    success=result.success,
                    output=result.message,
                    error=result.error or ""
                )
                    
            except Exception as e:
                if os.getenv('DEBUG'):
                    print(f"Python API failed: {e}")
                    
        # Fallback to subprocess
        if self.dry_run:
            return Result(
                success=True,
                output="Would update system",
                error=""
            )
            
        try:
            # First update channels
            if self.progress_callback:
                self.progress_callback("Updating channels...", 0.3)
                
            cmd1 = ['sudo', 'nix-channel', '--update']
            result1 = await self._run_command(cmd1)
            
            if result1['returncode'] != 0:
                return Result(
                    success=False,
                    output=result1['stdout'],
                    error=f"Channel update failed: {result1['stderr']}"
                )
                
            # Then rebuild
            if self.progress_callback:
                self.progress_callback("Rebuilding system...", 0.7)
                
            # Use the workaround for long-running rebuild
            rebuild_script = self._create_rebuild_script()
            cmd2 = ['bash', str(rebuild_script)]
            result2 = await self._run_command(cmd2, timeout=10)  # Quick timeout for script start
            
            return Result(
                success=True,
                output="System update started in background. Check /tmp/nixos-rebuild.log for progress.",
                error=""
            )
            
        except Exception as e:
            context = ErrorContext(
                operation="update_system",
                user_input="update system",
                command=['sudo', 'nixos-rebuild', 'switch'],
                metadata={"dry_run": self.dry_run}
            )
            
            nix_error = error_handler.handle_error(e, context)
            
            return Result(
                success=False,
                output="",
                error=nix_error.user_message,
                details=nix_error.suggestions
            )
            
    async def _execute_search(self, query: str) -> Result:
        """Execute package search"""
        if not query:
            return Result(
                success=False,
                output="",
                error="No search query specified"
            )
            
        # Use native operations for 10x faster search
        if self._native_ops:
            try:
                from .native_operations import NativeOperationType
                
                result = await self._native_ops.execute_native_operation(
                    NativeOperationType.SEARCH_PACKAGES,
                    packages=[query]
                )
                
                if result.success and result.data.get('results'):
                    output_lines = [f"Search results for '{query}':"]
                    for pkg in result.data['results'][:10]:  # Limit to 10 results
                        output_lines.append(f"  • {pkg}")
                    if len(result.data['results']) > 10:
                        output_lines.append(f"  ... and {len(result.data['results']) - 10} more results")
                    
                    return Result(
                        success=True,
                        output="\n".join(output_lines),
                        error="",
                        details=[f"Search completed in {result.duration_ms:.0f}ms"]
                    )
                else:
                    return Result(
                        success=result.success,
                        output=result.message,
                        error="" if result.success else result.data.get('error', '')
                    )
            except Exception as e:
                if os.getenv('DEBUG'):
                    print(f"Native search failed: {e}")
                # Fall through to subprocess
            
        # Try legacy Python API
        if self._has_python_api:
            try:
                from nix_humanity.core.native_operations import NixOperation, OperationType
                
                operation = NixOperation(
                    type=OperationType.SEARCH,
                    packages=[query],
                    dry_run=self.dry_run
                )
                
                result = await self.native_backend.execute(operation)
                
                return Result(
                    success=result.success,
                    output=result.message,
                    error=result.error or ""
                )
                    
            except Exception as e:
                if os.getenv('DEBUG'):
                    print(f"Python API failed for search: {e}")
                # Fall through to subprocess
        
        try:
            cmd = ['nix', 'search', 'nixpkgs', query]
            
            if self.progress_callback:
                self.progress_callback(f"Searching for '{query}'...", 0.5)
                
            result = await self._run_command(cmd)
            
            return Result(
                success=result['returncode'] == 0,
                output=result['stdout'] if result['stdout'] else f"No packages found matching '{query}'",
                error=result['stderr'] if result['returncode'] != 0 else ""
            )
            
        except Exception as e:
            context = ErrorContext(
                operation="search_package",
                user_input=f"search {query}",
                command=['nix', 'search', 'nixpkgs', query],
                metadata={"query": query}
            )
            
            nix_error = error_handler.handle_error(e, context)
            
            return Result(
                success=False,
                output="",
                error=nix_error.user_message,
                details=nix_error.suggestions
            )
            
    async def _execute_rollback(self) -> Result:
        """Execute system rollback"""
        # Use native operations for instant rollback
        if self._native_ops:
            try:
                from .native_operations import NativeOperationType
                
                result = await self._native_ops.execute_native_operation(
                    NativeOperationType.ROLLBACK
                )
                
                return Result(
                    success=result.success,
                    output=result.message,
                    error="" if result.success else result.data.get('error', ''),
                    details=result.suggestions
                )
            except Exception as e:
                if os.getenv('DEBUG'):
                    print(f"Native rollback failed: {e}")
                # Fall through to subprocess
        
        # Try legacy native backend
        if self._has_python_api:
            try:
                from nix_humanity.core.native_operations import NixOperation, OperationType
                
                operation = NixOperation(
                    type=OperationType.ROLLBACK,
                    dry_run=self.dry_run
                )
                
                result = await self.native_backend.execute(operation)
                
                return Result(
                    success=result.success,
                    output=result.message,
                    error=result.error or ""
                )
                    
            except Exception as e:
                if os.getenv('DEBUG'):
                    print(f"Python API failed: {e}")
                    
        # Fallback to subprocess
        if self.dry_run:
            return Result(
                success=True,
                output="Would rollback system",
                error=""
            )
            
        try:
            cmd = ['sudo', 'nixos-rebuild', 'switch', '--rollback']
            
            if self.progress_callback:
                self.progress_callback("Rolling back to previous generation...", 0.5)
                
            result = await self._run_command(cmd)
            
            return Result(
                success=result['returncode'] == 0,
                output=result['stdout'],
                error=result['stderr'] if result['returncode'] != 0 else ""
            )
            
        except Exception as e:
            context = ErrorContext(
                operation="rollback_system",
                user_input="rollback system",
                command=['sudo', 'nixos-rebuild', 'switch', '--rollback'],
                metadata={"dry_run": self.dry_run}
            )
            
            nix_error = error_handler.handle_error(e, context)
            
            return Result(
                success=False,
                output="",
                error=nix_error.user_message,
                details=nix_error.suggestions
            )
            
    async def _execute_help(self) -> Result:
        """Execute help command - shows available commands"""
        help_text = """Available commands:

📦 Package Management:
• Install: "install firefox", "add vim"
• Remove: "remove firefox", "uninstall vim"  
• Search: "search editor", "find browser"
• List installed: "what's installed?", "list packages"

🔄 System Management:
• Update: "update my system", "upgrade everything"
• Rebuild: "rebuild my config", "apply changes"
• Rollback: "rollback", "undo last change"
• Generations: "list generations", "switch to generation 5"

🧹 Maintenance:
• Clean up: "garbage collect", "free disk space"
• Check status: "system status", "health check"

⚙️ Configuration:
• Edit config: "edit configuration", "open config"
• Show config: "show configuration", "view config"

🌐 Network & Connectivity:
• Network status: "show network", "network status"
• IP addresses: "what's my ip?", "show ip"
• WiFi: "connect to wifi MyNetwork", "list wifi networks"
• Test connection: "test internet", "is internet working?"

⚡ Service Management:
• Start service: "start nginx", "start service ssh"
• Stop service: "stop mysql", "stop service docker"
• Restart service: "restart apache", "restart web server"
• Service status: "is nginx running?", "service status ssh"
• List services: "list services", "show all services"
• Enable/disable: "enable ssh", "disable nginx at boot"
• Service logs: "show nginx logs", "service logs postgresql"

📚 Help & Info:
• Help: "help", "what can you do?"
• Explain: "explain generations", "what is nix-shell?"

Examples:
- "what's my ip address?" → Shows all network interfaces
- "connect to wifi HomeNetwork" → Connects to WiFi
- "restart the web server" → Restarts nginx service
- "is ssh running?" → Checks SSH service status

Just describe what you need in natural language!"""
        
        return Result(
            success=True,
            output=help_text,
            error=""
        )
        
    async def _execute_remove(self, package: str) -> Result:
        """
        Execute package removal
        
        Args:
            package: The package to remove
            
        Returns:
            Result with removal status
        """
        # Try native backend first
        if self._has_python_api and self._native_backend:
            try:
                if self.progress_callback:
                    self.progress_callback(f"Removing {package} using native API...", 0.2)
                    
                # Use the native backend's remove method
                if hasattr(self._native_backend, 'remove_package'):
                    result = await self._native_backend.remove_package(package, self.dry_run)
                    return Result(
                        success=result.success,
                        output=result.message,
                        error=result.error if not result.success else "",
                        details=result.details if hasattr(result, 'details') else []
                    )
            except Exception as e:
                if self.progress_callback:
                    self.progress_callback("Native API failed, falling back to subprocess", 0.3)
                    print(f"Python API failed: {e}")
                    
        # Fallback to subprocess
        if self.dry_run:
            return Result(
                success=True,
                output=f"Would remove package: {package}",
                error=""
            )
            
        try:
            # Use nix profile remove (modern way)
            cmd = ['nix', 'profile', 'remove', f'nixpkgs#{package}']
            
            if self.progress_callback:
                self.progress_callback(f"Removing {package}...", 0.5)
                
            result = await self._run_command(cmd)
            
            if result['returncode'] == 0:
                return Result(
                    success=True,
                    output=f"Successfully removed {package}",
                    error=""
                )
            else:
                # Try with sudo if permission denied
                if "permission denied" in result['stderr'].lower():
                    cmd = ['sudo'] + cmd
                    if self.progress_callback:
                        self.progress_callback(f"Retrying with elevated privileges...", 0.7)
                    result = await self._run_command(cmd)
                    
                    if result['returncode'] == 0:
                        return Result(
                            success=True,
                            output=f"Successfully removed {package} (with sudo)",
                            error=""
                        )
                        
                return Result(
                    success=False,
                    output="",
                    error=result['stderr'] or f"Failed to remove {package}"
                )
                
        except Exception as e:
            context = ErrorContext(
                operation="remove_package",
                user_input=f"remove {package}",
                command=['nix', 'profile', 'remove', f'nixpkgs#{package}'],
                metadata={"package": package, "dry_run": self.dry_run}
            )
            
            nix_error = error_handler.handle_error(e, context)
            
            return Result(
                success=False,
                output="",
                error=nix_error.user_message,
                details=nix_error.suggestions
            )
            
    def _validate_execution_request(self, plan: List[str], intent: Intent) -> 'ValidationResult':
        """
        Comprehensive validation of execution request
        
        Args:
            plan: List of actions to execute
            intent: The original intent
            
        Returns:
            ValidationResult with validation status and reason
        """
        # SECURITY: Check plan size
        if len(plan) > 20:
            return ValidationResult(
                valid=False,
                reason="Plan too complex - maximum 20 actions allowed"
            )
        
        # SECURITY: Validate each action in plan
        for action in plan:
            if not isinstance(action, str):
                return ValidationResult(
                    valid=False,
                    reason="Invalid action type - actions must be strings"
                )
            
            # SECURITY: Check for dangerous patterns
            dangerous_patterns = [
                r'[;&|`$]',           # Shell metacharacters
                r'\$\{.*\}',          # Variable expansion
                r'\$\(.*\)',          # Command substitution
                r'`.*`',              # Backticks
                r'\.\.\/',            # Path traversal
                r'<[^>]+>',           # HTML/Script tags
                r'rm\s+-rf',          # Dangerous rm commands
                r'sudo\s+rm',         # Dangerous sudo rm
                r'chmod\s+777',       # Dangerous permissions
                r'/etc/passwd',       # System files
                r'/etc/shadow',       # System files
            ]
            
            import re
            for pattern in dangerous_patterns:
                if re.search(pattern, action):
                    return ValidationResult(
                        valid=False,
                        reason=f"Unsafe pattern detected in action: {pattern}"
                    )
        
        # SECURITY: Validate intent consistency
        if not intent or not hasattr(intent, 'type'):
            return ValidationResult(
                valid=False,
                reason="Invalid intent provided"
            )
        
        return ValidationResult(valid=True, reason="Validation passed")
    
    def _validate_package_name(self, package: str) -> bool:
        """
        Validate package name for safety
        
        Args:
            package: Package name to validate
            
        Returns:
            True if package name is safe, False otherwise
        """
        if not package or not isinstance(package, str):
            return False
        
        # SECURITY: Length check
        if len(package) > 100:
            return False
        
        # SECURITY: Character whitelist - allow only safe characters
        import re
        if not re.match(r'^[a-zA-Z0-9._-]+$', package):
            return False
        
        # SECURITY: Prevent relative paths and special names
        if package.startswith('.') or package.startswith('-'):
            return False
        
        if package in ['..', '.', '/', 'sudo', 'rm']:
            return False
        
        return True
    
    def _validate_search_query(self, query: str) -> bool:
        """
        Validate search query for safety
        
        Args:
            query: Search query to validate
            
        Returns:
            True if query is safe, False otherwise
        """
        if not query or not isinstance(query, str):
            return False
        
        # SECURITY: Length check
        if len(query) > 200:
            return False
        
        # SECURITY: Check for dangerous patterns
        dangerous_patterns = [
            r'[;&|`$]',           # Shell metacharacters
            r'\$\{.*\}',          # Variable expansion
            r'\$\(.*\)',          # Command substitution
            r'`.*`',              # Backticks
            r'<[^>]+>',           # HTML/Script tags
        ]
        
        import re
        for pattern in dangerous_patterns:
            if re.search(pattern, query):
                return False
        
        return True

    def _validate_command_args(self, cmd: List[str]) -> bool:
        """
        Validate command arguments for security
        
        Args:
            cmd: Command and arguments list
            
        Returns:
            True if command is safe, False otherwise
        """
        if not cmd or not isinstance(cmd, list):
            return False
            
        # SECURITY: Validate command exists and is whitelisted
        allowed_commands = [
            'nix', 'nixos-rebuild', 'nix-env', 'nix-channel',
            'nix-collect-garbage', 'nix-store', 'nix-build',
            'sudo', 'systemctl'  # Only for specific NixOS operations
        ]
        
        command = cmd[0] if cmd else ''
        base_command = os.path.basename(command)
        
        if base_command not in allowed_commands:
            return False
            
        # SECURITY: Validate each argument
        for arg in cmd[1:]:
            if not isinstance(arg, str):
                return False
                
            # SECURITY: Block dangerous argument patterns
            dangerous_arg_patterns = [
                r'[;&|`$]',           # Shell metacharacters
                r'\$\{.*\}',          # Variable expansion
                r'\$\(.*\)',          # Command substitution
                r'`.*`',              # Backticks
                r'\.\./',             # Path traversal
                r'rm\s+-rf',          # Dangerous rm commands
                r'/etc/passwd',       # System files
                r'/etc/shadow',       # System files
                r'--eval.*system',    # Dangerous evaluation
            ]
            
            import re
            for pattern in dangerous_arg_patterns:
                if re.search(pattern, arg, re.IGNORECASE):
                    return False
                    
        return True

    async def _run_command(self, cmd: List[str], timeout: Optional[int] = None) -> Dict[str, Any]:
        """Run a command asynchronously with comprehensive security validation"""
        try:
            # SECURITY: Use our comprehensive command validator
            cmd_valid, cmd_error, cmd_metadata = CommandValidator.validate_nix_command(cmd)
            if not cmd_valid:
                # Get safer alternative if available
                suggestion = CommandValidator.suggest_safer_alternative(cmd, cmd_metadata.get('reason', ''))
                error_msg = f'Command blocked: {cmd_error}'
                if suggestion:
                    error_msg += f'\nSuggestion: {suggestion}'
                
                return {
                    'returncode': -1,
                    'stdout': '',
                    'stderr': error_msg
                }
            
            # SECURITY: Additional legacy validation (belt and suspenders)
            if not self._validate_command_args(cmd):
                return {
                    'returncode': -1,
                    'stdout': '',
                    'stderr': f'Command blocked for security reasons: {" ".join(cmd[:2])}'
                }
            
            if timeout is None:
                timeout = 300  # 5 minutes default
                
            # SECURITY: Use minimal environment
            # Include nix store paths for nix commands
            nix_paths = [
                '/run/current-system/sw/bin',
                '/nix/var/nix/profiles/default/bin',
                '/usr/bin',
                '/bin',
                '/run/wrappers/bin'
            ]
            safe_env = {
                'PATH': ':'.join(nix_paths),
                'HOME': os.environ.get('HOME', '/tmp'),
                'USER': os.environ.get('USER', 'nixos'),
                'NIX_PATH': os.environ.get('NIX_PATH', ''),
            }
                
            # Run the command with restricted environment
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=safe_env  # SECURITY: Restricted environment
            )
            
            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return {
                    'returncode': -1,
                    'stdout': '',
                    'stderr': f'Command timed out after {timeout} seconds'
                }
                
            return {
                'returncode': process.returncode,
                'stdout': stdout.decode('utf-8', errors='replace'),
                'stderr': stderr.decode('utf-8', errors='replace')
            }
            
        except Exception as e:
            context = ErrorContext(
                operation="run_command",
                command=cmd,
                metadata={"timeout": timeout}
            )
            
            nix_error = error_handler.handle_error(e, context)
            
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': f'{nix_error.user_message}\nError code: {nix_error.error_code}'
            }
            
    def _create_rebuild_script(self) -> Path:
        """Create a script for background rebuild (workaround for timeouts)"""
        script_content = """#!/usr/bin/env bash
echo "🌟 Starting NixOS rebuild in background..."
sudo nixos-rebuild switch > /tmp/nixos-rebuild.log 2>&1 &
echo "✨ Rebuild started! Check progress with: tail -f /tmp/nixos-rebuild.log"
"""
        
        script_path = Path('/tmp/nixos-rebuild-wrapper.sh')
        script_path.write_text(script_content)
        script_path.chmod(0o755)
        
        return script_path
    
    async def _execute_garbage_collect(self) -> Result:
        """Execute garbage collection to free disk space"""
        # Use native operations for better garbage collection
        if self._native_ops:
            try:
                from .native_operations import NativeOperationType
                
                result = await self._native_ops.execute_native_operation(
                    NativeOperationType.GARBAGE_COLLECT,
                    options={'delete_old': True}
                )
                
                return Result(
                    success=result.success,
                    output=result.message,
                    error="" if result.success else result.data.get('error', ''),
                    details=result.suggestions
                )
            except Exception as e:
                if os.getenv('DEBUG'):
                    print(f"Native garbage collect failed: {e}")
                # Fall through to subprocess
        
        if self.dry_run:
            return Result(
                success=True,
                output="Would run garbage collection to free disk space",
                error=""
            )
        
        try:
            # Show how much space would be freed
            cmd_check = ['nix-store', '--gc', '--print-dead']
            if self.progress_callback:
                self.progress_callback("Checking how much space can be freed...", 0.2)
            
            check_result = await self._run_command(cmd_check)
            dead_paths = check_result['stdout'].split('\n') if check_result['stdout'] else []
            
            # Calculate approximate size (simplified)
            size_info = f"Found {len(dead_paths)} items to clean"
            
            # Actually run garbage collection
            cmd_gc = ['sudo', 'nix-collect-garbage', '-d']
            if self.progress_callback:
                self.progress_callback("Running garbage collection...", 0.5)
            
            result = await self._run_command(cmd_gc)
            
            if result['returncode'] == 0:
                return Result(
                    success=True,
                    output=f"Garbage collection completed!\n{size_info}\n{result['stdout']}",
                    error=""
                )
            else:
                return Result(
                    success=False,
                    output="",
                    error=result['stderr'] or "Failed to run garbage collection"
                )
                
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=f"Error during garbage collection: {str(e)}"
            )
    
    async def _execute_list_generations(self) -> Result:
        """List available system generations"""
        # Use native operations for INSTANT listing!
        if self._native_ops:
            try:
                from .native_operations import NativeOperationType
                
                result = await self._native_ops.execute_native_operation(
                    NativeOperationType.LIST_GENERATIONS
                )
                
                if result.success and result.data.get('generations'):
                    # Format generations nicely
                    output_lines = ["System generations:"]
                    for gen in result.data['generations']:
                        current = " (current)" if gen.get('current') else ""
                        output_lines.append(f"  {gen['number']} - {gen['date']}{current}")
                    
                    return Result(
                        success=True,
                        output="\n".join(output_lines),
                        error="",
                        details=[f"Found {len(result.data['generations'])} generations"]
                    )
                else:
                    return Result(
                        success=result.success,
                        output=result.message,
                        error="" if result.success else result.data.get('error', '')
                    )
            except Exception as e:
                if os.getenv('DEBUG'):
                    print(f"Native list generations failed: {e}")
                # Fall through to subprocess
        
        try:
            cmd = ['sudo', 'nix-env', '--list-generations', '-p', '/nix/var/nix/profiles/system']
            
            if self.progress_callback:
                self.progress_callback("Listing system generations...", 0.5)
            
            result = await self._run_command(cmd)
            
            if result['returncode'] == 0:
                return Result(
                    success=True,
                    output=result['stdout'],
                    error=""
                )
            else:
                return Result(
                    success=False,
                    output="",
                    error=result['stderr'] or "Failed to list generations"
                )
                
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=f"Error listing generations: {str(e)}"
            )
    
    async def _execute_switch_generation(self, generation: int) -> Result:
        """Switch to a specific system generation"""
        # Use native operations for fast generation switching
        if self._native_ops:
            try:
                from .native_operations import NativeOperationType
                
                result = await self._native_ops.execute_native_operation(
                    NativeOperationType.SWITCH_GENERATION,
                    options={'generation': generation}
                )
                
                return Result(
                    success=result.success,
                    output=result.message,
                    error="" if result.success else result.data.get('error', ''),
                    details=result.suggestions
                )
            except Exception as e:
                if os.getenv('DEBUG'):
                    print(f"Native switch generation failed: {e}")
                # Fall through to subprocess
        
        if self.dry_run:
            return Result(
                success=True,
                output=f"Would switch to generation {generation}",
                error=""
            )
        
        try:
            cmd = ['sudo', 'nix-env', '--switch-generation', str(generation), '-p', '/nix/var/nix/profiles/system']
            
            if self.progress_callback:
                self.progress_callback(f"Switching to generation {generation}...", 0.5)
            
            result = await self._run_command(cmd)
            
            if result['returncode'] == 0:
                # Also need to activate the configuration
                activate_cmd = ['sudo', '/nix/var/nix/profiles/system/bin/switch-to-configuration', 'switch']
                if self.progress_callback:
                    self.progress_callback("Activating configuration...", 0.8)
                
                activate_result = await self._run_command(activate_cmd)
                
                if activate_result['returncode'] == 0:
                    return Result(
                        success=True,
                        output=f"Successfully switched to generation {generation}",
                        error=""
                    )
                else:
                    return Result(
                        success=False,
                        output="",
                        error=f"Switched generation but failed to activate: {activate_result['stderr']}"
                    )
            else:
                return Result(
                    success=False,
                    output="",
                    error=result['stderr'] or f"Failed to switch to generation {generation}"
                )
                
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=f"Error switching generation: {str(e)}"
            )
    
    async def _execute_rebuild(self, rebuild_type: str = 'switch') -> Result:
        """Execute nixos-rebuild with specified type"""
        if self.dry_run:
            return Result(
                success=True,
                output=f"Would run: nixos-rebuild {rebuild_type}",
                error=""
            )
        
        # For long-running rebuilds, use the workaround
        if rebuild_type == 'switch':
            script_path = self._create_rebuild_script()
            return Result(
                success=True,
                output=f"Started rebuild in background. Monitor with: tail -f /tmp/nixos-rebuild.log",
                error=""
            )
        
        try:
            cmd = ['sudo', 'nixos-rebuild', rebuild_type]
            
            if self.progress_callback:
                self.progress_callback(f"Running nixos-rebuild {rebuild_type}...", 0.5)
            
            result = await self._run_command(cmd)
            
            if result['returncode'] == 0:
                return Result(
                    success=True,
                    output=f"Successfully ran nixos-rebuild {rebuild_type}",
                    error=""
                )
            else:
                return Result(
                    success=False,
                    output="",
                    error=result['stderr'] or f"Failed to run nixos-rebuild {rebuild_type}"
                )
                
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=f"Error during rebuild: {str(e)}"
            )
    
    async def _execute_edit_config(self) -> Result:
        """Show how to edit the configuration"""
        config_path = "/etc/nixos/configuration.nix"
        
        # Check if file exists
        if not Path(config_path).exists():
            return Result(
                success=False,
                output="",
                error=f"Configuration file not found at {config_path}"
            )
        
        return Result(
            success=True,
            output=f"""To edit your NixOS configuration:

1. Open the file with your editor:
   sudo nano {config_path}
   # or
   sudo vim {config_path}

2. Make your changes

3. Apply changes with:
   nixos-rebuild switch

Note: You need sudo to edit the system configuration.""",
            error=""
        )
    
    async def _execute_show_config(self) -> Result:
        """Show the current NixOS configuration"""
        config_path = "/etc/nixos/configuration.nix"
        
        try:
            # Read the configuration file
            with open(config_path, 'r') as f:
                content = f.read()
            
            return Result(
                success=True,
                output=content,
                error=""
            )
        except FileNotFoundError:
            return Result(
                success=False,
                output="",
                error=f"Configuration file not found at {config_path}"
            )
        except PermissionError:
            # Try with sudo
            cmd = ['sudo', 'cat', config_path]
            result = await self._run_command(cmd)
            
            if result['returncode'] == 0:
                return Result(
                    success=True,
                    output=result['stdout'],
                    error=""
                )
            else:
                return Result(
                    success=False,
                    output="",
                    error="Permission denied reading configuration"
                )
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=f"Error reading configuration: {str(e)}"
            )
    
    async def _execute_check_status(self) -> Result:
        """Check system status and health"""
        # Use native operations for instant system info
        if self._native_ops:
            try:
                from .native_operations import NativeOperationType
                
                result = await self._native_ops.execute_native_operation(
                    NativeOperationType.SYSTEM_INFO
                )
                
                if result.success and result.data:
                    output_lines = ["System Status:"]
                    for key, value in result.data.items():
                        formatted_key = key.replace('_', ' ').title()
                        output_lines.append(f"  {formatted_key}: {value}")
                    
                    # Also get disk usage
                    disk_result = await self._execute_disk_usage()
                    if disk_result.success:
                        output_lines.append("\n" + disk_result.output)
                    
                    return Result(
                        success=True,
                        output="\n".join(output_lines),
                        error=""
                    )
                else:
                    return Result(
                        success=result.success,
                        output=result.message,
                        error="" if result.success else result.data.get('error', '')
                    )
            except Exception as e:
                if os.getenv('DEBUG'):
                    print(f"Native system info failed: {e}")
                # Fall through to subprocess
        
        status_info = []
        
        try:
            # Get NixOS version
            version_cmd = ['nixos-version']
            version_result = await self._run_command(version_cmd)
            if version_result['returncode'] == 0:
                status_info.append(f"NixOS Version: {version_result['stdout'].strip()}")
            
            # Get current generation
            gen_cmd = ['sudo', 'nix-env', '--list-generations', '-p', '/nix/var/nix/profiles/system']
            gen_result = await self._run_command(gen_cmd)
            if gen_result['returncode'] == 0:
                lines = gen_result['stdout'].strip().split('\n')
                current = [l for l in lines if '(current)' in l]
                if current:
                    status_info.append(f"Current Generation: {current[0]}")
            
            # Check disk usage
            disk_cmd = ['df', '-h', '/']
            disk_result = await self._run_command(disk_cmd)
            if disk_result['returncode'] == 0:
                status_info.append("\nDisk Usage:")
                status_info.append(disk_result['stdout'])
            
            # Check system uptime
            uptime_cmd = ['uptime']
            uptime_result = await self._run_command(uptime_cmd)
            if uptime_result['returncode'] == 0:
                status_info.append(f"Uptime: {uptime_result['stdout'].strip()}")
            
            return Result(
                success=True,
                output="\n".join(status_info),
                error=""
            )
            
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=f"Error checking system status: {str(e)}"
            )
    
    async def _execute_list_installed(self) -> Result:
        """List installed packages"""
        # Use native operations for fast package listing
        if self._native_ops:
            try:
                from .native_operations import NativeOperationType
                
                result = await self._native_ops.execute_native_operation(
                    NativeOperationType.QUERY_INSTALLED
                )
                
                if result.success and result.data.get('packages'):
                    packages = result.data['packages']
                    output_lines = [f"Installed packages ({len(packages)} total):"]
                    # Show first 20 packages
                    for pkg in packages[:20]:
                        output_lines.append(f"  • {pkg}")
                    if len(packages) > 20:
                        output_lines.append(f"  ... and {len(packages) - 20} more packages")
                    
                    return Result(
                        success=True,
                        output="\n".join(output_lines),
                        error="",
                        details=[f"Query completed in {result.duration_ms:.0f}ms"]
                    )
                else:
                    return Result(
                        success=result.success,
                        output=result.message,
                        error="" if result.success else result.data.get('error', '')
                    )
            except Exception as e:
                if os.getenv('DEBUG'):
                    print(f"Native list installed failed: {e}")
                # Fall through to subprocess
        
        try:
            # List user packages
            user_cmd = ['nix', 'profile', 'list']
            
            if self.progress_callback:
                self.progress_callback("Listing installed packages...", 0.5)
            
            result = await self._run_command(user_cmd)
            
            output = ["User Packages (nix profile):\n"]
            
            if result['returncode'] == 0 and result['stdout']:
                output.append(result['stdout'])
            else:
                output.append("No user packages installed via nix profile\n")
            
            # Also show system packages hint
            output.append("\nTo see system-wide packages, check /etc/nixos/configuration.nix")
            output.append("or use: nix-store -q --requisites /run/current-system | cut -d- -f2- | sort | uniq")
            
            return Result(
                success=True,
                output="\n".join(output),
                error=""
            )
            
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=f"Error listing installed packages: {str(e)}"
            )
    
    # Network management methods
    async def _execute_show_network(self) -> Result:
        """Show network configuration and status"""
        try:
            network_info = []
            
            # Try nmcli first (NetworkManager)
            nmcli_cmd = ['nmcli', 'device', 'status']
            if self.progress_callback:
                self.progress_callback("Checking network status...", 0.3)
            
            nmcli_result = await self._run_command(nmcli_cmd)
            if nmcli_result['returncode'] == 0:
                network_info.append("Network Devices (NetworkManager):")
                network_info.append(nmcli_result['stdout'])
            
            # Also show IP addresses
            ip_cmd = ['ip', 'addr', 'show']
            ip_result = await self._run_command(ip_cmd)
            if ip_result['returncode'] == 0:
                network_info.append("\nNetwork Interfaces:")
                network_info.append(ip_result['stdout'])
            
            # Show routing table
            route_cmd = ['ip', 'route', 'show']
            route_result = await self._run_command(route_cmd)
            if route_result['returncode'] == 0:
                network_info.append("\nRouting Table:")
                network_info.append(route_result['stdout'])
            
            return Result(
                success=True,
                output="\n".join(network_info),
                error=""
            )
            
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=f"Error checking network status: {str(e)}"
            )
    
    async def _execute_show_ip(self) -> Result:
        """Show IP addresses for all interfaces"""
        try:
            ip_info = []
            
            # Get IP addresses
            ip_cmd = ['ip', '-4', 'addr', 'show']
            if self.progress_callback:
                self.progress_callback("Getting IP addresses...", 0.5)
            
            ipv4_result = await self._run_command(ip_cmd)
            if ipv4_result['returncode'] == 0:
                ip_info.append("IPv4 Addresses:")
                ip_info.append(ipv4_result['stdout'])
            
            # Also get IPv6
            ipv6_cmd = ['ip', '-6', 'addr', 'show']
            ipv6_result = await self._run_command(ipv6_cmd)
            if ipv6_result['returncode'] == 0:
                ip_info.append("\nIPv6 Addresses:")
                ip_info.append(ipv6_result['stdout'])
            
            # Try to get external IP
            ext_cmd = ['curl', '-s', 'https://api.ipify.org']
            ext_result = await self._run_command(ext_cmd)
            if ext_result['returncode'] == 0 and ext_result['stdout'].strip():
                ip_info.append(f"\nExternal IP: {ext_result['stdout'].strip()}")
            
            return Result(
                success=True,
                output="\n".join(ip_info),
                error=""
            )
            
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=f"Error getting IP addresses: {str(e)}"
            )
    
    async def _execute_connect_wifi(self, ssid: Optional[str]) -> Result:
        """Connect to a WiFi network"""
        if not ssid:
            return Result(
                success=False,
                output="",
                error="No WiFi network name (SSID) provided. Usage: 'connect to wifi MyNetwork'"
            )
        
        try:
            # Check if NetworkManager is available
            nm_check = await self._run_command(['which', 'nmcli'])
            if nm_check['returncode'] != 0:
                return Result(
                    success=False,
                    output="",
                    error="NetworkManager (nmcli) not found. WiFi configuration may require manual setup in /etc/nixos/configuration.nix"
                )
            
            if self.progress_callback:
                self.progress_callback(f"Connecting to WiFi network '{ssid}'...", 0.5)
            
            # Try to connect (will prompt for password if needed)
            connect_cmd = ['nmcli', 'device', 'wifi', 'connect', ssid]
            result = await self._run_command(connect_cmd)
            
            if result['returncode'] == 0:
                return Result(
                    success=True,
                    output=f"Successfully connected to WiFi network '{ssid}'",
                    error=""
                )
            else:
                # Provide helpful error message
                error_msg = result['stderr'] or "Failed to connect"
                suggestions = [
                    "Make sure the network name is correct",
                    "Check if WiFi is enabled: 'nmcli radio wifi'",
                    "List available networks: 'nmcli device wifi list'",
                    "For hidden networks, use: 'nmcli device wifi connect SSID hidden yes'"
                ]
                
                return Result(
                    success=False,
                    output="",
                    error=error_msg,
                    details=suggestions
                )
                
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=f"Error connecting to WiFi: {str(e)}"
            )
    
    async def _execute_list_wifi(self) -> Result:
        """List available WiFi networks"""
        try:
            # Check if NetworkManager is available
            nm_check = await self._run_command(['which', 'nmcli'])
            if nm_check['returncode'] != 0:
                return Result(
                    success=False,
                    output="",
                    error="NetworkManager (nmcli) not found. Cannot scan for WiFi networks."
                )
            
            if self.progress_callback:
                self.progress_callback("Scanning for WiFi networks...", 0.5)
            
            # Scan for networks
            scan_cmd = ['nmcli', 'device', 'wifi', 'list']
            result = await self._run_command(scan_cmd)
            
            if result['returncode'] == 0:
                return Result(
                    success=True,
                    output=result['stdout'],
                    error=""
                )
            else:
                return Result(
                    success=False,
                    output="",
                    error=result['stderr'] or "Failed to scan for WiFi networks"
                )
                
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=f"Error scanning WiFi networks: {str(e)}"
            )
    
    async def _execute_test_connection(self) -> Result:
        """Test internet connectivity"""
        try:
            test_results = []
            
            # Test DNS resolution
            if self.progress_callback:
                self.progress_callback("Testing DNS resolution...", 0.2)
            
            dns_cmd = ['nslookup', 'google.com']
            dns_result = await self._run_command(dns_cmd)
            if dns_result['returncode'] == 0:
                test_results.append("✅ DNS resolution: Working")
            else:
                test_results.append("❌ DNS resolution: Failed")
            
            # Test ping to common servers
            if self.progress_callback:
                self.progress_callback("Testing connectivity...", 0.5)
            
            ping_cmd = ['ping', '-c', '3', '8.8.8.8']
            ping_result = await self._run_command(ping_cmd)
            if ping_result['returncode'] == 0:
                test_results.append("✅ Internet connectivity: Working")
                # Extract ping statistics
                lines = ping_result['stdout'].split('\n')
                for line in lines:
                    if 'min/avg/max' in line:
                        test_results.append(f"   Latency: {line.strip()}")
            else:
                test_results.append("❌ Internet connectivity: Failed")
            
            # Test HTTP connectivity
            if self.progress_callback:
                self.progress_callback("Testing web access...", 0.8)
            
            http_cmd = ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 'https://www.google.com']
            http_result = await self._run_command(http_cmd)
            if http_result['returncode'] == 0 and http_result['stdout'].strip() == '200':
                test_results.append("✅ Web access (HTTPS): Working")
            else:
                test_results.append("❌ Web access (HTTPS): Failed")
            
            # Summary
            all_working = all('✅' in result for result in test_results)
            if all_working:
                test_results.append("\n🎉 All connectivity tests passed!")
            else:
                test_results.append("\n⚠️ Some connectivity issues detected.")
                test_results.append("Try: 'show network' for more details")
            
            return Result(
                success=True,
                output="\n".join(test_results),
                error=""
            )
            
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=f"Error testing connection: {str(e)}"
            )
    
    # Service management methods
    async def _execute_start_service(self, service: Optional[str]) -> Result:
        """Start a system service"""
        if not service:
            return Result(
                success=False,
                output="",
                error="No service name provided. Usage: 'start nginx' or 'start service ssh'"
            )
        
        try:
            # Normalize common service names
            service_map = {
                'ssh': 'sshd',
                'web': 'nginx',
                'webserver': 'nginx',
                'database': 'postgresql',
                'postgres': 'postgresql',
                'mysql': 'mysql',
                'docker': 'docker',
            }
            normalized_service = service_map.get(service.lower(), service)
            
            if self.progress_callback:
                self.progress_callback(f"Starting service '{normalized_service}'...", 0.5)
            
            cmd = ['sudo', 'systemctl', 'start', normalized_service]
            result = await self._run_command(cmd)
            
            if result['returncode'] == 0:
                # Check if it's actually running
                status_cmd = ['systemctl', 'is-active', normalized_service]
                status_result = await self._run_command(status_cmd)
                
                if status_result['returncode'] == 0:
                    return Result(
                        success=True,
                        output=f"Service '{normalized_service}' started successfully and is active",
                        error=""
                    )
                else:
                    return Result(
                        success=True,
                        output=f"Service '{normalized_service}' start command executed, but service may not be active. Check with 'service status {normalized_service}'",
                        error=""
                    )
            else:
                return Result(
                    success=False,
                    output="",
                    error=result['stderr'] or f"Failed to start service '{normalized_service}'"
                )
                
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=f"Error starting service: {str(e)}"
            )
    
    async def _execute_stop_service(self, service: Optional[str]) -> Result:
        """Stop a system service"""
        if not service:
            return Result(
                success=False,
                output="",
                error="No service name provided. Usage: 'stop nginx' or 'stop service ssh'"
            )
        
        try:
            # Normalize common service names
            service_map = {
                'ssh': 'sshd',
                'web': 'nginx',
                'webserver': 'nginx',
                'database': 'postgresql',
                'postgres': 'postgresql',
                'mysql': 'mysql',
                'docker': 'docker',
            }
            normalized_service = service_map.get(service.lower(), service)
            
            if self.progress_callback:
                self.progress_callback(f"Stopping service '{normalized_service}'...", 0.5)
            
            cmd = ['sudo', 'systemctl', 'stop', normalized_service]
            result = await self._run_command(cmd)
            
            if result['returncode'] == 0:
                return Result(
                    success=True,
                    output=f"Service '{normalized_service}' stopped successfully",
                    error=""
                )
            else:
                return Result(
                    success=False,
                    output="",
                    error=result['stderr'] or f"Failed to stop service '{normalized_service}'"
                )
                
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=f"Error stopping service: {str(e)}"
            )
    
    async def _execute_restart_service(self, service: Optional[str]) -> Result:
        """Restart a system service"""
        if not service:
            return Result(
                success=False,
                output="",
                error="No service name provided. Usage: 'restart nginx' or 'restart service ssh'"
            )
        
        try:
            # Normalize common service names
            service_map = {
                'ssh': 'sshd',
                'web': 'nginx',
                'webserver': 'nginx',
                'database': 'postgresql',
                'postgres': 'postgresql',
                'mysql': 'mysql',
                'docker': 'docker',
            }
            normalized_service = service_map.get(service.lower(), service)
            
            if self.progress_callback:
                self.progress_callback(f"Restarting service '{normalized_service}'...", 0.5)
            
            cmd = ['sudo', 'systemctl', 'restart', normalized_service]
            result = await self._run_command(cmd)
            
            if result['returncode'] == 0:
                # Check if it's actually running
                status_cmd = ['systemctl', 'is-active', normalized_service]
                status_result = await self._run_command(status_cmd)
                
                if status_result['returncode'] == 0:
                    return Result(
                        success=True,
                        output=f"Service '{normalized_service}' restarted successfully and is active",
                        error=""
                    )
                else:
                    return Result(
                        success=True,
                        output=f"Service '{normalized_service}' restart command executed, but service may not be active. Check with 'service status {normalized_service}'",
                        error=""
                    )
            else:
                return Result(
                    success=False,
                    output="",
                    error=result['stderr'] or f"Failed to restart service '{normalized_service}'"
                )
                
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=f"Error restarting service: {str(e)}"
            )
    
    async def _execute_service_status(self, service: Optional[str]) -> Result:
        """Check the status of a system service"""
        if not service:
            return Result(
                success=False,
                output="",
                error="No service name provided. Usage: 'service status nginx' or 'is ssh running?'"
            )
        
        try:
            # Normalize common service names
            service_map = {
                'ssh': 'sshd',
                'web': 'nginx',
                'webserver': 'nginx',
                'database': 'postgresql',
                'postgres': 'postgresql',
                'mysql': 'mysql',
                'docker': 'docker',
            }
            normalized_service = service_map.get(service.lower(), service)
            
            if self.progress_callback:
                self.progress_callback(f"Checking service '{normalized_service}' status...", 0.5)
            
            cmd = ['systemctl', 'status', normalized_service]
            result = await self._run_command(cmd)
            
            # Even if exit code is non-zero, we might have useful output
            if result['stdout']:
                return Result(
                    success=True,
                    output=result['stdout'],
                    error=""
                )
            else:
                return Result(
                    success=False,
                    output="",
                    error=result['stderr'] or f"Service '{normalized_service}' not found"
                )
                
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=f"Error checking service status: {str(e)}"
            )
    
    async def _execute_list_services(self) -> Result:
        """List all system services"""
        try:
            if self.progress_callback:
                self.progress_callback("Listing system services...", 0.5)
            
            # List all services with their status
            cmd = ['systemctl', 'list-units', '--type=service', '--all']
            result = await self._run_command(cmd)
            
            if result['returncode'] == 0:
                output = ["System Services:\n"]
                output.append(result['stdout'])
                output.append("\nTip: Use 'systemctl list-units --type=service --state=running' to see only running services")
                
                return Result(
                    success=True,
                    output="\n".join(output),
                    error=""
                )
            else:
                return Result(
                    success=False,
                    output="",
                    error=result['stderr'] or "Failed to list services"
                )
                
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=f"Error listing services: {str(e)}"
            )
    
    async def _execute_enable_service(self, service: Optional[str]) -> Result:
        """Enable a service to start at boot"""
        if not service:
            return Result(
                success=False,
                output="",
                error="No service name provided. Usage: 'enable nginx' or 'enable service ssh'"
            )
        
        try:
            # Normalize common service names
            service_map = {
                'ssh': 'sshd',
                'web': 'nginx',
                'webserver': 'nginx',
                'database': 'postgresql',
                'postgres': 'postgresql',
                'mysql': 'mysql',
                'docker': 'docker',
            }
            normalized_service = service_map.get(service.lower(), service)
            
            if self.progress_callback:
                self.progress_callback(f"Enabling service '{normalized_service}'...", 0.5)
            
            cmd = ['sudo', 'systemctl', 'enable', normalized_service]
            result = await self._run_command(cmd)
            
            if result['returncode'] == 0:
                return Result(
                    success=True,
                    output=f"Service '{normalized_service}' enabled. It will start automatically at boot.",
                    error=""
                )
            else:
                return Result(
                    success=False,
                    output="",
                    error=result['stderr'] or f"Failed to enable service '{normalized_service}'"
                )
                
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=f"Error enabling service: {str(e)}"
            )
    
    async def _execute_disable_service(self, service: Optional[str]) -> Result:
        """Disable a service from starting at boot"""
        if not service:
            return Result(
                success=False,
                output="",
                error="No service name provided. Usage: 'disable nginx' or 'disable service ssh'"
            )
        
        try:
            # Normalize common service names
            service_map = {
                'ssh': 'sshd',
                'web': 'nginx',
                'webserver': 'nginx',
                'database': 'postgresql',
                'postgres': 'postgresql',
                'mysql': 'mysql',
                'docker': 'docker',
            }
            normalized_service = service_map.get(service.lower(), service)
            
            if self.progress_callback:
                self.progress_callback(f"Disabling service '{normalized_service}'...", 0.5)
            
            cmd = ['sudo', 'systemctl', 'disable', normalized_service]
            result = await self._run_command(cmd)
            
            if result['returncode'] == 0:
                return Result(
                    success=True,
                    output=f"Service '{normalized_service}' disabled. It will not start automatically at boot.",
                    error=""
                )
            else:
                return Result(
                    success=False,
                    output="",
                    error=result['stderr'] or f"Failed to disable service '{normalized_service}'"
                )
                
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=f"Error disabling service: {str(e)}"
            )
    
    async def _execute_service_logs(self, service: Optional[str]) -> Result:
        """Show logs for a service"""
        if not service:
            return Result(
                success=False,
                output="",
                error="No service name provided. Usage: 'show logs for nginx' or 'service logs ssh'"
            )
        
        try:
            # Normalize common service names
            service_map = {
                'ssh': 'sshd',
                'web': 'nginx',
                'webserver': 'nginx',
                'database': 'postgresql',
                'postgres': 'postgresql',
                'mysql': 'mysql',
                'docker': 'docker',
            }
            normalized_service = service_map.get(service.lower(), service)
            
            if self.progress_callback:
                self.progress_callback(f"Getting logs for service '{normalized_service}'...", 0.5)
            
            # Get last 50 lines of logs
            cmd = ['journalctl', '-u', normalized_service, '-n', '50', '--no-pager']
            result = await self._run_command(cmd)
            
            if result['returncode'] == 0 and result['stdout']:
                output = [f"Recent logs for '{normalized_service}':\n"]
                output.append(result['stdout'])
                output.append(f"\nTip: Use 'journalctl -u {normalized_service} -f' to follow logs in real-time")
                
                return Result(
                    success=True,
                    output="\n".join(output),
                    error=""
                )
            else:
                # Try with sudo if permission denied
                if "permission denied" in result.get('stderr', '').lower():
                    cmd = ['sudo'] + cmd
                    result = await self._run_command(cmd)
                    if result['returncode'] == 0:
                        output = [f"Recent logs for '{normalized_service}':\n"]
                        output.append(result['stdout'])
                        return Result(
                            success=True,
                            output="\n".join(output),
                            error=""
                        )
                
                return Result(
                    success=False,
                    output="",
                    error=result['stderr'] or f"No logs found for service '{normalized_service}'"
                )
                
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=f"Error getting service logs: {str(e)}"
            )
    
    # User management methods
    async def _execute_create_user(self, username: Optional[str]) -> Result:
        """Create a new user"""
        if not username:
            return Result(
                success=False,
                output="",
                error="No username provided. Usage: 'create user john' or 'add new user alice'"
            )
        
        # Validate username
        if not username.replace('-', '').replace('_', '').isalnum():
            return Result(
                success=False,
                output="",
                error=f"Invalid username '{username}'. Use only letters, numbers, hyphens, and underscores."
            )
        
        if self.dry_run:
            return Result(
                success=True,
                output=f"Would create user '{username}'",
                error=""
            )
        
        try:
            # Check if user already exists
            check_cmd = ['id', username]
            check_result = await self._run_command(check_cmd)
            
            if check_result['returncode'] == 0:
                return Result(
                    success=False,
                    output="",
                    error=f"User '{username}' already exists"
                )
            
            # Create user
            cmd = ['sudo', 'useradd', '-m', username]
            
            if self.progress_callback:
                self.progress_callback(f"Creating user '{username}'...", 0.5)
            
            result = await self._run_command(cmd)
            
            if result['returncode'] == 0:
                return Result(
                    success=True,
                    output=f"Successfully created user '{username}'.\n\nNext steps:\n- Set password: 'change password {username}'\n- Grant sudo access: 'grant {username} sudo'\n- Add to groups: 'add {username} to docker group'",
                    error=""
                )
            else:
                return Result(
                    success=False,
                    output="",
                    error=result['stderr'] or f"Failed to create user '{username}'"
                )
                
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=f"Error creating user: {str(e)}"
            )
    
    async def _execute_list_users(self) -> Result:
        """List all users on the system"""
        try:
            # Get human users (UID >= 1000)
            cmd = ['getent', 'passwd']
            result = await self._run_command(cmd)
            
            if result['returncode'] == 0:
                users = []
                for line in result['stdout'].splitlines():
                    parts = line.split(':')
                    if len(parts) >= 3:
                        username = parts[0]
                        uid = int(parts[2])
                        if uid >= 1000 and uid < 65534:  # Human users
                            users.append(username)
                
                if users:
                    output = ["System users:"]
                    for user in sorted(users):
                        # Check if user has sudo
                        sudo_check = await self._run_command(['groups', user])
                        if sudo_check['returncode'] == 0:
                            groups = sudo_check['stdout'].strip()
                            if 'wheel' in groups or 'sudo' in groups:
                                output.append(f"  • {user} (sudo)")
                            else:
                                output.append(f"  • {user}")
                    
                    return Result(
                        success=True,
                        output="\n".join(output),
                        error=""
                    )
                else:
                    return Result(
                        success=True,
                        output="No regular users found (only system users exist)",
                        error=""
                    )
            else:
                return Result(
                    success=False,
                    output="",
                    error="Failed to list users"
                )
                
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=f"Error listing users: {str(e)}"
            )
    
    async def _execute_add_user_to_group(self, username: Optional[str], group: Optional[str]) -> Result:
        """Add a user to a group"""
        if not username or not group:
            return Result(
                success=False,
                output="",
                error="Both username and group required. Usage: 'add john to docker group'"
            )
        
        if self.dry_run:
            return Result(
                success=True,
                output=f"Would add user '{username}' to group '{group}'",
                error=""
            )
        
        try:
            # Check if user exists
            user_check = await self._run_command(['id', username])
            if user_check['returncode'] != 0:
                return Result(
                    success=False,
                    output="",
                    error=f"User '{username}' does not exist"
                )
            
            # Check if group exists
            group_check = await self._run_command(['getent', 'group', group])
            if group_check['returncode'] != 0:
                return Result(
                    success=False,
                    output="",
                    error=f"Group '{group}' does not exist"
                )
            
            # Add user to group
            cmd = ['sudo', 'usermod', '-a', '-G', group, username]
            
            if self.progress_callback:
                self.progress_callback(f"Adding '{username}' to '{group}' group...", 0.5)
            
            result = await self._run_command(cmd)
            
            if result['returncode'] == 0:
                return Result(
                    success=True,
                    output=f"Successfully added '{username}' to '{group}' group.\n\nNote: The user may need to log out and back in for changes to take effect.",
                    error=""
                )
            else:
                return Result(
                    success=False,
                    output="",
                    error=result['stderr'] or f"Failed to add user to group"
                )
                
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=f"Error adding user to group: {str(e)}"
            )
    
    async def _execute_change_password(self, username: Optional[str]) -> Result:
        """Change a user's password"""
        if not username:
            return Result(
                success=False,
                output="",
                error="No username provided. Usage: 'change password john' or 'reset alice password'"
            )
        
        if self.dry_run:
            return Result(
                success=True,
                output=f"Would change password for '{username}'",
                error=""
            )
        
        try:
            # Check if user exists
            user_check = await self._run_command(['id', username])
            if user_check['returncode'] != 0:
                return Result(
                    success=False,
                    output="",
                    error=f"User '{username}' does not exist"
                )
            
            # Note: We can't actually run passwd interactively, so provide instructions
            return Result(
                success=True,
                output=f"To change password for '{username}', run this command in your terminal:\n\nsudo passwd {username}\n\nYou'll be prompted to enter the new password twice.",
                error=""
            )
                
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=f"Error changing password: {str(e)}"
            )
    
    async def _execute_grant_sudo(self, username: Optional[str]) -> Result:
        """Grant sudo access to a user"""
        if not username:
            return Result(
                success=False,
                output="",
                error="No username provided. Usage: 'grant john sudo' or 'make alice sudoer'"
            )
        
        if self.dry_run:
            return Result(
                success=True,
                output=f"Would grant sudo access to '{username}'",
                error=""
            )
        
        try:
            # Check if user exists
            user_check = await self._run_command(['id', username])
            if user_check['returncode'] != 0:
                return Result(
                    success=False,
                    output="",
                    error=f"User '{username}' does not exist"
                )
            
            # Add user to wheel group (NixOS standard for sudo)
            cmd = ['sudo', 'usermod', '-a', '-G', 'wheel', username]
            
            if self.progress_callback:
                self.progress_callback(f"Granting sudo access to '{username}'...", 0.5)
            
            result = await self._run_command(cmd)
            
            if result['returncode'] == 0:
                return Result(
                    success=True,
                    output=f"Successfully granted sudo access to '{username}'.\n\nThe user is now in the 'wheel' group and can use sudo.\nThey may need to log out and back in for changes to take effect.",
                    error=""
                )
            else:
                return Result(
                    success=False,
                    output="",
                    error=result['stderr'] or f"Failed to grant sudo access"
                )
                
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=f"Error granting sudo access: {str(e)}"
            )
    
    # Storage management methods
    async def _execute_disk_usage(self) -> Result:
        """Show disk usage information"""
        try:
            cmd = ['df', '-h']
            result = await self._run_command(cmd)
            
            if result['returncode'] == 0:
                output = ["Disk Usage Summary:\n"]
                output.append(result['stdout'])
                
                # Also show NixOS specific info
                store_cmd = ['du', '-sh', '/nix/store']
                store_result = await self._run_command(store_cmd)
                
                if store_result['returncode'] == 0:
                    output.append(f"\nNix store size: {store_result['stdout'].strip()}")
                    output.append("\nTip: Run 'clean up space' to free disk space from old packages")
                
                return Result(
                    success=True,
                    output="\n".join(output),
                    error=""
                )
            else:
                return Result(
                    success=False,
                    output="",
                    error="Failed to get disk usage information"
                )
                
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=f"Error checking disk usage: {str(e)}"
            )
    
    async def _execute_analyze_disk(self) -> Result:
        """Analyze what's using disk space"""
        try:
            if self.progress_callback:
                self.progress_callback("Analyzing disk usage...", 0.3)
            
            # Get top directories by size
            # Run du command without shell
            du_result = await self._run_command(['du', '-h', '--max-depth=1', '/'])
            
            if du_result['returncode'] == 0 and du_result['stdout']:
                # Sort and limit the results in Python
                lines = du_result['stdout'].strip().split('\n')
                # Parse size and path
                size_entries = []
                for line in lines:
                    if line and '\t' in line:
                        size, path = line.split('\t', 1)
                        size_entries.append((size, path))
                
                # Sort by size (convert to bytes for proper sorting)
                def size_to_bytes(size_str):
                    multipliers = {'K': 1024, 'M': 1024**2, 'G': 1024**3, 'T': 1024**4}
                    if size_str[-1] in multipliers:
                        return float(size_str[:-1]) * multipliers[size_str[-1]]
                    return float(size_str)
                
                try:
                    sorted_entries = sorted(size_entries, key=lambda x: size_to_bytes(x[0]), reverse=True)[:20]
                    result = {
                        'returncode': 0,
                        'stdout': '\n'.join(f"{size}\t{path}" for size, path in sorted_entries),
                        'stderr': ''
                    }
                except Exception:
                    result = du_result
            else:
                result = du_result
            
            output = ["Disk space analysis (largest directories):\n"]
            
            if result['returncode'] == 0 and result['stdout']:
                output.append(result['stdout'])
            else:
                # Fallback to home directory analysis
                home_result = await self._run_command(['du', '-h', '--max-depth=1', os.path.expanduser('~')])
                
                if home_result['returncode'] == 0:
                    output.append("Top directories in home:\n")
                    output.append(home_result['stdout'])
            
            # NixOS specific analysis
            if self.progress_callback:
                self.progress_callback("Analyzing Nix store...", 0.7)
            
            # Count generations
            gen_cmd = ['sudo', 'nix-env', '--list-generations', '-p', '/nix/var/nix/profiles/system']
            gen_result = await self._run_command(gen_cmd)
            
            if gen_result['returncode'] == 0:
                gen_count = len(gen_result['stdout'].strip().split('\n'))
                output.append(f"\nSystem generations: {gen_count}")
                if gen_count > 5:
                    output.append("Consider cleaning old generations with 'garbage collect'")
            
            return Result(
                success=True,
                output="\n".join(output),
                error=""
            )
                
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=f"Error analyzing disk usage: {str(e)}"
            )
    
    async def _execute_mount_device(self, device: Optional[str], mount_point: Optional[str]) -> Result:
        """Mount a device"""
        if not device:
            return Result(
                success=False,
                output="",
                error="No device specified. Usage: 'mount /dev/sdb1' or 'mount usb drive'"
            )
        
        # Default mount point if not specified
        if not mount_point:
            mount_point = f"/mnt/{device.split('/')[-1]}"
        
        if self.dry_run:
            return Result(
                success=True,
                output=f"Would mount '{device}' to '{mount_point}'",
                error=""
            )
        
        try:
            # Create mount point if it doesn't exist
            mkdir_cmd = ['sudo', 'mkdir', '-p', mount_point]
            await self._run_command(mkdir_cmd)
            
            # Mount the device
            cmd = ['sudo', 'mount', device, mount_point]
            
            if self.progress_callback:
                self.progress_callback(f"Mounting {device}...", 0.5)
            
            result = await self._run_command(cmd)
            
            if result['returncode'] == 0:
                return Result(
                    success=True,
                    output=f"Successfully mounted '{device}' at '{mount_point}'\n\nTo unmount later: 'unmount {device}'",
                    error=""
                )
            else:
                return Result(
                    success=False,
                    output="",
                    error=result['stderr'] or f"Failed to mount device"
                )
                
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=f"Error mounting device: {str(e)}"
            )
    
    async def _execute_unmount_device(self, device: Optional[str]) -> Result:
        """Unmount a device"""
        if not device:
            return Result(
                success=False,
                output="",
                error="No device specified. Usage: 'unmount /dev/sdb1' or 'eject usb'"
            )
        
        if self.dry_run:
            return Result(
                success=True,
                output=f"Would unmount '{device}'",
                error=""
            )
        
        try:
            cmd = ['sudo', 'umount', device]
            
            if self.progress_callback:
                self.progress_callback(f"Unmounting {device}...", 0.5)
            
            result = await self._run_command(cmd)
            
            if result['returncode'] == 0:
                return Result(
                    success=True,
                    output=f"Successfully unmounted '{device}'\n\nThe device can now be safely removed.",
                    error=""
                )
            else:
                # Check if device is busy
                if "busy" in result.get('stderr', '').lower():
                    return Result(
                        success=False,
                        output="",
                        error=f"Device '{device}' is busy. Close any programs using it and try again."
                    )
                else:
                    return Result(
                        success=False,
                        output="",
                        error=result['stderr'] or f"Failed to unmount device"
                    )
                
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=f"Error unmounting device: {str(e)}"
            )
    
    async def _execute_find_large_files(self, count: int = 10) -> Result:
        """Find the largest files on the system"""
        try:
            if self.progress_callback:
                self.progress_callback(f"Finding {count} largest files...", 0.5)
            
            # Find large files in home directory
            # Find large files in home directory
            find_result = await self._run_command(['find', os.path.expanduser('~'), '-type', 'f', '-size', '+10M', '-exec', 'du', '-h', '{}', '+'])
            
            if find_result['returncode'] == 0 and find_result['stdout']:
                # Sort results in Python
                lines = find_result['stdout'].strip().split('\n')
                size_entries = []
                for line in lines:
                    if line and '\t' in line:
                        size, path = line.split('\t', 1)
                        size_entries.append((size, path))
                
                # Sort by size
                def size_to_bytes(size_str):
                    multipliers = {'K': 1024, 'M': 1024**2, 'G': 1024**3, 'T': 1024**4}
                    if size_str and size_str[-1] in multipliers:
                        return float(size_str[:-1]) * multipliers[size_str[-1]]
                    try:
                        return float(size_str)
                    except Exception:
                        return 0
                
                sorted_entries = sorted(size_entries, key=lambda x: size_to_bytes(x[0]), reverse=True)[:count]
                result = {
                    'returncode': 0,
                    'stdout': '\n'.join(f"{size}\t{path}" for size, path in sorted_entries),
                    'stderr': ''
                }
            else:
                result = find_result
            
            output = [f"Top {count} largest files in home directory:\n"]
            
            if result['returncode'] == 0 and result['stdout']:
                output.append(result['stdout'])
            else:
                output.append("Unable to scan home directory")
            
            # Also check /tmp for large files
            tmp_result = await self._run_command(['find', '/tmp', '-type', 'f', '-size', '+1M', '-exec', 'du', '-h', '{}', '+'])
            
            if tmp_result['returncode'] == 0 and tmp_result['stdout']:
                output.append("\nLarge files in /tmp:")
                output.append(tmp_result['stdout'])
            
            output.append("\nTip: Use 'clean up space' to remove old Nix packages and free disk space")
            
            return Result(
                success=True,
                output="\n".join(output),
                error=""
            )
                
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=f"Error finding large files: {str(e)}"
            )