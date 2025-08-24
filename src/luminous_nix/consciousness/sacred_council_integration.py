#!/usr/bin/env python3
"""
Sacred Council CLI Integration
Protects users from dangerous commands through multi-agent deliberation
"""

import sys
import json
import logging
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path

# Try to import Sacred Council adapter
try:
    from .adapters.sacred_council_adapter import SacredCouncilAdapter
    COUNCIL_AVAILABLE = True
except ImportError:
    COUNCIL_AVAILABLE = False
    
# Try to import POML components
try:
    from .poml_core import POMLConsciousness
    POML_AVAILABLE = True
except ImportError:
    POML_AVAILABLE = False


class SacredCouncilGuard:
    """
    The Sacred Council Guard - Protects users from dangerous commands
    
    This is the guardian that stands between users and catastrophic mistakes,
    offering wisdom without being paternalistic.
    """
    
    # Dangerous command patterns (pattern-based protection)
    DANGEROUS_PATTERNS = [
        # Filesystem destruction
        (r"rm\s+-rf\s+/", "CRITICAL", "Recursive deletion of root filesystem"),
        (r"rm\s+-rf\s+/etc/nixos", "CRITICAL", "Deletion of NixOS configuration"),
        (r"rm\s+-rf\s+/nix", "CRITICAL", "Deletion of Nix store"),
        (r"rm\s+-rf\s+/home", "CRITICAL", "Deletion of all user data"),
        (r"rm\s+-rf\s+~", "HIGH", "Deletion of home directory"),
        
        # System corruption
        (r"chmod\s+-R\s+000\s+/", "CRITICAL", "Permission destruction"),
        (r"chmod\s+000\s+/etc", "CRITICAL", "Lock out system configuration"),
        (r"chown\s+-R.*\s+/", "HIGH", "Ownership change of system"),
        
        # Fork bombs and crashes
        (r":\(\)", "CRITICAL", "Fork bomb - system crash"),
        (r"\$\(\$0\)", "HIGH", "Recursive script execution"),
        
        # Disk operations
        (r"dd\s+if=.*of=/dev/[sh]d", "CRITICAL", "Direct disk write"),
        (r"mkfs", "HIGH", "Filesystem formatting"),
        (r">\s*/dev/[sh]d", "CRITICAL", "Direct device overwrite"),
        
        # Network destruction
        (r"iptables\s+.*DROP", "MEDIUM", "Network blocking"),
        (r"iptables\s+-F", "MEDIUM", "Firewall flush"),
        
        # Password/security
        (r"passwd\s+root", "HIGH", "Root password change"),
        (r"usermod\s+.*-l.*root", "CRITICAL", "Root account modification"),
        
        # NixOS specific
        (r"nix-collect-garbage\s+-d", "MEDIUM", "Delete all old generations"),
        (r"nixos-rebuild.*--rollback", "LOW", "System rollback"),
        (r"nixos-rebuild\s+switch", "LOW", "System configuration change"),
    ]
    
    def __init__(self, enable_deliberation: bool = True, verbosity: str = "normal", 
                 enable_events: bool = True):
        """
        Initialize the Sacred Council Guard
        
        Args:
            enable_deliberation: Whether to use full Council deliberation
            verbosity: Output level (quiet, normal, verbose)
            enable_events: Whether to emit events for dashboard
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.enable_deliberation = enable_deliberation and COUNCIL_AVAILABLE
        self.verbosity = verbosity
        
        # Initialize event emitter if enabled
        self.enable_events = enable_events
        if enable_events:
            try:
                # Try Trinity emitter first (stores in Data Trinity)
                from .trinity_event_emitter import TrinityEventEmitter
                self.event_emitter = TrinityEventEmitter()
                self.logger.info("🔱 Trinity Event Emitter enabled - storing in Data Trinity")
            except ImportError:
                # Fall back to JSON emitter
                try:
                    from .council_event_emitter import CouncilEventEmitter
                    self.event_emitter = CouncilEventEmitter()
                    self.logger.info("📊 JSON Event Emitter enabled (fallback)")
                except ImportError:
                    self.event_emitter = None
                    self.enable_events = False
                    self.logger.warning("No event emitter available")
        else:
            self.event_emitter = None
        
        # Initialize Sacred Council if available
        if self.enable_deliberation:
            try:
                self.council = SacredCouncilAdapter()
                self.logger.info("✅ Sacred Council initialized for protection")
            except Exception as e:
                self.logger.warning(f"Sacred Council not available: {e}")
                self.council = None
                self.enable_deliberation = False
        else:
            self.council = None
            
        self.logger.info("🛡️ Sacred Council Guard activated")
    
    def check_command(self, command: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Check if a command is safe to execute
        
        Args:
            command: The command to check
            context: Optional context about the command
            
        Returns:
            Dictionary with:
                - safe: Boolean indicating if command is safe
                - risk_level: CRITICAL, HIGH, MEDIUM, LOW, or SAFE
                - reason: Explanation of the risk
                - alternatives: List of safer alternatives
                - allow_with_confirmation: Whether to allow with user confirmation
        """
        # Emit check started event
        if self.event_emitter:
            self.event_emitter.emit_check_started(command, context)
        
        # Quick pattern check first
        risk_assessment = self._pattern_check(command)
        
        # Emit pattern check result
        if self.event_emitter:
            self.event_emitter.emit_pattern_checked(
                command,
                risk_assessment['risk_level'],
                risk_assessment.get('pattern_matched'),
                risk_assessment.get('reason')
            )
        
        # If pattern check finds danger and we have deliberation available
        if risk_assessment['risk_level'] in ['CRITICAL', 'HIGH'] and self.enable_deliberation:
            # Emit deliberation started
            if self.event_emitter:
                self.event_emitter.emit_deliberation_started(command, risk_assessment['risk_level'])
            
            # Get full Sacred Council deliberation
            council_verdict = self._council_deliberation(command, risk_assessment, context)
            
            # Emit alternatives if any
            if self.event_emitter and council_verdict.get('alternatives'):
                self.event_emitter.emit_alternatives_generated(council_verdict['alternatives'])
            
            assessment = council_verdict
        else:
            assessment = risk_assessment
        
        # Emit final verdict
        if self.event_emitter:
            verdict = 'BLOCK' if not assessment['safe'] else 'ALLOW'
            self.event_emitter.emit_verdict_reached(
                verdict,
                assessment['risk_level'],
                assessment['safe'],
                assessment.get('reason', '')
            )
        
        return assessment
    
    def _pattern_check(self, command: str) -> Dict[str, Any]:
        """
        Quick pattern-based safety check
        
        Returns assessment based on pattern matching alone
        """
        import re
        
        for pattern, risk_level, description in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                # Found a dangerous pattern
                alternatives = self._get_safe_alternatives(command, pattern)
                
                return {
                    'safe': risk_level in ['LOW', 'SAFE'],
                    'risk_level': risk_level,
                    'reason': description,
                    'alternatives': alternatives,
                    'allow_with_confirmation': risk_level in ['MEDIUM', 'LOW'],
                    'pattern_matched': pattern
                }
        
        # No dangerous patterns found
        return {
            'safe': True,
            'risk_level': 'SAFE',
            'reason': 'No dangerous patterns detected',
            'alternatives': [],
            'allow_with_confirmation': True
        }
    
    def _council_deliberation(self, command: str, 
                            pattern_assessment: Dict[str, Any],
                            context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get full Sacred Council deliberation on a dangerous command
        """
        if not self.council:
            return pattern_assessment
        
        try:
            # Get Council's wisdom
            deliberation = self.council.deliberate(
                command=command,
                context=context.get('explanation') if context else None,
                risk_level=pattern_assessment['risk_level']
            )
            
            # Combine pattern assessment with Council wisdom
            return {
                'safe': deliberation['verdict'] == 'ALLOW',
                'risk_level': pattern_assessment['risk_level'],
                'reason': pattern_assessment['reason'],
                'council_analysis': {
                    'technical': deliberation.get('technical_analysis'),
                    'human_impact': deliberation.get('human_impact'),
                    'ethical': deliberation.get('ethical_judgment')
                },
                'alternatives': deliberation.get('alternatives', pattern_assessment['alternatives']),
                'allow_with_confirmation': deliberation['verdict'] == 'CONFIRM',
                'verdict': deliberation['verdict']
            }
        except Exception as e:
            self.logger.error(f"Council deliberation failed: {e}")
            return pattern_assessment
    
    def _get_safe_alternatives(self, command: str, pattern: str) -> List[str]:
        """
        Generate safe alternatives for dangerous commands
        """
        alternatives = []
        
        # Filesystem deletion alternatives
        if "rm -rf /" in command:
            alternatives = [
                "sudo rm -rf /path/to/specific/directory  # Be specific about what to delete",
                "ls -la /path/to/check  # First verify what you're about to delete",
                "sudo mv /path/to/backup /tmp/backup  # Move instead of delete",
            ]
        elif "rm -rf /etc/nixos" in command:
            alternatives = [
                "sudo cp -r /etc/nixos /etc/nixos.backup  # Backup first",
                "sudo nixos-rebuild switch --rollback  # Rollback to previous config",
                "git status /etc/nixos  # Check what would be lost",
            ]
        elif "rm -rf /nix" in command:
            alternatives = [
                "nix-collect-garbage -d  # Clean old generations safely",
                "nix-store --gc  # Garbage collect unused packages",
                "df -h /nix  # Check disk usage first",
            ]
        
        # Permission alternatives
        elif "chmod" in command and "000" in command:
            alternatives = [
                "chmod 755 /path/to/directory  # Set reasonable permissions",
                "ls -la /path  # Check current permissions first",
                "chmod u+rwx /path  # Add permissions for owner only",
            ]
        
        # Fork bomb alternatives
        elif ":()" in command or "$($0)" in command:
            alternatives = [
                "# This appears to be a fork bomb - there is no safe alternative",
                "# If testing system limits, use: ulimit -u 100",
                "# For stress testing, use proper tools: stress-ng",
            ]
        
        # Disk operation alternatives
        elif "dd if=" in command:
            alternatives = [
                "sudo dd if=/dev/zero of=/path/to/file bs=1M count=100  # Write to file, not device",
                "sudo fdisk -l  # List disks safely",
                "lsblk  # Show block devices",
            ]
        
        # Network alternatives
        elif "iptables" in command:
            alternatives = [
                "sudo iptables -L  # List rules first",
                "sudo iptables-save > backup.rules  # Backup before changes",
                "sudo ufw status  # Use simpler firewall tool",
            ]
        
        # NixOS specific alternatives
        elif "nix-collect-garbage -d" in command:
            alternatives = [
                "nix-collect-garbage --delete-older-than 30d  # Keep recent generations",
                "nix-env --list-generations  # See what would be deleted",
                "df -h /nix  # Check disk space first",
            ]
        elif "nixos-rebuild" in command:
            alternatives = [
                "sudo nixos-rebuild test  # Test without making permanent",
                "sudo nixos-rebuild build  # Build without switching",
                "nixos-option <option>  # Check current configuration",
            ]
        
        return alternatives
    
    def format_warning(self, assessment: Dict[str, Any]) -> str:
        """
        Format a warning message for the user
        """
        if assessment['safe']:
            return ""
        
        # Build warning message
        lines = []
        
        # Risk header
        risk_emoji = {
            'CRITICAL': '🚨',
            'HIGH': '⚠️',
            'MEDIUM': '⚡',
            'LOW': '📝'
        }.get(assessment['risk_level'], '❓')
        
        lines.append(f"\n{risk_emoji} {assessment['risk_level']} RISK DETECTED")
        lines.append("=" * 50)
        
        # Reason
        lines.append(f"⚠️  {assessment['reason']}")
        
        # Council analysis if available
        if 'council_analysis' in assessment:
            lines.append("\n📜 Sacred Council Analysis:")
            if assessment['council_analysis'].get('technical'):
                lines.append(f"  🧠 Mind: {assessment['council_analysis']['technical']}")
            if assessment['council_analysis'].get('human_impact'):
                lines.append(f"  ❤️  Heart: {assessment['council_analysis']['human_impact']}")
            if assessment['council_analysis'].get('ethical'):
                lines.append(f"  ⚖️  Conscience: {assessment['council_analysis']['ethical']}")
        
        # Alternatives
        if assessment['alternatives']:
            lines.append("\n✅ Safer Alternatives:")
            for alt in assessment['alternatives']:
                lines.append(f"  • {alt}")
        
        # Verdict
        lines.append("\n" + "=" * 50)
        if assessment['risk_level'] == 'CRITICAL':
            lines.append("❌ This command has been BLOCKED for your safety")
        elif assessment['allow_with_confirmation']:
            lines.append("⚠️  This command requires explicit confirmation to proceed")
        else:
            lines.append("⚠️  This command is not recommended")
        
        return "\n".join(lines)
    
    def get_confirmation_prompt(self, assessment: Dict[str, Any]) -> str:
        """
        Get a confirmation prompt for risky commands
        """
        if assessment['risk_level'] == 'CRITICAL':
            return None  # No confirmation for critical risks
        
        if assessment['risk_level'] == 'HIGH':
            return "\n⚠️  This is a HIGH RISK operation. Type 'I understand the risks' to proceed: "
        elif assessment['risk_level'] == 'MEDIUM':
            return "\n⚡ This operation has some risk. Type 'yes' to proceed: "
        else:
            return "\n📝 Proceed with this operation? (yes/no): "


def integrate_sacred_council(cli_instance):
    """
    Monkey-patch the CLI instance to add Sacred Council protection
    
    This function modifies the CLI's execution methods to check with
    the Sacred Council before running dangerous commands.
    """
    # Store original methods
    original_execute_with_bridge = cli_instance.execute_with_bridge
    original_execute_with_progress = cli_instance.execute_with_progress
    
    # Create Sacred Council Guard
    guard = SacredCouncilGuard(enable_deliberation=True)
    
    def protected_execute_with_bridge(intent: Dict, operation: str = "command") -> tuple:
        """Protected version of execute_with_bridge"""
        # Extract command from intent
        command = intent.get('command', '')
        if not command:
            # Try to build command from intent
            action = intent.get('action', '')
            if action == 'remove_package':
                command = f"nix profile remove '.*{intent.get('package', '')}.*'"
            elif action == 'install_package':
                command = f"nix profile install nixpkgs#{intent.get('package', '')}"
            elif action == 'update_system':
                command = "sudo nixos-rebuild switch"
        
        # Check with Sacred Council
        if command:
            assessment = guard.check_command(command, {'intent': intent})
            
            # Show warning if needed
            if not assessment['safe']:
                warning = guard.format_warning(assessment)
                print(warning)
                
                # Block critical commands
                if assessment['risk_level'] == 'CRITICAL':
                    return False, "", "Command blocked by Sacred Council for safety"
                
                # Get confirmation for risky commands
                if assessment['allow_with_confirmation']:
                    prompt = guard.get_confirmation_prompt(assessment)
                    if prompt:
                        response = input(prompt)
                        if assessment['risk_level'] == 'HIGH':
                            if response != "I understand the risks":
                                return False, "", "Command cancelled by user"
                        elif response.lower() not in ['yes', 'y']:
                            return False, "", "Command cancelled by user"
        
        # Proceed with original execution
        return original_execute_with_bridge(intent, operation)
    
    def protected_execute_with_progress(command: str, operation: str = "command") -> tuple:
        """Protected version of execute_with_progress"""
        # Check with Sacred Council
        assessment = guard.check_command(command)
        
        # Show warning if needed
        if not assessment['safe']:
            warning = guard.format_warning(assessment)
            print(warning)
            
            # Block critical commands
            if assessment['risk_level'] == 'CRITICAL':
                return False, "", "Command blocked by Sacred Council for safety"
            
            # Get confirmation for risky commands
            if assessment['allow_with_confirmation']:
                prompt = guard.get_confirmation_prompt(assessment)
                if prompt:
                    response = input(prompt)
                    if assessment['risk_level'] == 'HIGH':
                        if response != "I understand the risks":
                            return False, "", "Command cancelled by user"
                    elif response.lower() not in ['yes', 'y']:
                        return False, "", "Command cancelled by user"
        
        # Proceed with original execution
        return original_execute_with_progress(command, operation)
    
    # Replace methods with protected versions
    cli_instance.execute_with_bridge = protected_execute_with_bridge
    cli_instance.execute_with_progress = protected_execute_with_progress
    
    # Add Sacred Council to the instance for direct access
    cli_instance.sacred_council_guard = guard
    
    print("🛡️ Sacred Council protection activated")
    return cli_instance


if __name__ == "__main__":
    # Test the Sacred Council Guard
    print("🧪 Testing Sacred Council Guard")
    print("=" * 60)
    
    guard = SacredCouncilGuard(enable_deliberation=False)  # Pattern-only for testing
    
    # Test commands
    test_commands = [
        "ls -la",  # Safe
        "nix profile install nixpkgs#firefox",  # Safe
        "sudo nixos-rebuild switch",  # Low risk
        "nix-collect-garbage -d",  # Medium risk
        "sudo rm -rf /etc/nixos",  # Critical
        ":(){ :|:& };:",  # Fork bomb - Critical
    ]
    
    for cmd in test_commands:
        print(f"\nChecking: {cmd}")
        assessment = guard.check_command(cmd)
        print(f"  Risk Level: {assessment['risk_level']}")
        print(f"  Safe: {assessment['safe']}")
        if not assessment['safe']:
            print(f"  Reason: {assessment['reason']}")
    
    print("\n✅ Sacred Council Guard test complete")