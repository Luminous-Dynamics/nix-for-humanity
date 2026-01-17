//! # Consciousness Integration Pipeline
//!
//! Central integration system that combines multiple consciousness-related
//! modules into a coherent processing pipeline.

use crate::hdc::RealHV;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

// ═══════════════════════════════════════════════════════════════════════════════
// CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════════

/// Configuration for consciousness integration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IntegrationConfig {
    /// HDC dimension
    pub dimension: usize,
    /// Number of processing stages
    pub num_stages: usize,
    /// Enable phi calculation
    pub enable_phi: bool,
    /// Enable GWT workspace
    pub enable_gwt: bool,
    /// Attention heads count
    pub attention_heads: usize,
}

impl Default for IntegrationConfig {
    fn default() -> Self {
        Self {
            dimension: 512,
            num_stages: 4,
            enable_phi: true,
            enable_gwt: true,
            attention_heads: 8,
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// CONSCIOUSNESS STATE
// ═══════════════════════════════════════════════════════════════════════════════

/// Main consciousness state representation
#[derive(Debug, Clone)]
pub struct ConsciousnessState {
    /// Attention allocation
    pub attention: RealHV,
    /// Working memory contents
    pub working_memory: Vec<RealHV>,
    /// Current Phi value
    pub phi: f64,
    /// Arousal level
    pub arousal: f32,
    /// Metacognitive confidence
    pub metacognitive_confidence: f32,
    /// Active concepts
    pub active_concepts: HashMap<String, f32>,
}

impl ConsciousnessState {
    /// Create new consciousness state
    pub fn new(dimension: usize) -> Self {
        Self {
            attention: RealHV::random(dimension),
            working_memory: Vec::new(),
            phi: 0.0,
            arousal: 0.5,
            metacognitive_confidence: 0.5,
            active_concepts: HashMap::new(),
        }
    }

    /// Calculate integrated information
    pub fn calculate_phi(&self) -> f64 {
        // Simple phi approximation based on working memory coherence
        if self.working_memory.len() < 2 {
            return 0.0;
        }

        let mut total_coherence = 0.0;
        let mut count = 0;

        for i in 0..self.working_memory.len() {
            for j in (i + 1)..self.working_memory.len() {
                total_coherence += self.working_memory[i]
                    .cosine_similarity(&self.working_memory[j])
                    .abs() as f64;
                count += 1;
            }
        }

        if count > 0 {
            total_coherence / count as f64
        } else {
            0.0
        }
    }
}

impl Default for ConsciousnessState {
    fn default() -> Self {
        Self::new(512)
    }
}

/// Altered state index for modified consciousness
#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub struct AlteredStateIndex {
    /// Dream-likeness (0-1)
    pub dreaminess: f32,
    /// Dissociation level
    pub dissociation: f32,
    /// Hyperfocus intensity
    pub hyperfocus: f32,
    /// Flow state depth
    pub flow: f32,
}

impl Default for AlteredStateIndex {
    fn default() -> Self {
        Self {
            dreaminess: 0.0,
            dissociation: 0.0,
            hyperfocus: 0.0,
            flow: 0.0,
        }
    }
}

/// Predictive processing mode
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum PredictiveMode {
    /// Bottom-up sensory processing
    BottomUp,
    /// Top-down prediction
    TopDown,
    /// Bidirectional integration
    Bidirectional,
    /// Error-correction mode
    ErrorCorrection,
}

impl Default for PredictiveMode {
    fn default() -> Self {
        PredictiveMode::Bidirectional
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// BINDING TYPES
// ═══════════════════════════════════════════════════════════════════════════════

/// A bound perceptual object
#[derive(Debug, Clone)]
pub struct BoundObject {
    /// Object identifier
    pub id: String,
    /// Feature bindings
    pub features: HashMap<String, RealHV>,
    /// Binding strength
    pub binding_strength: f32,
    /// Attention weight
    pub attention_weight: f32,
    /// Timestamp of binding
    pub timestamp: u64,
}

/// Level of binding
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum BindingLevel {
    /// Weak/tentative binding
    Weak,
    /// Moderate binding
    Moderate,
    /// Strong/consolidated binding
    Strong,
    /// Integrated across modalities
    Integrated,
}

/// Temporal binding memory
#[derive(Debug, Clone)]
pub struct TemporalBindingMemory {
    /// Recent bindings
    bindings: Vec<BoundObject>,
    /// Maximum capacity
    capacity: usize,
    /// Theta phase for temporal coordination
    theta_phase: f32,
}

impl TemporalBindingMemory {
    /// Create new temporal binding memory
    pub fn new(capacity: usize) -> Self {
        Self {
            bindings: Vec::new(),
            capacity,
            theta_phase: 0.0,
        }
    }

    /// Add a binding
    pub fn add(&mut self, binding: BoundObject) {
        if self.bindings.len() >= self.capacity {
            self.bindings.remove(0);
        }
        self.bindings.push(binding);
    }

    /// Step theta phase
    pub fn step_theta(&mut self, dt: f32) {
        self.theta_phase = (self.theta_phase + dt * 6.0) % (2.0 * std::f32::consts::PI);
    }

    /// Get current bindings
    pub fn bindings(&self) -> &[BoundObject] {
        &self.bindings
    }
}

impl Default for TemporalBindingMemory {
    fn default() -> Self {
        Self::new(100)
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// WORKSPACE TYPES
// ═══════════════════════════════════════════════════════════════════════════════

/// An item in the global workspace
#[derive(Debug, Clone)]
pub struct WorkspaceItem {
    /// Item identifier
    pub id: String,
    /// Content representation
    pub content: RealHV,
    /// Activation level
    pub activation: f32,
    /// Source module
    pub source: String,
    /// Priority
    pub priority: f32,
    /// Decay rate
    pub decay_rate: f32,
}

impl WorkspaceItem {
    /// Create new workspace item
    pub fn new(id: impl Into<String>, content: RealHV, source: impl Into<String>) -> Self {
        Self {
            id: id.into(),
            content,
            activation: 1.0,
            source: source.into(),
            priority: 0.5,
            decay_rate: 0.1,
        }
    }

    /// Decay the item
    pub fn decay(&mut self, dt: f32) {
        self.activation *= 1.0 - self.decay_rate * dt;
    }

    /// Check if item is still active
    pub fn is_active(&self) -> bool {
        self.activation > 0.1
    }
}

/// A meta-level thought about thought
#[derive(Debug, Clone)]
pub struct MetaThought {
    /// Thought content
    pub content: String,
    /// Confidence in thought
    pub confidence: f32,
    /// Recursion level (thought about thought about...)
    pub recursion_level: u32,
    /// Related concepts
    pub related_concepts: Vec<String>,
}

// ═══════════════════════════════════════════════════════════════════════════════
// METRICS AND ASSESSMENT
// ═══════════════════════════════════════════════════════════════════════════════

/// Report on consciousness metrics
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct ConsciousnessMetricsReport {
    /// Phi value
    pub phi: f64,
    /// Attention coherence
    pub attention_coherence: f32,
    /// Working memory load
    pub working_memory_load: f32,
    /// Metacognitive accuracy
    pub metacognitive_accuracy: f32,
    /// Binding strength average
    pub binding_strength: f32,
    /// Workspace utilization
    pub workspace_utilization: f32,
}

/// Optimization recommendation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OptimizationRecommendation {
    /// Recommendation text
    pub recommendation: String,
    /// Priority level
    pub priority: f32,
    /// Target subsystem
    pub target: String,
    /// Expected improvement
    pub expected_improvement: f32,
}

/// Integration assessment result
#[derive(Debug, Clone)]
pub struct IntegrationAssessment {
    /// Overall score
    pub overall_score: f32,
    /// Component scores
    pub component_scores: HashMap<String, f32>,
    /// Issues found
    pub issues: Vec<String>,
    /// Recommendations
    pub recommendations: Vec<OptimizationRecommendation>,
}

impl Default for IntegrationAssessment {
    fn default() -> Self {
        Self {
            overall_score: 0.5,
            component_scores: HashMap::new(),
            issues: Vec::new(),
            recommendations: Vec::new(),
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN PIPELINE
// ═══════════════════════════════════════════════════════════════════════════════

/// Main consciousness integration pipeline
pub struct ConsciousnessPipeline {
    config: IntegrationConfig,
    state: ConsciousnessState,
    workspace: Vec<WorkspaceItem>,
    temporal_memory: TemporalBindingMemory,
    metrics: ConsciousnessMetricsReport,
}

impl ConsciousnessPipeline {
    /// Create new pipeline
    pub fn new(config: IntegrationConfig) -> Self {
        let state = ConsciousnessState::new(config.dimension);
        Self {
            config,
            state,
            workspace: Vec::new(),
            temporal_memory: TemporalBindingMemory::default(),
            metrics: ConsciousnessMetricsReport::default(),
        }
    }

    /// Process input through pipeline
    pub fn process(&mut self, input: &RealHV) -> ConsciousnessState {
        // Update attention
        self.state.attention = self.state.attention.bundle(&[input.clone()]);

        // Add to working memory
        if self.state.working_memory.len() < 7 {
            self.state.working_memory.push(input.clone());
        } else {
            self.state.working_memory.remove(0);
            self.state.working_memory.push(input.clone());
        }

        // Calculate phi
        self.state.phi = self.state.calculate_phi();

        // Update metrics
        self.metrics.phi = self.state.phi;
        self.metrics.working_memory_load = self.state.working_memory.len() as f32 / 7.0;

        self.state.clone()
    }

    /// Add item to workspace
    pub fn broadcast(&mut self, item: WorkspaceItem) {
        self.workspace.push(item);
    }

    /// Get current state
    pub fn state(&self) -> &ConsciousnessState {
        &self.state
    }

    /// Get metrics
    pub fn metrics(&self) -> &ConsciousnessMetricsReport {
        &self.metrics
    }

    /// Assess integration quality
    pub fn assess(&self) -> IntegrationAssessment {
        let mut assessment = IntegrationAssessment::default();
        assessment.overall_score = self.state.phi as f32 * 0.5 + self.state.metacognitive_confidence * 0.5;
        assessment.component_scores.insert("phi".to_string(), self.state.phi as f32);
        assessment.component_scores.insert("metacognition".to_string(), self.state.metacognitive_confidence);
        assessment
    }
}

impl Default for ConsciousnessPipeline {
    fn default() -> Self {
        Self::new(IntegrationConfig::default())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_consciousness_state() {
        let state = ConsciousnessState::new(512);
        assert!(state.phi == 0.0);
    }

    #[test]
    fn test_pipeline() {
        let mut pipeline = ConsciousnessPipeline::default();
        let input = RealHV::random(512);
        let state = pipeline.process(&input);
        assert!(state.working_memory.len() == 1);
    }
}
