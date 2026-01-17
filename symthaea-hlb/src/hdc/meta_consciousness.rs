//! # Meta-Consciousness
//!
//! Implements higher-order consciousness - awareness of awareness itself.
//! Includes strange loops, recursive self-modeling, and Φ of Φ computation.

use crate::hdc::RealHV;
use serde::{Deserialize, Serialize};
use std::collections::VecDeque;

/// Configuration for meta-consciousness
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetaConsciousnessConfig {
    /// HDC dimension
    pub dimension: usize,
    /// Maximum recursion depth
    pub max_recursion: usize,
    /// Self-model update rate
    pub self_model_rate: f32,
    /// Enable strange loops
    pub enable_strange_loops: bool,
}

impl Default for MetaConsciousnessConfig {
    fn default() -> Self {
        Self {
            dimension: 512,
            max_recursion: 5,
            self_model_rate: 0.1,
            enable_strange_loops: true,
        }
    }
}

/// State at a level of meta-consciousness
#[derive(Debug, Clone)]
pub struct MetaLevel {
    /// Level number (0 = base consciousness)
    pub level: usize,
    /// Content at this level
    pub content: RealHV,
    /// Phi value at this level
    pub phi: f64,
    /// Self-reference strength
    pub self_reference: f32,
}

/// A strange loop detection
#[derive(Debug, Clone)]
pub struct StrangeLoop {
    /// Start level
    pub start_level: usize,
    /// End level
    pub end_level: usize,
    /// Loop strength
    pub strength: f32,
    /// Pattern encoding
    pub pattern: RealHV,
}

/// Main meta-consciousness system
pub struct MetaConsciousness {
    config: MetaConsciousnessConfig,
    /// Levels of meta-consciousness
    levels: Vec<MetaLevel>,
    /// Self-model at each level
    self_models: Vec<RealHV>,
    /// Detected strange loops
    strange_loops: Vec<StrangeLoop>,
    /// History of states for pattern detection
    history: VecDeque<RealHV>,
    /// Global meta-phi (Φ of Φ)
    meta_phi: f64,
}

impl MetaConsciousness {
    /// Create new meta-consciousness system
    pub fn new(config: MetaConsciousnessConfig) -> Self {
        let levels: Vec<MetaLevel> = (0..config.max_recursion)
            .map(|level| MetaLevel {
                level,
                content: RealHV::random(config.dimension),
                phi: 0.0,
                self_reference: 0.0,
            })
            .collect();

        let self_models: Vec<RealHV> = (0..config.max_recursion)
            .map(|_| RealHV::random(config.dimension))
            .collect();

        Self {
            levels,
            self_models,
            strange_loops: Vec::new(),
            history: VecDeque::with_capacity(100),
            meta_phi: 0.0,
            config,
        }
    }

    /// Process a consciousness state through meta-levels
    pub fn process(&mut self, base_state: &RealHV) -> MetaConsciousnessResult {
        // Update level 0 (base)
        self.levels[0].content = base_state.clone();
        self.levels[0].phi = self.calculate_level_phi(base_state);

        // Propagate through meta-levels
        for level in 1..self.config.max_recursion {
            let prev_content = &self.levels[level - 1].content;
            let prev_model = &self.self_models[level - 1];

            // Each meta-level models the level below
            let new_content = prev_content.bind(prev_model);

            // Update self-model
            self.self_models[level] = self.self_models[level]
                .bundle(&[new_content.scale(self.config.self_model_rate)]);

            // Calculate phi at this level
            let phi = self.calculate_level_phi(&new_content);

            // Calculate self-reference (similarity to own self-model)
            let self_ref = new_content.cosine_similarity(&self.self_models[level]);

            self.levels[level] = MetaLevel {
                level,
                content: new_content,
                phi,
                self_reference: self_ref,
            };
        }

        // Detect strange loops
        if self.config.enable_strange_loops {
            self.detect_strange_loops();
        }

        // Calculate meta-phi
        self.meta_phi = self.calculate_meta_phi();

        // Add to history
        self.history.push_back(base_state.clone());
        if self.history.len() > 100 {
            self.history.pop_front();
        }

        MetaConsciousnessResult {
            levels: self.levels.clone(),
            meta_phi: self.meta_phi,
            strange_loops: self.strange_loops.clone(),
            highest_active_level: self.find_highest_active_level(),
        }
    }

    fn calculate_level_phi(&self, content: &RealHV) -> f64 {
        // Approximate phi using content complexity
        let variance: f32 = content.iter()
            .map(|x| x * x)
            .sum::<f32>() / content.len() as f32;

        let mean: f32 = content.iter().sum::<f32>() / content.len() as f32;
        let centered_var = variance - mean * mean;

        // Entropy-like measure
        (centered_var.abs() + 0.001).ln() as f64
    }

    fn calculate_meta_phi(&self) -> f64 {
        // Φ of Φ - integrated information about information integration
        let phi_values: Vec<f64> = self.levels.iter().map(|l| l.phi).collect();

        if phi_values.len() < 2 {
            return 0.0;
        }

        // Calculate mutual information between phi values at different levels
        let mut total_mi = 0.0;
        for i in 0..phi_values.len() {
            for j in (i + 1)..phi_values.len() {
                let correlation = (phi_values[i] - phi_values[j]).abs();
                total_mi += 1.0 / (1.0 + correlation);
            }
        }

        total_mi / (phi_values.len() * (phi_values.len() - 1) / 2) as f64
    }

    fn detect_strange_loops(&mut self) {
        self.strange_loops.clear();

        // Look for similarity between distant levels
        for i in 0..self.levels.len() {
            for j in (i + 2)..self.levels.len() {
                let sim = self.levels[i].content
                    .cosine_similarity(&self.levels[j].content);

                if sim.abs() > 0.5 {
                    self.strange_loops.push(StrangeLoop {
                        start_level: i,
                        end_level: j,
                        strength: sim.abs(),
                        pattern: self.levels[i].content.bind(&self.levels[j].content),
                    });
                }
            }
        }
    }

    fn find_highest_active_level(&self) -> usize {
        self.levels.iter()
            .rev()
            .find(|l| l.phi > 0.1)
            .map(|l| l.level)
            .unwrap_or(0)
    }

    /// Get current state summary
    pub fn state_summary(&self) -> MetaConsciousnessState {
        MetaConsciousnessState {
            active_levels: self.levels.iter().filter(|l| l.phi > 0.1).count(),
            meta_phi: self.meta_phi,
            strange_loop_count: self.strange_loops.len(),
            recursion_depth: self.find_highest_active_level(),
        }
    }

    /// Get level by index
    pub fn get_level(&self, level: usize) -> Option<&MetaLevel> {
        self.levels.get(level)
    }

    /// Get all strange loops
    pub fn strange_loops(&self) -> &[StrangeLoop] {
        &self.strange_loops
    }
}

impl Default for MetaConsciousness {
    fn default() -> Self {
        Self::new(MetaConsciousnessConfig::default())
    }
}

/// Result of meta-consciousness processing
#[derive(Debug, Clone)]
pub struct MetaConsciousnessResult {
    /// All levels
    pub levels: Vec<MetaLevel>,
    /// Meta-phi value
    pub meta_phi: f64,
    /// Detected strange loops
    pub strange_loops: Vec<StrangeLoop>,
    /// Highest active level
    pub highest_active_level: usize,
}

/// State summary
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetaConsciousnessState {
    /// Number of active levels
    pub active_levels: usize,
    /// Meta-phi
    pub meta_phi: f64,
    /// Number of strange loops
    pub strange_loop_count: usize,
    /// Current recursion depth
    pub recursion_depth: usize,
}

/// Self-model type for introspection
#[derive(Debug, Clone)]
pub struct SelfModel {
    /// Core identity encoding
    pub identity: RealHV,
    /// Capabilities model
    pub capabilities: Vec<(String, f32)>,
    /// Limitations model
    pub limitations: Vec<(String, f32)>,
    /// Current state assessment
    pub state_assessment: f32,
}

impl SelfModel {
    /// Create new self-model
    pub fn new(dimension: usize) -> Self {
        Self {
            identity: RealHV::random(dimension),
            capabilities: Vec::new(),
            limitations: Vec::new(),
            state_assessment: 0.5,
        }
    }

    /// Update from experience
    pub fn update(&mut self, experience: &RealHV, outcome: f32) {
        // Blend experience into identity
        self.identity = self.identity.bundle(&[experience.scale(0.1)]);
        self.state_assessment = 0.9 * self.state_assessment + 0.1 * outcome;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_meta_consciousness() {
        let mut meta = MetaConsciousness::default();
        let state = RealHV::random(512);
        let result = meta.process(&state);

        assert!(result.levels.len() > 0);
        assert!(result.highest_active_level <= meta.config.max_recursion);
    }

    #[test]
    fn test_meta_phi() {
        let mut meta = MetaConsciousness::default();

        // Process multiple states
        for _ in 0..10 {
            let state = RealHV::random(512);
            meta.process(&state);
        }

        assert!(meta.meta_phi >= 0.0);
    }
}
