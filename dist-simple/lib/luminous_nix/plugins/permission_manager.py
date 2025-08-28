"""
Permission Manager - The Sacred Boundary Keeper

This module manages plugin permissions, ensuring that every action
honors the boundaries declared in the manifest. It is the heart
of our trust architecture.
"""

import enum
from typing import Set, Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json


class Permission(enum.Enum):
    """
    The sacred capabilities that can be granted to plugins.
    Each permission represents a specific trust boundary.
    """
    # Filesystem permissions
    FILESYSTEM_READ = "filesystem.read"
    FILESYSTEM_WRITE = "filesystem.write"
    FILESYSTEM_WATCH = "filesystem.watch"
    
    # Network permissions
    NETWORK_LOCAL = "network.local"
    NETWORK_INTERNET = "network.internet"
    
    # Process permissions
    PROCESS_SPAWN = "process.spawn"
    PROCESS_MONITOR = "process.monitor"
    
    # System permissions
    SYSTEM_NOTIFICATIONS = "system.notifications"
    SYSTEM_INFO = "system.info"
    
    # Configuration permissions
    CONFIGURATION_READ = "configuration.read"
    CONFIGURATION_WRITE = "configuration.write"
    
    @classmethod
    def from_string(cls, value: str) -> Optional['Permission']:
        """Convert string to Permission enum"""
        for perm in cls:
            if perm.value == value:
                return perm
        return None


class RiskLevel(enum.Enum):
    """Risk levels for different permissions"""
    MINIMAL = "minimal"     # Read-only, local operations
    LOW = "low"             # Local modifications
    MEDIUM = "medium"       # Network access, spawning processes
    HIGH = "high"           # System configuration changes
    CRITICAL = "critical"   # Could compromise system integrity


@dataclass
class PermissionRequest:
    """A request from a plugin to perform an action"""
    plugin_id: str
    permission: Permission
    action: str
    context: Dict
    timestamp: datetime
    
    def to_audit_log(self) -> str:
        """Generate audit log entry"""
        return json.dumps({
            'timestamp': self.timestamp.isoformat(),
            'plugin_id': self.plugin_id,
            'permission': self.permission.value,
            'action': self.action,
            'context': self.context
        })


@dataclass
class ConsentDecision:
    """User's consent decision for a permission request"""
    granted: bool
    remember: bool
    duration_minutes: Optional[int]
    reason: Optional[str]
    timestamp: datetime


class PermissionManager:
    """
    The Guardian of plugin boundaries.
    
    This manager ensures that plugins can only perform actions
    within their declared and consented boundaries.
    """
    
    # Risk assessment for each permission
    PERMISSION_RISKS = {
        Permission.FILESYSTEM_READ: RiskLevel.MINIMAL,
        Permission.FILESYSTEM_WRITE: RiskLevel.LOW,
        Permission.FILESYSTEM_WATCH: RiskLevel.MINIMAL,
        Permission.NETWORK_LOCAL: RiskLevel.LOW,
        Permission.NETWORK_INTERNET: RiskLevel.MEDIUM,
        Permission.PROCESS_SPAWN: RiskLevel.MEDIUM,
        Permission.PROCESS_MONITOR: RiskLevel.MINIMAL,
        Permission.SYSTEM_NOTIFICATIONS: RiskLevel.MINIMAL,
        Permission.SYSTEM_INFO: RiskLevel.MINIMAL,
        Permission.CONFIGURATION_READ: RiskLevel.LOW,
        Permission.CONFIGURATION_WRITE: RiskLevel.HIGH,
    }
    
    def __init__(self, manifest: Dict):
        """
        Initialize with a plugin manifest.
        
        The manifest defines the soul of the plugin and its boundaries.
        """
        self.plugin_id = manifest.get('plugin', {}).get('id', 'unknown')
        self.governing_principle = manifest.get('consciousness', {}).get('governing_principle')
        self.sacred_promise = manifest.get('consciousness', {}).get('sacred_promise', '')
        
        # Extract granted permissions from manifest
        self.granted_permissions: Set[Permission] = set()
        capabilities = manifest.get('capabilities', {})
        for perm_str in capabilities.get('permissions', {}).get('required', []):
            perm = Permission.from_string(perm_str)
            if perm:
                self.granted_permissions.add(perm)
        
        # Extract forbidden actions from manifest
        self.forbidden_actions: Set[str] = set(
            manifest.get('boundaries', {}).get('forbidden_actions', [])
        )
        
        # Consent cache for remembered decisions
        self.consent_cache: Dict[str, ConsentDecision] = {}
        
        # Audit log of all permission checks
        self.audit_log: List[PermissionRequest] = []
    
    def can_perform(self, action: str, permission: Permission) -> Tuple[bool, str]:
        """
        The heart of trust: Can this plugin perform this action?
        
        Returns:
            (allowed, reason) - Whether action is allowed and why
        """
        # First check: Is this action explicitly forbidden?
        if self._is_forbidden(action):
            return False, f"Action '{action}' is explicitly forbidden by plugin boundaries"
        
        # Second check: Does the plugin have the required permission?
        if permission not in self.granted_permissions:
            return False, f"Plugin lacks permission '{permission.value}' for action '{action}'"
        
        # Third check: Is the permission aligned with governing principle?
        if not self._is_aligned_with_principle(permission):
            return False, f"Permission '{permission.value}' conflicts with governing principle '{self.governing_principle}'"
        
        # All checks passed
        return True, "Action permitted within declared boundaries"
    
    def _is_forbidden(self, action: str) -> bool:
        """
        Check if an action matches any forbidden pattern.
        """
        # Direct match
        if action in self.forbidden_actions:
            return True
        
        # Pattern matching (simple substring for now)
        for forbidden in self.forbidden_actions:
            if forbidden.lower() in action.lower():
                return True
        
        return False
    
    def _is_aligned_with_principle(self, permission: Permission) -> bool:
        """
        Verify that a permission aligns with the plugin's governing principle.
        
        This is where we enforce philosophical coherence.
        """
        principle_alignments = {
            "protect_attention": {
                # Can monitor and notify, but not write files or use network
                Permission.PROCESS_MONITOR,
                Permission.SYSTEM_NOTIFICATIONS,
                Permission.SYSTEM_INFO,
                Permission.FILESYSTEM_READ,
            },
            "preserve_privacy": {
                # Can work locally, but never network
                Permission.FILESYSTEM_READ,
                Permission.FILESYSTEM_WRITE,
                Permission.PROCESS_MONITOR,
                Permission.SYSTEM_INFO,
            },
            "enable_sovereignty": {
                # Can read everything to educate, but writes need consent
                Permission.FILESYSTEM_READ,
                Permission.CONFIGURATION_READ,
                Permission.SYSTEM_INFO,
                Permission.PROCESS_MONITOR,
            },
            "build_community": {
                # Can use network for connection
                Permission.NETWORK_LOCAL,
                Permission.NETWORK_INTERNET,
                Permission.FILESYSTEM_READ,
            }
        }
        
        # If we have specific alignments for this principle
        if self.governing_principle in principle_alignments:
            allowed = principle_alignments[self.governing_principle]
            # High-risk permissions need extra scrutiny
            if self.get_risk_level(permission) in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                return permission in allowed
        
        # Default: allow if risk is not high
        return self.get_risk_level(permission) not in [RiskLevel.HIGH, RiskLevel.CRITICAL]
    
    def request_permission(self, action: str, permission: Permission, 
                          context: Optional[Dict] = None) -> PermissionRequest:
        """
        Create a formal permission request.
        
        This generates an audit trail and prepares for consent ritual if needed.
        """
        request = PermissionRequest(
            plugin_id=self.plugin_id,
            permission=permission,
            action=action,
            context=context or {},
            timestamp=datetime.now()
        )
        
        # Add to audit log
        self.audit_log.append(request)
        
        return request
    
    def needs_consent(self, permission: Permission) -> bool:
        """
        Determine if a permission requires explicit user consent.
        
        This implements the Principle of Intentional Friction.
        """
        risk = self.get_risk_level(permission)
        
        # Always require consent for high-risk operations
        if risk in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            return True
        
        # Medium risk needs consent unless explicitly granted
        if risk == RiskLevel.MEDIUM:
            return permission not in self.granted_permissions
        
        # Low risk operations don't need consent if granted in manifest
        return False
    
    def get_risk_level(self, permission: Permission) -> RiskLevel:
        """Get the risk level for a permission"""
        return self.PERMISSION_RISKS.get(permission, RiskLevel.MEDIUM)
    
    def generate_consent_prompt(self, request: PermissionRequest) -> str:
        """
        Generate a meaningful consent prompt for the user.
        
        This is not just "Allow/Deny" - it's educational and mindful.
        """
        risk = self.get_risk_level(request.permission)
        risk_emoji = {
            RiskLevel.MINIMAL: "🟢",
            RiskLevel.LOW: "🟡",
            RiskLevel.MEDIUM: "🟠",
            RiskLevel.HIGH: "🔴",
            RiskLevel.CRITICAL: "⛔"
        }
        
        prompt = f"""
╔══════════════════════════════════════════════════════════╗
║                  🔐 Permission Request                     ║
╚══════════════════════════════════════════════════════════╝

Plugin: {self.plugin_id}
Governing Principle: {self.governing_principle}

Sacred Promise:
"{self.sacred_promise}"

Request:
  Action: {request.action}
  Permission: {request.permission.value}
  Risk Level: {risk_emoji[risk]} {risk.value.upper()}

What this means:
{self._explain_permission(request.permission)}

Context:
{json.dumps(request.context, indent=2) if request.context else "No additional context"}

Do you grant this permission?
[Y]es / [N]o / [A]lways / [Never] / [?] Learn more
"""
        return prompt
    
    def _explain_permission(self, permission: Permission) -> str:
        """
        Provide clear, educational explanation of what a permission means.
        """
        explanations = {
            Permission.FILESYSTEM_READ: 
                "📖 Read files on your system (cannot modify them)",
            Permission.FILESYSTEM_WRITE: 
                "✏️ Create or modify files on your system",
            Permission.FILESYSTEM_WATCH: 
                "👁️ Monitor when files change (passive observation)",
            Permission.NETWORK_LOCAL: 
                "🏠 Communicate within your local network only",
            Permission.NETWORK_INTERNET: 
                "🌍 Access the internet (could share data externally)",
            Permission.PROCESS_SPAWN: 
                "🚀 Start new programs or scripts",
            Permission.PROCESS_MONITOR: 
                "📊 See what programs are running (cannot control them)",
            Permission.SYSTEM_NOTIFICATIONS: 
                "🔔 Show you notifications",
            Permission.SYSTEM_INFO: 
                "ℹ️ Read system information (OS version, hardware, etc)",
            Permission.CONFIGURATION_READ: 
                "⚙️ Read your NixOS configuration",
            Permission.CONFIGURATION_WRITE: 
                "⚠️ MODIFY your NixOS configuration (requires rebuild)",
        }
        return explanations.get(permission, "Unknown permission")
    
    def record_consent(self, request: PermissionRequest, decision: ConsentDecision):
        """
        Record a user's consent decision.
        
        This builds trust through transparency and memory.
        """
        # Generate cache key
        cache_key = f"{request.permission.value}:{request.action}"
        
        if decision.remember:
            self.consent_cache[cache_key] = decision
        
        # Log the decision
        audit_entry = {
            'request': request.to_audit_log(),
            'decision': {
                'granted': decision.granted,
                'remember': decision.remember,
                'reason': decision.reason,
                'timestamp': decision.timestamp.isoformat()
            }
        }
        
        # In production, this would be saved to disk
        print(f"📝 Consent recorded: {json.dumps(audit_entry, indent=2)}")
    
    def get_boundaries_summary(self) -> str:
        """
        Generate a human-readable summary of this plugin's boundaries.
        
        This implements the Principle of Legible Boundaries.
        """
        summary = f"""
🔐 Permission Boundaries for {self.plugin_id}
════════════════════════════════════════════

Governing Principle: {self.governing_principle}

✅ GRANTED PERMISSIONS:
"""
        for perm in sorted(self.granted_permissions, key=lambda p: p.value):
            risk = self.get_risk_level(perm)
            summary += f"  • {perm.value} (Risk: {risk.value})\n"
            summary += f"    {self._explain_permission(perm)}\n"
        
        summary += "\n❌ FORBIDDEN ACTIONS:\n"
        for action in sorted(self.forbidden_actions)[:5]:  # Show first 5
            summary += f"  • {action}\n"
        
        if len(self.forbidden_actions) > 5:
            summary += f"  ... and {len(self.forbidden_actions) - 5} more\n"
        
        summary += f"\n📊 AUDIT SUMMARY:\n"
        summary += f"  Total requests: {len(self.audit_log)}\n"
        
        if self.audit_log:
            # Count by permission
            perm_counts = {}
            for req in self.audit_log:
                perm_counts[req.permission] = perm_counts.get(req.permission, 0) + 1
            
            summary += "  By permission:\n"
            for perm, count in sorted(perm_counts.items(), key=lambda x: x[1], reverse=True):
                summary += f"    • {perm.value}: {count} requests\n"
        
        return summary


# Example usage for testing
if __name__ == "__main__":
    # Load the Flow Guardian manifest
    import yaml
    from pathlib import Path
    
    manifest_path = Path(__file__).parent.parent.parent.parent / "plugins" / "flow-guardian" / "manifest.yaml"
    
    with open(manifest_path, 'r') as f:
        manifest = yaml.safe_load(f)
    
    # Create permission manager
    pm = PermissionManager(manifest)
    
    # Test some permissions
    print("=" * 60)
    print("Testing Permission Manager with Flow Guardian")
    print("=" * 60)
    
    # Test allowed action
    allowed, reason = pm.can_perform("block notification", Permission.SYSTEM_NOTIFICATIONS)
    print(f"\n✅ Can block notification? {allowed}")
    print(f"   Reason: {reason}")
    
    # Test forbidden action
    allowed, reason = pm.can_perform("share focus data with external services", Permission.NETWORK_INTERNET)
    print(f"\n❌ Can share data externally? {allowed}")
    print(f"   Reason: {reason}")
    
    # Test permission not granted
    allowed, reason = pm.can_perform("modify config", Permission.CONFIGURATION_WRITE)
    print(f"\n❌ Can modify config? {allowed}")
    print(f"   Reason: {reason}")
    
    # Generate consent prompt
    request = pm.request_permission(
        action="Monitor which apps steal focus",
        permission=Permission.PROCESS_MONITOR,
        context={"reason": "To track interruption sources"}
    )
    
    print("\n" + pm.generate_consent_prompt(request))
    
    # Show boundaries summary
    print(pm.get_boundaries_summary())