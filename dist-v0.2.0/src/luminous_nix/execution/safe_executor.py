#!/usr/bin/env python3
"""
Safe Command Executor for Luminous Nix
Provides multiple execution modes with safety guards and rollback capability
"""

import subprocess
import os
import time
import json
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass
import hashlib

class ExecutionMode(Enum):
    """Command execution modes with different safety levels"""
    DRY_RUN = "dry_run"          # Show what would happen (current default)
    SANDBOX = "sandbox"          # Execute in isolated environment
    CONFIRMED = "confirmed"      # Execute with user confirmation
    AUTOMATED = "automated"      # Full trust mode (future)
    ROLLBACK = "rollback"        # Undo previous operation

class RiskLevel(Enum):
    """Risk assessment for commands"""
    SAFE = "safe"                # Read-only operations
    LOW = "low"                  # Package installation
    MEDIUM = "medium"            # Configuration changes
    HIGH = "high"                # System-wide changes
    CRITICAL = "critical"        # Destructive operations

@dataclass
class ExecutionResult:
    """Result of command execution"""
    success: bool
    output: str
    error: Optional[str] = None
    mode: ExecutionMode = ExecutionMode.DRY_RUN
    risk_level: RiskLevel = RiskLevel.SAFE
    rollback_command: Optional[str] = None
    execution_time: float = 0.0
    generation_before: Optional[int] = None
    generation_after: Optional[int] = None

class SafeExecutor:
    """
    Safe command execution with multiple modes and rollback capability
    """
    
    def __init__(self, 
                 default_mode: ExecutionMode = ExecutionMode.DRY_RUN,
                 auto_confirm_low_risk: bool = False):
        """
        Initialize safe executor
        
        Args:
            default_mode: Default execution mode
            auto_confirm_low_risk: Auto-confirm low risk operations
        """
        self.default_mode = default_mode
        self.auto_confirm_low_risk = auto_confirm_low_risk
        
        # Track execution history for rollback
        self.history: List[ExecutionResult] = []
        self.max_history = 50
        
        # Risk assessment patterns
        self.risk_patterns = {
            RiskLevel.CRITICAL: [
                'rm -rf', 'format', 'mkfs', 'dd if=',
                'nixos-rebuild boot', 'poweroff', 'reboot'
            ],
            RiskLevel.HIGH: [
                'nixos-rebuild switch', 'nix-collect-garbage',
                'systemctl disable', 'firewall', 'iptables'
            ],
            RiskLevel.MEDIUM: [
                'configuration.nix', 'hardware-configuration',
                'systemctl enable', 'systemctl restart'
            ],
            RiskLevel.LOW: [
                'nix profile install', 'nix-env -i',
                'home-manager switch'
            ],
            RiskLevel.SAFE: [
                'nix search', 'nix-env -q', 'nixos-option',
                'systemctl status', 'nix profile list'
            ]
        }
        
        # Commands that can be rolled back
        self.rollback_pairs = {
            'nix profile install': 'nix profile remove',
            'nix-env -iA': 'nix-env -e',
            'systemctl enable': 'systemctl disable',
            'systemctl start': 'systemctl stop',
        }
    
    def assess_risk(self, command: str) -> RiskLevel:
        """
        Assess risk level of a command
        
        Args:
            command: Command to assess
        
        Returns:
            Risk level
        """
        command_lower = command.lower()
        
        # Check patterns from highest to lowest risk
        for risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH, 
                          RiskLevel.MEDIUM, RiskLevel.LOW, RiskLevel.SAFE]:
            patterns = self.risk_patterns.get(risk_level, [])
            if any(pattern in command_lower for pattern in patterns):
                return risk_level
        
        # Default to medium for unknown commands
        return RiskLevel.MEDIUM
    
    def get_current_generation(self) -> Optional[int]:
        """Get current NixOS generation number"""
        try:
            result = subprocess.run(
                ['nixos-rebuild', 'list-generations'],
                capture_output=True,
                text=True,
                timeout=5
            )
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if '(current)' in line:
                    # Extract generation number
                    parts = line.split()
                    if parts:
                        return int(parts[0])
        except:
            pass
        return None
    
    def generate_rollback_command(self, command: str) -> Optional[str]:
        """
        Generate rollback command if possible
        
        Args:
            command: Original command
        
        Returns:
            Rollback command or None
        """
        # Check for direct rollback pairs
        for install_pattern, remove_pattern in self.rollback_pairs.items():
            if install_pattern in command:
                # Extract package name and create rollback
                parts = command.split()
                if 'nixpkgs#' in command:
                    # Extract package from nixpkgs#package format
                    for part in parts:
                        if 'nixpkgs#' in part:
                            package = part.split('#')[1]
                            return f"{remove_pattern} {package}"
                elif len(parts) > 2:
                    # Last part is usually the package
                    package = parts[-1]
                    return f"{remove_pattern} {package}"
        
        # For NixOS rebuilds, we can rollback to previous generation
        if 'nixos-rebuild' in command and 'switch' in command:
            return "nixos-rebuild switch --rollback"
        
        return None
    
    def confirm_execution(self, command: str, risk_level: RiskLevel) -> bool:
        """
        Get user confirmation for command execution
        
        Args:
            command: Command to execute
            risk_level: Risk level
        
        Returns:
            True if confirmed
        """
        # Auto-confirm safe operations
        if risk_level == RiskLevel.SAFE:
            return True
        
        # Auto-confirm low risk if enabled
        if self.auto_confirm_low_risk and risk_level == RiskLevel.LOW:
            return True
        
        # Show risk warning
        risk_emoji = {
            RiskLevel.LOW: "🟢",
            RiskLevel.MEDIUM: "🟡",
            RiskLevel.HIGH: "🟠",
            RiskLevel.CRITICAL: "🔴"
        }.get(risk_level, "⚪")
        
        print(f"\n{risk_emoji} Risk Level: {risk_level.value.upper()}")
        print(f"Command: {command}")
        
        # Show what will happen
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            print("\n⚠️  This command will make significant system changes!")
            
            # Get current generation for rollback info
            current_gen = self.get_current_generation()
            if current_gen:
                print(f"📍 Current generation: {current_gen}")
                print(f"💡 You can rollback with: nixos-rebuild switch --rollback")
        
        # Get confirmation
        response = input(f"\nExecute this command? [y/N]: ").strip().lower()
        return response == 'y'
    
    def execute_sandboxed(self, command: str) -> ExecutionResult:
        """
        Execute command in sandboxed environment
        
        Args:
            command: Command to execute
        
        Returns:
            Execution result
        """
        # Create temporary Nix shell for isolation
        sandbox_command = f"""
        nix-shell --pure --packages coreutils --run '
            # Sandbox environment
            export HOME=/tmp/nix-sandbox-home
            export NIX_PATH=nixpkgs=/nix/var/nix/profiles/per-user/root/channels/nixos
            mkdir -p $HOME
            {command}
        '
        """
        
        try:
            result = subprocess.run(
                sandbox_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return ExecutionResult(
                success=(result.returncode == 0),
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else None,
                mode=ExecutionMode.SANDBOX,
                risk_level=self.assess_risk(command)
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                output="",
                error="Command timed out in sandbox",
                mode=ExecutionMode.SANDBOX,
                risk_level=self.assess_risk(command)
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                mode=ExecutionMode.SANDBOX,
                risk_level=self.assess_risk(command)
            )
    
    def execute_real(self, command: str) -> ExecutionResult:
        """
        Execute command for real (with safety checks)
        
        Args:
            command: Command to execute
        
        Returns:
            Execution result
        """
        start_time = time.time()
        risk_level = self.assess_risk(command)
        
        # Get generation before execution
        generation_before = self.get_current_generation()
        
        # Generate potential rollback command
        rollback_cmd = self.generate_rollback_command(command)
        
        try:
            # Use specific timeout based on command type
            timeout = 120 if 'nixos-rebuild' in command else 30
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # Get generation after execution
            generation_after = self.get_current_generation()
            
            execution_result = ExecutionResult(
                success=(result.returncode == 0),
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else None,
                mode=ExecutionMode.CONFIRMED,
                risk_level=risk_level,
                rollback_command=rollback_cmd,
                execution_time=time.time() - start_time,
                generation_before=generation_before,
                generation_after=generation_after
            )
            
            # Add to history for potential rollback
            self.history.append(execution_result)
            if len(self.history) > self.max_history:
                self.history = self.history[-self.max_history:]
            
            return execution_result
            
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                output="",
                error=f"Command timed out after {timeout} seconds",
                mode=ExecutionMode.CONFIRMED,
                risk_level=risk_level,
                execution_time=time.time() - start_time
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                mode=ExecutionMode.CONFIRMED,
                risk_level=risk_level,
                execution_time=time.time() - start_time
            )
    
    def execute(self, 
                command: str,
                mode: Optional[ExecutionMode] = None) -> ExecutionResult:
        """
        Execute command with specified mode
        
        Args:
            command: Command to execute
            mode: Execution mode (uses default if not specified)
        
        Returns:
            Execution result
        """
        mode = mode or self.default_mode
        risk_level = self.assess_risk(command)
        
        # Handle different modes
        if mode == ExecutionMode.DRY_RUN:
            # Just show what would happen
            return ExecutionResult(
                success=True,
                output=f"[DRY RUN] Would execute: {command}",
                mode=ExecutionMode.DRY_RUN,
                risk_level=risk_level,
                rollback_command=self.generate_rollback_command(command)
            )
        
        elif mode == ExecutionMode.SANDBOX:
            print(f"🧪 Executing in sandbox: {command}")
            return self.execute_sandboxed(command)
        
        elif mode == ExecutionMode.CONFIRMED:
            # Get confirmation based on risk
            if self.confirm_execution(command, risk_level):
                print(f"⚡ Executing: {command}")
                return self.execute_real(command)
            else:
                return ExecutionResult(
                    success=False,
                    output="",
                    error="Execution cancelled by user",
                    mode=ExecutionMode.CONFIRMED,
                    risk_level=risk_level
                )
        
        elif mode == ExecutionMode.ROLLBACK:
            return self.rollback_last()
        
        else:
            return ExecutionResult(
                success=False,
                output="",
                error=f"Unknown execution mode: {mode}",
                mode=mode,
                risk_level=risk_level
            )
    
    def rollback_last(self) -> ExecutionResult:
        """Rollback the last executed command if possible"""
        if not self.history:
            return ExecutionResult(
                success=False,
                output="",
                error="No commands to rollback",
                mode=ExecutionMode.ROLLBACK,
                risk_level=RiskLevel.SAFE
            )
        
        last_execution = self.history[-1]
        
        # Check if we have a rollback command
        if last_execution.rollback_command:
            print(f"🔄 Rolling back with: {last_execution.rollback_command}")
            return self.execute_real(last_execution.rollback_command)
        
        # Check if we can rollback via generation
        if (last_execution.generation_before and 
            last_execution.generation_after and
            last_execution.generation_before != last_execution.generation_after):
            
            rollback_cmd = "nixos-rebuild switch --rollback"
            print(f"🔄 Rolling back to generation {last_execution.generation_before}")
            return self.execute_real(rollback_cmd)
        
        return ExecutionResult(
            success=False,
            output="",
            error="Cannot rollback - no rollback method available",
            mode=ExecutionMode.ROLLBACK,
            risk_level=RiskLevel.SAFE
        )
    
    def get_execution_summary(self) -> str:
        """Get summary of recent executions"""
        if not self.history:
            return "No commands executed yet"
        
        summary_parts = [
            f"Executed {len(self.history)} commands"
        ]
        
        # Count by risk level
        risk_counts = {}
        for execution in self.history:
            risk = execution.risk_level
            risk_counts[risk] = risk_counts.get(risk, 0) + 1
        
        risk_summary = ", ".join(
            f"{level.value}={count}" 
            for level, count in risk_counts.items()
        )
        summary_parts.append(f"Risk levels: {risk_summary}")
        
        # Success rate
        success_count = sum(1 for e in self.history if e.success)
        success_rate = (success_count / len(self.history)) * 100
        summary_parts.append(f"Success rate: {success_rate:.1f}%")
        
        return " | ".join(summary_parts)


# Integration example
if __name__ == "__main__":
    # Demo safe executor
    executor = SafeExecutor(default_mode=ExecutionMode.DRY_RUN)
    
    # Test commands with different risk levels
    test_commands = [
        "nix search nixpkgs firefox",           # SAFE
        "nix profile install nixpkgs#vim",      # LOW
        "systemctl restart nginx",              # MEDIUM
        "nixos-rebuild switch",                 # HIGH
        "rm -rf /tmp/test",                     # CRITICAL
    ]
    
    print("=" * 60)
    print("SAFE EXECUTOR DEMO")
    print("=" * 60)
    
    for cmd in test_commands:
        print(f"\n📝 Command: {cmd}")
        risk = executor.assess_risk(cmd)
        print(f"   Risk: {risk.value}")
        
        # Try dry run
        result = executor.execute(cmd, ExecutionMode.DRY_RUN)
        print(f"   {result.output}")
        
        if result.rollback_command:
            print(f"   Rollback: {result.rollback_command}")
    
    print("\n" + "=" * 60)
    print("Execution Summary:")
    print(executor.get_execution_summary())