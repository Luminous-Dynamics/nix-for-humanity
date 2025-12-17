"""
W3C Decentralized Identity (DID) System for Luminous Nix

Provides sovereign identity with:
- did:mycelix:luminous_nix:{hash} format
- Cross-device synchronization (Holochain DHT)
- Social recovery (Shamir Secret Sharing, 5 guardians, 3 threshold)
- E0-E4 graduated assurance levels
"""

from .did_manager import DIDManager, LuminousNixDID, get_did_manager

__all__ = ["DIDManager", "LuminousNixDID", "get_did_manager"]
