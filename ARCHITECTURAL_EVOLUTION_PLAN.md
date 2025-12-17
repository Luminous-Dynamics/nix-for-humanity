# Architectural Evolution Plan

**Created**: December 2, 2025
**Purpose**: Guide for improving modularity, adding PQC support, and continuous evolution
**Status**: Strategic roadmap

---

## Executive Summary

This document outlines the strategic plan for evolving the Luminous Nix foundation to support:
1. **Enhanced Modularity** - Plugin architecture and extension points
2. **Post-Quantum Cryptography (PQC)** - Future-proof security
3. **Continuous Improvement** - Best practices for long-term evolution

---

## Part 1: Enhanced Modularity

### Current Modularity Assessment

**Strengths:**
- ✅ Clean separation of concerns (ExecutionPlan, StateManager, ErrorRecovery)
- ✅ Integration layers isolate systems
- ✅ Dependency injection pattern used throughout
- ✅ Each system independently testable

**Areas for Improvement:**
- ⚠️ Recovery strategies are hardcoded
- ⚠️ Step handlers are custom functions (no standard interface)
- ⚠️ Persistence backend is fixed (SQLite + JSON)
- ⚠️ Error classifiers use fixed patterns
- ⚠️ No plugin system for extensions

### Proposed Modular Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Plugin System                        │
│  - Discovery: Auto-load from plugins/ directory        │
│  - Registry: Central plugin registration               │
│  - Lifecycle: Init → Enable → Disable → Cleanup        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                 Extension Points                        │
├─────────────────────┬──────────────────┬────────────────┤
│  Step Handlers      │ Recovery         │ Persistence    │
│  - NixPackage       │ Strategies       │ Backends       │
│  - SystemRebuild    │ - NetworkRetry   │ - SQLite       │
│  - ConfigGen        │ - ResourceClean  │ - PostgreSQL   │
│  - Custom...        │ - Custom...      │ - Redis        │
│                     │                  │ - Custom...    │
├─────────────────────┼──────────────────┼────────────────┤
│  Error Classifiers  │ State Layers     │ Crypto         │
│  - PatternBased     │ - Semantic       │ Providers      │
│  - MLBased          │ - Context        │ - OpenSSL      │
│  - CustomRules      │ - Custom...      │ - liboqs (PQC) │
│  - Custom...        │                  │ - Custom...    │
└─────────────────────┴──────────────────┴────────────────┘
```

### Implementation Phases

#### Phase 1: Plugin System Foundation (Week 5)

**Goal**: Create plugin infrastructure

**Tasks:**
1. Create `PluginRegistry` for plugin management
2. Define `Plugin` base class with lifecycle methods
3. Implement plugin discovery (scan `plugins/` directory)
4. Add plugin loading/unloading
5. Create plugin versioning and dependency checking

**Example Implementation:**

```python
# src/luminous_nix/core/plugin_system.py

from typing import Dict, List, Type, Optional
from abc import ABC, abstractmethod
import importlib
import inspect
from pathlib import Path

class Plugin(ABC):
    """Base class for all plugins"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version (semver)"""
        pass

    @property
    def dependencies(self) -> List[str]:
        """List of required plugin names"""
        return []

    def on_load(self) -> None:
        """Called when plugin is loaded"""
        pass

    def on_enable(self) -> None:
        """Called when plugin is enabled"""
        pass

    def on_disable(self) -> None:
        """Called when plugin is disabled"""
        pass

    def on_unload(self) -> None:
        """Called when plugin is unloaded"""
        pass


class PluginRegistry:
    """Central registry for plugins"""

    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.enabled_plugins: set = set()

    def discover_plugins(self, plugin_dir: Path) -> List[Type[Plugin]]:
        """
        Discover plugins in directory.

        Looks for classes inheriting from Plugin in .py files.
        """
        discovered = []

        for file_path in plugin_dir.glob("**/*.py"):
            if file_path.name.startswith("_"):
                continue

            # Import module
            module_name = file_path.stem
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find Plugin classes
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, Plugin) and obj != Plugin:
                    discovered.append(obj)

        return discovered

    def register(self, plugin: Plugin) -> None:
        """Register a plugin"""
        if plugin.name in self.plugins:
            raise ValueError(f"Plugin {plugin.name} already registered")

        # Check dependencies
        for dep in plugin.dependencies:
            if dep not in self.plugins:
                raise ValueError(f"Plugin {plugin.name} requires {dep}")

        self.plugins[plugin.name] = plugin
        plugin.on_load()

    def enable(self, plugin_name: str) -> None:
        """Enable a plugin"""
        if plugin_name not in self.plugins:
            raise ValueError(f"Plugin {plugin_name} not found")

        plugin = self.plugins[plugin_name]
        plugin.on_enable()
        self.enabled_plugins.add(plugin_name)

    def disable(self, plugin_name: str) -> None:
        """Disable a plugin"""
        if plugin_name not in self.enabled_plugins:
            return

        plugin = self.plugins[plugin_name]
        plugin.on_disable()
        self.enabled_plugins.remove(plugin_name)

    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Get plugin by name"""
        return self.plugins.get(plugin_name)
```

#### Phase 2: Extension Points (Week 6)

**Goal**: Define extension interfaces

**Tasks:**
1. Create `StepHandler` interface for custom step types
2. Create `RecoveryStrategy` interface for custom recovery
3. Create `PersistenceBackend` interface for storage
4. Create `ErrorClassifier` interface for classification

**Example Extension Interfaces:**

```python
# src/luminous_nix/core/interfaces.py

from abc import ABC, abstractmethod
from typing import Dict, Any, List

class StepHandler(ABC):
    """Interface for custom step handlers"""

    @abstractmethod
    def can_handle(self, step_type: str) -> bool:
        """Check if this handler supports step type"""
        pass

    @abstractmethod
    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute step with parameters"""
        pass

    @abstractmethod
    def estimate_duration(self, parameters: Dict[str, Any]) -> float:
        """Estimate execution time in seconds"""
        pass

    def rollback(self, parameters: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Optional: Rollback step effects"""
        pass


class RecoveryStrategy(ABC):
    """Interface for custom recovery strategies"""

    @abstractmethod
    def can_recover(self, error: 'ClassifiedError') -> bool:
        """Check if this strategy can handle error"""
        pass

    @abstractmethod
    def recover(
        self,
        error: 'ClassifiedError',
        context: Dict[str, Any]
    ) -> bool:
        """Attempt recovery, return success"""
        pass

    @abstractmethod
    def estimate_time(self, error: 'ClassifiedError') -> float:
        """Estimate recovery time in seconds"""
        pass


class PersistenceBackend(ABC):
    """Interface for custom storage backends"""

    @abstractmethod
    def save_operation(self, operation: 'OperationState') -> None:
        """Save operation state"""
        pass

    @abstractmethod
    def load_operation(self, operation_id: str) -> Optional['OperationState']:
        """Load operation state"""
        pass

    @abstractmethod
    def list_operations(self, **filters) -> List['OperationState']:
        """List operations with filters"""
        pass

    @abstractmethod
    def delete_operation(self, operation_id: str) -> bool:
        """Delete operation"""
        pass


class ErrorClassifier(ABC):
    """Interface for custom error classifiers"""

    @abstractmethod
    def classify(
        self,
        error_message: str,
        context: Dict[str, Any]
    ) -> 'ClassifiedError':
        """Classify error message"""
        pass

    @abstractmethod
    def priority(self) -> int:
        """Classifier priority (higher = runs first)"""
        pass
```

#### Phase 3: Plugin Examples (Week 7)

**Goal**: Create example plugins to validate system

**Example Plugins:**

1. **NixPackageHandler Plugin** - Handle package operations
2. **MLErrorClassifier Plugin** - ML-based error classification
3. **PostgreSQLBackend Plugin** - PostgreSQL persistence
4. **SlackNotifier Plugin** - Send notifications to Slack

**Example Plugin:**

```python
# plugins/nix_package_handler.py

from luminous_nix.core.plugin_system import Plugin
from luminous_nix.core.interfaces import StepHandler

class NixPackageHandler(StepHandler, Plugin):
    """Handler for Nix package operations"""

    name = "nix_package_handler"
    version = "1.0.0"

    def can_handle(self, step_type: str) -> bool:
        return step_type in ['install_package', 'remove_package', 'search_package']

    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        step_type = parameters['step_type']

        if step_type == 'install_package':
            return self._install(parameters['package'])
        elif step_type == 'remove_package':
            return self._remove(parameters['package'])
        elif step_type == 'search_package':
            return self._search(parameters['query'])

    def estimate_duration(self, parameters: Dict[str, Any]) -> float:
        # Estimate based on step type
        estimates = {
            'install_package': 60.0,  # 1 minute
            'remove_package': 10.0,   # 10 seconds
            'search_package': 5.0     # 5 seconds
        }
        return estimates.get(parameters['step_type'], 30.0)

    def _install(self, package: str) -> Dict[str, Any]:
        # Actual implementation
        import subprocess
        result = subprocess.run(
            ['nix-env', '-iA', f'nixos.{package}'],
            capture_output=True,
            text=True
        )
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
```

---

## Part 2: Post-Quantum Cryptography (PQC)

### Why PQC?

**Threat**: Quantum computers will break current cryptography (RSA, ECC)
**Timeline**: 10-15 years until practical quantum computers
**Solution**: Implement PQC algorithms now for future-proofing

### Current Security Gaps

1. **State Storage** - SQLite database unencrypted
2. **JSON Backups** - Plaintext on disk
3. **Operation Signatures** - No integrity verification
4. **Secrets Management** - No secure storage for sensitive data

### PQC Integration Architecture

```
┌─────────────────────────────────────────────────────────┐
│              CryptoProvider (Interface)                 │
│  - encrypt() / decrypt()                               │
│  - sign() / verify()                                   │
│  - key_generation()                                    │
└─────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────┴─────────────────┐
        ↓                                    ↓
┌──────────────────┐              ┌──────────────────┐
│  ClassicCrypto   │              │    PQCCrypto     │
│  (OpenSSL)       │              │    (liboqs)      │
├──────────────────┤              ├──────────────────┤
│ • AES-256-GCM    │              │ • CRYSTALS-Kyber │
│ • RSA-4096       │              │ • CRYSTALS-Dilith│
│ • SHA-256        │              │ • Falcon         │
└──────────────────┘              └──────────────────┘
        ↓                                    ↓
┌─────────────────────────────────────────────────────────┐
│           Hybrid Mode (Recommended)                     │
│  - Use both classic + PQC                              │
│  - Secure against both classical and quantum attacks   │
└─────────────────────────────────────────────────────────┘
```

### Implementation Phases

#### Phase 1: Crypto Abstraction Layer (Week 8)

**Goal**: Abstract cryptography behind interfaces

```python
# src/luminous_nix/core/crypto.py

from abc import ABC, abstractmethod
from typing import Tuple, Optional
from dataclasses import dataclass

@dataclass
class CryptoKey:
    """Cryptographic key"""
    algorithm: str
    key_type: str  # 'public', 'private', 'symmetric'
    key_data: bytes
    metadata: dict

class CryptoProvider(ABC):
    """Abstract cryptography provider"""

    @abstractmethod
    def generate_keypair(self) -> Tuple[CryptoKey, CryptoKey]:
        """Generate public/private keypair"""
        pass

    @abstractmethod
    def encrypt(self, data: bytes, key: CryptoKey) -> bytes:
        """Encrypt data"""
        pass

    @abstractmethod
    def decrypt(self, ciphertext: bytes, key: CryptoKey) -> bytes:
        """Decrypt data"""
        pass

    @abstractmethod
    def sign(self, data: bytes, private_key: CryptoKey) -> bytes:
        """Sign data"""
        pass

    @abstractmethod
    def verify(self, data: bytes, signature: bytes, public_key: CryptoKey) -> bool:
        """Verify signature"""
        pass


class ClassicCryptoProvider(CryptoProvider):
    """OpenSSL-based cryptography"""

    def __init__(self):
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa, padding
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend

        self.backend = default_backend()

    def generate_keypair(self) -> Tuple[CryptoKey, CryptoKey]:
        """Generate RSA-4096 keypair"""
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization

        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=self.backend
        )

        public_key = private_key.public_key()

        return (
            CryptoKey(
                algorithm='RSA-4096',
                key_type='private',
                key_data=private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ),
                metadata={}
            ),
            CryptoKey(
                algorithm='RSA-4096',
                key_type='public',
                key_data=public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ),
                metadata={}
            )
        )

    def encrypt(self, data: bytes, key: CryptoKey) -> bytes:
        """Encrypt with AES-256-GCM"""
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        import os

        # Generate random nonce
        nonce = os.urandom(12)

        # Create cipher
        aesgcm = AESGCM(key.key_data[:32])  # Use first 32 bytes as key

        # Encrypt
        ciphertext = aesgcm.encrypt(nonce, data, None)

        # Return nonce + ciphertext
        return nonce + ciphertext

    # ... other methods


class PQCCryptoProvider(CryptoProvider):
    """Post-Quantum Cryptography (liboqs)"""

    def __init__(self):
        try:
            import oqs
            self.oqs = oqs
        except ImportError:
            raise ImportError(
                "liboqs not installed. Install with: "
                "pip install liboqs-python"
            )

    def generate_keypair(self) -> Tuple[CryptoKey, CryptoKey]:
        """Generate Kyber-1024 keypair"""
        # Kyber for encryption
        with self.oqs.KeyEncapsulation("Kyber1024") as kem:
            public_key = kem.generate_keypair()
            private_key = kem.export_secret_key()

            return (
                CryptoKey(
                    algorithm='Kyber-1024',
                    key_type='private',
                    key_data=private_key,
                    metadata={'kem': 'Kyber1024'}
                ),
                CryptoKey(
                    algorithm='Kyber-1024',
                    key_type='public',
                    key_data=public_key,
                    metadata={'kem': 'Kyber1024'}
                )
            )

    def encrypt(self, data: bytes, key: CryptoKey) -> bytes:
        """Encrypt using Kyber KEM + AES"""
        with self.oqs.KeyEncapsulation(key.metadata['kem']) as kem:
            # Encapsulate shared secret
            ciphertext, shared_secret = kem.encap_secret(key.key_data)

            # Use shared secret to encrypt data with AES
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            import os

            nonce = os.urandom(12)
            aesgcm = AESGCM(shared_secret[:32])
            encrypted_data = aesgcm.encrypt(nonce, data, None)

            # Return: kem_ciphertext + nonce + encrypted_data
            return ciphertext + nonce + encrypted_data


class HybridCryptoProvider(CryptoProvider):
    """Hybrid: Classic + PQC for maximum security"""

    def __init__(self):
        self.classic = ClassicCryptoProvider()
        self.pqc = PQCCryptoProvider()

    def generate_keypair(self) -> Tuple[CryptoKey, CryptoKey]:
        """Generate both classic and PQC keypairs"""
        classic_priv, classic_pub = self.classic.generate_keypair()
        pqc_priv, pqc_pub = self.pqc.generate_keypair()

        return (
            CryptoKey(
                algorithm='Hybrid-RSA4096-Kyber1024',
                key_type='private',
                key_data=b'',  # Composite key
                metadata={
                    'classic': classic_priv,
                    'pqc': pqc_priv
                }
            ),
            CryptoKey(
                algorithm='Hybrid-RSA4096-Kyber1024',
                key_type='public',
                key_data=b'',
                metadata={
                    'classic': classic_pub,
                    'pqc': pqc_pub
                }
            )
        )

    def encrypt(self, data: bytes, key: CryptoKey) -> bytes:
        """Double encrypt: classic + PQC"""
        # Encrypt with classic first
        classic_ct = self.classic.encrypt(data, key.metadata['classic'])

        # Then encrypt with PQC
        pqc_ct = self.pqc.encrypt(classic_ct, key.metadata['pqc'])

        return pqc_ct

    def decrypt(self, ciphertext: bytes, key: CryptoKey) -> bytes:
        """Double decrypt: PQC then classic"""
        # Decrypt PQC layer first
        classic_ct = self.pqc.decrypt(ciphertext, key.metadata['pqc'])

        # Then decrypt classic layer
        plaintext = self.classic.decrypt(classic_ct, key.metadata['classic'])

        return plaintext
```

#### Phase 2: Encrypted State Storage (Week 9)

**Goal**: Encrypt StateManager persistence

```python
# src/luminous_nix/core/encrypted_state_manager.py

from .state_manager import StateManager
from .crypto import CryptoProvider, CryptoKey

class EncryptedStateManager(StateManager):
    """StateManager with encrypted storage"""

    def __init__(
        self,
        db_path: Path,
        json_dir: Path,
        crypto_provider: CryptoProvider,
        encryption_key: CryptoKey
    ):
        super().__init__(db_path, json_dir)
        self.crypto = crypto_provider
        self.key = encryption_key

    def create_operation(
        self,
        user_query: str,
        user_id: Optional[str] = None
    ) -> OperationState:
        """Create operation with encrypted sensitive data"""
        state = super().create_operation(user_query, user_id)

        # Encrypt sensitive fields
        if state.user_query:
            encrypted_query = self.crypto.encrypt(
                state.user_query.encode(),
                self.key
            )
            state.user_query_encrypted = encrypted_query
            state.user_query = None  # Remove plaintext

        return state

    def update_operation(self, state: OperationState) -> None:
        """Update with encryption"""
        # Encrypt before saving
        if hasattr(state, 'sensitive_data'):
            state.sensitive_data_encrypted = self.crypto.encrypt(
                state.sensitive_data,
                self.key
            )
            del state.sensitive_data

        super().update_operation(state)
```

#### Phase 3: Operation Signatures (Week 10)

**Goal**: Sign operations for integrity verification

```python
# src/luminous_nix/core/signed_operations.py

from .state_manager import OperationState
from .crypto import CryptoProvider, CryptoKey
import json
import hashlib

class SignedOperationState(OperationState):
    """OperationState with signature verification"""

    signature: Optional[bytes] = None
    signature_algorithm: Optional[str] = None


class SignedStateManager(EncryptedStateManager):
    """StateManager with operation signatures"""

    def __init__(
        self,
        db_path: Path,
        json_dir: Path,
        crypto_provider: CryptoProvider,
        encryption_key: CryptoKey,
        signing_key: CryptoKey
    ):
        super().__init__(db_path, json_dir, crypto_provider, encryption_key)
        self.signing_key = signing_key

    def create_operation(
        self,
        user_query: str,
        user_id: Optional[str] = None
    ) -> SignedOperationState:
        """Create signed operation"""
        state = SignedOperationState(
            operation_id=self._generate_operation_id(),
            user_query=user_query,
            user_id=user_id,
            # ... other fields
        )

        # Sign operation
        state.signature = self._sign_operation(state)
        state.signature_algorithm = self.crypto.__class__.__name__

        return state

    def update_operation(self, state: SignedOperationState) -> None:
        """Update and re-sign"""
        # Re-sign before saving
        state.signature = self._sign_operation(state)

        super().update_operation(state)

    def get_operation(self, operation_id: str) -> Optional[SignedOperationState]:
        """Get and verify signature"""
        state = super().get_operation(operation_id)

        if state and not self._verify_signature(state):
            raise ValueError(f"Operation {operation_id} signature invalid!")

        return state

    def _sign_operation(self, state: SignedOperationState) -> bytes:
        """Sign operation state"""
        # Create canonical representation
        data = {
            'operation_id': state.operation_id,
            'user_query': state.user_query,
            'status': state.status.value,
            'created_at': state.created_at.isoformat() if state.created_at else None,
            # ... other fields
        }

        canonical = json.dumps(data, sort_keys=True).encode()

        # Sign
        signature = self.crypto.sign(canonical, self.signing_key)

        return signature

    def _verify_signature(self, state: SignedOperationState) -> bool:
        """Verify operation signature"""
        if not state.signature:
            return False

        # Recreate canonical representation
        data = {
            'operation_id': state.operation_id,
            'user_query': state.user_query,
            'status': state.status.value,
            'created_at': state.created_at.isoformat() if state.created_at else None,
        }

        canonical = json.dumps(data, sort_keys=True).encode()

        # Verify
        return self.crypto.verify(
            canonical,
            state.signature,
            self.signing_key  # Would use public key in production
        )
```

---

## Part 3: Continuous Improvement Strategy

### Versioning & Compatibility

#### Semantic Versioning

**Format**: MAJOR.MINOR.PATCH

- **MAJOR**: Breaking changes (incompatible API)
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

**Example Evolution:**
```
v1.0.0 → Foundation complete (current)
v1.1.0 → Add plugin system (backward compatible)
v1.2.0 → Add PQC support (backward compatible)
v2.0.0 → Change core API (breaking change)
```

#### Compatibility Strategy

```python
# src/luminous_nix/core/version.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class Version:
    """Semantic version"""
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def is_compatible_with(self, other: 'Version') -> bool:
        """Check if versions are compatible"""
        # Same major version = compatible
        return self.major == other.major


class CompatibilityLayer:
    """Handle version migrations"""

    def __init__(self, current_version: Version):
        self.current = current_version
        self.migrations = {}

    def register_migration(
        self,
        from_version: Version,
        to_version: Version,
        migrate_func: callable
    ):
        """Register migration function"""
        key = (str(from_version), str(to_version))
        self.migrations[key] = migrate_func

    def migrate_state(
        self,
        state: dict,
        from_version: Version
    ) -> dict:
        """Migrate state from old version to current"""
        if from_version == self.current:
            return state

        # Find migration path
        key = (str(from_version), str(self.current))
        if key in self.migrations:
            return self.migrations[key](state)

        raise ValueError(f"No migration from {from_version} to {self.current}")


# Example migration
def migrate_1_0_to_1_1(state: dict) -> dict:
    """Migrate from v1.0 to v1.1"""
    # v1.1 added 'retry_strategy' field
    if 'retry_strategy' not in state:
        state['retry_strategy'] = 'exponential_backoff'
    return state
```

### Testing Strategy for New Features

#### Test Categories

```
Unit Tests       → Test individual components
  ↓
Integration Tests → Test system combinations
  ↓
End-to-End Tests  → Test complete workflows
  ↓
Performance Tests → Test scalability
  ↓
Security Tests    → Test crypto/safety
```

#### Test Template for New Features

```python
# tests/test_new_feature.py

import pytest
from luminous_nix.core.new_feature import NewFeature

class TestNewFeature:
    """Tests for new feature"""

    def test_basic_functionality(self):
        """Test core feature works"""
        feature = NewFeature()
        result = feature.do_something()
        assert result == expected

    def test_edge_cases(self):
        """Test edge cases"""
        feature = NewFeature()
        # Empty input
        result = feature.do_something(None)
        assert result is handled_gracefully

    def test_error_handling(self):
        """Test error cases"""
        feature = NewFeature()
        with pytest.raises(ValueError):
            feature.do_something(invalid_input)

    def test_integration_with_existing(self):
        """Test integration with existing systems"""
        feature = NewFeature()
        executor = StatefulExecutor(...)
        # Test they work together

    def test_backward_compatibility(self):
        """Test doesn't break existing code"""
        # Old usage patterns still work

    def test_performance(self):
        """Test performance acceptable"""
        import time
        start = time.time()
        feature.do_something()
        duration = time.time() - start
        assert duration < 1.0  # Should complete in <1s
```

### Documentation Standards

#### Required Documentation for New Features

1. **Code Documentation**
   - Docstrings for all public APIs
   - Type hints throughout
   - Example usage in docstrings

2. **User Documentation**
   - README section for feature
   - Tutorial/guide if complex
   - API reference

3. **Developer Documentation**
   - Architecture decisions (ADR)
   - Implementation notes
   - Extension points

4. **Migration Guides**
   - Breaking changes
   - Upgrade path
   - Deprecation notices

### Extension Pattern Examples

#### Example 1: Custom Step Type

```python
# plugins/custom_step.py

from luminous_nix.core.plugin_system import Plugin
from luminous_nix.core.interfaces import StepHandler

class CustomStepPlugin(StepHandler, Plugin):
    """Plugin adding custom step type"""

    name = "custom_step"
    version = "1.0.0"

    def can_handle(self, step_type: str) -> bool:
        return step_type == 'my_custom_operation'

    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        # Custom logic
        return {'success': True, 'result': 'Custom operation completed'}

    def estimate_duration(self, parameters: Dict[str, Any]) -> float:
        return 30.0  # 30 seconds

# Usage:
# 1. Drop plugin in plugins/ directory
# 2. System auto-discovers on startup
# 3. Use in ExecutionPlan:
#
# step = ExecutionStep(
#     id="custom",
#     name="Custom Operation",
#     step_type="my_custom_operation",
#     handler=registry.get_handler("my_custom_operation"),
#     parameters={'foo': 'bar'}
# )
```

#### Example 2: Custom Error Classifier

```python
# plugins/ml_classifier.py

from luminous_nix.core.plugin_system import Plugin
from luminous_nix.core.interfaces import ErrorClassifier

class MLErrorClassifierPlugin(ErrorClassifier, Plugin):
    """ML-based error classification"""

    name = "ml_error_classifier"
    version = "1.0.0"
    dependencies = []

    def __init__(self):
        # Load ML model
        import joblib
        self.model = joblib.load('error_classifier_model.pkl')

    def classify(
        self,
        error_message: str,
        context: Dict[str, Any]
    ) -> ClassifiedError:
        """Classify using ML model"""
        # Extract features
        features = self._extract_features(error_message)

        # Predict
        category, severity, recoverability = self.model.predict([features])

        return ClassifiedError(
            message=error_message,
            category=ErrorCategory(category),
            severity=ErrorSeverity(severity),
            recoverability=RecoverabilityLevel(recoverability),
            operation_id=context.get('operation_id', 'unknown')
        )

    def priority(self) -> int:
        return 100  # High priority (runs before pattern-based)

    def _extract_features(self, error_message: str) -> List[float]:
        # Feature engineering
        return [...]
```

---

## Implementation Roadmap

### Timeline

```
Week 5:  Plugin System Foundation
Week 6:  Extension Points & Interfaces
Week 7:  Example Plugins
Week 8:  Crypto Abstraction Layer
Week 9:  Encrypted State Storage
Week 10: Operation Signatures
Week 11: PQC Integration Testing
Week 12: Documentation & Migration Guides
```

### Success Criteria

**Modularity:**
- ✅ Plugin system working with 3+ example plugins
- ✅ Extension points documented
- ✅ Backward compatibility maintained

**PQC:**
- ✅ Hybrid crypto working (classic + PQC)
- ✅ State storage encrypted
- ✅ Operations signed and verified
- ✅ Performance acceptable (<20% overhead)

**Continuous Improvement:**
- ✅ Versioning strategy implemented
- ✅ Migration system working
- ✅ Testing standards documented
- ✅ Extension patterns validated

---

## Recommendations

### Priority Order

1. **Modularity First** (Weeks 5-7)
   - Enables community contributions
   - Makes system more maintainable
   - Foundation for other improvements

2. **PQC Integration** (Weeks 8-10)
   - Future-proofs security
   - Adds competitive advantage
   - Demonstrates forward thinking

3. **Continuous Process** (Ongoing)
   - Document as you build
   - Test everything
   - Maintain compatibility

### Quick Wins

**Immediate (This Week):**
1. Add version field to OperationState
2. Document extension points in existing code
3. Create plugins/ directory structure

**Short-term (Next Month):**
1. Implement basic plugin system
2. Create 2-3 example plugins
3. Add encryption to sensitive state data

**Long-term (Next Quarter):**
1. Full PQC integration
2. Community plugin marketplace
3. Performance optimization based on real usage

---

## Conclusion

This plan provides a clear path for evolving Luminous Nix:

**Modularity** → Enables extensibility and community contributions
**PQC** → Future-proofs security against quantum threats
**Continuous Improvement** → Ensures long-term sustainability

The foundation we built in Weeks 1-4 is solid enough to support these enhancements without major refactoring. Each improvement builds on the previous, creating a more powerful, flexible, and secure system.

**Next Steps:**
1. Review this plan
2. Prioritize features based on user needs
3. Start with modularity (Week 5)
4. Iterate and improve

The journey from foundation to production-ready system continues! 🚀

---

**Created**: December 2, 2025
**Status**: Strategic roadmap
**Timeline**: 12 weeks for complete implementation
**Confidence**: HIGH (builds on solid foundation)
