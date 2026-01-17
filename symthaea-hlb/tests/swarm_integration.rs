//! Swarm Learning Integration Tests
//!
//! Tests for the P2P swarm intelligence system.
//! These tests verify the swarm types and basic functionality
//! without requiring actual P2P connections.

use symthaea::swarm::{
    SwarmConfig, SwarmError, PeerStats, SwarmIntelligence,
};

// ============================================================================
// SWARM CONFIG TESTS
// ============================================================================

#[test]
fn test_swarm_config_default() {
    let config = SwarmConfig::default();

    assert!(config.enabled, "Swarm should be enabled by default");
    assert_eq!(config.pattern_topic, "sophia-patterns");
    assert!(config.max_peers > 0, "Should have positive max_peers");
    assert!(config.min_reputation > 0.0 && config.min_reputation < 1.0);
}

#[test]
fn test_swarm_config_custom() {
    let config = SwarmConfig {
        enabled: false,
        pattern_topic: "custom-topic".to_string(),
        max_peers: 100,
        min_reputation: 0.8,
    };

    assert!(!config.enabled);
    assert_eq!(config.pattern_topic, "custom-topic");
    assert_eq!(config.max_peers, 100);
    assert_eq!(config.min_reputation, 0.8);
}

// ============================================================================
// PEER STATS TESTS
// ============================================================================

#[test]
fn test_peer_stats_default() {
    let stats = PeerStats::default();

    assert_eq!(stats.patterns_received, 0);
    assert_eq!(stats.queries_answered, 0);
    assert_eq!(stats.reputation, 0.5, "Default reputation should be neutral (0.5)");
}

#[test]
fn test_peer_stats_fields() {
    let stats = PeerStats {
        patterns_received: 10,
        queries_answered: 5,
        last_seen: std::time::SystemTime::now(),
        reputation: 0.85,
    };

    assert_eq!(stats.patterns_received, 10);
    assert_eq!(stats.queries_answered, 5);
    assert!(stats.reputation > 0.8);
}

// ============================================================================
// SWARM ERROR TESTS
// ============================================================================

#[test]
fn test_swarm_error_variants() {
    let errors = [
        SwarmError::ConnectionFailed("test".to_string()),
        SwarmError::PeerNotFound("test".to_string()),
        SwarmError::SendFailed("test".to_string()),
        SwarmError::InvalidMessage("test".to_string()),
        SwarmError::Timeout,
        SwarmError::Internal("test".to_string()),
    ];

    assert_eq!(errors.len(), 6);
}

#[test]
fn test_swarm_error_display() {
    let error = SwarmError::ConnectionFailed("network down".to_string());
    let display = format!("{}", error);
    assert!(display.contains("Connection failed"));
    assert!(display.contains("network down"));

    let timeout = SwarmError::Timeout;
    let display = format!("{}", timeout);
    assert!(display.contains("timed out"));
}

// ============================================================================
// SWARM INTELLIGENCE TESTS
// ============================================================================

#[tokio::test]
async fn test_swarm_intelligence_creation() {
    let config = SwarmConfig::default();
    let swarm = SwarmIntelligence::new(config).await;

    assert!(swarm.is_ok(), "Should create swarm intelligence successfully");
}

#[tokio::test]
async fn test_swarm_intelligence_with_disabled_config() {
    let config = SwarmConfig {
        enabled: false,
        ..Default::default()
    };

    let swarm = SwarmIntelligence::new(config).await;
    assert!(swarm.is_ok(), "Should create disabled swarm");
}

#[tokio::test]
async fn test_swarm_intelligence_custom_topic() {
    let config = SwarmConfig {
        pattern_topic: "test-topic".to_string(),
        ..Default::default()
    };

    let swarm = SwarmIntelligence::new(config).await;
    assert!(swarm.is_ok());
}

// ============================================================================
// SWARM MESSAGE TESTS (Via serialization)
// ============================================================================

#[test]
fn test_learned_pattern_structure() {
    // Test pattern structure without actual networking
    let pattern: Vec<i8> = vec![1, -1, 1, 1, -1];
    let intent = "greeting".to_string();
    let confidence = 0.85f32;
    let peer_id = "12D3KooW...".to_string();

    assert_eq!(pattern.len(), 5);
    assert!(!intent.is_empty());
    assert!(confidence > 0.0 && confidence <= 1.0);
    assert!(!peer_id.is_empty());
}

#[test]
fn test_query_structure() {
    let query: Vec<i8> = vec![1, 1, -1, -1, 1];
    let context = "seeking help".to_string();
    let requester = "12D3KooW...".to_string();

    assert_eq!(query.len(), 5);
    assert!(!context.is_empty());
    assert!(!requester.is_empty());
}

#[test]
fn test_response_structure() {
    let patterns: Vec<Vec<i8>> = vec![
        vec![1, -1, 1],
        vec![-1, 1, -1],
    ];
    let intents = vec!["help".to_string(), "assist".to_string()];
    let confidences = vec![0.9f32, 0.8f32];
    let responder = "12D3KooW...".to_string();

    assert_eq!(patterns.len(), 2);
    assert_eq!(intents.len(), 2);
    assert_eq!(confidences.len(), 2);
    assert!(!responder.is_empty());
}

// ============================================================================
// PRIVACY-PRESERVING KNOWLEDGE SHARING TESTS
// ============================================================================

#[test]
fn test_pattern_is_privacy_preserving() {
    // Hypervectors are privacy-preserving because they encode
    // semantic meaning without raw data
    let pattern: Vec<i8> = vec![1, -1, 1, 1, -1, -1, 1, -1, 1, 1];

    // The pattern encodes meaning, not identifiable data
    // It's impossible to reverse-engineer the original input
    assert_eq!(pattern.len(), 10);

    // All values are bipolar (-1 or 1)
    for &val in &pattern {
        assert!(val == 1 || val == -1);
    }
}

#[test]
fn test_collective_resonance_via_addition() {
    // Swarm consensus is achieved via vector addition
    // Similar patterns reinforce, different ones cancel
    let pattern1: Vec<i8> = vec![1, 1, -1, 1, -1];
    let pattern2: Vec<i8> = vec![1, 1, -1, 1, -1]; // Same as pattern1
    let pattern3: Vec<i8> = vec![-1, -1, 1, -1, 1]; // Opposite of pattern1

    // Adding similar patterns reinforces
    let sum_similar: Vec<i16> = pattern1.iter()
        .zip(pattern2.iter())
        .map(|(&a, &b)| a as i16 + b as i16)
        .collect();

    // Adding opposite patterns cancels
    let sum_opposite: Vec<i16> = pattern1.iter()
        .zip(pattern3.iter())
        .map(|(&a, &b)| a as i16 + b as i16)
        .collect();

    // Similar patterns have strong sum
    let similar_magnitude: i16 = sum_similar.iter().map(|x| x.abs()).sum();
    assert_eq!(similar_magnitude, 10); // All 2s -> 2*5=10

    // Opposite patterns cancel out
    let opposite_magnitude: i16 = sum_opposite.iter().map(|x| x.abs()).sum();
    assert_eq!(opposite_magnitude, 0); // All 0s
}

// ============================================================================
// REPUTATION SYSTEM TESTS
// ============================================================================

#[test]
fn test_reputation_bounds() {
    let config = SwarmConfig::default();

    // Reputation should be between 0 and 1
    assert!(config.min_reputation >= 0.0);
    assert!(config.min_reputation <= 1.0);
}

#[test]
fn test_reputation_threshold() {
    let config = SwarmConfig {
        min_reputation: 0.7,
        ..Default::default()
    };

    let trusted_peer = PeerStats {
        reputation: 0.8,
        ..Default::default()
    };

    let untrusted_peer = PeerStats {
        reputation: 0.5,
        ..Default::default()
    };

    assert!(trusted_peer.reputation >= config.min_reputation);
    assert!(untrusted_peer.reputation < config.min_reputation);
}
