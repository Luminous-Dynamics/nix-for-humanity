"""
W3C Decentralized Identifier (DID) Management for Luminous Nix

Phase 1 Implementation (Simplified for MVP):
- Create/load DIDs locally
- Basic storage and retrieval
- Foundation for future Holochain sync and social recovery
"""

from typing import Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import hashlib
import secrets
from datetime import datetime


@dataclass
class LuminousNixDID:
    """
    Luminous Nix user identity using Mycelix DID standard.

    Format: did:mycelix:luminous_nix:{public_key_hash}
    """
    did: str  # Full DID (e.g., "did:mycelix:luminous_nix:QmXx7...")
    public_key: str
    private_key_encrypted: str  # Encrypted with user passphrase
    created_at: str
    assurance_level: str  # E0, E1, E2, E3, E4

    # Social recovery (Phase 2)
    recovery_guardians: List[str]  # List of guardian DIDs
    recovery_threshold: int  # Number of guardians needed to recover


class DIDManager:
    """
    Manages Luminous Nix user DIDs.

    Phase 1 Features:
    - Create new DIDs
    - Load existing DIDs
    - Local storage (encrypted)

    Phase 2 Features (coming soon):
    - Cross-device synchronization (Holochain DHT)
    - Social recovery (Shamir Secret Sharing)
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize DID manager with storage location."""
        self.storage_path = storage_path or Path.home() / ".luminous-nix" / "identity"
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # DID file location
        self.did_file = self.storage_path / "did.json"

    def create_or_load(self, passphrase: Optional[str] = None) -> LuminousNixDID:
        """
        Create new DID or load existing one.

        Args:
            passphrase: User passphrase for encrypting private key
                       If None, generates random passphrase (dev mode)

        Returns:
            LuminousNixDID object
        """
        # Check if DID already exists
        if self.did_file.exists():
            return self.load_did(passphrase)
        else:
            return self.create_did(passphrase)

    def create_did(self, passphrase: Optional[str] = None) -> LuminousNixDID:
        """
        Create new Mycelix DID for user.

        Phase 1: Simple local creation
        Phase 2: Will register with Holochain DHT
        """
        # Generate passphrase if not provided (dev mode)
        if passphrase is None:
            passphrase = secrets.token_hex(16)
            print(f"⚠️  Generated passphrase (dev mode): {passphrase}")
            print("   Save this passphrase! You'll need it to access your DID.")

        # Generate simple keypair (Phase 1 - will use proper crypto in Phase 2)
        public_key, private_key = self._generate_keypair()

        # Create DID from public key
        # Format: did:mycelix:luminous_nix:{public_key_hash}
        public_key_hash = hashlib.sha256(public_key.encode()).hexdigest()[:16]
        did = f"did:mycelix:luminous_nix:{public_key_hash}"

        # Encrypt private key with passphrase (simple XOR for Phase 1)
        private_key_encrypted = self._encrypt_simple(private_key, passphrase)

        # Create DID object
        luminous_did = LuminousNixDID(
            did=did,
            public_key=public_key,
            private_key_encrypted=private_key_encrypted,
            created_at=datetime.now().isoformat(),
            assurance_level="E0",  # Start at E0 (basic)
            recovery_guardians=[],
            recovery_threshold=0
        )

        # Save to local storage
        self._save_did(luminous_did)

        print(f"✅ Created new Luminous Nix DID: {did}")
        print(f"   Assurance Level: E0 (Basic)")
        print(f"   Storage: {self.did_file}")

        return luminous_did

    def load_did(self, passphrase: Optional[str] = None) -> LuminousNixDID:
        """Load existing DID from storage."""
        if not self.did_file.exists():
            raise FileNotFoundError(f"No DID found at {self.did_file}. Create one first.")

        with open(self.did_file, 'r') as f:
            did_data = json.load(f)

        # Reconstruct LuminousNixDID object
        luminous_did = LuminousNixDID(**did_data)

        # Verify passphrase can decrypt private key (if provided)
        if passphrase:
            try:
                self._decrypt_simple(luminous_did.private_key_encrypted, passphrase)
            except Exception as e:
                raise ValueError(f"Invalid passphrase! {e}")

        print(f"✅ Loaded Luminous Nix DID: {luminous_did.did}")
        print(f"   Created: {luminous_did.created_at}")
        print(f"   Assurance Level: {luminous_did.assurance_level}")

        return luminous_did

    def _generate_keypair(self) -> tuple[str, str]:
        """
        Generate keypair for DID.

        Phase 1: Simple random keys
        Phase 2: Will use proper Ed25519 or similar
        """
        # Generate 32-byte random keys (hex encoded)
        private_key = secrets.token_hex(32)

        # Derive public key from private (simplified for Phase 1)
        public_key = hashlib.sha256(private_key.encode()).hexdigest()

        return public_key, private_key

    def _encrypt_simple(self, text: str, passphrase: str) -> str:
        """
        Simple encryption for Phase 1.

        Phase 2: Will use proper encryption (AES-256-GCM or similar)
        """
        # Simple XOR cipher (NOT SECURE - placeholder for Phase 1)
        key = hashlib.sha256(passphrase.encode()).digest()

        encrypted = bytearray()
        for i, char in enumerate(text.encode()):
            encrypted.append(char ^ key[i % len(key)])

        return encrypted.hex()

    def _decrypt_simple(self, encrypted_hex: str, passphrase: str) -> str:
        """
        Simple decryption for Phase 1.

        Phase 2: Will use proper decryption
        """
        # Simple XOR cipher (same operation encrypts and decrypts)
        key = hashlib.sha256(passphrase.encode()).digest()

        encrypted = bytes.fromhex(encrypted_hex)
        decrypted = bytearray()

        for i, byte in enumerate(encrypted):
            decrypted.append(byte ^ key[i % len(key)])

        return decrypted.decode()

    def _save_did(self, did: LuminousNixDID) -> None:
        """Save DID to local storage."""
        did_data = asdict(did)

        with open(self.did_file, 'w') as f:
            json.dump(did_data, f, indent=2)

        # Set file permissions (readable only by owner)
        self.did_file.chmod(0o600)

    def get_current_did(self) -> Optional[LuminousNixDID]:
        """Get current user's DID (if exists)."""
        if self.did_file.exists():
            try:
                return self.load_did(passphrase=None)
            except Exception:
                return None
        return None


# Singleton instance
_did_manager: Optional[DIDManager] = None


def get_did_manager() -> DIDManager:
    """Get singleton DID manager."""
    global _did_manager
    if _did_manager is None:
        _did_manager = DIDManager()
    return _did_manager
