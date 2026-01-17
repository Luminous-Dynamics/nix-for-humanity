//! # Relational Consciousness
//!
//! Implements consciousness as a relational phenomenon, where awareness
//! emerges from the interactions and relationships between cognitive components.

use crate::hdc::RealHV;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// A node in the relational consciousness network
#[derive(Debug, Clone)]
pub struct RelationalNode {
    /// Node identifier
    pub id: String,
    /// Node content encoding
    pub encoding: RealHV,
    /// Relations to other nodes
    pub relations: HashMap<String, Relation>,
    /// Activation level
    pub activation: f32,
    /// Consciousness contribution
    pub phi_contribution: f64,
}

/// A relation between consciousness nodes
#[derive(Debug, Clone)]
pub struct Relation {
    /// Target node ID
    pub target_id: String,
    /// Relation type
    pub relation_type: RelationType,
    /// Relation strength
    pub strength: f32,
    /// Directional encoding
    pub direction_encoding: RealHV,
}

/// Types of relations in consciousness
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum RelationType {
    /// Causal relation
    Causes,
    /// Part-whole relation
    PartOf,
    /// Similarity relation
    SimilarTo,
    /// Temporal sequence
    Precedes,
    /// Attention focus
    AttendsTo,
    /// Binding relation
    BoundWith,
    /// Mutual information
    MutualInfo,
    /// Custom relation
    Custom,
}

/// Configuration for relational consciousness
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RelationalConfig {
    /// HDC dimension
    pub dimension: usize,
    /// Maximum relations per node
    pub max_relations: usize,
    /// Activation threshold
    pub activation_threshold: f32,
    /// Relation decay rate
    pub decay_rate: f32,
}

impl Default for RelationalConfig {
    fn default() -> Self {
        Self {
            dimension: 512,
            max_relations: 50,
            activation_threshold: 0.1,
            decay_rate: 0.05,
        }
    }
}

/// Main relational consciousness system
pub struct RelationalConsciousness {
    config: RelationalConfig,
    /// All nodes in the network
    nodes: HashMap<String, RelationalNode>,
    /// Global relational encoding
    global_encoding: RealHV,
    /// Integration metric
    phi: f64,
    /// Processing cycle count
    cycle_count: u64,
}

impl RelationalConsciousness {
    /// Create new relational consciousness
    pub fn new(config: RelationalConfig) -> Self {
        Self {
            global_encoding: RealHV::random(config.dimension),
            nodes: HashMap::new(),
            phi: 0.0,
            cycle_count: 0,
            config,
        }
    }

    /// Add a node to the network
    pub fn add_node(&mut self, id: impl Into<String>, encoding: RealHV) -> &RelationalNode {
        let id = id.into();
        let node = RelationalNode {
            id: id.clone(),
            encoding,
            relations: HashMap::new(),
            activation: 0.5,
            phi_contribution: 0.0,
        };
        self.nodes.insert(id.clone(), node);
        self.nodes.get(&id).unwrap()
    }

    /// Add a relation between nodes
    pub fn add_relation(&mut self, from_id: &str, to_id: &str, relation_type: RelationType, strength: f32) {
        if let Some(from_node) = self.nodes.get_mut(from_id) {
            if from_node.relations.len() < self.config.max_relations {
                let relation = Relation {
                    target_id: to_id.to_string(),
                    relation_type,
                    strength,
                    direction_encoding: RealHV::random(self.config.dimension),
                };
                from_node.relations.insert(to_id.to_string(), relation);
            }
        }
    }

    /// Process one cycle of relational dynamics
    pub fn process_cycle(&mut self) {
        self.cycle_count += 1;

        // Collect updates to avoid borrow issues
        let mut activation_updates: HashMap<String, f32> = HashMap::new();

        for (node_id, node) in &self.nodes {
            let mut new_activation = node.activation;

            // Spread activation through relations
            for (target_id, relation) in &node.relations {
                if let Some(_target) = self.nodes.get(target_id) {
                    new_activation += relation.strength * 0.1;
                }
            }

            // Apply decay
            new_activation *= 1.0 - self.config.decay_rate;

            // Clamp activation
            new_activation = new_activation.clamp(0.0, 1.0);

            activation_updates.insert(node_id.clone(), new_activation);
        }

        // Apply updates
        for (node_id, activation) in activation_updates {
            if let Some(node) = self.nodes.get_mut(&node_id) {
                node.activation = activation;
            }
        }

        // Calculate phi
        self.calculate_phi();
    }

    /// Calculate integrated information
    fn calculate_phi(&mut self) {
        if self.nodes.len() < 2 {
            self.phi = 0.0;
            return;
        }

        // Calculate mutual information between connected nodes
        let mut total_mi = 0.0;
        let mut count = 0;

        for node in self.nodes.values() {
            for relation in node.relations.values() {
                if let Some(target) = self.nodes.get(&relation.target_id) {
                    // Approximate MI as correlation of encodings
                    let correlation = node.encoding.cosine_similarity(&target.encoding).abs();
                    total_mi += correlation as f64 * relation.strength as f64;
                    count += 1;
                }
            }
        }

        self.phi = if count > 0 {
            total_mi / count as f64
        } else {
            0.0
        };
    }

    /// Get current phi value
    pub fn phi(&self) -> f64 {
        self.phi
    }

    /// Get node by ID
    pub fn get_node(&self, id: &str) -> Option<&RelationalNode> {
        self.nodes.get(id)
    }

    /// Get all nodes
    pub fn nodes(&self) -> impl Iterator<Item = &RelationalNode> {
        self.nodes.values()
    }

    /// Get global encoding
    pub fn global_encoding(&self) -> &RealHV {
        &self.global_encoding
    }

    /// Update global encoding based on current state
    pub fn update_global_encoding(&mut self) {
        let active_encodings: Vec<RealHV> = self.nodes.values()
            .filter(|n| n.activation > self.config.activation_threshold)
            .map(|n| n.encoding.scale(n.activation))
            .collect();

        if !active_encodings.is_empty() {
            self.global_encoding = self.global_encoding.bundle(&active_encodings);
        }
    }
}

impl Default for RelationalConsciousness {
    fn default() -> Self {
        Self::new(RelationalConfig::default())
    }
}

/// Result of relational query
#[derive(Debug, Clone)]
pub struct RelationalQueryResult {
    /// Matching nodes
    pub matches: Vec<String>,
    /// Confidence scores
    pub confidences: HashMap<String, f32>,
    /// Relation paths
    pub paths: Vec<Vec<String>>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_relational_consciousness() {
        let mut rc = RelationalConsciousness::default();

        let enc1 = RealHV::random(512);
        let enc2 = RealHV::random(512);

        rc.add_node("node1", enc1);
        rc.add_node("node2", enc2);
        rc.add_relation("node1", "node2", RelationType::Causes, 0.8);

        rc.process_cycle();

        assert!(rc.phi() >= 0.0);
    }
}
