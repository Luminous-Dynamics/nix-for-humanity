//! # Hierarchical Closed-form Continuous-time Networks
//!
//! Multi-scale CfC architecture where each level operates at different
//! temporal scales, enabling simultaneous processing of:
//! - Level 0: Fast sensory dynamics (tau 0.1-0.5)
//! - Level 1: Semantic integration (tau 0.5-5.0)
//! - Level 2: Narrative/contextual processing (tau 5.0-10.0)
//!
//! Top-down feedback allows higher levels to modulate lower-level
//! time constants via sigmoid gating.

use ndarray::Array1;
use serde::{Deserialize, Serialize};
use super::cfc::{CfCNetwork, CfCNetworkConfig, CfCConfig, ActivationType};

/// Configuration for hierarchical CfC
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HierarchicalCfCConfig {
    /// Input dimension
    pub input_dim: usize,
    /// Output dimension
    pub output_dim: usize,
    /// Per-level configurations: (hidden_dim, tau_min, tau_max)
    pub levels: Vec<(usize, f32, f32)>,
    /// Enable top-down feedback
    pub top_down_feedback: bool,
    /// Feedback strength (0.0 to 1.0)
    pub feedback_strength: f32,
}

impl Default for HierarchicalCfCConfig {
    fn default() -> Self {
        Self {
            input_dim: 64,
            output_dim: 32,
            levels: vec![
                (64, 0.1, 0.5),   // Level 0: fast/sensory
                (64, 0.5, 5.0),   // Level 1: semantic
                (32, 5.0, 10.0),  // Level 2: narrative
            ],
            top_down_feedback: true,
            feedback_strength: 0.3,
        }
    }
}

/// Hierarchical CfC network with multi-scale temporal processing
pub struct HierarchicalCfC {
    /// Configuration
    config: HierarchicalCfCConfig,
    /// CfC networks at each level
    levels: Vec<CfCNetwork>,
    /// Total steps processed
    total_steps: u64,
}

impl HierarchicalCfC {
    /// Create a new hierarchical CfC network
    pub fn new(config: HierarchicalCfCConfig) -> Self {
        let mut levels = Vec::new();

        for (i, &(hidden_dim, tau_min, tau_max)) in config.levels.iter().enumerate() {
            // Each level takes the output of the previous level as input
            // Level 0 takes the raw input, subsequent levels take previous level's hidden dim
            let level_input_dim = if i == 0 {
                config.input_dim
            } else {
                config.levels[i - 1].0 // Previous level's hidden dim
            };

            let level_output_dim = hidden_dim; // Output matches hidden for inter-level passing

            let cell_config = CfCConfig {
                input_dim: level_input_dim,
                hidden_dim,
                use_backbone: false,
                backbone_layers: 0,
                backbone_dim: 0,
                activation: ActivationType::SiLU,
                tau_range: (tau_min, tau_max),
                dropout: 0.0,
            };

            let net_config = CfCNetworkConfig {
                input_dim: level_input_dim,
                hidden_dim,
                num_layers: 1,
                output_dim: level_output_dim,
                cell_config,
                residual: false,
                bidirectional: false,
            };

            levels.push(CfCNetwork::new(net_config));
        }

        Self {
            config,
            levels,
            total_steps: 0,
        }
    }

    /// Process input through all levels (bottom-up), then apply top-down feedback
    pub fn step(&mut self, input: &Array1<f32>, dt: f32) -> Array1<f32> {
        self.total_steps += 1;

        // Bottom-up: each level's output is the next level's input
        let mut current = input.clone();
        let mut level_outputs = Vec::new();

        for level in &mut self.levels {
            current = level.forward(&current, dt);
            level_outputs.push(current.clone());
        }

        // Top-down feedback: higher levels modulate lower level tau values
        if self.config.top_down_feedback && self.levels.len() > 1 {
            for i in (0..self.levels.len() - 1).rev() {
                let higher_output = &level_outputs[i + 1];
                // Compute sigmoid gate from higher level output
                let gate_strength = self.config.feedback_strength;
                let mean_activation: f32 = higher_output.iter().sum::<f32>()
                    / higher_output.len() as f32;
                let gate = 1.0 / (1.0 + (-mean_activation).exp()); // sigmoid

                // Scale lower level tau values: tau *= (1 + gate_strength * (gate - 0.5))
                // gate > 0.5 → slow down lower level (increase tau)
                // gate < 0.5 → speed up lower level (decrease tau)
                let tau_scale = 1.0 + gate_strength * (gate - 0.5);
                self.levels[i].scale_tau_all(tau_scale);
            }
        }

        // Return the top level's output
        level_outputs.last().cloned().unwrap_or_else(|| Array1::zeros(self.config.output_dim))
    }

    /// Reset all levels
    pub fn reset(&mut self) {
        for level in &mut self.levels {
            level.reset();
        }
        self.total_steps = 0;
    }

    /// Get the number of levels
    pub fn num_levels(&self) -> usize {
        self.levels.len()
    }

    /// Get total parameters across all levels
    pub fn num_parameters(&self) -> usize {
        self.levels.iter().map(|l| l.num_parameters()).sum()
    }

    /// Get states from all levels
    pub fn all_states(&self) -> Vec<Vec<Array1<f32>>> {
        self.levels.iter().map(|l| l.state()).collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_hierarchical_cfc_creation() {
        let config = HierarchicalCfCConfig::default();
        let hcfc = HierarchicalCfC::new(config);
        assert_eq!(hcfc.num_levels(), 3);
    }

    #[test]
    fn test_hierarchical_cfc_forward() {
        let config = HierarchicalCfCConfig::default();
        let mut hcfc = HierarchicalCfC::new(config);

        let input = Array1::from_vec(vec![0.5; 64]);
        let output = hcfc.step(&input, 0.1);

        // Output should be the top level's output_dim (= hidden_dim = 32)
        assert_eq!(output.len(), 32);
        assert!(output.iter().all(|x| x.is_finite()));
    }

    #[test]
    fn test_hierarchical_cfc_stability() {
        let config = HierarchicalCfCConfig::default();
        let mut hcfc = HierarchicalCfC::new(config);
        let input = Array1::from_vec(vec![0.3; 64]);

        for step in 0..1000 {
            let output = hcfc.step(&input, 0.1);
            assert!(
                output.iter().all(|x| x.is_finite()),
                "Hierarchical CfC diverged at step {}",
                step
            );
        }
    }

    #[test]
    fn test_hierarchical_reset() {
        let config = HierarchicalCfCConfig::default();
        let mut hcfc = HierarchicalCfC::new(config);
        let input = Array1::from_vec(vec![1.0; 64]);

        hcfc.step(&input, 0.1);
        hcfc.reset();

        // After reset, all states should be zero
        for level_states in hcfc.all_states() {
            for state in level_states {
                assert!(state.iter().all(|x| *x == 0.0), "State not reset");
            }
        }
    }
}
