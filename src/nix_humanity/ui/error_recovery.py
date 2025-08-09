"""
from typing import Tuple, Dict, List, Optional
🔧 Error Recovery System for TUI

Provides automatic recovery mechanisms and guided recovery flows
for common error scenarios.
"""

from typing import Dict, List, Optional, Callable, Any, Tuple
from enum import Enum
from dataclasses import dataclass
import asyncio
import logging
from datetime import datetime, timedelta

from .error_handler import EnhancedError, ErrorCategory, ErrorSeverity

logger = logging.getLogger(__name__)


class RecoveryStrategy(Enum):
    """Recovery strategies"""
    RETRY = "retry"                    # Simple retry
    RETRY_WITH_BACKOFF = "backoff"    # Exponential backoff
    FALLBACK = "fallback"              # Use fallback method
    RESET = "reset"                    # Reset to known good state
    GUIDED = "guided"                  # Guide user through recovery
    AUTOMATIC = "automatic"            # Automatic recovery
    SKIP = "skip"                      # Skip operation
    ABORT = "abort"                    # Abort and return to safe state


@dataclass
class RecoveryAction:
    """A recovery action to take"""
    name: str
    description: str
    action: Callable
    requires_confirmation: bool = False
    estimated_duration: Optional[timedelta] = None
    success_rate: float = 0.8


@dataclass
class RecoveryPlan:
    """Complete recovery plan for an error"""
    error: EnhancedError
    strategy: RecoveryStrategy
    actions: List[RecoveryAction]
    fallback_plan: Optional['RecoveryPlan'] = None


class ErrorRecovery:
    """Handles error recovery in the TUI"""
    
    def __init__(self):
        self.recovery_history: List[Tuple[EnhancedError, bool]] = []
        self.recovery_strategies = self._init_recovery_strategies()
        self.max_retries = 3
        self.retry_delays = [1, 2, 5]  # Seconds
        
    def _init_recovery_strategies(self) -> Dict[ErrorCategory, RecoveryStrategy]:
        """Initialize default recovery strategies by error category"""
        return {
            ErrorCategory.NETWORK: RecoveryStrategy.RETRY_WITH_BACKOFF,
            ErrorCategory.PERMISSION: RecoveryStrategy.GUIDED,
            ErrorCategory.PACKAGE: RecoveryStrategy.FALLBACK,
            ErrorCategory.CONFIGURATION: RecoveryStrategy.GUIDED,
            ErrorCategory.SYNTAX: RecoveryStrategy.GUIDED,
            ErrorCategory.DEPENDENCY: RecoveryStrategy.AUTOMATIC,
            ErrorCategory.SYSTEM: RecoveryStrategy.RESET,
            ErrorCategory.UNKNOWN: RecoveryStrategy.SKIP
        }
        
    async def create_recovery_plan(self, error: EnhancedError) -> RecoveryPlan:
        """Create a recovery plan for an error"""
        strategy = self.recovery_strategies.get(
            error.category, 
            RecoveryStrategy.SKIP
        )
        
        actions = await self._create_recovery_actions(error, strategy)
        
        # Create main plan
        plan = RecoveryPlan(
            error=error,
            strategy=strategy,
            actions=actions
        )
        
        # Add fallback if needed
        if strategy in [RecoveryStrategy.RETRY, RecoveryStrategy.RETRY_WITH_BACKOFF]:
            fallback_strategy = RecoveryStrategy.GUIDED
            fallback_actions = await self._create_recovery_actions(error, fallback_strategy)
            plan.fallback_plan = RecoveryPlan(
                error=error,
                strategy=fallback_strategy,
                actions=fallback_actions
            )
            
        return plan
        
    async def _create_recovery_actions(self, 
                                     error: EnhancedError, 
                                     strategy: RecoveryStrategy) -> List[RecoveryAction]:
        """Create specific recovery actions based on error and strategy"""
        actions = []
        
        if strategy == RecoveryStrategy.RETRY:
            actions.append(RecoveryAction(
                name="retry_operation",
                description="Retry the failed operation",
                action=self._create_retry_action(error),
                estimated_duration=timedelta(seconds=5)
            ))
            
        elif strategy == RecoveryStrategy.RETRY_WITH_BACKOFF:
            actions.append(RecoveryAction(
                name="retry_with_backoff",
                description="Retry with exponential backoff",
                action=self._create_backoff_retry_action(error),
                estimated_duration=timedelta(seconds=15)
            ))
            
        elif strategy == RecoveryStrategy.FALLBACK:
            # Create fallback actions based on error type
            if error.category == ErrorCategory.PACKAGE:
                actions.extend([
                    RecoveryAction(
                        name="search_alternatives",
                        description="Search for alternative packages",
                        action=self._create_search_alternatives_action(error),
                        success_rate=0.9
                    ),
                    RecoveryAction(
                        name="update_channels",
                        description="Update package channels",
                        action=self._create_update_channels_action(),
                        requires_confirmation=True,
                        estimated_duration=timedelta(minutes=2)
                    )
                ])
                
        elif strategy == RecoveryStrategy.RESET:
            actions.append(RecoveryAction(
                name="reset_state",
                description="Reset to last known good state",
                action=self._create_reset_action(error),
                requires_confirmation=True,
                success_rate=0.95
            ))
            
        elif strategy == RecoveryStrategy.GUIDED:
            # Create guided recovery based on error
            if error.category == ErrorCategory.PERMISSION:
                actions.extend(self._create_permission_recovery_actions(error))
            elif error.category == ErrorCategory.CONFIGURATION:
                actions.extend(self._create_configuration_recovery_actions(error))
            elif error.category == ErrorCategory.SYNTAX:
                actions.extend(self._create_syntax_recovery_actions(error))
                
        elif strategy == RecoveryStrategy.AUTOMATIC:
            # Automatic recovery for dependencies
            if error.category == ErrorCategory.DEPENDENCY:
                actions.extend([
                    RecoveryAction(
                        name="resolve_dependencies",
                        description="Automatically resolve dependencies",
                        action=self._create_resolve_dependencies_action(error),
                        estimated_duration=timedelta(minutes=5),
                        success_rate=0.85
                    )
                ])
                
        return actions
        
    def _create_retry_action(self, error: EnhancedError) -> Callable:
        """Create simple retry action"""
        async def retry():
            logger.info(f"Retrying operation: {error.context.operation}")
            # Return instruction to retry
            return {"action": "retry", "operation": error.context.operation}
        return retry
        
    def _create_backoff_retry_action(self, error: EnhancedError) -> Callable:
        """Create exponential backoff retry action"""
        async def retry_with_backoff():
            for attempt, delay in enumerate(self.retry_delays):
                logger.info(f"Retry attempt {attempt + 1} after {delay}s delay")
                await asyncio.sleep(delay)
                # Return instruction to retry
                result = {"action": "retry", "operation": error.context.operation, "attempt": attempt + 1}
                # In real implementation, would check if retry succeeded
                # For now, simulate success on last attempt
                if attempt == len(self.retry_delays) - 1:
                    result["success"] = True
                yield result
        return retry_with_backoff
        
    def _create_search_alternatives_action(self, error: EnhancedError) -> Callable:
        """Create action to search for alternative packages"""
        async def search_alternatives():
            # Extract package name from error context
            if error.context.user_input:
                parts = error.context.user_input.split()
                if len(parts) > 1:
                    package = parts[-1]
                    return {
                        "action": "search",
                        "query": package,
                        "type": "alternatives"
                    }
            return {"action": "search", "type": "general"}
        return search_alternatives
        
    def _create_update_channels_action(self) -> Callable:
        """Create action to update Nix channels"""
        async def update_channels():
            return {
                "action": "execute",
                "command": "sudo nix-channel --update",
                "description": "Updating package channels"
            }
        return update_channels
        
    def _create_reset_action(self, error: EnhancedError) -> Callable:
        """Create reset to safe state action"""
        async def reset_state():
            return {
                "action": "reset",
                "target": "last_known_good",
                "component": error.context.component
            }
        return reset_state
        
    def _create_permission_recovery_actions(self, error: EnhancedError) -> List[RecoveryAction]:
        """Create guided recovery for permission errors"""
        actions = []
        
        # Check if sudo would help
        if error.context.user_input and not error.context.user_input.startswith("sudo"):
            actions.append(RecoveryAction(
                name="try_with_sudo",
                description="Try the command with sudo",
                action=lambda: {"action": "retry", "prefix": "sudo"},
                success_rate=0.9
            ))
            
        # Check permissions
        actions.append(RecoveryAction(
            name="check_permissions",
            description="Check and display file permissions",
            action=lambda: {"action": "diagnose", "type": "permissions"},
            success_rate=1.0
        ))
        
        # Fix permissions if possible
        actions.append(RecoveryAction(
            name="fix_permissions",
            description="Attempt to fix file permissions",
            action=lambda: {"action": "fix", "type": "permissions"},
            requires_confirmation=True,
            success_rate=0.7
        ))
        
        return actions
        
    def _create_configuration_recovery_actions(self, error: EnhancedError) -> List[RecoveryAction]:
        """Create guided recovery for configuration errors"""
        actions = []
        
        # Validate configuration
        actions.append(RecoveryAction(
            name="validate_config",
            description="Validate configuration syntax",
            action=lambda: {"action": "validate", "target": "configuration"},
            success_rate=1.0
        ))
        
        # Show diff from working config
        actions.append(RecoveryAction(
            name="show_diff",
            description="Show differences from last working configuration",
            action=lambda: {"action": "diff", "target": "configuration"},
            success_rate=1.0
        ))
        
        # Rollback option
        actions.append(RecoveryAction(
            name="rollback_config",
            description="Rollback to previous configuration",
            action=lambda: {"action": "rollback", "target": "configuration"},
            requires_confirmation=True,
            success_rate=0.95
        ))
        
        return actions
        
    def _create_syntax_recovery_actions(self, error: EnhancedError) -> List[RecoveryAction]:
        """Create guided recovery for syntax errors"""
        actions = []
        
        # Show syntax error location
        actions.append(RecoveryAction(
            name="show_error_location",
            description="Show exact location of syntax error",
            action=lambda: {"action": "highlight", "type": "syntax_error"},
            success_rate=1.0
        ))
        
        # Suggest fix
        actions.append(RecoveryAction(
            name="suggest_fix",
            description="Suggest syntax correction",
            action=lambda: {"action": "suggest", "type": "syntax_fix"},
            success_rate=0.8
        ))
        
        # Open in editor
        actions.append(RecoveryAction(
            name="open_editor",
            description="Open configuration in editor",
            action=lambda: {"action": "edit", "target": "configuration"},
            success_rate=1.0
        ))
        
        return actions
        
    def _create_resolve_dependencies_action(self, error: EnhancedError) -> Callable:
        """Create action to automatically resolve dependencies"""
        async def resolve_dependencies():
            return {
                "action": "resolve",
                "type": "dependencies",
                "automatic": True
            }
        return resolve_dependencies
        
    async def execute_recovery_plan(self, 
                                  plan: RecoveryPlan,
                                  progress_callback: Optional[Callable] = None) -> bool:
        """Execute a recovery plan"""
        success = False
        
        for i, action in enumerate(plan.actions):
            if progress_callback:
                await progress_callback(f"Executing: {action.description}", i, len(plan.actions))
                
            try:
                # Execute action
                if asyncio.iscoroutinefunction(action.action):
                    result = await action.action()
                elif asyncio.isgeneratorfunction(action.action):
                    async for result in action.action():
                        if progress_callback:
                            await progress_callback(f"Progress: {result}", i, len(plan.actions))
                else:
                    result = action.action()
                    
                # Check result
                if isinstance(result, dict) and result.get("success"):
                    success = True
                    break
                    
            except Exception as e:
                logger.error(f"Recovery action failed: {e}")
                continue
                
        # Try fallback plan if main plan failed
        if not success and plan.fallback_plan:
            if progress_callback:
                await progress_callback("Trying fallback recovery plan...", 0, 1)
            success = await self.execute_recovery_plan(plan.fallback_plan, progress_callback)
            
        # Record recovery attempt
        self.recovery_history.append((plan.error, success))
        
        return success
        
    def get_recovery_suggestions(self, error: EnhancedError) -> List[str]:
        """Get quick recovery suggestions for an error"""
        suggestions = []
        
        # Based on error category
        if error.category == ErrorCategory.NETWORK:
            suggestions.extend([
                "Check your internet connection",
                "Try again in a few moments",
                "Check if services are running: systemctl status"
            ])
        elif error.category == ErrorCategory.PERMISSION:
            suggestions.extend([
                "Try with sudo if appropriate",
                "Check file ownership and permissions",
                "Ensure you're in the correct user group"
            ])
        elif error.category == ErrorCategory.PACKAGE:
            suggestions.extend([
                "Search for the correct package name",
                "Update your package channels",
                "Check if the package exists in nixpkgs"
            ])
        elif error.category == ErrorCategory.CONFIGURATION:
            suggestions.extend([
                "Validate your configuration syntax",
                "Check for typos or missing imports",
                "Compare with a working configuration"
            ])
            
        return suggestions
        
    def get_recovery_stats(self) -> Dict[str, Any]:
        """Get recovery statistics"""
        if not self.recovery_history:
            return {
                "total_recoveries": 0,
                "success_rate": 0,
                "by_category": {}
            }
            
        total = len(self.recovery_history)
        successful = sum(1 for _, success in self.recovery_history if success)
        
        # By category
        by_category = {}
        for error, success in self.recovery_history:
            cat = error.category.value
            if cat not in by_category:
                by_category[cat] = {"total": 0, "successful": 0}
            by_category[cat]["total"] += 1
            if success:
                by_category[cat]["successful"] += 1
                
        return {
            "total_recoveries": total,
            "success_rate": successful / total if total > 0 else 0,
            "successful": successful,
            "failed": total - successful,
            "by_category": by_category
        }