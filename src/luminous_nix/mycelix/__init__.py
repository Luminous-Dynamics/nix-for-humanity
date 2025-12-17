"""
Mycelix Protocol Integration for Luminous Nix

Provides:
- W3C Decentralized Identity (DIDs)
- MATL Trust Scoring (45% Byzantine resistance)
- Epistemic Cube Classification (E/N/M)
- Zero-TrustML Credits (Holochain)
- Sophia Intelligence (9-layer consciousness)

Layer 7: Collective Intelligence
"""

from .identity import get_did_manager, DIDManager, LuminousNixDID
# from .trust import get_matl_engine, MATLEngine, MATLScore  # Coming in Week 3
# from .epistemic import get_epistemic_classifier  # Coming in Week 5
# from .credits import get_wallet  # Coming in Week 7

# Sophia Intelligence System
from .sophia_cli_integration import (
    get_sophia_cli_assistant,
    enable_sophia_for_cli,
    SophiaCLIAssistant
)

# Sophia Phase 4: Multi-Agent Orchestration
from .orchestration import (
    MetaSophia,
    TaskRouter,
    AgentRegistry,
    AgentMessage,
    MessageType,
    AgentProfile,
    OrchestrationContext,
    ConsensusResponse,
)

__version__ = "0.1.0-alpha"
__all__ = [
    "get_did_manager",
    "DIDManager",
    "LuminousNixDID",
    "get_sophia_cli_assistant",
    "enable_sophia_for_cli",
    "SophiaCLIAssistant",
    # Orchestration
    "MetaSophia",
    "TaskRouter",
    "AgentRegistry",
    "AgentMessage",
    "MessageType",
    "AgentProfile",
    "OrchestrationContext",
    "ConsensusResponse",
]
