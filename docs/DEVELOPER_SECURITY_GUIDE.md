# 🔐 Developer Security Architecture Guide

**Version**: v0.4.0-dev
**Last Updated**: December 2, 2025
**Audience**: Developers, security engineers, contributors

---

## 🎯 Overview

This guide provides technical details of Luminous Nix's security architecture for developers who need to:
- Understand the security implementation
- Contribute security-related code
- Extend security features via plugins
- Audit the security design
- Integrate with external security systems

---

## 📐 Architecture Overview

### Three-Layer Security Model

```
┌─────────────────────────────────────────────────────────┐
│                  Application Layer                       │
│  (CLI, TUI, API - User-facing components)               │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                 Security Layer (This Guide)              │
├──────────────────┬──────────────────┬───────────────────┤
│   Layer 3:       │   Layer 2:       │   Layer 1:        │
│   Signatures     │   Encryption     │   Storage         │
│   (Week 10)      │   (Week 9-10)    │   (StateManager)  │
└──────────────────┴──────────────────┴───────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    Storage Layer                         │
│  (Filesystem, Database - Encrypted data at rest)        │
└─────────────────────────────────────────────────────────┘
```

### Component Interaction

```python
# High-level flow
User Request
    → StateManager.save_state(operation)
        → _sign_operation(operation)          # Layer 3: Sign
            → Creates canonical JSON
            → RSA-PSS signature with SHA-256
        → _save_encrypted(operation)          # Layer 2: Encrypt
            → PQCEncryption.encrypt(data, key)
                → Kyber-1024 KEM
                → AES-256-GCM for data
        → Write to disk                       # Layer 1: Store
            → operation_id.encrypted
```

---

## 🔒 Layer 1: Storage (StateManager)

### Core Module

**File**: `src/luminous_nix/core/state_manager.py`

### Key Classes

#### OperationState

```python
@dataclass
class OperationState:
    """
    Represents a single NixOS operation with full security metadata.

    Security Fields:
    - signature: Cryptographic signature (bytes)
    - signature_algorithm: Algorithm used (e.g., 'RSA-4096')
    - operation_type: Type of operation for audit logging
    """
    # Identity
    operation_id: str
    parent_id: Optional[str] = None
    operation_type: OperationType = OperationType.CUSTOM

    # Core data
    user_query: str = ""
    status: OperationStatus = OperationStatus.CREATED
    result: Optional[Any] = None
    error: Optional[str] = None

    # Security (Week 10: Operation Signatures)
    signature: Optional[bytes] = None
    signature_algorithm: Optional[str] = None

    # Metadata
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
```

#### StateManager

```python
@dataclass
class StateManager:
    """
    Manages operation state with optional encryption and signing.

    Security Features:
    - AES-256-GCM encryption with Kyber-1024 KEM
    - RSA-PSS signatures with SHA-256
    - Automatic key management
    - Backward compatibility with unsigned/unencrypted data
    """
    storage_dir: Path
    encryption_enabled: bool = True   # Week 9-10: PQC Integration
    signing_enabled: bool = False     # Week 10: Operation Signatures

    # Private fields
    _encryption_key: Optional[Any] = None
    _signing_key: Optional[Any] = None
```

### API Reference

#### save_state()

```python
def save_state(self, state: OperationState) -> bool:
    """
    Save operation with optional encryption and signing.

    Security Flow:
    1. If signing_enabled: Sign operation → adds signature field
    2. If encryption_enabled: Encrypt entire operation → .encrypted file
    3. Else: Save as JSON → .json file

    Args:
        state: Operation to save

    Returns:
        True on success, False on failure

    Raises:
        No exceptions - returns False on error
    """
```

#### load_state()

```python
def load_state(self, operation_id: str) -> Optional[OperationState]:
    """
    Load operation with automatic encrypted/unencrypted detection.

    Security Flow:
    1. Check cache
    2. Try encrypted format (.encrypted) → decrypt if encryption_enabled
    3. Try unencrypted format (.json)
    4. If signing_enabled: Verify signature
    5. Return operation or None

    Args:
        operation_id: ID of operation to load

    Returns:
        OperationState or None if not found or verification failed

    Security Note:
        - Tampered operations return None (signature verification failure)
        - Logs warnings for unsigned operations when signing_enabled
    """
```

---

## 🔐 Layer 2: Encryption (PQC)

### Core Module

**File**: `src/luminous_nix/security/pqc.py`

### Encryption Architecture

```
┌──────────────────────────────────────────────────┐
│           PQC Encryption Pipeline                │
├──────────────────────────────────────────────────┤
│                                                  │
│  1. Key Encapsulation Mechanism (KEM)          │
│     ┌────────────────────────────────────┐     │
│     │  Kyber-1024 (NIST Standard)        │     │
│     │  • Public key: 1568 bytes          │     │
│     │  • Private key: 3168 bytes         │     │
│     │  • Ciphertext: 1568 bytes          │     │
│     │  • Shared secret: 32 bytes         │     │
│     └────────────────────────────────────┘     │
│                    ↓                             │
│  2. Symmetric Encryption                        │
│     ┌────────────────────────────────────┐     │
│     │  AES-256-GCM                       │     │
│     │  • Key: Derived from shared secret │     │
│     │  • Nonce: 12 bytes random          │     │
│     │  • Tag: 16 bytes (authentication)  │     │
│     └────────────────────────────────────┘     │
│                    ↓                             │
│  3. Format                                      │
│     ┌────────────────────────────────────┐     │
│     │  nonce(12) + kem_ct(1568) +        │     │
│     │  encrypted_data + tag(16)          │     │
│     └────────────────────────────────────┘     │
└──────────────────────────────────────────────────┘
```

### Key Classes

#### PQCKeyManager

```python
class PQCKeyManager:
    """
    Manages post-quantum cryptographic keys.

    Features:
    - Kyber-1024 key generation
    - PEM format serialization
    - Secure key storage
    - Key rotation support
    """

    def generate_key_pair(self) -> Tuple[bytes, bytes]:
        """
        Generate Kyber-1024 key pair.

        Returns:
            (public_key, private_key) as PEM-encoded bytes

        Security Note:
            Uses oqs.KeyEncapsulation("Kyber1024") from liboqs
            NIST standardized, quantum-resistant
        """

    def save_private_key(self, private_key: bytes, path: Path) -> None:
        """
        Save private key with secure permissions.

        Security:
            - File permissions: 0o600 (owner read/write only)
            - Parent directory: 0o700 (owner only)
            - Atomic write (temp file + rename)
        """
```

#### PQCEncryption

```python
class PQCEncryption:
    """
    Handles encryption/decryption with post-quantum algorithms.

    Algorithm: Kyber-1024 (KEM) + AES-256-GCM
    """

    def encrypt(self, data: bytes, public_key: bytes) -> bytes:
        """
        Encrypt data using hybrid PQC scheme.

        Process:
        1. Load public key
        2. Encapsulate shared secret using Kyber-1024
        3. Derive AES key from shared secret
        4. Encrypt data with AES-256-GCM
        5. Return: nonce + kem_ciphertext + encrypted_data + tag

        Args:
            data: Plaintext to encrypt
            public_key: PEM-encoded Kyber-1024 public key

        Returns:
            Encrypted data (format described above)
        """

    def decrypt(self, ciphertext: bytes, private_key: bytes) -> bytes:
        """
        Decrypt data using hybrid PQC scheme.

        Process:
        1. Parse ciphertext format
        2. Decapsulate shared secret using private key
        3. Derive AES key from shared secret
        4. Decrypt data with AES-256-GCM
        5. Verify authentication tag
        6. Return plaintext

        Args:
            ciphertext: Encrypted data
            private_key: PEM-encoded Kyber-1024 private key

        Returns:
            Decrypted plaintext

        Raises:
            DecryptionError: If decryption fails (wrong key, corrupted data)
        """
```

### Encryption Format Specification

```
Encrypted File Format:
┌────────────┬─────────────┬──────────────┬──────────┐
│  Nonce     │  KEM CT     │  Encrypted   │  Auth    │
│  12 bytes  │  1568 bytes │  Variable    │  16 bytes│
└────────────┴─────────────┴──────────────┴──────────┘

Total size = 12 + 1568 + len(plaintext) + 16
           = 1596 + len(plaintext) bytes

Example:
- 100 byte operation → 1696 byte encrypted file
- 1KB operation → 2620 byte encrypted file
- 10KB operation → 11620 byte encrypted file
```

---

## ✍️ Layer 3: Signatures (Integrity)

### Signature Architecture

```
┌──────────────────────────────────────────────────┐
│         Operation Signing Pipeline               │
├──────────────────────────────────────────────────┤
│                                                  │
│  1. Canonical Representation                    │
│     ┌────────────────────────────────────┐     │
│     │  Create deterministic JSON         │     │
│     │  • Sorted keys                     │     │
│     │  • UTF-8 encoding                  │     │
│     │  • No whitespace variations        │     │
│     └────────────────────────────────────┘     │
│                    ↓                             │
│  2. Hash                                        │
│     ┌────────────────────────────────────┐     │
│     │  SHA-256                           │     │
│     │  • 256-bit digest                  │     │
│     │  • Collision resistant             │     │
│     └────────────────────────────────────┘     │
│                    ↓                             │
│  3. Sign                                        │
│     ┌────────────────────────────────────┐     │
│     │  RSA-PSS (4096-bit key)            │     │
│     │  • PSS padding with MGF1           │     │
│     │  • MAX_LENGTH salt                 │     │
│     │  • Signature: 512 bytes            │     │
│     └────────────────────────────────────┘     │
└──────────────────────────────────────────────────┘
```

### Implementation

#### _sign_operation()

```python
def _sign_operation(self, state: OperationState) -> bytes:
    """
    Sign operation state for integrity verification.

    Canonical Data Included:
    - operation_id
    - operation_type
    - user_query
    - status
    - created_at
    - result (if present)

    Algorithm: RSA-PSS with SHA-256
    - Key size: 4096 bits
    - Padding: PSS with MGF1(SHA-256)
    - Salt length: MAX_LENGTH

    Returns:
        512-byte signature

    Security Properties:
    - Deterministic: Same operation → same signature (given same key)
    - Tamper-evident: Any modification invalidates signature
    - Non-repudiation: Only private key holder can create valid signature
    """
    # Create canonical representation
    canonical_data = {
        'operation_id': state.operation_id,
        'operation_type': state.operation_type.value,
        'user_query': state.user_query,
        'status': state.status.value,
        'created_at': state.created_at.isoformat() if state.created_at else None,
    }

    if state.result is not None:
        canonical_data['result'] = str(state.result)

    # Serialize to canonical JSON (sorted keys for determinism)
    canonical_json = json.dumps(canonical_data, sort_keys=True).encode('utf-8')

    # Sign using RSA-PSS
    private_key = load_pem_private_key(self._signing_key, password=None)

    signature = private_key.sign(
        canonical_json,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    return signature
```

#### _verify_signature()

```python
def _verify_signature(self, state: OperationState) -> bool:
    """
    Verify operation signature.

    Process:
    1. Recreate canonical representation (same as signing)
    2. Load public key (derived from private key)
    3. Verify signature using RSA-PSS

    Returns:
        True if signature valid, False otherwise

    Security Note:
        - Invalid signatures cause operation to be rejected
        - Missing signatures logged as warning when signing_enabled
        - Unsigned operations allowed when signing_enabled=False
    """
```

### Canonical Representation Example

```python
# Example operation
state = OperationState(
    operation_id="install_firefox",
    operation_type=OperationType.INSTALL,
    user_query="install firefox",
    status=OperationStatus.COMPLETED,
    created_at=datetime(2025, 12, 2, 14, 30),
    result="Firefox installed successfully"
)

# Canonical JSON (what gets signed)
{
  "created_at": "2025-12-02T14:30:00",
  "operation_id": "install_firefox",
  "operation_type": "install",
  "result": "Firefox installed successfully",
  "status": "completed",
  "user_query": "install firefox"
}

# Note: Alphabetically sorted keys for determinism
```

---

## 🔌 Extension Points

### Custom Encryption Providers

```python
from abc import ABC, abstractmethod

class CryptoProvider(ABC):
    """Interface for custom encryption providers"""

    @abstractmethod
    def encrypt(self, data: bytes, key: bytes) -> bytes:
        """Encrypt data"""
        pass

    @abstractmethod
    def decrypt(self, ciphertext: bytes, key: bytes) -> bytes:
        """Decrypt data"""
        pass

# Example: Custom provider using different algorithm
class CustomPQCProvider(CryptoProvider):
    def encrypt(self, data: bytes, key: bytes) -> bytes:
        # Use Dilithium instead of Kyber
        # Or hybrid RSA + Kyber
        # Or hardware security module (HSM)
        pass
```

### Custom Signature Algorithms

```python
# Future: Support for Dilithium signatures
class DilithiumSignatureProvider:
    """Post-quantum signature scheme"""

    def sign(self, data: bytes, private_key: bytes) -> bytes:
        """Sign using Dilithium-3"""
        with oqs.Signature("Dilithium3") as sig:
            signature = sig.sign(data)
        return signature

    def verify(self, data: bytes, signature: bytes, public_key: bytes) -> bool:
        """Verify Dilithium signature"""
        with oqs.Signature("Dilithium3") as sig:
            return sig.verify(data, signature, public_key)
```

---

## 🔐 Security Considerations

### Threat Model

**Protects Against**:
1. **Disk Theft** - Data encrypted at rest
2. **File System Access** - Can't read encrypted files without key
3. **Data Tampering** - Signatures detect modifications
4. **Quantum Attacks** - PQC algorithms resistant
5. **Replay Attacks** - Timestamps in signatures

**Does NOT Protect Against**:
1. **Memory Dumps** - Data decrypted in RAM during use
2. **Key Compromise** - If private keys stolen, security lost
3. **Side-Channel Attacks** - Timing attacks, power analysis
4. **Physical Access** - Recommend full disk encryption separately
5. **Malicious Code Execution** - If attacker can run code as user

### Key Management Best Practices

```python
# ✅ GOOD: Let StateManager manage keys
manager = StateManager(
    storage_dir=storage_dir,
    encryption_enabled=True,
    signing_enabled=True
)

# ❌ BAD: Managing keys manually
key_manager = PQCKeyManager()
pub, priv = key_manager.generate_key_pair()
# Now responsible for secure storage, rotation, backup
```

### Secure Key Storage

```python
# Default key locations
/var/lib/luminous-nix/keys/
├── encryption.pem         # PQC encryption private key (0600)
├── encryption.pub         # PQC encryption public key (0644)
├── signing.pem            # RSA signing private key (0600)
└── archive/               # Rotated keys (0700)
    ├── encryption_2025-12-01.pem
    └── signing_2025-12-01.pem

# Permissions critical:
# - Private keys: 0600 (owner read/write only)
# - Public keys: 0644 (world readable, owner writable)
# - Key directory: 0700 (owner only)
```

---

## 🧪 Testing

### Unit Tests

```python
# Example unit test for encryption
def test_encrypt_decrypt_roundtrip():
    """Test that encrypt→decrypt returns original data"""
    pqc = PQCEncryption()
    key_manager = PQCKeyManager()

    # Generate keys
    public_key, private_key = key_manager.generate_key_pair()

    # Test data
    original = b"Sensitive operation data"

    # Encrypt
    encrypted = pqc.encrypt(original, public_key)

    # Verify encrypted is different
    assert encrypted != original

    # Decrypt
    decrypted = pqc.decrypt(encrypted, private_key)

    # Verify matches original
    assert decrypted == original
```

### Integration Tests

```python
# Example integration test
def test_full_security_pipeline(tmp_path):
    """Test encryption + signing together"""
    manager = StateManager(
        storage_dir=tmp_path,
        encryption_enabled=True,
        signing_enabled=True
    )

    # Create operation
    state = OperationState(
        operation_id="test_op",
        user_query="install firefox"
    )

    # Save (encrypts + signs)
    manager.save_state(state)

    # Verify file is encrypted
    encrypted_file = tmp_path / "test_op.encrypted"
    assert encrypted_file.exists()
    assert b"install firefox" not in encrypted_file.read_bytes()

    # Load (decrypts + verifies)
    loaded = manager.load_state("test_op")
    assert loaded is not None
    assert loaded.user_query == "install firefox"
    assert loaded.signature is not None
```

### Performance Tests

```python
def test_encryption_performance(tmp_path, benchmark):
    """Benchmark encryption performance"""
    manager = StateManager(
        storage_dir=tmp_path,
        encryption_enabled=True
    )

    state = OperationState(
        operation_id="perf_test",
        user_query="test"
    )

    # Benchmark save (includes encryption)
    result = benchmark(manager.save_state, state)

    # Assert performance target
    assert benchmark.stats['mean'] < 1.0  # <1s average
```

---

## 📊 Performance Optimization

### Caching Strategies

```python
class StateManager:
    # In-memory cache for frequently accessed operations
    _cache: Dict[str, OperationState] = field(default_factory=dict)

    def load_state(self, operation_id: str) -> Optional[OperationState]:
        # Check cache first (avoids decrypt overhead)
        if operation_id in self._cache:
            return self._cache[operation_id]

        # Load and decrypt
        state = self._load_encrypted(operation_id)

        # Cache for future access
        if state:
            self._cache[operation_id] = state

        return state
```

### Batch Operations

```python
def save_states_batch(self, states: List[OperationState]) -> List[bool]:
    """
    Save multiple operations efficiently.

    Optimization: Single key initialization for all operations
    """
    results = []

    # Initialize encryption once
    if self.encryption_enabled and not self._encryption_key:
        self._init_encryption()

    # Process all operations
    for state in states:
        results.append(self.save_state(state))

    return results
```

---

## 🔄 Migration Path to Future Algorithms

### Dilithium Signatures (Future)

```python
# Current: RSA-4096 signatures
state.signature_algorithm = "RSA-4096"

# Future: Dilithium-3 (NIST PQC signature standard)
state.signature_algorithm = "Dilithium-3"

# Transition: Hybrid (both RSA + Dilithium)
state.signature_algorithm = "Hybrid-RSA4096-Dilithium3"
state.signature = rsa_sig + dilithium_sig
```

### Algorithm Versioning

```python
# Operation state tracks algorithm used
class OperationState:
    signature_algorithm: Optional[str] = None  # "RSA-4096", "Dilithium-3", etc.
    encryption_algorithm: Optional[str] = None  # "Kyber-1024", "Hybrid-RSA-Kyber"

# Migration logic
def verify_signature(self, state: OperationState) -> bool:
    if state.signature_algorithm == "RSA-4096":
        return self._verify_rsa_pss(state)
    elif state.signature_algorithm == "Dilithium-3":
        return self._verify_dilithium(state)
    elif state.signature_algorithm.startswith("Hybrid-"):
        return self._verify_hybrid(state)
    else:
        raise ValueError(f"Unknown algorithm: {state.signature_algorithm}")
```

---

## 🚨 Security Audit Checklist

### Code Review
- [ ] All private keys have 0600 permissions
- [ ] No hardcoded keys or secrets
- [ ] All cryptographic operations use constant-time comparisons
- [ ] Error messages don't leak sensitive information
- [ ] Random number generation uses cryptographically secure RNG

### Cryptographic Implementation
- [ ] Using NIST-standardized algorithms (Kyber-1024, SHA-256)
- [ ] Proper padding schemes (PSS for RSA)
- [ ] Correct parameter sizes (4096-bit RSA, 256-bit AES)
- [ ] Authenticated encryption (AES-GCM, not just AES-CBC)
- [ ] Fresh nonces/IVs for every encryption

### Key Management
- [ ] Keys generated with sufficient entropy
- [ ] Private keys never logged or exposed
- [ ] Key rotation mechanism implemented
- [ ] Archived keys properly secured
- [ ] Key backup procedures documented

---

## 📚 References

### Standards
- **NIST FIPS 203**: Kyber (Module-Lattice-Based Key-Encapsulation Mechanism)
- **NIST FIPS 180-4**: SHA-256 (Secure Hash Standard)
- **RFC 8017**: RSA-PSS (PKCS #1 v2.2)
- **NIST SP 800-38D**: AES-GCM

### Libraries
- **liboqs**: Open Quantum Safe library (Kyber implementation)
- **cryptography**: Python cryptographic library (RSA, AES, SHA-256)

### Further Reading
- [Post-Quantum Cryptography Overview](https://csrc.nist.gov/projects/post-quantum-cryptography)
- [Kyber Algorithm Specification](https://pq-crystals.org/kyber/)
- [RSA-PSS Best Practices](https://datatracker.ietf.org/doc/html/rfc8017)

---

## 🆘 Support

### Reporting Security Issues

**DO NOT** open public GitHub issues for security vulnerabilities.

**Instead**:
1. Email: security@luminousdynamics.org
2. Use PGP encryption (key available on website)
3. Include:
   - Detailed description
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Getting Help

- **Questions**: GitHub Discussions
- **Bugs**: GitHub Issues (non-security)
- **Contributing**: See `CONTRIBUTING.md`

---

*Last updated: December 2, 2025*
*Version: v0.4.0-dev*
*Security Architecture: Production Ready*
