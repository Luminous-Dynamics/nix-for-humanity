//! # Global Workspace Theory Implementation
//!
//! Implements Baars' Global Workspace Theory (GWT) for conscious access.
//! The workspace acts as a shared "blackboard" where specialized modules
//! compete for access and broadcast information globally.

use crate::hdc::RealHV;
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, VecDeque};

/// Configuration for global workspace
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GlobalWorkspaceConfig {
    /// HDC dimension
    pub dimension: usize,
    /// Maximum items in workspace
    pub capacity: usize,
    /// Broadcast threshold (activation level to broadcast)
    pub broadcast_threshold: f32,
    /// Decay rate per step
    pub decay_rate: f32,
    /// Competition strength
    pub competition_strength: f32,
}

impl Default for GlobalWorkspaceConfig {
    fn default() -> Self {
        Self {
            dimension: 512,
            capacity: 10,
            broadcast_threshold: 0.6,
            decay_rate: 0.1,
            competition_strength: 0.5,
        }
    }
}

/// A coalition competing for workspace access
#[derive(Debug, Clone)]
pub struct Coalition {
    /// Coalition identifier
    pub id: String,
    /// Member contents
    pub members: Vec<RealHV>,
    /// Combined representation
    pub combined: RealHV,
    /// Activation strength
    pub activation: f32,
    /// Source module
    pub source: String,
    /// Priority
    pub priority: f32,
}

impl Coalition {
    /// Create new coalition
    pub fn new(id: impl Into<String>, members: Vec<RealHV>, source: impl Into<String>) -> Self {
        let combined = if members.is_empty() {
            RealHV::zeros(512)
        } else {
            members[0].bundle(&members[1..])
        };

        Self {
            id: id.into(),
            members,
            combined,
            activation: 0.5,
            source: source.into(),
            priority: 0.5,
        }
    }

    /// Boost activation
    pub fn boost(&mut self, amount: f32) {
        self.activation = (self.activation + amount).min(1.0);
    }

    /// Decay activation
    pub fn decay(&mut self, rate: f32) {
        self.activation = (self.activation * (1.0 - rate)).max(0.0);
    }
}

/// Broadcast event
#[derive(Debug, Clone)]
pub struct Broadcast {
    /// Coalition that won broadcast
    pub coalition: Coalition,
    /// Global representation
    pub global_representation: RealHV,
    /// Receiving modules
    pub receivers: Vec<String>,
    /// Timestamp
    pub timestamp: u64,
}

/// Main global workspace
pub struct GlobalWorkspace {
    config: GlobalWorkspaceConfig,
    /// Coalitions competing for access
    coalitions: Vec<Coalition>,
    /// Current broadcast (if any)
    current_broadcast: Option<Broadcast>,
    /// Broadcast history
    history: VecDeque<Broadcast>,
    /// Registered specialist modules
    specialists: HashMap<String, SpecialistModule>,
    /// Global state representation
    global_state: RealHV,
    /// Step counter
    step: u64,
}

/// A specialist module that can contribute to workspace
#[derive(Debug, Clone)]
pub struct SpecialistModule {
    /// Module name
    pub name: String,
    /// Module encoding
    pub encoding: RealHV,
    /// Current relevance
    pub relevance: f32,
    /// Can receive broadcasts
    pub can_receive: bool,
    /// Can send to workspace
    pub can_send: bool,
}

impl GlobalWorkspace {
    /// Create new global workspace
    pub fn new(config: GlobalWorkspaceConfig) -> Self {
        Self {
            global_state: RealHV::random(config.dimension),
            coalitions: Vec::new(),
            current_broadcast: None,
            history: VecDeque::with_capacity(100),
            specialists: HashMap::new(),
            step: 0,
            config,
        }
    }

    /// Register a specialist module
    pub fn register_specialist(&mut self, name: impl Into<String>, encoding: RealHV) {
        let name = name.into();
        self.specialists.insert(name.clone(), SpecialistModule {
            name,
            encoding,
            relevance: 0.5,
            can_receive: true,
            can_send: true,
        });
    }

    /// Submit a coalition to compete for broadcast
    pub fn submit(&mut self, coalition: Coalition) {
        if self.coalitions.len() < self.config.capacity {
            self.coalitions.push(coalition);
        } else {
            // Replace weakest coalition
            if let Some(min_idx) = self.coalitions.iter()
                .enumerate()
                .min_by(|a, b| a.1.activation.partial_cmp(&b.1.activation).unwrap())
                .map(|(idx, _)| idx)
            {
                if self.coalitions[min_idx].activation < coalition.activation {
                    self.coalitions[min_idx] = coalition;
                }
            }
        }
    }

    /// Process one step of workspace dynamics
    pub fn step(&mut self) -> Option<Broadcast> {
        self.step += 1;

        // Apply competition (lateral inhibition)
        self.apply_competition();

        // Decay all coalitions
        for coalition in &mut self.coalitions {
            coalition.decay(self.config.decay_rate);
        }

        // Remove inactive coalitions
        self.coalitions.retain(|c| c.activation > 0.05);

        // Find winner (if any above threshold)
        let winner = self.coalitions.iter()
            .filter(|c| c.activation > self.config.broadcast_threshold)
            .max_by(|a, b| a.activation.partial_cmp(&b.activation).unwrap())
            .cloned();

        if let Some(winning_coalition) = winner {
            // Create broadcast
            let receivers: Vec<String> = self.specialists.keys().cloned().collect();

            let broadcast = Broadcast {
                coalition: winning_coalition.clone(),
                global_representation: winning_coalition.combined.clone(),
                receivers,
                timestamp: self.step,
            };

            // Update global state
            self.global_state = self.global_state
                .bundle(&[winning_coalition.combined.scale(0.5)]);

            // Store in history
            self.history.push_back(broadcast.clone());
            if self.history.len() > 100 {
                self.history.pop_front();
            }

            self.current_broadcast = Some(broadcast.clone());

            // Remove winning coalition
            self.coalitions.retain(|c| c.id != winning_coalition.id);

            Some(broadcast)
        } else {
            self.current_broadcast = None;
            None
        }
    }

    fn apply_competition(&mut self) {
        if self.coalitions.len() < 2 {
            return;
        }

        // Calculate inhibition for each coalition
        let mut inhibitions: Vec<f32> = vec![0.0; self.coalitions.len()];

        for i in 0..self.coalitions.len() {
            for j in 0..self.coalitions.len() {
                if i != j {
                    // Inhibition based on activation difference and similarity
                    let sim = self.coalitions[i].combined
                        .cosine_similarity(&self.coalitions[j].combined)
                        .abs();

                    inhibitions[i] += self.coalitions[j].activation * sim * self.config.competition_strength;
                }
            }
        }

        // Apply inhibition
        for (i, coalition) in self.coalitions.iter_mut().enumerate() {
            coalition.activation = (coalition.activation - inhibitions[i]).max(0.0);
        }
    }

    /// Get current broadcast
    pub fn current_broadcast(&self) -> Option<&Broadcast> {
        self.current_broadcast.as_ref()
    }

    /// Get global state
    pub fn global_state(&self) -> &RealHV {
        &self.global_state
    }

    /// Get broadcast history
    pub fn history(&self) -> &VecDeque<Broadcast> {
        &self.history
    }

    /// Get all current coalitions
    pub fn coalitions(&self) -> &[Coalition] {
        &self.coalitions
    }

    /// Query workspace with a pattern
    pub fn query(&self, pattern: &RealHV) -> Vec<(String, f32)> {
        self.coalitions.iter()
            .map(|c| (c.id.clone(), c.combined.cosine_similarity(pattern)))
            .collect()
    }
}

impl Default for GlobalWorkspace {
    fn default() -> Self {
        Self::new(GlobalWorkspaceConfig::default())
    }
}

/// Statistics about workspace
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorkspaceStats {
    /// Current number of coalitions
    pub coalition_count: usize,
    /// Total broadcasts
    pub total_broadcasts: usize,
    /// Average activation
    pub avg_activation: f32,
    /// Workspace utilization
    pub utilization: f32,
}

impl GlobalWorkspace {
    /// Get statistics
    pub fn stats(&self) -> WorkspaceStats {
        let avg_activation = if self.coalitions.is_empty() {
            0.0
        } else {
            self.coalitions.iter().map(|c| c.activation).sum::<f32>()
                / self.coalitions.len() as f32
        };

        WorkspaceStats {
            coalition_count: self.coalitions.len(),
            total_broadcasts: self.history.len(),
            avg_activation,
            utilization: self.coalitions.len() as f32 / self.config.capacity as f32,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_global_workspace() {
        let mut gw = GlobalWorkspace::default();

        // Add some coalitions
        let c1 = Coalition::new("c1", vec![RealHV::random(512)], "module1");
        let c2 = Coalition::new("c2", vec![RealHV::random(512)], "module2");

        gw.submit(c1);
        gw.submit(c2);

        // Step workspace
        gw.step();

        assert!(gw.coalitions().len() <= 2);
    }

    #[test]
    fn test_broadcast() {
        let mut gw = GlobalWorkspace::default();

        // Add high-activation coalition
        let mut c1 = Coalition::new("winner", vec![RealHV::random(512)], "module1");
        c1.activation = 0.8;

        gw.submit(c1);

        // Should broadcast
        let broadcast = gw.step();
        assert!(broadcast.is_some());
    }
}
