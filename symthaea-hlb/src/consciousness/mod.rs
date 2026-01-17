//! # Consciousness Module: Integration and Awareness
//!
//! This module provides consciousness-related capabilities including:
//! - Consciousness unification and integration
//! - Seven Harmonies value alignment framework
//! - Phi-based attention mechanisms
//! - Empathic unification and emotional understanding
//! - Evolution and recursive improvement
//! - Affective consciousness and emotion processing
//! - Primitive reasoning and evolution

pub mod affective_consciousness;
pub mod autopoietic_consciousness;
pub mod cincinnati_consciousness;
pub mod consciousness_unification;
pub mod contextual_weights;
pub mod cross_modal_binding;
pub mod dream;
pub mod empathic_unification;
pub mod evolution_bridge;
pub mod gis_integration;
pub mod harmonies_integration;
pub mod multi_modal_integration;
pub mod neuro_bridge;
pub mod pac;
pub mod phi_attention;
pub mod primitive_consciousness;
pub mod primitive_discovery;
pub mod primitive_evolution;
pub mod primitive_reasoning;
pub mod recursive_improvement;
pub mod semantic_value_embedder;
pub mod seven_harmonies;
pub mod unified_value_evaluator;
pub mod value_feedback_loop;

// Re-export key types
pub use seven_harmonies::{SevenHarmonies, Harmony, HarmonyAlignment, AlignmentResult};
pub use affective_consciousness::{CoreAffect, EmotionCategory, AffectiveConsciousnessAnalyzer};
pub use primitive_reasoning::{PrimitiveReasoner, ReasoningResult};
pub use primitive_evolution::{PrimitiveEvolver, EvolutionResult};
pub use cross_modal_binding::{CrossModalBinder, BindingResult};
pub use autopoietic_consciousness::{AutopoieticConsciousness, AutopoieticState};

/// A node in the consciousness network
#[derive(Debug, Clone)]
pub struct ConsciousNode {
    /// Node identifier
    pub id: u64,
    /// Node name
    pub name: String,
    /// Activation level (0.0-1.0)
    pub activation: f32,
    /// Integrated information (Phi)
    pub phi: f64,
    /// Connection weights to other nodes
    pub connections: std::collections::HashMap<u64, f32>,
    /// Current state vector
    pub state: Vec<f32>,
}
