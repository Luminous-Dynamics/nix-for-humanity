"""
POML to CLI Bridge - Progressive Integration

This bridge connects the POML Consciousness system to actual command execution,
enabling gradual activation from suggestion-only to full execution.
"""

import logging
import subprocess
from typing import Dict, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ExecutionMode(Enum):
    """Progressive execution modes"""
    SHADOW = "shadow"      # Watch only, no execution
    SUGGEST = "suggest"    # Suggest commands, no execution  
    ASSISTED = "assisted"  # Execute with confirmation
    FULL = "full"         # Execute automatically


@dataclass
class BridgeResult:
    """Result from bridge operation"""
    success: bool
    mode: ExecutionMode
    command: str
    output: Optional[str] = None
    error: Optional[str] = None
    suggestion: Optional[str] = None


class POMLtoCLIBridge:
    """
    Bridges POML Consciousness to CLI execution with progressive activation.
    
    This allows the aspirational POML system to gradually connect to real
    command execution as confidence and safety validation improves.
    """
    
    # Safe commands that can be executed without confirmation
    SAFE_COMMANDS = {
        'nix-env -q',           # Query installed packages
        'nix search',           # Search for packages
        'nix-env --version',    # Check version
        'nix-channel --list',   # List channels
        'nixos-version',        # Show NixOS version
        'nix-store --version',  # Store version
        'nix show-config',      # Show configuration
        'nix-instantiate --eval', # Evaluate expressions (read-only)
    }
    
    # Commands that need special handling
    PRIVILEGED_COMMANDS = {
        'nixos-rebuild': 'Rebuilds system configuration',
        'nix-env -i': 'Installs packages', 
        'nix-channel --update': 'Updates channels',
        'nix-collect-garbage': 'Cleans up store',
    }
    
    def __init__(self, readiness: float = 0.3):
        """
        Initialize bridge with readiness level.
        
        Args:
            readiness: Current readiness level (0.0 to 1.0)
                      0.0-0.3: Shadow mode (watch only)
                      0.3-0.6: Suggest mode (suggest commands)
                      0.6-0.9: Assisted mode (execute with confirmation)
                      0.9-1.0: Full mode (execute automatically)
        """
        self.readiness = readiness
        self.execution_log = []
        self.success_count = 0
        self.failure_count = 0
        
    def get_execution_mode(self) -> ExecutionMode:
        """Determine execution mode based on readiness"""
        if self.readiness < 0.3:
            return ExecutionMode.SHADOW
        elif self.readiness < 0.6:
            return ExecutionMode.SUGGEST
        elif self.readiness < 0.9:
            return ExecutionMode.ASSISTED
        else:
            return ExecutionMode.FULL
    
    def translate_poml_to_command(self, poml_result: Dict[str, Any]) -> str:
        """
        Translate POML consciousness result to executable command.
        
        Args:
            poml_result: Result from POML processing
            
        Returns:
            Executable command string
        """
        # Extract command from POML result structure
        if 'command' in poml_result:
            return poml_result['command']
        
        # Handle different POML response formats
        if 'action' in poml_result:
            action = poml_result['action']
            if action == 'install':
                package = poml_result.get('package', '')
                return f"nix-env -iA nixpkgs.{package}"
            elif action == 'search':
                query = poml_result.get('query', '')
                return f"nix search nixpkgs {query}"
            elif action == 'remove':
                package = poml_result.get('package', '')
                return f"nix-env -e {package}"
        
        # Fallback to raw command if present
        return poml_result.get('raw_command', '')
    
    def is_safe_command(self, command: str) -> bool:
        """Check if command is safe to execute without confirmation"""
        # Check against safe command prefixes
        for safe_cmd in self.SAFE_COMMANDS:
            if command.startswith(safe_cmd):
                return True
        return False
    
    def needs_privileges(self, command: str) -> bool:
        """Check if command needs elevated privileges"""
        for priv_cmd in self.PRIVILEGED_COMMANDS:
            if priv_cmd in command:
                return True
        return False
    
    def execute_command(self, command: str) -> Tuple[bool, str, str]:
        """
        Execute command with appropriate safety checks.
        
        Returns:
            Tuple of (success, stdout, stderr)
        """
        try:
            # Add safety timeout
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            success = result.returncode == 0
            return success, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out after 30 seconds"
        except Exception as e:
            return False, "", str(e)
    
    def bridge_execution(self, poml_result: Dict[str, Any]) -> BridgeResult:
        """
        Main bridge method - progressively executes based on readiness.
        
        Args:
            poml_result: Result from POML consciousness processing
            
        Returns:
            BridgeResult with execution details
        """
        # Translate POML to command
        command = self.translate_poml_to_command(poml_result)
        
        if not command:
            return BridgeResult(
                success=False,
                mode=ExecutionMode.SHADOW,
                command="",
                error="No command could be extracted from POML result"
            )
        
        # Determine execution mode
        mode = self.get_execution_mode()
        
        # Shadow mode - just observe
        if mode == ExecutionMode.SHADOW:
            logger.info(f"[SHADOW MODE] Would execute: {command}")
            return BridgeResult(
                success=True,
                mode=mode,
                command=command,
                suggestion=f"In shadow mode. Would execute: {command}"
            )
        
        # Suggest mode - provide command but don't execute
        if mode == ExecutionMode.SUGGEST:
            logger.info(f"[SUGGEST MODE] Suggested command: {command}")
            
            # Check safety and provide appropriate suggestion
            if self.is_safe_command(command):
                suggestion = f"Safe command suggested: {command}"
            elif self.needs_privileges(command):
                suggestion = f"Privileged command (needs sudo): {command}"
            else:
                suggestion = f"Command suggested (review carefully): {command}"
            
            return BridgeResult(
                success=True,
                mode=mode,
                command=command,
                suggestion=suggestion
            )
        
        # Assisted mode - execute safe commands, confirm others
        if mode == ExecutionMode.ASSISTED:
            if self.is_safe_command(command):
                # Execute safe commands directly
                success, stdout, stderr = self.execute_command(command)
                
                # Track success for readiness adjustment
                if success:
                    self.success_count += 1
                    self.adjust_readiness(0.01)  # Small increase
                else:
                    self.failure_count += 1
                    self.adjust_readiness(-0.02)  # Larger decrease
                
                return BridgeResult(
                    success=success,
                    mode=mode,
                    command=command,
                    output=stdout,
                    error=stderr if not success else None
                )
            else:
                # Unsafe commands need confirmation
                return BridgeResult(
                    success=True,
                    mode=mode,
                    command=command,
                    suggestion=f"Command needs confirmation: {command}\\nUse --yes to execute"
                )
        
        # Full mode - execute all commands (still with some safety)
        if mode == ExecutionMode.FULL:
            # Even in full mode, extremely dangerous commands should be blocked
            if 'rm -rf /' in command or 'dd if=/dev/zero' in command:
                return BridgeResult(
                    success=False,
                    mode=mode,
                    command=command,
                    error="Command blocked for safety reasons"
                )
            
            success, stdout, stderr = self.execute_command(command)
            
            # Track execution results
            if success:
                self.success_count += 1
            else:
                self.failure_count += 1
                self.adjust_readiness(-0.05)  # Reduce readiness on failure
            
            return BridgeResult(
                success=success,
                mode=mode,
                command=command,
                output=stdout,
                error=stderr if not success else None
            )
        
        return BridgeResult(
            success=False,
            mode=mode,
            command=command,
            error="Unknown execution mode"
        )
    
    def adjust_readiness(self, delta: float):
        """Adjust readiness level based on performance"""
        self.readiness = max(0.0, min(1.0, self.readiness + delta))
        logger.info(f"Readiness adjusted to {self.readiness:.2%}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get bridge execution statistics"""
        total = self.success_count + self.failure_count
        success_rate = self.success_count / total if total > 0 else 0
        
        return {
            'readiness': self.readiness,
            'mode': self.get_execution_mode().value,
            'total_executions': total,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'success_rate': success_rate,
            'can_execute': self.readiness >= 0.6
        }
    
    def progressive_test(self) -> bool:
        """
        Test bridge with progressively complex commands.
        Used for integration testing and readiness validation.
        """
        test_commands = [
            {'action': 'search', 'query': 'firefox'},  # Safe search
            {'command': 'nix-env -q'},                  # Safe query
            {'action': 'install', 'package': 'hello'},  # Needs confirmation
        ]
        
        results = []
        for test_cmd in test_commands:
            result = self.bridge_execution(test_cmd)
            results.append(result.success)
            logger.info(f"Test result: {result}")
        
        # Adjust readiness based on test results
        if all(results):
            self.adjust_readiness(0.1)
            return True
        else:
            self.adjust_readiness(-0.05)
            return False


# Integration helper for existing code
def integrate_with_cli(poml_consciousness, cli_executor):
    """
    Helper function to integrate POML consciousness with CLI executor.
    
    This can be called from existing code to progressively enable
    POML-based command execution.
    """
    bridge = POMLtoCLIBridge(readiness=0.5)  # Start in suggest mode
    
    def enhanced_execute(intent: str, context: Dict[str, Any] = None):
        """Enhanced execution through POML bridge"""
        # Process through POML consciousness
        poml_result = poml_consciousness.process_intent(intent, context)
        
        # Bridge to execution
        bridge_result = bridge.bridge_execution(poml_result)
        
        # Return appropriate response based on mode
        if bridge_result.mode == ExecutionMode.SUGGEST:
            return bridge_result.suggestion
        elif bridge_result.success:
            return bridge_result.output or "Command executed successfully"
        else:
            return f"Error: {bridge_result.error}"
    
    return enhanced_execute