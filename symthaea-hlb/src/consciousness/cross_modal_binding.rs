//! # Cross-Modal Binding: Multi-Sensory Integration
//!
//! Provides mechanisms for binding information across different modalities
//! (vision, audio, text, etc.) into unified conscious representations.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use symthaea_core::hdc::RealHV;

/// Types of sensory modalities
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum Modality {
    /// Visual information
    Visual,
    /// Auditory information
    Auditory,
    /// Textual/linguistic information
    Textual,
    /// Proprioceptive (body sense)
    Proprioceptive,
    /// Temporal/sequential
    Temporal,
    /// Spatial
    Spatial,
    /// Emotional/affective
    Affective,
    /// Abstract/conceptual
    Abstract,
}

/// Configuration for cross-modal binding
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BindingConfig {
    /// Hypervector dimension
    pub dimension: usize,
    /// Binding strength threshold
    pub binding_threshold: f32,
    /// Decay rate for temporal binding
    pub temporal_decay: f32,
    /// Maximum bindings per modality
    pub max_bindings: usize,
    /// Whether to use attention weighting
    pub use_attention: bool,
}

impl Default for BindingConfig {
    fn default() -> Self {
        Self {
            dimension: 512,
            binding_threshold: 0.5,
            temporal_decay: 0.1,
            max_bindings: 100,
            use_attention: true,
        }
    }
}

/// A modal representation
#[derive(Debug, Clone)]
pub struct ModalRepresentation {
    /// The modality
    pub modality: Modality,
    /// Hypervector representation
    pub hv: RealHV,
    /// Confidence in this representation
    pub confidence: f32,
    /// Timestamp
    pub timestamp: u64,
    /// Source identifier
    pub source: String,
    /// Attention weight
    pub attention: f32,
}

impl ModalRepresentation {
    /// Create a new modal representation
    pub fn new(modality: Modality, hv: RealHV, confidence: f32, source: impl Into<String>) -> Self {
        Self {
            modality,
            hv,
            confidence,
            timestamp: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap_or_default()
                .as_millis() as u64,
            source: source.into(),
            attention: 1.0,
        }
    }

    /// Update attention weight
    pub fn with_attention(mut self, attention: f32) -> Self {
        self.attention = attention.clamp(0.0, 1.0);
        self
    }
}

/// Result of a binding operation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BindingResult {
    /// The bound representation (as vector for serialization)
    pub bound_hv: Vec<f32>,
    /// Modalities involved
    pub modalities: Vec<Modality>,
    /// Binding strength
    pub strength: f32,
    /// Coherence measure
    pub coherence: f32,
    /// Individual modal contributions
    pub contributions: HashMap<String, f32>,
}

/// The cross-modal binder
#[derive(Debug)]
pub struct CrossModalBinder {
    /// Configuration
    config: BindingConfig,
    /// Current modal representations per modality
    representations: HashMap<Modality, Vec<ModalRepresentation>>,
    /// Current bound state
    current_binding: Option<RealHV>,
    /// Binding history
    binding_history: Vec<BindingResult>,
    /// Statistics
    stats: BinderStats,
}

/// Statistics for the binder
#[derive(Debug, Clone, Default)]
pub struct BinderStats {
    /// Total bindings performed
    pub total_bindings: u64,
    /// Average binding strength
    pub avg_strength: f32,
    /// Average coherence
    pub avg_coherence: f32,
    /// Modality counts
    pub modality_counts: HashMap<Modality, u64>,
}

impl CrossModalBinder {
    /// Create a new cross-modal binder
    pub fn new(config: BindingConfig) -> Self {
        Self {
            config,
            representations: HashMap::new(),
            current_binding: None,
            binding_history: Vec::new(),
            stats: BinderStats::default(),
        }
    }

    /// Add a modal representation
    pub fn add_representation(&mut self, repr: ModalRepresentation) {
        let modality = repr.modality;

        let reps = self.representations.entry(modality).or_insert_with(Vec::new);

        // Maintain max bindings
        if reps.len() >= self.config.max_bindings {
            reps.remove(0);
        }

        reps.push(repr);

        // Update stats
        *self.stats.modality_counts.entry(modality).or_insert(0) += 1;
    }

    /// Perform cross-modal binding
    pub fn bind(&mut self) -> Option<BindingResult> {
        if self.representations.is_empty() {
            return None;
        }

        // Collect all representations with attention weighting
        let mut weighted_hvs = Vec::new();
        let mut modalities = Vec::new();
        let mut contributions = HashMap::new();

        for (modality, reps) in &self.representations {
            if let Some(rep) = reps.last() {
                let weight = if self.config.use_attention {
                    rep.attention * rep.confidence
                } else {
                    rep.confidence
                };

                weighted_hvs.push((rep.hv.clone(), weight));
                modalities.push(*modality);
                contributions.insert(format!("{:?}", modality), weight);
            }
        }

        if weighted_hvs.is_empty() {
            return None;
        }

        // Compute weighted bundle
        let _total_weight: f32 = weighted_hvs.iter().map(|(_, w)| w).sum();
        let bound_hv = if weighted_hvs.len() == 1 {
            weighted_hvs[0].0.clone()
        } else {
            let hvs: Vec<RealHV> = weighted_hvs.iter().map(|(hv, _)| hv.clone()).collect();
            RealHV::bundle(&hvs)
        };

        // Calculate binding strength (average pairwise similarity)
        let strength = self.calculate_binding_strength(&weighted_hvs);

        // Calculate coherence
        let coherence = self.calculate_coherence(&weighted_hvs);

        // Update current binding
        self.current_binding = Some(bound_hv.clone());

        // Update statistics
        self.stats.total_bindings += 1;
        let n = self.stats.total_bindings as f32;
        self.stats.avg_strength = (self.stats.avg_strength * (n - 1.0) + strength) / n;
        self.stats.avg_coherence = (self.stats.avg_coherence * (n - 1.0) + coherence) / n;

        let result = BindingResult {
            bound_hv: bound_hv.as_slice().to_vec(),
            modalities,
            strength,
            coherence,
            contributions,
        };

        self.binding_history.push(result.clone());
        Some(result)
    }

    /// Calculate binding strength
    fn calculate_binding_strength(&self, weighted_hvs: &[(RealHV, f32)]) -> f32 {
        if weighted_hvs.len() < 2 {
            return 1.0;
        }

        let mut total_sim = 0.0;
        let mut count = 0;

        for i in 0..weighted_hvs.len() {
            for j in (i + 1)..weighted_hvs.len() {
                let sim = weighted_hvs[i].0.similarity(&weighted_hvs[j].0);
                total_sim += sim;
                count += 1;
            }
        }

        if count > 0 {
            total_sim / count as f32
        } else {
            1.0
        }
    }

    /// Calculate coherence measure
    fn calculate_coherence(&self, weighted_hvs: &[(RealHV, f32)]) -> f32 {
        if weighted_hvs.is_empty() {
            return 0.0;
        }

        // Coherence based on weight consistency and similarity
        let total_weight: f32 = weighted_hvs.iter().map(|(_, w)| w).sum();
        let avg_weight = total_weight / weighted_hvs.len() as f32;

        let weight_variance: f32 = weighted_hvs.iter()
            .map(|(_, w)| (w - avg_weight).powi(2))
            .sum::<f32>() / weighted_hvs.len() as f32;

        // Lower variance = higher coherence
        1.0 / (1.0 + weight_variance.sqrt())
    }

    /// Query current binding against a probe
    pub fn query(&self, probe: &RealHV) -> Option<f32> {
        self.current_binding.as_ref().map(|binding| {
            binding.similarity(probe)
        })
    }

    /// Unbind a specific modality from current binding
    pub fn unbind(&mut self, modality: Modality) -> Option<RealHV> {
        let current = self.current_binding.as_ref()?;
        let modal_rep = self.representations.get(&modality)?.last()?;

        // Unbind by binding with inverse
        let unbound = current.bind(&modal_rep.hv);
        Some(unbound)
    }

    /// Apply temporal decay
    pub fn decay(&mut self, dt: f32) {
        let decay_factor = (1.0 - self.config.temporal_decay * dt).max(0.0);

        for reps in self.representations.values_mut() {
            for rep in reps.iter_mut() {
                rep.attention *= decay_factor;
            }
            // Remove representations with very low attention
            reps.retain(|r| r.attention > 0.01);
        }
    }

    /// Get current bound state
    pub fn current_binding(&self) -> Option<&RealHV> {
        self.current_binding.as_ref()
    }

    /// Get representations for a modality
    pub fn get_representations(&self, modality: Modality) -> Option<&Vec<ModalRepresentation>> {
        self.representations.get(&modality)
    }

    /// Get statistics
    pub fn stats(&self) -> &BinderStats {
        &self.stats
    }

    /// Clear all representations
    pub fn clear(&mut self) {
        self.representations.clear();
        self.current_binding = None;
    }
}

impl Default for CrossModalBinder {
    fn default() -> Self {
        Self::new(BindingConfig::default())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_binder_creation() {
        let binder = CrossModalBinder::default();
        assert!(binder.current_binding().is_none());
    }

    #[test]
    fn test_modal_representation() {
        let hv = RealHV::random(512, 42);
        let repr = ModalRepresentation::new(Modality::Visual, hv, 0.9, "camera");
        assert_eq!(repr.modality, Modality::Visual);
        assert_eq!(repr.confidence, 0.9);
    }

    #[test]
    fn test_binding() {
        let mut binder = CrossModalBinder::default();

        let visual = ModalRepresentation::new(
            Modality::Visual,
            RealHV::random(512, 42),
            0.9,
            "camera"
        );
        let audio = ModalRepresentation::new(
            Modality::Auditory,
            RealHV::random(512, 42),
            0.8,
            "microphone"
        );

        binder.add_representation(visual);
        binder.add_representation(audio);

        let result = binder.bind();
        assert!(result.is_some());

        let binding = result.unwrap();
        assert_eq!(binding.modalities.len(), 2);
        assert!(binding.strength >= 0.0 && binding.strength <= 1.0);
    }
}
