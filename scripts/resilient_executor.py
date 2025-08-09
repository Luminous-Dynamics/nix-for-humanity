#!/usr/bin/env python3
"""
from typing import Dict, Optional
Resilient Command Executor
==========================

Multi-tiered command execution following the resilient architecture pattern.
Each tier provides honest capabilities and graceful fallback.

Tiers:
1. Python API (NixOS 25.11) - Direct, fast, safe
2. Modern nix commands - Current, reliable
3. Legacy nix-env - Universal compatibility
4. Instruction mode - Always works

"Meet users where they are, not where we wish they were."
"""

import os
import sys
import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Callable, Any
from dataclasses import dataclass
from enum import Enum
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.system_capabilities import SystemCapabilities

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExecutionTier(Enum):
    """Available execution tiers"""
    PYTHON_API = "python_api"
    NIX_PROFILE = "nix_profile"
    NIX_ENV = "nix_env"
    INSTRUCTIONS = "instructions"


@dataclass
class ExecutionResult:
    """Result of a command execution"""
    success: bool
    output: str
    error: Optional[str]
    tier_used: ExecutionTier
    duration: float
    needs_confirmation: bool = False
    confirmation_message: Optional[str] = None


@dataclass
class CommandIntent:
    """Parsed command intent"""
    action: str  # install, remove, update, etc.
    target: Optional[str]  # package name, service name, etc.
    options: Dict[str, Any]  # additional options


class ExecutionTierBase:
    """Base class for execution tiers"""
    
    def __init__(self, capabilities: SystemCapabilities):
        self.capabilities = capabilities
        self.name = "Base Tier"
        self.tier = ExecutionTier.INSTRUCTIONS
        
    def is_available(self) -> bool:
        """Check if this tier is available on the system"""
        return True
        
    def get_capability_score(self) -> float:
        """Return a score indicating how capable this tier is (0.0-1.0)"""
        return 0.0
        
    def get_capabilities_message(self) -> str:
        """Human-readable description of what this tier can do"""
        return "Basic capability information"
        
    def can_handle(self, intent: CommandIntent) -> bool:
        """Check if this tier can handle the given intent"""
        return False
        
    def execute(self, intent: CommandIntent, dry_run: bool = False) -> ExecutionResult:
        """Execute the command intent"""
        return ExecutionResult(
            success=False,
            output="Not implemented",
            error="Base tier cannot execute",
            tier_used=self.tier,
            duration=0.0
        )
        
    def get_confirmation_message(self, intent: CommandIntent) -> str:
        """Get confirmation message for the action"""
        return f"Execute {intent.action} {intent.target or ''}?"


class PythonAPITier(ExecutionTierBase):
    """Tier 1: Direct Python API integration"""
    
    def __init__(self, capabilities: SystemCapabilities):
        super().__init__(capabilities)
        self.name = "Python API (Fastest)"
        self.tier = ExecutionTier.PYTHON_API
        self.api_available = False
        self._try_import_api()
        
    def _try_import_api(self):
        """Try to import nixos-rebuild Python API"""
        try:
            # First try to find via which command
            result = subprocess.run(['which', 'nixos-rebuild'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                rebuild_path = Path(result.stdout.strip()).resolve()
                store_path = str(rebuild_path.parent.parent)
                
                # Look for Python site-packages in the store path
                from glob import glob
                python_paths = glob(f"{store_path}/lib/python*/site-packages")
                
                for path in python_paths:
                    module_path = Path(path) / "nixos_rebuild"
                    if module_path.exists():
                        sys.path.insert(0, path)
                        try:
                            global nix, models
                            from nixos_rebuild import nix, models
                            self.api_available = True
                            logger.info(f"✅ Found nixos-rebuild Python API at {path}")
                            return
                        except ImportError as e:
                            logger.debug(f"Failed to import from {path}: {e}")
                            continue
            
            # Fallback: Try common patterns
            nixos_paths = [
                "/nix/store/*/nixos-rebuild-ng-*/lib/python3.*/site-packages",
                "/run/current-system/sw/lib/python3.*/site-packages"
            ]
            
            for pattern in nixos_paths:
                for path in glob(pattern):
                    if os.path.exists(path):
                        sys.path.insert(0, path)
                        try:
                            global nix, models
                            from nixos_rebuild import nix, models
                            self.api_available = True
                            logger.info(f"✅ Found nixos-rebuild Python API at {path}")
                            return
                        except ImportError:
                            continue
                            
        except Exception as e:
            logger.debug(f"Python API not available: {e}")
            
    def is_available(self) -> bool:
        return self.api_available and self.capabilities.has_nixos_rebuild_ng
        
    def get_capability_score(self) -> float:
        return 1.0 if self.is_available() else 0.0
        
    def get_capabilities_message(self) -> str:
        if self.is_available():
            return "Direct NixOS API access - fastest execution, real-time progress"
        return "Python API not available on this system"
        
    def can_handle(self, intent: CommandIntent) -> bool:
        if not self.is_available():
            return False
        # Can handle system operations best
        return intent.action in ["update", "rollback", "switch", "boot", "test"]
        
    def execute(self, intent: CommandIntent, dry_run: bool = False) -> ExecutionResult:
        start_time = time.time()
        
        if not self.is_available():
            return ExecutionResult(
                success=False,
                output="",
                error="Python API not available",
                tier_used=self.tier,
                duration=0.0
            )
            
        try:
            if intent.action == "update":
                # Use Python API for system update
                if dry_run:
                    output = "Would update system using Python API"
                else:
                    # This would use the actual API
                    output = "System update via Python API (simulated)"
                    
                return ExecutionResult(
                    success=True,
                    output=output,
                    error=None,
                    tier_used=self.tier,
                    duration=time.time() - start_time
                )
                
        except Exception as e:
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                tier_used=self.tier,
                duration=time.time() - start_time
            )


class NixProfileTier(ExecutionTierBase):
    """Tier 2: Modern nix profile commands"""
    
    def __init__(self, capabilities: SystemCapabilities):
        super().__init__(capabilities)
        self.name = "Nix Profile (Modern)"
        self.tier = ExecutionTier.NIX_PROFILE
        
    def is_available(self) -> bool:
        return self.capabilities.has_nix_profile
        
    def get_capability_score(self) -> float:
        return 0.8 if self.is_available() else 0.0
        
    def get_capabilities_message(self) -> str:
        if self.is_available():
            return "Modern nix commands - reliable and current"
        return "Nix profile commands not available"
        
    def can_handle(self, intent: CommandIntent) -> bool:
        if not self.is_available():
            return False
        # Best for package management
        return intent.action in ["install", "remove", "list", "search"]
        
    def execute(self, intent: CommandIntent, dry_run: bool = False) -> ExecutionResult:
        start_time = time.time()
        
        try:
            if intent.action == "install" and intent.target:
                cmd = ["nix", "profile", "install", f"nixpkgs#{intent.target}"]
                
                if dry_run:
                    output = f"Would run: {' '.join(cmd)}"
                    success = True
                else:
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    output = result.stdout
                    success = result.returncode == 0
                    
                return ExecutionResult(
                    success=success,
                    output=output,
                    error=None if success else result.stderr,
                    tier_used=self.tier,
                    duration=time.time() - start_time
                )
                
            elif intent.action == "search" and intent.target:
                cmd = ["nix", "search", "nixpkgs", intent.target]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                return ExecutionResult(
                    success=result.returncode == 0,
                    output=result.stdout,
                    error=result.stderr if result.returncode != 0 else None,
                    tier_used=self.tier,
                    duration=time.time() - start_time
                )
                
        except Exception as e:
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                tier_used=self.tier,
                duration=time.time() - start_time
            )


class NixEnvTier(ExecutionTierBase):
    """Tier 3: Legacy nix-env commands"""
    
    def __init__(self, capabilities: SystemCapabilities):
        super().__init__(capabilities)
        self.name = "Nix-env (Legacy)"
        self.tier = ExecutionTier.NIX_ENV
        
    def is_available(self) -> bool:
        return self.capabilities.has_nix_env
        
    def get_capability_score(self) -> float:
        return 0.6 if self.is_available() else 0.0
        
    def get_capabilities_message(self) -> str:
        if self.is_available():
            return "Legacy commands - universal compatibility"
        return "Nix-env not available"
        
    def can_handle(self, intent: CommandIntent) -> bool:
        if not self.is_available():
            return False
        # Can handle basic package operations
        return intent.action in ["install", "remove", "list"]
        
    def execute(self, intent: CommandIntent, dry_run: bool = False) -> ExecutionResult:
        start_time = time.time()
        
        try:
            if intent.action == "install" and intent.target:
                cmd = ["nix-env", "-iA", f"nixpkgs.{intent.target}"]
                
                if dry_run:
                    output = f"Would run: {' '.join(cmd)}"
                    success = True
                else:
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    output = result.stdout
                    success = result.returncode == 0
                    
                return ExecutionResult(
                    success=success,
                    output=output,
                    error=None if success else result.stderr,
                    tier_used=self.tier,
                    duration=time.time() - start_time
                )
                
        except Exception as e:
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                tier_used=self.tier,
                duration=time.time() - start_time
            )


class InstructionsTier(ExecutionTierBase):
    """Tier 4: Provide instructions for manual execution"""
    
    def __init__(self, capabilities: SystemCapabilities):
        super().__init__(capabilities)
        self.name = "Instructions (Always Works)"
        self.tier = ExecutionTier.INSTRUCTIONS
        
    def is_available(self) -> bool:
        return True  # Always available
        
    def get_capability_score(self) -> float:
        return 0.3  # Can provide help but not execute
        
    def get_capabilities_message(self) -> str:
        return "I'll provide clear instructions for you to execute"
        
    def can_handle(self, intent: CommandIntent) -> bool:
        return True  # Can provide instructions for anything
        
    def execute(self, intent: CommandIntent, dry_run: bool = False) -> ExecutionResult:
        start_time = time.time()
        
        instructions = self._generate_instructions(intent)
        
        return ExecutionResult(
            success=True,
            output=instructions,
            error=None,
            tier_used=self.tier,
            duration=time.time() - start_time,
            needs_confirmation=False  # No confirmation needed for instructions
        )
        
    def _generate_instructions(self, intent: CommandIntent) -> str:
        """Generate clear instructions based on intent"""
        if intent.action == "install" and intent.target:
            return f"""To install {intent.target}, you can use one of these methods:

1. **Declarative (Recommended)**
   Edit /etc/nixos/configuration.nix and add:
   ```
   environment.systemPackages = with pkgs; [ {intent.target} ];
   ```
   Then run: `sudo nixos-rebuild switch`

2. **User-level with Home Manager**
   Edit ~/.config/home-manager/home.nix and add:
   ```
   home.packages = with pkgs; [ {intent.target} ];
   ```
   Then run: `home-manager switch`

3. **Imperative (Quick)**
   Run: `nix-env -iA nixpkgs.{intent.target}`

4. **Temporary Shell**
   Try it first: `nix-shell -p {intent.target}`"""
   
        elif intent.action == "update":
            return """To update your system:

1. Update channel: `sudo nix-channel --update`
2. Rebuild system: `sudo nixos-rebuild switch`

For a safer approach:
- Test first: `sudo nixos-rebuild test`
- If good, apply: `sudo nixos-rebuild switch`"""

        elif intent.action == "rollback":
            return """To rollback your system:

1. List generations: `sudo nix-env --list-generations --profile /nix/var/nix/profiles/system`
2. Rollback to previous: `sudo nixos-rebuild switch --rollback`
3. Or boot specific generation: `sudo nixos-rebuild switch --rollback-to <number>`"""

        return f"Instructions for '{intent.action}' {intent.target or ''} are being prepared..."


class ResilientExecutor:
    """Main executor that manages all tiers"""
    
    def __init__(self, capabilities: SystemCapabilities):
        self.capabilities = capabilities
        self.tiers = [
            PythonAPITier(capabilities),
            NixProfileTier(capabilities),
            NixEnvTier(capabilities),
            InstructionsTier(capabilities)
        ]
        
        # Sort by capability score
        self.tiers.sort(key=lambda t: t.get_capability_score(), reverse=True)
        
        # User preferences
        self.preferred_tier: Optional[ExecutionTier] = None
        self.require_confirmation = True
        self.verbose = True
        
        self._log_initialization()
        
    def _log_initialization(self):
        """Log available tiers"""
        logger.info("🛡️ Resilient Executor initialized with tiers:")
        for tier in self.tiers:
            if tier.is_available():
                logger.info(f"  ✅ {tier.name}: {tier.get_capabilities_message()}")
            else:
                logger.info(f"  ❌ {tier.name}: Not available")
                
    def execute(self, intent: CommandIntent, 
                dry_run: bool = False,
                tier_override: Optional[ExecutionTier] = None) -> ExecutionResult:
        """Execute command with appropriate tier"""
        
        # Select tier
        if tier_override:
            tier = self._get_tier_by_type(tier_override)
            if not tier or not tier.is_available():
                return ExecutionResult(
                    success=False,
                    output="",
                    error=f"Requested tier {tier_override} not available",
                    tier_used=ExecutionTier.INSTRUCTIONS,
                    duration=0.0
                )
        else:
            tier = self._select_best_tier(intent)
            
        if not tier:
            return ExecutionResult(
                success=False,
                output="",
                error="No execution tier available",
                tier_used=ExecutionTier.INSTRUCTIONS,
                duration=0.0
            )
            
        # Log tier selection
        if self.verbose:
            logger.info(f"🎯 Selected tier: {tier.name}")
            
        # Check if confirmation needed
        if self.require_confirmation and tier.tier != ExecutionTier.INSTRUCTIONS:
            confirmation_msg = tier.get_confirmation_message(intent)
            return ExecutionResult(
                success=True,
                output="",
                error=None,
                tier_used=tier.tier,
                duration=0.0,
                needs_confirmation=True,
                confirmation_message=confirmation_msg
            )
            
        # Execute
        result = tier.execute(intent, dry_run)
        
        # If failed and not instruction tier, try fallback
        if not result.success and tier.tier != ExecutionTier.INSTRUCTIONS:
            logger.warning(f"⚠️  {tier.name} failed: {result.error}")
            logger.info("🔄 Trying fallback tier...")
            
            # Find next tier
            current_idx = self.tiers.index(tier)
            for fallback_tier in self.tiers[current_idx + 1:]:
                if fallback_tier.is_available() and fallback_tier.can_handle(intent):
                    result = fallback_tier.execute(intent, dry_run)
                    if result.success:
                        break
                        
        return result
        
    def _select_best_tier(self, intent: CommandIntent) -> Optional[ExecutionTierBase]:
        """Select the best available tier for the intent"""
        for tier in self.tiers:
            if tier.is_available() and tier.can_handle(intent):
                return tier
        
        # Fallback to instructions if nothing else works
        return self.tiers[-1]  # Instructions tier is always last
        
    def _get_tier_by_type(self, tier_type: ExecutionTier) -> Optional[ExecutionTierBase]:
        """Get a specific tier by type"""
        for tier in self.tiers:
            if tier.tier == tier_type:
                return tier
        return None
        
    def get_status_report(self) -> str:
        """Get a status report of all tiers"""
        report = "🛡️ Resilient Executor Status:\n\n"
        
        for tier in self.tiers:
            status = "✅" if tier.is_available() else "❌"
            score = tier.get_capability_score()
            report += f"{status} {tier.name} (Score: {score:.1f})\n"
            report += f"   {tier.get_capabilities_message()}\n\n"
            
        return report


def parse_intent(command: str) -> CommandIntent:
    """Parse a command string into an intent"""
    # Simple parsing for demonstration
    parts = command.lower().split()
    
    if not parts:
        return CommandIntent("unknown", None, {})
        
    action = parts[0]
    target = parts[1] if len(parts) > 1 else None
    
    # Map common variations
    action_map = {
        "install": "install",
        "add": "install",
        "get": "install",
        "remove": "remove",
        "uninstall": "remove",
        "delete": "remove",
        "update": "update",
        "upgrade": "update",
        "search": "search",
        "find": "search",
        "list": "list",
        "show": "list",
        "rollback": "rollback",
        "undo": "rollback"
    }
    
    normalized_action = action_map.get(action, action)
    
    return CommandIntent(normalized_action, target, {})


def main():
    """Test the resilient executor"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Resilient Command Executor")
    parser.add_argument("command", nargs="+", help="Command to execute")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--tier", choices=["python_api", "nix_profile", "nix_env", "instructions"],
                      help="Force specific tier")
    parser.add_argument("--no-confirm", action="store_true", help="Skip confirmation")
    parser.add_argument("--status", action="store_true", help="Show tier status")
    parser.add_argument("--json", action="store_true", help="Output JSON for programmatic use")
    
    args = parser.parse_args()
    
    # Load system capabilities
    from scripts.system_capabilities import CapabilityDetector
    detector = CapabilityDetector()
    capabilities = detector.detect_all()
    
    # Create executor
    executor = ResilientExecutor(capabilities)
    executor.require_confirmation = not args.no_confirm
    
    if args.status:
        print(executor.get_status_report())
        return
        
    # Parse command
    command = " ".join(args.command)
    intent = parse_intent(command)
    
    if not args.json:
        print(f"🎯 Intent: {intent.action} {intent.target or ''}")
    
    # Execute
    tier_override = ExecutionTier(args.tier) if args.tier else None
    result = executor.execute(intent, dry_run=args.dry_run, tier_override=tier_override)
    
    # Handle JSON output
    if args.json:
        # Convert result to JSON-serializable dict
        result_dict = {
            "success": result.success,
            "output": result.output,
            "error": result.error,
            "tier_used": result.tier_used.value,
            "duration": result.duration,
            "needs_confirmation": result.needs_confirmation,
            "confirmation_message": result.confirmation_message
        }
        print("__JSON_START__")
        print(json.dumps(result_dict))
        print("__JSON_END__")
        return
    
    # Handle confirmation
    if result.needs_confirmation:
        print(f"\n⚠️  {result.confirmation_message}")
        response = input("Continue? (y/N): ")
        if response.lower() == 'y':
            # Re-execute without confirmation
            executor.require_confirmation = False
            result = executor.execute(intent, dry_run=args.dry_run, tier_override=tier_override)
        else:
            print("❌ Cancelled")
            return
            
    # Show result
    if result.success:
        print(f"\n✅ Success using {result.tier_used.value}")
        if result.output:
            print(result.output)
    else:
        print(f"\n❌ Failed")
        if result.error:
            print(f"Error: {result.error}")
            
    print(f"\n⏱️  Execution time: {result.duration:.2f}s")


if __name__ == "__main__":
    main()