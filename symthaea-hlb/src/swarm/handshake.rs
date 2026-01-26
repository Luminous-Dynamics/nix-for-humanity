//! Hybrid Handshake Protocol - Trust Bridge between Holochain and Iroh
//!
//! This module implements the "Trust Challenge" protocol that ensures
//! only trusted peers (verified via Holochain) can establish real-time
//! tensor streams (via Iroh).
//!
//! ## Protocol Flow
//!
//! ```text
//!     Node A                                    Node B
//!        │                                         │
//!        │──────── 1. Iroh Connect ───────────────>│
//!        │                                         │
//!        │<─────── 2. Trust Challenge ─────────────│
//!        │         (nonce)                         │
//!        │                                         │
//!        │──────── 3. Trust Response ─────────────>│
//!        │         (signed nonce + agent key)      │
//!        │                                         │
//!        │         4. Verify Signature             │
//!        │         5. Check Holochain DHT Trust    │
//!        │                                         │
//!        │<─────── 6. Trust Ack / Reject ──────────│
//!        │                                         │
//!        │<═══════ 7. Tensor Streaming ═══════════>│
//!        │         (if trusted)                    │
//! ```
//!
//! ## Security Model
//!
//! - The nonce prevents replay attacks
//! - The signature proves possession of the Holochain agent key
//! - The DHT lookup verifies the agent's reputation
//! - Only after trust verification can tensor streaming begin

use crate::swarm::{
    SwarmConfig, SwarmResult, SwarmError,
    TrustLevel, SwarmMessage,
};
use std::time::{SystemTime, Duration};
use rand::Rng;

/// The hybrid handshake manager
pub struct HybridHandshake {
    /// Configuration
    config: SwarmConfig,

    /// Pending challenges we've issued
    pending_challenges: std::collections::HashMap<String, PendingChallenge>,

    /// Challenge timeout
    challenge_timeout: Duration,
}

/// A pending trust challenge
struct PendingChallenge {
    /// The nonce we sent
    nonce: Vec<u8>,

    /// When the challenge was issued
    issued_at: SystemTime,

    /// The peer we challenged
    peer_node_id: String,
}

impl HybridHandshake {
    /// Create a new handshake manager
    pub fn new(config: SwarmConfig) -> Self {
        Self {
            config,
            pending_challenges: std::collections::HashMap::new(),
            challenge_timeout: Duration::from_secs(30),
        }
    }

    /// Generate a trust challenge for a new peer
    pub fn create_challenge(&mut self, peer_node_id: &str) -> SwarmMessage {
        // Generate cryptographic nonce
        let nonce: Vec<u8> = rand::thread_rng()
            .sample_iter(rand::distributions::Standard)
            .take(32)
            .collect();

        // Store pending challenge
        self.pending_challenges.insert(
            peer_node_id.to_string(),
            PendingChallenge {
                nonce: nonce.clone(),
                issued_at: SystemTime::now(),
                peer_node_id: peer_node_id.to_string(),
            },
        );

        SwarmMessage::TrustChallenge { nonce }
    }

    /// Create a response to a trust challenge
    ///
    /// In a real implementation, this would sign the nonce with the
    /// Holochain agent's private key.
    pub fn create_response(
        &self,
        nonce: &[u8],
        agent_key: &str,
        _agent_private_key: &[u8], // Would be used for real signing
    ) -> SwarmMessage {
        // In production: sign nonce with Ed25519 key
        // For now: simple HMAC-style binding
        let mut signed = nonce.to_vec();
        signed.extend_from_slice(agent_key.as_bytes());

        SwarmMessage::TrustResponse {
            signed_nonce: signed,
            agent_key: agent_key.to_string(),
        }
    }

    /// Verify a trust response
    pub fn verify_response(
        &mut self,
        peer_node_id: &str,
        signed_nonce: &[u8],
        agent_key: &str,
    ) -> SwarmResult<TrustLevel> {
        // Get pending challenge
        let challenge = self.pending_challenges.remove(peer_node_id)
            .ok_or_else(|| SwarmError::TrustVerificationError {
                reason: "No pending challenge for this peer".to_string(),
            })?;

        // Check timeout
        if challenge.issued_at.elapsed().unwrap_or(Duration::MAX) > self.challenge_timeout {
            return Err(SwarmError::TrustVerificationError {
                reason: "Challenge timed out".to_string(),
            });
        }

        // Verify signature format (simplified)
        // In production: verify Ed25519 signature
        let expected_len = challenge.nonce.len() + agent_key.len();
        if signed_nonce.len() != expected_len {
            return Err(SwarmError::TrustVerificationError {
                reason: "Invalid signature length".to_string(),
            });
        }

        // Verify nonce matches
        if &signed_nonce[..challenge.nonce.len()] != challenge.nonce.as_slice() {
            return Err(SwarmError::TrustVerificationError {
                reason: "Nonce mismatch".to_string(),
            });
        }

        // Verify agent key binding
        if &signed_nonce[challenge.nonce.len()..] != agent_key.as_bytes() {
            return Err(SwarmError::TrustVerificationError {
                reason: "Agent key mismatch".to_string(),
            });
        }

        // In production: query Holochain DHT for agent's reputation
        // For now: return verified with default trust
        Ok(TrustLevel::Verified(0.7))
    }

    /// Check if a trust level meets minimum requirements
    pub fn meets_trust_requirement(&self, trust: &TrustLevel) -> bool {
        trust.value() >= self.config.min_trust_level
    }

    /// Clean up expired challenges
    pub fn cleanup_expired(&mut self) {
        self.pending_challenges.retain(|_, challenge| {
            challenge.issued_at.elapsed()
                .map(|d| d < self.challenge_timeout)
                .unwrap_or(false)
        });
    }

    /// Get the number of pending challenges
    pub fn pending_count(&self) -> usize {
        self.pending_challenges.len()
    }
}

/// Result of a complete handshake
#[derive(Debug, Clone)]
pub struct HandshakeResult {
    /// The peer's node ID
    pub peer_node_id: String,

    /// The peer's agent key (if verified)
    pub agent_key: Option<String>,

    /// Trust level after verification
    pub trust_level: TrustLevel,

    /// Whether streaming is allowed
    pub streaming_allowed: bool,

    /// Time taken for handshake (milliseconds)
    pub handshake_time_ms: u64,
}

impl HandshakeResult {
    /// Create a successful handshake result
    pub fn success(
        peer_node_id: impl Into<String>,
        agent_key: impl Into<String>,
        trust_level: TrustLevel,
        handshake_time_ms: u64,
    ) -> Self {
        Self {
            peer_node_id: peer_node_id.into(),
            agent_key: Some(agent_key.into()),
            trust_level,
            streaming_allowed: true,
            handshake_time_ms,
        }
    }

    /// Create a failed handshake result
    pub fn failed(peer_node_id: impl Into<String>) -> Self {
        Self {
            peer_node_id: peer_node_id.into(),
            agent_key: None,
            trust_level: TrustLevel::Untrusted,
            streaming_allowed: false,
            handshake_time_ms: 0,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_create_challenge() {
        let config = SwarmConfig::default();
        let mut handshake = HybridHandshake::new(config);

        let challenge = handshake.create_challenge("peer-123");

        match challenge {
            SwarmMessage::TrustChallenge { nonce } => {
                assert_eq!(nonce.len(), 32);
            }
            _ => panic!("Expected TrustChallenge"),
        }

        assert_eq!(handshake.pending_count(), 1);
    }

    #[test]
    fn test_create_response() {
        let config = SwarmConfig::default();
        let handshake = HybridHandshake::new(config);

        let nonce = vec![1, 2, 3, 4];
        let response = handshake.create_response(&nonce, "agent-key", b"private");

        match response {
            SwarmMessage::TrustResponse { signed_nonce, agent_key } => {
                assert!(!signed_nonce.is_empty());
                assert_eq!(agent_key, "agent-key");
            }
            _ => panic!("Expected TrustResponse"),
        }
    }

    #[test]
    fn test_verify_response() {
        let config = SwarmConfig::default();
        let mut handshake = HybridHandshake::new(config);

        // Create challenge
        let challenge = handshake.create_challenge("peer-123");
        let nonce = match challenge {
            SwarmMessage::TrustChallenge { nonce } => nonce,
            _ => panic!("Expected TrustChallenge"),
        };

        // Create response
        let response = handshake.create_response(&nonce, "agent-key", b"private");
        let (signed_nonce, agent_key) = match response {
            SwarmMessage::TrustResponse { signed_nonce, agent_key } => (signed_nonce, agent_key),
            _ => panic!("Expected TrustResponse"),
        };

        // Verify
        let trust = handshake.verify_response("peer-123", &signed_nonce, &agent_key).unwrap();
        assert!(matches!(trust, TrustLevel::Verified(_)));
    }

    #[test]
    fn test_trust_requirement() {
        let mut config = SwarmConfig::default();
        config.min_trust_level = 0.5;
        let handshake = HybridHandshake::new(config);

        assert!(handshake.meets_trust_requirement(&TrustLevel::Verified(0.7)));
        assert!(!handshake.meets_trust_requirement(&TrustLevel::Verified(0.3)));
        assert!(!handshake.meets_trust_requirement(&TrustLevel::Unknown));
    }

    #[test]
    fn test_handshake_result() {
        let success = HandshakeResult::success("peer-1", "agent-1", TrustLevel::Verified(0.8), 150);
        assert!(success.streaming_allowed);

        let failed = HandshakeResult::failed("peer-2");
        assert!(!failed.streaming_allowed);
    }
}
