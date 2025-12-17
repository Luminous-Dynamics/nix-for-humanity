"""
StateManager - Operation state tracking and persistence

This module implements state management for Luminous Nix operations,
tracking state across all 6 architecture layers with dual persistence
(SQLite + JSON).

Based on design: DEEP_DIVE_STATE_MANAGEMENT.md
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any
from datetime import datetime
from enum import Enum
from pathlib import Path
import uuid
import sqlite3
import json
import logging

logger = logging.getLogger(__name__)


class OperationType(Enum):
    """Type of NixOS operation being performed"""
    SEARCH = "search"                # Search for packages
    INSTALL = "install"              # Install packages
    UNINSTALL = "uninstall"          # Remove packages
    UPDATE = "update"                # Update packages/system
    CONFIG_GENERATE = "config_generate"  # Generate configuration
    SYSTEM_REBUILD = "system_rebuild"    # Rebuild system
    ROLLBACK = "rollback"            # Rollback to previous generation
    CUSTOM = "custom"                # Custom operation


class OperationStatus(Enum):
    """Lifecycle status of an operation"""
    CREATED = "created"              # Just created, not started
    ANALYZING = "analyzing"          # Layer 1-2: Intent + Context analysis
    PLANNING = "planning"            # Layer 3: Strategy selection
    READY = "ready"                  # Plan complete, ready to execute
    EXECUTING = "executing"          # Layer 4: Active execution
    PAUSED = "paused"                # Paused by user or system
    COMPLETED = "completed"          # Successfully finished
    FAILED = "failed"                # Failed with error
    ROLLED_BACK = "rolled_back"      # Rolled back after failure
    ROLLBACK_FAILED = "rollback_failed"  # Rollback itself failed
    CANCELLED = "cancelled"          # Cancelled by user

    def is_terminal(self) -> bool:
        """Check if this is a final state"""
        return self in {
            OperationStatus.COMPLETED,
            OperationStatus.FAILED,
            OperationStatus.ROLLED_BACK,
            OperationStatus.ROLLBACK_FAILED,
            OperationStatus.CANCELLED
        }

    def is_active(self) -> bool:
        """Check if operation is currently running"""
        return self in {
            OperationStatus.ANALYZING,
            OperationStatus.PLANNING,
            OperationStatus.EXECUTING
        }


@dataclass
class LayerState:
    """State for a single architecture layer"""
    layer_number: int  # 1-6
    layer_name: str    # "Semantic Understanding", "Context Analysis", etc.
    status: str        # "pending", "in_progress", "complete", "failed"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[float] = None

    # Layer-specific data
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    # Performance metrics
    metrics: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for persistence"""
        return {
            'layer_number': self.layer_number,
            'layer_name': self.layer_name,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_ms': self.duration_ms,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'errors': self.errors,
            'metrics': self.metrics
        }


@dataclass
class OperationState:
    """
    Complete state of an operation across all 6 layers.

    This is the master state object that tracks everything about
    a user's request from "install firefox" through completion.
    """

    # Identity
    operation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_id: Optional[str] = None  # For sub-operations
    operation_type: OperationType = OperationType.CUSTOM  # Type of operation

    # User context
    user_query: str = ""
    user_id: str = "default"  # For multi-user systems
    session_id: str = ""

    # Lifecycle
    status: OperationStatus = OperationStatus.CREATED
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Layer states (all 6 layers)
    layers: Dict[int, LayerState] = field(default_factory=dict)

    # Execution plan (from Layer 4)
    execution_plan: Optional[Any] = None  # ExecutionPlan reference
    current_step_id: Optional[str] = None
    completed_steps: Set[str] = field(default_factory=set)
    failed_steps: Set[str] = field(default_factory=set)

    # Results
    result: Optional[Any] = None
    error: Optional[str] = None
    error_details: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    tags: Set[str] = field(default_factory=set)
    priority: int = 5  # 1-10, higher = more important
    estimated_duration_s: Optional[float] = None
    actual_duration_s: Optional[float] = None

    # Recovery information
    resumable: bool = True
    checkpoint_data: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3

    # Learning data (Layer 6)
    user_feedback: Optional[str] = None  # "success", "failure", "partial"
    feedback_details: Dict[str, Any] = field(default_factory=dict)

    # Security / Integrity (Week 10: Operation Signatures)
    signature: Optional[bytes] = None  # Cryptographic signature
    signature_algorithm: Optional[str] = None  # Algorithm used (RSA-4096, Kyber-1024, etc.)

    # 🆕 Week 2: User Identity (Layer 7 - Mycelix Integration)
    user_did: Optional[str] = None  # User's DID (did:mycelix:luminous_nix:...)
    assurance_level: Optional[str] = None  # E0, E1, E2, E3, or E4

    # 🆕 Week 3: Trust Metadata (MATL Trust Scoring)
    trust_score: Optional[float] = None  # 0.0-1.0 (calculated by MATL engine)
    trust_components: Dict[str, float] = field(default_factory=dict)  # PoGQ, TCDM, Entropy

    def __post_init__(self):
        """Initialize layer states"""
        if not self.layers:
            layer_names = [
                "Semantic Understanding",
                "Context Analysis",
                "Strategy Selection",
                "Execution",
                "Adaptive Monitoring",
                "Learning"
            ]
            for i, name in enumerate(layer_names, 1):
                self.layers[i] = LayerState(
                    layer_number=i,
                    layer_name=name,
                    status="pending"
                )

    # === State Queries ===

    def get_current_layer(self) -> Optional[LayerState]:
        """Get the layer currently in progress"""
        for layer in self.layers.values():
            if layer.status == "in_progress":
                return layer
        return None

    def get_completed_layers(self) -> List[LayerState]:
        """Get all completed layers"""
        return [l for l in self.layers.values() if l.status == "complete"]

    def get_progress_percent(self) -> float:
        """Calculate overall progress (0.0-1.0)"""
        if self.status.is_terminal():
            return 1.0

        completed = len([l for l in self.layers.values() if l.status == "complete"])
        total = len(self.layers)
        return completed / total if total > 0 else 0.0

    def is_resumable(self) -> bool:
        """Can this operation be resumed?"""
        return (
            self.resumable and
            not self.status.is_terminal() and
            self.status != OperationStatus.CANCELLED and
            len(self.checkpoint_data) > 0
        )

    def can_retry(self) -> bool:
        """Can this operation be retried?"""
        return (
            self.status == OperationStatus.FAILED and
            self.retry_count < self.max_retries
        )

    # === State Transitions ===

    def start_layer(self, layer_number: int, input_data: Dict[str, Any] = None):
        """Start processing a layer"""
        if layer_number in self.layers:
            layer = self.layers[layer_number]
            layer.status = "in_progress"
            layer.started_at = datetime.now()
            if input_data:
                layer.input_data = input_data

    def complete_layer(self, layer_number: int, output_data: Dict[str, Any] = None):
        """Mark a layer as complete"""
        if layer_number in self.layers:
            layer = self.layers[layer_number]
            layer.status = "complete"
            layer.completed_at = datetime.now()
            if layer.started_at:
                duration = (layer.completed_at - layer.started_at).total_seconds() * 1000
                layer.duration_ms = duration
            if output_data:
                layer.output_data = output_data

    def fail_layer(self, layer_number: int, error: str):
        """Mark a layer as failed"""
        if layer_number in self.layers:
            layer = self.layers[layer_number]
            layer.status = "failed"
            layer.completed_at = datetime.now()
            layer.errors.append(error)

    # === Serialization ===

    def to_dict(self) -> Dict[str, Any]:
        """Serialize complete state to dictionary"""
        import base64
        return {
            'operation_id': self.operation_id,
            'parent_id': self.parent_id,
            'operation_type': self.operation_type.value if hasattr(self, 'operation_type') else 'custom',
            'user_query': self.user_query,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'layers': {k: v.to_dict() for k, v in self.layers.items()},
            'current_step_id': self.current_step_id,
            'completed_steps': list(self.completed_steps),
            'failed_steps': list(self.failed_steps),
            'result': self.result,
            'error': self.error,
            'error_details': self.error_details,
            'tags': list(self.tags),
            'priority': self.priority,
            'estimated_duration_s': self.estimated_duration_s,
            'actual_duration_s': self.actual_duration_s,
            'resumable': self.resumable,
            'checkpoint_data': self.checkpoint_data,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'user_feedback': self.user_feedback,
            'feedback_details': self.feedback_details,
            # Week 10: Operation Signatures
            'signature': base64.b64encode(self.signature).decode('utf-8') if self.signature else None,
            'signature_algorithm': self.signature_algorithm,
            # 🆕 Week 2: User Identity
            'user_did': self.user_did,
            'assurance_level': self.assurance_level,
            # 🆕 Week 3: Trust Metadata
            'trust_score': self.trust_score,
            'trust_components': self.trust_components
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OperationState':
        """Deserialize from dictionary"""
        # Convert datetime strings
        created_at = datetime.fromisoformat(data['created_at'])
        started_at = datetime.fromisoformat(data['started_at']) if data.get('started_at') else None
        completed_at = datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None

        # Convert layers
        layers = {}
        for k, v in data.get('layers', {}).items():
            layer_data = v.copy()
            if layer_data.get('started_at'):
                layer_data['started_at'] = datetime.fromisoformat(layer_data['started_at'])
            if layer_data.get('completed_at'):
                layer_data['completed_at'] = datetime.fromisoformat(layer_data['completed_at'])
            layers[int(k)] = LayerState(**layer_data)

        import base64
        # Deserialize signature (Week 10)
        signature_data = data.get('signature')
        signature = base64.b64decode(signature_data) if signature_data else None

        return cls(
            operation_id=data['operation_id'],
            parent_id=data.get('parent_id'),
            operation_type=OperationType(data.get('operation_type', 'custom')),
            user_query=data['user_query'],
            user_id=data.get('user_id', 'default'),
            session_id=data.get('session_id', ''),
            status=OperationStatus(data['status']),
            created_at=created_at,
            started_at=started_at,
            completed_at=completed_at,
            layers=layers,
            current_step_id=data.get('current_step_id'),
            completed_steps=set(data.get('completed_steps', [])),
            failed_steps=set(data.get('failed_steps', [])),
            result=data.get('result'),
            error=data.get('error'),
            error_details=data.get('error_details', {}),
            tags=set(data.get('tags', [])),
            priority=data.get('priority', 5),
            estimated_duration_s=data.get('estimated_duration_s'),
            actual_duration_s=data.get('actual_duration_s'),
            resumable=data.get('resumable', True),
            checkpoint_data=data.get('checkpoint_data', {}),
            retry_count=data.get('retry_count', 0),
            max_retries=data.get('max_retries', 3),
            user_feedback=data.get('user_feedback'),
            feedback_details=data.get('feedback_details', {}),
            # Week 10: Operation Signatures
            signature=signature,
            signature_algorithm=data.get('signature_algorithm'),
            # 🆕 Week 2: User Identity
            user_did=data.get('user_did'),
            assurance_level=data.get('assurance_level'),
            # 🆕 Week 3: Trust Metadata
            trust_score=data.get('trust_score'),
            trust_components=data.get('trust_components', {})
        )


class StateTransitionValidator:
    """Validates state transitions are legal"""

    # Valid state transitions
    TRANSITIONS = {
        OperationStatus.CREATED: {
            OperationStatus.ANALYZING,
            OperationStatus.CANCELLED
        },
        OperationStatus.ANALYZING: {
            OperationStatus.PLANNING,
            OperationStatus.FAILED,
            OperationStatus.PAUSED,
            OperationStatus.CANCELLED
        },
        OperationStatus.PLANNING: {
            OperationStatus.READY,
            OperationStatus.FAILED,
            OperationStatus.PAUSED,
            OperationStatus.CANCELLED
        },
        OperationStatus.READY: {
            OperationStatus.EXECUTING,
            OperationStatus.PAUSED,
            OperationStatus.CANCELLED
        },
        OperationStatus.EXECUTING: {
            OperationStatus.COMPLETED,
            OperationStatus.FAILED,
            OperationStatus.PAUSED,
            OperationStatus.CANCELLED
        },
        OperationStatus.PAUSED: {
            OperationStatus.ANALYZING,
            OperationStatus.PLANNING,
            OperationStatus.READY,
            OperationStatus.EXECUTING,
            OperationStatus.CANCELLED
        },
        OperationStatus.FAILED: {
            OperationStatus.ANALYZING,  # Retry from start
            OperationStatus.ROLLED_BACK,
            OperationStatus.ROLLBACK_FAILED
        },
        # Terminal states can't transition
        OperationStatus.COMPLETED: set(),
        OperationStatus.ROLLED_BACK: set(),
        OperationStatus.ROLLBACK_FAILED: set(),
        OperationStatus.CANCELLED: set()
    }

    @classmethod
    def can_transition(cls, from_status: OperationStatus, to_status: OperationStatus) -> bool:
        """Check if transition is valid"""
        return to_status in cls.TRANSITIONS.get(from_status, set())

    @classmethod
    def validate_transition(cls, state: OperationState, new_status: OperationStatus):
        """Validate transition and raise if invalid"""
        if not cls.can_transition(state.status, new_status):
            raise ValueError(
                f"Invalid transition from {state.status.value} to {new_status.value}"
            )


@dataclass
class StateManager:
    """
    Manages operation state with dual persistence (SQLite + JSON).

    Provides CRUD operations, querying, and crash recovery support.

    Week 9-10 Enhancement: Supports encrypted state persistence using PQC.
    """

    db_path: Optional[Path] = None
    json_dir: Optional[Path] = None
    storage_dir: Optional[Path] = None  # For encrypted storage
    encryption_enabled: bool = True      # Enable encryption by default
    signing_enabled: bool = False        # Enable operation signing (Week 10)

    # In-memory cache for fast access
    _cache: Dict[str, OperationState] = field(default_factory=dict, init=False)
    _conn: Optional[sqlite3.Connection] = field(default=None, init=False)

    # PQC encryption components (initialized if encryption enabled)
    _encryption: Optional[Any] = field(default=None, init=False)
    _public_key: Optional[Any] = field(default=None, init=False)
    _private_key: Optional[Any] = field(default=None, init=False)

    # Signing components (Week 10: Operation Signatures)
    _signing_key: Optional[Any] = field(default=None, init=False)

    def __post_init__(self):
        """Initialize database and directories"""
        # If storage_dir is provided but db_path/json_dir are not, derive them
        if self.storage_dir is not None:
            self.storage_dir = Path(self.storage_dir)
            if self.db_path is None:
                self.db_path = self.storage_dir / "operations.db"
            if self.json_dir is None:
                self.json_dir = self.storage_dir / "json"

        # Ensure paths are Path objects (for backward compatibility)
        if self.db_path is not None:
            self.db_path = Path(self.db_path)
        else:
            raise ValueError("Either db_path or storage_dir must be provided")

        if self.json_dir is not None:
            self.json_dir = Path(self.json_dir)
        else:
            raise ValueError("Either json_dir or storage_dir must be provided")

        # Storage dir defaults to db_path parent if not specified
        if self.storage_dir is None:
            self.storage_dir = self.db_path.parent
        else:
            self.storage_dir = Path(self.storage_dir)

        # Create directories
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.json_dir.mkdir(parents=True, exist_ok=True)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

        # Initialize encryption if enabled
        if self.encryption_enabled:
            self._init_encryption()

        # Initialize signing if enabled (Week 10: Operation Signatures)
        if self.signing_enabled:
            self._init_signing()

        # 🆕 Week 2: Initialize DID manager and load current user DID
        self._did_manager = None
        self._current_user_did = None
        self._init_did_manager()

    def _init_database(self):
        """Initialize SQLite database with schema"""
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row

        cursor = self._conn.cursor()

        # Create operations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS operations (
                operation_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                user_query TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                resumable INTEGER DEFAULT 1,
                priority INTEGER DEFAULT 5,
                data TEXT NOT NULL,
                UNIQUE(operation_id)
            )
        """)

        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_id ON operations(user_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status ON operations(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at ON operations(created_at)
        """)

        self._conn.commit()

    def create_operation(
        self,
        user_query: str,
        user_id: str = "default",
        tags: Set[str] = None
    ) -> OperationState:
        """Create a new operation"""
        state = OperationState(
            user_query=user_query,
            user_id=user_id,
            tags=tags or set()
        )

        # 🆕 Week 2: Attach user DID to operation
        if self._current_user_did:
            state.user_did = self._current_user_did.did
            state.assurance_level = self._current_user_did.assurance_level
            logger.debug(f"Attached DID to operation: {state.user_did}")

        # Save to database
        self._save_to_db(state)

        # Save to JSON
        self._save_to_json(state)

        # Cache
        self._cache[state.operation_id] = state

        return state

    def get_operation(self, operation_id: str) -> Optional[OperationState]:
        """Get operation by ID"""
        # Check cache first
        if operation_id in self._cache:
            return self._cache[operation_id]

        # Query database
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT data FROM operations WHERE operation_id = ?",
            (operation_id,)
        )
        row = cursor.fetchone()

        if row:
            data = json.loads(row['data'])
            state = OperationState.from_dict(data)
            self._cache[operation_id] = state
            return state

        return None

    def update_operation(self, state: OperationState):
        """Update an existing operation"""
        # Update database
        self._save_to_db(state)

        # Update JSON
        self._save_to_json(state)

        # Update cache
        self._cache[state.operation_id] = state

    def list_operations(
        self,
        user_id: Optional[str] = None,
        status: Optional[OperationStatus] = None,
        limit: int = 100
    ) -> List[OperationState]:
        """List operations with optional filters"""
        cursor = self._conn.cursor()

        query = "SELECT data FROM operations WHERE 1=1"
        params = []

        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)

        if status:
            query += " AND status = ?"
            params.append(status.value)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        operations = []
        for row in rows:
            data = json.loads(row['data'])
            state = OperationState.from_dict(data)
            operations.append(state)

        return operations

    def get_active_operations(self) -> List[OperationState]:
        """Get all active (non-terminal) operations"""
        cursor = self._conn.cursor()

        # Query for active statuses
        active_statuses = [
            s.value for s in [
                OperationStatus.CREATED,
                OperationStatus.ANALYZING,
                OperationStatus.PLANNING,
                OperationStatus.READY,
                OperationStatus.EXECUTING,
                OperationStatus.PAUSED
            ]
        ]

        placeholders = ','.join('?' * len(active_statuses))
        cursor.execute(
            f"SELECT data FROM operations WHERE status IN ({placeholders})",
            active_statuses
        )
        rows = cursor.fetchall()

        operations = []
        for row in rows:
            data = json.loads(row['data'])
            state = OperationState.from_dict(data)
            operations.append(state)

        return operations

    def delete_operation(self, operation_id: str):
        """Delete an operation"""
        # Remove from database
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM operations WHERE operation_id = ?", (operation_id,))
        self._conn.commit()

        # Remove from cache
        self._cache.pop(operation_id, None)

        # Remove JSON file
        json_file = self._get_json_path(operation_id)
        if json_file.exists():
            json_file.unlink()

    def _save_to_db(self, state: OperationState):
        """Save state to SQLite"""
        data_json = json.dumps(state.to_dict())

        cursor = self._conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO operations
            (operation_id, user_id, user_query, status, created_at, started_at, completed_at, resumable, priority, data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            state.operation_id,
            state.user_id,
            state.user_query,
            state.status.value,
            state.created_at.isoformat(),
            state.started_at.isoformat() if state.started_at else None,
            state.completed_at.isoformat() if state.completed_at else None,
            1 if state.resumable else 0,
            state.priority,
            data_json
        ))
        self._conn.commit()

    def _save_to_json(self, state: OperationState):
        """Save state to JSON file"""
        json_file = self._get_json_path(state.operation_id)
        json_file.parent.mkdir(parents=True, exist_ok=True)

        with open(json_file, 'w') as f:
            json.dump(state.to_dict(), f, indent=2)

    def _get_json_path(self, operation_id: str) -> Path:
        """Get JSON file path for operation"""
        if self.encryption_enabled:
            # Encrypted files go directly in storage_dir
            return self.storage_dir / f"{operation_id}.encrypted"
        else:
            # Unencrypted files go directly in storage_dir as well
            return self.storage_dir / f"{operation_id}.json"

    def _init_encryption(self):
        """Initialize PQC encryption components"""
        try:
            from luminous_nix.security.pqc import PQCKeyManager, PQCEncryption

            key_manager = PQCKeyManager()

            # Try to load existing keys from storage_dir
            key_file_public = self.storage_dir / ".state_manager_public.pem"
            key_file_private = self.storage_dir / ".state_manager_private.pem"

            if key_file_public.exists() and key_file_private.exists():
                # Load existing keys
                self._public_key = key_manager.load_public_key(key_file_public)
                self._private_key = key_manager.load_private_key(key_file_private)
                logger.info("Loaded existing encryption keys for StateManager")
            else:
                # Generate new key pair and save
                self._public_key, self._private_key = key_manager.generate_key_pair()
                key_manager.save_public_key(self._public_key, key_file_public)
                key_manager.save_private_key(self._private_key, key_file_private)
                logger.info("Generated new encryption keys for StateManager")

            self._encryption = PQCEncryption()

        except ImportError as e:
            logger.error(f"Failed to initialize PQC encryption: {e}")
            logger.warning("Falling back to unencrypted storage")
            self.encryption_enabled = False

    def _init_signing(self):
        """Initialize operation signing components (Week 10)"""
        try:
            from luminous_nix.security.pqc import PQCKeyManager

            key_manager = PQCKeyManager()

            # Try to load existing signing key from storage_dir
            signing_key_file = self.storage_dir / ".state_manager_signing.pem"

            if signing_key_file.exists():
                # Load existing signing key (private key used for signing)
                self._signing_key = key_manager.load_private_key(signing_key_file)
                logger.info("Loaded existing signing key for StateManager")
            else:
                # Generate new key pair and save
                # For signing, we only need the private key
                public_key, private_key = key_manager.generate_key_pair()
                self._signing_key = private_key
                key_manager.save_private_key(private_key, signing_key_file)
                logger.info("Generated new signing key for StateManager")

        except ImportError as e:
            logger.error(f"Failed to initialize operation signing: {e}")
            logger.warning("Falling back to unsigned operations")
            self.signing_enabled = False

    def _init_did_manager(self):
        """🆕 Week 2: Initialize DID manager and load current user DID"""
        try:
            from luminous_nix.mycelix.identity import DIDManager

            # Use storage_dir/identity for DID storage (consistent with state storage)
            did_storage_path = self.storage_dir.parent / "identity"
            self._did_manager = DIDManager(storage_path=did_storage_path)
            self._current_user_did = self._did_manager.get_current_did()

            if self._current_user_did:
                logger.info(f"Loaded user DID: {self._current_user_did.did[:30]}...")
            else:
                logger.info("No user DID found (run 'ask-nix did setup' to create one)")

        except ImportError as e:
            logger.warning(f"DID manager not available: {e}")
            self._did_manager = None
            self._current_user_did = None

    def _sign_operation(self, state: OperationState) -> bytes:
        """
        Sign operation state for integrity verification.

        Creates a canonical representation of the operation and signs it
        using the private signing key.

        Args:
            state: Operation state to sign

        Returns:
            Signature bytes
        """
        import hashlib

        # Create canonical representation (deterministic JSON)
        canonical_data = {
            'operation_id': state.operation_id,
            'operation_type': state.operation_type.value if hasattr(state, 'operation_type') else 'custom',
            'user_query': state.user_query,
            'status': state.status.value,
            'created_at': state.created_at.isoformat() if state.created_at else None,
        }

        # Include result if present (for completed operations)
        if state.result is not None:
            canonical_data['result'] = str(state.result)

        # Serialize to canonical JSON (sorted keys for determinism)
        canonical_json = json.dumps(canonical_data, sort_keys=True).encode('utf-8')

        # Sign using PQC
        try:
            from luminous_nix.security.pqc import PQCEncryption

            encryption = PQCEncryption()

            # Use encryption module's sign method if available
            # For now, use SHA-256 hash + RSA signature
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import padding
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives import serialization

            # Load private key for signing
            private_key = serialization.load_pem_private_key(
                self._signing_key if isinstance(self._signing_key, bytes) else self._signing_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ),
                password=None,
                backend=default_backend()
            )

            # Sign
            signature = private_key.sign(
                canonical_json,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            return signature

        except Exception as e:
            logger.error(f"Failed to sign operation: {e}")
            raise

    def _verify_signature(self, state: OperationState) -> bool:
        """
        Verify operation signature.

        Args:
            state: Operation state with signature to verify

        Returns:
            True if signature is valid, False otherwise
        """
        if state.signature is None:
            # No signature to verify (unsigned operation)
            if self.signing_enabled:
                logger.warning(f"Operation {state.operation_id} has no signature but signing is enabled")
            return not self.signing_enabled  # If signing disabled, unsigned is OK

        try:
            # Recreate canonical representation
            canonical_data = {
                'operation_id': state.operation_id,
                'operation_type': state.operation_type.value if hasattr(state, 'operation_type') else 'custom',
                'user_query': state.user_query,
                'status': state.status.value,
                'created_at': state.created_at.isoformat() if state.created_at else None,
            }

            if state.result is not None:
                canonical_data['result'] = str(state.result)

            canonical_json = json.dumps(canonical_data, sort_keys=True).encode('utf-8')

            # Verify signature
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import padding
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives import serialization

            # Load private key (in production, would use public key)
            # For now, using private key since we're self-signing
            private_key = serialization.load_pem_private_key(
                self._signing_key if isinstance(self._signing_key, bytes) else self._signing_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ),
                password=None,
                backend=default_backend()
            )

            # Get public key from private key
            public_key = private_key.public_key()

            # Verify
            public_key.verify(
                state.signature,
                canonical_json,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            return True

        except Exception as e:
            logger.error(f"Signature verification failed for operation {state.operation_id}: {e}")
            return False

    def save_state(self, state: OperationState) -> bool:
        """
        Save state with optional encryption and signing (Week 10).

        This is the high-level API used by KeyManager, BackupManager, etc.
        Returns True on success, False on failure.
        """
        try:
            # Sign operation if signing enabled (Week 10: Operation Signatures)
            if self.signing_enabled:
                state.signature = self._sign_operation(state)
                state.signature_algorithm = 'RSA-4096'  # Current algorithm

            # Save (encrypted or plaintext)
            if self.encryption_enabled:
                return self._save_encrypted(state)
            else:
                self._save_to_json(state)
                return True
        except Exception as e:
            logger.error(f"Failed to save state {state.operation_id}: {e}")
            return False

    def load_state(self, operation_id: str) -> Optional[OperationState]:
        """
        Load state with automatic encrypted/unencrypted detection.

        Tries encrypted first, falls back to unencrypted.
        Supports migration from unencrypted to encrypted.

        Week 10: Verifies signatures if signing is enabled.
        """
        # Check cache first
        if operation_id in self._cache:
            cached = self._cache[operation_id]
            # Verify signature if signing enabled (Week 10)
            if self.signing_enabled and not self._verify_signature(cached):
                logger.error(f"Cached operation {operation_id} signature verification failed")
                return None
            return cached

        # Try encrypted format
        if self.encryption_enabled:
            encrypted_path = self.storage_dir / f"{operation_id}.encrypted"
            if encrypted_path.exists():
                state = self._load_encrypted(encrypted_path)
                if state:
                    # Verify signature if signing enabled (Week 10)
                    if self.signing_enabled and not self._verify_signature(state):
                        logger.error(f"Operation {operation_id} signature verification failed")
                        return None

                    self._cache[operation_id] = state
                    return state

        # Try unencrypted format (for migration or when encryption disabled)
        json_path = self.storage_dir / f"{operation_id}.json"
        if json_path.exists():
            state = self._load_from_json(json_path)
            if state:
                # Verify signature if present (Week 10)
                if self.signing_enabled and hasattr(state, 'signature') and state.signature:
                    if not self._verify_signature(state):
                        logger.error(f"Operation {operation_id} signature verification failed")
                        return None

                # Migrate to encrypted if encryption enabled
                if self.encryption_enabled:
                    logger.info(f"Migrating {operation_id} to encrypted format")
                    self._save_encrypted(state)
                    # Optionally remove old file
                    # json_path.unlink()

                self._cache[operation_id] = state
                return state

        # Try old subdirectory structure for backward compatibility
        json_path_old = self.json_dir / operation_id[:8] / f"{operation_id}.json"
        if json_path_old.exists():
            state = self._load_from_json(json_path_old)
            if state:
                self._cache[operation_id] = state
                return state

        # Try database as last resort
        return self.get_operation(operation_id)

    def _save_encrypted(self, state: OperationState) -> bool:
        """Save state with PQC encryption"""
        try:
            import pickle

            # Serialize state
            state_data = pickle.dumps(state.to_dict())

            # Encrypt
            ciphertext = self._encryption.encrypt(state_data, self._public_key)

            # Save to file
            encrypted_path = self._get_json_path(state.operation_id)
            # Ensure parent directory exists (but file goes directly in storage_dir)
            if not encrypted_path.parent.exists():
                encrypted_path.parent.mkdir(parents=True, exist_ok=True)
            encrypted_path.write_bytes(ciphertext)

            return True
        except Exception as e:
            logger.error(f"Encryption failed for {state.operation_id}: {e}")
            return False

    def _load_encrypted(self, path: Path) -> Optional[OperationState]:
        """Load encrypted state"""
        try:
            import pickle

            # Read encrypted data
            ciphertext = path.read_bytes()

            # Decrypt
            state_data = self._encryption.decrypt(ciphertext, self._private_key)

            # Deserialize
            data = pickle.loads(state_data)
            state = OperationState.from_dict(data)

            return state
        except Exception as e:
            logger.error(f"Decryption failed for {path}: {e}")
            return None

    def _load_from_json(self, path: Path) -> Optional[OperationState]:
        """Load unencrypted JSON state"""
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            return OperationState.from_dict(data)
        except Exception as e:
            logger.error(f"Failed to load JSON from {path}: {e}")
            return None


class CrashRecoveryManager:
    """Manages crash recovery for operations"""

    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager

    def recover_on_startup(self) -> List[OperationState]:
        """
        Recover from crash on system startup.

        Returns list of operations that were recovered (paused for resume).
        """
        recovered = []

        # Get all active operations
        active_ops = self.state_manager.get_active_operations()

        for state in active_ops:
            if state.resumable and len(state.checkpoint_data) > 0:
                # Mark as paused for resume
                state.status = OperationStatus.PAUSED
                self.state_manager.update_operation(state)
                recovered.append(state)
                logger.info(f"Recovered operation {state.operation_id} - paused for resume")

            else:
                # Non-resumable operation - mark as failed
                state.status = OperationStatus.FAILED
                state.error = "System crash - operation was not resumable"
                self.state_manager.update_operation(state)
                logger.info(f"Failed operation {state.operation_id} - not resumable")

        return recovered


if __name__ == "__main__":
    # Example usage
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create manager
        manager = StateManager(
            db_path=tmpdir / "test.db",
            json_dir=tmpdir / "json"
        )

        # Create operation
        state = manager.create_operation(
            user_query="install firefox",
            user_id="test_user",
            tags={'install', 'browser'}
        )

        print(f"Created operation: {state.operation_id}")
        print(f"Status: {state.status.value}")
        print(f"Layers: {len(state.layers)}")

        # Start layer
        state.start_layer(1, {'query': 'install firefox'})
        manager.update_operation(state)

        # Complete layer
        state.complete_layer(1, {'intent': 'install', 'package': 'firefox'})
        manager.update_operation(state)

        print(f"Progress: {state.get_progress_percent() * 100:.1f}%")

        # List operations
        ops = manager.list_operations(user_id="test_user")
        print(f"Found {len(ops)} operations for test_user")
