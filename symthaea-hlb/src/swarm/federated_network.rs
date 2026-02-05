//! Federated Network Communication Layer
//!
//! This module provides network communication primitives for federated CfC learning
//! across the Symthaea swarm. It supports both local channel-based simulation for
//! testing and a TCP backend stub for future real network deployment.
//!
//! # Architecture
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────────────────┐
//! │                      FEDERATED NETWORK LAYER                                 │
//! ├─────────────────────────────────────────────────────────────────────────────┤
//! │                                                                              │
//! │  ┌───────────────────────┐         ┌───────────────────────┐                │
//! │  │   FederatedNode       │         │   FederatedCoordinator│                │
//! │  │                       │         │                       │                │
//! │  │ • node_id (32 bytes)  │         │ • Node registry       │                │
//! │  │ • address (socket)    │    ────▶│ • Message routing     │                │
//! │  │ • trust_score         │         │ • Sync coordination   │                │
//! │  │ • local aggregator    │         │ • Heartbeat manager   │                │
//! │  └───────────────────────┘         └───────────────────────┘                │
//! │                                                                              │
//! │  ┌───────────────────────────────────────────────────────────────────────┐  │
//! │  │                      NetworkBackend (Trait)                            │  │
//! │  ├───────────────────────────────────────────────────────────────────────┤  │
//! │  │                                                                        │  │
//! │  │  ┌─────────────────────────┐    ┌─────────────────────────┐           │  │
//! │  │  │   LocalChannelBackend   │    │      TcpBackend        │           │  │
//! │  │  │   (Testing/Simulation)  │    │   (Future Real Net)    │           │  │
//! │  │  │                         │    │                         │           │  │
//! │  │  │ • Tokio MPSC channels   │    │ • TCP connections       │           │  │
//! │  │  │ • Zero latency          │    │ • Real network I/O      │           │  │
//! │  │  │ • Perfect reliability   │    │ • Timeout handling      │           │  │
//! │  │  └─────────────────────────┘    └─────────────────────────┘           │  │
//! │  └───────────────────────────────────────────────────────────────────────┘  │
//! └─────────────────────────────────────────────────────────────────────────────┘
//! ```
//!
//! # Example
//!
//! ```rust,ignore
//! use symthaea::swarm::federated_network::{
//!     FederatedCoordinator, FederatedNetworkConfig, LocalChannelBackend,
//! };
//!
//! // Create coordinator with 3 nodes
//! let config = FederatedNetworkConfig::default()
//!     .with_num_nodes(3)
//!     .with_sync_interval_ms(1000);
//!
//! let coordinator = FederatedCoordinator::new_with_backend(
//!     config,
//!     LocalChannelBackend::new(),
//! ).await?;
//!
//! // Run federated learning round
//! coordinator.run_sync_round().await?;
//! ```

use crate::swarm::federated_cfc::{
    DifferentialPrivacyConfig, FederatedAggregator, GradientMessage,
};
use async_trait::async_trait;
use parking_lot::RwLock;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::net::SocketAddr;
use std::sync::Arc;
use std::time::{Duration, SystemTime};
use tokio::sync::{broadcast, mpsc, oneshot};
use tracing::{debug, info, warn};

// ============================================================================
// CONFIGURATION
// ============================================================================

/// Configuration for the federated network
#[derive(Debug, Clone)]
pub struct FederatedNetworkConfig {
    /// Number of nodes in the federation
    pub num_nodes: usize,

    /// Interval between synchronization rounds (milliseconds)
    pub sync_interval_ms: u64,

    /// Timeout for network operations (milliseconds)
    pub timeout_ms: u64,

    /// Minimum number of nodes required for aggregation
    pub min_nodes_for_aggregation: usize,

    /// Enable differential privacy
    pub enable_dp: bool,

    /// Differential privacy configuration
    pub dp_config: Option<DifferentialPrivacyConfig>,

    /// Enable Byzantine fault tolerance
    pub enable_byzantine_tolerance: bool,

    /// Trim fraction for Byzantine tolerance (0.0 to 0.5)
    pub byzantine_trim_fraction: f32,

    /// Heartbeat interval (milliseconds)
    pub heartbeat_interval_ms: u64,

    /// Maximum staleness for gradients (milliseconds)
    pub max_gradient_staleness_ms: u64,
}

impl Default for FederatedNetworkConfig {
    fn default() -> Self {
        Self {
            num_nodes: 3,
            sync_interval_ms: 5000,
            timeout_ms: 10000,
            min_nodes_for_aggregation: 2,
            enable_dp: false,
            dp_config: None,
            enable_byzantine_tolerance: false,
            byzantine_trim_fraction: 0.1,
            heartbeat_interval_ms: 5000,
            max_gradient_staleness_ms: 60000,
        }
    }
}

impl FederatedNetworkConfig {
    /// Create a new config with specified number of nodes
    pub fn with_num_nodes(mut self, num_nodes: usize) -> Self {
        self.num_nodes = num_nodes;
        self.min_nodes_for_aggregation = (num_nodes / 2).max(1);
        self
    }

    /// Set the synchronization interval
    pub fn with_sync_interval_ms(mut self, interval_ms: u64) -> Self {
        self.sync_interval_ms = interval_ms;
        self
    }

    /// Set the network timeout
    pub fn with_timeout_ms(mut self, timeout_ms: u64) -> Self {
        self.timeout_ms = timeout_ms;
        self
    }

    /// Enable differential privacy with the given config
    pub fn with_differential_privacy(mut self, config: DifferentialPrivacyConfig) -> Self {
        self.enable_dp = true;
        self.dp_config = Some(config);
        self
    }

    /// Enable Byzantine fault tolerance
    pub fn with_byzantine_tolerance(mut self, trim_fraction: f32) -> Self {
        self.enable_byzantine_tolerance = true;
        self.byzantine_trim_fraction = trim_fraction.clamp(0.0, 0.5);
        self
    }

    /// Create a config for testing (fast timeouts, small network)
    pub fn for_testing() -> Self {
        Self {
            num_nodes: 3,
            sync_interval_ms: 100,
            timeout_ms: 1000,
            min_nodes_for_aggregation: 2,
            enable_dp: false,
            dp_config: None,
            enable_byzantine_tolerance: false,
            byzantine_trim_fraction: 0.1,
            heartbeat_interval_ms: 500,
            max_gradient_staleness_ms: 5000,
        }
    }
}

// ============================================================================
// MESSAGE TYPES
// ============================================================================

/// Messages exchanged in the federated network
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum FederatedMessage {
    /// Share gradient data with the network
    GradientShare(GradientMessage),

    /// Broadcast aggregated model update
    ModelUpdate {
        /// Aggregated weights
        weights: Vec<f32>,
        /// Round number
        round: u64,
        /// Source node ID
        source_id: [u8; 32],
        /// Timestamp
        timestamp: u64,
    },

    /// Heartbeat to indicate node is alive
    Heartbeat {
        /// Source node ID
        node_id: [u8; 32],
        /// Current round number
        round: u64,
        /// Node's trust score
        trust_score: f32,
        /// Timestamp
        timestamp: u64,
    },

    /// Request to join the federation
    JoinRequest {
        /// Node ID
        node_id: [u8; 32],
        /// Node's address
        address: String,
        /// Initial trust score
        trust_score: f32,
    },

    /// Acknowledgment of join request
    JoinAck {
        /// Accepted node ID
        node_id: [u8; 32],
        /// Current round number
        current_round: u64,
        /// List of known peers
        peers: Vec<([u8; 32], String)>,
    },

    /// Node is leaving the federation
    Leave {
        /// Node ID
        node_id: [u8; 32],
        /// Reason for leaving
        reason: String,
    },

    /// Request current model weights from coordinator
    SyncRequest {
        /// Node ID
        node_id: [u8; 32],
        /// Last known round
        last_round: u64,
    },

    /// Response with current model weights
    SyncResponse {
        /// Current weights
        weights: Vec<f32>,
        /// Current round
        round: u64,
    },
}

impl FederatedMessage {
    /// Get the message type as a string for logging
    pub fn message_type(&self) -> &'static str {
        match self {
            Self::GradientShare(_) => "GradientShare",
            Self::ModelUpdate { .. } => "ModelUpdate",
            Self::Heartbeat { .. } => "Heartbeat",
            Self::JoinRequest { .. } => "JoinRequest",
            Self::JoinAck { .. } => "JoinAck",
            Self::Leave { .. } => "Leave",
            Self::SyncRequest { .. } => "SyncRequest",
            Self::SyncResponse { .. } => "SyncResponse",
        }
    }

    /// Get the source node ID if available
    pub fn source_node_id(&self) -> Option<[u8; 32]> {
        match self {
            Self::GradientShare(g) => Some(g.source_id),
            Self::ModelUpdate { source_id, .. } => Some(*source_id),
            Self::Heartbeat { node_id, .. } => Some(*node_id),
            Self::JoinRequest { node_id, .. } => Some(*node_id),
            Self::JoinAck { node_id, .. } => Some(*node_id),
            Self::Leave { node_id, .. } => Some(*node_id),
            Self::SyncRequest { node_id, .. } => Some(*node_id),
            Self::SyncResponse { .. } => None,
        }
    }
}

// ============================================================================
// FEDERATED NODE
// ============================================================================

/// A node in the federated network
#[derive(Debug, Clone)]
pub struct FederatedNode {
    /// Unique 32-byte identifier for this node
    pub node_id: [u8; 32],

    /// Network address for this node
    pub address: NodeAddress,

    /// Trust score from the network (0.0 to 1.0)
    pub trust_score: f32,

    /// Last heartbeat timestamp
    pub last_heartbeat: u64,

    /// Current synchronization round
    pub current_round: u64,

    /// Whether this node is active
    pub is_active: bool,
}

/// Address of a node (can be socket address or channel identifier)
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub enum NodeAddress {
    /// Socket address for TCP connections
    Socket(SocketAddr),

    /// Channel identifier for local simulation
    Channel(String),

    /// Placeholder for unassigned address
    Unassigned,
}

impl std::fmt::Display for NodeAddress {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Socket(addr) => write!(f, "tcp://{}", addr),
            Self::Channel(id) => write!(f, "channel://{}", id),
            Self::Unassigned => write!(f, "unassigned"),
        }
    }
}

impl FederatedNode {
    /// Create a new federated node
    pub fn new(node_id: [u8; 32], address: NodeAddress) -> Self {
        let timestamp = SystemTime::now()
            .duration_since(SystemTime::UNIX_EPOCH)
            .map(|d| d.as_millis() as u64)
            .unwrap_or(0);

        Self {
            node_id,
            address,
            trust_score: 0.5, // Default trust
            last_heartbeat: timestamp,
            current_round: 0,
            is_active: true,
        }
    }

    /// Create a node with a generated random ID
    pub fn with_random_id(address: NodeAddress) -> Self {
        let mut node_id = [0u8; 32];
        let mut rng = rand::thread_rng();
        rand::Rng::fill(&mut rng, &mut node_id);
        Self::new(node_id, address)
    }

    /// Get hex-encoded short ID (first 8 bytes)
    pub fn short_id(&self) -> String {
        hex::encode(&self.node_id[..8])
    }

    /// Update heartbeat timestamp
    pub fn update_heartbeat(&mut self) {
        self.last_heartbeat = SystemTime::now()
            .duration_since(SystemTime::UNIX_EPOCH)
            .map(|d| d.as_millis() as u64)
            .unwrap_or(0);
    }

    /// Check if node is stale (no heartbeat in given duration)
    pub fn is_stale(&self, max_staleness_ms: u64) -> bool {
        let now = SystemTime::now()
            .duration_since(SystemTime::UNIX_EPOCH)
            .map(|d| d.as_millis() as u64)
            .unwrap_or(0);

        now.saturating_sub(self.last_heartbeat) > max_staleness_ms
    }
}

// ============================================================================
// NETWORK BACKEND TRAIT
// ============================================================================

/// Result type for network operations
pub type NetworkResult<T> = Result<T, NetworkError>;

/// Errors that can occur in network operations
#[derive(Debug)]
pub enum NetworkError {
    /// Timeout waiting for response
    Timeout { operation: String, timeout_ms: u64 },

    /// Connection failed
    ConnectionFailed { target: String, reason: String },

    /// Channel closed
    ChannelClosed { reason: String },

    /// Send failed
    SendFailed { reason: String },

    /// Receive failed
    ReceiveFailed { reason: String },

    /// Node not found
    NodeNotFound { node_id: String },

    /// Serialization error
    Serialization { reason: String },

    /// Internal error
    Internal { reason: String },
}

impl std::fmt::Display for NetworkError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Timeout {
                operation,
                timeout_ms,
            } => {
                write!(f, "Timeout after {}ms: {}", timeout_ms, operation)
            }
            Self::ConnectionFailed { target, reason } => {
                write!(f, "Connection to {} failed: {}", target, reason)
            }
            Self::ChannelClosed { reason } => {
                write!(f, "Channel closed: {}", reason)
            }
            Self::SendFailed { reason } => {
                write!(f, "Send failed: {}", reason)
            }
            Self::ReceiveFailed { reason } => {
                write!(f, "Receive failed: {}", reason)
            }
            Self::NodeNotFound { node_id } => {
                write!(f, "Node not found: {}", node_id)
            }
            Self::Serialization { reason } => {
                write!(f, "Serialization error: {}", reason)
            }
            Self::Internal { reason } => {
                write!(f, "Internal error: {}", reason)
            }
        }
    }
}

impl std::error::Error for NetworkError {}

/// Trait for network communication backends
///
/// This abstraction allows swapping between local channels (for testing)
/// and real network protocols (TCP, QUIC) for production.
#[async_trait]
pub trait NetworkBackend: Send + Sync {
    /// Send a message to a specific node
    async fn send(&self, target: &NodeAddress, message: FederatedMessage) -> NetworkResult<()>;

    /// Broadcast a message to all known nodes
    async fn broadcast(&self, message: FederatedMessage) -> NetworkResult<usize>;

    /// Receive the next message (blocking with timeout)
    async fn receive(&self, timeout: Duration) -> NetworkResult<(NodeAddress, FederatedMessage)>;

    /// Register a new node with the backend
    async fn register_node(&self, node: &FederatedNode) -> NetworkResult<()>;

    /// Unregister a node from the backend
    async fn unregister_node(&self, node_id: &[u8; 32]) -> NetworkResult<()>;

    /// Get the local node's address
    fn local_address(&self) -> NodeAddress;

    /// Check if backend is connected/ready
    fn is_ready(&self) -> bool;
}

// ============================================================================
// LOCAL CHANNEL BACKEND
// ============================================================================

/// Message wrapper with source address for channel routing
pub struct ChannelEnvelope {
    source: NodeAddress,
    message: FederatedMessage,
}

/// Local channel-based backend for testing and simulation
///
/// This backend uses Tokio MPSC channels to simulate network communication
/// between nodes in the same process. It's ideal for:
/// - Unit and integration tests
/// - Development and debugging
/// - Performance benchmarks without network overhead
pub struct LocalChannelBackend {
    /// Local node's identifier
    local_id: String,

    /// Senders for each registered node
    senders: Arc<RwLock<HashMap<String, mpsc::Sender<ChannelEnvelope>>>>,

    /// Receiver for incoming messages
    receiver: Arc<tokio::sync::Mutex<mpsc::Receiver<ChannelEnvelope>>>,

    /// Our own sender (for others to send to us)
    self_sender: mpsc::Sender<ChannelEnvelope>,

    /// Whether the backend is initialized
    ready: Arc<std::sync::atomic::AtomicBool>,
}

impl LocalChannelBackend {
    /// Create a new local channel backend
    pub fn new() -> Self {
        Self::with_id(format!("node-{}", rand::random::<u32>()))
    }

    /// Create a new local channel backend with a specific ID
    pub fn with_id(id: String) -> Self {
        let (tx, rx) = mpsc::channel(1000);

        Self {
            local_id: id,
            senders: Arc::new(RwLock::new(HashMap::new())),
            receiver: Arc::new(tokio::sync::Mutex::new(rx)),
            self_sender: tx,
            ready: Arc::new(std::sync::atomic::AtomicBool::new(true)),
        }
    }

    /// Get a sender for this backend (for other nodes to register)
    pub fn get_sender(&self) -> mpsc::Sender<ChannelEnvelope> {
        self.self_sender.clone()
    }

    /// Register another node's sender with this backend
    pub fn register_peer_sender(&self, node_id: &str, sender: mpsc::Sender<ChannelEnvelope>) {
        self.senders.write().insert(node_id.to_string(), sender);
    }

    /// Get the local ID
    pub fn local_id(&self) -> &str {
        &self.local_id
    }
}

impl Default for LocalChannelBackend {
    fn default() -> Self {
        Self::new()
    }
}

#[async_trait]
impl NetworkBackend for LocalChannelBackend {
    async fn send(&self, target: &NodeAddress, message: FederatedMessage) -> NetworkResult<()> {
        let target_id = match target {
            NodeAddress::Channel(id) => id.clone(),
            _ => {
                return Err(NetworkError::SendFailed {
                    reason: "LocalChannelBackend only supports Channel addresses".to_string(),
                })
            }
        };

        let sender = self.senders.read().get(&target_id).cloned();

        match sender {
            Some(tx) => {
                let envelope = ChannelEnvelope {
                    source: NodeAddress::Channel(self.local_id.clone()),
                    message,
                };

                tx.send(envelope)
                    .await
                    .map_err(|_| NetworkError::ChannelClosed {
                        reason: format!("Channel to {} closed", target_id),
                    })?;

                Ok(())
            }
            None => Err(NetworkError::NodeNotFound { node_id: target_id }),
        }
    }

    async fn broadcast(&self, message: FederatedMessage) -> NetworkResult<usize> {
        let senders: Vec<(String, mpsc::Sender<ChannelEnvelope>)> = self
            .senders
            .read()
            .iter()
            .map(|(k, v)| (k.clone(), v.clone()))
            .collect();

        let mut sent_count = 0;

        for (node_id, tx) in senders {
            let envelope = ChannelEnvelope {
                source: NodeAddress::Channel(self.local_id.clone()),
                message: message.clone(),
            };

            if tx.send(envelope).await.is_ok() {
                sent_count += 1;
            } else {
                debug!("Failed to send to {}", node_id);
            }
        }

        Ok(sent_count)
    }

    async fn receive(&self, timeout: Duration) -> NetworkResult<(NodeAddress, FederatedMessage)> {
        let mut rx = self.receiver.lock().await;

        match tokio::time::timeout(timeout, rx.recv()).await {
            Ok(Some(envelope)) => Ok((envelope.source, envelope.message)),
            Ok(None) => Err(NetworkError::ChannelClosed {
                reason: "Receiver channel closed".to_string(),
            }),
            Err(_) => Err(NetworkError::Timeout {
                operation: "receive".to_string(),
                timeout_ms: timeout.as_millis() as u64,
            }),
        }
    }

    async fn register_node(&self, node: &FederatedNode) -> NetworkResult<()> {
        // For local channels, registration happens via register_peer_sender
        debug!("Node registration requested for {}", node.short_id());
        Ok(())
    }

    async fn unregister_node(&self, node_id: &[u8; 32]) -> NetworkResult<()> {
        let short_id = hex::encode(&node_id[..8]);
        self.senders.write().remove(&short_id);
        debug!("Node {} unregistered", short_id);
        Ok(())
    }

    fn local_address(&self) -> NodeAddress {
        NodeAddress::Channel(self.local_id.clone())
    }

    fn is_ready(&self) -> bool {
        self.ready.load(std::sync::atomic::Ordering::SeqCst)
    }
}

// ============================================================================
// TCP BACKEND STUB
// ============================================================================

/// TCP-based backend for real network communication (stub for future implementation)
///
/// This is a placeholder that will be implemented when real network
/// communication is needed. For now, it returns errors for all operations.
#[allow(dead_code)]
pub struct TcpBackend {
    /// Local bind address
    local_addr: SocketAddr,

    /// Connection pool (placeholder)
    connections: Arc<RwLock<HashMap<SocketAddr, ()>>>,

    /// Whether the backend is initialized
    ready: Arc<std::sync::atomic::AtomicBool>,
}

impl TcpBackend {
    /// Create a new TCP backend (stub)
    #[allow(dead_code)]
    pub fn new(bind_addr: SocketAddr) -> Self {
        Self {
            local_addr: bind_addr,
            connections: Arc::new(RwLock::new(HashMap::new())),
            ready: Arc::new(std::sync::atomic::AtomicBool::new(false)),
        }
    }
}

#[async_trait]
impl NetworkBackend for TcpBackend {
    async fn send(&self, _target: &NodeAddress, _message: FederatedMessage) -> NetworkResult<()> {
        Err(NetworkError::Internal {
            reason: "TcpBackend not yet implemented".to_string(),
        })
    }

    async fn broadcast(&self, _message: FederatedMessage) -> NetworkResult<usize> {
        Err(NetworkError::Internal {
            reason: "TcpBackend not yet implemented".to_string(),
        })
    }

    async fn receive(&self, _timeout: Duration) -> NetworkResult<(NodeAddress, FederatedMessage)> {
        Err(NetworkError::Internal {
            reason: "TcpBackend not yet implemented".to_string(),
        })
    }

    async fn register_node(&self, _node: &FederatedNode) -> NetworkResult<()> {
        Err(NetworkError::Internal {
            reason: "TcpBackend not yet implemented".to_string(),
        })
    }

    async fn unregister_node(&self, _node_id: &[u8; 32]) -> NetworkResult<()> {
        Err(NetworkError::Internal {
            reason: "TcpBackend not yet implemented".to_string(),
        })
    }

    fn local_address(&self) -> NodeAddress {
        NodeAddress::Socket(self.local_addr)
    }

    fn is_ready(&self) -> bool {
        self.ready.load(std::sync::atomic::Ordering::SeqCst)
    }
}

// ============================================================================
// FEDERATED COORDINATOR
// ============================================================================

/// Statistics about the federated network
#[derive(Debug, Clone, Default)]
pub struct CoordinatorStats {
    /// Number of active nodes
    pub active_nodes: usize,

    /// Current synchronization round
    pub current_round: u64,

    /// Total gradients received
    pub gradients_received: u64,

    /// Total model updates broadcast
    pub model_updates_broadcast: u64,

    /// Total heartbeats received
    pub heartbeats_received: u64,

    /// Number of failed send attempts
    pub send_failures: u64,

    /// Uptime in seconds
    pub uptime_seconds: u64,
}

/// Event broadcast by the coordinator
#[derive(Debug, Clone)]
pub enum CoordinatorEvent {
    /// New node joined
    NodeJoined {
        node_id: [u8; 32],
        address: NodeAddress,
    },

    /// Node left or was removed
    NodeLeft { node_id: [u8; 32], reason: String },

    /// Synchronization round completed
    RoundCompleted { round: u64, participants: usize },

    /// Model updated
    ModelUpdated { round: u64, weights_dim: usize },

    /// Error occurred
    Error { message: String },
}

/// Coordinator for federated learning across multiple nodes
///
/// The coordinator manages:
/// - Node registration and heartbeat monitoring
/// - Gradient collection and aggregation
/// - Model update broadcasting
/// - Synchronization rounds
pub struct FederatedCoordinator {
    /// Configuration
    config: FederatedNetworkConfig,

    /// Network backend
    backend: Arc<dyn NetworkBackend>,

    /// Local node information
    local_node: Arc<RwLock<FederatedNode>>,

    /// Known peer nodes
    peers: Arc<RwLock<HashMap<[u8; 32], FederatedNode>>>,

    /// Federated aggregator for gradient processing
    aggregator: Arc<RwLock<FederatedAggregator>>,

    /// Current round number
    current_round: Arc<std::sync::atomic::AtomicU64>,

    /// Statistics
    stats: Arc<RwLock<CoordinatorStats>>,

    /// Event broadcaster
    event_tx: broadcast::Sender<CoordinatorEvent>,

    /// Start time
    start_time: std::time::Instant,

    /// Running flag
    running: Arc<std::sync::atomic::AtomicBool>,

    /// Shutdown signal sender
    shutdown_tx: Option<oneshot::Sender<()>>,
}

impl FederatedCoordinator {
    /// Create a new coordinator with a local channel backend (for testing)
    pub async fn new(config: FederatedNetworkConfig, initial_weights: Vec<f32>) -> Self {
        Self::new_with_backend(
            config,
            initial_weights,
            Arc::new(LocalChannelBackend::new()),
        )
        .await
    }

    /// Create a new coordinator with a specific backend
    pub async fn new_with_backend(
        config: FederatedNetworkConfig,
        initial_weights: Vec<f32>,
        backend: Arc<dyn NetworkBackend>,
    ) -> Self {
        let (event_tx, _) = broadcast::channel(100);
        let (shutdown_tx, _shutdown_rx) = oneshot::channel();

        // Create local node
        let local_node = FederatedNode::with_random_id(backend.local_address());

        // Create aggregator with optional DP and Byzantine tolerance
        let mut aggregator = FederatedAggregator::new(initial_weights)
            .with_source_id(local_node.node_id)
            .with_max_staleness(config.max_gradient_staleness_ms);

        if config.enable_dp {
            if let Some(dp_config) = config.dp_config.clone() {
                aggregator = aggregator.with_differential_privacy(dp_config);
            }
        }

        if config.enable_byzantine_tolerance {
            aggregator = aggregator.with_byzantine_tolerance(config.byzantine_trim_fraction);
        }

        Self {
            config,
            backend,
            local_node: Arc::new(RwLock::new(local_node)),
            peers: Arc::new(RwLock::new(HashMap::new())),
            aggregator: Arc::new(RwLock::new(aggregator)),
            current_round: Arc::new(std::sync::atomic::AtomicU64::new(0)),
            stats: Arc::new(RwLock::new(CoordinatorStats::default())),
            event_tx,
            start_time: std::time::Instant::now(),
            running: Arc::new(std::sync::atomic::AtomicBool::new(true)),
            shutdown_tx: Some(shutdown_tx),
        }
    }

    /// Get the local node ID
    pub fn local_node_id(&self) -> [u8; 32] {
        self.local_node.read().node_id
    }

    /// Get the local node's short ID
    pub fn local_short_id(&self) -> String {
        self.local_node.read().short_id()
    }

    /// Subscribe to coordinator events
    pub fn subscribe_events(&self) -> broadcast::Receiver<CoordinatorEvent> {
        self.event_tx.subscribe()
    }

    /// Get current statistics
    pub fn stats(&self) -> CoordinatorStats {
        let mut stats = self.stats.read().clone();
        stats.uptime_seconds = self.start_time.elapsed().as_secs();
        stats.active_nodes = self.peers.read().len();
        stats.current_round = self.current_round.load(std::sync::atomic::Ordering::SeqCst);
        stats
    }

    /// Get current round number
    pub fn current_round(&self) -> u64 {
        self.current_round.load(std::sync::atomic::Ordering::SeqCst)
    }

    /// Get number of active peers
    pub fn peer_count(&self) -> usize {
        self.peers.read().len()
    }

    /// Get current model weights
    pub fn get_weights(&self) -> Vec<f32> {
        self.aggregator.read().local_weights().to_vec()
    }

    /// Update local model weights
    pub fn update_weights(&self, weights: Vec<f32>) {
        self.aggregator.write().update_local_weights(weights);
    }

    /// Register a peer node
    pub fn register_peer(&self, node: FederatedNode) {
        let node_id = node.node_id;
        let address = node.address.clone();

        self.peers.write().insert(node_id, node);

        info!("Peer registered: {}", hex::encode(&node_id[..8]));

        let _ = self
            .event_tx
            .send(CoordinatorEvent::NodeJoined { node_id, address });
    }

    /// Unregister a peer node
    pub fn unregister_peer(&self, node_id: &[u8; 32], reason: &str) {
        if self.peers.write().remove(node_id).is_some() {
            info!(
                "Peer unregistered: {} ({})",
                hex::encode(&node_id[..8]),
                reason
            );

            let _ = self.event_tx.send(CoordinatorEvent::NodeLeft {
                node_id: *node_id,
                reason: reason.to_string(),
            });
        }
    }

    /// Process an incoming message
    pub async fn process_message(
        &self,
        source: NodeAddress,
        message: FederatedMessage,
    ) -> NetworkResult<()> {
        debug!("Processing {} from {}", message.message_type(), source);

        match message {
            FederatedMessage::GradientShare(gradient) => {
                self.handle_gradient_share(gradient).await?;
            }
            FederatedMessage::Heartbeat {
                node_id,
                round,
                trust_score,
                timestamp,
            } => {
                self.handle_heartbeat(node_id, round, trust_score, timestamp);
            }
            FederatedMessage::JoinRequest {
                node_id,
                address,
                trust_score,
            } => {
                self.handle_join_request(node_id, address, trust_score)
                    .await?;
            }
            FederatedMessage::SyncRequest {
                node_id,
                last_round,
            } => {
                self.handle_sync_request(source, node_id, last_round)
                    .await?;
            }
            FederatedMessage::Leave { node_id, reason } => {
                self.unregister_peer(&node_id, &reason);
            }
            FederatedMessage::ModelUpdate { weights, round, .. } => {
                self.handle_model_update(weights, round).await?;
            }
            _ => {
                debug!("Ignoring message type: {}", message.message_type());
            }
        }

        Ok(())
    }

    /// Handle incoming gradient share
    async fn handle_gradient_share(&self, gradient: GradientMessage) -> NetworkResult<()> {
        debug!(
            "Received gradient from {}",
            hex::encode(&gradient.source_id[..8])
        );

        let accepted = self.aggregator.write().receive_gradient(gradient);

        if accepted {
            self.stats.write().gradients_received += 1;
        }

        Ok(())
    }

    /// Handle heartbeat from a peer
    fn handle_heartbeat(&self, node_id: [u8; 32], round: u64, trust_score: f32, _timestamp: u64) {
        if let Some(peer) = self.peers.write().get_mut(&node_id) {
            peer.update_heartbeat();
            peer.current_round = round;
            peer.trust_score = trust_score;
        }

        self.stats.write().heartbeats_received += 1;
    }

    /// Handle join request
    async fn handle_join_request(
        &self,
        node_id: [u8; 32],
        address: String,
        trust_score: f32,
    ) -> NetworkResult<()> {
        let node = FederatedNode {
            node_id,
            address: NodeAddress::Channel(address.clone()),
            trust_score,
            last_heartbeat: SystemTime::now()
                .duration_since(SystemTime::UNIX_EPOCH)
                .map(|d| d.as_millis() as u64)
                .unwrap_or(0),
            current_round: 0,
            is_active: true,
        };

        self.register_peer(node);

        // Send acknowledgment
        let peers: Vec<([u8; 32], String)> = self
            .peers
            .read()
            .iter()
            .map(|(id, n)| (*id, n.address.to_string()))
            .collect();

        let ack = FederatedMessage::JoinAck {
            node_id,
            current_round: self.current_round(),
            peers,
        };

        self.backend
            .send(&NodeAddress::Channel(address), ack)
            .await?;

        Ok(())
    }

    /// Handle sync request
    async fn handle_sync_request(
        &self,
        source: NodeAddress,
        _node_id: [u8; 32],
        _last_round: u64,
    ) -> NetworkResult<()> {
        let response = FederatedMessage::SyncResponse {
            weights: self.get_weights(),
            round: self.current_round(),
        };

        self.backend.send(&source, response).await?;

        Ok(())
    }

    /// Handle model update from coordinator
    async fn handle_model_update(&self, weights: Vec<f32>, round: u64) -> NetworkResult<()> {
        if round > self.current_round() {
            self.update_weights(weights);
            self.current_round
                .store(round, std::sync::atomic::Ordering::SeqCst);

            let _ = self.event_tx.send(CoordinatorEvent::ModelUpdated {
                round,
                weights_dim: self.get_weights().len(),
            });
        }

        Ok(())
    }

    /// Share local gradient with all peers
    pub async fn share_gradient(&self, noise_scale: f32) -> NetworkResult<usize> {
        let gradient = self.aggregator.read().export_local_gradient(noise_scale);
        let message = FederatedMessage::GradientShare(gradient);

        let sent = self.backend.broadcast(message).await?;

        debug!("Shared gradient with {} peers", sent);
        Ok(sent)
    }

    /// Send heartbeat to all peers
    pub async fn send_heartbeat(&self) -> NetworkResult<usize> {
        let local_node = self.local_node.read().clone();

        let message = FederatedMessage::Heartbeat {
            node_id: local_node.node_id,
            round: self.current_round(),
            trust_score: local_node.trust_score,
            timestamp: SystemTime::now()
                .duration_since(SystemTime::UNIX_EPOCH)
                .map(|d| d.as_millis() as u64)
                .unwrap_or(0),
        };

        self.backend.broadcast(message).await
    }

    /// Run a single synchronization round
    ///
    /// This collects gradients from peers, aggregates them, and broadcasts
    /// the updated model.
    pub async fn run_sync_round(&self) -> NetworkResult<Option<Vec<f32>>> {
        let round = self
            .current_round
            .fetch_add(1, std::sync::atomic::Ordering::SeqCst)
            + 1;

        info!("Starting sync round {}", round);

        // Check if we have enough peers
        let peer_count = self.peer_count();
        if peer_count < self.config.min_nodes_for_aggregation.saturating_sub(1) {
            warn!(
                "Not enough peers for aggregation ({}/{})",
                peer_count, self.config.min_nodes_for_aggregation
            );
            return Ok(None);
        }

        // Share our gradient
        let noise_scale = if self.config.enable_dp {
            self.config
                .dp_config
                .as_ref()
                .map(|c| c.sigma() as f32)
                .unwrap_or(0.0)
        } else {
            0.0
        };

        self.share_gradient(noise_scale).await?;

        // Wait for gradients from peers (with timeout)
        let timeout = Duration::from_millis(self.config.timeout_ms);
        let deadline = std::time::Instant::now() + timeout;

        while std::time::Instant::now() < deadline {
            // Check if we have enough contributions
            if self.aggregator.read().pending_contributions()
                >= self.config.min_nodes_for_aggregation
            {
                break;
            }

            // Try to receive a message
            match self.backend.receive(Duration::from_millis(100)).await {
                Ok((source, message)) => {
                    if let Err(e) = self.process_message(source, message).await {
                        warn!("Error processing message: {}", e);
                    }
                }
                Err(NetworkError::Timeout { .. }) => {
                    // Continue waiting
                }
                Err(e) => {
                    warn!("Error receiving message: {}", e);
                }
            }
        }

        // Perform aggregation
        let aggregated = self.aggregator.write().aggregate();

        if let Some(ref new_weights) = aggregated {
            // Apply aggregated gradient
            self.aggregator.write().apply_gradient(new_weights, 0.1);

            // Broadcast updated model
            let local_node = self.local_node.read();
            let update_msg = FederatedMessage::ModelUpdate {
                weights: self.get_weights(),
                round,
                source_id: local_node.node_id,
                timestamp: SystemTime::now()
                    .duration_since(SystemTime::UNIX_EPOCH)
                    .map(|d| d.as_millis() as u64)
                    .unwrap_or(0),
            };

            self.backend.broadcast(update_msg).await?;
            self.stats.write().model_updates_broadcast += 1;

            // Emit event
            let _ = self.event_tx.send(CoordinatorEvent::RoundCompleted {
                round,
                participants: peer_count + 1,
            });

            info!(
                "Round {} completed with {} participants",
                round,
                peer_count + 1
            );
        }

        Ok(aggregated)
    }

    /// Shutdown the coordinator
    pub async fn shutdown(&mut self) {
        self.running
            .store(false, std::sync::atomic::Ordering::SeqCst);

        // Send leave message to all peers
        let local_node = self.local_node.read().clone();
        let leave_msg = FederatedMessage::Leave {
            node_id: local_node.node_id,
            reason: "Coordinator shutdown".to_string(),
        };

        let _ = self.backend.broadcast(leave_msg).await;

        // Take and drop the shutdown sender
        if let Some(tx) = self.shutdown_tx.take() {
            let _ = tx.send(());
        }

        info!("Coordinator shutdown complete");
    }
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/// Create a fully connected local channel network for testing
///
/// Returns a vector of coordinators that can communicate with each other.
pub async fn create_test_network(
    num_nodes: usize,
    weights_dim: usize,
) -> Vec<FederatedCoordinator> {
    let config = FederatedNetworkConfig::for_testing().with_num_nodes(num_nodes);
    let initial_weights = vec![0.0f32; weights_dim];

    // Create backends first
    let backends: Vec<Arc<LocalChannelBackend>> = (0..num_nodes)
        .map(|i| Arc::new(LocalChannelBackend::with_id(format!("node-{}", i))))
        .collect();

    // Cross-register all backends
    for i in 0..num_nodes {
        for j in 0..num_nodes {
            if i != j {
                backends[i].register_peer_sender(backends[j].local_id(), backends[j].get_sender());
            }
        }
    }

    // Create coordinators
    let mut coordinators = Vec::new();
    for backend in backends {
        let coordinator = FederatedCoordinator::new_with_backend(
            config.clone(),
            initial_weights.clone(),
            backend,
        )
        .await;
        coordinators.push(coordinator);
    }

    // Register peers with each other
    for i in 0..num_nodes {
        for j in 0..num_nodes {
            if i != j {
                let peer_node = FederatedNode::new(
                    coordinators[j].local_node_id(),
                    NodeAddress::Channel(format!("node-{}", j)),
                );
                coordinators[i].register_peer(peer_node);
            }
        }
    }

    coordinators
}

// ============================================================================
// TESTS
// ============================================================================

#[cfg(test)]
mod tests {
    use super::*;

    // =========================================================================
    // Configuration Tests
    // =========================================================================

    #[test]
    fn test_config_default() {
        let config = FederatedNetworkConfig::default();
        assert_eq!(config.num_nodes, 3);
        assert_eq!(config.sync_interval_ms, 5000);
        assert_eq!(config.timeout_ms, 10000);
        assert!(!config.enable_dp);
        assert!(!config.enable_byzantine_tolerance);
    }

    #[test]
    fn test_config_with_num_nodes() {
        let config = FederatedNetworkConfig::default().with_num_nodes(5);
        assert_eq!(config.num_nodes, 5);
        assert_eq!(config.min_nodes_for_aggregation, 2);
    }

    #[test]
    fn test_config_with_dp() {
        let config = FederatedNetworkConfig::default()
            .with_differential_privacy(DifferentialPrivacyConfig::moderate_privacy());
        assert!(config.enable_dp);
        assert!(config.dp_config.is_some());
    }

    #[test]
    fn test_config_for_testing() {
        let config = FederatedNetworkConfig::for_testing();
        assert_eq!(config.sync_interval_ms, 100);
        assert_eq!(config.timeout_ms, 1000);
    }

    // =========================================================================
    // Message Tests
    // =========================================================================

    #[test]
    fn test_message_types() {
        let gradient = GradientMessage::new([0u8; 32], vec![0.1; 10], 0.8);
        let msg = FederatedMessage::GradientShare(gradient);
        assert_eq!(msg.message_type(), "GradientShare");

        let msg = FederatedMessage::Heartbeat {
            node_id: [0u8; 32],
            round: 1,
            trust_score: 0.9,
            timestamp: 0,
        };
        assert_eq!(msg.message_type(), "Heartbeat");
    }

    #[test]
    fn test_message_source_node_id() {
        let gradient = GradientMessage::new([1u8; 32], vec![0.1; 10], 0.8);
        let msg = FederatedMessage::GradientShare(gradient);
        assert_eq!(msg.source_node_id(), Some([1u8; 32]));

        let msg = FederatedMessage::SyncResponse {
            weights: vec![],
            round: 0,
        };
        assert_eq!(msg.source_node_id(), None);
    }

    // =========================================================================
    // Node Tests
    // =========================================================================

    #[test]
    fn test_node_creation() {
        let node = FederatedNode::new([0u8; 32], NodeAddress::Unassigned);
        assert_eq!(node.node_id, [0u8; 32]);
        assert_eq!(node.trust_score, 0.5);
        assert!(node.is_active);
    }

    #[test]
    fn test_node_with_random_id() {
        let node = FederatedNode::with_random_id(NodeAddress::Unassigned);
        assert!(node.node_id != [0u8; 32]);
    }

    #[test]
    fn test_node_short_id() {
        let mut id = [0u8; 32];
        id[0] = 0xAB;
        id[1] = 0xCD;
        let node = FederatedNode::new(id, NodeAddress::Unassigned);
        assert_eq!(node.short_id().len(), 16);
        assert!(node.short_id().starts_with("abcd"));
    }

    #[test]
    fn test_node_staleness() {
        let mut node = FederatedNode::new([0u8; 32], NodeAddress::Unassigned);
        assert!(!node.is_stale(60000)); // Not stale within 1 minute

        // Set heartbeat to past
        node.last_heartbeat = 0;
        assert!(node.is_stale(60000)); // Should be stale now
    }

    // =========================================================================
    // Node Address Tests
    // =========================================================================

    #[test]
    fn test_node_address_display() {
        let addr = NodeAddress::Channel("test-123".to_string());
        assert_eq!(format!("{}", addr), "channel://test-123");

        let socket_addr: SocketAddr = "127.0.0.1:8080".parse().unwrap();
        let addr = NodeAddress::Socket(socket_addr);
        assert_eq!(format!("{}", addr), "tcp://127.0.0.1:8080");

        let addr = NodeAddress::Unassigned;
        assert_eq!(format!("{}", addr), "unassigned");
    }

    // =========================================================================
    // Local Channel Backend Tests
    // =========================================================================

    #[tokio::test]
    async fn test_local_backend_creation() {
        let backend = LocalChannelBackend::new();
        assert!(backend.is_ready());
        assert!(matches!(backend.local_address(), NodeAddress::Channel(_)));
    }

    #[tokio::test]
    async fn test_local_backend_with_id() {
        let backend = LocalChannelBackend::with_id("my-node".to_string());
        assert_eq!(backend.local_id(), "my-node");
    }

    #[tokio::test]
    async fn test_local_backend_send_to_unknown() {
        let backend = LocalChannelBackend::new();
        let result = backend
            .send(
                &NodeAddress::Channel("unknown".to_string()),
                FederatedMessage::Heartbeat {
                    node_id: [0u8; 32],
                    round: 0,
                    trust_score: 0.5,
                    timestamp: 0,
                },
            )
            .await;
        assert!(matches!(result, Err(NetworkError::NodeNotFound { .. })));
    }

    #[tokio::test]
    async fn test_local_backend_communication() {
        let backend1 = LocalChannelBackend::with_id("node-1".to_string());
        let backend2 = LocalChannelBackend::with_id("node-2".to_string());

        // Cross-register
        backend1.register_peer_sender("node-2", backend2.get_sender());
        backend2.register_peer_sender("node-1", backend1.get_sender());

        // Send from 1 to 2
        let msg = FederatedMessage::Heartbeat {
            node_id: [1u8; 32],
            round: 5,
            trust_score: 0.8,
            timestamp: 12345,
        };

        backend1
            .send(&NodeAddress::Channel("node-2".to_string()), msg.clone())
            .await
            .unwrap();

        // Receive on 2
        let (source, received) = backend2.receive(Duration::from_secs(1)).await.unwrap();
        assert_eq!(source, NodeAddress::Channel("node-1".to_string()));
        assert_eq!(received.message_type(), "Heartbeat");
    }

    #[tokio::test]
    async fn test_local_backend_broadcast() {
        let backend1 = LocalChannelBackend::with_id("node-1".to_string());
        let backend2 = LocalChannelBackend::with_id("node-2".to_string());
        let backend3 = LocalChannelBackend::with_id("node-3".to_string());

        // Register all peers with node-1
        backend1.register_peer_sender("node-2", backend2.get_sender());
        backend1.register_peer_sender("node-3", backend3.get_sender());

        // Broadcast from node-1
        let msg = FederatedMessage::Heartbeat {
            node_id: [1u8; 32],
            round: 1,
            trust_score: 0.5,
            timestamp: 0,
        };

        let sent_count = backend1.broadcast(msg).await.unwrap();
        assert_eq!(sent_count, 2);

        // Both should receive
        let _ = backend2.receive(Duration::from_secs(1)).await.unwrap();
        let _ = backend3.receive(Duration::from_secs(1)).await.unwrap();
    }

    #[tokio::test]
    async fn test_local_backend_receive_timeout() {
        let backend = LocalChannelBackend::new();
        let result = backend.receive(Duration::from_millis(10)).await;
        assert!(matches!(result, Err(NetworkError::Timeout { .. })));
    }

    // =========================================================================
    // Coordinator Tests
    // =========================================================================

    #[tokio::test]
    async fn test_coordinator_creation() {
        let config = FederatedNetworkConfig::for_testing();
        let coordinator = FederatedCoordinator::new(config, vec![0.0; 10]).await;

        assert_eq!(coordinator.current_round(), 0);
        assert_eq!(coordinator.peer_count(), 0);
        assert_eq!(coordinator.get_weights().len(), 10);
    }

    #[tokio::test]
    async fn test_coordinator_update_weights() {
        let config = FederatedNetworkConfig::for_testing();
        let coordinator = FederatedCoordinator::new(config, vec![0.0; 5]).await;

        coordinator.update_weights(vec![1.0, 2.0, 3.0, 4.0, 5.0]);
        let weights = coordinator.get_weights();

        assert_eq!(weights.len(), 5);
        assert!((weights[0] - 1.0).abs() < 0.001);
        assert!((weights[4] - 5.0).abs() < 0.001);
    }

    #[tokio::test]
    async fn test_coordinator_register_peer() {
        let config = FederatedNetworkConfig::for_testing();
        let coordinator = FederatedCoordinator::new(config, vec![0.0; 10]).await;

        let peer = FederatedNode::with_random_id(NodeAddress::Channel("peer-1".to_string()));
        let peer_id = peer.node_id;

        coordinator.register_peer(peer);
        assert_eq!(coordinator.peer_count(), 1);

        coordinator.unregister_peer(&peer_id, "test");
        assert_eq!(coordinator.peer_count(), 0);
    }

    #[tokio::test]
    async fn test_coordinator_stats() {
        let config = FederatedNetworkConfig::for_testing();
        let coordinator = FederatedCoordinator::new(config, vec![0.0; 10]).await;

        let stats = coordinator.stats();
        assert_eq!(stats.active_nodes, 0);
        assert_eq!(stats.current_round, 0);
        assert_eq!(stats.gradients_received, 0);
    }

    #[tokio::test]
    async fn test_coordinator_event_subscription() {
        let config = FederatedNetworkConfig::for_testing();
        let coordinator = FederatedCoordinator::new(config, vec![0.0; 10]).await;

        let mut rx = coordinator.subscribe_events();

        let peer = FederatedNode::with_random_id(NodeAddress::Channel("peer-1".to_string()));
        coordinator.register_peer(peer);

        let event = rx.try_recv();
        assert!(event.is_ok());
        assert!(matches!(
            event.unwrap(),
            CoordinatorEvent::NodeJoined { .. }
        ));
    }

    // =========================================================================
    // Integration Tests
    // =========================================================================

    #[tokio::test]
    async fn test_create_test_network() {
        let coordinators = create_test_network(3, 10).await;

        assert_eq!(coordinators.len(), 3);

        for coordinator in &coordinators {
            // Each coordinator should see 2 peers
            assert_eq!(coordinator.peer_count(), 2);
            assert_eq!(coordinator.get_weights().len(), 10);
        }
    }

    #[tokio::test]
    async fn test_gradient_sharing() {
        let coordinators = create_test_network(3, 10).await;

        // Update weights on coordinator 0
        coordinators[0].update_weights(vec![1.0; 10]);

        // Share gradient from coordinator 0
        let sent = coordinators[0].share_gradient(0.0).await.unwrap();
        assert_eq!(sent, 2); // Should send to 2 peers

        // Give a bit of time for messages to arrive
        tokio::time::sleep(Duration::from_millis(50)).await;

        // Coordinator 1 should be able to receive the gradient
        let result = coordinators[1]
            .backend
            .receive(Duration::from_millis(100))
            .await;
        assert!(result.is_ok());

        let (_, msg) = result.unwrap();
        assert_eq!(msg.message_type(), "GradientShare");
    }

    #[tokio::test]
    async fn test_heartbeat_broadcast() {
        let coordinators = create_test_network(2, 5).await;

        // Send heartbeat from coordinator 0
        let sent = coordinators[0].send_heartbeat().await.unwrap();
        assert_eq!(sent, 1); // Should send to 1 peer

        // Coordinator 1 should receive it
        let (_, msg) = coordinators[1]
            .backend
            .receive(Duration::from_millis(100))
            .await
            .unwrap();
        assert_eq!(msg.message_type(), "Heartbeat");
    }

    #[tokio::test]
    async fn test_full_sync_round() {
        let coordinators = create_test_network(3, 4).await;

        // Set different initial weights for each coordinator
        coordinators[0].update_weights(vec![1.0, 0.0, 0.0, 0.0]);
        coordinators[1].update_weights(vec![0.0, 1.0, 0.0, 0.0]);
        coordinators[2].update_weights(vec![0.0, 0.0, 1.0, 0.0]);

        // Run sync round on coordinator 0 (acting as coordinator)
        // First, the other coordinators need to share their gradients
        coordinators[1].share_gradient(0.0).await.unwrap();
        coordinators[2].share_gradient(0.0).await.unwrap();

        // Run sync round on coordinator 0
        let result = coordinators[0].run_sync_round().await;
        assert!(result.is_ok());

        // The result may or may not have aggregated weights depending on timing
        // In a real scenario, we'd need more sophisticated synchronization
    }

    #[tokio::test]
    async fn test_coordinator_shutdown() {
        let config = FederatedNetworkConfig::for_testing();
        let mut coordinator = FederatedCoordinator::new(config, vec![0.0; 10]).await;

        // Should not panic
        coordinator.shutdown().await;
    }

    // =========================================================================
    // Error Handling Tests
    // =========================================================================

    #[test]
    fn test_network_error_display() {
        let err = NetworkError::Timeout {
            operation: "receive".to_string(),
            timeout_ms: 1000,
        };
        assert!(format!("{}", err).contains("1000"));
        assert!(format!("{}", err).contains("receive"));

        let err = NetworkError::NodeNotFound {
            node_id: "abc123".to_string(),
        };
        assert!(format!("{}", err).contains("abc123"));
    }

    // =========================================================================
    // TCP Backend Stub Tests
    // =========================================================================

    #[tokio::test]
    async fn test_tcp_backend_not_implemented() {
        let addr: SocketAddr = "127.0.0.1:8080".parse().unwrap();
        let backend = TcpBackend::new(addr);

        assert!(!backend.is_ready());

        let result = backend
            .send(
                &NodeAddress::Unassigned,
                FederatedMessage::Heartbeat {
                    node_id: [0u8; 32],
                    round: 0,
                    trust_score: 0.5,
                    timestamp: 0,
                },
            )
            .await;
        assert!(matches!(result, Err(NetworkError::Internal { .. })));
    }
}
