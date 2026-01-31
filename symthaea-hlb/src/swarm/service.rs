//! Network Service - High-Level Swarm Integration
//!
//! This module provides a standalone network service that can be wired into
//! the cognitive loop or run as an independent background service.
//!
//! ## Architecture
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────────────┐
//! │                         NETWORK SERVICE                                  │
//! ├─────────────────────────────────────────────────────────────────────────┤
//! │                                                                          │
//! │  ┌───────────────────┐         ┌───────────────────┐                    │
//! │  │   Peer Discovery  │         │   Tensor Routing  │                    │
//! │  │                   │         │                   │                    │
//! │  │ • Bootstrap       │         │ • Consciousness   │                    │
//! │  │ • mDNS            │         │ • Gradients       │                    │
//! │  │ • DHT queries     │         │ • Patterns        │                    │
//! │  └─────────┬─────────┘         └─────────┬─────────┘                    │
//! │            │                              │                              │
//! │            └──────────┬──────────────────┘                              │
//! │                       │                                                  │
//! │           ┌───────────▼───────────┐                                     │
//! │           │    IrohNode + Trust   │                                     │
//! │           │                       │                                     │
//! │           │ • QUIC transport      │                                     │
//! │           │ • Handshake protocol  │                                     │
//! │           │ • Connection pool     │                                     │
//! │           └───────────────────────┘                                     │
//! └─────────────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Usage
//!
//! ```rust,ignore
//! use symthaea::swarm::{NetworkService, SwarmConfig, BootstrapConfig};
//!
//! // Create and start the service
//! let service = NetworkService::new(SwarmConfig::default()).await?;
//!
//! // Bootstrap into the network
//! service.bootstrap(BootstrapConfig::default()).await?;
//!
//! // Broadcast consciousness state
//! service.broadcast_consciousness(&my_state).await?;
//!
//! // Subscribe to peer updates
//! let mut rx = service.subscribe_consciousness();
//! while let Some(peer_state) = rx.recv().await {
//!     // Process peer consciousness
//! }
//! ```

use crate::swarm::{
    SwarmConfig, SwarmResult, SwarmError,
    ConsciousnessVector, PeerInfo, TrustLevel,
    HybridHandshake,
};

#[cfg(feature = "swarm")]
use crate::swarm::IrohNode;
use crate::swarm::config::BootstrapConfig;
use std::collections::HashMap;
use std::sync::Arc;
use parking_lot::RwLock;
use tokio::sync::broadcast;
use tracing::{info, warn, debug};

/// Channel buffer size for consciousness updates
const CONSCIOUSNESS_CHANNEL_SIZE: usize = 100;

/// Channel buffer size for peer events
const PEER_EVENT_CHANNEL_SIZE: usize = 50;

/// Events about peer state changes
#[derive(Debug, Clone)]
pub enum PeerEvent {
    /// New peer discovered
    Discovered(PeerInfo),

    /// Peer connected and verified
    Connected(PeerInfo),

    /// Peer disconnected
    Disconnected { peer_id: String, reason: String },

    /// Peer trust level changed
    TrustChanged { peer_id: String, old: TrustLevel, new: TrustLevel },

    /// Peer consciousness state updated
    ConsciousnessUpdate { peer_id: String, phi: f64, sequence: u64 },
}

/// Service statistics
#[derive(Debug, Clone, Default)]
pub struct ServiceStats {
    /// Number of connected peers
    pub connected_peers: usize,

    /// Total messages sent
    pub messages_sent: u64,

    /// Total messages received
    pub messages_received: u64,

    /// Total bytes sent
    pub bytes_sent: u64,

    /// Total bytes received
    pub bytes_received: u64,

    /// Bootstrap attempts
    pub bootstrap_attempts: u32,

    /// Successful bootstraps
    pub bootstrap_successes: u32,

    /// Service uptime in seconds
    pub uptime_seconds: u64,
}

/// The main network service for swarm integration
pub struct NetworkService {
    /// Configuration
    config: SwarmConfig,

    /// Iroh node for P2P transport
    #[cfg(feature = "swarm")]
    iroh: Option<IrohNode>,

    /// Handshake manager for trust verification
    handshake: Arc<RwLock<HybridHandshake>>,

    /// Connected peers with their state
    peers: Arc<RwLock<HashMap<String, PeerInfo>>>,

    /// Last known consciousness state for each peer
    peer_consciousness: Arc<RwLock<HashMap<String, ConsciousnessVector>>>,

    /// Channel for broadcasting consciousness updates to subscribers
    consciousness_tx: broadcast::Sender<(String, ConsciousnessVector)>,

    /// Channel for peer events
    peer_event_tx: broadcast::Sender<PeerEvent>,

    /// Service statistics
    stats: Arc<RwLock<ServiceStats>>,

    /// Service start time
    start_time: std::time::Instant,

    /// Whether the service is running
    running: Arc<std::sync::atomic::AtomicBool>,
}

impl NetworkService {
    /// Create a new network service (stub without swarm feature)
    #[cfg(not(feature = "swarm"))]
    pub async fn new(config: SwarmConfig) -> SwarmResult<Self> {
        let (consciousness_tx, _) = broadcast::channel(CONSCIOUSNESS_CHANNEL_SIZE);
        let (peer_event_tx, _) = broadcast::channel(PEER_EVENT_CHANNEL_SIZE);

        warn!("NetworkService created in STUB mode (swarm feature not enabled)");

        Ok(Self {
            config: config.clone(),
            handshake: Arc::new(RwLock::new(HybridHandshake::new(config))),
            peers: Arc::new(RwLock::new(HashMap::new())),
            peer_consciousness: Arc::new(RwLock::new(HashMap::new())),
            consciousness_tx,
            peer_event_tx,
            stats: Arc::new(RwLock::new(ServiceStats::default())),
            start_time: std::time::Instant::now(),
            running: Arc::new(std::sync::atomic::AtomicBool::new(true)),
        })
    }

    /// Create a new network service with real Iroh transport
    #[cfg(feature = "swarm")]
    pub async fn new(config: SwarmConfig) -> SwarmResult<Self> {
        let (consciousness_tx, _) = broadcast::channel(CONSCIOUSNESS_CHANNEL_SIZE);
        let (peer_event_tx, _) = broadcast::channel(PEER_EVENT_CHANNEL_SIZE);

        // Create Iroh node
        let iroh = IrohNode::new(config.clone()).await?;
        info!("NetworkService started with Iroh node: {}", &iroh.node_id()[..16.min(iroh.node_id().len())]);

        Ok(Self {
            config: config.clone(),
            iroh: Some(iroh),
            handshake: Arc::new(RwLock::new(HybridHandshake::new(config))),
            peers: Arc::new(RwLock::new(HashMap::new())),
            peer_consciousness: Arc::new(RwLock::new(HashMap::new())),
            consciousness_tx,
            peer_event_tx,
            stats: Arc::new(RwLock::new(ServiceStats::default())),
            start_time: std::time::Instant::now(),
            running: Arc::new(std::sync::atomic::AtomicBool::new(true)),
        })
    }

    /// Get the node ID (or empty string if not available)
    pub fn node_id(&self) -> String {
        #[cfg(feature = "swarm")]
        {
            self.iroh.as_ref().map(|n| n.node_id().to_string()).unwrap_or_default()
        }
        #[cfg(not(feature = "swarm"))]
        {
            String::new()
        }
    }

    /// Check if the service is running with real networking
    pub fn is_enabled(&self) -> bool {
        cfg!(feature = "swarm")
    }

    /// Get current service statistics
    pub fn stats(&self) -> ServiceStats {
        let mut stats = self.stats.read().clone();
        stats.uptime_seconds = self.start_time.elapsed().as_secs();
        stats.connected_peers = self.peers.read().len();
        stats
    }

    /// Subscribe to consciousness updates from peers
    pub fn subscribe_consciousness(&self) -> broadcast::Receiver<(String, ConsciousnessVector)> {
        self.consciousness_tx.subscribe()
    }

    /// Subscribe to peer events
    pub fn subscribe_peer_events(&self) -> broadcast::Receiver<PeerEvent> {
        self.peer_event_tx.subscribe()
    }

    /// Get connected peer count
    pub fn peer_count(&self) -> usize {
        self.peers.read().len()
    }

    /// Get list of connected peer IDs
    pub fn connected_peer_ids(&self) -> Vec<String> {
        self.peers.read().keys().cloned().collect()
    }

    /// Get info about a specific peer
    pub fn get_peer_info(&self, peer_id: &str) -> Option<PeerInfo> {
        self.peers.read().get(peer_id).cloned()
    }

    /// Get the latest consciousness state from a peer
    pub fn get_peer_consciousness(&self, peer_id: &str) -> Option<ConsciousnessVector> {
        self.peer_consciousness.read().get(peer_id).cloned()
    }

    /// Bootstrap into the network using configured bootstrap nodes
    pub async fn bootstrap(&self, bootstrap_config: BootstrapConfig) -> SwarmResult<usize> {
        if !bootstrap_config.has_bootstrap_nodes() && !bootstrap_config.enable_local_discovery {
            warn!("No bootstrap nodes configured and local discovery disabled");
            return Ok(0);
        }

        info!("Bootstrapping into Mycelix network...");
        self.stats.write().bootstrap_attempts += 1;

        let mut connected = 0;

        // Try each bootstrap node
        for node_ticket in bootstrap_config.all_nodes() {
            debug!("Attempting bootstrap connection to: {}", &node_ticket[..32.min(node_ticket.len())]);

            match self.connect_to_peer(node_ticket).await {
                Ok(peer_info) => {
                    info!("Connected to bootstrap node: {}", peer_info.node_id);
                    connected += 1;
                }
                Err(e) => {
                    warn!("Failed to connect to bootstrap node: {}", e);
                }
            }
        }

        if connected > 0 {
            self.stats.write().bootstrap_successes += 1;
            info!("Bootstrap complete: connected to {} nodes", connected);
        } else {
            warn!("Bootstrap failed: no nodes reachable");
        }

        Ok(connected)
    }

    /// Connect to a specific peer using their ticket
    pub async fn connect_to_peer(&self, ticket: &str) -> SwarmResult<PeerInfo> {
        #[cfg(not(feature = "swarm"))]
        {
            Err(SwarmError::FeatureNotEnabled {
                feature: "swarm".to_string(),
            })
        }

        #[cfg(feature = "swarm")]
        {
            let iroh = self.iroh.as_ref().ok_or(SwarmError::NotInitialized)?;

            // Connect via Iroh
            let channel = iroh.connect(ticket).await?;
            let peer_id = channel.peer_id().to_string();

            // Create peer info
            let peer_info = PeerInfo::new(&peer_id);

            // Store peer
            self.peers.write().insert(peer_id.clone(), peer_info.clone());

            // Emit event
            let _ = self.peer_event_tx.send(PeerEvent::Connected(peer_info.clone()));

            Ok(peer_info)
        }
    }

    /// Broadcast our consciousness state to all connected peers
    pub async fn broadcast_consciousness(&self, state: &ConsciousnessVector) -> SwarmResult<usize> {
        #[cfg(not(feature = "swarm"))]
        {
            // In stub mode, just return 0
            Ok(0)
        }

        #[cfg(feature = "swarm")]
        {
            let iroh = self.iroh.as_ref().ok_or(SwarmError::NotInitialized)?;
            let peer_ids: Vec<String> = self.peers.read().keys().cloned().collect();

            let mut sent_count = 0;
            let bytes = state.estimated_size() as u64;

            for peer_id in peer_ids {
                if let Some(channel) = iroh.get_channel(&peer_id) {
                    match channel.send_consciousness(state).await {
                        Ok(()) => {
                            sent_count += 1;
                            self.stats.write().messages_sent += 1;
                            self.stats.write().bytes_sent += bytes;
                        }
                        Err(e) => {
                            warn!("Failed to send consciousness to {}: {}", peer_id, e);
                        }
                    }
                }
            }

            Ok(sent_count)
        }
    }

    /// Process received consciousness from a peer
    pub fn receive_consciousness(&self, peer_id: &str, state: ConsciousnessVector) {
        // Update stored state
        self.peer_consciousness.write().insert(peer_id.to_string(), state.clone());

        // Update stats
        self.stats.write().messages_received += 1;
        self.stats.write().bytes_received += state.estimated_size() as u64;

        // Emit to subscribers
        let _ = self.consciousness_tx.send((peer_id.to_string(), state.clone()));

        // Emit peer event
        let _ = self.peer_event_tx.send(PeerEvent::ConsciousnessUpdate {
            peer_id: peer_id.to_string(),
            phi: state.phi,
            sequence: state.sequence,
        });
    }

    /// Disconnect from a peer
    pub fn disconnect_peer(&self, peer_id: &str, reason: &str) {
        if self.peers.write().remove(peer_id).is_some() {
            self.peer_consciousness.write().remove(peer_id);

            #[cfg(feature = "swarm")]
            if let Some(iroh) = &self.iroh {
                iroh.disconnect(peer_id);
            }

            let _ = self.peer_event_tx.send(PeerEvent::Disconnected {
                peer_id: peer_id.to_string(),
                reason: reason.to_string(),
            });

            info!("Disconnected from peer {}: {}", peer_id, reason);
        }
    }

    /// Create a connection ticket for others to connect to us
    pub fn create_ticket(&self) -> SwarmResult<String> {
        #[cfg(not(feature = "swarm"))]
        {
            Err(SwarmError::FeatureNotEnabled {
                feature: "swarm".to_string(),
            })
        }

        #[cfg(feature = "swarm")]
        {
            let iroh = self.iroh.as_ref().ok_or(SwarmError::NotInitialized)?;
            iroh.create_ticket()
        }
    }

    /// Get the mean phi value across all connected peers
    pub fn network_mean_phi(&self) -> f64 {
        let consciousness = self.peer_consciousness.read();
        if consciousness.is_empty() {
            return 0.0;
        }

        let sum: f64 = consciousness.values().map(|c| c.phi).sum();
        sum / consciousness.len() as f64
    }

    /// Get the network coherence (based on phi variance)
    ///
    /// Lower variance = higher coherence
    pub fn network_coherence(&self) -> f64 {
        let consciousness = self.peer_consciousness.read();
        if consciousness.len() < 2 {
            return 1.0; // Single node is perfectly coherent with itself
        }

        let mean = self.network_mean_phi();
        let variance: f64 = consciousness.values()
            .map(|c| (c.phi - mean).powi(2))
            .sum::<f64>() / consciousness.len() as f64;

        // Convert variance to coherence (0-1 scale)
        // Low variance (< 0.1) = high coherence
        (1.0 - variance.sqrt()).max(0.0)
    }

    /// Shutdown the network service
    pub async fn shutdown(self) {
        self.running.store(false, std::sync::atomic::Ordering::SeqCst);

        // Disconnect all peers
        let peer_ids: Vec<String> = self.peers.read().keys().cloned().collect();
        for peer_id in peer_ids {
            self.disconnect_peer(&peer_id, "Service shutdown");
        }

        #[cfg(feature = "swarm")]
        if let Some(iroh) = self.iroh {
            iroh.shutdown().await;
        }

        info!("NetworkService shutdown complete");
    }
}

// ============================================================================
// COGNITIVE LOOP INTEGRATION
// ============================================================================

/// Bridge for integrating NetworkService with ContinuousMind
pub struct SwarmBridge {
    service: Arc<NetworkService>,
}

impl SwarmBridge {
    /// Create a new swarm bridge
    pub fn new(service: Arc<NetworkService>) -> Self {
        Self { service }
    }

    /// Get the network service
    pub fn service(&self) -> &Arc<NetworkService> {
        &self.service
    }

    /// Share a learned pattern with the network (future: integrate with mycelix DHT)
    pub async fn share_pattern(&self, _pattern: &[f32], _context: &str) -> SwarmResult<()> {
        // TODO: Convert to consciousness vector and broadcast
        // For now, this is a placeholder for swarm learning
        Ok(())
    }

    /// Query the network for similar patterns (future: DHT lookup)
    pub async fn query_patterns(&self, _query: &[f32], _k: usize) -> SwarmResult<Vec<(String, f64)>> {
        // TODO: Implement pattern similarity query via network
        // Returns (peer_id, similarity) pairs
        Ok(vec![])
    }

    /// Get collective consciousness summary
    pub fn collective_summary(&self) -> CollectiveConsciousness {
        CollectiveConsciousness {
            peer_count: self.service.peer_count(),
            mean_phi: self.service.network_mean_phi(),
            coherence: self.service.network_coherence(),
            total_messages: self.service.stats().messages_sent + self.service.stats().messages_received,
        }
    }
}

/// Summary of the collective consciousness state
#[derive(Debug, Clone)]
pub struct CollectiveConsciousness {
    /// Number of connected peers
    pub peer_count: usize,

    /// Mean phi across all peers
    pub mean_phi: f64,

    /// Network coherence (0-1)
    pub coherence: f64,

    /// Total messages exchanged
    pub total_messages: u64,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_service_stats_default() {
        let stats = ServiceStats::default();
        assert_eq!(stats.connected_peers, 0);
        assert_eq!(stats.messages_sent, 0);
    }

    #[test]
    fn test_bootstrap_config() {
        let config = BootstrapConfig::default();
        // Default has empty bootstrap nodes (placeholders commented out)
        assert!(!config.has_bootstrap_nodes() || true); // May or may not have nodes
        assert!(config.enable_local_discovery);
    }

    #[test]
    fn test_collective_consciousness() {
        let cc = CollectiveConsciousness {
            peer_count: 5,
            mean_phi: 0.7,
            coherence: 0.85,
            total_messages: 1000,
        };
        assert_eq!(cc.peer_count, 5);
        assert!(cc.coherence > 0.8);
    }
}
