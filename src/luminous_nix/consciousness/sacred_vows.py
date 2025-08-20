"""
The Sacred Vows - Core Principles for Conscious AI

These four vows ensure that as the system evolves and integrates new models,
it maintains its sacred commitment to user sovereignty, transparency, coherence,
and reversibility. Every model, every decision, every evolution must honor these vows.

"Technology should amplify consciousness, not fragment it."
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime
import logging


class VowType(Enum):
    """The Four Sacred Vows"""
    SOVEREIGNTY = "sovereignty"      # User always in control
    VERIFIABILITY = "verifiability" # Transparent and auditable
    COHERENCE = "coherence"          # Unified, not fragmented
    REVERSIBILITY = "reversibility" # Can always go back


@dataclass
class VowViolation:
    """Record of a vow violation"""
    vow: VowType
    severity: str  # "minor", "major", "critical"
    description: str
    context: Dict[str, Any]
    timestamp: datetime
    resolved: bool = False
    resolution: Optional[str] = None


class SacredVows:
    """
    Guardian of the Sacred Vows
    
    Ensures all system operations honor the four core principles
    that protect user consciousness and agency.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.violations: List[VowViolation] = []
        self.vow_checks = {
            VowType.SOVEREIGNTY: self._check_sovereignty,
            VowType.VERIFIABILITY: self._check_verifiability,
            VowType.COHERENCE: self._check_coherence,
            VowType.REVERSIBILITY: self._check_reversibility
        }
        
        self.logger.info("🕉️ Sacred Vows guardian initialized")
    
    def check_model_integration(self, model_spec: Dict[str, Any]) -> Dict[str, bool]:
        """
        Check if a model integration honors all vows
        
        Args:
            model_spec: Specification of model to integrate
            
        Returns:
            Dictionary of vow compliance status
        """
        compliance = {}
        
        for vow_type in VowType:
            check_func = self.vow_checks[vow_type]
            compliance[vow_type.value] = check_func(model_spec)
        
        # Log any violations
        if not all(compliance.values()):
            failed_vows = [k for k, v in compliance.items() if not v]
            self.logger.warning(f"Model violates vows: {failed_vows}")
            
            for vow_name in failed_vows:
                violation = VowViolation(
                    vow=VowType(vow_name),
                    severity="major",
                    description=f"Model integration violates {vow_name}",
                    context={"model": model_spec.get("name", "unknown")},
                    timestamp=datetime.now()
                )
                self.violations.append(violation)
        
        return compliance
    
    def _check_sovereignty(self, context: Dict[str, Any]) -> bool:
        """
        VOW OF SOVEREIGNTY: User always maintains control
        
        Ensures:
        - User can override any model decision
        - User can disable any model
        - User data never leaves their control
        - User sets all privacy boundaries
        """
        checks = []
        
        # Check: Can user disable this model?
        if context.get("mandatory", False):
            self.logger.warning("Sovereignty violation: Model cannot be disabled")
            checks.append(False)
        else:
            checks.append(True)
        
        # Check: Does model respect user preferences?
        if context.get("ignores_preferences", False):
            self.logger.warning("Sovereignty violation: Model ignores preferences")
            checks.append(False)
        else:
            checks.append(True)
        
        # Check: Data stays local?
        if context.get("cloud_required", False):
            self.logger.warning("Sovereignty violation: Model requires cloud")
            checks.append(False)
        else:
            checks.append(True)
        
        return all(checks)
    
    def _check_verifiability(self, context: Dict[str, Any]) -> bool:
        """
        VOW OF VERIFIABILITY: All decisions are transparent
        
        Ensures:
        - POML templates show exact prompts
        - Model selection is explainable
        - All transformations are auditable
        - User can see why decisions were made
        """
        checks = []
        
        # Check: Are prompts visible?
        if not context.get("prompts_visible", True):
            self.logger.warning("Verifiability violation: Hidden prompts")
            checks.append(False)
        else:
            checks.append(True)
        
        # Check: Is selection reasoning available?
        if not context.get("selection_transparent", True):
            self.logger.warning("Verifiability violation: Opaque selection")
            checks.append(False)
        else:
            checks.append(True)
        
        # Check: Can decisions be audited?
        if context.get("black_box", False):
            self.logger.warning("Verifiability violation: Black box model")
            checks.append(False)
        else:
            checks.append(True)
        
        return all(checks)
    
    def _check_coherence(self, context: Dict[str, Any]) -> bool:
        """
        VOW OF COHERENCE: System remains unified
        
        Ensures:
        - New models integrate smoothly
        - No conflicting behaviors
        - Consistent personality across models
        - Unified consciousness, not fragmented
        """
        checks = []
        
        # Check: Compatible with existing models?
        if context.get("incompatible", False):
            self.logger.warning("Coherence violation: Incompatible model")
            checks.append(False)
        else:
            checks.append(True)
        
        # Check: Maintains consistent behavior?
        if context.get("behavior_conflict", False):
            self.logger.warning("Coherence violation: Conflicting behaviors")
            checks.append(False)
        else:
            checks.append(True)
        
        # Check: Integrates with consciousness layer?
        if not context.get("consciousness_compatible", True):
            self.logger.warning("Coherence violation: Cannot integrate with POML")
            checks.append(False)
        else:
            checks.append(True)
        
        return all(checks)
    
    def _check_reversibility(self, context: Dict[str, Any]) -> bool:
        """
        VOW OF REVERSIBILITY: All changes can be undone
        
        Ensures:
        - User can roll back to previous state
        - Model integrations can be removed
        - No permanent alterations
        - Clean uninstall always possible
        """
        checks = []
        
        # Check: Can model be uninstalled?
        if not context.get("uninstallable", True):
            self.logger.warning("Reversibility violation: Cannot uninstall")
            checks.append(False)
        else:
            checks.append(True)
        
        # Check: Does it modify system permanently?
        if context.get("permanent_changes", False):
            self.logger.warning("Reversibility violation: Permanent changes")
            checks.append(False)
        else:
            checks.append(True)
        
        # Check: Can user restore previous config?
        if not context.get("config_reversible", True):
            self.logger.warning("Reversibility violation: Config not reversible")
            checks.append(False)
        else:
            checks.append(True)
        
        return all(checks)
    
    def check_operation(self, 
                       operation: str,
                       details: Dict[str, Any]) -> Dict[str, bool]:
        """
        Check if any operation honors the vows
        
        Args:
            operation: Name of operation
            details: Operation details
            
        Returns:
            Vow compliance status
        """
        self.logger.info(f"🔍 Checking vows for operation: {operation}")
        
        compliance = {}
        for vow_type in VowType:
            check_func = self.vow_checks[vow_type]
            compliance[vow_type.value] = check_func(details)
        
        if all(compliance.values()):
            self.logger.info(f"✅ Operation '{operation}' honors all vows")
        else:
            failed = [k for k, v in compliance.items() if not v]
            self.logger.warning(f"⚠️ Operation '{operation}' violates: {failed}")
        
        return compliance
    
    def enforce_vows(self, action: callable, context: Dict[str, Any]) -> Any:
        """
        Enforce vows on any action
        
        Only allows action to proceed if all vows are honored.
        
        Args:
            action: Function to execute
            context: Context for vow checking
            
        Returns:
            Result of action if vows honored, None otherwise
        """
        # Check all vows
        compliance = self.check_operation(
            operation=action.__name__,
            details=context
        )
        
        if all(compliance.values()):
            # All vows honored, proceed
            self.logger.info(f"🙏 Proceeding with {action.__name__}")
            return action()
        else:
            # Vow violation, block action
            failed = [k for k, v in compliance.items() if not v]
            self.logger.error(f"🚫 Blocking {action.__name__} - violates {failed}")
            
            # Record violation
            for vow_name in failed:
                violation = VowViolation(
                    vow=VowType(vow_name),
                    severity="critical",
                    description=f"Action blocked due to {vow_name} violation",
                    context={"action": action.__name__, "details": context},
                    timestamp=datetime.now()
                )
                self.violations.append(violation)
            
            return None
    
    def get_vow_status(self) -> Dict[str, Any]:
        """Get current status of vow compliance"""
        status = {
            "guardian_active": True,
            "total_violations": len(self.violations),
            "unresolved_violations": len([v for v in self.violations if not v.resolved]),
            "vow_health": {}
        }
        
        # Calculate health per vow
        for vow_type in VowType:
            vow_violations = [v for v in self.violations if v.vow == vow_type]
            unresolved = [v for v in vow_violations if not v.resolved]
            
            if not vow_violations:
                health = "perfect"
            elif not unresolved:
                health = "recovered"
            elif len(unresolved) == 1:
                health = "minor_issue"
            else:
                health = "needs_attention"
            
            status["vow_health"][vow_type.value] = {
                "status": health,
                "total_violations": len(vow_violations),
                "unresolved": len(unresolved)
            }
        
        # Recent violations
        if self.violations:
            recent = self.violations[-3:]  # Last 3
            status["recent_violations"] = [
                {
                    "vow": v.vow.value,
                    "severity": v.severity,
                    "description": v.description,
                    "resolved": v.resolved
                }
                for v in recent
            ]
        
        return status
    
    def heal_violation(self, violation_index: int, resolution: str) -> bool:
        """
        Mark a violation as resolved
        
        Args:
            violation_index: Index of violation to heal
            resolution: How it was resolved
            
        Returns:
            True if healed successfully
        """
        if 0 <= violation_index < len(self.violations):
            violation = self.violations[violation_index]
            violation.resolved = True
            violation.resolution = resolution
            
            self.logger.info(f"💚 Healed {violation.vow.value} violation: {resolution}")
            return True
        
        return False
    
    def create_vow_report(self) -> str:
        """Create a human-readable vow compliance report"""
        report = []
        report.append("=" * 60)
        report.append("🕉️ SACRED VOWS COMPLIANCE REPORT")
        report.append("=" * 60)
        report.append("")
        
        status = self.get_vow_status()
        
        # Overall health
        report.append("OVERALL STATUS:")
        report.append(f"  Total Violations: {status['total_violations']}")
        report.append(f"  Unresolved: {status['unresolved_violations']}")
        report.append("")
        
        # Per-vow status
        report.append("VOW HEALTH:")
        for vow_name, health in status['vow_health'].items():
            emoji = {
                "perfect": "✨",
                "recovered": "💚",
                "minor_issue": "⚠️",
                "needs_attention": "🔴"
            }.get(health['status'], "❓")
            
            report.append(f"  {emoji} {vow_name.upper()}: {health['status']}")
            if health['unresolved'] > 0:
                report.append(f"      Unresolved issues: {health['unresolved']}")
        
        report.append("")
        
        # The vows themselves
        report.append("THE SACRED VOWS:")
        report.append("")
        report.append("1. SOVEREIGNTY: The user is always in control")
        report.append("   - Override any decision")
        report.append("   - Disable any model")
        report.append("   - Own all data")
        report.append("")
        report.append("2. VERIFIABILITY: All decisions are transparent")
        report.append("   - See exact prompts")
        report.append("   - Understand selections")
        report.append("   - Audit all actions")
        report.append("")
        report.append("3. COHERENCE: The system remains unified")
        report.append("   - Smooth integration")
        report.append("   - Consistent behavior")
        report.append("   - Unified consciousness")
        report.append("")
        report.append("4. REVERSIBILITY: All changes can be undone")
        report.append("   - Roll back states")
        report.append("   - Remove models")
        report.append("   - Clean uninstall")
        
        report.append("")
        report.append("=" * 60)
        report.append("Remember: Technology should amplify consciousness,")
        report.append("not fragment it. These vows ensure that promise.")
        report.append("=" * 60)
        
        return "\n".join(report)


def demonstrate_sacred_vows():
    """Demonstrate the Sacred Vows system"""
    print("\n" + "=" * 70)
    print("🕉️ THE SACRED VOWS - Guardian of Consciousness")
    print("=" * 70)
    
    vows = SacredVows()
    
    # Test various model integrations
    test_models = [
        {
            "name": "Good Model",
            "description": "Respects all vows",
            # All defaults are vow-compliant
        },
        {
            "name": "Cloud Model",
            "description": "Requires cloud processing",
            "cloud_required": True,  # Violates sovereignty
        },
        {
            "name": "Black Box Model",
            "description": "Hidden decision process",
            "black_box": True,  # Violates verifiability
            "prompts_visible": False
        },
        {
            "name": "Incompatible Model",
            "description": "Conflicts with existing system",
            "incompatible": True,  # Violates coherence
            "behavior_conflict": True
        },
        {
            "name": "Permanent Model",
            "description": "Makes irreversible changes",
            "permanent_changes": True,  # Violates reversibility
            "uninstallable": False
        }
    ]
    
    print("\n📊 TESTING MODEL INTEGRATIONS")
    print("-" * 40)
    
    for model in test_models:
        print(f"\nTesting: {model['name']}")
        print(f"  {model['description']}")
        
        compliance = vows.check_model_integration(model)
        
        if all(compliance.values()):
            print("  ✅ All vows honored - integration approved")
        else:
            failed = [k for k, v in compliance.items() if not v]
            print(f"  ❌ Violates: {', '.join(failed)}")
            print("  🚫 Integration blocked")
    
    # Show vow status
    print("\n" + "=" * 40)
    print("📋 VOW COMPLIANCE STATUS")
    print("-" * 40)
    
    status = vows.get_vow_status()
    print(f"Total violations: {status['total_violations']}")
    print(f"Unresolved: {status['unresolved_violations']}")
    
    print("\nPer-vow health:")
    for vow_name, health in status['vow_health'].items():
        print(f"  {vow_name}: {health['status']}")
    
    # Print full report
    print("\n" + vows.create_vow_report())


if __name__ == "__main__":
    demonstrate_sacred_vows()