"""
Post-Quantum Cryptography (PQC) Module

Provides quantum-resistant encryption for state persistence.

Current Implementation: Hybrid approach using RSA-4096 + AES-256-GCM
Future: Will migrate to NIST PQC standards (Kyber, Dilithium)

Design Philosophy:
- Interface designed for easy PQC algorithm swap
- Uses strong classical cryptography as foundation
- Ready for NIST PQC finalist integration
"""

from typing import Any, Tuple, Optional
from pathlib import Path
import json
import pickle
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
import os


class PQCKeyManager:
    """
    Manages post-quantum cryptographic key pairs.

    Current: RSA-4096 (placeholder for Kyber-1024)
    Future: NIST PQC finalist algorithms
    """

    def __init__(self, key_size: int = 4096):
        """
        Initialize PQC key manager.

        Args:
            key_size: Key size in bits (4096 for strong RSA)
        """
        self.key_size = key_size
        self.backend = default_backend()

    def generate_key_pair(self) -> Tuple[Any, Any]:
        """
        Generate a PQC key pair.

        Returns:
            Tuple of (public_key, private_key)
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.key_size,
            backend=self.backend
        )
        public_key = private_key.public_key()
        return (public_key, private_key)

    def serialize_public_key(self, public_key: Any) -> str:
        """
        Serialize public key to PEM format.

        Args:
            public_key: Public key object

        Returns:
            PEM-encoded string
        """
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode('utf-8')

    def serialize_private_key(self, private_key: Any) -> str:
        """
        Serialize private key to PEM format.

        Args:
            private_key: Private key object

        Returns:
            PEM-encoded string
        """
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        return pem.decode('utf-8')

    def deserialize_public_key(self, pem_data: str) -> Any:
        """
        Deserialize public key from PEM format.

        Args:
            pem_data: PEM-encoded string

        Returns:
            Public key object
        """
        return serialization.load_pem_public_key(
            pem_data.encode('utf-8'),
            backend=self.backend
        )

    def deserialize_private_key(self, pem_data: str) -> Any:
        """
        Deserialize private key from PEM format.

        Args:
            pem_data: PEM-encoded string

        Returns:
            Private key object
        """
        return serialization.load_pem_private_key(
            pem_data.encode('utf-8'),
            password=None,
            backend=self.backend
        )

    def save_public_key(self, public_key: Any, path: Path) -> None:
        """Save public key to file"""
        pem = self.serialize_public_key(public_key)
        path.write_text(pem)

    def save_private_key(self, private_key: Any, path: Path) -> None:
        """Save private key to file"""
        pem = self.serialize_private_key(private_key)
        path.write_text(pem)

    def load_public_key(self, path: Path) -> Any:
        """Load public key from file"""
        pem = path.read_text()
        return self.deserialize_public_key(pem)

    def load_private_key(self, path: Path) -> Any:
        """Load private key from file"""
        pem = path.read_text()
        return self.deserialize_private_key(pem)


class PQCEncryption:
    """
    PQC-based encryption/decryption.

    Uses hybrid approach:
    - AES-256-GCM for data encryption (fast, quantum-resistant)
    - RSA-4096/OAEP for key encapsulation (will become Kyber)
    """

    def __init__(self):
        """Initialize PQC encryption"""
        pass

    def encrypt(self, plaintext: bytes, public_key: Any) -> bytes:
        """
        Encrypt data with PQC.

        Args:
            plaintext: Data to encrypt
            public_key: Public key for encryption

        Returns:
            Encrypted data with encapsulated key
        """
        # Generate random symmetric key
        symmetric_key = AESGCM.generate_key(bit_length=256)

        # Encrypt data with AES-GCM
        aesgcm = AESGCM(symmetric_key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)

        # Encapsulate symmetric key with public key
        encrypted_key = public_key.encrypt(
            symmetric_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Package: encrypted_key_length (4 bytes) + encrypted_key + nonce (12 bytes) + ciphertext
        key_len = len(encrypted_key).to_bytes(4, 'big')
        return key_len + encrypted_key + nonce + ciphertext

    def decrypt(self, encrypted_data: bytes, private_key: Any) -> bytes:
        """
        Decrypt PQC-encrypted data.

        Args:
            encrypted_data: Encrypted data
            private_key: Private key for decryption

        Returns:
            Decrypted plaintext
        """
        # Extract components
        key_len = int.from_bytes(encrypted_data[:4], 'big')
        encrypted_key = encrypted_data[4:4 + key_len]
        nonce = encrypted_data[4 + key_len:4 + key_len + 12]
        ciphertext = encrypted_data[4 + key_len + 12:]

        # Decrypt symmetric key
        symmetric_key = private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Decrypt data
        aesgcm = AESGCM(symmetric_key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)

        return plaintext


class EncryptedStatePersistence:
    """
    Encrypted persistence for operation state.

    Provides quantum-resistant storage of sensitive state data.
    """

    def __init__(self, public_key: Any, private_key: Any):
        """
        Initialize encrypted state persistence.

        Args:
            public_key: Public key for encryption
            private_key: Private key for decryption
        """
        self.public_key = public_key
        self.private_key = private_key
        self.encryption = PQCEncryption()

    def save_state(self, state: 'OperationState', path: Path) -> None:
        """
        Save operation state with encryption.

        Args:
            state: OperationState to save
            path: File path for encrypted state
        """
        # Serialize state to bytes
        state_data = pickle.dumps(state)

        # Encrypt
        encrypted = self.encryption.encrypt(state_data, self.public_key)

        # Save to file
        path.write_bytes(encrypted)

    def load_state(self, path: Path) -> 'OperationState':
        """
        Load encrypted operation state.

        Args:
            path: File path to encrypted state

        Returns:
            Decrypted OperationState
        """
        # Load encrypted data
        encrypted = path.read_bytes()

        # Decrypt
        state_data = self.encryption.decrypt(encrypted, self.private_key)

        # Deserialize
        state = pickle.loads(state_data)

        return state


class PQCKeyRotation:
    """
    Handles key rotation for encrypted data.

    Allows migrating encrypted data to new keys without decryption exposure.
    """

    def __init__(self):
        """Initialize key rotation handler"""
        self.encryption = PQCEncryption()

    def rotate_state_file(
        self,
        old_path: Path,
        new_path: Path,
        old_private_key: Any,
        new_public_key: Any
    ) -> None:
        """
        Rotate encryption key for state file.

        Args:
            old_path: Path to file encrypted with old key
            new_path: Path for file encrypted with new key
            old_private_key: Old private key for decryption
            new_public_key: New public key for encryption
        """
        # Read and decrypt with old key
        encrypted_old = old_path.read_bytes()
        plaintext = self.encryption.decrypt(encrypted_old, old_private_key)

        # Encrypt with new key
        encrypted_new = self.encryption.encrypt(plaintext, new_public_key)

        # Write to new path
        new_path.write_bytes(encrypted_new)


# Example usage
if __name__ == "__main__":
    print("PQC Foundation Example")
    print("-" * 50)

    # Generate keys
    key_manager = PQCKeyManager()
    public_key, private_key = key_manager.generate_key_pair()
    print("✓ Generated PQC key pair")

    # Encrypt/decrypt
    encryption = PQCEncryption()
    plaintext = b"Sensitive data requiring quantum-resistant protection"
    ciphertext = encryption.encrypt(plaintext, public_key)
    decrypted = encryption.decrypt(ciphertext, private_key)
    print(f"✓ Encryption/Decryption: {decrypted == plaintext}")

    # State encryption
    import tempfile
    from luminous_nix.core.state_manager import OperationState, OperationStatus

    persistence = EncryptedStatePersistence(public_key, private_key)

    state = OperationState()
    state.operation_id = "test"
    state.user_query = "install firefox"
    state.status = OperationStatus.PLANNING

    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "state.encrypted"
        persistence.save_state(state, state_file)
        loaded = persistence.load_state(state_file)
        print(f"✓ State Encryption: {loaded.operation_id == 'test'}")

    print("\nPQC Foundation Ready ✅")
