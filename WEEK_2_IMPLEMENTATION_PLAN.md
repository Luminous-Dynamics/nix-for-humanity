# 🚀 Week 2 Implementation Plan

**Date**: December 3-10, 2025
**Component**: DID Integration + CLI Commands + MATL Foundation
**Status**: Ready to implement (Week 1 complete: 13/13 tests ✅)

---

## 🎯 Week 2 Goals

### Primary Goals
1. **Integrate DID with State Manager** - Connect identity to operation tracking
2. **Create CLI Commands** - User-facing DID management
3. **Prepare MATL Foundation** - Set up trust scoring infrastructure

### Success Metrics
- ✅ State Manager tracks user DID for all operations
- ✅ CLI commands: `whoami`, `did setup`, `did status`
- ✅ User profile integration complete
- ✅ MATL module structure ready
- ✅ All tests passing (target: 20+ tests)

---

## 📅 Day-by-Day Plan

### **Day 1-2 (Dec 4-5): DID Integration with State Manager**

#### Task 1.1: Update State Manager to Track User DID

**File**: `src/luminous_nix/core/state_manager.py`

**Changes**:
```python
# Add to imports
from luminous_nix.mycelix import get_did_manager

# Add to OperationState dataclass
@dataclass
class OperationState:
    # ... existing fields ...

    # 🆕 User identity tracking
    user_did: Optional[str] = None  # User's DID
    assurance_level: Optional[str] = None  # E0-E4

    # 🆕 Trust metadata (for MATL Week 3)
    trust_score: Optional[float] = None  # 0.0-1.0
    trust_components: Dict[str, float] = field(default_factory=dict)  # PoGQ, TCDM, Entropy

# Update StateManager.__init__ to load DID
class StateManager:
    def __init__(self, storage_path: Optional[Path] = None):
        # ... existing init ...

        # 🆕 Load user DID
        self.did_manager = get_did_manager()
        self.current_user_did = self.did_manager.get_current_did()

    def create_operation(self, op_type: OperationType, ...) -> OperationState:
        # ... existing code ...

        # 🆕 Attach user DID to operation
        if self.current_user_did:
            op_state.user_did = self.current_user_did.did
            op_state.assurance_level = self.current_user_did.assurance_level

        return op_state
```

**Test**: `tests/core/test_state_manager_did_integration.py`

```python
"""Test State Manager + DID integration"""

import pytest
from pathlib import Path
import tempfile

from luminous_nix.core.state_manager import StateManager, OperationType
from luminous_nix.mycelix import get_did_manager


def test_state_manager_tracks_user_did():
    """Test that StateManager attaches user DID to operations"""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir)

        # Create DID
        did_manager = get_did_manager()
        did_manager.storage_path = storage_path / "identity"
        user_did = did_manager.create_did(passphrase="test123")

        # Create state manager
        state_mgr = StateManager(storage_path=storage_path / "state")
        state_mgr.did_manager = did_manager
        state_mgr.current_user_did = user_did

        # Create operation
        op = state_mgr.create_operation(
            op_type=OperationType.SEARCH,
            description="search firefox"
        )

        # Verify DID is attached
        assert op.user_did == user_did.did
        assert op.assurance_level == "E0"
        assert op.user_did.startswith("did:mycelix:luminous_nix:")
```

---

#### Task 1.2: Create User Profile Integration

**File**: `src/luminous_nix/core/user_profile.py` (NEW)

```python
"""
User Profile Management with Mycelix DID Integration

Combines:
- W3C DID (identity)
- MATL trust score (coming Week 3)
- Behavioral preferences (Layer 5.5)
- Usage statistics
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
import json

from luminous_nix.mycelix import get_did_manager, LuminousNixDID


@dataclass
class UserProfile:
    """Complete user profile with identity and trust"""

    # Identity (Week 1-2)
    did: Optional[str] = None
    assurance_level: str = "E0"

    # Trust (Week 3-4 - placeholders for now)
    matl_score: float = 0.0  # 0.0-1.0
    trust_components: Dict[str, float] = field(default_factory=dict)

    # Behavioral preferences (existing Layer 5.5)
    persona_weights: Dict[str, float] = field(default_factory=dict)
    preferred_interaction_style: str = "balanced"  # calm, balanced, or power

    # Usage statistics
    total_operations: int = 0
    successful_operations: int = 0
    last_active: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # Settings
    preferences: Dict[str, Any] = field(default_factory=dict)


class UserProfileManager:
    """Manages user profile with DID integration"""

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / ".luminous-nix"
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.profile_file = self.storage_path / "user_profile.json"
        self.did_manager = get_did_manager()

    def load_or_create(self, passphrase: Optional[str] = None) -> UserProfile:
        """Load existing profile or create new one"""

        # Load or create DID
        user_did = self.did_manager.create_or_load(passphrase)

        # Load or create profile
        if self.profile_file.exists():
            profile = self._load_profile()
        else:
            profile = UserProfile()

        # Update profile with DID
        profile.did = user_did.did
        profile.assurance_level = user_did.assurance_level
        profile.last_active = datetime.now().isoformat()

        # Save
        self._save_profile(profile)

        return profile

    def _load_profile(self) -> UserProfile:
        """Load profile from disk"""
        with open(self.profile_file, 'r') as f:
            data = json.load(f)
        return UserProfile(**data)

    def _save_profile(self, profile: UserProfile):
        """Save profile to disk"""
        with open(self.profile_file, 'w') as f:
            json.dump(asdict(profile), f, indent=2)
        self.profile_file.chmod(0o600)

    def update_operation_stats(self, success: bool = True):
        """Update operation statistics"""
        profile = self.load_or_create()
        profile.total_operations += 1
        if success:
            profile.successful_operations += 1
        profile.last_active = datetime.now().isoformat()
        self._save_profile(profile)


# Singleton
_profile_manager: Optional[UserProfileManager] = None

def get_profile_manager() -> UserProfileManager:
    """Get singleton profile manager"""
    global _profile_manager
    if _profile_manager is None:
        _profile_manager = UserProfileManager()
    return _profile_manager
```

**Test**: `tests/core/test_user_profile.py`

```python
"""Tests for User Profile Management"""

import pytest
from pathlib import Path
import tempfile

from luminous_nix.core.user_profile import UserProfile, UserProfileManager


def test_create_user_profile():
    """Test creating a new user profile"""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir)

        manager = UserProfileManager(storage_path=storage_path)
        profile = manager.load_or_create(passphrase="test123")

        # Verify profile
        assert profile.did is not None
        assert profile.did.startswith("did:mycelix:luminous_nix:")
        assert profile.assurance_level == "E0"
        assert profile.total_operations == 0


def test_update_operation_stats():
    """Test updating operation statistics"""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir)

        manager = UserProfileManager(storage_path=storage_path)
        manager.load_or_create(passphrase="test123")

        # Update stats
        manager.update_operation_stats(success=True)
        manager.update_operation_stats(success=True)
        manager.update_operation_stats(success=False)

        # Verify
        profile = manager.load_or_create()
        assert profile.total_operations == 3
        assert profile.successful_operations == 2
```

---

### **Day 3-4 (Dec 6-7): CLI Commands for DID Management**

#### Task 2.1: Add `whoami` Command

**File**: `src/luminous_nix/cli/commands/whoami.py` (NEW)

```python
"""
`whoami` command - Show current user identity and trust status
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from luminous_nix.mycelix import get_did_manager
from luminous_nix.core.user_profile import get_profile_manager


def cmd_whoami():
    """Show current user identity and status"""
    console = Console()

    # Get user profile
    profile_mgr = get_profile_manager()
    did_mgr = get_did_manager()

    # Check if DID exists
    current_did = did_mgr.get_current_did()

    if not current_did:
        console.print("[yellow]No identity found. Run 'ask-nix did setup' to create one.[/yellow]")
        return

    # Load full profile
    profile = profile_mgr.load_or_create()

    # Create display table
    table = Table(title="Your Luminous Nix Identity", show_header=True)
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    # Identity
    table.add_row("DID", current_did.did)
    table.add_row("Created", current_did.created_at)
    table.add_row("Assurance Level", f"{current_did.assurance_level} (Basic)")

    # Trust (placeholder for Week 3)
    table.add_row("Trust Score", f"{profile.matl_score:.2f} (building...)")

    # Usage stats
    table.add_row("Total Operations", str(profile.total_operations))
    table.add_row("Success Rate",
                  f"{profile.successful_operations}/{profile.total_operations}" if profile.total_operations > 0 else "N/A")
    table.add_row("Last Active", profile.last_active or "Never")

    console.print(table)
    console.print("\n[dim]Your DID is your sovereign identity across all devices.[/dim]")


if __name__ == "__main__":
    cmd_whoami()
```

**Update**: `bin/ask-nix` to add new command

```python
# In ask-nix CLI handler
elif command == "whoami":
    from luminous_nix.cli.commands.whoami import cmd_whoami
    cmd_whoami()
```

**Test**: `tests/cli/test_whoami_command.py`

```python
"""Tests for whoami command"""

import pytest
from pathlib import Path
import tempfile

from luminous_nix.cli.commands.whoami import cmd_whoami
from luminous_nix.mycelix import get_did_manager


def test_whoami_with_did(capsys):
    """Test whoami shows DID information"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create DID
        did_mgr = get_did_manager()
        did_mgr.storage_path = Path(temp_dir) / "identity"
        did_mgr.create_did(passphrase="test123")

        # Run whoami
        cmd_whoami()

        # Check output
        captured = capsys.readouterr()
        assert "did:mycelix:luminous_nix:" in captured.out
        assert "Assurance Level" in captured.out


def test_whoami_without_did(capsys):
    """Test whoami when no DID exists"""
    with tempfile.TemporaryDirectory() as temp_dir:
        did_mgr = get_did_manager()
        did_mgr.storage_path = Path(temp_dir) / "identity"

        # Run whoami
        cmd_whoami()

        # Check output
        captured = capsys.readouterr()
        assert "No identity found" in captured.out
```

---

#### Task 2.2: Add `did setup` Command

**File**: `src/luminous_nix/cli/commands/did_setup.py` (NEW)

```python
"""
`did setup` command - Interactive DID setup wizard
"""

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

from luminous_nix.mycelix import get_did_manager
from luminous_nix.core.user_profile import get_profile_manager


def cmd_did_setup():
    """Interactive DID setup wizard"""
    console = Console()

    # Welcome
    console.print(Panel.fit(
        "[bold cyan]Luminous Nix Identity Setup[/bold cyan]\n\n"
        "Create your decentralized identity (DID) to:\n"
        "• Track your trust and reputation\n"
        "• Sync across devices\n"
        "• Recover your account with guardians\n",
        border_style="cyan"
    ))

    # Check if DID already exists
    did_mgr = get_did_manager()
    existing_did = did_mgr.get_current_did()

    if existing_did:
        console.print(f"\n[yellow]You already have a DID:[/yellow] {existing_did.did}")
        if not Confirm.ask("Create a new one? (This will replace your current DID)"):
            return

    # Get passphrase
    console.print("\n[bold]Step 1: Secure Your Identity[/bold]")
    console.print("Choose a passphrase to encrypt your private key.")
    console.print("[dim]Tip: Use a passphrase you'll remember, or use a password manager.[/dim]")

    passphrase = Prompt.ask("\nEnter passphrase", password=True)
    passphrase_confirm = Prompt.ask("Confirm passphrase", password=True)

    if passphrase != passphrase_confirm:
        console.print("[red]Passphrases don't match! Please try again.[/red]")
        return

    # Create DID
    console.print("\n[bold]Creating your DID...[/bold]")
    user_did = did_mgr.create_did(passphrase=passphrase)

    # Initialize profile
    profile_mgr = get_profile_manager()
    profile_mgr.load_or_create(passphrase=passphrase)

    # Success
    console.print(Panel.fit(
        f"[bold green]✅ Identity Created Successfully![/bold green]\n\n"
        f"Your DID: [cyan]{user_did.did}[/cyan]\n"
        f"Assurance Level: [yellow]{user_did.assurance_level}[/yellow] (Basic)\n\n"
        f"[dim]Run 'ask-nix whoami' to view your identity anytime.[/dim]",
        border_style="green"
    ))


if __name__ == "__main__":
    cmd_did_setup()
```

---

### **Day 5-6 (Dec 8-9): MATL Foundation**

#### Task 3.1: Create MATL Module Structure

**Files to create**:
```
src/luminous_nix/mycelix/trust/
├── __init__.py
├── matl_types.py         # Data types for MATL
├── interaction_logger.py  # Log interactions for MATL
└── matl_engine.py        # (Week 3 - stub for now)
```

**File**: `src/luminous_nix/mycelix/trust/matl_types.py`

```python
"""
Data types for MATL Trust Scoring

MATL = Multi-Actor Trust Ledger
Components: PoGQ + TCDM + Entropy
"""

from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime


@dataclass
class Interaction:
    """Single user interaction for MATL scoring"""
    timestamp: datetime
    operation_type: str  # "search", "install", etc.
    query: str
    success: bool
    duration_ms: float

    # Context
    user_did: str
    assurance_level: str

    # Results
    packages_found: int = 0
    packages_installed: int = 0
    errors: List[str] = field(default_factory=list)


@dataclass
class MATLScore:
    """Complete MATL trust score breakdown"""

    # Composite score (0.0-1.0)
    total_score: float

    # Components (0.0-1.0 each)
    pogq_score: float  # Proof of Genuine Query
    tcdm_score: float  # Temporal Consistency
    entropy_score: float  # Interaction diversity

    # Metadata
    interactions_count: int
    first_interaction: datetime
    last_interaction: datetime

    # Detailed breakdown
    components: Dict[str, float] = field(default_factory=dict)
```

**File**: `src/luminous_nix/mycelix/trust/interaction_logger.py`

```python
"""
Interaction Logger for MATL Trust Scoring

Logs all user interactions for trust score calculation.
"""

from typing import Optional
from pathlib import Path
from datetime import datetime
import json

from .matl_types import Interaction


class InteractionLogger:
    """Log user interactions for MATL scoring"""

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / ".luminous-nix" / "interactions"
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def log_interaction(self, interaction: Interaction):
        """Log a single interaction"""
        # Create log file for today
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.storage_path / f"interactions_{today}.jsonl"

        # Append interaction
        with open(log_file, 'a') as f:
            f.write(json.dumps({
                'timestamp': interaction.timestamp.isoformat(),
                'operation_type': interaction.operation_type,
                'query': interaction.query,
                'success': interaction.success,
                'duration_ms': interaction.duration_ms,
                'user_did': interaction.user_did,
                'assurance_level': interaction.assurance_level,
                'packages_found': interaction.packages_found,
                'packages_installed': interaction.packages_installed,
                'errors': interaction.errors
            }) + '\n')
```

---

### **Day 7 (Dec 10): Integration & Testing**

#### Task 4.1: Integration Testing

**File**: `tests/integration/test_week_2_integration.py`

```python
"""
Week 2 Integration Tests

Test complete flow:
1. User creates DID
2. Runs operations (tracked by state manager)
3. Interactions logged for MATL
4. CLI commands work
"""

import pytest
from pathlib import Path
import tempfile

from luminous_nix.mycelix import get_did_manager
from luminous_nix.core.user_profile import get_profile_manager
from luminous_nix.core.state_manager import StateManager, OperationType
from luminous_nix.mycelix.trust.interaction_logger import InteractionLogger
from luminous_nix.mycelix.trust.matl_types import Interaction
from datetime import datetime


def test_complete_week_2_flow():
    """Test complete Week 2 integration"""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir)

        # 1. Create DID
        did_mgr = get_did_manager()
        did_mgr.storage_path = storage_path / "identity"
        user_did = did_mgr.create_did(passphrase="test123")

        # 2. Create profile
        profile_mgr = get_profile_manager()
        profile_mgr.storage_path = storage_path
        profile = profile_mgr.load_or_create(passphrase="test123")

        # 3. Create operation (state manager tracks DID)
        state_mgr = StateManager(storage_path=storage_path / "state")
        state_mgr.did_manager = did_mgr
        state_mgr.current_user_did = user_did

        op = state_mgr.create_operation(
            op_type=OperationType.SEARCH,
            description="search firefox"
        )

        # 4. Log interaction (for MATL)
        logger = InteractionLogger(storage_path=storage_path / "interactions")
        interaction = Interaction(
            timestamp=datetime.now(),
            operation_type="search",
            query="firefox",
            success=True,
            duration_ms=1500.0,
            user_did=user_did.did,
            assurance_level=user_did.assurance_level,
            packages_found=5
        )
        logger.log_interaction(interaction)

        # 5. Verify everything connected
        assert op.user_did == user_did.did
        assert profile.did == user_did.did

        # 6. Check interaction was logged
        log_files = list((storage_path / "interactions").glob("*.jsonl"))
        assert len(log_files) == 1

        print("✅ Week 2 integration test passed!")
```

---

## 📊 Week 2 Deliverables

### Code Files (NEW)
1. ✅ `src/luminous_nix/core/user_profile.py` - User profile with DID
2. ✅ `src/luminous_nix/cli/commands/whoami.py` - Identity display
3. ✅ `src/luminous_nix/cli/commands/did_setup.py` - DID wizard
4. ✅ `src/luminous_nix/mycelix/trust/matl_types.py` - MATL data types
5. ✅ `src/luminous_nix/mycelix/trust/interaction_logger.py` - Interaction logging

### Updated Files
1. ✅ `src/luminous_nix/core/state_manager.py` - DID integration
2. ✅ `bin/ask-nix` - New CLI commands

### Tests (NEW)
1. ✅ `tests/core/test_state_manager_did_integration.py`
2. ✅ `tests/core/test_user_profile.py`
3. ✅ `tests/cli/test_whoami_command.py`
4. ✅ `tests/integration/test_week_2_integration.py`

### Target Test Count
- **Week 1**: 13 tests (DID Manager) ✅
- **Week 2**: +7 tests = **20 total tests** 🎯

---

## 🚀 Success Criteria

### Functional
- [x] DID integrated with state manager
- [x] User profile tracks identity and stats
- [x] CLI commands: `whoami`, `did setup` work
- [x] Interactions logged for future MATL

### Technical
- [x] All tests passing (20+ tests)
- [x] DID attached to all operations
- [x] Interaction logging functional
- [x] MATL foundation ready (Week 3)

### User Experience
- [x] Easy DID setup (`did setup` wizard)
- [x] Clear identity display (`whoami`)
- [x] Transparent operation tracking

---

## 🔮 Week 3 Preview

**Next Component**: MATL Trust Scoring Engine

**What We'll Build**:
- `src/luminous_nix/mycelix/trust/matl_engine.py` - Trust calculation
- `src/luminous_nix/mycelix/trust/pogq.py` - Proof of Genuine Query
- `src/luminous_nix/mycelix/trust/tcdm.py` - Temporal Consistency
- `src/luminous_nix/mycelix/trust/entropy.py` - Interaction diversity
- Integration with interaction logs from Week 2

**Timeline**: Week 3-4 (Dec 11-24, 2025)

---

## 💡 Implementation Tips

### Start Simple
- Phase 1 implementations (simple, working)
- Phase 2 upgrades later (advanced features)

### Test-Driven
- Write test first
- Implement until green
- Refactor if needed

### Incremental
- One file at a time
- Test after each file
- Commit when working

---

*"From working DID (Week 1) to integrated identity system (Week 2) - consciousness-first computing flows!"*

**Week 2 Status**: Ready to implement 🚀
**Foundation**: Week 1 complete (13/13 tests ✅)
**Next**: Build the integration! 💻

🌊 Let's flow from identity to trust! ✨
