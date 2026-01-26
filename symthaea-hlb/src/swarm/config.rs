//! Swarm Configuration
//!
//! Configuration for the hybrid Iroh + Holochain swarm network.

use serde::{Deserialize, Serialize};

/// Main swarm configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SwarmConfig {
    /// Port to listen on (0 = OS-assigned)
    pub listen_port: u16,

    /// Enable mDNS for local peer discovery
    pub enable_mdns: bool,

    /// Enable DERP relays for NAT traversal
    pub enable_derp: bool,

    /// Maximum number of concurrent peer connections
    pub max_peers: usize,

    /// Minimum trust level required for tensor streaming
    pub min_trust_level: f64,

    /// Timeout for connection attempts (milliseconds)
    pub connect_timeout_ms: u64,

    /// Heartbeat interval (milliseconds)
    pub heartbeat_interval_ms: u64,

    /// Bootstrap peers for initial discovery
    pub bootstrap_peers: Vec<String>,

    /// Path to persist node identity
    pub identity_path: Option<String>,
}

impl Default for SwarmConfig {
    fn default() -> Self {
        Self {
            listen_port: 0, // OS-assigned for flexibility
            enable_mdns: true,
            enable_derp: true,
            max_peers: 50,
            min_trust_level: 0.5, // Minimum Φ reputation for streaming
            connect_timeout_ms: 5000,
            heartbeat_interval_ms: 30000,
            bootstrap_peers: vec![],
            identity_path: None,
        }
    }
}

impl SwarmConfig {
    /// Create config for local testing (no external connections)
    pub fn local_only() -> Self {
        Self {
            enable_derp: false,
            bootstrap_peers: vec![],
            ..Default::default()
        }
    }

    /// Create config for production with DERP relays
    pub fn production() -> Self {
        Self {
            max_peers: 100,
            min_trust_level: 0.7,
            ..Default::default()
        }
    }
}

/// Configuration for a specific peer connection
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PeerConfig {
    /// Peer's node ID (Iroh NodeId as hex string)
    pub node_id: String,

    /// Peer's Holochain agent public key (for trust verification)
    pub agent_key: Option<String>,

    /// Known DERP relay for this peer
    pub derp_relay: Option<String>,

    /// Direct addresses if known
    pub direct_addresses: Vec<String>,

    /// Nickname for this peer
    pub nickname: Option<String>,
}

impl PeerConfig {
    /// Create config from just a node ID
    pub fn from_node_id(node_id: impl Into<String>) -> Self {
        Self {
            node_id: node_id.into(),
            agent_key: None,
            derp_relay: None,
            direct_addresses: vec![],
            nickname: None,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_default_config() {
        let config = SwarmConfig::default();
        assert_eq!(config.listen_port, 0);
        assert!(config.enable_mdns);
        assert!(config.enable_derp);
        assert_eq!(config.max_peers, 50);
    }

    #[test]
    fn test_local_only_config() {
        let config = SwarmConfig::local_only();
        assert!(!config.enable_derp);
        assert!(config.bootstrap_peers.is_empty());
    }

    #[test]
    fn test_peer_config() {
        let peer = PeerConfig::from_node_id("abc123");
        assert_eq!(peer.node_id, "abc123");
        assert!(peer.agent_key.is_none());
    }
}
